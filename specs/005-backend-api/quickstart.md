# Backend API Quickstart Guide

**Feature**: 005-backend-api
**Phase**: Phase 1 - Design & Contracts
**Date**: 2025-12-07

## Overview

This guide provides step-by-step instructions for implementing the Backend API feature, which adds RESTful endpoints for task management to the existing FastAPI application with SQLModel database integration.

## Prerequisites

- Completed Phase II database setup (feature 004-database-setup)
- Working PostgreSQL database (Neon) with SQLModel models
- FastAPI application with async database connection
- Better Auth integration for user authentication
- Python 3.11+ development environment

## Implementation Steps

### Step 1: Install Additional Dependencies

Update `backend/requirements.txt` with JWT and validation libraries:

```txt
# Existing dependencies from 004-database-setup
fastapi==0.104.1
sqlmodel[asyncpg]==0.0.14
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
python-multipart==0.0.6
uvicorn[standard]==0.24.0
python-dotenv==1.0.0

# New dependencies for API implementation
python-jose[cryptography]==3.3.0  # JWT handling
passlib[bcrypt]==1.7.4            # Password hashing (if needed)
email-validator==2.1.0            # Email validation
pydantic-settings==2.1.0          # Settings management
```

Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Create Pydantic Schemas

Create `backend/src/schemas/task.py`:

```python
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


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: datetime
    version: str
    database: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: dict
    timestamp: datetime
    path: str
```

Create `backend/src/schemas/__init__.py`:

```python
"""Schemas package initialization."""

from .task import (
    Priority,
    RecurrencePattern,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    HealthResponse,
    ErrorResponse,
)

__all__ = [
    'Priority',
    'RecurrencePattern',
    'TaskCreate',
    'TaskUpdate',
    'TaskResponse',
    'TaskListResponse',
    'HealthResponse',
    'ErrorResponse',
]
```

### Step 3: Implement Authentication Dependencies

Create `backend/src/dependencies/auth.py`:

```python
"""Authentication dependencies for JWT token validation."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.database import get_session_dependency
from src.models.models import User

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session_dependency())
) -> User:
    """
    Validate JWT token and return current user.

    Args:
        credentials: HTTP Bearer credentials
        session: Database session

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: int = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Retrieve user from database
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    user = result.first()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Authenticated user

    Returns:
        User: Active user
    """
    return current_user


def verify_user_id_match(
    url_user_id: int,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Verify that URL user_id matches JWT user_id.

    Args:
        url_user_id: User ID from URL path
        current_user: Authenticated user from JWT

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If user IDs don't match
    """
    if url_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID mismatch"
        )
    return current_user
```

### Step 4: Implement Task Service Layer

Create `backend/src/services/task_service.py`:

```python
"""Task service layer for business logic."""

from typing import List, Optional
from datetime import datetime
from sqlmodel import select, update, delete, func
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from src.models.models import Task
from src.schemas.task import TaskCreate, TaskUpdate, Priority, RecurrencePattern


class TaskService:
    """Service class for task business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(self, task_create: TaskCreate, user_id: int) -> Task:
        """
        Create a new task for a user.

        Args:
            task_create: Task creation data
            user_id: Owner user ID

        Returns:
            Task: Created task

        Raises:
            HTTPException: If validation fails
        """
        # Convert Pydantic model to dict and add user_id
        task_data = task_create.model_dump()
        task_data["user_id"] = user_id

        # Create task instance
        task = Task(**task_data)

        # Save to database
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def get_user_tasks(
        self,
        user_id: int,
        completed: Optional[bool] = None,
        priority: Optional[Priority] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks for a user with optional filtering.

        Args:
            user_id: User ID
            completed: Filter by completion status
            priority: Filter by priority
            skip: Number of items to skip
            limit: Maximum items to return

        Returns:
            List[Task]: User's tasks
        """
        # Build base query
        statement = select(Task).where(Task.user_id == user_id)

        # Add filters
        if completed is not None:
            statement = statement.where(Task.is_completed == completed)

        if priority is not None:
            statement = statement.where(Task.priority == priority)

        # Add ordering and pagination
        statement = (
            statement
            .order_by(Task.priority.desc(), Task.due_date.asc().nulls_last(), Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Execute query
        result = await self.session.exec(statement)
        return result.all()

    async def get_task_by_id(self, task_id: int, user_id: int) -> Task:
        """
        Get a specific task by ID for a user.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            Task: Task instance

        Raises:
            HTTPException: If task not found
        """
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )

        result = await self.session.exec(statement)
        task = result.first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        return task

    async def update_task(
        self,
        task_id: int,
        task_update: TaskUpdate,
        user_id: int
    ) -> Task:
        """
        Update an existing task.

        Args:
            task_id: Task ID
            task_update: Update data
            user_id: User ID

        Returns:
            Task: Updated task

        Raises:
            HTTPException: If task not found
        """
        # Get existing task
        task = await self.get_task_by_id(task_id, user_id)

        # Update fields (only non-None values)
        update_data = task_update.model_dump(exclude_unset=True)

        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Update task
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        Delete a task for a user.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            bool: True if deleted

        Raises:
            HTTPException: If task not found
        """
        # Verify task exists and belongs to user
        await self.get_task_by_id(task_id, user_id)

        # Delete task
        statement = delete(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )

        result = await self.session.exec(statement)
        await self.session.commit()

        return result.rowcount > 0

    async def toggle_task_complete(self, task_id: int, user_id: int) -> Task:
        """
        Toggle task completion status.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            Task: Updated task

        Raises:
            HTTPException: If task not found
        """
        # Get existing task
        task = await self.get_task_by_id(task_id, user_id)

        # Toggle completion status
        task.is_completed = not task.is_completed
        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        return task

    async def get_user_task_stats(self, user_id: int) -> dict:
        """
        Get task statistics for a user.

        Args:
            user_id: User ID

        Returns:
            dict: Task statistics
        """
        # Count tasks by status
        total_statement = select(func.count(Task.id)).where(Task.user_id == user_id)
        completed_statement = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.is_completed == True
        )
        overdue_statement = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.is_completed == False,
            Task.due_date < datetime.utcnow()
        )

        total_result = await self.session.exec(total_statement)
        completed_result = await self.session.exec(completed_statement)
        overdue_result = await self.session.exec(overdue_statement)

        return {
            "total": total_result.first(),
            "completed": completed_result.first(),
            "pending": total_result.first() - completed_result.first(),
            "overdue": overdue_result.first()
        }
```

### Step 5: Implement Task API Routes

Create `backend/src/api/tasks.py`:

```python
"""Task API routes for CRUD operations."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_session_dependency
from src.dependencies.auth import verify_user_id_match
from src.models.models import User
from src.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    Priority,
)
from src.services.task_service import TaskService

# Create router
tasks_router = APIRouter()


@tasks_router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: int,
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(verify_user_id_match)
):
    """
    List all tasks for the authenticated user.

    Args:
        user_id: User ID (from URL)
        completed: Filter by completion status
        priority: Filter by priority level
        skip: Number of items to skip (pagination)
        limit: Maximum items to return
        session: Database session
        current_user: Authenticated user

    Returns:
        TaskListResponse: List of tasks with metadata
    """
    task_service = TaskService(session)
    tasks = await task_service.get_user_tasks(
        user_id=current_user.id,
        completed=completed,
        priority=priority,
        skip=skip,
        limit=limit
    )

    return TaskListResponse(
        tasks=tasks,
        count=len(tasks),
        user_id=current_user.id
    )


@tasks_router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    user_id: int,
    task_create: TaskCreate,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(verify_user_id_match)
):
    """
    Create a new task for the authenticated user.

    Args:
        user_id: User ID (from URL)
        task_create: Task creation data
        session: Database session
        current_user: Authenticated user

    Returns:
        TaskResponse: Created task
    """
    task_service = TaskService(session)
    task = await task_service.create_task(task_create, current_user.id)

    return TaskResponse.model_validate(task)


@tasks_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(verify_user_id_match)
):
    """
    Get a specific task by ID.

    Args:
        user_id: User ID (from URL)
        task_id: Task ID
        session: Database session
        current_user: Authenticated user

    Returns:
        TaskResponse: Task details
    """
    task_service = TaskService(session)
    task = await task_service.get_task_by_id(task_id, current_user.id)

    return TaskResponse.model_validate(task)


@tasks_router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(verify_user_id_match)
):
    """
    Update an existing task.

    Args:
        user_id: User ID (from URL)
        task_id: Task ID
        task_update: Task update data
        session: Database session
        current_user: Authenticated user

    Returns:
        TaskResponse: Updated task
    """
    task_service = TaskService(session)
    task = await task_service.update_task(task_id, task_update, current_user.id)

    return TaskResponse.model_validate(task)


@tasks_router.delete("/tasks/{task_id}")
async def delete_task(
    user_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(verify_user_id_match)
):
    """
    Delete a task.

    Args:
        user_id: User ID (from URL)
        task_id: Task ID
        session: Database session
        current_user: Authenticated user

    Returns:
        dict: Success message
    """
    task_service = TaskService(session)
    await task_service.delete_task(task_id, current_user.id)

    return {"message": "Task deleted successfully", "task_id": task_id}


@tasks_router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    user_id: int,
    task_id: int,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(verify_user_id_match)
):
    """
    Toggle task completion status.

    Args:
        user_id: User ID (from URL)
        task_id: Task ID
        session: Database session
        current_user: Authenticated user

    Returns:
        TaskResponse: Updated task
    """
    task_service = TaskService(session)
    task = await task_service.toggle_task_complete(task_id, current_user.id)

    return TaskResponse.model_validate(task)
```

### Step 6: Update Main Application

Update `backend/main.py` to include the new task routes:

```python
"""
Main FastAPI application entry point for Todo Evolution Phase II
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.api.health import health_router
from src.api.tasks import tasks_router  # Add this import
from src.core.database import create_tables, validate_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Todo Evolution API starting up...")

    # Initialize database
    try:
        # Validate database connection first
        if await validate_database_connection():
            print("Database connection validated successfully")

            # Create database tables
            await create_tables()
            print("Database initialization complete")
        else:
            print("WARNING: Database connection validation failed")
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")
        raise

    yield

    # Shutdown
    print("Todo Evolution API shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Todo Evolution API",
    description="Phase II full-stack todo application API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])  # Add this line


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Todo Evolution API - Phase II",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
```

### Step 7: Update Configuration

Update `backend/src/core/config.py` to include JWT settings:

```python
"""Application configuration settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Todo Evolution API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "localhost"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-vercel-app.vercel.app"
    ]

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/todoapp"
    DATABASE_URL_ASYNC: str = ""

    # JWT Authentication (Better Auth)
    BETTER_AUTH_SECRET: str = "your-secret-key-here"
    JWT_ALGORITHM: str = "HS256"

    # Database Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    class Config:
        env_file = ".env"


# Create settings instance
settings = Settings()
```

## Testing the Implementation

### 1. Start the Development Server

```bash
cd backend
python main.py
```

The server should start at http://localhost:8000

### 2. Verify API Documentation

Visit http://localhost:8000/docs to see the interactive Swagger documentation

### 3. Test Health Endpoint

```bash
curl http://localhost:8000/api/v1/health
```

### 4. Test Task Endpoints (with Authentication)

You'll need a valid JWT token from Better Auth to test the task endpoints:

```bash
# Example curl command with JWT token
curl -X GET "http://localhost:8000/api/123/tasks" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### 5. Test via Swagger UI

1. Visit http://localhost:8000/docs
2. Click "Authorize" and enter your JWT token
3. Test each endpoint using the interactive interface

## Validation Checklist

- [ ] Application starts without errors
- [ ] Health endpoint responds correctly
- [ ] Task endpoints appear in Swagger documentation
- [ ] JWT authentication works
- [ ] User isolation enforced (403 errors for mismatched user IDs)
- [ ] Pydantic schema validation works
- [ ] Database operations complete successfully
- [ ] Error responses return proper HTTP status codes

## Next Steps

After completing this quickstart:

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Implement the task service layer with comprehensive error handling
3. Add input validation and sanitization
4. Implement rate limiting and security measures
5. Add comprehensive logging and monitoring
6. Create unit and integration tests
7. Deploy to production environment

This quickstart provides the foundation for a production-ready backend API that follows all constitutional requirements and best practices.