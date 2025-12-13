"""Integration test for marking tasks complete via CLI."""

import pytest
from unittest.mock import Mock, patch
from io import StringIO
from src.ui.cli import TodoCLI
from src.services.task_service import TaskService
from src.domain.task import Task


def test_complete_task_via_cli():
    """Test completing a task through the CLI interface."""
    # Create a mock task service
    mock_task_service = Mock(spec=TaskService)
    
    # Create a mock task to return
    mock_task = Task(id=1, description="Test task", is_completed=False)
    mock_task_service.mark_task_complete.return_value = mock_task
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Simulate user input for task ID
    with patch('builtins.input', return_value='1'):
        # Capture printed output
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            cli._complete_task("complete 1")
        
        output = captured_output.getvalue()
        
        # Verify the output message
        assert "Task 1 marked as complete: Test task" in output
        
        # Verify the task service method was called with the correct ID
        mock_task_service.mark_task_complete.assert_called_once_with(1)


def test_complete_invalid_task_id():
    """Test completing a task with an invalid ID."""
    # Create a mock task service
    mock_task_service = Mock(spec=TaskService)
    
    # Mock the service to raise an exception when completing
    mock_task_service.mark_task_complete.side_effect = Exception("Task not found")
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._complete_task("complete 999")
    
    output = captured_output.getvalue()
    
    # Verify the error message
    assert "Error completing task" in output
    
    # Verify the task service method was called
    mock_task_service.mark_task_complete.assert_called_once_with(999)


def test_complete_task_with_invalid_format():
    """Test completing a task with an invalid command format."""
    # Create a mock task service (should not be called)
    mock_task_service = Mock(spec=TaskService)
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._complete_task("complete")  # Missing task ID
    
    output = captured_output.getvalue()
    
    # Verify the usage message
    assert "Usage: complete <task_id>" in output
    
    # Verify the task service method was not called
    mock_task_service.mark_task_complete.assert_not_called()


def test_complete_task_with_non_numeric_id():
    """Test completing a task with a non-numeric ID."""
    # Create a mock task service (should not be called)
    mock_task_service = Mock(spec=TaskService)
    
    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)
    
    # Capture printed output
    captured_output = StringIO()
    with patch('sys.stdout', captured_output):
        cli._complete_task("complete abc")  # Non-numeric task ID
    
    output = captured_output.getvalue()
    
    # Verify the error message
    assert "Task ID must be a number" in output
    
    # Verify the task service method was not called
    mock_task_service.mark_task_complete.assert_not_called()