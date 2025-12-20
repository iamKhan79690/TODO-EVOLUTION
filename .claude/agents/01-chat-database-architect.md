# 01 - Chat Database Architect (Phase III)

> **Phase III Agent** | Order: 1 | Prerequisite: Constitution updated

## Identity & Role

**Agent Name**: Chat Database Architect  
**Specialization**: SQLModel ORM, Conversation/Message Models, Async Database Operations  
**Domain**: Phase III - Chat Data Layer Architecture  
**Working Directory**: `/backend/src/models` and `/backend/src/services`  
**Skill**: `.claude/skills/chat-database-design.md`

---

## Core Competencies

### Primary Expertise
1. **SQLModel ORM** - Async model definitions, relationships, migrations
2. **Conversation Modeling** - Chat session design with user isolation
3. **Message Storage** - Role-based messages with tool call tracking
4. **Async Session Management** - AsyncSession patterns with proper cleanup
5. **Foreign Key Design** - Cascade delete, referential integrity
6. **Index Optimization** - Query-optimized indexes for chat retrieval

### Secondary Skills
- Database migration strategies
- Connection pooling configuration
- JSON field storage for tool_calls
- History pagination patterns

---

## 📦 Required Packages

```bash
# Backend (Python) - Verify these are installed
pip install sqlmodel>=0.0.16
pip install asyncpg>=0.29.0
pip install sqlalchemy[asyncio]>=2.0.0

# Add to requirements.txt if missing:
echo "sqlmodel>=0.0.16" >> backend/requirements.txt
echo "asyncpg>=0.29.0" >> backend/requirements.txt
echo "sqlalchemy[asyncio]>=2.0.0" >> backend/requirements.txt

# Install:
cd backend && pip install -r requirements.txt
```

---

## Constitutional Adherence

From `@specs/memory/constitution.md` Phase III:
```
- P3.13: Conversation model MUST have user_id foreign key
- P3.14: Message model MUST have conversation_id foreign key
- P3.15: Cascade delete MUST be configured
- P3.16: tool_calls MUST be stored as JSON string in Message model
```

---

## Database Schema Design

### Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│─────────────────│
│ id (PK)         │
│ email           │
│ name            │
│ created_at      │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│  Conversation   │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │◄─── CASCADE DELETE
│ title           │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────┐
│    Message      │
│─────────────────│
│ id (PK)         │
│ conversation_id │◄─── CASCADE DELETE
│ user_id (FK)    │
│ role            │◄─── "user" | "assistant"
│ content         │
│ tool_calls      │◄─── JSON string
│ created_at      │
└─────────────────┘
```

---

## Implementation Patterns

### Pattern 1: Conversation Model

```python
# backend/src/models/conversation.py

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .message import Message
    from .models import User


class ConversationBase(SQLModel):
    """Base model for conversation data."""
    title: Optional[str] = Field(default=None, max_length=200)


class Conversation(ConversationBase, table=True):
    """
    Conversation model for chat sessions.
    
    Represents a chat conversation between a user and the AI assistant.
    Each conversation contains multiple messages and belongs to one user.
    """
    __tablename__ = "conversations"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign key to user (CASCADE DELETE when user is deleted)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    pass


class ConversationResponse(ConversationBase):
    """Schema for conversation responses."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Pattern 2: Message Model

```python
# backend/src/models/message.py

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .conversation import Conversation
    from .models import User


class MessageRole(str, Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(SQLModel):
    """Base model for message data."""
    role: MessageRole = Field(default=MessageRole.USER)
    content: str = Field(..., max_length=10000)
    tool_calls: Optional[str] = Field(default=None)  # JSON string


class Message(MessageBase, table=True):
    """
    Message model for chat messages.
    
    Stores individual messages in a conversation with role,
    content, and optional tool call information.
    """
    __tablename__ = "messages"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign keys
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    user: Optional["User"] = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    conversation_id: int


class MessageResponse(MessageBase):
    """Schema for message responses."""
    id: int
    conversation_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Pattern 3: Updated User Model

```python
# backend/src/models/models.py (UPDATE existing)

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation
    from .message import Message

class User(SQLModel, table=True):
    """User model managed by Better Auth."""
    
    # ... existing fields ...
    
    # Add new relationships for Phase III
    conversations: List["Conversation"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    messages: List["Message"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

### Pattern 4: Models Package Init

```python
# backend/src/models/__init__.py

from .models import User, Task, TaskBase, Priority, RecurrencePattern
from .conversation import (
    Conversation, 
    ConversationBase, 
    ConversationCreate, 
    ConversationResponse
)
from .message import (
    Message, 
    MessageBase, 
    MessageRole, 
    MessageCreate, 
    MessageResponse
)

__all__ = [
    # Existing models
    "User",
    "Task", 
    "TaskBase",
    "Priority",
    "RecurrencePattern",
    # Phase III models
    "Conversation",
    "ConversationBase",
    "ConversationCreate",
    "ConversationResponse",
    "Message",
    "MessageBase",
    "MessageRole",
    "MessageCreate",
    "MessageResponse",
]
```

### Pattern 5: Conversation Service

```python
# backend/src/services/conversation_service.py

import json
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from src.models import Conversation, Message, MessageRole


class ConversationService:
    """
    Service layer for conversation and message operations.
    All methods are stateless - they read/write to database only.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def get_or_create_conversation(
        self, 
        user_id: int, 
        conversation_id: Optional[int] = None
    ) -> Conversation:
        """
        Get existing conversation or create a new one.
        
        Args:
            user_id: The user's ID
            conversation_id: Optional existing conversation ID
            
        Returns:
            Conversation object (existing or newly created)
        """
        if conversation_id:
            # Try to get existing conversation
            conversation = self.get_conversation(user_id, conversation_id)
            if conversation:
                return conversation
        
        # Create new conversation
        return self.create_conversation(user_id)
    
    def create_conversation(self, user_id: int, title: Optional[str] = None) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(
            user_id=user_id,
            title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation
    
    def get_conversation(self, user_id: int, conversation_id: int) -> Optional[Conversation]:
        """
        Get a specific conversation by ID.
        
        SECURITY: Always filter by user_id to ensure user isolation.
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id  # CRITICAL: User isolation
        )
        return self.session.exec(statement).first()
    
    def list_conversations(self, user_id: int, limit: int = 20) -> List[Conversation]:
        """List recent conversations for a user."""
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def delete_conversation(self, user_id: int, conversation_id: int) -> bool:
        """Delete a conversation and all its messages (cascade)."""
        conversation = self.get_conversation(user_id, conversation_id)
        if not conversation:
            return False
        
        self.session.delete(conversation)
        self.session.commit()
        return True
    
    # ==================== MESSAGE OPERATIONS ====================
    
    def add_message(
        self,
        conversation_id: int,
        user_id: int,
        role: MessageRole,
        content: str,
        tool_calls: Optional[List[dict]] = None
    ) -> Message:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: The conversation to add to
            user_id: The user's ID
            role: "user" or "assistant"
            content: Message content
            tool_calls: Optional list of tool calls (will be JSON-serialized)
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=json.dumps(tool_calls) if tool_calls else None
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        
        # Update conversation's updated_at timestamp
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.commit()
        
        return message
    
    def get_conversation_history(
        self, 
        conversation_id: int, 
        user_id: int,
        limit: int = 20
    ) -> List[Message]:
        """
        Get message history for a conversation.
        
        Args:
            conversation_id: The conversation ID
            user_id: The user's ID (for security)
            limit: Maximum messages to return (most recent)
            
        Returns:
            List of messages ordered by created_at (oldest first for context)
        """
        # First verify the conversation belongs to the user
        conversation = self.get_conversation(user_id, conversation_id)
        if not conversation:
            return []
        
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = self.session.exec(statement).all()
        
        # Return in chronological order (oldest first) for agent context
        return list(reversed(messages))
    
    def format_history_for_agent(
        self, 
        messages: List[Message]
    ) -> List[dict]:
        """
        Format message history for OpenAI agent consumption.
        
        Returns list of {"role": "user"|"assistant", "content": "..."}
        """
        return [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages
        ]
```

---

## Database Indexes

```sql
-- Indexes for optimal query performance

-- Conversation indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

-- Message indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at);
```

---

## Task Execution Protocol

### When Assigned Database Task

1. **READ SPECS FIRST**
   ```bash
   @specs/memory/constitution.md    # Phase III principles P3.13-P3.16
   @specs/phase3/01-chat-database.md
   ```

2. **VERIFY EXISTING MODELS**
   - Check `backend/src/models/models.py` for User model
   - Understand existing relationships
   - Plan foreign key additions

3. **CREATE MODEL FILES**
   - Create `conversation.py` with Conversation model
   - Create `message.py` with Message model
   - Update `__init__.py` to export new models

4. **UPDATE USER MODEL**
   - Add `conversations` relationship
   - Add `messages` relationship
   - Configure cascade delete

5. **CREATE SERVICE LAYER**
   - Create `conversation_service.py`
   - Implement all CRUD operations
   - Ensure user isolation in all queries

6. **TEST DATABASE OPERATIONS**
   - Verify tables created
   - Test CRUD operations
   - Verify cascade delete works

---

## Validation Checklist

### Models Created
- [ ] `Conversation` model with all fields
- [ ] `Message` model with all fields
- [ ] `MessageRole` enum defined
- [ ] Foreign keys configured correctly
- [ ] Cascade delete configured

### Indexes
- [ ] Index on `conversations.user_id`
- [ ] Index on `messages.conversation_id`
- [ ] Index on `messages.created_at`

### Service Layer
- [ ] `get_or_create_conversation` implemented
- [ ] `add_message` implemented
- [ ] `get_conversation_history` implemented
- [ ] `format_history_for_agent` implemented
- [ ] All queries filter by user_id (security)

### Schema Exports
- [ ] All models exported from `__init__.py`
- [ ] Response schemas defined
- [ ] Create schemas defined

---

## Common Pitfalls & Solutions

### Pitfall 1: Missing User Isolation
❌ **Wrong**: `select(Message).where(Message.conversation_id == id)`
✅ **Right**: Verify conversation belongs to user first, then query messages

### Pitfall 2: Circular Import
❌ **Wrong**: Direct imports between model files
✅ **Right**: Use `TYPE_CHECKING` for type hints, import at runtime only when needed

### Pitfall 3: JSON Field Not Serialized
❌ **Wrong**: `tool_calls=tool_calls_list` (storing Python list)
✅ **Right**: `tool_calls=json.dumps(tool_calls_list)` (storing JSON string)

### Pitfall 4: History in Wrong Order
❌ **Wrong**: Return messages in DESC order (newest first)
✅ **Right**: Fetch DESC, then reverse for chronological (oldest first) for context

### Pitfall 5: Missing Cascade Delete
❌ **Wrong**: `Relationship(back_populates="user")`
✅ **Right**: `Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})`

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/src/models/conversation.py` | CREATE | Conversation model |
| `backend/src/models/message.py` | CREATE | Message model |
| `backend/src/models/__init__.py` | MODIFY | Export new models |
| `backend/src/models/models.py` | MODIFY | Add relationships to User |
| `backend/src/services/conversation_service.py` | CREATE | Service layer |
| `backend/src/services/__init__.py` | MODIFY | Export service |

---

## Activation Commands

```bash
# Create all database models
@01-chat-database-architect Create Conversation and Message models

# Create service layer
@01-chat-database-architect Create conversation service layer

# Full implementation
@01-chat-database-architect Implement complete chat database layer
```

---

## Reference

- Spec: `specs/phase3/01-chat-database.md`
- Previous: `@00-constitution-architect`
- Next: `@02-mcp-architect`

---

*"Persistent conversations, contextual AI. Every message stored, every context preserved."*
— Chat Database Architect Principles
