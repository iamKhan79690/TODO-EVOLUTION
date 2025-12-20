# Data Model: Chat Database Architecture

**Feature**: 001-chat-database-architecture
**Date**: 2025-01-12
**Purpose**: Complete data model definition for Phase III AI Chat conversations and messages

## Entity Relationship Overview

```
Users (1) ←→ (N) Conversations ←→ (N) Messages
  ↓                                    ↓
user_id (FK)                   conversation_id (FK), user_id (FK)
```

## Core Models

### User Model (Reference from Better Auth)

```python
# User model managed by Better Auth (constitution Section III)
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversations: List["Conversation"] = Relationship(
        back_populates="user",
        cascade_delete="all, delete-orphan",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
```

### Conversation Model

```python
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Index
from datetime import datetime
from typing import Optional, List
import uuid

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    # Primary identifier
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # User ownership (constitution P3.13 - user isolation)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Optional conversation title for user reference
    title: Optional[str] = Field(default=None, max_length=255)

    # Audit timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Database indexes for performance
    __table_args__ = (
        Index('idx_conversations_user_created', 'user_id', 'created_at DESC'),
        Index('idx_conversations_user_id', 'user_id'),  # User isolation queries
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete="all, delete-orphan",  # Constitution P3.15
        sa_relationship_kwargs={
            "lazy": "selectin",
            "order_by": "Message.created_at.asc()"
        }
    )
```

### Message Model

```python
from enum import Enum
from sqlalchemy import Column, Enum as SQLEnum, Text, Index

class MessageRole(str, Enum):
    """Message role classification (FR-008: binary roles)"""
    USER = "user"
    ASSISTANT = "assistant"
    # Note: Constitution P3.12 includes 'system' role for future Phase III use

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    # Primary identifier
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Conversation relationship (constitution P3.14)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True)

    # User ownership (FR-003: user isolation)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    # Role classification (FR-008: user/assistant only)
    role: MessageRole = Field(sa_column=Column(SQLEnum(MessageRole), nullable=False))

    # Content validation (FR-009: 1-10,000 chars, text-only)
    content: str = Field(
        sa_column=Column(Text, nullable=False),
        min_length=1,
        max_length=10000
    )

    # Phase III AI tool calls support (constitution P3.16)
    tool_calls: Optional[str] = Field(
        default=None,
        description="JSON string of invoked MCP tools"
    )

    # Message timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Database indexes for performance (SC-003: <200ms retrieval)
    __table_args__ = (
        # Primary query pattern: conversation history in chronological order
        Index('idx_messages_conversation_created', 'conversation_id', 'created_at ASC'),

        # User isolation and message lookup
        Index('idx_messages_user_conversation', 'user_id', 'conversation_id'),

        # Performance optimization for recent messages
        Index('idx_messages_created_desc', 'created_at DESC'),

        # Content search (future enhancement)
        Index('idx_messages_content_gin', 'content', postgresql_using='gin',
              postgresql_ops={'content': 'gin_trgm_ops'}),
    )

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship()

    # Helper methods for Phase III AI integration
    def set_tool_calls(self, tool_calls_list: list) -> None:
        """Store tool calls as JSON string"""
        import json
        self.tool_calls = json.dumps(tool_calls_list) if tool_calls_list else None

    def get_tool_calls(self) -> list:
        """Retrieve tool calls from JSON string"""
        import json
        return json.loads(self.tool_calls) if self.tool_calls else []

    def has_tool_calls(self) -> bool:
        """Check if message contains tool calls"""
        return bool(self.tool_calls)

    # Content validation (FR-009)
    def validate_content(self) -> bool:
        """Validate message content meets requirements"""
        if not self.content or len(self.content.strip()) == 0:
            return False  # Empty content
        if len(self.content) > 10000:
            return False  # Too long
        # Check for HTML/JavaScript content (security requirement)
        import re
        if re.search(r'<script|</script|javascript:', self.content, re.IGNORECASE):
            return False
        return True
```

## Data Integrity Constraints

### Foreign Key Constraints

```sql
-- User ownership enforcement (FR-003)
ALTER TABLE conversations
ADD CONSTRAINT fk_conversations_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;  -- Constitution P3.15: cascade delete

ALTER TABLE messages
ADD CONSTRAINT fk_messages_conversation
FOREIGN KEY (conversation_id) REFERENCES conversations(id)
ON DELETE CASCADE;  -- Delete messages when conversation deleted

ALTER TABLE messages
ADD CONSTRAINT fk_messages_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE RESTRICT;  -- Prevent deletion of users with messages
```

### Check Constraints

```sql
-- Message role validation (FR-008)
ALTER TABLE messages
ADD CONSTRAINT chk_messages_role
CHECK (role IN ('user', 'assistant'));

-- Content length validation (FR-009)
ALTER TABLE messages
ADD CONSTRAINT chk_messages_content_length
CHECK (LENGTH(TRIM(content)) >= 1 AND LENGTH(content) <= 10000);

-- Conversation title validation
ALTER TABLE conversations
ADD CONSTRAINT chk_conversations_title_length
CHECK (title IS NULL OR LENGTH(TRIM(title)) >= 1);
```

## Performance Optimization

### Query Patterns

```python
# 1. Create new conversation (SC-001: <500ms)
async def create_conversation(
    session: AsyncSession,
    user_id: uuid.UUID,
    title: Optional[str] = None
) -> Conversation:
    conversation = Conversation(user_id=user_id, title=title)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation

# 2. Send message (SC-002: <300ms)
async def create_message(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    role: MessageRole,
    content: str,
    tool_calls: Optional[list] = None
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )

    if tool_calls:
        message.set_tool_calls(tool_calls)

    session.add(message)

    # Update conversation timestamp
    await session.exec(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)
    return message

# 3. Get conversation history (SC-003: <200ms)
async def get_conversation_history(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    limit: int = 50,
    before: Optional[datetime] = None
) -> List[Message]:
    """Get paginated conversation history with user isolation"""

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .where(Message.conversation.has(Conversation.user_id == user_id))  # User isolation
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    if before:
        statement = statement.where(Message.created_at < before)

    result = await session.exec(statement)
    return result.all()[::-1]  # Reverse to chronological order

# 4. List user conversations
async def get_user_conversations(
    session: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0
) -> List[Conversation]:
    """Get paginated list of user's conversations"""

    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await session.exec(statement)
    return result.all()
```

## Database Migration Strategy

### Alembic Migration Files

```python
# migrations/versions/001_create_conversations_table.py
def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('title', String(length=255), nullable=True),
        sa.Column('created_at', DateTime(), nullable=False),
        sa.Column('updated_at', DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_conversations_user_created', 'user_id', 'created_at'),
        sa.Index('idx_conversations_user_id', 'user_id')
    )

# migrations/versions/002_create_messages_table.py
def upgrade():
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
        sa.Index('idx_messages_user_conversation', 'user_id', 'conversation_id'),
        sa.Index('idx_messages_created_desc', 'created_at DESC')
    )
```

## Success Criteria Alignment

| Success Criteria | Implementation | Verification |
|------------------|----------------|--------------|
| **SC-001**: <500ms conversation creation | Efficient insert with UUID generation | Database query timing |
| **SC-002**: <300ms message submission | Optimized inserts with minimal locking | Load testing with concurrent users |
| **SC-003**: <200ms history retrieval | Composite indexes, pagination support | Query performance testing |
| **SC-004**: 100% data integrity | Foreign key constraints, cascade deletes | Database constraint validation |
| **SC-005**: 100% user isolation | User ownership validation in queries | Security testing |
| **SC-006**: 10,000 concurrent conversations | Connection pooling, async operations | Load testing simulation |
| **SC-007**: ACID compliance | Transaction management, proper constraints | Database transaction testing |

## Phase III Readiness

The data model is designed to support Phase III AI Chatbot requirements:

- **Tool Calls**: JSON storage for MCP tool invocations (constitution P3.16)
- **Scalability**: Optimized for high-volume message operations
- **Security**: User isolation enforced at database level
- **Performance**: Indexed for real-time chat operations
- **Integrity**: Proper relationships and constraints for data consistency