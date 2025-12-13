"""Recurrence rules for recurring tasks."""

from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Literal
from enum import Enum


class Frequency(Enum):
    """Possible recurrence frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class EndCondition(Enum):
    """Possible end conditions for recurrence."""
    NEVER = "never"
    AFTER_OCCURRENCES = "after_occurrences"
    ON_DATE = "on_date"


@dataclass
class RecurrenceRule:
    """Defines how a task repeats over time.
    
    Attributes:
        id: Unique identifier for the recurrence rule
        frequency: How often the task repeats (daily, weekly, monthly, yearly, custom)
        interval: How many frequency units between occurrences (e.g., every 2 weeks)
        days_of_week: Days of the week for weekly recurrence (mon, tue, etc.)
        day_of_month: Day of month for monthly recurrence (1-31)
        specific_time: Time of day for the recurring task (HH:MM format)
        end_condition: When the recurrence should end (never, after N occurrences, by date)
        end_count: Number of occurrences for 'after_occurrences' end condition
        end_date: Date to end recurrence for 'on_date' end condition
        created_at: When the recurrence rule was created
        exceptions: List of skipped dates for the recurrence pattern
    """
    
    id: str
    frequency: Frequency
    interval: int = 1
    days_of_week: List[str] = None  # e.g., ["mon", "fri"] for weekly
    day_of_month: Optional[int] = None  # 1-31 for monthly
    specific_time: Optional[str] = None  # HH:MM format
    end_condition: EndCondition = EndCondition.NEVER
    end_count: Optional[int] = None  # for 'after_occurrences'
    end_date: Optional[date] = None  # for 'on_date'
    created_at: Optional[datetime] = None
    exceptions: List[date] = None  # specific dates to skip
    
    def __post_init__(self):
        """Validate the recurrence rule after initialization."""
        if self.interval <= 0:
            raise ValueError("Interval must be a positive integer")
            
        # Validate days of week if frequency is weekly
        if self.frequency == Frequency.WEEKLY and not self.days_of_week:
            raise ValueError("Days of week must be specified for weekly recurrence")
            
        if self.days_of_week:
            valid_days = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
            for day in self.days_of_week:
                if day not in valid_days:
                    raise ValueError(f"Invalid day of week: {day}. Must be one of {valid_days}")
                    
        # Validate day of month if frequency is monthly
        if self.day_of_month is not None:
            if not (1 <= self.day_of_month <= 31):
                raise ValueError("Day of month must be between 1 and 31")
                
        # Validate time format if specified
        if self.specific_time:
            # Basic time format validation (HH:MM)
            try:
                hour, minute = self.specific_time.split(':')
                hour_int = int(hour)
                minute_int = int(minute)
                if not (0 <= hour_int <= 23) or not (0 <= minute_int <= 59):
                    raise ValueError("Hour must be 0-23 and minute must be 0-59")
            except (ValueError, AttributeError):
                raise ValueError(f"Time format must be HH:MM (e.g., '09:30'), got: {self.specific_time}")
                
        # Validate end condition specifics
        if self.end_condition == EndCondition.AFTER_OCCURRENCES and not self.end_count:
            raise ValueError("End count must be specified when end condition is 'after_occurrences'")
        elif self.end_condition == EndCondition.ON_DATE and not self.end_date:
            raise ValueError("End date must be specified when end condition is 'on_date'")
            
        if self.end_count is not None and self.end_count <= 0:
            raise ValueError("End count must be a positive integer")
            
        if self.created_at is None:
            self.created_at = datetime.now()
            
        if self.days_of_week is None:
            self.days_of_week = []
            
        if self.exceptions is None:
            self.exceptions = []
    
    def should_repeat(self) -> bool:
        """Determine if the recurrence should continue based on end conditions."""
        if self.end_condition == EndCondition.NEVER:
            return True
        # Additional logic would be needed here to check occurrences or date
        # This is simplified for now
        return True
    
    def get_next_occurrence(self, last_occurrence: datetime) -> datetime:
        """Calculate the next occurrence based on this rule and the last occurrence."""
        # This is a simplified implementation - a full implementation would be more complex
        # depending on the frequency type
        if self.frequency == Frequency.DAILY:
            # Move to next day (or next N days based on interval)
            from datetime import timedelta
            return last_occurrence + timedelta(days=self.interval)
        elif self.frequency == Frequency.WEEKLY:
            # Move to same weekday of next week (or next N weeks)
            from datetime import timedelta
            return last_occurrence + timedelta(weeks=self.interval)
        elif self.frequency == Frequency.MONTHLY:
            # Move to same day of next month (or next N months)
            # This is simplified - would need to handle month boundaries properly
            import calendar
            next_month = last_occurrence.month + self.interval
            year = last_occurrence.year
            while next_month > 12:
                year += 1
                next_month -= 12
            # Adjust day if it exceeds days in target month
            max_day = calendar.monthrange(year, next_month)[1]
            day = min(self.day_of_month or last_occurrence.day, max_day)
            return last_occurrence.replace(year=year, month=next_month, day=day)
        elif self.frequency == Frequency.YEARLY:
            # Move to same date of next year (or next N years)
            return last_occurrence.replace(year=last_occurrence.year + self.interval)
        else:  # CUSTOM
            # For custom, interpret interval as days
            from datetime import timedelta
            return last_occurrence + timedelta(days=self.interval)