# API Contract: Todo Operations

## Overview
This document describes the functional operations available in the console-based todo application. Though the application is CLI-based, these operations represent the underlying service layer functionality that could be exposed through an API in future phases.

## Operation Contracts

### 1. Create Task
- **Operation**: `task_service.create_task(description: str)`
- **Input**: Task description (string, 1-2000 characters)
- **Output**: Task object with ID, description, completion status, and creation timestamp
- **Success**: New task is created and returned with a unique ID
- **Errors**: 
  - `InvalidTaskDescription` if description is empty/whitespace or too long
  - `TaskLimitExceeded` if maximum task count would be exceeded

### 2. Get Task by ID
- **Operation**: `task_service.get_task(task_id: int)`
- **Input**: Task ID (positive integer)
- **Output**: Task object if found, error if not found
- **Success**: Returns the requested task
- **Errors**: `TaskNotFound` if ID does not exist

### 3. Get All Tasks
- **Operation**: `task_service.get_all_tasks()`
- **Input**: None
- **Output**: List of all tasks
- **Success**: Returns list of all tasks in the system

### 4. Mark Task Complete
- **Operation**: `task_service.mark_task_complete(task_id: int)`
- **Input**: Task ID (positive integer)
- **Output**: Updated Task object
- **Success**: Task is marked as complete and returned
- **Errors**: `TaskNotFound` if ID does not exist

### 5. Delete Task
- **Operation**: `task_service.delete_task(task_id: int)`
- **Input**: Task ID (positive integer)
- **Output**: Boolean indicating success
- **Success**: Task is removed from the system
- **Errors**: `TaskNotFound` if ID does not exist

### 6. Update Task Description
- **Operation**: `task_service.update_task(task_id: int, description: str)`
- **Input**: Task ID (positive integer), new description (string, 1-2000 characters)
- **Output**: Updated Task object
- **Success**: Task description is updated and returned
- **Errors**: 
  - `TaskNotFound` if ID does not exist
  - `InvalidTaskDescription` if description is invalid

## Validation Rules
- All descriptions must be 1-2000 characters
- All IDs must be positive integers
- Operations on non-existent IDs return `TaskNotFound` error
- Task limit is 1000 tasks per instance

## Error Response Format
```
{
  "error": {
    "type": "ErrorType",
    "message": "Human-readable error message",
    "code": 400-500
  }
}
```