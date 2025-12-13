# Data Model: Recurring Tasks & Due Dates

**Feature**: 003-recurring-tasks-due-dates  
**Date**: 2025-12-02  
**Domain**: Task Management

## Overview

This document defines the data model changes required to implement the recurring tasks and due dates features, specifically:

1. Adding due date and time functionality to tasks
2. Implementing recurring task patterns with auto-rescheduling
3. Supporting time-based reminders and notifications
4. Managing recurring task instances and exceptions

## Entity: Task (Extended)

### Properties

| Property | Type | Required | Validation | Description |
|----------|------|----------|------------|-------------|
| id | UUID/string | Yes | Unique identifier | System-generated unique identifier for the task |
| title | string | Yes | Max 200 chars, non-empty | Task title or summary |
| description | string | No | Max 1000 chars | Detailed task description |
| status | enum | Yes | Values: pending, completed, in_progress | Current status of the task |
| priority | enum | No | Values: high, medium, low | Priority level, defaults to 'medium' |
| tags | list of strings | No | Max 10 tags, each 50 chars max | List of tags for categorizing tasks |
| created_at | datetime | Yes | System timestamp | When the task was created |
| updated_at | datetime | No | System timestamp | When the task was last updated |
| completed_at | datetime | No | System timestamp | When the task was marked as completed |
| due_date | datetime | No | Future date/time only | When the task is due (with time precision) |
| notification_sent | boolean | No | Default: false | Whether a notification has been sent for this task |
| recurrence_rule | RecurrenceRule object | No | Valid recurrence rule | Defines recurrence pattern for recurring tasks |

### Validation Rules

1. **Due date validation**: Due date must be in the future (not in the past)
2. **Recurrence validation**: If recurrence_rule is set, due_date is required
3. **Priority validation**: Priority must be one of `high`, `medium`, or `low`
4. All other validations from the base Task entity remain unchanged

## Entity: RecurrenceRule

### Properties

| Property | Type | Required | Validation | Description |
|----------|------|----------|------------|-------------|
| id | UUID/string | Yes | Unique identifier | System-generated unique identifier for the recurrence rule |
| frequency | enum | Yes | Values: daily, weekly, monthly, yearly, custom | How often the task repeats |
| interval | integer | No | Positive integer, default: 1 | How many frequency units between occurrences (e.g., every 2 weeks) |
| days_of_week | list of strings | No | Values: mon, tue, wed, thu, fri, sat, sun (for weekly) | Days of the week for weekly recurrence |
| day_of_month | integer | No | 1-31 (for monthly) | Day of month for monthly recurrence |
| specific_time | time | No | Format: HH:MM | Time of day for the recurring task |
| end_condition | enum | No | Values: never, after_occurrences, on_date | When the recurrence should end |
| end_count | integer | No | Positive integer | Number of occurrences for 'after_occurrences' end condition |
| end_date | date | No | Future date | Date to end recurrence for 'on_date' end condition |
| created_at | datetime | Yes | System timestamp | When the recurrence rule was created |
| exceptions | list of dates | No | List of skipped dates | Specific dates to skip in the recurrence pattern |

### Frequency Enum Values

- `daily`: Task repeats every day or every N days
- `weekly`: Task repeats on specific day(s) of the week
- `monthly`: Task repeats on a specific day of the month
- `yearly`: Task repeats annually on the same date
- `custom`: Task repeats with custom schedule (interval in days)

### End Condition Enum Values

- `never`: Recurrence continues indefinitely
- `after_occurrences`: Recurrence ends after specified number of occurrences
- `on_date`: Recurrence ends on a specific date

### Validation Rules

1. **Interval validation**: If specified, must be a positive integer
2. **Days of week validation**: For weekly frequency, at least one day must be specified
3. **Day of month validation**: For monthly frequency, must be 1-31
4. **End condition validation**: Depends on specific end condition type (count for 'after_occurrences', date for 'on_date')
5. **Time validation**: If specified, must be in valid time format (HH:MM)

## Entity: Reminder

### Properties

| Property | Type | Required | Validation | Description |
|----------|------|----------|------------|-------------|
| id | UUID/string | Yes | Unique identifier | System-generated unique identifier for the reminder |
| task_id | UUID/string | Yes | Must reference existing task | The task this reminder is associated with |
| enabled | boolean | No | Default: true | Whether the reminder is active |
| reminder_times | list of integers | No | Values in minutes before due date (e.g., [15, 60, 1440]) | Times before due date to send notification |
| last_triggered | datetime | No | System timestamp | Last time a reminder was sent |
| snooze_until | datetime | No | Future timestamp | Temporary postponement of reminder |
| created_at | datetime | Yes | System timestamp | When the reminder was created |

### Validation Rules

1. **Task reference validation**: task_id must reference an existing task
2. **Reminder times validation**: Each value must be a positive integer representing minutes before due date
3. **Snooze validation**: If specified, snooze_until must be in the future

## Entity: RecurringTaskInstance

### Properties

| Property | Type | Required | Validation | Description |
|----------|------|----------|------------|-------------|
| id | UUID/string | Yes | Unique identifier | System-generated unique identifier for the task instance |
| original_task_id | UUID/string | Yes | Must reference existing recurring task | The template task for this instance |
| title | string | Yes | Max 200 chars, non-empty | Task title (may be modified from original) |
| description | string | No | Max 1000 chars | Detailed task description (may be modified from original) |
| status | enum | Yes | Values: pending, completed, in_progress | Current status of the instance |
| priority | enum | No | Values: high, medium, low | Priority level, defaults to original task's priority |
| due_date | datetime | Yes | Future date/time only | When this instance is due |
| created_at | datetime | Yes | System timestamp | When the instance was created |
| completed_at | datetime | No | System timestamp | When the instance was marked as completed |
| is_exception | boolean | No | Default: false | Whether this is an exception to the recurrence pattern |

### Validation Rules

1. **Original task validation**: original_task_id must reference an existing recurring task
2. **Due date validation**: Due date must be in the future
3. **Status validation**: Must be one of the allowed status values

## Relationships

- Each Task can have at most one associated RecurrenceRule (for recurring tasks)
- Each RecurrenceRule belongs to one Task
- Each Task can have at most one associated Reminder configuration
- Each Reminder belongs to one Task
- Each RecurringTaskInstance references an original recurring Task
- Multiple RecurringTaskInstances can reference the same original task

## State Transitions

### Task State Transitions
- When status changes to `completed`, `completed_at` is set to current timestamp
- When status changes from `completed` to any other status, `completed_at` is cleared
- `updated_at` is updated on every modification

### Recurring Task Behavior
- When a recurring task is marked complete, a new instance is automatically created based on the recurrence pattern
- If an instance is marked complete with a specific date in the future, the next instance is scheduled for that date
- If a recurring task's pattern is modified, future instances will use the new pattern

## Example Instances

```python
# Example of a recurring task (meeting)
recurring_task_example = {
    "id": "task-123",
    "title": "Weekly Team Meeting",
    "description": "Weekly sync with the team",
    "status": "pending",
    "priority": "medium",
    "tags": ["work", "meeting"],
    "created_at": "2025-12-02T09:00:00Z",
    "due_date": "2025-12-06T10:00:00Z",  # Next occurrence
    "recurrence_rule": {
        "id": "rr-456",
        "frequency": "weekly",
        "interval": 1,
        "days_of_week": ["fri"],
        "specific_time": "10:00",
        "end_condition": "never",
        "created_at": "2025-12-02T09:00:00Z"
    },
    "reminder": {
        "id": "rem-789",
        "enabled": True,
        "reminder_times": [60, 15],  # 1 hour and 15 minutes before
        "last_triggered": None
    }
}

# Example of a one-time task with due date and reminder
single_task_example = {
    "id": "task-124",
    "title": "Submit quarterly report",
    "description": "Complete and submit the Q4 report",
    "status": "pending",
    "priority": "high",
    "tags": ["work", "report"],
    "created_at": "2025-12-02T09:15:00Z",
    "due_date": "2025-12-15T17:00:00Z",
    "reminder": {
        "id": "rem-901",
        "enabled": True,
        "reminder_times": [1440, 60],  # 1 day and 1 hour before
        "last_triggered": None
    }
}
```

## In-Memory Storage Model

The TaskList will be enhanced to support time-based operations, including:

1. **Due date tracking**: Tasks will be indexed by due date for efficient retrieval
2. **Recurrence handling**: A RecurrenceScheduler component will manage creating new task instances
3. **Reminder scheduling**: A ReminderScheduler component will track and send notifications

The in-memory collection will support the following operations efficiently:
- O(1) access for finding tasks by ID
- O(log n) operations for retrieving tasks by due date using sorted structures
- O(n) operations for checking all tasks for upcoming due dates or recurrence triggers
- O(1) operations for basic task CRUD operations (unchanged from base implementation)