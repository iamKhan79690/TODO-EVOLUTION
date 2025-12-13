"""Integration test for adding a task via CLI."""

import pytest
from unittest.mock import Mock, patch
from src.ui.cli import TodoCLI
from src.services.task_service import TaskService


def test_add_task_via_cli():
    """Test adding a task through the CLI interface."""
    # Create a mock task service
    mock_task_service = Mock(spec=TaskService)

    # Create a mock task to return
    mock_task = Mock()
    mock_task.id = 1
    mock_task.description = "Buy groceries"
    mock_task_service.create_task.return_value = mock_task

    # Create CLI instance with mock service
    cli = TodoCLI(mock_task_service)

    # Mock the input function to simulate user input
    with patch('builtins.input', return_value='Buy groceries'):
        # Capture printed output
        with patch('sys.stdout') as mock_stdout:
            cli._add_task()

            # Verify the task service was called with the correct parameters
            # The new create_task signature is (title, description="", priority="medium", tags=None, due_date=None, recurrence_rule=None, reminder=None)
            mock_task_service.create_task.assert_called_once_with(
                "Buy groceries",
                "Buy groceries - Buy groceries",  # Full description (title + description)
                "medium",  # Default priority
                ['Buy groceries'],  # Default tags (using title as tag)
                None,  # No due date
                None,  # No recurrence rule
                None   # No reminder
            )