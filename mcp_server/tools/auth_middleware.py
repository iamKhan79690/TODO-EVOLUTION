"""
JWT Authentication Middleware for MCP Tools

Provides JWT token validation and user context extraction for all MCP tool operations.
Ensures user isolation and proper authentication enforcement.
"""

import sys
from pathlib import Path

# Ensure MCP server root is in path
MCP_ROOT = Path(__file__).parent.parent
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

from typing import Dict, Any, Optional, Callable
from functools import wraps
import structlog

from config.jwt_config import validate_jwt_token
from utils.correlation_ids import with_correlation_id, get_correlation_id
from utils.exceptions import (
    raise_auth_token_missing,
    raise_auth_token_invalid,
    raise_auth_token_expired,
    raise_user_isolation_violation
)

logger = structlog.get_logger(__name__)


class AuthenticationError(Exception):
    """Authentication-related errors."""
    pass


def validate_jwt_token_from_args(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and validate JWT token from function arguments.

    Args:
        args: Function arguments dictionary containing jwt_token

    Returns:
        User context dictionary with user_id, email, name

    Raises:
        AuthenticationError: If JWT token is missing or invalid
    """
    if not args or "jwt_token" not in args:
        raise_auth_token_missing()

    jwt_token = args.get("jwt_token")
    if not jwt_token:
        raise_auth_token_missing()

    try:
        return validate_jwt_token(jwt_token)
    except ValueError as e:
        if "expired" in str(e).lower():
            raise_auth_token_expired()
        else:
            raise_auth_token_invalid()


def extract_user_context(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user context from function arguments.

    Args:
        args: Function arguments dictionary

    Returns:
        User context dictionary

    Raises:
        AuthenticationError: If user context cannot be extracted
    """
    try:
        return validate_jwt_token_from_args(args)
    except AuthenticationError as e:
        correlation_id = get_correlation_id()
        logger.error(
            "User context extraction failed",
            correlation_id=correlation_id,
            error=str(e)
        )
        raise


def require_authentication(func: Callable) -> Callable:
    """
    Decorator to require JWT authentication for MCP tools.

    This decorator validates the JWT token from function arguments,
    extracts user context, and enforces user isolation.

    Usage:
        @require_authentication
        async def some_tool(param1: str, param2: int, jwt_token: str):
            user_context = extract_user_context({"jwt_token": jwt_token})
            # Implementation here
            pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        correlation_id = get_correlation_id()

        try:
            # Extract user context from JWT token
            user_context = extract_user_context(kwargs)

            logger.info(
                "JWT authentication successful",
                correlation_id=correlation_id,
                user_id=user_context.get("user_id"),
                tool_name=func.__name__
            )

            # Add user context to kwargs for use in function
            kwargs["_user_context"] = user_context

            return await func(*args, **kwargs)

        except AuthenticationError as e:
            logger.error(
                "Authentication failed",
                correlation_id=correlation_id,
                error=str(e),
                tool_name=func.__name__
            )
            # Re-raise the authentication error
            raise

    return wrapper


def validate_user_ownership(user_context: Dict[str, Any], task_user_id: int, tool_name: str = None) -> bool:
    """
    Validate that a user has ownership/access to a task.

    Args:
        user_context: User context from JWT token
        task_user_id: User ID of the task to validate
        tool_name: Name of the calling tool for logging

    Returns:
        True if user owns the task, False otherwise

    Raises:
        AuthorizationError: If user does not own the task
    """
    authenticated_user_id = user_context.get("user_id")

    if not authenticated_user_id:
        logger.error(
            "No user_id found in JWT token",
            tool_name=tool_name,
            correlation_id=get_correlation_id()
        )
        raise_user_isolation_violation()

    if isinstance(authenticated_user_id, str):
        try:
            authenticated_user_id = int(authenticated_user_id)
        except ValueError:
            logger.error(
                "Invalid user_id format in JWT token",
                user_id=authenticated_user_id,
                tool_name=tool_name,
                correlation_id=get_correlation_id()
            )
            raise_user_isolation_violation()

    if authenticated_user_id != task_user_id:
        logger.warning(
            "User isolation violation detected",
            authenticated_user_id=authenticated_user_id,
            requested_task_user_id=task_user_id,
            tool_name=tool_name,
            correlation_id=get_correlation_id()
        )
        raise_user_isolation_violation()

    return True


def require_user_ownership(task_user_id_param: str = "task_user_id"):
    """
    Decorator to require user ownership validation for database operations.

    Args:
        task_user_id_param: Parameter name that contains the task's user_id

    Usage:
        @require_user_ownership("task_user_id")
        async def get_task_by_id(task_id: int, task_user_id: int, jwt_token: str):
            # First validate JWT
            user_context = extract_user_context({"jwt_token": jwt_token})

            # Then validate ownership
            validate_user_ownership(user_context, task_user_id, "get_task_by_id")

            # Database operation here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            correlation_id = get_correlation_id()

            try:
                # Extract user context from JWT token
                if "_user_context" not in kwargs:
                    user_context = extract_user_context(kwargs)
                else:
                    user_context = kwargs["_user_context"]

                # Get task user_id from parameters
                task_user_id = kwargs.get(task_user_id_param)
                if task_user_id is None:
                    logger.error(
                        f"Missing required parameter: {task_user_id_param}",
                        correlation_id=correlation_id,
                        tool_name=func.__name__
                    )
                    raise ValueError(f"Missing required parameter: {task_user_user_id_param}")

                # Validate user ownership
                validate_user_ownership(user_context, task_user_id, func.__name__)

                return await func(*args, **kwargs)

            except Exception as e:
                logger.error(
                    f"User ownership validation failed in {func.__name__}",
                    correlation_id=correlation_id,
                    error=str(e)
                )
                raise

        return wrapper
    return decorator


# Convenience functions for common authentication patterns
def get_user_context(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get user context from arguments, handling authentication internally.

    Args:
        args: Function arguments dictionary

    Returns:
        User context dictionary

    Raises:
        AuthenticationError: If authentication fails
    """
    return extract_user_context(args)


def get_user_id(args: Dict[str, Any]) -> int:
    """
    Get user ID from arguments, handling authentication internally.

    Args:
        args: Function arguments dictionary

    Returns:
        User ID as integer

    Raises:
        AuthenticationError: If authentication fails
    """
    user_context = get_user_context(args)
    user_id = user_context.get("user_id")

    if isinstance(user_id, str):
        try:
            return int(user_id)
        except ValueError:
            raise AuthenticationError(f"Invalid user_id format: {user_id}")

    if not isinstance(user_id, int):
        raise AuthenticationError(f"Invalid user_id type: {type(user_id)}")

    return user_id


# Authentication context manager for testing and debugging
class AuthenticationContext:
    """Context manager for testing authentication flows."""

    def __init__(self, jwt_token: str, user_id: int = 123, email: str = "test@example.com"):
        self.jwt_token = jwt_token
        self.user_id = user_id
        self.email = email

    def __enter__(self):
        return {
            "jwt_token": self.jwt_token,
            "_user_context": {
                "user_id": self.user_id,
                "email": self.email,
                "name": "Test User"
            }
        }

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Mock authentication for development/testing
def create_mock_auth_context() -> AuthenticationContext:
    """Create a mock authentication context for testing."""
    return AuthenticationContext(
        jwt_token="mock_jwt_token_for_development",
        user_id=123,
        email="dev@example.com"
    )


# Export convenience functions
__all__ = [
    "require_authentication",
    "require_user_ownership",
    "extract_user_context",
    "validate_user_ownership",
    "get_user_context",
    "get_user_id",
    "AuthenticationContext",
    "create_mock_auth_context"
]