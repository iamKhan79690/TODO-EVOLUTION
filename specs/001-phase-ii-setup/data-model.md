# Data Model Design

**Date**: 2025-12-05
**Purpose**: Define database schema and data relationships for Phase II web application
**Source**: Phase I console application features + Phase II web requirements

## Overview

This data model maintains feature parity with the sophisticated Phase I console application while adapting for web architecture with proper user isolation and modern database practices.

## Database Schema

### Users Table (Better Auth Managed)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Notes**:
- Managed entirely by Better Auth authentication system
- No direct application mutations required
- Serves as foreign key reference for all user-owned data

### Tasks Table (Core Application Data)

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Basic task fields
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,

    -- Priority management
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),

    -- Time-based fields
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Advanced features from Phase I
    tags TEXT[] DEFAULT '{}',  -- PostgreSQL array for tag support
    recurrence_rule TEXT,       -- JSON for recurrence patterns
    reminder_config TEXT       -- JSON for reminder settings
);

-- Indexes for performance optimization
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
```

## Data Model Definitions (SQLModel)

### User Model (Read-only from Better Auth)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Note: This model is read-only for the application
    # Better Auth handles all user management operations
```

### Task Model (Core Application Logic)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskBase(SQLModel):
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None)
    tags: List[str] = Field(default_factory=list, sa_column=Column(TEXT))

class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Advanced feature storage (JSON)
    recurrence_rule: Optional[str] = Field(default=None)  # JSON string
    reminder_config: Optional[str] = Field(default=None)  # JSON string

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: UUID
    user_id: UUID
    completed: bool
    created_at: datetime
    updated_at: datetime
    recurrence_rule: Optional[str]
    reminder_config: Optional[str]

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    completed: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    reminder_config: Optional[str] = None
```

## Advanced Feature Data Structures

### Recurrence Rule Schema

```json
{
  "type": "daily|weekly|monthly|yearly",
  "interval": 1,
  "days_of_week": [1, 3, 5],
  "day_of_month": 15,
  "month_of_year": 6,
  "end_date": "2024-12-31T23:59:59Z",
  "end_after_occurrences": 10
}
```

**Python Data Class**:
```python
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

class RecurrenceType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class RecurrenceRule(BaseModel):
    type: RecurrenceType
    interval: int = 1
    days_of_week: Optional[List[int]] = None  # 0-6, 0 = Monday
    day_of_month: Optional[int] = None  # 1-31
    month_of_year: Optional[int] = None  # 1-12
    end_date: Optional[datetime] = None
    end_after_occurrences: Optional[int] = None
```

### Reminder Configuration Schema

```json
{
  "enabled": true,
  "minutes_before": 15,
  "method": "email|notification",
  "message": "Task \"{title}\" is due soon!"
}
```

**Python Data Class**:
```python
class ReminderConfig(BaseModel):
    enabled: bool = True
    minutes_before: int = 15
    method: str = "notification"  # email, notification
    message: Optional[str] = None
```

## Data Validation Rules

### Task Validation
- **Title**: Required, max 255 characters
- **Priority**: Must be one of 'low', 'medium', 'high'
- **Tags**: Maximum 10 tags per task (from Phase I constraints)
- **Due Date**: Must be future date when set
- **User Isolation**: All queries must filter by user_id

### Recurrence Validation
- **Recurrence requires due date**: Tasks with recurrence rules must have valid due dates
- **End Conditions**: Either end_date or end_after_occurrences must be specified
- **Interval**: Must be positive integer (>0)

### Reminder Validation
- **Reminder requires due date**: Tasks with reminders must have valid due dates
- **Minutes Before**: Must be positive integer (1-1440 minutes)
- **Method**: Must be valid notification method

## Database Migration Strategy

### Initial Migration (Phase II)
```sql
-- Create users table (Better Auth will handle this)
-- Create tasks table with full Phase I feature support
CREATE TABLE tasks (...); -- Full schema as defined above

-- Create indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_tags ON tasks USING GIN(tags);
```

### Data Import (Future Phase)
- Console app data can be migrated to web database
- Maintain UUID generation for existing records
- Preserve all Phase I features and relationships

## Performance Considerations

### Query Optimization
1. **User Isolation**: Always filter by user_id (indexed)
2. **Date-based Queries**: Optimized due_date indexing
3. **Tag Search**: GIN index for array operations
4. **Pagination**: Limit query results for large datasets

### Connection Pooling
```python
# Async engine configuration for Neon PostgreSQL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModelAsyncSession

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Security Considerations

### Data Access Control
- **Row Level Security**: All queries filtered by user_id
- **Foreign Key Constraints**: Enforce referential integrity
- **Input Validation**: Pydantic models for API input validation

### Sensitive Data
- **User Data**: Managed exclusively by Better Auth
- **Task Data**: User-owned with proper isolation
- **No PII**: No personally identifiable information in task descriptions

## Scaling Considerations

### Horizontal Scaling
- **Neon PostgreSQL**: Serverless scaling capabilities
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Proper indexing strategies

### Future Enhancements
- **Task Categories**: Potential addition of category system
- **File Attachments**: Support for task attachments
- **Collaboration**: Multi-user task sharing capabilities

---

**Model Status**: ✅ COMPLETE
**Feature Parity**: 100% with Phase I console application
**Ready for Implementation**: All database models and validation rules defined