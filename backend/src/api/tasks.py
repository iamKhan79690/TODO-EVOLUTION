"""Task API routes for CRUD operations."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.database import get_session_dependency
from src.dependencies.auth import get_current_active_user
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
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to return"),
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all tasks for the authenticated user.

    Args:
        completed: Filter by completion status
        priority: Filter by priority level
        skip: Number of items to skip (pagination)
        limit: Maximum items to return
        session: Database session
        current_user: Authenticated user from JWT

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
    task_create: TaskCreate,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new task for the authenticated user.

    Args:
        task_create: Task creation data
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        TaskResponse: Created task
    """
    task_service = TaskService(session)
    task = await task_service.create_task(task_create, current_user.id)

    return TaskResponse.model_validate(task)


@tasks_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        TaskResponse: Task details
    """
    task_service = TaskService(session)
    task = await task_service.get_task_by_id(task_id, current_user.id)

    return TaskResponse.model_validate(task)


@tasks_router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing task.

    Args:
        task_id: Task ID
        task_update: Task update data
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        TaskResponse: Updated task
    """
    task_service = TaskService(session)
    task = await task_service.update_task(task_id, task_update, current_user.id)

    return TaskResponse.model_validate(task)


@tasks_router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def patch_task(
    task_id: int,
    task_update: TaskUpdate,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(get_current_active_user)
):
    """
    Partially update an existing task.

    Args:
        task_id: Task ID
        task_update: Task update data
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        TaskResponse: Updated task
    """
    task_service = TaskService(session)
    task = await task_service.update_task(task_id, task_update, current_user.id)

    return TaskResponse.model_validate(task)


@tasks_router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a task.

    Args:
        task_id: Task ID
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        dict: Success message
    """
    task_service = TaskService(session)
    await task_service.delete_task(task_id, current_user.id)

    return {"message": "Task deleted successfully", "task_id": task_id}


@tasks_router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: int,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(get_current_active_user)
):
    """
    Toggle task completion status.

    Args:
        task_id: Task ID
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        TaskResponse: Updated task
    """
    task_service = TaskService(session)
    task = await task_service.toggle_task_complete(task_id, current_user.id)

    return TaskResponse.model_validate(task)