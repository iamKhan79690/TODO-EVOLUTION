"""Unit tests for TaskList domain model."""

import pytest
from src.domain.task_list import TaskList
from src.domain.task import Task
from src.domain.errors import TaskNotFound, InvalidTaskDescription, TaskLimitExceeded


def test_tasklist_initialization():
    """Test TaskList initializes correctly."""
    task_list = TaskList()
    
    assert len(task_list.tasks) == 0
    assert task_list.next_id == 1


def test_tasklist_add_task():
    """Test adding a task to the task list."""
    task_list = TaskList()
    
    task_id = task_list.add_task("Buy groceries")
    
    assert task_id == 1
    assert len(task_list.tasks) == 1
    assert 1 in task_list.tasks
    assert task_list.tasks[1].description == "Buy groceries"
    assert task_list.tasks[1].is_completed is False


def test_tasklist_add_task_with_empty_description():
    """Test adding a task with empty description raises error."""
    task_list = TaskList()
    
    with pytest.raises(InvalidTaskDescription):
        task_list.add_task("")


def test_tasklist_add_task_with_long_description():
    """Test adding a task with description exceeding 2000 chars raises error."""
    task_list = TaskList()
    long_desc = "x" * 2001
    
    with pytest.raises(InvalidTaskDescription):
        task_list.add_task(long_desc)


def test_tasklist_get_task():
    """Test getting a specific task."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries")
    
    task = task_list.get_task(task_id)
    
    assert task is not None
    assert task.id == task_id
    assert task.description == "Buy groceries"


def test_tasklist_get_task_nonexistent():
    """Test getting a non-existent task returns None."""
    task_list = TaskList()
    
    task = task_list.get_task(999)
    
    assert task is None


def test_get_all_tasks_empty_list():
    """Test getting all tasks from an empty list."""
    task_list = TaskList()
    
    all_tasks = task_list.get_all_tasks()
    
    assert len(all_tasks) == 0


def test_get_all_tasks_with_tasks():
    """Test getting all tasks from a list with tasks."""
    task_list = TaskList()
    task_list.add_task("Task 1")
    task_list.add_task("Task 2")
    task_list.add_task("Task 3")
    
    all_tasks = task_list.get_all_tasks()
    
    assert len(all_tasks) == 3
    descriptions = [task.description for task in all_tasks]
    assert "Task 1" in descriptions
    assert "Task 2" in descriptions
    assert "Task 3" in descriptions


def test_get_pending_tasks_empty_list():
    """Test getting pending tasks from an empty list."""
    task_list = TaskList()
    
    pending_tasks = task_list.get_pending_tasks()
    
    assert len(pending_tasks) == 0


def test_get_pending_tasks_with_mixed_status():
    """Test getting pending tasks when list has mixed completion status."""
    task_list = TaskList()
    task_list.add_task("Pending task 1")
    task_id_2 = task_list.add_task("Completed task")
    task_list.add_task("Pending task 2")
    
    # Complete the second task
    task_list.complete_task(task_id_2)
    
    pending_tasks = task_list.get_pending_tasks()
    
    assert len(pending_tasks) == 2
    pending_descriptions = [task.description for task in pending_tasks]
    assert "Pending task 1" in pending_descriptions
    assert "Pending task 2" in pending_descriptions
    assert "Completed task" not in pending_descriptions


def test_get_completed_tasks_empty_list():
    """Test getting completed tasks from an empty list."""
    task_list = TaskList()
    
    completed_tasks = task_list.get_completed_tasks()
    
    assert len(completed_tasks) == 0


def test_get_completed_tasks_with_mixed_status():
    """Test getting completed tasks when list has mixed completion status."""
    task_list = TaskList()
    task_id_1 = task_list.add_task("Completed task 1")
    task_list.add_task("Pending task")
    task_id_3 = task_list.add_task("Completed task 2")
    
    # Complete the first and third tasks
    task_list.complete_task(task_id_1)
    task_list.complete_task(task_id_3)
    
    completed_tasks = task_list.get_completed_tasks()
    
    assert len(completed_tasks) == 2
    completed_descriptions = [task.description for task in completed_tasks]
    assert "Completed task 1" in completed_descriptions
    assert "Completed task 2" in completed_descriptions
    assert "Pending task" not in completed_descriptions


def test_tasklist_get_all_tasks():
    """Test getting all tasks."""
    task_list = TaskList()
    task_list.add_task("Buy groceries")
    task_list.add_task("Walk the dog")
    
    all_tasks = task_list.get_all_tasks()
    
    assert len(all_tasks) == 2
    descriptions = [task.description for task in all_tasks]
    assert "Buy groceries" in descriptions
    assert "Walk the dog" in descriptions


def test_tasklist_get_pending_tasks():
    """Test getting pending tasks."""
    task_list = TaskList()
    task_list.add_task("Buy groceries")
    task_id = task_list.add_task("Walk the dog")
    task_list.complete_task(task_id)  # Complete the second task
    
    pending_tasks = task_list.get_pending_tasks()
    
    assert len(pending_tasks) == 1
    assert pending_tasks[0].description == "Buy groceries"
    assert pending_tasks[0].is_completed is False


def test_tasklist_get_completed_tasks():
    """Test getting completed tasks."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries")
    task_list.add_task("Walk the dog")
    
    task_list.complete_task(task_id)  # Complete the first task
    
    completed_tasks = task_list.get_completed_tasks()
    
    assert len(completed_tasks) == 1
    assert completed_tasks[0].id == task_id
    assert completed_tasks[0].is_completed is True


def test_tasklist_complete_task():
    """Test completing a task."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries")
    
    result = task_list.complete_task(task_id)
    
    assert result is True
    assert task_list.tasks[task_id].is_completed is True


def test_tasklist_complete_task_nonexistent():
    """Test completing a non-existent task raises error."""
    task_list = TaskList()
    
    with pytest.raises(TaskNotFound):
        task_list.complete_task(999)


def test_tasklist_complete_task_already_completed():
    """Test completing a task that is already completed."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries")
    
    # Complete the task once
    task_list.complete_task(task_id)
    assert task_list.tasks[task_id].is_completed is True
    
    # Complete the task again - should still be completed
    result = task_list.complete_task(task_id)
    assert result is True
    assert task_list.tasks[task_id].is_completed is True


def test_tasklist_get_completed_tasks_after_completion():
    """Test that completed tasks appear in the get_completed_tasks list."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries")
    assert task_id == 1
    
    # Initially, no completed tasks
    completed_tasks = task_list.get_completed_tasks()
    assert len(completed_tasks) == 0
    
    # After completing the task
    task_list.complete_task(task_id)
    completed_tasks = task_list.get_completed_tasks()
    assert len(completed_tasks) == 1
    assert completed_tasks[0].id == task_id
    assert completed_tasks[0].is_completed is True


def test_tasklist_delete_task():
    """Test deleting a task."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries")
    
    # Verify the task exists before deletion
    assert len(task_list.tasks) == 1
    assert task_id in task_list.tasks
    
    result = task_list.delete_task(task_id)
    
    assert result is True
    assert len(task_list.tasks) == 0
    assert task_id not in task_list.tasks


def test_tasklist_delete_task_nonexistent():
    """Test deleting a non-existent task raises error."""
    task_list = TaskList()
    
    with pytest.raises(TaskNotFound):
        task_list.delete_task(999)


def test_tasklist_delete_multiple_tasks():
    """Test deleting tasks doesn't affect other tasks."""
    task_list = TaskList()
    task_id_1 = task_list.add_task("Task 1")
    task_id_2 = task_list.add_task("Task 2")
    task_id_3 = task_list.add_task("Task 3")
    
    # Verify all tasks exist
    assert len(task_list.tasks) == 3
    assert all(tid in task_list.tasks for tid in [task_id_1, task_id_2, task_id_3])
    
    # Delete task 2
    result = task_list.delete_task(task_id_2)
    
    assert result is True
    assert len(task_list.tasks) == 2
    assert task_id_2 not in task_list.tasks
    assert task_id_1 in task_list.tasks
    assert task_id_3 in task_list.tasks
    assert task_list.tasks[task_id_1].description == "Task 1"
    assert task_list.tasks[task_id_3].description == "Task 3"


def test_tasklist_delete_task_then_add_new():
    """Test that adding new tasks after deletion works correctly."""
    task_list = TaskList()
    task_id_1 = task_list.add_task("Task 1")
    task_id_2 = task_list.add_task("Task 2")
    
    # Delete the second task
    result = task_list.delete_task(task_id_2)
    assert result is True
    
    # Add a new task - it should get the next available ID
    new_task_id = task_list.add_task("Task 3")
    # The next_id should have been incremented, so the new task gets ID 3
    assert new_task_id == 3


def test_tasklist_update_task():
    """Test updating a task description."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries")
    
    result = task_list.update_task(task_id, "Buy groceries and cook dinner")
    
    assert result is True
    assert task_list.tasks[task_id].description == "Buy groceries and cook dinner"


def test_tasklist_update_task_nonexistent():
    """Test updating a non-existent task raises error."""
    task_list = TaskList()
    
    with pytest.raises(TaskNotFound):
        task_list.update_task(999, "New description")


def test_tasklist_task_limit():
    """Test task limit functionality."""
    task_list = TaskList(max_tasks=2)
    task_list.add_task("Task 1")
    task_list.add_task("Task 2")
    
    with pytest.raises(TaskLimitExceeded):
        task_list.add_task("Task 3")


def test_tasklist_update_task_with_invalid_description():
    """Test updating a task with invalid description raises error."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries")

    with pytest.raises(InvalidTaskDescription):
        task_list.update_task(task_id, "")  # Empty description


def test_tasklist_add_task_with_priority():
    """Test adding a task with a specific priority."""
    task_list = TaskList()

    task_id = task_list.add_task("Buy groceries", priority='high')

    assert task_id == 1
    assert task_list.tasks[1].priority == 'high'


def test_tasklist_add_task_with_tags():
    """Test adding a task with tags."""
    task_list = TaskList()

    task_id = task_list.add_task("Buy groceries", tags=['home', 'urgent'])

    assert task_id == 1
    assert 'home' in task_list.tasks[1].tags
    assert 'urgent' in task_list.tasks[1].tags


def test_tasklist_update_task_with_priority():
    """Test updating a task with a new priority."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries", priority='low')

    result = task_list.update_task(task_id, new_priority='high')

    assert result is True
    assert task_list.tasks[task_id].priority == 'high'


def test_tasklist_update_task_with_tags():
    """Test updating a task with new tags."""
    task_list = TaskList()
    task_id = task_list.add_task("Buy groceries", tags=['work'])

    result = task_list.update_task(task_id, new_tags=['home', 'urgent'])

    assert result is True
    assert 'home' in task_list.tasks[task_id].tags
    assert 'urgent' in task_list.tasks[task_id].tags
    assert 'work' not in task_list.tasks[task_id].tags


def test_tasklist_search_tasks():
    """Test searching for tasks by keyword."""
    task_list = TaskList()
    task_list.add_task("Buy groceries for the house")
    task_list.add_task("Walk the dog")
    task_list.add_task("Do house cleaning")

    # Add one with tags and priority
    task_list.add_task("Complete project", priority='high', tags=['work', 'urgent'])

    results = task_list.search_tasks("house")

    assert len(results) == 2
    descriptions = [task.description for task in results]
    assert "Buy groceries for the house" in descriptions
    assert "Do house cleaning" in descriptions

def test_tasklist_search_tasks_case_insensitive():
    """Test searching for tasks by keyword is case insensitive."""
    task_list = TaskList()
    task_list.add_task("Buy groceries for the HOUSE")
    task_list.add_task("Walk the dog")
    task_list.add_task("do house cleaning")

    results = task_list.search_tasks("house")

    assert len(results) == 2
    descriptions = [task.description for task in results]
    assert "Buy groceries for the HOUSE" in descriptions
    assert "do house cleaning" in descriptions

def test_tasklist_search_tasks_no_match():
    """Test searching for tasks with no matches."""
    task_list = TaskList()
    task_list.add_task("Buy groceries")
    task_list.add_task("Walk the dog")

    results = task_list.search_tasks("house")

    assert len(results) == 0

def test_tasklist_filter_by_priority():
    """Test filtering tasks by priority."""
    task_list = TaskList()
    task_list.add_task("High priority task", priority='high')
    task_list.add_task("Medium priority task", priority='medium')
    task_list.add_task("Another high priority task", priority='high')
    task_list.add_task("Low priority task", priority='low')

    high_priority_tasks = task_list.filter_by_priority('high')

    assert len(high_priority_tasks) == 2
    priorities = [task.priority for task in high_priority_tasks]
    assert all(p == 'high' for p in priorities)
    descriptions = [task.description for task in high_priority_tasks]
    assert "High priority task" in descriptions
    assert "Another high priority task" in descriptions

def test_tasklist_filter_by_invalid_priority():
    """Test filtering tasks by invalid priority raises error."""
    task_list = TaskList()
    task_list.add_task("Task", priority='high')

    with pytest.raises(ValueError, match="Priority must be one of"):
        task_list.filter_by_priority('critical')

def test_tasklist_filter_by_tag():
    """Test filtering tasks by a specific tag."""
    task_list = TaskList()
    task_list.add_task("Task 1", tags=['work', 'urgent'])
    task_list.add_task("Task 2", tags=['home'])
    task_list.add_task("Task 3", tags=['work', 'personal'])
    task_list.add_task("Task 4", tags=['fun'])

    work_tasks = task_list.filter_by_tag('work')

    assert len(work_tasks) == 2
    descriptions = [task.description for task in work_tasks]
    assert "Task 1" in descriptions
    assert "Task 3" in descriptions

def test_tasklist_filter_by_status():
    """Test filtering tasks by completion status."""
    task_list = TaskList()
    task_id_1 = task_list.add_task("Pending task")
    task_id_2 = task_list.add_task("Another pending task")
    task_id_3 = task_list.add_task("Completed task")
    task_id_4 = task_list.add_task("Another completed task")

    # Complete tasks 3 and 4
    task_list.complete_task(task_id_3)
    task_list.complete_task(task_id_4)

    pending_tasks = task_list.filter_by_status(False)  # Get pending tasks
    completed_tasks = task_list.filter_by_status(True)  # Get completed tasks

    assert len(pending_tasks) == 2
    assert len(completed_tasks) == 2

    pending_descriptions = [task.description for task in pending_tasks]
    completed_descriptions = [task.description for task in completed_tasks]

    assert "Pending task" in pending_descriptions
    assert "Another pending task" in pending_descriptions
    assert "Completed task" in completed_descriptions
    assert "Another completed task" in completed_descriptions

def test_tasklist_sort_by_priority():
    """Test sorting tasks by priority (high -> medium -> low)."""
    task_list = TaskList()
    task_list.add_task("Low priority task", priority='low')
    task_list.add_task("High priority task", priority='high')
    task_list.add_task("Medium priority task", priority='medium')
    task_list.add_task("Another high priority task", priority='high')

    sorted_tasks = task_list.sort_by_priority()

    assert len(sorted_tasks) == 4

    # The order should be: high, high, medium, low
    expected_order = ['high', 'high', 'medium', 'low']
    actual_order = [task.priority for task in sorted_tasks]
    assert actual_order == expected_order

def test_tasklist_sort_by_title():
    """Test sorting tasks alphabetically by description."""
    task_list = TaskList()
    task_list.add_task("Zebra task")
    task_list.add_task("Apple task")
    task_list.add_task("Mango task")
    task_list.add_task("Banana task")

    sorted_tasks = task_list.sort_by_title()

    assert len(sorted_tasks) == 4

    # The order should be alphabetical: Apple, Banana, Mango, Zebra
    expected_descriptions = ["Apple task", "Banana task", "Mango task", "Zebra task"]
    actual_descriptions = [task.description for task in sorted_tasks]
    assert actual_descriptions == expected_descriptions