"""
MCP Server Main Entry Point

FastMCP server implementation for Phase III AI Chatbot task management integration.
Provides 5 core tools: add_task, list_tasks, complete_task, delete_task, update_task.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path for cross-module imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

import asyncio
import signal
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastmcp import FastMCP
import structlog

# Local imports
from config.jwt_config import jwt_config, validate_jwt_token
from config.database_config import initialize_database, close_database
from utils.correlation_ids import CorrelationContext, with_correlation_id
from utils.performance import performance_monitor, PerformanceContext
from utils.memory_manager import memory_manager

# Import task tools
from tools.task_tools import (
    task_service,
    register_task_tools,
    add_task as add_task_tool
)


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global MCP server instance
mcp = FastMCP("Task Management Server")


@asynccontextmanager
async def lifespan(app):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("🚀 Starting MCP Server", version="1.0.0")

    try:
        # Initialize database
        logger.info("📊 Initializing database connections...")
        await initialize_database()

        # Start performance monitoring
        logger.info("📊 Starting performance monitoring...")
        performance_monitor.start_monitoring()

        # Start memory management
        logger.info("🧠 Starting memory management...")
        memory_manager.start_monitoring()

        # Register task tools
        logger.info("🛠️ Registering task management tools...")
        register_task_tools(mcp)
        logger.info("✅ Task tools registered successfully")

        logger.info("✅ MCP Server startup complete")

    except Exception as e:
        logger.error("❌ Failed to start MCP Server", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down MCP Server...")

    try:
        # Stop monitoring
        performance_monitor.stop_monitoring()
        memory_manager.stop_monitoring()

        # Close database connections
        await close_database()

        logger.info("✅ MCP Server shutdown complete")

    except Exception as e:
        logger.error("❌ Error during shutdown", error=str(e))


# FastMCP handles lifespan automatically - no manual registration needed


def extract_user_from_jwt(token: str) -> Dict[str, Any]:
    """
    Extract user context from JWT token with error handling.

    Args:
        token: JWT token string

    Returns:
        User context dictionary

    Raises:
        ValueError: If token is invalid
    """
    try:
        user_context = validate_jwt_token(token)
        logger.info("JWT validation successful", user_id=user_context.get("user_id"))
        return user_context
    except Exception as e:
        logger.error("JWT validation failed", error=str(e))
        raise ValueError(f"Authentication failed: {e}")


# MCP tools are automatically registered via @mcp.tool() decorators in tools.task_tools
from tools.task_tools import *  # Import all decorated tools


@mcp.tool()
async def list_tasks(
    jwt_token: str,
    status: str = "pending",
    priority: str = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List tasks for the authenticated user with filtering and pagination.

    Args:
        jwt_token: JWT authentication token
        status: Filter by completion status (completed, pending, all)
        priority: Filter by priority level (low, medium, high, urgent)
        limit: Maximum number of tasks to return (1-100)
        offset: Number of tasks to skip for pagination

    Returns:
        List of tasks matching the filter criteria
    """
    with CorrelationContext():
        logger.info("list_tasks called", status=status, priority=priority)

        async with PerformanceContext("list_tasks"):
            try:
                # Validate JWT and extract user context
                user_context = extract_user_from_jwt(jwt_token)

                # Validate parameters
                if status not in ["completed", "pending", "all"]:
                    raise ValueError("Status must be one of: completed, pending, all")

                if priority and priority not in ["low", "medium", "high", "urgent"]:
                    raise ValueError("Priority must be one of: low, medium, high, urgent")

                if limit < 1 or limit > 100:
                    raise ValueError("Limit must be between 1 and 100")

                if offset < 0:
                    raise ValueError("Offset must be 0 or greater")

                # TODO: Implement actual task retrieval from database
                # This is a placeholder implementation

                tasks_data = []  # Placeholder - would query database

                logger.info("Tasks retrieved successfully", count=len(tasks_data))

                return {
                    "success": True,
                    "data": {
                        "tasks": tasks_data,
                        "total_count": len(tasks_data),
                        "limit": limit,
                        "offset": offset,
                        "has_more": False  # Placeholder
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }

            except ValueError as e:
                logger.warning("Validation error in list_tasks", error=str(e))
                return {
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(e)
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }
            except Exception as e:
                logger.error("Unexpected error in list_tasks", error=str(e))
                return {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred"
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }


# Task Management Tools Implementation
# These tools integrate with the FastAPI backend for task operations

from services.fastapi_client import FastAPIClient, with_fastapi_client
from tools.auth_middleware import get_user_context


@mcp.tool()
async def complete_task(
    task_id: int,
    jwt_token: str
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        task_id: The ID of the task to complete
        jwt_token: JWT authentication token (required)

    Returns:
        Dictionary containing:
        - success: Boolean indicating operation success
        - task: Updated task data
        - message: Success/error message
    """
    with CorrelationContext():
        logger.info("complete_task called", task_id=task_id)

        async with PerformanceContext("complete_task"):
            try:
                # Validate JWT and extract user context
                user_context = extract_user_from_jwt(jwt_token)
                user_id = user_context.get("user_id")

                # Complete task using FastAPI client
                async with with_fastapi_client() as fastapi_client:
                    result = await fastapi_client.complete_task(
                        user_id=user_id,
                        jwt_token=jwt_token,
                        task_id=task_id
                    )

                logger.info("Task completed successfully", task_id=task_id)

                return {
                    "success": True,
                    "data": {
                        "task": result,
                        "task_id": task_id,
                        "is_completed": True
                    },
                    "message": f"Task {task_id} has been marked as completed",
                    "correlation_id": CorrelationContext.get_correlation_id()
                }

            except ValueError as e:
                logger.warning("Validation error in complete_task", error=str(e))
                return {
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(e)
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }
            except Exception as e:
                logger.error("Error completing task", error=str(e), task_id=task_id)
                return {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": f"Failed to complete task: {str(e)}"
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }


@mcp.tool()
async def delete_task(
    task_id: int,
    jwt_token: str
) -> Dict[str, Any]:
    """
    Delete a task.

    Args:
        task_id: The ID of the task to delete
        jwt_token: JWT authentication token (required)

    Returns:
        Dictionary containing:
        - success: Boolean indicating operation success
        - message: Success/error message
    """
    with CorrelationContext():
        logger.info("delete_task called", task_id=task_id)

        async with PerformanceContext("delete_task"):
            try:
                # Validate JWT and extract user context
                user_context = extract_user_from_jwt(jwt_token)
                user_id = user_context.get("user_id")

                # Delete task using FastAPI client
                async with with_fastapi_client() as fastapi_client:
                    result = await fastapi_client.delete_task(
                        user_id=user_id,
                        jwt_token=jwt_token,
                        task_id=task_id
                    )

                logger.info("Task deleted successfully", task_id=task_id)

                return {
                    "success": True,
                    "data": {
                        "task_id": task_id,
                        "deleted": True
                    },
                    "message": f"Task {task_id} has been deleted successfully",
                    "correlation_id": CorrelationContext.get_correlation_id()
                }

            except ValueError as e:
                logger.warning("Validation error in delete_task", error=str(e))
                return {
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(e)
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }
            except Exception as e:
                logger.error("Error deleting task", error=str(e), task_id=task_id)
                return {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": f"Failed to delete task: {str(e)}"
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }


@mcp.tool()
async def update_task(
    task_id: int,
    jwt_token: str,
    title: str = None,
    description: str = None,
    priority: str = None,
    due_date: str = None
) -> Dict[str, Any]:
    """
    Update an existing task.

    Args:
        task_id: The ID of the task to update
        jwt_token: JWT authentication token (required)
        title: New title for the task (optional)
        description: New description for the task (optional)
        priority: New priority level - low, medium, high, urgent (optional)
        due_date: New due date in ISO 8601 format (optional)

    Returns:
        Dictionary containing:
        - success: Boolean indicating operation success
        - task: Updated task data
        - message: Success/error message
    """
    with CorrelationContext():
        logger.info("update_task called", task_id=task_id)

        async with PerformanceContext("update_task"):
            try:
                # Validate JWT and extract user context
                user_context = extract_user_from_jwt(jwt_token)
                user_id = user_context.get("user_id")

                # Validate priority if provided
                if priority and priority not in ["low", "medium", "high", "urgent"]:
                    raise ValueError("Priority must be one of: low, medium, high, urgent")

                # At least one field must be provided for update
                if not any([title, description, priority, due_date]):
                    raise ValueError("At least one field must be provided for update")

                # Update task using FastAPI client
                async with with_fastapi_client() as fastapi_client:
                    result = await fastapi_client.update_task(
                        user_id=user_id,
                        jwt_token=jwt_token,
                        task_id=task_id,
                        title=title,
                        description=description,
                        priority=priority,
                        due_date=due_date
                    )

                logger.info("Task updated successfully", task_id=task_id)

                return {
                    "success": True,
                    "data": {
                        "task": result,
                        "task_id": task_id,
                        "updated_fields": {
                            k: v for k, v in {
                                "title": title,
                                "description": description,
                                "priority": priority,
                                "due_date": due_date
                            }.items() if v is not None
                        }
                    },
                    "message": f"Task {task_id} has been updated successfully",
                    "correlation_id": CorrelationContext.get_correlation_id()
                }

            except ValueError as e:
                logger.warning("Validation error in update_task", error=str(e))
                return {
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": str(e)
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }
            except Exception as e:
                logger.error("Error updating task", error=str(e), task_id=task_id)
                return {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": f"Failed to update task: {str(e)}"
                    },
                    "correlation_id": CorrelationContext.get_correlation_id()
                }


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info("Received signal", signal=signum)
        logger.info("Gracefully shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main entry point for the MCP server."""
    # Setup signal handlers
    setup_signal_handlers()

    # Log startup information
    logger.info("🎯 Starting TODO-Evolution MCP Server")
    logger.info("📝 Version: 1.0.0")
    logger.info("🔧 Environment: %s", os.getenv("ENVIRONMENT", "development"))
    logger.info("🚀 Transport: %s", os.getenv("TRANSPORT", "stdio"))

    try:
        # Run the MCP server
        logger.info("🚀 MCP Server starting...")
        mcp.run()

    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error("💥 Server error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()