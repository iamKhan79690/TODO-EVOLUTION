"""
MCP Tools for TODO-Evolution application.

This module provides MCP (Model Context Protocol) tools for task management
operations that can be used by AI agents.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .auth import require_authentication, require_task_ownership, AuthenticationError, AuthorizationError
from .services import TaskService
from ..models.models import Priority, TaskStatus

logger = logging.getLogger(__name__)

# Global MCP server instance (will be injected by main.py)
_mcp_instance = None

def register_tools(mcp):
    """Register all tools with the MCP server instance."""
    global _mcp_instance
    _mcp_instance = mcp

    # Register all tools
    mcp.tool()(add_task)
    mcp.tool()(list_tasks)
    mcp.tool()(complete_task)
    mcp.tool()(update_task)
    mcp.tool()(delete_task)
    mcp.tool()(get_task_statistics)

    logger.info("✅ MCP tools registered successfully")

# Tool functions will be registered by register_tools() function
async def add_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None,
    jwt_token: str = None
) -> Dict[str, Any]:
    """
    Add a new task to the user's todo list.

    Args:
        title: Task title (required)
        description: Optional task description
        priority: Task priority (low, medium, high)
        due_date: Optional due date in ISO format
        jwt_token: JWT authentication token

    Returns:
        Dict containing success status and task data or error message
    """
    try:
        # Validate priority
        try:
            priority_enum = Priority(priority.lower())
        except ValueError:
            priority_enum = Priority.MEDIUM

        # Parse due date if provided
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid due date format: {due_date}")

        # Create task using TaskService
        task = await TaskService.create_task(
            user_id=current_user.id,  # Will be set by auth decorator
            title=title,
            description=description,
            priority=priority_enum,
            due_date=due_date_obj
        )

        logger.info(f"Task created successfully: {task.id} - {task.title}")

        return {
            "success": True,
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "status": task.status.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "message": f"Task '{task.title}' has been created successfully."
            }
        }

    except AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "AUTHENTICATION_FAILED",
                "message": "Authentication failed. Please provide a valid JWT token."
            }
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(e)
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error in add_task: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while creating the task."
            }
        }

# MCP tools are registered via register_tools() function
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    jwt_token: str = None
) -> Dict[str, Any]:
    """
    List tasks for the authenticated user.

    Args:
        status: Optional status filter (pending, in_progress, completed, cancelled, all)
        limit: Maximum number of tasks to return (default: 20)
        offset: Number of tasks to skip (default: 0)
        jwt_token: JWT authentication token

    Returns:
        Dict containing success status and list of tasks or error message
    """
    try:
        # Get tasks using TaskService
        tasks = await TaskService.get_user_tasks(
            user_id=current_user.id,  # Will be set by auth decorator
            status=status,
            limit=limit,
            offset=offset
        )

        # Format tasks for response
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "status": task.status.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            })

        logger.info(f"Retrieved {len(task_list)} tasks for user")

        return {
            "success": True,
            "data": {
                "tasks": task_list,
                "count": len(task_list),
                "limit": limit,
                "offset": offset,
                "message": f"Found {len(task_list)} tasks."
            }
        }

    except AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "AUTHENTICATION_FAILED",
                "message": "Authentication failed. Please provide a valid JWT token."
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error in list_tasks: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving tasks."
            }
        }

# MCP tools are registered via register_tools() function
async def complete_task(
    task_id: int,
    jwt_token: str = None
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        task_id: ID of the task to complete
        jwt_token: JWT authentication token

    Returns:
        Dict containing success status and task data or error message
    """
    try:
        # Complete task using TaskService
        task = await TaskService.complete_task(
            task_id=task_id,
            user_id=current_user.id  # Will be set by auth decorator
        )

        if not task:
            return {
                "success": False,
                "error": {
                    "code": "TASK_NOT_FOUND",
                    "message": f"Task with ID {task_id} not found."
                }
            }

        logger.info(f"Task completed successfully: {task.id} - {task.title}")

        return {
            "success": True,
            "data": {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "message": f"Task '{task.title}' has been marked as completed."
            }
        }

    except AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "AUTHENTICATION_FAILED",
                "message": "Authentication failed. Please provide a valid JWT token."
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error in complete_task: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while completing the task."
            }
        }

# MCP tools are registered via register_tools() function
async def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    jwt_token: str = None
) -> Dict[str, Any]:
    """
    Update an existing task.

    Args:
        task_id: ID of the task to update
        title: Optional new title
        description: Optional new description
        priority: Optional new priority (low, medium, high)
        due_date: Optional new due date in ISO format
        jwt_token: JWT authentication token

    Returns:
        Dict containing success status and updated task data or error message
    """
    try:
        # Build updates dictionary
        updates = {}

        if title is not None:
            updates['title'] = title

        if description is not None:
            updates['description'] = description

        if priority is not None:
            try:
                updates['priority'] = Priority(priority.lower())
            except ValueError:
                logger.warning(f"Invalid priority: {priority}, using medium")
                updates['priority'] = Priority.MEDIUM

        if due_date is not None:
            if due_date == "":
                updates['due_date'] = None
            else:
                try:
                    updates['due_date'] = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Invalid due date format: {due_date}")
                    return {
                        "success": False,
                        "error": {
                            "code": "INVALID_DATE_FORMAT",
                            "message": "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)."
                        }
                    }

        if not updates:
            return {
                "success": False,
                "error": {
                    "code": "NO_UPDATES",
                    "message": "No valid updates provided."
                }
            }

        # Update task using TaskService
        task = await TaskService.update_task(
            task_id=task_id,
            user_id=current_user.id,  # Will be set by auth decorator
            updates=updates
        )

        if not task:
            return {
                "success": False,
                "error": {
                    "code": "TASK_NOT_FOUND",
                    "message": f"Task with ID {task_id} not found."
                }
            }

        logger.info(f"Task updated successfully: {task.id} - {task.title}")

        return {
            "success": True,
            "data": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "status": task.status.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "message": f"Task '{task.title}' has been updated successfully."
            }
        }

    except AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "AUTHENTICATION_FAILED",
                "message": "Authentication failed. Please provide a valid JWT token."
            }
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(e)
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error in update_task: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while updating the task."
            }
        }

# MCP tools are registered via register_tools() function
async def delete_task(
    task_id: int,
    jwt_token: str = None
) -> Dict[str, Any]:
    """
    Delete a task (soft delete).

    Args:
        task_id: ID of the task to delete
        jwt_token: JWT authentication token

    Returns:
        Dict containing success status or error message
    """
    try:
        # Delete task using TaskService
        success = await TaskService.delete_task(
            task_id=task_id,
            user_id=current_user.id  # Will be set by auth decorator
        )

        if not success:
            return {
                "success": False,
                "error": {
                    "code": "TASK_NOT_FOUND",
                    "message": f"Task with ID {task_id} not found."
                }
            }

        logger.info(f"Task deleted successfully: {task_id}")

        return {
            "success": True,
            "data": {
                "id": task_id,
                "message": f"Task with ID {task_id} has been deleted successfully."
            }
        }

    except AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "AUTHENTICATION_FAILED",
                "message": "Authentication failed. Please provide a valid JWT token."
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error in delete_task: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while deleting the task."
            }
        }

# MCP tools are registered via register_tools() function
async def get_task_statistics(
    jwt_token: str = None
) -> Dict[str, Any]:
    """
    Get task statistics for the authenticated user.

    Args:
        jwt_token: JWT authentication token

    Returns:
        Dict containing success status and task statistics or error message
    """
    try:
        # Get statistics using TaskService
        stats = await TaskService.get_task_statistics(
            user_id=current_user.id  # Will be set by auth decorator
        )

        logger.info(f"Retrieved task statistics for user")

        return {
            "success": True,
            "data": {
                "statistics": stats,
                "total_tasks": sum(stats.values()),
                "message": f"Found {sum(stats.values())} total tasks."
            }
        }

    except AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "AUTHENTICATION_FAILED",
                "message": "Authentication failed. Please provide a valid JWT token."
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_task_statistics: {str(e)}")
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred while retrieving task statistics."
            }
        }

# Apply authentication decorators to all tools
for tool_name, tool_func in list(locals().items()):
    if callable(tool_func) and tool_name not in ['register_tools']:
        if hasattr(tool_func, '__name__') and tool_func.__name__ not in ['set_mcp_instance']:
            # Skip if already decorated or is a utility function
            if tool_name.startswith('_') or tool_name in ['register_tools']:
                continue

            # Apply authentication and logging
            tool_func = require_authentication(tool_func)

            # Apply task ownership for task-specific operations
            if 'task' in tool_name and task_name != 'add_task' and tool_name != 'list_tasks':
                tool_func = require_task_ownership(tool_func)

            # Update the function in locals
            locals()[tool_name] = tool_func