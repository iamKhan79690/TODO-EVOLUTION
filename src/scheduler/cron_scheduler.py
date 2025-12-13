"""Cron-like scheduler for recurrence patterns using croniter library."""

from datetime import datetime, timedelta
from typing import Optional
import croniter
from ..domain.recurrence_rule import RecurrenceRule, Frequency


class CronScheduler:
    """Provides cron-like scheduling capabilities for recurring tasks."""
    
    def __init__(self):
        """Initialize the CronScheduler."""
        pass
    
    def convert_frequency_to_cron(self, recurrence_rule: RecurrenceRule) -> str:
        """Convert our recurrence rule to a cron expression.

        Args:
            recurrence_rule: RecurrenceRule object to convert

        Returns:
            Cron expression string
        """
        # Default to '* * * * *' (every minute) as a base
        minute = "0"  # Default to the top of the hour
        hour = recurrence_rule.specific_time.split(':')[0] if recurrence_rule.specific_time else "*"
        
        if recurrence_rule.frequency == Frequency.DAILY:
            # Daily: run once per day at the specified time
            return f"{minute} {hour} * * *"
        
        elif recurrence_rule.frequency == Frequency.WEEKLY:
            # Weekly: run on specific days of the week
            # Cron days: 0=Sunday, 1=Monday, etc.
            days_map = {"mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6, "sun": 0}
            days_numbers = [str(days_map[day]) for day in recurrence_rule.days_of_week]
            days_part = ','.join(days_numbers)
            return f"{minute} {hour} * * {days_part}"
        
        elif recurrence_rule.frequency == Frequency.MONTHLY:
            # Monthly: run on specific day of the month
            day_of_month = recurrence_rule.day_of_month or 1
            return f"{minute} {hour} {day_of_month} * *"
        
        elif recurrence_rule.frequency == Frequency.YEARLY:
            # Yearly: run on specific day and month
            day_of_month = recurrence_rule.day_of_month or 1
            # For yearly, we'll use the creation month or January if not specified
            # This is a simplification - real implementation might take the original task creation month
            return f"{minute} {hour} {day_of_month} 1 *"
        
        elif recurrence_rule.frequency == Frequency.CUSTOM:
            # For custom, interpret interval as days
            # This is a simplified approach - a full implementation would be more complex
            # For now, if interval is 1, run daily; if 7, run weekly; etc.
            if recurrence_rule.interval == 1:
                return f"{minute} {hour} * * *"
            elif recurrence_rule.interval == 7:
                return f"{minute} {hour} * * 1"  # Weekly on Monday
            else:
                # For other intervals, use daily and let the system handle the interval
                return f"{minute} {hour} * * *"
        
        # Default case
        return f"{minute} {hour} * * *"
    
    def get_next_occurrence(self, recurrence_rule: RecurrenceRule, from_datetime: datetime = None) -> datetime:
        """Calculate the next occurrence of a recurring task.

        Args:
            recurrence_rule: RecurrenceRule object defining the recurrence pattern
            from_datetime: Datetime to calculate from (default: current time)

        Returns:
            datetime object representing the next occurrence
        """
        if from_datetime is None:
            from_datetime = datetime.now()
        
        try:
            # Convert the recurrence rule to a cron expression
            cron_expression = self.convert_frequency_to_cron(recurrence_rule)
            
            # Use croniter to find the next occurrence
            cron_iter = croniter.croniter(cron_expression, from_datetime)
            next_occurrence = cron_iter.get_next(datetime)
            
            return next_occurrence
        except Exception as e:
            # In case of error with croniter, fall back to our basic calculation
            print(f"Croniter error: {e}. Falling back to basic calculation.")
            return self._basic_calculation(recurrence_rule, from_datetime)
    
    def _basic_calculation(self, recurrence_rule: RecurrenceRule, from_datetime: datetime) -> datetime:
        """Basic calculation method as fallback if croniter fails."""
        # This is a simplified version that mimics what we had in the RecurrenceRule
        if recurrence_rule.frequency == Frequency.DAILY:
            # Move to next day (or next N days based on interval)
            from datetime import timedelta
            return from_datetime + timedelta(days=recurrence_rule.interval)
        elif recurrence_rule.frequency == Frequency.WEEKLY:
            # Move to same weekday of next week (or next N weeks)
            from datetime import timedelta
            return from_datetime + timedelta(weeks=recurrence_rule.interval)
        elif recurrence_rule.frequency == Frequency.MONTHLY:
            # Move to same day of next month (or next N months)
            # This is simplified - would need to handle month boundaries properly
            import calendar
            next_month = from_datetime.month + recurrence_rule.interval
            year = from_datetime.year
            while next_month > 12:
                year += 1
                next_month -= 12
            # Adjust day if it exceeds days in target month
            max_day = calendar.monthrange(year, next_month)[1]
            day = min(recurrence_rule.day_of_month or from_datetime.day, max_day)
            return from_datetime.replace(year=year, month=next_month, day=day)
        elif recurrence_rule.frequency == Frequency.YEARLY:
            # Move to same date of next year (or next N years)
            return from_datetime.replace(year=from_datetime.year + recurrence_rule.interval)
        else:  # CUSTOM
            # For custom, interpret interval as days
            from datetime import timedelta
            return from_datetime + timedelta(days=recurrence_rule.interval)
    
    def calculate_occurrences_in_range(self, recurrence_rule: RecurrenceRule, 
                                     start_date: datetime, end_date: datetime) -> List[datetime]:
        """Calculate all occurrences of a recurring task within a date range.

        Args:
            recurrence_rule: RecurrenceRule object defining the recurrence pattern
            start_date: Start of the date range
            end_date: End of the date range

        Returns:
            List of datetime objects representing all occurrences in the range
        """
        occurrences = []
        
        try:
            # Convert the recurrence rule to a cron expression
            cron_expression = self.convert_frequency_to_cron(recurrence_rule)
            
            # Use croniter to iterate over occurrences in the range
            cron_iter = croniter.croniter(cron_expression, start_date)
            
            # Get the first occurrence
            current_occurrence = cron_iter.get_next(datetime)
            
            # Get all occurrences within the range
            while current_occurrence <= end_date:
                occurrences.append(current_occurrence)
                current_occurrence = cron_iter.get_next(datetime)
        except Exception as e:
            # In case of error with croniter, use a basic calculation
            print(f"Croniter error in range calculation: {e}.")
            # For range calculation, use a simplified approach:
            # Start with the first occurrence and keep adding intervals until past end_date
            current = self.get_next_occurrence(recurrence_rule, start_date)
            while current <= end_date and len(occurrences) < 100:  # Prevent infinite loops
                occurrences.append(current)
                current = self.get_next_occurrence(recurrence_rule, current)
        
        return occurrences