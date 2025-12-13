"""Input validation functions for the todo application."""

from datetime import datetime
from typing import List, Union
from src.domain.recurrence_rule import RecurrenceRule, Frequency, EndCondition


def validate_task_description(description: str) -> Union[bool, str]:
    """
    Validate a task description.

    Args:
        description: The task description to validate

    Returns:
        True if valid, otherwise an error message string
    """
    if not description or not description.strip():
        return "Task description cannot be empty or contain only whitespace"

    if len(description) > 2000:
        return "Task description must be less than 2000 characters"

    return True


def validate_task_title(title: str) -> Union[bool, str]:
    """
    Validate a task title.

    Args:
        title: The task title to validate

    Returns:
        True if valid, otherwise an error message string
    """
    if not title or not title.strip():
        return "Task title cannot be empty or contain only whitespace"

    if len(title) > 200:
        return "Task title must be less than 200 characters"

    return True


def validate_task_id(task_id: int) -> Union[bool, str]:
    """
    Validate a task ID.

    Args:
        task_id: The task ID to validate

    Returns:
        True if valid, otherwise an error message string
    """
    if not isinstance(task_id, int) or task_id <= 0:
        return "Task ID must be a positive integer"

    return True


def validate_task_limit(current_count: int, max_limit: int = 1000) -> Union[bool, str]:
    """
    Validate that the task limit is not exceeded.

    Args:
        current_count: Current number of tasks
        max_limit: Maximum allowed tasks

    Returns:
        True if valid, otherwise an error message string
    """
    if current_count >= max_limit:
        return f"Cannot exceed maximum of {max_limit} tasks"

    return True


def validate_priority(priority: str) -> Union[bool, str]:
    """
    Validate a task priority.

    Args:
        priority: The priority level to validate ('high', 'medium', 'low')

    Returns:
        True if valid, otherwise an error message string
    """
    valid_priorities = ['high', 'medium', 'low']
    if priority not in valid_priorities:
        return f"Priority must be one of: {', '.join(valid_priorities)}"

    return True


def validate_tags(tags: List[str]) -> Union[bool, str]:
    """
    Validate a list of task tags.

    Args:
        tags: The list of tags to validate

    Returns:
        True if valid, otherwise an error message string
    """
    if not isinstance(tags, list):
        return "Tags must be a list"

    if len(tags) > 10:
        return "Maximum 10 tags allowed per task"

    for tag in tags:
        if not isinstance(tag, str):
            return f"Tag '{tag}' must be a string"

        if not (1 <= len(tag) <= 50):
            return f"Each tag must be 1-50 characters: '{tag}'"

        if not tag.replace('-', '').replace('_', '').isalnum():
            return f"Tag '{tag}' contains invalid characters. Only alphanumeric, hyphens, and underscores allowed."

    return True


def validate_due_date(due_date) -> Union[bool, str]:
    """
    Validate a task due date.

    Args:
        due_date: The due date to validate

    Returns:
        True if valid, otherwise an error message string
    """
    if due_date is None:
        # None is acceptable (tasks without due dates)
        return True

    if not isinstance(due_date, datetime):
        return "Due date must be a datetime object"

    if due_date < datetime.now():
        return "Due date must be in the future"

    return True


def validate_recurrence_rule(recurrence_rule) -> Union[bool, str]:
    """
    Validate a task recurrence rule.

    Args:
        recurrence_rule: The recurrence rule to validate

    Returns:
        True if valid, otherwise an error message string
    """
    if recurrence_rule is None:
        # None is acceptable (non-recurring tasks)
        return True

    if not isinstance(recurrence_rule, RecurrenceRule):
        return "Recurrence rule must be a RecurrenceRule object"

    # Validate interval
    if recurrence_rule.interval <= 0:
        return "Recurrence interval must be a positive integer"

    # Validate frequency
    valid_frequencies = [freq.value for freq in Frequency]
    if recurrence_rule.frequency.value not in valid_frequencies:
        return f"Frequency must be one of: {', '.join(valid_frequencies)}"

    # For weekly frequency, validate days of week
    if recurrence_rule.frequency == Frequency.WEEKLY:
        if not recurrence_rule.days_of_week:
            return "Days of week must be specified for weekly recurrence"

        valid_days = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
        invalid_days = set(recurrence_rule.days_of_week) - valid_days
        if invalid_days:
            return f"Invalid days of week: {', '.join(invalid_days)}. Valid days: {', '.join(valid_days)}"

    # For monthly frequency, validate day of month
    if recurrence_rule.frequency == Frequency.MONTHLY:
        if recurrence_rule.day_of_month is None:
            return "Day of month must be specified for monthly recurrence"
        if not (1 <= recurrence_rule.day_of_month <= 31):
            return "Day of month must be between 1 and 31"

    # Validate end condition
    valid_end_conditions = [condition.value for condition in EndCondition]
    if recurrence_rule.end_condition.value not in valid_end_conditions:
        return f"End condition must be one of: {', '.join(valid_end_conditions)}"

    # Validate end count if condition is after_occurrences
    if recurrence_rule.end_condition == EndCondition.AFTER_OCCURRENCES:
        if recurrence_rule.end_count is None or recurrence_rule.end_count <= 0:
            return "End count must be a positive integer when end condition is 'after_occurrences'"

    # Validate end date if condition is on_date
    if recurrence_rule.end_condition == EndCondition.ON_DATE:
        if recurrence_rule.end_date is None:
            return "End date must be specified when end condition is 'on_date'"
        if recurrence_rule.end_date < datetime.now().date():
            return "End date must be in the future"

    return True


def validate_reminder_settings(reminder_settings) -> Union[bool, str]:
    """
    Validate reminder settings.

    Args:
        reminder_settings: The reminder settings to validate

    Returns:
        True if valid, otherwise an error message string
    """
    if reminder_settings is None:
        # None is acceptable (tasks without reminders)
        return True

    # Basic validation - could be enhanced based on actual reminder class structure
    if hasattr(reminder_settings, 'reminder_times'):
        if isinstance(reminder_settings.reminder_times, list):
            for time in reminder_settings.reminder_times:
                if not isinstance(time, int) or time <= 0:
                    return f"Each reminder time must be a positive integer, got: {time}"

    return True
