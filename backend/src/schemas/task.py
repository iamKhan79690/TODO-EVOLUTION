"""Task-related Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator


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


class TaskBase(BaseModel):
    """Base task schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    recurrence_pattern: RecurrencePattern = Field(RecurrencePattern.NONE, description="Task recurrence pattern")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title field."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace-only')
        return v.strip()

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        """Validate due date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v

    @field_validator('recurrence_pattern')
    @classmethod
    def validate_recurrence_requires_due_date(cls, v, info):
        """Recurrence pattern requires due date."""
        if v != RecurrencePattern.NONE and not info.data.get('due_date'):
            raise ValueError('Recurrence pattern requires a due date')
        return v


class TaskCreate(TaskBase):
    """Schema for creating new tasks."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating existing tasks."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    is_completed: Optional[bool] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate title field for updates."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty or whitespace-only')
        return v.strip() if v else v


class TaskResponse(TaskBase):
    """Schema for task responses."""
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list responses."""
    tasks: list[TaskResponse]
    count: int
    user_id: int