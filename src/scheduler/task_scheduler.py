"""Task scheduler for handling recurring tasks and reminders."""

import threading
import time
from datetime import datetime, timedelta
from typing import List
from ..domain.task import Task
from ..domain.task_list import TaskList
from .recurrence_service import RecurrenceService
from .reminder_service import ReminderService
from ..scheduler.cron_scheduler import CronScheduler


class TaskScheduler:
    """Manages background operations for recurring tasks and reminders."""
    
    def __init__(self, task_list: TaskList, recurrence_service: RecurrenceService, 
                 reminder_service: ReminderService):
        """Initialize TaskScheduler with required services.

        Args:
            task_list: TaskList instance to operate on
            recurrence_service: RecurrenceService instance
            reminder_service: ReminderService instance
        """
        self.task_list = task_list
        self.recurrence_service = recurrence_service
        self.reminder_service = reminder_service
        self.running = False
        self.scheduler_thread = None
        
    def start_scheduler(self):
        """Start the background scheduler."""
        if self.running:
            return  # Already running
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
    def stop_scheduler(self):
        """Stop the background scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
    
    def _scheduler_loop(self):
        """Main scheduler loop that runs in a separate thread."""
        while self.running:
            try:
                # Check for upcoming reminders every 30 seconds
                self.reminder_service.send_notifications()
                
                # Process recurring tasks - check each minute
                self._process_recurring_tasks()
                
                # Sleep for 30 seconds before next check
                time.sleep(30)
                
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
                # Continue running even if there's an error
    
    def _process_recurring_tasks(self):
        """Process any recurring tasks that need new instances generated."""
        completed_recurring_tasks = []
        
        # Find completed recurring tasks that should generate new instances
        for task in self.task_list.get_completed_tasks():
            if (task.recurrence_rule and 
                    task.recurrence_rule.should_repeat()):
                completed_recurring_tasks.append(task)
        
        # Generate new instances for these tasks
        for task in completed_recurring_tasks:
            try:
                # Generate the next instance based on the recurrence rule
                next_due_date = task.recurrence_rule.get_next_occurrence(
                    task.due_date or task.completed_at or task.created_at
                )
                
                # Create a new instance based on the completed task
                new_task_id = self.task_list.next_id
                new_task = Task(
                    id=new_task_id,
                    description=task.description,
                    is_completed=False,  # New tasks start incomplete
                    created_at=datetime.now(),
                    priority=task.priority,
                    tags=task.tags.copy() if task.tags else [],
                    due_date=next_due_date,
                    recurrence_rule=task.recurrence_rule,
                    reminder=task.reminder  # Carry over reminders to the new instance
                )
                
                # Add the new task to the list
                self.task_list.tasks[new_task_id] = new_task
                self.task_list.next_id += 1
                
            except Exception as e:
                print(f"Error generating next instance for task {task.id}: {e}")
    
    def get_upcoming_reminders(self, minutes_ahead: int = 60) -> List[Task]:
        """Get tasks that have due dates within the specified time frame.

        Args:
            minutes_ahead: Number of minutes to look ahead (default: 60)

        Returns:
            List of Task objects with due dates within the specified period
        """
        now = datetime.now()
        future_limit = now + timedelta(minutes=minutes_ahead)
        
        return [task for task in self.task_list.get_all_tasks() 
                if task.due_date and now <= task.due_date <= future_limit and not task.is_completed]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get tasks that are past their due date and still pending.

        Returns:
            List of Task objects that are overdue
        """
        now = datetime.now()
        return [task for task in self.task_list.get_all_tasks() 
                if task.due_date and task.due_date < now and not task.is_completed]