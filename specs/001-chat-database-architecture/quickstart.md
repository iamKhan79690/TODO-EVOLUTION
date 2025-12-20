# Quickstart Guide: Chat Database Architecture

**Feature**: 001-chat-database-architecture
**Phase**: Implementation Ready
**Date**: 2025-01-12

## Overview

This guide provides step-by-step instructions for implementing the chat database architecture for Phase III AI Chatbot. The implementation includes database models, API endpoints, and authentication integration.

## Prerequisites

### System Requirements
- Python 3.11+
- PostgreSQL 14+ (Neon recommended)
- Node.js 18+ (for frontend integration)
- Git

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname

# Authentication (Constitution Section III)
BETTER_AUTH_SECRET=your-secret-key-here

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

# Optional: OpenAI API Key for Phase III AI Integration
OPENAI_API_KEY=sk-your-openai-key
```

## Installation Steps

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi
pip install sqlmodel[all]
pip install asyncpg  # PostgreSQL async driver
pip install alembic  # Database migrations
pip install uvicorn[standard]  # ASGI server
pip install python-jose[cryptography]  # JWT handling
pip install python-multipart  # Form data support
```

### 2. Database Configuration

```python
# backend/src/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

DATABASE_URL = os.getenv("DATABASE_URL")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncSession:
    """Dependency for database sessions"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 3. Model Implementation

Create `backend/src/models/chat.py`:

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Enum, Index
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_conversations_user_created', 'user_id', 'created_at DESC'),
    )

    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete="all, delete-orphan",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    role: MessageRole = Field(sa_column=Column(Enum(MessageRole), nullable=False))
    content: str = Field(min_length=1, max_length=10000)
    tool_calls: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index('idx_messages_conversation_created', 'conversation_id', 'created_at ASC'),
        Index('idx_messages_user_conversation', 'user_id', 'conversation_id'),
    )

    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

### 4. Database Migration Setup

```bash
# Initialize Alembic
alembic init alembic

# Configure alembic.ini
# Set sqlalchemy.url = your DATABASE_URL
# Set file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
```

Create migration file `alembic/versions/create_chat_tables.py`:

```python
def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('title', String(length=255), nullable=True),
        sa.Column('created_at', DateTime(), nullable=False),
        sa.Column('updated_at', DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_conversations_user_created', 'user_id', 'created_at'),
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('conversation_id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('role', Enum('user', 'assistant', name='messagerole'), nullable=False),
        sa.Column('content', Text(), nullable=False),
        sa.Column('tool_calls', String(), nullable=True),
        sa.Column('created_at', DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_messages_conversation_created', 'conversation_id', 'created_at'),
    )

# Run migrations
alembic upgrade head
```

### 5. API Implementation

Create `backend/src/routes/chat.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlmodel import select, Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import uuid

from ..models.chat import Conversation, Message, MessageRole
from ..database import get_session
from ..dependencies.auth import verify_jwt_token, get_current_user_authorized

router = APIRouter(prefix="/api/{user_id}", tags=["Chat"])

# Dependency for user authorization
AuthorizedUser = Depends(get_current_user_authorized)
DbSession = Depends(get_session)

@router.get("/conversations")
async def list_conversations(
    user_id: uuid.UUID,
    current_user: dict = AuthorizedUser,
    session: AsyncSession = DbSession,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """List user's conversations"""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await session.exec(statement)
    conversations = result.all()

    return {
        "conversations": conversations,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": len(conversations),
            "has_next": len(conversations) == limit,
            "has_prev": offset > 0
        }
    }

@router.post("/conversations", status_code=201)
async def create_conversation(
    user_id: uuid.UUID,
    current_user: dict = AuthorizedUser,
    session: AsyncSession = DbSession,
    title: Optional[str] = None
) -> Conversation:
    """Create new conversation"""
    conversation = Conversation(user_id=user_id, title=title)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    current_user: dict = AuthorizedUser,
    session: AsyncSession = DbSession,
    limit: int = 50,
    before: Optional[datetime] = None
) -> dict:
    """Get conversation messages"""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.conversation.has(Conversation.user_id == user_id))
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    if before:
        statement = statement.where(Message.created_at < before)

    result = await session.exec(statement)
    messages = result.all()[::-1]  # Reverse to chronological order

    return {
        "messages": messages,
        "pagination": {
            "limit": limit,
            "offset": 0,
            "total": len(messages),
            "has_next": len(messages) == limit,
            "has_prev": False
        }
    }

@router.post("/conversations/{conversation_id}/messages", status_code=201)
async def create_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message_data: dict,
    current_user: dict = AuthorizedUser,
    session: AsyncSession = DbSession
) -> Message:
    """Send message to conversation"""

    # Validate content
    content = message_data.get("content", "").strip()
    if not content or len(content) > 10000:
        raise HTTPException(status_code=400, detail="Content must be 1-10,000 characters")

    # Validate role
    role = message_data.get("role")
    if role not in ["user", "assistant"]:
        raise HTTPException(status_code=400, detail="Role must be 'user' or 'assistant'")

    # Create message
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=MessageRole(role),
        content=content
    )

    # Handle tool calls if provided
    if "tool_calls" in message_data:
        import json
        message.tool_calls = json.dumps(message_data["tool_calls"])

    session.add(message)

    # Update conversation timestamp
    conversation = await session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)

    return message
```

### 6. Main Application Setup

Create `backend/src/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .database import engine
from .models.chat import SQLModel  # Import all models
from .routes import chat

# Create database tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

app = FastAPI(
    title="Chat API",
    description="Phase III AI Chatbot Database API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)

@app.on_event("startup")
async def startup_event():
    await create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Testing the Implementation

### 1. Start the Server

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test API Endpoints

#### Create Conversation
```bash
curl -X POST "http://localhost:8000/api/YOUR_USER_ID/conversations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Conversation"}'
```

#### Send Message
```bash
curl -X POST "http://localhost:8000/api/YOUR_USER_ID/conversations/CONVERSATION_ID/messages" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello, this is a test message",
    "role": "user"
  }'
```

#### Get Messages
```bash
curl -X GET "http://localhost:8000/api/YOUR_USER_ID/conversations/CONVERSATION_ID/messages" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Verification Checklist

### Database Requirements ✅
- [ ] Tables created with proper foreign key constraints
- [ ] Indexes created for performance optimization
- [ ] Cascade delete configured correctly
- [ ] Content validation enforced

### API Requirements ✅
- [ ] JWT authentication working
- [ ] User isolation enforced
- [ ] Pagination support
- [ ] Error handling implemented
- [ ] OpenAPI documentation available at `/docs`

### Performance Targets ✅
- [ ] Conversation creation < 500ms
- [ ] Message submission < 300ms
- [ ] History retrieval < 200ms for 100 messages
- [ ] Supports 10,000 concurrent users

### Security Requirements ✅
- [ ] JWT token verification
- [ ] User ID matching JWT validation
- [ ] Content sanitization (no HTML/JS)
- [ ] SQL injection prevention via SQLModel

## Next Steps

1. **Frontend Integration**: Implement Next.js components for chat interface
2. **Phase III AI Integration**: Add OpenAI agent and MCP server
3. **Load Testing**: Verify performance under load
4. **Monitoring**: Add logging and metrics
5. **Deployment**: Deploy to production infrastructure

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify DATABASE_URL format
   - Check network connectivity
   - Ensure PostgreSQL server is running

2. **JWT Authentication Failures**
   - Verify BETTER_AUTH_SECRET matches between frontend and backend
   - Check token expiration
   - Ensure proper Authorization header format

3. **Performance Issues**
   - Check database indexes are created
   - Verify connection pool configuration
   - Monitor database query performance

### Support

- Check the API documentation at `http://localhost:8000/docs`
- Review the constitution document for compliance requirements
- Refer to the data model documentation for schema details

---

**Implementation Status**: ✅ Ready for development
**Constitution Compliance**: ✅ All requirements met
**Performance Targets**: ✅ All criteria achievable