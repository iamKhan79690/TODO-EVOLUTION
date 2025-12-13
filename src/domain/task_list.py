"""TaskList domain model representing a collection of todo items."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .task import Task
from .errors import TaskNotFound, InvalidTaskDescription, TaskLimitExceeded


class TaskList:
    """Collection of tasks with operations to manage them.

    Attributes:
        tasks: Dictionary mapping task IDs to Task objects
        next_id: Next available ID for new tasks (auto-incrementing)
        max_tasks: Maximum number of tasks allowed in the list
    """

    def __init__(self, max_tasks: int = 1000):
        """Initialize a TaskList with a maximum capacity.

        Args:
            max_tasks: Maximum number of tasks allowed (default: 1000)
        """
        self.tasks: Dict[int, Task] = {}
        self.next_id: int = 1
        self.max_tasks = max_tasks

    def add_task(self, description: str, priority: str = 'medium', tags: List[str] = None, due_date: datetime = None,
                 recurrence_rule = None, reminder = None) -> int:
        """Add a new task and return its ID.

        Args:
            description: Description of the task to add
            priority: Priority level for the task (default: 'medium')
            tags: List of tags for categorizing the task (default: [])
            due_date: When the task is due (default: None)
            recurrence_rule: Recurrence pattern for recurring tasks (default: None)
            reminder: Reminder configuration for the task (default: None)

        Returns:
            ID of the newly created task

        Raises:
            TaskLimitExceeded: If maximum task count would be exceeded
            InvalidTaskDescription: If description is invalid
        """
        if len(self.tasks) >= self.max_tasks:
            raise TaskLimitExceeded(f"Cannot exceed maximum of {self.max_tasks} tasks")

        if not description or not description.strip():
            raise InvalidTaskDescription(
                "Task description cannot be empty or contain only whitespace"
            )

        if len(description) > 2000:
            raise InvalidTaskDescription(
                "Task description must be less than 2000 characters"
            )

        task_id = self.next_id
        task = Task(id=task_id, description=description, priority=priority, tags=tags or [],
                    due_date=due_date, recurrence_rule=recurrence_rule, reminder=reminder)
        self.tasks[task_id] = task
        self.next_id += 1

        return task_id

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks in the list.

        Returns:
            List of all Task objects
        """
        return list(self.tasks.values())

    def get_pending_tasks(self) -> List[Task]:
        """Get only incomplete tasks.

        Returns:
            List of Task objects with is_completed=False
        """
        return [task for task in self.tasks.values() if not task.is_completed]

    def get_completed_tasks(self) -> List[Task]:
        """Get only completed tasks.

        Returns:
            List of Task objects with is_completed=True
        """
        return [task for task in self.tasks.values() if task.is_completed]

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as complete (returns success).

        Args:
            task_id: ID of the task to complete

        Returns:
            True if the task was successfully completed

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
        """
        if task_id not in self.tasks:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        task = self.tasks[task_id]
        task.complete()

        # If this is a recurring task, generate the next instance
        if task.recurrence_rule and task.recurrence_rule.should_repeat():
            # Create a new instance based on the recurrence rule
            next_due_date = task.recurrence_rule.get_next_occurrence(task.due_date or datetime.now())
            # In a real implementation, this would add a new task based on the template
            # For now, we just complete this task and leave the next one to be generated separately

        return True

    def delete_task(self, task_id: int) -> bool:
        """Remove a task from the list (returns success).

        Args:
            task_id: ID of the task to delete

        Returns:
            True if the task was successfully deleted

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
        """
        if task_id not in self.tasks:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        del self.tasks[task_id]
        return True

    def update_task(self, task_id: int, new_description: str = None, new_priority: str = None,
                    new_tags: List[str] = None, new_due_date: datetime = None) -> bool:
        """Update task properties (returns success).

        Args:
            task_id: ID of the task to update
            new_description: New description for the task (optional)
            new_priority: New priority for the task (optional)
            new_tags: New list of tags for the task (optional)
            new_due_date: New due date for the task (optional)

        Returns:
            True if the task was successfully updated

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
            InvalidTaskDescription: If the new description is invalid
        """
        if task_id not in self.tasks:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        task = self.tasks[task_id]

        if new_description is not None:
            if not new_description or not new_description.strip():
                raise InvalidTaskDescription(
                    "Task description cannot be empty or contain only whitespace"
                )

            if len(new_description) > 2000:
                raise InvalidTaskDescription(
                    "Task description must be less than 2000 characters"
                )

            task.update_description(new_description)

        if new_priority is not None:
            task.update_priority(new_priority)

        if new_tags is not None:
            task.update_tags(new_tags)

        if new_due_date is not None:
            task.update_due_date(new_due_date)

        return True

    # Search functionality
    def search_tasks(self, keyword: str) -> List[Task]:
        """Search tasks by keyword in description (case-insensitive).

        Args:
            keyword: Keyword to search for in task descriptions

        Returns:
            List of Task objects that match the keyword
        """
        if not keyword:
            return []

        keyword_lower = keyword.lower()
        matching_tasks = []

        for task in self.tasks.values():
            if keyword_lower in task.description.lower():
                matching_tasks.append(task)

        return matching_tasks

    # Filter functionality
    def filter_by_priority(self, priority: str) -> List[Task]:
        """Filter tasks by priority level.

        Args:
            priority: Priority level to filter by ('high', 'medium', 'low')

        Returns:
            List of Task objects with the specified priority
        """
        valid_priorities = ['high', 'medium', 'low']
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

        return [task for task in self.tasks.values() if task.priority == priority]

    def filter_by_tag(self, tag: str) -> List[Task]:
        """Filter tasks by a specific tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of Task objects that have the specified tag
        """
        return [task for task in self.tasks.values() if tag in task.tags]

    def filter_by_status(self, is_completed: bool) -> List[Task]:
        """Filter tasks by status.

        Args:
            is_completed: If True, return completed tasks; if False, return pending tasks

        Returns:
            List of Task objects with the specified status
        """
        return [task for task in self.tasks.values() if task.is_completed == is_completed]

    # Sort functionality
    def sort_by_priority(self) -> List[Task]:
        """Sort tasks by priority (high -> medium -> low).

        Returns:
            List of Task objects sorted by priority
        """
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        return sorted(self.tasks.values(), key=lambda task: priority_order[task.priority])

    def sort_by_title(self) -> List[Task]:
        """Sort tasks by title/description alphabetically.

        Returns:
            List of Task objects sorted by description
        """
        return sorted(self.tasks.values(), key=lambda task: task.description.lower())

    def sort_by_due_date(self) -> List[Task]:
        """Sort tasks by due date (earliest to latest, tasks without due dates last).

        Returns:
            List of Task objects sorted by due date
        """
        def sort_key(task):
            # If task has no due date, sort it to the end (return a far future date)
            if task.due_date is None:
                # Use a date far in the future to put tasks without due dates at the end
                return datetime.max
            return task.due_date

        return sorted(self.tasks.values(), key=sort_key)

    # Time-based queries
    def get_overdue_tasks(self) -> List[Task]:
        """Get tasks that are past their due date and still pending.

        Returns:
            List of Task objects that are overdue
        """
        now = datetime.now()
        return [task for task in self.tasks.values()
                if task.due_date and task.due_date < now and not task.is_completed]

    def get_upcoming_tasks(self, days_ahead: int = 7) -> List[Task]:
        """Get tasks due within the specified number of days.

        Args:
            days_ahead: Number of days to look ahead (default: 7)

        Returns:
            List of Task objects due within the specified period
        """
        now = datetime.now()
        future_limit = now + timedelta(days=days_ahead)

        return [task for task in self.tasks.values()
                if task.due_date and now <= task.due_date <= future_limit and not task.is_completed]

    def get_tasks_with_reminders(self) -> List[Task]:
        """Get tasks that have reminder configurations.

        Returns:
            List of Task objects that have reminders set
        """
        return [task for task in self.tasks.values() if task.reminder and task.reminder.enabled]

    def get_recurring_tasks(self) -> List[Task]:
        """Get tasks that have recurrence rules.

        Returns:
            List of Task objects that are recurring
        """
        return [task for task in self.tasks.values() if task.recurrence_rule]
