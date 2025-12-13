# Task Service Contract

**Feature**: 002-task-enhancements  
**Contract Version**: 1.0  
**Date**: 2025-12-02  

## Overview

This contract defines the interface for the Task Service that implements the task enhancement features (priorities, tags, search, filter, sort). This service will be used by the UI layer to manage tasks with the new functionality.

## Service Interface: TaskService

### Methods

#### 1. create_task(title, description, priority, tags)

**Description**: Creates a new task with the specified properties.

**Parameters**:
- `title` (string): The task title (required, 1-200 chars)
- `description` (string): The task description (optional, 0-1000 chars)
- `priority` (enum): Priority level - 'high', 'medium', or 'low' (default: 'medium')
- `tags` (list of strings): Tags to categorize the task (optional, up to 10 tags)

**Returns**: Task object with all properties including generated ID and timestamps

**Validations**:
- Title must be between 1-200 characters
- Description must be between 0-1000 characters if provided
- Priority must be one of 'high', 'medium', 'low'
- Each tag must be 1-50 chars and contain only alphanumeric characters and hyphens
- Maximum of 10 tags allowed

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

#### 3. update_task(task_id, title, description, status, priority, tags)

**Description**: Updates an existing task with new values.

**Parameters**:
- `task_id` (string or UUID): The unique identifier of the task
- `title` (string): The updated task title (1-200 chars)
- `description` (string): The updated task description (0-1000 chars)
- `status` (enum): Updated status - 'pending', 'in_progress', or 'completed'
- `priority` (enum): Updated priority - 'high', 'medium', or 'low'
- `tags` (list of strings): Updated tags (up to 10 tags)

**Returns**: Updated Task object

**Validations**:
- All validations from create_task apply
- Status must be one of 'pending', 'in_progress', 'completed'

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
- `sort_by` (enum): Sort criteria - 'priority', 'title', 'created_date', or None
- `filter_by` (dict): Filter criteria with keys like 'status', 'priority', 'tag', 'keyword'

**Returns**: List of Task objects

**Examples of filter_by**:
- `{'status': 'completed'}` - filter by status
- `{'priority': 'high'}` - filter by priority
- `{'tag': 'work'}` - filter by tag
- `{'keyword': 'meeting'}` - search by keyword in title/description
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
- `priority` (enum): Priority level - 'high', 'medium', or 'low'

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
- `sort_criteria` (enum): Sorting criteria - 'priority', 'title'

**Returns**: List of Task objects sorted according to criteria
  - For 'priority': High -> Medium -> Low
  - For 'title': Alphabetically A-Z

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
    }
  },
  "required": ["id", "title", "status", "priority", "created_at"]
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