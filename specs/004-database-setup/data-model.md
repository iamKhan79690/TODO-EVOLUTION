# Data Model Specification

**Date**: 2025-12-07
**Feature**: 004-database-setup
**Database**: Neon PostgreSQL with SQLModel

## Overview

The data model implements the constitution's specified schema with User and Task entities, supporting full Phase I feature parity while maintaining data integrity and performance optimization.

## Core Entities

### User Entity

**Purpose**: Authentication and profile management (managed by Better Auth)
**Table Name**: `users`
**Primary Key**: `id` (UUID, managed by Better Auth)

**Fields**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,                    -- Better Auth managed
    email VARCHAR(255) UNIQUE NOT NULL,     -- User email address
    name VARCHAR(255),                      -- Display name
    created_at TIMESTAMP DEFAULT NOW(),     -- Account creation timestamp
    updated_at TIMESTAMP DEFAULT NOW()      -- Profile update timestamp
);
```

**Constraints**:
- `email` must be unique and not null
- `created_at` auto-populated on insert
- `updated_at` auto-updated on changes
- Better Auth manages all CRUD operations

**Indexes**:
- Primary key on `id`
- Unique index on `email`

### Task Entity

**Purpose**: Todo items with full Phase I feature support
**Table Name**: `tasks`
**Primary Key**: `id` (UUID)
**Foreign Key**: `user_id` → `users.id`

**Fields**:
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    tags TEXT[],                        -- Array of tag strings
    due_date TIMESTAMP,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR(50),      -- 'daily', 'weekly', 'monthly', 'yearly'
    recurrence_end_date TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Constraints**:
- `user_id` foreign key with cascading deletes
- `priority` limited to: 'low', 'medium', 'high'
- `recurrence_pattern` limited to standard values
- `title` required, max 500 characters
- `tags` stored as PostgreSQL array for efficient queries

**Indexes**:
- Primary key on `id`
- Foreign key index on `user_id` (for user-specific queries)
- Index on `completed` (for filtering incomplete tasks)
- Composite index on `(user_id, completed)` (for common query patterns)
- GIN index on `tags` (for efficient array queries)

## Entity Relationships

### User → Tasks (One-to-Many)

**Description**: Each user can have multiple tasks
**Relationship**: `users.id` ← `tasks.user_id`
**Cardinality**: 1:N
**Cascading**: User deletion removes all associated tasks

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

# Base table for Better Auth users (read-only for our app)
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")

    # Core task fields
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)

    # Phase I features
    tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    due_date: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[RecurrencePattern] = Field(default=None)
    recurrence_end_date: Optional[datetime] = Field(default=None)

    # Completion tracking
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="tasks")
```

## Data Validation Rules

### Task Validation

**Title**:
- Required field
- 1-500 characters
- No leading/trailing whitespace

**Priority**:
- Default: 'medium'
- Valid values: 'low', 'medium', 'high'

**Tags**:
- Optional array of strings
- Each tag: 1-50 characters
- Maximum 10 tags per task
- Duplicate tags removed automatically

**Due Date**:
- Optional datetime
- Must be in the future for new tasks
- Past dates allowed for existing tasks (editing)

**Recurrence**:
- `is_recurring` must be true if `recurrence_pattern` is set
- `recurrence_end_date` must be after `due_date` if both set
- Valid patterns: 'daily', 'weekly', 'monthly', 'yearly'

### Business Logic

**Task Completion**:
- Setting `completed = True` automatically sets `completed_at`
- Setting `completed = False` automatically clears `completed_at`
- Recurring tasks create next instance on completion

**Due Date Handling**:
- Tasks with past due dates highlighted in UI
- Overdue tasks calculated based on current date vs due_date

**Tag Management**:
- Tags stored in lowercase for consistency
- Whitespace trimmed from individual tags
- Empty strings filtered from tag arrays

## Query Patterns and Optimization

### Common Queries

**User Task List**:
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND completed = false
ORDER BY due_date ASC, priority DESC, created_at DESC;
```

**Task Search**:
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND (title ILIKE $2 OR description ILIKE $2 OR $3 = ANY(tags))
ORDER BY created_at DESC;
```

**Tag Filter**:
```sql
SELECT * FROM tasks
WHERE user_id = $1 AND $2 = ANY(tags)
ORDER BY created_at DESC;
```

**Overdue Tasks**:
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND completed = false
  AND due_date < NOW()
ORDER BY due_date ASC;
```

### Performance Considerations

**Indexes Used**:
- `user_id` index for user-specific queries
- `completed` index for filtering
- `(user_id, completed)` composite index for common patterns
- `tags` GIN index for array queries

**Query Optimization**:
- Use parameterized queries (SQLModel automatic)
- Limit result sets for large datasets
- Implement pagination for task lists
- Cache frequently accessed user preferences

## Migration Strategy

### Phase II Approach

**Automatic Table Creation**:
- SQLModel `create_all()` on application startup
- No manual SQL migrations required
- Tables created with proper constraints and indexes

**Data Population**:
- Better Auth creates user records
- Task creation handled by application logic
- Default values ensure data integrity

### Future Considerations (Phase III+)

**Alembic Integration**:
- Schema versioning for production deployments
- Automated migration scripts
- Rollback capabilities for schema changes

**Data Archival**:
- Archived completed tasks table
- Data retention policies
- Performance optimization for large datasets

## Security and Privacy

**Data Isolation**:
- All queries filtered by `user_id`
- No cross-user data access possible
- Foreign key constraints enforce data integrity

**Privacy Considerations**:
- User email addresses stored securely
- No sensitive data in task descriptions
- GDPR compliance through user data control

**Access Control**:
- Database access through application layer only
- User isolation enforced at query level
- No direct database access for end users

## Testing Strategy

### Data Validation Tests

- Task creation with valid/invalid data
- Edge cases for due dates and recurrence
- Tag array handling and validation
- User relationship enforcement

### Performance Tests

- Query performance with large datasets
- Concurrent user access patterns
- Connection pool efficiency
- Index utilization verification

### Integration Tests

- User task creation and retrieval
- Cross-table relationship integrity
- Transaction rollback scenarios
- Error handling and recovery

This data model provides a solid foundation for the Phase II application while maintaining flexibility for future enhancements and ensuring data integrity and performance.