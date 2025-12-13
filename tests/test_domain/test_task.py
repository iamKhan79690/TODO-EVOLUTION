"""Unit tests for Task domain model."""

import pytest
from datetime import datetime
from src.domain.task import Task
from src.domain.errors import TaskLimitExceeded, InvalidTaskDescription


def test_task_creation_with_valid_data():
    """Test creating a task with valid data."""
    task = Task(id=1, description="Buy groceries")

    assert task.id == 1
    assert task.description == "Buy groceries"
    assert task.is_completed is False
    assert isinstance(task.created_at, datetime)
    assert task.priority == 'medium'  # Default priority
    assert task.tags == []  # Default tags


def test_task_creation_with_priority():
    """Test creating a task with specific priority."""
    task = Task(id=1, description="Buy groceries", priority='high')

    assert task.id == 1
    assert task.description == "Buy groceries"
    assert task.priority == 'high'


def test_task_creation_with_tags():
    """Test creating a task with specific tags."""
    task = Task(id=1, description="Buy groceries", tags=['work', 'urgent'])

    assert task.id == 1
    assert task.description == "Buy groceries"
    assert task.tags == ['work', 'urgent']


def test_task_creation_with_completion_status():
    """Test creating a task with completion status."""
    task = Task(id=1, description="Buy groceries", is_completed=True)

    assert task.id == 1
    assert task.description == "Buy groceries"
    assert task.is_completed is True


def test_task_creation_with_empty_description():
    """Test creating a task with empty description raises error."""
    with pytest.raises(ValueError, match="Task description cannot be empty"):
        Task(id=1, description="")


def test_task_creation_with_whitespace_description():
    """Test creating a task with whitespace-only description raises error."""
    with pytest.raises(ValueError, match="Task description cannot be empty"):
        Task(id=1, description="   ")


def test_task_creation_with_long_description():
    """Test creating a task with description exceeding 2000 chars raises error."""
    long_desc = "x" * 2001

    with pytest.raises(ValueError, match="Task description must be less than 2000 characters"):
        Task(id=1, description=long_desc)


def test_task_creation_with_invalid_priority():
    """Test creating a task with invalid priority raises error."""
    with pytest.raises(ValueError, match="Priority must be one of"):
        Task(id=1, description="Buy groceries", priority='critical')


def test_task_creation_with_invalid_tag_length():
    """Test creating a task with invalid tag length raises error."""
    with pytest.raises(ValueError, match="Each tag must be 1-50 characters"):
        Task(id=1, description="Buy groceries", tags=['a' * 51])


def test_task_creation_with_invalid_tag_characters():
    """Test creating a task with invalid tag characters raises error."""
    with pytest.raises(ValueError, match="contains invalid characters"):
        Task(id=1, description="Buy groceries", tags=['work@home'])


def test_task_creation_with_too_many_tags():
    """Test creating a task with too many tags raises error."""
    with pytest.raises(ValueError, match="Maximum 10 tags allowed per task"):
        Task(id=1, description="Buy groceries", tags=[f'tag{i}' for i in range(11)])


def test_task_complete_method_additional():
    """Test the complete() method sets is_completed to True."""
    task = Task(id=1, description="Buy groceries")
    assert task.is_completed is False

    task.complete()
    assert task.is_completed is True


def test_task_complete_method_sets_completed_at():
    """Test the complete() method sets completed_at timestamp."""
    task = Task(id=1, description="Buy groceries")
    assert task.completed_at is None

    task.complete()
    assert task.completed_at is not None


def test_task_complete_method_already_completed():
    """Test the complete() method works on an already completed task."""
    task = Task(id=1, description="Buy groceries", is_completed=True)
    assert task.is_completed is True

    task.complete()  # Should still be completed
    assert task.is_completed is True


def test_task_reopen_method_additional():
    """Test the reopen() method sets is_completed to False."""
    task = Task(id=1, description="Buy groceries", is_completed=True)
    assert task.is_completed is True

    task.reopen()
    assert task.is_completed is False


def test_task_reopen_method_clears_completed_at():
    """Test the reopen() method clears completed_at timestamp."""
    task = Task(id=1, description="Buy groceries", is_completed=True)
    task.complete()  # Set completed_at
    assert task.completed_at is not None

    task.reopen()
    assert task.completed_at is None


def test_task_reopen_method_already_open():
    """Test the reopen() method works on an already open task."""
    task = Task(id=1, description="Buy groceries", is_completed=False)
    assert task.is_completed is False

    task.reopen()  # Should still be open
    assert task.is_completed is False


def test_update_priority():
    """Test updating task priority."""
    task = Task(id=1, description="Buy groceries", priority='low')
    assert task.priority == 'low'

    task.update_priority('high')
    assert task.priority == 'high'


def test_update_priority_invalid():
    """Test updating task priority with invalid value raises error."""
    task = Task(id=1, description="Buy groceries", priority='low')

    with pytest.raises(ValueError, match="Priority must be one of"):
        task.update_priority('critical')


def test_add_tag():
    """Test adding a tag to task."""
    task = Task(id=1, description="Buy groceries", tags=['work'])
    assert 'home' not in task.tags

    task.add_tag('home')
    assert 'home' in task.tags
    assert len(task.tags) == 2


def test_add_tag_duplicate():
    """Test adding a duplicate tag doesn't duplicate it."""
    task = Task(id=1, description="Buy groceries", tags=['work'])
    assert task.tags == ['work']

    task.add_tag('work')
    assert task.tags == ['work']  # Still only one 'work' tag


def test_add_tag_invalid():
    """Test adding an invalid tag raises error."""
    task = Task(id=1, description="Buy groceries", tags=['work'])

    with pytest.raises(ValueError, match="Tag must be 1-50 characters"):
        task.add_tag('a' * 51)


def test_remove_tag():
    """Test removing a tag from task."""
    task = Task(id=1, description="Buy groceries", tags=['work', 'home'])
    assert 'work' in task.tags

    task.remove_tag('work')
    assert 'work' not in task.tags
    assert 'home' in task.tags


def test_update_tags():
    """Test updating all tags for task."""
    task = Task(id=1, description="Buy groceries", tags=['work'])
    assert task.tags == ['work']

    task.update_tags(['personal', 'urgent'])
    assert task.tags == ['personal', 'urgent']


def test_update_tags_invalid():
    """Test updating with invalid tags raises error."""
    task = Task(id=1, description="Buy groceries", tags=['work'])

    with pytest.raises(ValueError, match="Tag must be 1-50 characters"):
        task.update_tags(['valid', 'a' * 51])


def test_task_updated_at_on_modification():
    """Test that updating task properties updates the updated_at timestamp."""
    task = Task(id=1, description="Buy groceries")
    original_updated_at = task.updated_at
    assert original_updated_at is None  # updated_at is set on first modification

    task.update_priority('high')
    assert task.updated_at is not None
    assert task.updated_at != original_updated_at