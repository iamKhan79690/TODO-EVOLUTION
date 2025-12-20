"""
Database service layer for MCP server operations.

This module provides high-level database operations for the MCP tools,
handling Task and User model interactions with proper error handling
and transaction management.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, update, delete
from src.database import get_session
from src.models.models import Task, User, TaskStatus, Priority

logger = logging.getLogger(__name__)

class TaskService:
    """Service class for task-related database operations."""

    @staticmethod
    async def create_task(
        user_id: int,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        due_date: Optional[datetime] = None
    ) -> Task:
        """
        Create a new task for a user.

        Args:
            user_id: ID of the user creating the task
            title: Task title (required)
            description: Optional task description
            priority: Task priority level
            due_date: Optional due date

        Returns:
            Created Task object

        Raises:
            ValueError: If title is empty or too long
            DatabaseError: If database operation fails
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")

        if len(title) > 255:
            raise ValueError("Task title cannot exceed 255 characters")

        if description and len(description) > 2000:
            raise ValueError("Task description cannot exceed 2000 characters")

        try:
            async with get_session() as session:
                task = Task(
                    user_id=user_id,
                    title=title.strip(),
                    description=description.strip() if description else None,
                    priority=priority,
                    due_date=due_date,
                    status=TaskStatus.PENDING,
                    created_at=datetime.utcnow()
                )

                session.add(task)
                await session.commit()
                await session.refresh(task)

                logger.info(f"Created task {task.id} for user {user_id}: {title}")
                return task

        except Exception as e:
            logger.error(f"Failed to create task for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def get_user_tasks(
        user_id: int,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Task]:
        """
        Get tasks for a user with optional filtering.

        Args:
            user_id: ID of the user
            status: Optional status filter (pending, in_progress, completed, cancelled, all)
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            include_deleted: Whether to include soft-deleted tasks

        Returns:
            List of Task objects

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            async with get_session() as session:
                # Build base query
                query = select(Task).where(Task.user_id == user_id)

                # Apply status filter
                if status and status.lower() != "all":
                    try:
                        task_status = TaskStatus(status.lower())
                        query = query.where(Task.status == task_status)
                    except ValueError:
                        # Invalid status, ignore filter
                        logger.warning(f"Invalid status filter: {status}")

                # Apply soft delete filter
                if not include_deleted:
                    query = query.where(Task.is_deleted == False)

                # Apply ordering and pagination
                query = query.order_by(Task.created_at.desc())
                query = query.offset(offset).limit(limit)

                result = await session.exec(query)
                tasks = result.all()

                logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
                return tasks

        except Exception as e:
            logger.error(f"Failed to get tasks for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def get_task_by_id(task_id: int, user_id: int) -> Optional[Task]:
        """
        Get a specific task by ID for a user.

        Args:
            task_id: ID of the task
            user_id: ID of the user requesting the task

        Returns:
            Task object if found and owned by user, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            async with get_session() as session:
                query = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id,
                    Task.is_deleted == False
                )

                result = await session.exec(query)
                task = result.first()

                return task

        except Exception as e:
            logger.error(f"Failed to get task {task_id} for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def update_task(
        task_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Task]:
        """
        Update a task with new values.

        Args:
            task_id: ID of the task to update
            user_id: ID of the user updating the task
            updates: Dictionary of fields to update

        Returns:
            Updated Task object if found and owned by user, None otherwise

        Raises:
            ValueError: If update data is invalid
            DatabaseError: If database operation fails
        """
        # Validate updates
        allowed_fields = {
            'title': str,
            'description': (str, type(None)),
            'priority': Priority,
            'due_date': (datetime, type(None))
        }

        for field, value in updates.items():
            if field not in allowed_fields:
                raise ValueError(f"Invalid field: {field}")

            expected_types = allowed_fields[field]
            if not isinstance(value, expected_types):
                raise ValueError(f"Invalid type for {field}: expected {expected_types}")

            # Additional validation
            if field == 'title':
                if not value or not value.strip():
                    raise ValueError("Task title cannot be empty")
                if len(value) > 255:
                    raise ValueError("Task title cannot exceed 255 characters")

            if field == 'description' and value and len(value) > 2000:
                raise ValueError("Task description cannot exceed 2000 characters")

        try:
            async with get_session() as session:
                # Get existing task
                task = await TaskService.get_task_by_id(task_id, user_id)
                if not task:
                    return None

                # Update fields
                update_data = updates.copy()
                update_data['updated_at'] = datetime.utcnow()

                # Apply updates
                for field, value in update_data.items():
                    setattr(task, field, value)

                session.add(task)
                await session.commit()
                await session.refresh(task)

                logger.info(f"Updated task {task_id} for user {user_id}")
                return task

        except Exception as e:
            logger.error(f"Failed to update task {task_id} for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def complete_task(task_id: int, user_id: int) -> Optional[Task]:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to complete
            user_id: ID of the user completing the task

        Returns:
            Updated Task object if found and owned by user, None otherwise

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            async with get_session() as session:
                # Get existing task
                task = await TaskService.get_task_by_id(task_id, user_id)
                if not task:
                    return None

                # Check if already completed
                if task.status == TaskStatus.COMPLETED:
                    logger.warning(f"Task {task_id} is already completed")
                    return task

                # Update task
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.updated_at = datetime.utcnow()

                session.add(task)
                await session.commit()
                await session.refresh(task)

                logger.info(f"Completed task {task_id} for user {user_id}")
                return task

        except Exception as e:
            logger.error(f"Failed to complete task {task_id} for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def delete_task(task_id: int, user_id: int) -> bool:
        """
        Soft delete a task.

        Args:
            task_id: ID of the task to delete
            user_id: ID of the user deleting the task

        Returns:
            True if task was deleted, False if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            async with get_session() as session:
                # Get existing task
                task = await TaskService.get_task_by_id(task_id, user_id)
                if not task:
                    return False

                # Soft delete
                task.is_deleted = True
                task.updated_at = datetime.utcnow()

                session.add(task)
                await session.commit()

                logger.info(f"Deleted task {task_id} for user {user_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to delete task {task_id} for user {user_id}: {str(e)}")
            raise

    @staticmethod
    async def get_task_statistics(user_id: int) -> Dict[str, int]:
        """
        Get task statistics for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with task counts by status

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            async with get_session() as session:
                # Count tasks by status
                from sqlmodel import func

                stats_query = select(
                    Task.status,
                    func.count(Task.id).label('count')
                ).where(
                    Task.user_id == user_id,
                    Task.is_deleted == False
                ).group_by(Task.status)

                result = await session.exec(stats_query)
                stats = dict(result.all())

                # Convert status to strings and ensure all statuses are present
                status_counts = {
                    "pending": 0,
                    "in_progress": 0,
                    "completed": 0,
                    "cancelled": 0
                }

                for status, count in stats.items():
                    if status.value in status_counts:
                        status_counts[status.value] = count

                return status_counts

        except Exception as e:
            logger.error(f"Failed to get task statistics for user {user_id}: {str(e)}")
            raise