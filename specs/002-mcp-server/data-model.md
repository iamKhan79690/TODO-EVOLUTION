# Data Model: MCP Server Task Management

**Feature**: 002-mcp-server
**Date**: 2025-01-12
**Based on**: Existing SQLModel models from `backend/src/models/models.py`

---

## Overview

The MCP server leverages the existing TODO-Evolution data models, specifically the `Task` and `User` entities. This ensures consistency between the FastAPI backend and MCP server while maintaining data integrity and user isolation.

---

## Core Entities

### 1. User Entity

**Source**: `backend/src/models/models.py:28-40`

```python
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
```

**Key Characteristics**:
- Primary key: `id` (integer, auto-generated)
- Unique constraint: `email` (for Better Auth integration)
- One-to-many relationship with tasks
- Managed by Better Auth authentication system

**MCP Server Usage**:
- User identification from JWT token `sub` claim
- User isolation enforcement in all queries
- Task ownership validation

### 2. Task Entity

**Source**: `backend/src/models/models.py:42-61`

```python
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
```

**Key Characteristics**:
- Primary key: `id` (integer, auto-generated)
- Foreign key: `user_id` → `user.id` (ensures user isolation)
- Completion tracking: `is_completed` boolean
- Timestamps: `created_at`, `updated_at` (auto-managed)
- Content validation: title (1-200 chars), description (max 1000 chars)

### 3. Supporting Enums

#### Priority Enum
**Source**: `backend/src/models/models.py:11-16`

```python
class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
```

**MCP Tool Usage**:
- Input validation for `add_task` and `update_task` tools
- Filtering for `list_tasks` tool
- Default value: `MEDIUM` for new tasks

#### Recurrence Pattern Enum
**Source**: `backend/src/models/models.py:19-26`

```python
class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
```

**MCP Tool Usage**:
- Optional parameter for task creation
- Future enhancement possibility for Phase IV+
- Default value: `NONE` for basic task management

---

## MCP Tool Data Mappings

### 1. add_task Tool

**Input Schema** → **Task Model Mapping**:

```python
# MCP Tool Input
{
    "title": str,           # → Task.title (1-200 chars, required)
    "description": str,     # → Task.description (max 1000 chars, optional)
    "priority": str,        # → Task.priority (enum: low/medium/high/urgent, optional)
    "due_date": str,        # → Task.due_date (ISO 8601 datetime, optional)
    "jwt_token": str        # → User context extraction
}

# Database Task Created
{
    "id": int,              # Auto-generated primary key
    "title": str,           # From input
    "description": str,     # From input or None
    "priority": Priority,   # From input or MEDIUM default
    "due_date": datetime,   # From input or None
    "is_completed": bool,   # False for new tasks
    "created_at": datetime, # Auto-generated
    "updated_at": datetime, # Auto-generated
    "user_id": int,         # From JWT token
    "recurrence_pattern": RecurrencePattern  # NONE default
}
```

### 2. list_tasks Tool

**Filter Parameters** → **SQL Query Mapping**:

```python
# MCP Tool Input
{
    "status": str,          # Filter on Task.is_completed (completed/pending/all)
    "priority": str,        # Filter on Task.priority (enum)
    "limit": int,           # LIMIT clause (1-100, default 20)
    "offset": int,          # OFFSET clause (default 0)
    "jwt_token": str        # User context + WHERE user_id clause
}

# SQL Query Example
SELECT * FROM tasks
WHERE user_id = {extracted_user_id}
  AND (is_completed = {status_filter} OR {status_filter = 'all'})
  AND (priority = '{priority_filter}' OR {priority_filter IS NULL})
ORDER BY created_at DESC
LIMIT {limit} OFFSET {offset}
```

### 3. complete_task Tool

**Input Validation** → **Database Update**:

```python
# MCP Tool Input
{
    "task_id": int,         # → WHERE Task.id = task_id AND user_id = jwt_user_id
    "jwt_token": str        # → User context extraction
}

# Database Operation
UPDATE tasks
SET is_completed = true, updated_at = NOW()
WHERE id = {task_id} AND user_id = {extracted_user_id}
RETURNING *
```

### 4. delete_task Tool

**Soft Delete Implementation**:

```python
# MCP Tool Input
{
    "task_id": int,         # → WHERE Task.id = task_id AND user_id = jwt_user_id
    "jwt_token": str        # → User context extraction
}

# Database Operation (Soft Delete)
UPDATE tasks
SET updated_at = NOW(),
    is_completed = true,
    title = '[DELETED] ' || title
WHERE id = {task_id} AND user_id = {extracted_user_id}
```

### 5. update_task Tool

**Partial Update Mapping**:

```python
# MCP Tool Input
{
    "task_id": int,         # WHERE Task.id = task_id AND user_id = jwt_user_id
    "title": str,           # Optional: SET title = {title}
    "description": str,     # Optional: SET description = {description}
    "priority": str,        # Optional: SET priority = {priority}
    "due_date": str,        # Optional: SET due_date = {due_date}
    "jwt_token": str        # User context extraction
}

# Dynamic SQL Update
UPDATE tasks
SET updated_at = NOW()
    {, title = ? if title provided}
    {, description = ? if description provided}
    {, priority = ? if priority provided}
    {, due_date = ? if due_date provided}
WHERE id = {task_id} AND user_id = {extracted_user_id}
RETURNING *
```

---

## Validation Rules

### Input Validation Constraints

| Field | Type | Required | Constraints | MCP Tool Enforcement |
|-------|------|----------|-------------|----------------------|
| title | string | Yes | 1-200 characters | All tools with title input |
| description | string | No | max 1000 characters | add_task, update_task |
| priority | string | No | enum: low/medium/high/urgent | add_task, list_tasks, update_task |
| due_date | string | No | ISO 8601 datetime format | add_task, update_task |
| task_id | integer | Yes | positive integer | complete_task, delete_task, update_task |
| status | string | No | enum: completed/pending/all | list_tasks |
| limit | integer | No | 1-100, default 20 | list_tasks |
| offset | integer | No | >= 0, default 0 | list_tasks |

### Database Constraints

**Existing Constraints** (from SQLModel):
- `tasks.user_id` → `users.id` (foreign key)
- `tasks.title` NOT NULL, length 1-200
- `tasks.description` NULLABLE, length max 1000
- `tasks.is_completed` NOT NULL, default false
- `tasks.created_at` NOT NULL, auto-generated
- `tasks.updated_at` NOT NULL, auto-updated
- `users.email` UNIQUE, length max 255

**User Isolation Enforcement**:
```python
# All queries MUST include user filter
WHERE user_id = {extracted_from_jwt_token}
```

---

## Query Patterns

### 1. User Isolation Pattern

```python
async def get_user_tasks(session: AsyncSession, user_id: int):
    """Get all tasks for a specific user."""
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.exec(statement)
    return result.all()
```

### 2. Filtering Pattern

```python
async def filter_tasks(session: AsyncSession, user_id: int,
                      status: str = None, priority: str = None):
    """Filter tasks with optional status and priority."""
    statement = select(Task).where(Task.user_id == user_id)

    if status == "completed":
        statement = statement.where(Task.is_completed == True)
    elif status == "pending":
        statement = statement.where(Task.is_completed == False)

    if priority:
        statement = statement.where(Task.priority == priority)

    return await session.exec(statement)
```

### 3. Pagination Pattern

```python
async def paginate_tasks(session: AsyncSession, user_id: int,
                        limit: int = 20, offset: int = 0):
    """Paginated task retrieval."""
    statement = (select(Task)
                 .where(Task.user_id == user_id)
                 .order_by(Task.created_at.desc())
                 .limit(limit)
                 .offset(offset))
    return await session.exec(statement)
```

### 4. Optimistic Concurrency Pattern

```python
async def update_task_safe(session: AsyncSession, task_id: int,
                          user_id: int, updates: dict):
    """Update task with user validation."""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = await session.exec(statement).first()

    if not task:
        raise ValueError("Task not found or access denied")

    for field, value in updates.items():
        if hasattr(task, field) and value is not None:
            setattr(task, field, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    await session.commit()
    return task
```

---

## Performance Considerations

### Database Indexes

**Existing Indexes** (from SQLModel):
- Primary key: `tasks.id`
- Foreign key: `tasks.user_id` (automatically indexed)
- Unique: `users.email`

**Recommended Additional Indexes**:
```sql
-- For status filtering
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, is_completed);

-- For priority filtering
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);

-- For chronological ordering
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Composite index for common queries
CREATE INDEX idx_tasks_user_status_created ON tasks(user_id, is_completed, created_at DESC);
```

### Query Optimization

**Efficient User Task Retrieval**:
```python
# Optimized query with proper indexing
statement = select(Task).where(
    Task.user_id == user_id,
    Task.is_completed == False  # Common case: pending tasks
).order_by(Task.created_at.desc()).limit(20)
```

**Batch Operations**:
```python
# For bulk operations, use batch processing
async def bulk_complete_tasks(session: AsyncSession, task_ids: List[int], user_id: int):
    """Complete multiple tasks efficiently."""
    statement = update(Task).where(
        Task.id.in_(task_ids),
        Task.user_id == user_id
    ).values(is_completed=True, updated_at=datetime.utcnow())

    result = await session.exec(statement)
    return result.rowcount
```

---

## Integration Points

### 1. FastAPI Backend Integration

**Shared Database Session**:
```python
# Use same session factory as FastAPI backend
from backend.src.dependencies.database import DbSession
from backend.src.models.models import Task, User, Priority
```

**Shared Environment Variables**:
```python
DATABASE_URL = os.getenv("DATABASE_URL")  # Same as FastAPI backend
JWT_SECRET = os.getenv("JWT_SECRET")     # Same as FastAPI backend
```

### 2. MCP Server Integration

**Tool Registration**:
```python
from fastmcp import FastMCP

mcp = FastMCP(name="Task Management Server")

@mcp.tool()
async def add_task(title: str, jwt_token: str, **kwargs):
    """Add task using shared Task model."""
    # Implementation uses Task model directly
```

**Error Handling**:
```python
# Use same error patterns as FastAPI backend
from fastapi import HTTPException

if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

---

## Migration Strategy

### No Schema Changes Required

The MCP server leverages existing database schema without modifications:

1. **Existing Models**: Use `Task` and `User` from `backend/src/models/models.py`
2. **Existing Constraints**: Foreign key relationships maintained
3. **Existing Indexes**: Basic indexes available, optimize as needed
4. **Migration Compatibility**: Works with existing Alembic migrations

### Optional Schema Enhancements (Future)

For Phase IV+ enhancements:
```sql
-- Add MCP-specific metadata
ALTER TABLE tasks ADD COLUMN mcp_created_at TIMESTAMP;
ALTER TABLE tasks ADD COLUMN mcp_updated_at TIMESTAMP;

-- Add MCP operation tracking
CREATE TABLE mcp_operations (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    user_id INTEGER REFERENCES users(id),
    operation VARCHAR(50),
    tool_name VARCHAR(100),
    correlation_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Testing Strategy

### Unit Tests

**Model Validation**:
```python
def test_task_model_validation():
    """Test Task model field validation."""
    task = Task(title="Test Task", user_id=1)
    assert task.title == "Test Task"
    assert task.priority == Priority.MEDIUM
    assert task.is_completed is False
```

**User Isolation**:
```python
async def test_user_task_isolation(session: AsyncSession):
    """Test that users can only access their own tasks."""
    user1_tasks = await get_user_tasks(session, user_id=1)
    user2_tasks = await get_user_tasks(session, user_id=2)
    assert len(set(t.id for t in user1_tasks) & set(t.id for t in user2_tasks)) == 0
```

### Integration Tests

**Database Operations**:
```python
async def test_complete_workflow(session: AsyncSession):
    """Test complete task management workflow."""
    # Create task
    task = await create_task(session, title="Test Task", user_id=1)

    # Update task
    updated = await update_task(session, task.id, user_id=1, {"priority": "high"})
    assert updated.priority == Priority.HIGH

    # Complete task
    completed = await complete_task(session, task.id, user_id=1)
    assert completed.is_completed is True
```

---

*This data model leverages the existing TODO-Evolution database schema while providing MCP-specific optimizations and validation patterns for Phase III AI Chatbot integration.*