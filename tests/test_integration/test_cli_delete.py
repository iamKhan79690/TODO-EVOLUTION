"""Integration test for deleting tasks via CLI."""

import pytest
from unittest.mock import Mock, patch
from io import StringIO
from src.ui.cli import TodoCLI
from src.services.task_service import TaskService
from src.domain.task import Task


def test_delete_task_via_cli():
    """Test deleting a task through the CLI interface."""
    # Create a mock task service
    mock_task_service = Mock(spec=TaskService)
    
    # Set up the mock to return True for successful deletion
    mock_task_service.delete_task.return_value = True
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Simulate user input for task ID
    with patch('builtins.input', return_value='1'):
        # Capture printed output
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            cli._delete_task("delete 1")
        
        output = captured_output.getvalue()
        
        # Verify the output message
        assert "Task 1 deleted successfully" in output
        
        # Verify the task service method was called with the correct ID
        mock_task_service.delete_task.assert_called_once_with(1)


def test_delete_nonexistent_task():
    """Test deleting a task that doesn't exist."""
    # Create a mock task service
    mock_task_service = Mock(spec=TaskService)
    
    # Set up the mock to return False for unsuccessful deletion
    mock_task_service.delete_task.return_value = False
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._delete_task("delete 999")
    
    output = captured_output.getvalue()
    
    # Verify the appropriate message
    assert "Task 999 not found" in output
    
    # Verify the task service method was called
    mock_task_service.delete_task.assert_called_once_with(999)


def test_delete_task_with_invalid_format():
    """Test deleting a task with an invalid command format."""
    # Create a mock task service (should not be called)
    mock_task_service = Mock(spec=TaskService)
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._delete_task("delete")  # Missing task ID
    
    output = captured_output.getvalue()
    
    # Verify the usage message
    assert "Usage: delete <task_id>" in output
    
    # Verify the task service method was not called
    mock_task_service.delete_task.assert_not_called()


def test_delete_task_with_non_numeric_id():
    """Test deleting a task with a non-numeric ID."""
    # Create a mock task service (should not be called)
    mock_task_service = Mock(spec=TaskService)
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._delete_task("delete abc")  # Non-numeric task ID
    
    output = captured_output.getvalue()
    
    # Verify the error message
    assert "Task ID must be a number" in output
    
    # Verify the task service method was not called
    mock_task_service.delete_task.assert_not_called()


def test_delete_task_error_handling():
    """Test error handling when deleting a task fails."""
    # Create a mock task service that raises an exception
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.delete_task.side_effect = Exception("Deletion failed")
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._delete_task("delete 1")
    
    output = captured_output.getvalue()
    
    # Verify the error message
    assert "Error deleting task" in output
    
    # Verify the task service method was called
    mock_task_service.delete_task.assert_called_once_with(1)