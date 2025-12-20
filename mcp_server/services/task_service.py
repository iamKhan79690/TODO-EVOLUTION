"""
Task Service Layer for MCP Server

Business logic layer for task CRUD operations with validation, error handling,
and database integration. Handles all task-related database operations while
maintaining user isolation and data integrity.
"""

import sys
from pathlib import Path

# Ensure MCP server root is in path
MCP_ROOT = Path(__file__).parent.parent
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

# Add project root for backend imports
PROJECT_ROOT = MCP_ROOT.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.sql.expression import select as sql_select

# Import existing models from backend
try:
    from backend.src.models.models import Task, User, Priority, RecurrencePattern
except ImportError:
    # Fallback for testing without backend models
    class Priority:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        URGENT = "urgent"

    class RecurrencePattern:
        NONE = "none"
        DAILY = "daily"
        WEEKLY = "weekly"
        MONTHLY = "monthly"
        YEARLY = "yearly"

    # Mock classes for testing
    class Task:
        id = None
        title = ""
        description = ""
        priority = Priority.MEDIUM
        due_date = None
        recurrence_pattern = RecurrencePattern.NONE
        is_completed = False
        created_at = None
        updated_at = None
        user_id = None

    class User:
        id = None
        email = ""
        name = ""

from config.database_config import get_db_session
from utils.correlation_ids import with_correlation_id, get_correlation_id
from utils.exceptions import (
    ValidationError,
    TaskNotFoundError,
    TaskAlreadyCompletedError,
    DatabaseError,
    handle_exception,
    raise_validation_error
)

logger = structlog.get_logger(__name__)


class TaskService:
    """Service class for task management operations."""

    def __init__(self):
        """Initialize the task service."""
        self._session_cache = {}

    @with_correlation_id
    async def create_task(
        self,
        title: str,
        user_id: int,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[datetime] = None,
        recurrence_pattern: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Task:
        """
        Create a new task for the specified user.

        Args:
            title: Task title (1-200 characters)
            user_id: User ID who owns the task
            description: Optional task description (max 1000 characters)
            priority: Optional task priority (low, medium, high, urgent)
            due_date: Optional due date
            recurrence_pattern: Optional recurrence pattern
            correlation_id: Optional correlation ID for tracing

        Returns:
            Created Task object

        Raises:
            ValidationError: If input validation fails
            DatabaseError: If database operation fails
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Creating new task",
            correlation_id=correlation_id,
            title=title[:50],
            user_id=user_id
        )

        try:
            # Validate input parameters
            await self._validate_task_input(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                recurrence_pattern=recurrence_pattern
            )

            async with get_db_session() as session:
                try:
                    # Create task instance
                    task = Task(
                        title=title.strip(),
                        description=description.strip() if description else None,
                        priority=self._parse_priority(priority),
                        due_date=due_date,
                        recurrence_pattern=self._parse_recurrence_pattern(recurrence_pattern),
                        is_completed=False,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        user_id=user_id
                    )

                    # Save to database
                    session.add(task)
                    await session.commit()
                    await session.refresh(task)

                    logger.info(
                        "Task created successfully",
                        correlation_id=correlation_id,
                        task_id=task.id,
                        title=task.title
                    )

                    return task

                except Exception as e:
                    await session.rollback()
                    raise DatabaseError(
                        f"Failed to create task: {e}",
                        original_error=e
                    )

        except Exception as e:
            logger.error(
                "Unexpected error creating task",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise DatabaseError(
                f"Unexpected error in create_task: {e}",
                original_error=e
            )

    @with_correlation_id
    async def get_task_by_id(
        self,
        task_id: int,
        user_id: int,
        correlation_id: Optional[str] = None
    ) -> Task:
        """
        Get a task by ID for the specified user.

        Args:
            task_id: Task ID to retrieve
            user_id: User ID requesting the task
            correlation_id: Optional correlation ID for tracing

        Returns:
            Task object

        Raises:
            TaskNotFoundError: If task not found
            DatabaseError: If database operation fails
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Retrieving task by ID",
            correlation_id=correlation_id,
            task_id=task_id,
            user_id=user_id
        )

        try:
            async with get_db_session() as session:
                try:
                    # Query for task with user isolation
                    stmt = select(Task).where(
                        and_(
                            Task.id == task_id,
                            Task.user_id == user_id
                        )
                    )

                    result = await session.execute(stmt)
                    task = result.scalar_one_or_none()

                    if not task:
                        raise TaskNotFoundError(task_id)

                    logger.info(
                        "Task retrieved successfully",
                        correlation_id=correlation_id,
                        task_id=task.id,
                        title=task.title
                    )

                    return task

                except Exception as e:
                    raise DatabaseError(
                        f"Failed to retrieve task: {e}",
                        original_error=e
                    )

        except TaskNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Unexpected error retrieving task",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise DatabaseError(
                f"Unexpected error in get_task_by_id: {e}",
                original_error=e
            )

    @with_correlation_id
    async def list_tasks(
        self,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        correlation_id: Optional[str] = None
    ) -> Tuple[List[Task], int]:
        """
        List tasks for the specified user with filtering and pagination.

        Args:
            user_id: User ID to list tasks for
            status: Filter by completion status (completed, pending, all)
            priority: Filter by priority level
            limit: Maximum number of tasks to return (1-100)
            offset: Number of tasks to skip for pagination
            correlation_id: Optional correlation ID for tracing

        Returns:
            Tuple of (tasks list, total count)

        Raises:
            ValidationError: If input validation fails
            DatabaseError: If database operation fails
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Listing tasks",
            correlation_id=correlation_id,
            user_id=user_id,
            status=status,
            priority=priority,
            limit=limit,
            offset=offset
        )

        try:
            # Validate input parameters
            await self._validate_list_parameters(status, priority, limit, offset)

            async with get_db_session() as session:
                try:
                    # Build query with filters
                    query = select(Task).where(Task.user_id == user_id)

                    # Add status filter
                    if status and status != "all":
                        if status == "completed":
                            query = query.where(Task.is_completed == True)
                        elif status == "pending":
                            query = query.where(Task.is_completed == False)

                    # Add priority filter
                    if priority:
                        query = query.where(Task.priority == self._parse_priority(priority))

                    # Add ordering (newest first)
                    query = query.order_by(Task.created_at.desc())

                    # Get total count
                    count_stmt = select(func.count()).select_from(query.subquery())
                    total_count_result = await session.execute(count_stmt)
                    total_count = total_count_result.scalar()

                    # Add pagination
                    query = query.limit(limit).offset(offset)

                    # Execute query
                    result = await session.execute(query)
                    tasks = list(result.scalars().all())

                    logger.info(
                        "Tasks listed successfully",
                        correlation_id=correlation_id,
                        count=len(tasks),
                        total_count=total_count,
                        filters={"status": status, "priority": priority}
                    )

                    return tasks, total_count

                except Exception as e:
                    raise DatabaseError(
                        f"Failed to list tasks: {e}",
                        original_error=e
                    )

        except Exception as e:
            logger.error(
                "Unexpected error listing tasks",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise DatabaseError(
                f"Unexpected error in list_tasks: {e}",
                original_error=e
            )

    @with_correlation_id
    async def complete_task(
        self,
        task_id: int,
        user_id: int,
        correlation_id: Optional[str] = None
    ) -> Task:
        """
        Mark a task as completed.

        Args:
            task_id: Task ID to mark as completed
            user_id: User ID requesting the operation
            correlation_id: Optional correlation ID for tracing

        Returns:
            Updated Task object

        Raises:
            TaskNotFoundError: If task not found
            TaskAlreadyCompletedError: If task is already completed
            DatabaseError: If database operation fails
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Completing task",
            correlation_id=correlation_id,
            task_id=task_id,
            user_id=user_id
        )

        try:
            async with get_db_session() as session:
                try:
                    # Get task first to check current state
                    task = await self.get_task_by_id(task_id, user_id, correlation_id)

                    if task.is_completed:
                        raise TaskAlreadyCompletedError(task_id)

                    # Mark as completed
                    task.is_completed = True
                    task.updated_at = datetime.utcnow()

                    # Save to database
                    session.add(task)
                    await session.commit()
                    await session.refresh(task)

                    logger.info(
                        "Task completed successfully",
                        correlation_id=correlation_id,
                        task_id=task_id,
                        title=task.title
                    )

                    return task

                except Exception as e:
                    await session.rollback()
                    raise DatabaseError(
                        f"Failed to complete task: {e}",
                        original_error=e
                    )

        except (TaskNotFoundError, TaskAlreadyCompletedError):
            raise
        except Exception as e:
            logger.error(
                "Unexpected error completing task",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise DatabaseError(
                f"Unexpected error in complete_task: {e}",
                original_error=e
            )

    @with_correlation_id
    async def update_task(
        self,
        task_id: int,
        user_id: int,
        updates: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Task:
        """
        Update an existing task with partial updates.

        Args:
            task_id: Task ID to update
            user_id: User ID requesting the operation
            updates: Dictionary of fields to update
            correlation_id: Optional correlation ID for tracing

        Returns:
            Updated Task object

        Raises:
            TaskNotFoundError: If task not found
            ValidationError: If input validation fails
            DatabaseError: If database operation fails
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Updating task",
            correlation_id=correlation_id,
            task_id=task_id,
            user_id=user_id,
            update_fields=list(updates.keys())
        )

        try:
            # Validate update parameters
            await self._validate_update_parameters(updates)

            async with get_db_session() as session:
                try:
                    # Get task first
                    task = await self.get_task_by_id(task_id, user_id, correlation_id)

                    # Apply updates
                    updated = False
                    for field, value in updates.items():
                        if value is not None:
                            if field == "title":
                                if len(value.strip()) == 0:
                                    raise_validation_error(
                                        "Task title cannot be empty",
                                        field="title"
                                    )
                                if len(value) > 200:
                                    raise_validation_error(
                                        "Task title must be 200 characters or less",
                                        field="title"
                                    )
                                task.title = value.strip()
                                updated = True

                            elif field == "description":
                                if len(value) > 1000:
                                    raise_validation_error(
                                        "Task description must be 1000 characters or less",
                                        field="description"
                                    )
                                task.description = value.strip() if value else None
                                updated = True

                            elif field == "priority":
                                task.priority = self._parse_priority(value)
                                updated = True

                            elif field == "due_date":
                                if value:
                                    if isinstance(value, str):
                                        # Parse ISO 8601 datetime
                                        from dateutil.parser import parse
                                        task.due_date = parse(value)
                                    elif isinstance(value, datetime):
                                        task.due_date = value
                                else:
                                    task.due_date = None
                                updated = True

                    if not updated:
                        logger.warning(
                            "No valid updates provided for task",
                            correlation_id=correlation_id,
                            task_id=task_id
                        )
                        # Return unchanged task
                        return task

                    # Update timestamp
                    task.updated_at = datetime.utcnow()

                    # Save to database
                    session.add(task)
                    await session.commit()
                    await session.refresh(task)

                    logger.info(
                        "Task updated successfully",
                        correlation_id=correlation_id,
                        task_id=task_id,
                        title=task.title,
                        updated_fields=list(updates.keys())
                    )

                    return task

                except Exception as e:
                    await session.rollback()
                    raise DatabaseError(
                        f"Failed to update task: {e}",
                        original_error=e
                    )

        except TaskNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Unexpected error updating task",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise DatabaseError(
                f"Unexpected error in update_task: {e}",
                original_error=e
            )

    @with_correlation_id
    async def delete_task(
        self,
        task_id: int,
        user_id: int,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Soft delete a task by marking it as deleted.

        Args:
            task_id: Task ID to delete
            user_id: User ID requesting the operation
            correlation_id: Optional correlation ID for tracing

        Returns:
            True if successful, False otherwise

        Raises:
            TaskNotFoundError: If task not found
            DatabaseError: If database operation fails
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Deleting task",
            correlation_id=correlation_id,
            task_id=task_id,
            user_id=user_id
        )

        try:
            async with get_db_session() as session:
                try:
                    # Get task first
                    task = await self.get_task_by_id(task_id, user_id, correlation_id)

                    # Soft delete by marking as deleted
                    task.title = f"[DELETED] {task.title}"
                    task.updated_at = datetime.utcnow()

                    # Save to database
                    session.add(task)
                    await session.commit()

                    logger.info(
                        "Task deleted successfully (soft delete)",
                        correlation_id=correlation_id,
                        task_id=task_id,
                        original_title=task.title.replace("[DELETED] ", "")
                    )

                    return True

                except Exception as e:
                    await session.rollback()
                    raise DatabaseError(
                        f"Failed to delete task: {e}",
                        original_error=e
                    )

        except TaskNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Unexpected error deleting task",
                correlation_id=correlation_id,
                error=str(e)
            )
            raise DatabaseError(
                f"Unexpected error in delete_task: {e}",
                original_error=e
            )

    # Private helper methods

    async def _validate_task_input(
        self,
        title: str,
        description: Optional[str],
        priority: Optional[str],
        due_date: Optional[datetime],
        recurrence_pattern: Optional[str]
    ) -> None:
        """Validate task input parameters."""
        # Title validation
        if not title or title.strip() == "":
            raise_validation_error("Task title is required", field="title")
        if len(title.strip()) > 200:
            raise_validation_error("Task title must be 200 characters or less", field="title")

        # Description validation
        if description and len(description) > 1000:
            raise_validation_error(
                "Task description must be 1000 characters or less",
                field="description"
            )

        # Priority validation
        if priority and priority not in ["low", "medium", "high", "urgent"]:
            raise_validation_error(
                "Priority must be one of: low, medium, high, urgent",
                field="priority"
            )

        # Due date validation
        if due_date and not isinstance(due_date, datetime):
            raise_validation_error(
                "due_date must be a datetime object",
                field="due_date"
            )

        # Recurrence pattern validation
        if (recurrence_pattern and
            recurrence_pattern not in [
                "none", "daily", "weekly", "monthly", "yearly"
            ]):
            raise_validation_error(
                "Recurrence pattern must be one of: none, daily, weekly, monthly, yearly",
                field="recurrence_pattern"
            )

    async def _validate_list_parameters(
        self,
        status: Optional[str],
        priority: Optional[str],
        limit: int,
        offset: int
    ) -> None:
        """Validate list parameters."""
        # Status validation
        if status and status not in ["completed", "pending", "all"]:
            raise_validation_error(
                "Status must be one of: completed, pending, all",
                field="status"
            )

        # Priority validation
        if priority and priority not in ["low", "medium", "high", "urgent"]:
            raise_validation_error(
                "Priority must be one of: low, medium, high, urgent",
                field="priority"
            )

        # Limit validation
        if not (1 <= limit <= 100):
            raise_validation_error(
                "Limit must be between 1 and 100",
                field="limit"
            )

        # Offset validation
        if offset < 0:
            raise_validation_error(
                "Offset must be 0 or greater",
                field="offset"
            )

    async def _validate_update_parameters(self, updates: Dict[str, Any]) -> None:
        """Validate update parameters."""
        valid_fields = ["title", "description", "priority", "due_date"]

        for field in updates.keys():
            if field not in valid_fields:
                raise_validation_error(
                    f"Invalid field for update: {field}. Valid fields: {', '.join(valid_fields)}",
                    field=field
                )

    def _parse_priority(self, priority: Optional[str]) -> Priority:
        """Parse priority string to Priority enum."""
        if not priority:
            return Priority.MEDIUM

        priority_map = {
            "low": Priority.LOW,
            "medium": Priority.MEDIUM,
            "high": Priority.HIGH,
            "urgent": Priority.URGENT
        }

        try:
            return priority_map[priority.lower()]
        except KeyError:
            return Priority.MEDIUM  # Default fallback

    def _parse_recurrence_pattern(self, pattern: Optional[str]) -> RecurrencePattern:
        """Parse recurrence pattern string to RecurrencePattern enum."""
        if not pattern:
            return RecurrencePattern.NONE

        pattern_map = {
            "none": RecurrencePattern.NONE,
            "daily": RecurrencePattern.DAILY,
            "weekly": RecurrencePattern.WEEKLY,
            "monthly": RecurrencePattern.MONTHLY,
            "yearly": RecurrencePattern.YEARLY
        }

        try:
            return pattern_map[pattern.lower()]
        except KeyError:
            return RecurrencePattern.NONE  # Default fallback


# Global task service instance
task_service = TaskService()


# Convenience functions
async def create_task(*args, **kwargs) -> Task:
    """Convenience function to create a task."""
    return await task_service.create_task(*args, **kwargs)


async def get_task_by_id(*args, **kwargs) -> Task:
    """Convenience function to get a task by ID."""
    return await task_service.get_task_by_id(*args, **kwargs)


async def list_tasks(*args, **kwargs) -> Tuple[List[Task], int]:
    """Convenience function to list tasks."""
    return await task_service.list_tasks(*args, **kwargs)


async def complete_task(*args, **kwargs) -> Task:
    """Convenience function to complete a task."""
    return await task_service.complete_task(*args, **kwargs)


async def update_task(*args, **kwargs) -> Task:
    """Convenience function to update a task."""
    return await task_service.update_task(*args, **kwargs)


async def delete_task(*args, **kwargs) -> bool:
    """Convenience function to delete a task."""
    return await task_service.delete_task(*args, **kwargs)