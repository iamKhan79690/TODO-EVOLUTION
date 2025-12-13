"""Recurrence service implementing logic for recurring tasks."""

from typing import List, Optional
from ..domain.task import Task
from ..domain.task_list import TaskList
from ..domain.recurrence_rule import RecurrenceRule
from ..domain.errors import TaskNotFound, InvalidTaskDescription, TaskLimitExceeded
from .validation import validate_recurrence_rule


class RecurrenceService:
    """Business logic layer that handles recurrence patterns and rules."""

    def __init__(self, task_list: TaskList):
        """Initialize RecurrenceService with a TaskList.

        Args:
            task_list: TaskList instance to operate on
        """
        self.task_list = task_list

    def create_recurring_task(self, description: str, priority: str = "medium", tags: List[str] = None, 
                              due_date = None, recurrence_rule: RecurrenceRule = None) -> Task:
        """Create a recurring task with validation.

        Args:
            description: Description of the new recurring task
            priority: Priority level (default: 'medium')
            tags: List of tags for categorizing the task (default: [])
            due_date: Due date for the task
            recurrence_rule: Recurrence pattern for the task

        Returns:
            The created recurring Task object

        Raises:
            InvalidTaskDescription: If the description is invalid
            TaskLimitExceeded: If the task limit would be exceeded
            ValueError: If recurrence rule is invalid
        """
        from datetime import datetime
        if due_date and due_date < datetime.now():
            raise ValueError("Due date must be in the future")

        validation_result = validate_recurrence_rule(recurrence_rule)
        if validation_result is not True:
            raise ValueError(f"Invalid recurrence rule: {validation_result}")

        if not description or not description.strip():
            raise InvalidTaskDescription(
                "Task description cannot be empty or contain only whitespace"
            )

        if len(description) > 2000:
            raise InvalidTaskDescription(
                "Task description must be less than 2000 characters"
            )

        task_id = self.task_list.add_task(description, priority, tags or [], due_date, recurrence_rule)
        return self.task_list.get_task(task_id)

    def generate_next_instance(self, task_id: int) -> Task:
        """Generate the next instance of a recurring task based on its recurrence rule.

        Args:
            task_id: ID of the recurring task template

        Returns:
            New Task instance based on the recurrence rule

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
            ValueError: If the task is not a recurring task
        """
        template_task = self.task_list.get_task(task_id)
        if not template_task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        if not template_task.recurrence_rule:
            raise ValueError(f"Task with ID {task_id} is not a recurring task")

        # Check if the recurrence pattern allows for another instance
        if not template_task.recurrence_rule.should_repeat():
            raise ValueError(f"Recurrence pattern for task {task_id} has ended")

        # Calculate the next due date based on the recurrence rule
        next_due_date = template_task.recurrence_rule.get_next_occurrence(
            template_task.due_date or template_task.created_at
        )

        # Create a new task instance with the same properties as the template
        # but with a new ID and the next due date
        new_task_id = self.task_list.next_id
        new_task = Task(
            id=new_task_id,
            description=template_task.description,
            priority=template_task.priority,
            tags=template_task.tags.copy(),
            due_date=next_due_date,
            recurrence_rule=template_task.recurrence_rule
        )
        
        # Add the new instance to the task list
        self.task_list.tasks[new_task_id] = new_task
        self.task_list.next_id += 1

        return new_task

    def update_recurrence_pattern(self, task_id: int, new_pattern: RecurrenceRule) -> Task:
        """Update the recurrence pattern for a recurring task.

        Args:
            task_id: ID of the recurring task to update
            new_pattern: New recurrence pattern

        Returns:
            The updated Task object

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
            ValueError: If the new pattern is invalid
        """
        validation_result = validate_recurrence_rule(new_pattern)
        if validation_result is not True:
            raise ValueError(f"Invalid recurrence rule: {validation_result}")

        task = self.task_list.get_task(task_id)
        if not task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        if not task.recurrence_rule:
            raise ValueError(f"Task with ID {task_id} is not a recurring task")

        # Update the recurrence rule
        task.recurrence_rule = new_pattern

        return task

    def skip_recurring_instance(self, task_id: int) -> bool:
        """Mark a recurring task instance to be skipped.

        Args:
            task_id: ID of the recurring task instance to skip

        Returns:
            True if the task instance was successfully marked for skipping

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
        """
        task = self.task_list.get_task(task_id)
        if not task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        if not task.recurrence_rule:
            raise ValueError(f"Task with ID {task_id} is not a recurring task")

        # In this implementation, we'll consider "skipping" as completing without generating a new instance
        # This would be handled differently in a more comprehensive system
        # For now, we'll just mark it as complete
        task.complete()
        
        # Don't generate the next instance as it was skipped
        return True

    def modify_recurring_instance(self, task_id: int, updates: dict) -> Task:
        """Modify a specific instance of a recurring task without affecting the overall pattern.

        Args:
            task_id: ID of the recurring task instance to modify
            updates: Dictionary of updates to apply

        Returns:
            The modified Task object

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
            ValueError: If the updates contain invalid values
        """
        task = self.task_list.get_task(task_id)
        if not task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        if not task.recurrence_rule:
            raise ValueError(f"Task with ID {task_id} is not a recurring task")

        # Apply updates based on the provided keys
        for key, value in updates.items():
            if key == 'due_date':
                from datetime import datetime
                if value < datetime.now():
                    raise ValueError("Due date must be in the future")
                task.update_due_date(value)
            elif key == 'title' or key == 'description':
                task.update_description(value)
            elif key == 'priority':
                from .validation import validate_priority
                validation_result = validate_priority(value)
                if validation_result is not True:
                    raise ValueError(f"Invalid priority: {validation_result}")
                task.update_priority(value)
            elif key == 'tags':
                from .validation import validate_tags
                validation_result = validate_tags(value)
                if validation_result is not True:
                    raise ValueError(f"Invalid tags: {validation_result}")
                task.update_tags(value)
            else:
                # For unsupported properties, raise an error
                raise ValueError(f"Unsupported property for update: {key}")

        return task

    def get_recurring_task_instances(self, task_template_id: int, start_date, end_date) -> List[Task]:
        """Get all instances of a recurring task within the specified date range.

        Args:
            task_template_id: ID of the recurring task template
            start_date: Start of date range to retrieve instances
            end_date: End of date range to retrieve instances

        Returns:
            List of Task objects that are instances of the recurring task in the date range
        """
        # This is a simplified implementation
        # In a real implementation, we would need to generate all instances 
        # that would have existed in the given date range according to the recurrence rule
        
        # For now, return tasks that match the template and have due dates in range
        result = []
        for task in self.task_list.get_all_tasks():
            # Check if this task is part of the recurring series by matching description and recurrence rule
            if (task.recurrence_rule and 
                task.id >= task_template_id and  # Simplified check
                task.due_date and 
                start_date <= task.due_date <= end_date):
                result.append(task)
        
        return result