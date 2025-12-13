"""Service tests for TaskService functionality."""

import pytest
from src.services.task_service import TaskService
from src.domain.errors import InvalidTaskDescription, TaskLimitExceeded, TaskNotFound
from src.domain.task_list import TaskList


def test_create_task_with_valid_description():
    """Test creating a task with valid description."""
    service = TaskService()

    task = service.create_task("Buy groceries")

    assert task is not None
    assert task.description == "Buy groceries"
    assert task.is_completed is False


def test_create_task_with_priority():
    """Test creating a task with specific priority."""
    service = TaskService()

    task = service.create_task("Buy groceries", priority='high')

    assert task is not None
    assert task.priority == 'high'


def test_create_task_with_tags():
    """Test creating a task with tags."""
    service = TaskService()

    task = service.create_task("Buy groceries", tags=['home', 'urgent'])

    assert task is not None
    assert 'home' in task.tags
    assert 'urgent' in task.tags


def test_create_task_with_empty_description():
    """Test creating a task with empty description raises error."""
    service = TaskService()

    with pytest.raises(InvalidTaskDescription):
        service.create_task("")


def test_create_task_with_whitespace_description():
    """Test creating a task with whitespace-only description raises error."""
    service = TaskService()

    with pytest.raises(InvalidTaskDescription):
        service.create_task("   ")


def test_create_task_with_long_description():
    """Test creating a task with description exceeding 2000 chars raises error."""
    service = TaskService()
    long_desc = "x" * 2001

    with pytest.raises(InvalidTaskDescription):
        service.create_task(long_desc)


def test_create_multiple_tasks():
    """Test creating multiple tasks assigns unique IDs."""
    service = TaskService()

    task1 = service.create_task("First task")
    task2 = service.create_task("Second task")

    assert task1.id == 1
    assert task2.id == 2
    assert task1.description == "First task"
    assert task2.description == "Second task"


def test_task_limit_exceeded():
    """Test creating tasks beyond limit raises error."""
    service = TaskService()
    # Create a task list with a limit of 1
    limited_list = TaskList(max_tasks=1)
    service = TaskService(limited_list)

    # First task should succeed
    task1 = service.create_task("First task")
    assert task1.id == 1

    # Second task should fail
    with pytest.raises(TaskLimitExceeded):
        service.create_task("Second task")


def test_get_all_tasks_empty_list():
    """Test getting all tasks from an empty service."""
    service = TaskService()

    all_tasks = service.get_all_tasks()

    assert len(all_tasks) == 0


def test_get_all_tasks_with_tasks():
    """Test getting all tasks from a service with tasks."""
    service = TaskService()

    # Create some tasks
    task1 = service.create_task("Task 1")
    task2 = service.create_task("Task 2")
    task3 = service.create_task("Task 3")

    all_tasks = service.get_all_tasks()

    assert len(all_tasks) == 3

    # Check that all created tasks are in the returned list
    task_descriptions = [task.description for task in all_tasks]
    assert task1.description in task_descriptions
    assert task2.description in task_descriptions
    assert task3.description in task_descriptions


def test_get_individual_task():
    """Test getting a specific task by ID."""
    service = TaskService()

    # Create a task
    original_task = service.create_task("Test task")
    task_id = original_task.id

    # Retrieve the same task
    retrieved_task = service.get_task(task_id)

    assert retrieved_task.id == task_id
    assert retrieved_task.description == "Test task"
    assert retrieved_task.is_completed is False


def test_get_nonexistent_task():
    """Test getting a task that doesn't exist raises error."""
    service = TaskService()

    with pytest.raises(TaskNotFound):
        service.get_task(999)


def test_get_task_after_completion():
    """Test getting a task that has been completed."""
    service = TaskService()

    original_task = service.create_task("Test task")
    task_id = original_task.id
    assert original_task.is_completed is False

    # Complete the task
    completed_task = service.mark_task_complete(task_id)
    assert completed_task.is_completed is True

    # Retrieve the task again
    retrieved_task = service.get_task(task_id)
    assert retrieved_task.id == task_id
    assert retrieved_task.is_completed is True


def test_get_task_after_update():
    """Test getting a task that has been updated."""
    service = TaskService()

    original_task = service.create_task("Original task")
    task_id = original_task.id
    assert original_task.description == "Original task"

    # Update the task
    updated_task = service.update_task(task_id, "Updated task")
    assert updated_task.description == "Updated task"

    # Retrieve the task again
    retrieved_task = service.get_task(task_id)
    assert retrieved_task.id == task_id
    assert retrieved_task.description == "Updated task"


def test_mark_task_complete():
    """Test marking a task as complete."""
    service = TaskService()

    # Create a task
    original_task = service.create_task("Test task")
    task_id = original_task.id
    assert original_task.is_completed is False

    # Complete the task
    completed_task = service.mark_task_complete(task_id)

    assert completed_task.id == task_id
    assert completed_task.is_completed is True


def test_mark_nonexistent_task_complete():
    """Test marking a non-existent task as complete raises error."""
    service = TaskService()

    with pytest.raises(TaskNotFound):
        service.mark_task_complete(999)


def test_mark_already_completed_task():
    """Test marking an already completed task."""
    service = TaskService()

    # Create and complete a task
    original_task = service.create_task("Test task")
    task_id = original_task.id
    completed_task = service.mark_task_complete(task_id)
    assert completed_task.is_completed is True

    # Try to complete it again - should still work
    recompleted_task = service.mark_task_complete(task_id)
    assert recompleted_task.id == task_id
    assert recompleted_task.is_completed is True


def test_get_task_after_completion():
    """Test getting a task after it has been completed."""
    service = TaskService()

    # Create a task
    original_task = service.create_task("Test task")
    task_id = original_task.id
    assert original_task.is_completed is False

    # Complete the task
    service.mark_task_complete(task_id)

    # Retrieve the task again
    retrieved_task = service.get_task(task_id)
    assert retrieved_task.id == task_id
    assert retrieved_task.is_completed is True


def test_task_persists_completion():
    """Test that completion status persists in the task list."""
    service = TaskService()

    # Create a task
    original_task = service.create_task("Test task")
    task_id = original_task.id
    assert original_task.is_completed is False

    # Complete the task
    service.mark_task_complete(task_id)

    # Verify all tasks shows the task as completed
    all_tasks = service.get_all_tasks()
    completed_task = next((t for t in all_tasks if t.id == task_id), None)
    assert completed_task is not None
    assert completed_task.is_completed is True


def test_delete_task():
    """Test deleting a task."""
    service = TaskService()

    # Create a task
    original_task = service.create_task("Test task")
    task_id = original_task.id
    assert original_task is not None

    # Verify the task exists
    all_tasks_before = service.get_all_tasks()
    assert len(all_tasks_before) == 1

    # Delete the task
    result = service.delete_task(task_id)

    assert result is True

    # Verify the task no longer exists
    all_tasks_after = service.get_all_tasks()
    assert len(all_tasks_after) == 0


def test_delete_nonexistent_task():
    """Test deleting a non-existent task returns False."""
    service = TaskService()

    result = service.delete_task(999)
    assert result is False


def test_get_deleted_task_fails():
    """Test that getting a deleted task raises an error."""
    service = TaskService()

    # Create a task
    original_task = service.create_task("Test task")
    task_id = original_task.id
    assert original_task is not None

    # Delete the task
    result = service.delete_task(task_id)
    assert result is True

    # Trying to get the deleted task should raise an error
    with pytest.raises(TaskNotFound):
        service.get_task(task_id)


def test_delete_task_then_create_new():
    """Test that deleting a task and creating a new one works properly."""
    service = TaskService()

    # Create first task
    task1 = service.create_task("First task")
    task1_id = task1.id
    assert task1_id == 1

    # Delete the first task
    result = service.delete_task(task1_id)
    assert result is True

    # Create a new task - it should get the next available ID
    task2 = service.create_task("Second task")
    task2_id = task2.id
    # Note: The behavior depends on TaskList implementation,
    # but typically IDs are not reused after deletion
    assert task2_id > task1_id  # The ID will be incremented


def test_delete_task_persists_change():
    """Test that deletion persists in the service's task list."""
    service = TaskService()

    # Create two tasks
    task1 = service.create_task("Task 1")
    task2 = service.create_task("Task 2")
    task1_id = task1.id
    task2_id = task2.id

    # Verify both exist
    all_tasks = service.get_all_tasks()
    assert len(all_tasks) == 2

    # Delete one of them
    result = service.delete_task(task1_id)
    assert result is True

    # Verify only the other one remains
    remaining_tasks = service.get_all_tasks()
    assert len(remaining_tasks) == 1
    assert remaining_tasks[0].id == task2_id
    assert remaining_tasks[0].description == "Task 2"


def test_update_task_with_priority():
    """Test updating a task with a new priority."""
    service = TaskService()
    original_task = service.create_task("Test task", priority='low')
    task_id = original_task.id
    assert original_task.priority == 'low'

    # Update the priority
    updated_task = service.update_task(task_id, priority='high')
    assert updated_task.priority == 'high'

    # Verify the change persists
    retrieved_task = service.get_task(task_id)
    assert retrieved_task.priority == 'high'


def test_update_task_with_tags():
    """Test updating a task with new tags."""
    service = TaskService()
    original_task = service.create_task("Test task", tags=['work'])
    task_id = original_task.id
    assert original_task.tags == ['work']

    # Update the tags
    updated_task = service.update_task(task_id, tags=['home', 'urgent'])
    assert 'home' in updated_task.tags
    assert 'urgent' in updated_task.tags
    assert 'work' not in updated_task.tags

    # Verify the change persists
    retrieved_task = service.get_task(task_id)
    assert 'home' in retrieved_task.tags
    assert 'urgent' in retrieved_task.tags
    assert 'work' not in retrieved_task.tags


def test_update_task_with_multiple_properties():
    """Test updating multiple properties of a task."""
    service = TaskService()
    original_task = service.create_task("Test task", priority='low', tags=['work'])
    task_id = original_task.id
    assert original_task.priority == 'low'
    assert original_task.tags == ['work']

    # Update multiple properties
    updated_task = service.update_task(task_id, title="Updated task", priority='high', tags=['personal'])
    assert updated_task.description == "Updated task"
    assert updated_task.priority == 'high'
    assert updated_task.tags == ['personal']

    # Verify the changes persist
    retrieved_task = service.get_task(task_id)
    assert retrieved_task.description == "Updated task"
    assert retrieved_task.priority == 'high'
    assert retrieved_task.tags == ['personal']


def test_update_task_with_status():
    """Test updating a task status."""
    service = TaskService()
    original_task = service.create_task("Test task")
    task_id = original_task.id
    assert original_task.is_completed is False

    # Update the status to completed
    updated_task = service.update_task(task_id, status='completed')
    assert updated_task.is_completed is True

    # Verify the change persists
    retrieved_task = service.get_task(task_id)
    assert retrieved_task.is_completed is True

    # Update the status back to pending
    updated_task_again = service.update_task(task_id, status='pending')
    assert updated_task_again.is_completed is False

    # Verify the change persists
    retrieved_task_again = service.get_task(task_id)
    assert retrieved_task_again.is_completed is False


def test_search_tasks():
    """Test searching for tasks by keyword."""
    service = TaskService()
    task1 = service.create_task("Buy groceries for the house")
    task2 = service.create_task("Walk the dog")
    task3 = service.create_task("Do house cleaning")
    task4 = service.create_task("Complete project", priority='high', tags=['work', 'urgent'])

    results = service.search_tasks("house")

    assert len(results) == 2
    descriptions = [task.description for task in results]
    assert "Buy groceries for the house" in descriptions
    assert "Do house cleaning" in descriptions


def test_filter_tasks_by_priority():
    """Test filtering tasks by priority."""
    service = TaskService()
    service.create_task("High priority task", priority='high')
    service.create_task("Medium priority task", priority='medium')
    service.create_task("Another high priority task", priority='high')
    service.create_task("Low priority task", priority='low')

    high_priority_tasks = service.filter_tasks_by_priority('high')

    assert len(high_priority_tasks) == 2
    priorities = [task.priority for task in high_priority_tasks]
    assert all(p == 'high' for p in priorities)
    descriptions = [task.description for task in high_priority_tasks]
    assert "High priority task" in descriptions
    assert "Another high priority task" in descriptions


def test_filter_tasks_by_tag():
    """Test filtering tasks by a specific tag."""
    service = TaskService()
    service.create_task("Task 1", tags=['work', 'urgent'])
    service.create_task("Task 2", tags=['home'])
    service.create_task("Task 3", tags=['work', 'personal'])
    service.create_task("Task 4", tags=['fun'])

    work_tasks = service.filter_tasks_by_tag('work')

    assert len(work_tasks) == 2
    descriptions = [task.description for task in work_tasks]
    assert "Task 1" in descriptions
    assert "Task 3" in descriptions


def test_sort_tasks_by_priority():
    """Test sorting tasks by priority (high -> medium -> low)."""
    service = TaskService()
    service.create_task("Low priority task", priority='low')
    service.create_task("High priority task", priority='high')
    service.create_task("Medium priority task", priority='medium')
    service.create_task("Another high priority task", priority='high')

    sorted_tasks = service.sort_tasks('priority')

    assert len(sorted_tasks) == 4

    # The order should be: high, high, medium, low
    expected_order = ['high', 'high', 'medium', 'low']
    actual_order = [task.priority for task in sorted_tasks]
    assert actual_order == expected_order


def test_sort_tasks_by_title():
    """Test sorting tasks alphabetically by title."""
    service = TaskService()
    service.create_task("Zebra task")
    service.create_task("Apple task")
    service.create_task("Mango task")
    service.create_task("Banana task")

    sorted_tasks = service.sort_tasks('title')

    assert len(sorted_tasks) == 4

    # The order should be alphabetical: Apple, Banana, Mango, Zebra
    expected_descriptions = ["Apple task", "Banana task", "Mango task", "Zebra task"]
    actual_descriptions = [task.description for task in sorted_tasks]
    assert actual_descriptions == expected_descriptions


def test_get_all_tasks_with_sorting():
    """Test getting all tasks with optional sorting."""
    service = TaskService()
    service.create_task("Low priority task", priority='low')
    service.create_task("High priority task", priority='high')
    service.create_task("Medium priority task", priority='medium')

    # Get tasks sorted by priority
    sorted_tasks = service.get_all_tasks(sort_by='priority')

    assert len(sorted_tasks) == 3

    # The order should be: high, medium, low
    expected_order = ['high', 'medium', 'low']
    actual_order = [task.priority for task in sorted_tasks]
    assert actual_order == expected_order


def test_get_all_tasks_with_filtering():
    """Test getting all tasks with optional filtering."""
    service = TaskService()
    service.create_task("High priority task", priority='high')
    service.create_task("Medium priority task", priority='medium')
    service.create_task("Another high priority task", priority='high')

    # Get tasks filtered by high priority
    filtered_tasks = service.get_all_tasks(filter_by={'priority': 'high'})

    assert len(filtered_tasks) == 2
    priorities = [task.priority for task in filtered_tasks]
    assert all(p == 'high' for p in priorities)


def test_get_all_tasks_with_keyword_filtering():
    """Test getting all tasks with keyword filtering."""
    service = TaskService()
    service.create_task("Buy groceries for the house")
    service.create_task("Walk the dog")
    service.create_task("Do house cleaning")

    # Get tasks filtered by keyword
    filtered_tasks = service.get_all_tasks(filter_by={'keyword': 'house'})

    assert len(filtered_tasks) == 2
    descriptions = [task.description for task in filtered_tasks]
    assert "Buy groceries for the house" in descriptions
    assert "Do house cleaning" in descriptions