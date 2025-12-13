# Data Model: Console-Based Todo Project

## Domain Entities

### Task (TodoItem)

**Description**: Represents a single todo item with its state and metadata

**Fields**:
- `id: int` - Unique identifier for the task (auto-generated)
- `description: str` - Human-readable description of the task
- `is_completed: bool` - Completion status (default: False)
- `created_at: datetime` - Timestamp when task was created

**Validation Rules**:
- Description must not be empty or contain only whitespace
- Description must be less than 2000 characters
- ID must be unique within the system
- ID must be a positive integer

**State Transitions**:
- `pending` → `completed`: When task is marked as complete
- `completed` → `pending`: When task is marked as incomplete (if feature is supported)

**Methods**:
- `complete()`: Mark the task as complete
- `reopen()`: Mark the task as incomplete (if feature is supported)
- `update_description(new_description: str)`: Update the task description

### TaskList

**Description**: Collection of tasks with operations to manage them

**Fields**:
- `tasks: Dict[int, Task]` - Dictionary mapping task IDs to Task objects
- `next_id: int` - Next available ID for new tasks (auto-incrementing)

**Validation Rules**:
- No duplicate task IDs
- Maximum of 1000 tasks per instance
- Task IDs must be positive integers

**Methods**:
- `add_task(description: str) -> int`: Add a new task and return its ID
- `get_task(task_id: int) -> Task | None`: Retrieve a task by ID
- `get_all_tasks() -> List[Task]`: Get all tasks in the list
- `get_pending_tasks() -> List[Task]`: Get only incomplete tasks
- `get_completed_tasks() -> List[Task]`: Get only completed tasks
- `complete_task(task_id: int) -> bool`: Mark a task as complete (returns success)
- `delete_task(task_id: int) -> bool`: Remove a task from the list (returns success)
- `update_task(task_id: int, new_description: str) -> bool`: Update task description (returns success)

## Service Layer Contracts

### Task Service Interface

**Description**: Business logic layer that orchestrates operations on tasks

**Methods**:
- `create_task(description: str) -> Result[Task, Error]`: Create a new task with validation
- `get_task(task_id: int) -> Result[Task, Error]`: Get a specific task
- `get_all_tasks() -> List[Task]`: Get all tasks
- `mark_task_complete(task_id: int) -> Result[Task, Error]`: Mark task as complete
- `delete_task(task_id: int) -> Result[bool, Error]`: Delete a task
- `update_task(task_id: int, description: str) -> Result[Task, Error]`: Update a task description

## Validation Rules

### Input Validation
- Task descriptions must be non-empty and not just whitespace
- Task descriptions must be less than 2000 characters
- Task IDs must be positive integers that exist in the system
- Operations on non-existent tasks must return appropriate errors

### Business Rules
- A task cannot be marked complete if it's already complete (optional, depending on requirements)
- Only the task owner can modify the task (in single-user context, this is implicitly satisfied)
- Task ordering can be configurable (by creation date, by ID, etc.)

## Error Types

### Domain Errors
- `TaskNotFound`: Requested task ID does not exist
- `InvalidTaskDescription`: Task description fails validation
- `TaskLimitExceeded`: Attempting to create a task when limit is reached
- `InvalidTaskStateTransition`: Attempting an invalid state change

## Constraints

### Performance Constraints
- Operations should complete within 10 seconds for up to 1000 tasks
- Memory usage should not exceed 100MB for 1000 tasks
- Task creation should be O(1), retrieval O(1), deletion O(1)

### Domain Constraints
- Tasks are immutable except for their completion status and description
- Task IDs are never reused after deletion
- All operations maintain data consistency