# Data Model: Task Enhancements

**Feature**: 002-task-enhancements  
**Date**: 2025-12-02  
**Domain**: Task Management

## Overview

This document defines the data model changes required to implement the task enhancement features, specifically:

1. Adding priority levels (High, Medium, Low) to tasks
2. Adding tagging functionality to tasks
3. Supporting search, filter, and sort functionality

## Entity: Task

### Properties

| Property | Type | Required | Validation | Description |
|----------|------|----------|------------|-------------|
| id | UUID/string | Yes | Unique identifier | System-generated unique identifier for the task |
| title | string | Yes | Max 200 chars, non-empty | Task title or summary |
| description | string | No | Max 1000 chars | Detailed task description |
| status | enum | Yes | Values: pending, completed, in_progress | Current status of the task |
| priority | enum | Yes | Values: high, medium, low | Priority level, defaults to 'medium' |
| tags | list of strings | No | Max 10 tags, each 50 chars max | List of tags for categorizing tasks |
| created_at | datetime | Yes | System timestamp | When the task was created |
| updated_at | datetime | No | System timestamp | When the task was last updated |
| completed_at | datetime | No | System timestamp | When the task was marked as completed |

### Priority Enum Values

- `high`: High priority tasks that require immediate attention
- `medium`: Medium priority tasks (default value)
- `low`: Low priority tasks that can be deferred

### Status Enum Values

- `pending`: Task is not started yet
- `in_progress`: Task is currently being worked on
- `completed`: Task has been completed

### Validation Rules

1. **Priority validation**: Priority must be one of `high`, `medium`, or `low`
2. **Title validation**: Title must be 1-200 characters and non-empty
3. **Description validation**: Description must be 0-1000 characters
4. **Tags validation**: 
   - Each tag must be 1-50 characters and contain only alphanumeric characters and hyphens
   - Maximum of 10 tags per task
   - Tags should be case-insensitive but stored in lowercase
5. **Status validation**: Status must be one of `pending`, `in_progress`, or `completed`
6. **Timestamp validation**: 
   - `created_at` is system-generated and mandatory
   - `updated_at` is updated whenever the task is modified
   - `completed_at` is set when status changes to `completed` and cleared when status changes from `completed`

### State Transitions

- When status changes to `completed`, `completed_at` is set to current timestamp
- When status changes from `completed` to any other status, `completed_at` is cleared
- `updated_at` is updated on every modification

## Entity: TaskList

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| tasks | list of Task | Yes | Collection of tasks |
| total_count | integer | Yes | Total number of tasks in the list |

### Methods/Operations

1. **add_task(task)**: Add a new task to the list
2. **remove_task(task_id)**: Remove a task by ID
3. **find_by_id(task_id)**: Find a task by its ID
4. **search(keyword)**: Find tasks with keyword in title or description
5. **filter_by_priority(priority)**: Filter tasks by priority level
6. **filter_by_status(status)**: Filter tasks by status
7. **filter_by_tag(tag)**: Filter tasks by a specific tag
8. **sort_by_priority()**: Sort tasks with high priority first, then medium, then low
9. **sort_by_title()**: Sort tasks alphabetically by title
10. **sort_by_created_date()**: Sort tasks by creation date

### Search & Filter Operations

- **Search operation**: Case-insensitive search in both title and description fields
- **Filter operations**: Can be combined (AND logic) - e.g., filter by high priority AND work tag
- **Sort operations**: Applied after filtering, maintains stable sort for equal values

## Relationships

- Each Task exists independently in the TaskList collection
- Tags are stored directly in the Task entity, not in a separate table (to maintain in-memory simplicity)
- No foreign key relationships needed in this in-memory implementation

## Example Instances

```python
task_example_1 = {
    "id": "task-123",
    "title": "Implement priority feature",
    "description": "Add priority levels to tasks",
    "status": "in_progress",
    "priority": "high",
    "tags": ["development", "feature", "priority"],
    "created_at": "2025-12-02T10:00:00Z",
    "updated_at": "2025-12-02T11:30:00Z",
    "completed_at": None
}

task_example_2 = {
    "id": "task-124",
    "title": "Write documentation",
    "description": "Create user guide for new features",
    "status": "pending",
    "priority": "medium",
    "tags": ["documentation", "guide"],
    "created_at": "2025-12-02T09:15:00Z",
    "updated_at": "2025-12-02T09:15:00Z",
    "completed_at": None
}
```

## In-Memory Storage Model

The TaskList will be implemented as a simple Python list with in-memory storage. For this feature, we'll maintain the existing in-memory storage approach from the base application, simply extending the Task model with additional attributes.

The in-memory collection will support the following operations efficiently:
- O(1) access for finding tasks by ID using a dictionary lookup
- O(n) operations for search, filtering, and sorting (acceptable for console application with limited dataset)
- O(n log n) for sorting operations when required