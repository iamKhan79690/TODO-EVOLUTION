# Quickstart Guide: Task Enhancement Features

**Feature**: 002-task-enhancements  
**Date**: 2025-12-02  
**Version**: 1.0

## Overview

This guide provides developers with information to quickly understand and start working on the task enhancement features, which include:

1. Task priorities (High, Medium, Low)
2. Task tagging functionality
3. Search capabilities
4. Filtering by priority, status, and tags
5. Sorting by priority and title

## Prerequisites

- Python 3.13+ installed
- UV package manager installed
- Understanding of the existing console todo application

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
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

### 1. Updated Task Model

The `Task` model has been extended with:
- `priority` attribute: Enum with values "high", "medium", "low" (default: "medium")
- `tags` attribute: List of strings for categorizing tasks

### 2. Enhanced UI Features

The console interface now includes:
- Prompts for priority and tags when creating tasks
- Display of priority and tags in task lists
- New search and filter menu options
- Sorting options for task lists

### 3. Service Layer Updates

The `TaskService` now provides:
- Search functionality across titles and descriptions
- Filtering by priority, status, and tags
- Sorting by priority and title

## Project Structure

```
src/
├── domain/
│   ├── task.py          # Updated with priority and tags
│   └── task_list.py     # New methods for search/filter/sort
├── services/
│   └── task_service.py  # Updated with new operations
└── ui/
    ├── cli.py           # Updated UI with new features
    ├── menu.py          # New search/filter menu
    └── formatters.py    # Updated display format
```

## Implementation Guidelines

### Creating Tasks with New Features

When implementing the "Add Task" workflow:

1. Prompt for priority after title and description: `Select priority (1: High, 2: Medium, 3: Low)`
2. Prompt for tags: `Enter tags (comma-separated): work, urgent`
3. Validate priority is one of the allowed values
4. Validate tags follow naming conventions

### Display Format

Update the task display format to: `[ ] 1. Buy Milk (High) [Home] - Description...`

### Search Implementation

- Search should be case-insensitive
- Look for matches in both title and description
- If a task matches in both title and description, still return it only once

### Filter Implementation

- Multiple filters should work with AND logic (e.g., high priority AND work tag)
- When filtering by tags, match any of the tags in the task's tag list

### Sort Implementation

- Priority sorting: High → Medium → Low
- Title sorting: A → Z (alphabetical)

## Testing Requirements

1. **Domain Tests**: Test the extended Task model with priorities and tags
2. **Service Tests**: Test search, filter, and sort operations
3. **Integration Tests**: Test CLI interactions for new features

Example test cases to include:
```python
# Test creating a task with priority and tags
def test_create_task_with_priority_and_tags():
    # Implementation here

# Test filtering tasks by priority
def test_filter_tasks_by_priority():
    # Implementation here

# Test searching tasks by keyword
def test_search_tasks_by_keyword():
    # Implementation here
```

## Common Development Tasks

### Adding Priority Validation

```python
def validate_priority(priority):
    valid_priorities = ['high', 'medium', 'low']
    if priority not in valid_priorities:
        raise ValidationError(f"Priority must be one of {valid_priorities}")
```

### Adding Tag Validation

```python
def validate_tags(tags):
    if not isinstance(tags, list):
        raise ValidationError("Tags must be a list")
    for tag in tags:
        if not (1 <= len(tag) <= 50):
            raise ValidationError(f"Each tag must be 1-50 characters")
        if not re.match(r'^[a-zA-Z0-9-]+$', tag):
            raise ValidationError(f"Tag '{tag}' contains invalid characters")
        if len(tags) > 10:
            raise ValidationError("Maximum 10 tags allowed per task")
```

## Error Handling

- Validate all inputs before creating or updating tasks
- Handle cases where no tasks match search/filters
- Ensure consistent timestamp handling
- Provide clear error messages to users

## Performance Considerations

- Search, filter, and sort operations should complete in under 1 second
- For in-memory implementation, efficiency is less critical but still consider O(n) vs O(n²) operations
- Use appropriate data structures for frequent operations

## Next Steps

1. Review the [Data Model](data-model.md) for detailed entity specifications
2. Review the [Task Service Contract](contracts/task-service-contract.md) for interface specifications
3. Implement the feature following the [Tasks](tasks.md) breakdown (to be generated)