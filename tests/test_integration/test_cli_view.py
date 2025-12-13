"""Integration test for viewing tasks via CLI."""

import pytest
from unittest.mock import Mock, patch
from io import StringIO
from src.ui.cli import TodoCLI
from src.services.task_service import TaskService
from src.domain.task import Task


def test_view_tasks_via_cli():
    """Test viewing tasks through the CLI interface."""
    # Create a mock task service
    mock_task_service = Mock(spec=TaskService)

    # Create mock tasks to return
    mock_task1 = Task(id=1, description="Task 1", is_completed=False)
    mock_task2 = Task(id=2, description="Task 2", is_completed=True)

    mock_task_service.get_all_tasks.return_value = [mock_task1, mock_task2]

    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)

    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._list_tasks()

    output = captured_output.getvalue()

    # Verify the output contains the tasks
    assert "Task 1" in output
    assert "Task 2" in output
    assert "1." in output  # Task ID format is "ID. description"
    assert "2." in output  # Task ID format is "ID. description"
    assert "[ ] (Medium) 1. Task 1" in output  # Pending task with ID and description (includes priority)
    assert "[x] (Medium) 2. Task 2" in output  # Completed task with ID and description (includes priority)

    # Verify the task service method was called
    mock_task_service.get_all_tasks.assert_called_once()


def test_view_empty_tasks_list():
    """Test viewing an empty task list."""
    # Create a mock task service
    mock_task_service = Mock(spec=TaskService)
    
    # Return empty list
    mock_task_service.get_all_tasks.return_value = []
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._list_tasks()
    
    output = captured_output.getvalue()
    
    # Verify the output indicates no tasks
    assert "No tasks found" in output
    
    # Verify the task service method was called
    mock_task_service.get_all_tasks.assert_called_once()