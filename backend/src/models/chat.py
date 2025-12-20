"""
SQLModel definitions for the AI Chat Assistant feature.

These models extend the existing TODO application schema with chat functionality
including conversations, messages, and context management.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, JSON, Boolean, Integer, Text, CheckConstraint, DateTime


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Message type enumeration."""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    OPERATION_RESULT = "operation_result"


class OperationStatus(str, Enum):
    """Operation status enumeration for AI operations."""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"


class Conversation(SQLModel, table=True):
    """Chat conversation model."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: Optional[str] = Field(default="New Conversation", max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    messages_count: int = Field(default=0)
    last_message_at: Optional[datetime] = None
    extra_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)
    contexts: List["ConversationContext"] = Relationship(back_populates="conversation", cascade_delete=True)

    # Table constraints
    __table_args__ = (
        CheckConstraint("user_id IS NOT NULL", name="conversations_user_active_check"),
        CheckConstraint("updated_at >= created_at", name="conversations_updated_check"),
    )


class Message(SQLModel, table=True):
    """Chat message model with rich metadata."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)  # Required for audit trail
    role: MessageRole = Field(nullable=False)
    content: str = Field(...)  # JSON content stored as string
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Database column name
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # For API compatibility
    message_type: MessageType = Field(default=MessageType.TEXT)
    operation_status: OperationStatus = Field(default=OperationStatus.DELIVERED)
    operation_type: Optional[str] = Field(default=None, max_length=50)  # e.g., 'add_task', 'complete_task'
    operation_result: Optional[str] = Field(default=None, sa_column=Column(JSON))
    error_details: Optional[str] = Field(default=None, sa_column=Column(JSON))
    extra_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    # Audit fields
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    retry_count: int = Field(default=0)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    task_operations: List["TaskOperationLog"] = Relationship(back_populates="message")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "CASE WHEN message_type = 'text' THEN jsonb_typeof(content::jsonb) = 'string' AND content::text <> '' ELSE true END",
            name="messages_content_not_empty"
        ),
        CheckConstraint("timestamp IS NOT NULL", name="messages_timestamp_order"),
        CheckConstraint("retry_count >= 0 AND retry_count <= 5", name="messages_retry_count_check"),
    )


class ConversationContext(SQLModel, table=True):
    """AI conversation context and memory management."""

    __tablename__ = "conversation_contexts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False)
    context_type: str = Field(max_length=50)  # e.g., 'task_memory', 'user_preferences', 'conversation_state'
    context_key: str = Field(max_length=100)  # Specific key within the context type
    context_value: str = Field(default="", sa_column=Column(JSON))
    expires_at: Optional[datetime] = None  # For temporary context that should expire
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    extra_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    # Relationships
    conversation: Conversation = Relationship(back_populates="contexts")


class TaskOperationLog(SQLModel, table=True):
    """Audit log for task operations performed through AI chat."""

    __tablename__ = "task_operations_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message_id: UUID = Field(foreign_key="messages.id", nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    operation_type: str = Field(max_length=50)  # 'add_task', 'complete_task', 'update_task', 'delete_task'
    task_id: Optional[int] = Field(default=None)  # Reference to the actual task if available
    operation_data: str = Field(default="", sa_column=Column(JSON))  # Input data
    operation_result: Optional[str] = Field(default=None, sa_column=Column(JSON))  # Result data
    status: str = Field(max_length=20)  # 'success', 'failed', 'partial'
    error_message: Optional[str] = Field(default=None, max_length=1000)
    processing_time_ms: Optional[int] = None  # Time taken to process operation
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    message: Message = Relationship(back_populates="task_operations")


# Update User model to include chat relationships
# Note: This will be added to the existing User model in models.py
# User.conversations: List[Conversation] = Relationship(back_populates="user")


# Helper functions for creating indexes
def create_chat_indexes():
    """Return a list of indexes that should be created for chat tables."""
    return [
        # Conversation indexes
        "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_conversations_user_active ON conversations(user_id, is_active);",
        "CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_conversations_last_message ON conversations(last_message_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_conversations_metadata ON conversations USING GIN(metadata);",

        # Message indexes
        "CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);",
        "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(conversation_id, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(conversation_id, role);",
        "CREATE INDEX IF NOT EXISTS idx_messages_operation_status ON messages(operation_status);",
        "CREATE INDEX IF NOT EXISTS idx_messages_content ON messages USING GIN(content);",
        "CREATE INDEX IF NOT EXISTS idx_messages_operation_type ON messages(operation_type);",

        # Context indexes
        "CREATE INDEX IF NOT EXISTS idx_contexts_conversation_id ON conversation_contexts(conversation_id);",
        "CREATE INDEX IF NOT EXISTS idx_contexts_type_key ON conversation_contexts(context_type, context_key);",
        "CREATE INDEX IF NOT EXISTS idx_contexts_expires_at ON conversation_contexts(expires_at);",

        # Operation log indexes
        "CREATE INDEX IF NOT EXISTS idx_operations_message_id ON task_operations_log(message_id);",
        "CREATE INDEX IF NOT EXISTS idx_operations_user_id ON task_operations_log(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_operations_created_at ON task_operations_log(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_operations_status ON task_operations_log(status);",
    ]


# Database extension commands
def setup_chat_extensions():
    """Return SQL commands to set up necessary PostgreSQL extensions."""
    return [
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",  # For UUID generation
        "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";",    # For text search (optional)
    ]