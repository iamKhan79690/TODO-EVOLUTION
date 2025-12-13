"""Reminder service implementing notification logic for tasks."""

from datetime import datetime, timedelta
from typing import List, Optional
from ..domain.task import Task
from ..domain.task_list import TaskList
from ..domain.reminder import Reminder
from ..domain.errors import TaskNotFound
from .validation import validate_reminder_settings


class ReminderService:
    """Business logic layer that handles reminder scheduling and delivery."""

    def __init__(self, task_list: TaskList):
        """Initialize ReminderService with a TaskList.

        Args:
            task_list: TaskList instance to operate on
        """
        self.task_list = task_list

    def check_for_upcoming_reminders(self) -> List[Task]:
        """Check for tasks with due dates approaching and send notifications as configured.

        Returns:
            List of tasks with upcoming due dates that need notifications
        """
        current_time = datetime.now()
        upcoming_tasks = []

        # Get all pending tasks with due dates and enabled reminders
        for task in self.task_list.get_all_tasks():
            if (task.due_date and 
                not task.is_completed and 
                task.reminder and 
                task.reminder.enabled):
                
                # Check if any of the reminder times match
                time_diff = (task.due_date - current_time).total_seconds() // 60  # Difference in minutes
                
                for reminder_time in task.reminder.reminder_times:
                    # Allow a 1-minute margin of error
                    if abs(time_diff - reminder_time) <= 1:
                        # Prevent duplicate notifications
                        if (task.reminder.last_triggered is None or 
                            (current_time - task.reminder.last_triggered).total_seconds() > 60):
                            upcoming_tasks.append(task)

        return upcoming_tasks

    def send_notifications(self) -> None:
        """Send console-based notifications for tasks that need them."""
        upcoming_tasks = self.check_for_upcoming_reminders()
        
        for task in upcoming_tasks:
            # Update the last triggered timestamp
            task.reminder.last_triggered = datetime.now()
            
            # Send console notification
            print(f"🔔 REMINDER: Task '{task.description}' is due in {', '.join([str(t) for t in task.reminder.reminder_times])} minutes")

    def snooze_reminder(self, task_id: int, duration_minutes: int) -> bool:
        """Temporarily postpone a reminder for the specified duration.

        Args:
            task_id: ID of the task whose reminder to snooze
            duration_minutes: Number of minutes to delay the reminder (e.g., 15, 30, 60)

        Returns:
            Boolean indicating success
        """
        task = self.task_list.get_task(task_id)
        if not task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        if not task.reminder:
            return False  # Task has no reminder to snooze

        task.reminder.set_snooze(duration_minutes)
        return True

    def disable_reminder(self, task_id: int) -> bool:
        """Disable notifications for a specific task.

        Args:
            task_id: ID of the task whose reminder to disable

        Returns:
            Boolean indicating success
        """
        task = self.task_list.get_task(task_id)
        if not task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        if not task.reminder:
            return False  # Task has no reminder to disable

        task.reminder.enabled = False
        return True

    def enable_reminder(self, task_id: int) -> bool:
        """Enable notifications for a specific task.

        Args:
            task_id: ID of the task whose reminder to enable

        Returns:
            Boolean indicating success
        """
        task = self.task_list.get_task(task_id)
        if not task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        if not task.reminder:
            # If there's no reminder object yet, create one with default settings
            from uuid import uuid4
            reminder_id = str(uuid4())
            task.reminder = Reminder(
                id=reminder_id,
                task_id=str(task_id),
                enabled=True
            )

        task.reminder.enabled = True
        return True

    def create_reminder_for_task(self, task_id: int, reminder_times: List[int] = None, enabled: bool = True) -> Reminder:
        """Create a new reminder for a task.

        Args:
            task_id: ID of the task to create a reminder for
            reminder_times: List of times in minutes before due date to send notification
            enabled: Whether the reminder is initially enabled (default: True)

        Returns:
            The created Reminder object

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
            ValueError: If the reminder settings are invalid
        """
        task = self.task_list.get_task(task_id)
        if not task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        # Validate the reminder settings
        if reminder_times:
            for time in reminder_times:
                if not isinstance(time, int) or time <= 0:
                    raise ValueError(f"Each reminder time must be a positive integer, got: {time}")

        from uuid import uuid4
        reminder_id = str(uuid4())
        
        reminder = Reminder(
            id=reminder_id,
            task_id=str(task_id),
            enabled=enabled,
            reminder_times=reminder_times or []
        )

        # Attach the reminder to the task
        task.reminder = reminder

        return reminder

    def update_reminder_settings(self, task_id: int, reminder_times: List[int] = None, 
                                enabled: bool = None) -> Reminder:
        """Update the reminder settings for a task.

        Args:
            task_id: ID of the task whose reminder to update
            reminder_times: New list of times in minutes before due date to send notification (optional)
            enabled: Whether the reminder should be enabled (optional)

        Returns:
            The updated Reminder object

        Raises:
            TaskNotFound: If the task with the given ID doesn't exist
            ValueError: If the new reminder settings are invalid
        """
        task = self.task_list.get_task(task_id)
        if not task:
            raise TaskNotFound(f"Task with ID {task_id} does not exist")

        if not task.reminder:
            raise ValueError(f"Task with ID {task_id} has no reminder to update")

        # Update reminder times if provided
        if reminder_times is not None:
            for time in reminder_times:
                if not isinstance(time, int) or time <= 0:
                    raise ValueError(f"Each reminder time must be a positive integer, got: {time}")
            task.reminder.reminder_times = reminder_times

        # Update enabled status if provided
        if enabled is not None:
            task.reminder.enabled = enabled

        return task.reminder

    def get_all_task_reminders(self) -> List[Task]:
        """Get all tasks with reminder configurations.

        Returns:
            List of Task objects that have reminders set
        """
        return [task for task in self.task_list.get_all_tasks() 
                if task.reminder and task.reminder.enabled]