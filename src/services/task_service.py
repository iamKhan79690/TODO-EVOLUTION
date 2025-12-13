"""Task service implementing business logic for task operations."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
from ..domain.task import Task
from ..domain.task_list import TaskList
from ..domain.errors import TaskNotFound, InvalidTaskDescription, TaskLimitExceeded
from .validation import validate_task_description, validate_task_id, validate_task_limit, validate_due_date, validate_recurrence_rule, validate_reminder_settings


class TaskService:
    """Business logic layer that orchestrates operations on tasks.

    Attributes:
        task_list: The TaskList instance to operate on
    """

    def __init__(self, task_list: Optional[TaskList] = None):
        """Initialize TaskService with a TaskList.

        Args:
            task_list: TaskList instance to operate on (creates new if None)
        """
        self.task_list = task_list or TaskList()

    def create_task(self, title: str, description: str = "", priority: str = "medium", tags: List[str] = None,
                    due_date = None, recurrence_rule = None, reminder = None) -> Task:
        """Create a new task with validation.

        Args:
            title: Title of the new task (will be used as description for compatibility)
            description: Description of the new task (optional)
            priority: Priority level (high, medium, low) with default 'medium'
            tags: List of tags to categorize the task (optional)
            due_date: When the task is due (optional)
            recurrence_rule: Recurrence pattern for the task (optional)
            reminder: Reminder configuration for the task (optional)

        Returns:
            The created Task object

        Raises:
            InvalidTaskDescription: If the description is invalid
            TaskLimitExceeded: If the task limit would be exceeded
            ValueError: If due_date, recurrence_rule, or reminder are invalid
        """
        # Use title as description for compatibility with existing code
        full_description = title
        if description:
            full_description = f"{title} - {description}"

        validation_result = validate_task_description(full_description)
        if validation_result is not True:
            raise InvalidTaskDescription(validation_result)

        validation_result = validate_task_limit(len(self.task_list.tasks))
        if validation_result is not True:
            raise TaskLimitExceeded(validation_result)

        # Validate due date if provided
        if due_date:
            validation_result = validate_due_date(due_date)
            if validation_result is not True:
                raise ValueError(f"Invalid due date: {validation_result}")

        # Validate recurrence rule if provided
        if recurrence_rule:
            validation_result = validate_recurrence_rule(recurrence_rule)
            if validation_result is not True:
                raise ValueError(f"Invalid recurrence rule: {validation_result}")

        # Validate reminder settings if provided
        if reminder:
            validation_result = validate_reminder_settings(reminder)
            if validation_result is not True:
                raise ValueError(f"Invalid reminder settings: {validation_result}")

        # Check if the recurrence rule exists without a due date
        if recurrence_rule and not due_date:
            raise ValueError("Due date is required when setting a recurrence rule")

        task_id = self.task_list.add_task(
            full_description, priority, tags,
            due_date, recurrence_rule,
            reminder
        )
        return self.task_list.get_task(task_id)

    def get_task(self, task_id: int) -> Task:
        """Get a specific task.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            The requested Task object

        Raises:
            ValueError: If task_id is invalid
            TaskNotFound: If task with given ID doesn't exist
        """
        validation_result = validate_task_id(task_id)
        if validation_result is not True:
            raise ValueError(validation_result)

        task = self.task_list.get_task(task_id)
        if task is None:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        return task

    def get_all_tasks(self, sort_by: Optional[str] = None, filter_by: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks with optional sorting and filtering.

        Args:
            sort_by: Sort criteria ('priority', 'title', 'created_date', or None)
            filter_by: Filter criteria with keys like 'status', 'priority', 'tag', 'keyword'

        Returns:
            List of all Task objects
        """
        tasks = self.task_list.get_all_tasks()

        # Apply filters if provided
        if filter_by:
            if 'status' in filter_by:
                status = filter_by['status']
                if status in ['pending', 'completed']:
                    is_completed = status == 'completed'
                    tasks = [task for task in tasks if task.is_completed == is_completed]
            if 'priority' in filter_by:
                priority = filter_by['priority']
                tasks = [task for task in tasks if task.priority == priority]
            if 'tag' in filter_by:
                tag = filter_by['tag']
                tasks = [task for task in tasks if tag in task.tags]
            if 'keyword' in filter_by:
                keyword = filter_by['keyword']
                keyword_lower = keyword.lower()
                tasks = [task for task in tasks if keyword_lower in task.description.lower()]

        # Apply sorting if requested
        if sort_by == 'priority':
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            tasks = sorted(tasks, key=lambda task: priority_order[task.priority])
        elif sort_by == 'title':
            tasks = sorted(tasks, key=lambda task: task.description.lower())
        # created_date is the default ordering, so no need to sort again

        return tasks

    def mark_task_complete(self, task_id: int) -> Task:
        """Mark task as complete.

        Args:
            task_id: ID of the task to mark complete

        Returns:
            The updated Task object

        Raises:
            ValueError: If task_id is invalid
            TaskNotFound: If task with given ID doesn't exist
        """
        validation_result = validate_task_id(task_id)
        if validation_result is not True:
            raise ValueError(validation_result)

        self.task_list.complete_task(task_id)
        return self.task_list.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if the task was successfully deleted, False otherwise

        Raises:
            ValueError: If task_id is invalid
        """
        validation_result = validate_task_id(task_id)
        if validation_result is not True:
            raise ValueError(validation_result)

        try:
            return self.task_list.delete_task(task_id)
        except TaskNotFound:
            return False

    def update_task(self, task_id: int, title: str = None, description: str = None, status: str = None, priority: str = None, tags: List[str] = None,
                    due_date = None, recurrence_rule = None, reminder_settings = None) -> Task:
        """Update a task with new properties.

        Args:
            task_id: ID of the task to update
            title: New title for the task (optional)
            description: New description for the task (optional)
            status: New status for the task (pending, completed, in_progress) (optional)
            priority: New priority for the task (high, medium, low) (optional)
            tags: New tags for the task (optional)
            due_date: New due date for the task (optional)
            recurrence_rule: New recurrence pattern for the task (optional)
            reminder_settings: New reminder configuration for the task (optional)

        Returns:
            The updated Task object

        Raises:
            ValueError: If task_id or any parameter is invalid
            TaskNotFound: If task with given ID doesn't exist
            InvalidTaskDescription: If the new description is invalid
        """
        validation_result = validate_task_id(task_id)
        if validation_result is not True:
            raise ValueError(validation_result)

        # Validate due date if provided
        if due_date:
            validation_result = validate_due_date(due_date)
            if validation_result is not True:
                raise ValueError(f"Invalid due date: {validation_result}")

        # Validate recurrence rule if provided
        if recurrence_rule:
            validation_result = validate_recurrence_rule(recurrence_rule)
            if validation_result is not True:
                raise ValueError(f"Invalid recurrence rule: {validation_result}")

        # Validate reminder settings if provided
        if reminder_settings:
            validation_result = validate_reminder_settings(reminder_settings)
            if validation_result is not True:
                raise ValueError(f"Invalid reminder settings: {validation_result}")

        # Check if the recurrence rule is provided without a due date
        if recurrence_rule and not due_date:
            raise ValueError("Due date is required when updating to a recurrence rule")

        # Prepare update parameters
        new_description = None
        if title is not None and description is not None:
            new_description = f"{title} - {description}"
        elif title is not None:
            new_description = title
        elif description is not None:
            new_description = description

        # Validate description if updating
        if new_description:
            validation_result = validate_task_description(new_description)
            if validation_result is not True:
                raise InvalidTaskDescription(validation_result)

        # Validate status if updating
        if status is not None:
            valid_statuses = ['pending', 'completed', 'in_progress']
            if status not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")

        # Validate priority if updating
        if priority is not None:
            valid_priorities = ['high', 'medium', 'low']
            if priority not in valid_priorities:
                raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

        # Perform basic updates to the task
        self.task_list.update_task(task_id, new_description, priority, tags, due_date)

        # Update task with new fields specifically
        task = self.task_list.get_task(task_id)
        if due_date is not None:
            task.update_due_date(due_date)
        if recurrence_rule is not None:
            task.recurrence_rule = recurrence_rule
        if reminder_settings is not None:
            task.reminder = reminder_settings

        # Update status if specified
        if status is not None:
            if status == 'completed':
                task.complete()
            elif status == 'pending':
                task.reopen()
            elif status == 'in_progress':
                # For in_progress status, just ensure it's not completed
                if task.is_completed:
                    task.reopen()

        return self.task_list.get_task(task_id)

    # Search functionality
    def search_tasks(self, keyword: str) -> List[Task]:
        """Search tasks by keyword in title/description.

        Args:
            keyword: The search term (case-insensitive)

        Returns:
            List of matching Task objects
        """
        return self.task_list.search_tasks(keyword)

    # Filter functionality
    def filter_tasks_by_priority(self, priority: str) -> List[Task]:
        """Filter tasks by priority level.

        Args:
            priority: Priority level to filter by ('high', 'medium', 'low')

        Returns:
            List of Task objects with the specified priority
        """
        return self.task_list.filter_by_priority(priority)

    def filter_tasks_by_tag(self, tag: str) -> List[Task]:
        """Filter tasks by a specific tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of Task objects that have the specified tag
        """
        return self.task_list.filter_by_tag(tag)

    # Sort functionality
    def sort_tasks(self, sort_criteria: str) -> List[Task]:
        """Sort tasks based on the specified criteria.

        Args:
            sort_criteria: Sorting criteria ('priority', 'title')

        Returns:
            List of Task objects sorted according to criteria
        """
        if sort_criteria == 'priority':
            return self.task_list.sort_by_priority()
        elif sort_criteria == 'title':
            return self.task_list.sort_by_title()
        else:
            raise ValueError(f"Invalid sort criteria: {sort_criteria}. Valid options: 'priority', 'title'")
