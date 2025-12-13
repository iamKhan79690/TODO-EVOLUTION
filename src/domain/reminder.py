"""Reminder configuration for tasks."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Reminder:
    """Represents a scheduled notification for a task.
    
    Attributes:
        id: Unique identifier for the reminder
        task_id: The task this reminder is associated with
        enabled: Whether the reminder is active (default: True)
        reminder_times: Times before due date to send notification (in minutes)
        last_triggered: Last time a reminder was sent
        snooze_until: Temporary postponement of reminder
        created_at: When the reminder was created
    """
    
    id: str
    task_id: str
    enabled: bool = True
    reminder_times: List[int] = None  # Times in minutes before due date
    last_triggered: Optional[datetime] = None
    snooze_until: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate the reminder after initialization."""
        if self.reminder_times is None:
            self.reminder_times = []
            
        # Validate reminder times
        for time in self.reminder_times:
            if not isinstance(time, int) or time <= 0:
                raise ValueError(f"Each reminder time must be a positive integer, got: {time}")
                
        # Validate snooze_until is in the future
        if self.snooze_until is not None and self.snooze_until < datetime.now():
            raise ValueError("Snooze time must be in the future")
            
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def should_notify(self, current_time: datetime, due_time: datetime) -> bool:
        """Determine if a notification should be sent based on due time and reminder settings."""
        if not self.enabled or current_time < due_time:
            return False
            
        # Check if we're currently in a snoozed state
        if self.snooze_until and current_time < self.snooze_until:
            return False
            
        # Check if any of the reminder times match
        time_diff = (due_time - current_time).total_seconds() // 60  # Difference in minutes
        
        for reminder_time in self.reminder_times:
            # Allow a 1-minute margin of error
            if abs(time_diff - reminder_time) <= 1:
                # Prevent duplicate notifications
                if self.last_triggered is None or (current_time - self.last_triggered).total_seconds() > 60:
                    return True
                    
        return False
    
    def set_snooze(self, minutes: int):
        """Temporarily postpone the reminder by the specified number of minutes."""
        from datetime import timedelta
        self.snooze_until = datetime.now() + timedelta(minutes=minutes)
        
    def reset_snooze(self):
        """Reset the snooze state."""
        self.snooze_until = None