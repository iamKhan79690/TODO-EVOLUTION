"""
MCP Task Tools

Provides task management tools for MCP server integration with AI agents.
Implements task CRUD operations with authentication, validation, and monitoring.
"""

import os
import sys
from pathlib import Path

# Ensure MCP server root is in path
MCP_ROOT = Path(__file__).parent.parent
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, EmbeddedResource

from services.task_service import TaskService
from services.fastapi_client import FastAPIClient, with_fastapi_client
from utils.correlation_ids import with_correlation_id, get_correlation_id
from utils.performance import track_performance, PerformanceContext
from utils.exceptions import (
    ValidationError,
    DatabaseError,
    TaskNotFoundError
)
from tools.auth_middleware import (
    require_authentication,
    get_user_context,
    validate_user_ownership
)

# Initialize FastMCP
mcp = FastMCP("Task Management Tools")

# Initialize task service
task_service = TaskService()


@mcp.tool()
@require_authentication
@with_correlation_id
async def add_task(
    title: str,
    jwt_token: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    recurrence_pattern: Optional[str] = None,
    _user_context: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task for the authenticated user.

    This tool allows AI agents to create tasks on behalf of users with proper
    authentication and validation. Supports optional description, priority levels,
    due dates, and recurrence patterns.

    Args:
        title: Task title (required, max 200 characters)
        jwt_token: JWT authentication token (required)
        description: Optional task description (max 1000 characters)
        priority: Optional priority level (low, medium, high, urgent)
        due_date: Optional due date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        recurrence_pattern: Optional recurrence pattern (none, daily, weekly, monthly, yearly)
        _user_context: User context from JWT middleware (injected)
        correlation_id: Correlation ID for tracing (injected)

    Returns:
        Dictionary containing:
        - success: Boolean indicating operation success
        - task_id: ID of the created task
        - title: Task title
        - description: Task description
        - priority: Task priority
        - due_date: Task due date (ISO format or None)
        - recurrence_pattern: Task recurrence pattern
        - is_completed: Completion status (always False for new tasks)
        - created_at: Creation timestamp (ISO format)
        - updated_at: Last update timestamp (ISO format)
        - message: Success message

    Raises:
        ValidationError: If input validation fails
        AuthenticationError: If JWT token is invalid or expired
        DatabaseError: If database operation fails
    """

    correlation_id = correlation_id or get_correlation_id()

    # Get user context from JWT token
    user_context = _user_context or get_user_context({"jwt_token": jwt_token})
    user_id = user_context["user_id"]

    # Parse due_date if provided as string
    parsed_due_date = None
    if due_date:
        try:
            if isinstance(due_date, str):
                # Handle both date and datetime formats
                if 'T' in due_date:
                    # Full datetime format
                    parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                else:
                    # Date only format - set to end of day
                    parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d")
                    parsed_due_date = parsed_due_date.replace(hour=23, minute=59, second=59)
            elif isinstance(due_date, datetime):
                parsed_due_date = due_date
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Invalid due_date format: {due_date}. Expected ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                field="due_date"
            )

    try:
        # Create task using FastAPI backend
        async with with_fastapi_client() as fastapi_client:
            task = await fastapi_client.create_task(
                user_id=user_id,
                jwt_token=jwt_token,
                title=title,
                description=description,
                priority=priority or "medium",
                due_date=parsed_due_date.isoformat() if parsed_due_date else None
            )

        # Format response for MCP
        response_data = {
            "success": True,
            "task_id": task["id"],
            "title": task.get("title"),
            "description": task.get("description"),
            "priority": task.get("priority"),
            "due_date": task.get("due_date"),
            "is_completed": task.get("is_completed", False),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at"),
            "message": f"Task '{task.get('title')}' created successfully with ID {task.get('id')}"
        }

        # Return structured response for MCP
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"✅ Task created successfully!\n\n"
                         f"**Title:** {response_data['title']}\n"
                         f"**ID:** {response_data['task_id']}\n"
                         f"**Priority:** {response_data['priority']}\n"
                         f"**Due Date:** {response_data['due_date'] or 'None'}\n"
                         f"**Is Completed:** {response_data['is_completed']}\n\n"
                         f"Task has been added to your todo list."
                )
            ],
            "data": response_data
        }

    except ValidationError as e:
        # Return structured error for MCP
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"❌ Validation Error: {e.message}"
                )
            ],
            "data": {
                "success": False,
                "error": "validation_error",
                "message": e.message,
                "field": getattr(e, 'field', None)
            }
        }

    except DatabaseError as e:
        # Return structured error for MCP
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"❌ Database Error: Unable to create task. Please try again later."
                )
            ],
            "data": {
                "success": False,
                "error": "database_error",
                "message": "Database operation failed"
            }
        }


# Register tools with MCP
def register_task_tools(mcp_server: FastMCP) -> None:
    """
    Register all task management tools with the MCP server.

    Args:
        mcp_server: FastMCP server instance
    """
    # The @mcp.tool() decorator automatically registers the tools
    # This function ensures all tools are loaded when the module is imported
    pass


# Export the main tools and service for external access
__all__ = [
    "mcp",
    "task_service",
    "add_task",
    "register_task_tools"
]