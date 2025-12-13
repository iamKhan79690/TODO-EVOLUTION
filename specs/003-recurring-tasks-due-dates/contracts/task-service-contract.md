# Task Service Contract with Recurring Tasks & Due Dates

**Feature**: 003-recurring-tasks-due-dates  
**Contract Version**: 1.0  
**Date**: 2025-12-02  

## Overview

This contract defines the interface for the Task Service that implements the recurring tasks and due dates features. This service will be used by the UI layer to manage tasks with due dates, recurring patterns, and time-based reminders.

## Service Interface: TaskService (Extended)

### Methods

#### 1. create_task(title, description, priority, tags, due_date, recurrence_rule, reminder_settings)

**Description**: Creates a new task with optional due date, recurrence pattern, and reminder settings.

**Parameters**:
- `title` (string): The task title (required, 1-200 chars)
- `description` (string): The task description (optional, 0-1000 chars)
- `priority` (enum): Priority level - 'high', 'medium', or 'low' (default: 'medium')
- `tags` (list of strings): Tags to categorize the task (optional, up to 10 tags)
- `due_date` (datetime): When the task is due (optional)
- `recurrence_rule` (object): Recurrence pattern definition (optional)
- `reminder_settings` (object): Reminder configuration (optional)

**Returns**: Task object with all properties including generated ID and timestamps

**Validations**:
- Title must be between 1-200 characters
- Description must be between 0-1000 characters if provided
- Priority must be one of 'high', 'medium', 'low'
- Each tag must be 1-50 chars and contain only alphanumeric characters and hyphens
- Maximum of 10 tags allowed
- Due date must be in the future if provided
- If recurrence_rule is provided, due_date is required

**Error Cases**:
- `ValidationError`: If any validation fails
- `TaskCreationError`: If task creation fails for any other reason

---

#### 2. get_task(task_id)

**Description**: Retrieves a task by its ID.

**Parameters**:
- `task_id` (string or UUID): The unique identifier of the task

**Returns**: Task object or None if not found

**Error Cases**:
- `TaskNotFoundError`: If no task with the given ID exists

---

#### 3. update_task(task_id, title, description, status, priority, tags, due_date, recurrence_rule, reminder_settings)

**Description**: Updates an existing task with new values.

**Parameters**:
- `task_id` (string or UUID): The unique identifier of the task
- `title` (string): The updated task title (1-200 chars)
- `description` (string): The updated task description (0-1000 chars)
- `status` (enum): Updated status - 'pending', 'in_progress', 'completed'
- `priority` (enum): Updated priority - 'high', 'medium', 'low'
- `tags` (list of strings): Updated tags (up to 10 tags)
- `due_date` (datetime): Updated due date (optional)
- `recurrence_rule` (object): Updated recurrence pattern (optional)
- `reminder_settings` (object): Updated reminder configuration (optional)

**Returns**: Updated Task object

**Validations**:
- All validations from create_task apply
- Status must be one of 'pending', 'in_progress', 'completed'
- Due date must be in the future if provided

**Error Cases**:
- `TaskNotFoundError`: If no task with the given ID exists
- `ValidationError`: If any validation fails
- `TaskUpdateError`: If task update fails for any other reason

---

#### 4. delete_task(task_id)

**Description**: Deletes a task by its ID.

**Parameters**:
- `task_id` (string or UUID): The unique identifier of the task to delete

**Returns**: Boolean indicating success (true) or failure (false)

**Error Cases**:
- `TaskDeletionError`: If task deletion fails for any reason

---

#### 5. get_all_tasks(sort_by=None, filter_by=None)

**Description**: Retrieves all tasks with optional sorting and filtering.

**Parameters**:
- `sort_by` (enum): Sort criteria - 'priority', 'title', 'due_date', 'created_date', or None
- `filter_by` (dict): Filter criteria with keys like 'status', 'priority', 'tag', 'keyword', 'due_date_range'

**Returns**: List of Task objects

**Examples of filter_by**:
- `{'status': 'completed'}` - filter by status
- `{'priority': 'high'}` - filter by priority
- `{'tag': 'work'}` - filter by tag
- `{'keyword': 'meeting'}` - search by keyword in title/description
- `{'due_date_range': {'start': '2025-12-01', 'end': '2025-12-31'}}` - filter by due date range
- `{'priority': 'high', 'tag': 'work'}` - combine multiple filters (AND logic)

---

#### 6. search_tasks(keyword)

**Description**: Searches tasks by keyword in title and description.

**Parameters**:
- `keyword` (string): The search term (case-insensitive)

**Returns**: List of matching Task objects

---

#### 7. filter_tasks_by_priority(priority)

**Description**: Filters tasks by priority level.

**Parameters**:
- `priority` (enum): Priority level - 'high', 'medium', 'low'

**Returns**: List of Task objects with the specified priority

---

#### 8. filter_tasks_by_tag(tag)

**Description**: Filters tasks by a specific tag.

**Parameters**:
- `tag` (string): The tag to filter by (case-insensitive)

**Returns**: List of Task objects with the specified tag

---

#### 9. sort_tasks(sort_criteria)

**Description**: Sorts tasks based on the specified criteria.

**Parameters**:
- `sort_criteria` (enum): Sorting criteria - 'priority', 'title', 'due_date'

**Returns**: List of Task objects sorted according to criteria
  - For 'priority': High -> Medium -> Low
  - For 'title': Alphabetically A-Z
  - For 'due_date': Earliest to latest (tasks without due dates last)

---

#### 10. get_overdue_tasks()

**Description**: Retrieves all tasks that are past their due date and still pending.

**Returns**: List of Task objects that are overdue

---

#### 11. get_upcoming_tasks(days_ahead)

**Description**: Retrieves tasks due within the specified number of days.

**Parameters**:
- `days_ahead` (integer): Number of days to look ahead (e.g., 7 for next week)

**Returns**: List of Task objects due within the specified period

---

#### 12. complete_task(task_id)

**Description**: Marks a task as complete and handles recurrence if applicable.

**Parameters**:
- `task_id` (string or UUID): The unique identifier of the task

**Returns**: Updated Task object (completed) or new recurrent instance if applicable

**Behavior**:
- If the task has a recurrence rule, creates a new instance based on the rule
- If the task is a recurring instance, may trigger creation of the next instance

---

#### 13. create_recurring_task(title, description, priority, tags, due_date, recurrence_rule, reminder_settings)

**Description**: Creates a new recurring task template.

**Parameters**:
- `title` (string): The task title (required, 1-200 chars)
- `description` (string): The task description (optional, 0-1000 chars)
- `priority` (enum): Priority level - 'high', 'medium', or 'low' (default: 'medium')
- `tags` (list of strings): Tags to categorize the task (optional, up to 10 tags)
- `due_date` (datetime): When the first instance is due
- `recurrence_rule` (object): Recurrence pattern definition (required for recurring tasks)
- `reminder_settings` (object): Reminder configuration (optional)

**Returns**: Recurring Task Template object

---

#### 14. get_recurring_task_instances(task_template_id, start_date, end_date)

**Description**: Retrieves all instances of a recurring task within the specified date range.

**Parameters**:
- `task_template_id` (string or UUID): The unique identifier of the recurring task template
- `start_date` (date): Start of date range to retrieve instances
- `end_date` (date): End of date range to retrieve instances

**Returns**: List of RecurringTaskInstance objects

---

#### 15. skip_recurring_instance(task_instance_id)

**Description**: Marks a specific instance of a recurring task to be skipped.

**Parameters**:
- `task_instance_id` (string or UUID): The unique identifier of the specific task instance

**Returns**: Boolean indicating success

---

#### 16. modify_recurring_instance(task_instance_id, updates)

**Description**: Modifies a specific instance of a recurring task without affecting the recurrence pattern.

**Parameters**:
- `task_instance_id` (string or UUID): The unique identifier of the specific task instance
- `updates` (dict): Values to update (e.g., due_date, title, description)

**Returns**: Updated RecurringTaskInstance object

---

## Service Interface: ReminderService

### Methods

#### 1. check_for_upcoming_reminders()

**Description**: Checks for tasks with due dates approaching and sends notifications as configured.

**Returns**: List of tasks with upcoming due dates that need notifications

**Behavior**:
- Checks all pending tasks with due dates
- Compares due dates with current time and reminder settings
- Sends console notifications for tasks that meet reminder criteria
- Updates the `last_triggered` field in the reminder configuration

---

#### 2. snooze_reminder(task_id, duration_minutes)

**Description**: Temporarily postpones a reminder for the specified duration.

**Parameters**:
- `task_id` (string or UUID): The unique identifier of the task
- `duration_minutes` (integer): Number of minutes to delay the reminder (e.g., 15, 30, 60)

**Returns**: Boolean indicating success

---

#### 3. disable_reminder(task_id)

**Description**: Disables notifications for a specific task.

**Parameters**:
- `task_id` (string or UUID): The unique identifier of the task

**Returns**: Boolean indicating success

---

#### 4. enable_reminder(task_id)

**Description**: Enables notifications for a specific task.

**Parameters**:
- `task_id` (string or UUID): The unique identifier of the task

**Returns**: Boolean indicating success

---

## Service Interface: RecurrenceService

### Methods

#### 1. generate_next_instance(task_template_id)

**Description**: Creates the next instance of a recurring task based on its recurrence pattern.

**Parameters**:
- `task_template_id` (string or UUID): The unique identifier of the recurring task template

**Returns**: New RecurringTaskInstance object

**Behavior**:
- Calculates the next occurrence based on the recurrence rule
- Creates a new task instance with the same properties as the template
- Applies any modifications specified in the recurrence rule

---

#### 2. update_recurrence_pattern(task_template_id, new_pattern)

**Description**: Updates the recurrence pattern for a recurring task template.

**Parameters**:
- `task_template_id` (string or UUID): The unique identifier of the recurring task template
- `new_pattern` (object): New recurrence pattern definition

**Returns**: Updated Task object with new recurrence pattern

**Behavior**:
- Updates future instances to use the new pattern
- Does not affect already-generated instances

---

## Task Object Schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier for the task"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "maxLength": 1000,
      "description": "Task description"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "in_progress", "completed"],
      "description": "Current status of the task"
    },
    "priority": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "default": "medium",
      "description": "Priority level of the task"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 50,
        "pattern": "^[a-zA-Z0-9-]+$"
      },
      "maxItems": 10,
      "description": "List of tags for the task"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "When the task was created"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "When the task was last updated"
    },
    "completed_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "When the task was completed (null if not completed)"
    },
    "due_date": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "When the task is due (null if no due date set)"
    },
    "notification_sent": {
      "type": "boolean",
      "default": false,
      "description": "Whether a notification has been sent for this task"
    },
    "recurrence_rule": {
      "type": ["object", "null"],
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier for the recurrence rule"
        },
        "frequency": {
          "type": "string",
          "enum": ["daily", "weekly", "monthly", "yearly", "custom"],
          "description": "How often the task repeats"
        },
        "interval": {
          "type": "integer",
          "minimum": 1,
          "default": 1,
          "description": "How many frequency units between occurrences"
        },
        "days_of_week": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
          },
          "description": "Days of the week for weekly recurrence"
        },
        "day_of_month": {
          "type": "integer",
          "minimum": 1,
          "maximum": 31,
          "description": "Day of month for monthly recurrence"
        },
        "specific_time": {
          "type": "string",
          "pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$",
          "description": "Time of day for the recurring task (HH:MM format)"
        },
        "end_condition": {
          "type": "string",
          "enum": ["never", "after_occurrences", "on_date"],
          "default": "never",
          "description": "When the recurrence should end"
        },
        "end_count": {
          "type": "integer",
          "minimum": 1,
          "description": "Number of occurrences for 'after_occurrences' end condition"
        },
        "end_date": {
          "type": "string",
          "format": "date",
          "description": "Date to end recurrence for 'on_date' end condition"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "When the recurrence rule was created"
        },
        "exceptions": {
          "type": "array",
          "items": {
            "type": "string",
            "format": "date"
          },
          "description": "List of skipped dates for the recurrence pattern"
        }
      },
      "required": ["id", "frequency"],
      "description": "Recurrence pattern for recurring tasks"
    },
    "reminder": {
      "type": ["object", "null"],
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier for the reminder"
        },
        "enabled": {
          "type": "boolean",
          "default": true,
          "description": "Whether the reminder is active"
        },
        "reminder_times": {
          "type": "array",
          "items": {
            "type": "integer",
            "minimum": 1
          },
          "description": "Times before due date to send notification (in minutes)"
        },
        "last_triggered": {
          "type": ["string", "null"],
          "format": "date-time",
          "description": "Last time a reminder was sent"
        },
        "snooze_until": {
          "type": ["string", "null"],
          "format": "date-time",
          "description": "Temporary postponement of reminder"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "When the reminder was created"
        }
      },
      "required": ["id", "enabled"],
      "description": "Reminder configuration for the task"
    }
  },
  "required": ["id", "title", "status", "created_at"]
}
```

## Error Responses

### ValidationError
```json
{
  "error": "ValidationError",
  "message": "Description of validation error",
  "details": {
    "field": "field name",
    "value": "supplied value",
    "reason": "validation reason"
  }
}
```

### TaskNotFoundError
```json
{
  "error": "TaskNotFoundError",
  "message": "Task with ID [task_id] not found"
}
```

### Other Service Errors
```json
{
  "error": "ErrorType",
  "message": "Human-readable error message"
}
```