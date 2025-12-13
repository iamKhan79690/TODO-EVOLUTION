"""
SQLModel definitions for the Todo Evolution application.
"""

from enum import Enum
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class User(SQLModel, table=True):
    """User model managed by Better Auth."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")


class TaskBase(SQLModel):
    """Base task model with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Priority = Field(Priority.MEDIUM)
    due_date: Optional[datetime] = None
    recurrence_pattern: RecurrencePattern = Field(RecurrencePattern.NONE)


class Task(TaskBase, table=True):
    """Task model for user tasks."""

    id: Optional[int] = Field(default=None, primary_key=True)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")

    # Relationships
    user: User = Relationship(back_populates="tasks")