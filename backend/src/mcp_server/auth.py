"""
JWT Authentication middleware for MCP server.

This module provides authentication and authorization functions for MCP tools,
leveraging the existing FastAPI authentication system.
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from functools import wraps

from src.auth.better_auth_config import verify_token
from src.database import get_session
from src.models.models import User
from src.auth.token_store import token_blacklist

logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    """Custom exception for authentication failures."""
    pass

class AuthorizationError(Exception):
    """Custom exception for authorization failures."""
    pass

async def extract_jwt_from_header(authorization: str) -> str:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        JWT token string

    Raises:
        AuthenticationError: If token is missing or malformed
    """
    if not authorization:
        raise AuthenticationError("Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid Authorization header format. Expected 'Bearer <token>'")

    token = authorization[7:]  # Remove "Bearer " prefix

    if not token:
        raise AuthenticationError("Empty token in Authorization header")

    return token

async def authenticate_user(jwt_token: str) -> User:
    """
    Authenticate user using JWT token.

    Args:
        jwt_token: JWT token to validate

    Returns:
        User object if authentication successful

    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    try:
        # Verify token and get user ID
        token_data = verify_token(jwt_token)
        user_id = int(token_data.sub)

        # Check if token is blacklisted
        if await token_blacklist.is_blacklisted(jwt_token):
            raise AuthenticationError("Token is blacklisted")

        # Get user from database
        async with get_session() as session:
            user = await session.get(User, user_id)
            if not user:
                raise AuthenticationError("User not found")

            if not user.is_active:
                raise AuthenticationError("User account is inactive")

            return user

    except ValueError as e:
        raise AuthenticationError(f"Invalid token format: {str(e)}")
    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        logger.error(f"Authentication error: {str(e)}")
        raise AuthenticationError("Authentication failed")

def require_authentication(func):
    """
    Decorator to require authentication for MCP tools.

    This decorator extracts JWT token from tool parameters and authenticates
    the user before calling the tool function.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract JWT token from kwargs or use parameter named jwt_token
        jwt_token = kwargs.pop('jwt_token', None)

        if not jwt_token:
            # Try to get from other common parameter names
            for param_name in ['token', 'auth_token', 'access_token']:
                if param_name in kwargs:
                    jwt_token = kwargs.pop(param_name)
                    break

        if not jwt_token:
            raise AuthenticationError("JWT token required. Pass as 'jwt_token' parameter.")

        # Authenticate user
        user = await authenticate_user(jwt_token)

        # Add user to kwargs for the tool function
        kwargs['current_user'] = user

        # Call the original function
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Tool execution error for user {user.id}: {str(e)}")
            raise

    return wrapper

async def check_user_owns_task(user_id: int, task_id: int) -> bool:
    """
    Check if user owns the specified task.

    Args:
        user_id: User ID
        task_id: Task ID

    Returns:
        True if user owns the task, False otherwise
    """
    try:
        async with get_session() as session:
            # Query to check if task belongs to user
            from sqlmodel import select
            from src.models.models import Task

            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id,
                Task.is_deleted == False
            )

            result = await session.exec(statement)
            task = result.first()

            return task is not None

    except Exception as e:
        logger.error(f"Error checking task ownership: {str(e)}")
        return False

def require_task_ownership(func):
    """
    Decorator to require task ownership for MCP tools.

    This decorator should be used after @require_authentication and
    expects task_id to be in the function parameters.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get current user from kwargs (set by @require_authentication)
        current_user = kwargs.get('current_user')
        if not current_user:
            raise AuthorizationError("User not authenticated")

        # Get task_id from kwargs
        task_id = kwargs.get('task_id')
        if task_id is None:
            raise AuthorizationError("task_id parameter required")

        # Check ownership
        if not await check_user_owns_task(current_user.id, task_id):
            raise AuthorizationError("Access denied: You don't own this task")

        # Call the original function
        return await func(*args, **kwargs)

    return wrapper

def log_mcp_operation(tool_name: str, user_id: int, success: bool, error_message: str = None):
    """
    Log MCP tool operations for audit purposes.

    Args:
        tool_name: Name of the MCP tool
        user_id: ID of the user who called the tool
        success: Whether the operation was successful
        error_message: Error message if operation failed
    """
    if success:
        logger.info(f"MCP Tool '{tool_name}' executed successfully by user {user_id}")
    else:
        logger.error(f"MCP Tool '{tool_name}' failed for user {user_id}: {error_message}")

# Utility functions for tool developers
def create_error_response(error_code: str, message: str) -> Dict[str, Any]:
    """
    Create standardized error response for MCP tools.

    Args:
        error_code: Error code (e.g., "AUTHENTICATION_REQUIRED", "TASK_NOT_FOUND")
        message: Human-readable error message

    Returns:
        Standardized error response dictionary
    """
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": message
        }
    }

def create_success_response(data: Any) -> Dict[str, Any]:
    """
    Create standardized success response for MCP tools.

    Args:
        data: Response data

    Returns:
        Standardized success response dictionary
    """
    return {
        "success": True,
        "data": data
    }