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
        result = await self.session.execute(statement)
        return result.scalars().all()

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

        result = await self.session.execute(statement)
        task = result.scalars().first()

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

        result = await self.session.execute(statement)
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

        total_result = await self.session.execute(total_statement)
        completed_result = await self.session.execute(completed_statement)
        overdue_result = await self.session.execute(overdue_statement)

        return {
            "total": total_result.scalar_one_or_none() or 0,
            "completed": completed_result.scalar_one_or_none() or 0,
            "pending": (total_result.scalar_one_or_none() or 0) - (completed_result.scalar_one_or_none() or 0),
            "overdue": overdue_result.scalar_one_or_none() or 0
        }