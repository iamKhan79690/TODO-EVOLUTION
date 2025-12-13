"""Output formatting utilities for the todo application."""

from typing import List
from datetime import datetime
from src.domain.task import Task


def format_task_list(tasks: List[Task]) -> str:
    """
    Format a list of tasks for display.

    Args:
        tasks: List of Task objects to format

    Returns:
        Formatted string representation of the tasks
    """
    if not tasks:
        return "No tasks found."

    formatted_tasks = []
    for task in tasks:
        status = "[x]" if task.is_completed else "[ ]"
        priority = f"({task.priority.capitalize()})" if task.priority else ""

        # Format due date if present
        due_date_str = ""
        if task.due_date:
            due_date_str = f"(Due: {task.due_date.strftime('%Y-%m-%d %H:%M')})"

        # Add recurrence indicator if applicable
        recurrence_indicator = "[R]" if task.recurrence_rule else ""

        # Add notification indicator if applicable
        notification_indicator = "[N]" if task.reminder and task.reminder.enabled else ""

        tags = f"[{', '.join(task.tags)}]" if task.tags else ""

        task_parts = [status, f"{task.id}. {task.description}"]

        # Insert indicators and priority in a consistent order
        if priority:
            task_parts.insert(1, priority)
        if due_date_str:
            task_parts.insert(-1 if tags else len(task_parts), due_date_str)
        if recurrence_indicator:
            task_parts.insert(-1 if tags else len(task_parts), recurrence_indicator)
        if notification_indicator:
            task_parts.insert(-1 if tags else len(task_parts), notification_indicator)
        if tags:
            task_parts.append(tags)

        formatted_tasks.append(" ".join(task_parts))

    return "\n".join(formatted_tasks)


def format_task(task: Task) -> str:
    """
    Format a single task for display.

    Args:
        task: Task object to format

    Returns:
        Formatted string representation of the task
    """
    status = "[x]" if task.is_completed else "[ ]"
    priority = f"({task.priority.capitalize()})" if task.priority else ""

    # Format due date if present
    due_date_str = ""
    if task.due_date:
        due_date_str = f"(Due: {task.due_date.strftime('%Y-%m-%d %H:%M')})"

    # Add recurrence indicator if applicable
    recurrence_indicator = "[R]" if task.recurrence_rule else ""

    # Add notification indicator if applicable
    notification_indicator = "[N]" if task.reminder and task.reminder.enabled else ""

    tags = f"[{', '.join(task.tags)}]" if task.tags else ""

    task_parts = [status, f"{task.id}. {task.description}"]

    # Insert indicators and priority in a consistent order
    if priority:
        task_parts.insert(1, priority)
    if due_date_str:
        task_parts.insert(-1 if tags else len(task_parts), due_date_str)
    if recurrence_indicator:
        task_parts.insert(-1 if tags else len(task_parts), recurrence_indicator)
    if notification_indicator:
        task_parts.insert(-1 if tags else len(task_parts), notification_indicator)
    if tags:
        task_parts.append(tags)

    return " ".join(task_parts)


def format_task_with_details(task: Task) -> str:
    """
    Format a single task with detailed information for display.

    Args:
        task: Task object to format

    Returns:
        Formatted string representation of the task with detailed information
    """
    status = "[x]" if task.is_completed else "[ ]"
    title = f"{task.id}. {task.description}"
    priority = f"Priority: {task.priority.capitalize()}" if task.priority else ""

    # Format due date if present
    due_date_str = f"Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}" if task.due_date else ""

    # Format creation/completion dates
    created_str = f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}" if task.created_at else ""
    completed_str = f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}" if task.completed_at else ""

    # Recurrence information
    recurrence_info = ""
    if task.recurrence_rule:
        frequency = task.recurrence_rule.frequency.value
        recurrence_info = f"Recurrence: {frequency}"
        if task.recurrence_rule.interval > 1:
            recurrence_info += f" every {task.recurrence_rule.interval} {frequency}s"

    # Reminder information
    reminder_info = ""
    if task.reminder and task.reminder.enabled:
        reminder_times = ", ".join([str(t) for t in task.reminder.reminder_times]) if task.reminder.reminder_times else "default"
        reminder_info = f"Reminders: {reminder_times} mins before"

    # Collect all parts
    parts = [status, title]
    if priority:
        parts.append(f"[{priority}]")
    if due_date_str:
        parts.append(f"[{due_date_str}]")
    if recurrence_info:
        parts.append(f"[{recurrence_info}]")
    if reminder_info:
        parts.append(f"[{reminder_info}]")
    if created_str:
        parts.append(f"[{created_str}]")
    if completed_str:
        parts.append(f"[{completed_str}]")

    # Add tags if any
    if task.tags:
        tags_str = f"[{', '.join(task.tags)}]"
        parts.append(tags_str)

    return " ".join(parts)
