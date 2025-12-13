# Quickstart Guide: Recurring Tasks & Due Dates

**Feature**: 003-recurring-tasks-due-dates  
**Date**: 2025-12-02  
**Version**: 1.0

## Overview

This guide provides developers with information to quickly understand and start working on the recurring tasks and due dates features, which include:

1. Setting due dates and times for tasks
2. Receiving console-based time reminders
3. Creating recurring tasks that auto-reschedule after completion
4. Managing individual instances of recurring tasks

## Prerequisites

- Python 3.13+ installed
- UV package manager installed
- Understanding of the existing console todo application
- Familiarity with the date/time libraries like datetime and croniter

## Setup

1. **Install dependencies** (in addition to existing ones):
   ```bash
   uv add croniter  # For cron-like recurrence pattern processing
   ```

2. **Run the application**:
   ```bash
   uv run src/main.py
   ```

3. **Run tests**:
   ```bash
   uv run pytest
   ```

## Key Changes Overview

### 1. Extended Task Model

The `Task` model has been extended with:
- `due_date` attribute: DateTime when the task is due
- `recurrence_rule` attribute: Object defining recurrence pattern
- `reminder_settings` attribute: Object configuring notification times

### 2. New Domain Models

Added the following new domain models:
- `RecurrenceRule`: Defines how a task repeats
- `Reminder`: Configures notification settings
- `RecurringTaskInstance`: Represents individual instances of recurring tasks

### 3. Enhanced UI Features

The console interface now includes:
- Prompts for due date/time when creating tasks
- Recurrence pattern selection options
- Reminder configuration settings
- New views for upcoming tasks and overdue tasks

### 4. New Service Layer Components

Added the following service components:
- `RecurrenceService`: Handles recurrence pattern logic
- `ReminderService`: Manages notification scheduling
- `TaskScheduler`: Manages time-based operations

## Project Structure

```
src/
├── domain/
│   ├── task.py              # Extended with due_date, recurrence, reminders
│   ├── task_list.py         # Updated with time-based operations
│   ├── recurrence_rule.py   # New: Recurrence pattern implementation
│   ├── reminder.py          # New: Reminder configuration
│   └── errors.py            # Domain-specific exceptions
├── services/
│   ├── task_service.py      # Extended with new functionality
│   ├── recurrence_service.py # New: Recurrence pattern handling
│   ├── reminder_service.py   # New: Reminder scheduling and delivery
│   └── validation.py         # Extended with new field validation
├── scheduler/               # New: Time-based operations
│   ├── task_scheduler.py    # Handles recurring task generation and reminders
│   └── cron_scheduler.py    # Cron-like scheduling using croniter
└── ui/
    ├── cli.py               # Updated with new features
    ├── menu.py              # Updated with new options
    └── formatters.py         # Updated display format with due dates/notifications
```

## Implementation Guidelines

### Creating Tasks with Due Dates

When implementing due date functionality:

1. Validate that due dates are in the future
2. Add a date/time picker interface in the CLI
3. Store due dates with time precision (datetime)

### Implementing Recurring Tasks

When implementing recurring task functionality:

1. Create a `RecurrenceRule` model with frequency (daily, weekly, monthly, etc.)
2. Implement the logic to generate new task instances based on the recurrence pattern
3. Handle recurrence end conditions (never, after N occurrences, by date)
4. Allow users to skip or modify specific instances

### Reminder System Implementation

When implementing the reminder system:

1. Create a background process (or periodic check) to monitor for upcoming due dates
2. Implement console-based notification output
3. Support configurable reminder timing (e.g., 1 hour before, 1 day before)
4. Include snooze functionality for postponing reminders

### Display Format Updates

Update the task display to show:
- Due dates in an appropriate format (e.g., "Due: Dec 15, 2025 10:00 AM")
- Recurring task indicators (e.g., "🔄" or "(Recurring)")
- Overdue task indicators

## Testing Requirements

1. **Domain Tests**: Test the extended Task model with due dates, recurrence, and reminders
2. **Service Tests**: Test recurrence and reminder service operations
3. **Scheduler Tests**: Test the time-based operations
4. **Integration Tests**: Test CLI interactions for new features

Example test cases to include:
```python
# Test creating a task with due date
def test_create_task_with_due_date():
    # Implementation here

# Test generating next instance of recurring task
def test_generate_next_recurring_instance():
    # Implementation here

# Test reminder notification logic
def test_reminder_notification():
    # Implementation here
```

## Common Development Tasks

### Adding Due Date Validation

```python
from datetime import datetime

def validate_due_date(due_date):
    if due_date and due_date < datetime.now():
        raise ValidationError("Due date must be in the future")
```

### Adding Recurrence Pattern Processing

```python
from croniter import croniter
from datetime import datetime

def calculate_next_occurrence(recurrence_rule, last_date=None):
    # Implementation based on frequency type
    if recurrence_rule.frequency == 'daily':
        # Return next day
    elif recurrence_rule.frequency == 'weekly':
        # Return same day of next week
    # ... etc
```

## Error Handling

- Validate due dates are in the future
- Validate recurrence patterns are properly formatted
- Handle cases where system time changes (daylight savings, etc.)
- Provide clear error messages to users for invalid inputs

## Performance Considerations

- Time-based checks should run efficiently (consider running every 30 seconds rather than continuously)
- Store recurring tasks in a way that allows for efficient retrieval
- Consider performance implications of checking many tasks for upcoming due dates

## Next Steps

1. Review the [Data Model](data-model.md) for detailed entity specifications
2. Review the [Task Service Contract](contracts/task-service-contract.md) for interface specifications
3. Implement the feature following the [Tasks](tasks.md) breakdown (to be generated)
4. Ensure all functionality is console-based as per Phase I constraints