"""
Custom Exceptions and Error Handling for MCP Server

Provides structured error handling with proper error codes, correlation IDs,
and user-friendly messages for production debugging.
"""

import sys
from pathlib import Path

# Ensure MCP server root is in path
MCP_ROOT = Path(__file__).parent.parent
if str(MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(MCP_ROOT))

import traceback
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from utils.correlation_ids import get_correlation_id


class ErrorCode(Enum):
    """Standardized error codes for MCP server."""

    # Authentication & Authorization
    AUTH_TOKEN_MISSING = "AUTH_TOKEN_MISSING"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_USER_NOT_FOUND = "AUTH_USER_NOT_FOUND"
    USER_ISOLATION_VIOLATION = "USER_ISOLATION_VIOLATION"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    TITLE_TOO_SHORT = "TITLE_TOO_SHORT"
    TITLE_TOO_LONG = "TITLE_TOO_LONG"
    DESCRIPTION_TOO_LONG = "DESCRIPTION_TOO_LONG"
    INVALID_PRIORITY = "INVALID_PRIORITY"
    INVALID_DUE_DATE = "INVALID_DUE_DATE"
    INVALID_STATUS = "INVALID_STATUS"
    INVALID_LIMIT = "INVALID_LIMIT"
    INVALID_OFFSET = "INVALID_OFFSET"
    INVALID_TASK_ID = "INVALID_TASK_ID"

    # Resource Not Found
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_ALREADY_COMPLETED = "TASK_ALREADY_COMPLETED"
    TASK_ALREADY_DELETED = "TASK_ALREADY_DELETED"
    NO_TASKS_FOUND = "NO_TASKS_FOUND"

    # Database
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_CONSTRAINT_ERROR = "DATABASE_CONSTRAINT_ERROR"
    DATABASE_TIMEOUT = "DATABASE_TIMEOUT"

    # System
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"

    # MCP Specific
    MCP_PROTOCOL_ERROR = "MCP_PROTOCOL_ERROR"
    TOOL_EXECUTION_ERROR = "TOOL_EXECUTION_ERROR"
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    INVALID_TOOL_PARAMETERS = "INVALID_TOOL_PARAMETERS"


@dataclass
class ErrorDetail:
    """Detailed error information for debugging."""
    field: Optional[str] = None
    reason: Optional[str] = None
    value: Optional[Any] = None
    context: Optional[Dict[str, Any]] = None


class MCPException(Exception):
    """
    Base exception for MCP server errors.

    Provides structured error information with correlation IDs for debugging.
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[List[ErrorDetail]] = None,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or []
        self.context = context or {}
        self.correlation_id = correlation_id or get_correlation_id()
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "success": False,
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": [
                    {
                        "field": d.field,
                        "reason": d.reason,
                        "value": d.value,
                        "context": d.context
                    }
                    for d in self.details
                ] if self.details else None
            },
            "correlation_id": self.correlation_id
        }

    def to_log_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "status_code": self.status_code,
            "details": [d.__dict__ for d in self.details],
            "context": self.context,
            "correlation_id": self.correlation_id,
            "cause": str(self.cause) if self.cause else None,
            "traceback": traceback.format_exc()
        }


# Authentication and Authorization Errors

class AuthenticationError(MCPException):
    """Base class for authentication errors."""

    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=401,
            **kwargs
        )


class AuthorizationError(MCPException):
    """Base class for authorization errors."""

    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=403,
            **kwargs
        )


# Validation Errors

class ValidationError(MCPException):
    """Base class for validation errors."""

    def __init__(self, message: str, field: str = None, **kwargs):
        details = kwargs.pop("details", None)
        if not details and field:
            details = [ErrorDetail(field=field, reason="Validation failed")]

        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details,
            **kwargs
        )


class TaskNotFoundError(MCPException):
    """Raised when a task is not found."""

    def __init__(self, task_id: Any, **kwargs):
        super().__init__(
            message=f"Task with ID {task_id} not found",
            error_code=ErrorCode.TASK_NOT_FOUND,
            status_code=404,
            details=[ErrorDetail(value=task_id, reason="Task does not exist")],
            **kwargs
        )


class TaskAlreadyCompletedError(MCPException):
    """Raised when trying to complete an already completed task."""

    def __init__(self, task_id: Any, **kwargs):
        super().__init__(
            message=f"Task {task_id} is already marked as completed",
            error_code=ErrorCode.TASK_ALREADY_COMPLETED,
            status_code=409,
            details=[ErrorDetail(value=task_id, reason="Task already completed")],
            **kwargs
        )


# Database Errors

class DatabaseError(MCPException):
    """Base class for database errors."""

    def __init__(self, message: str, error_code: ErrorCode, **kwargs):
        status_code = kwargs.pop("status_code", 500)
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            **kwargs
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, original_error: Exception = None, **kwargs):
        super().__init__(
            message="Database connection failed",
            error_code=ErrorCode.DATABASE_CONNECTION_ERROR,
            status_code=503,
            cause=original_error,
            **kwargs
        )


class DatabaseTimeoutError(DatabaseError):
    """Raised when database operation times out."""

    def __init__(self, operation: str, timeout_seconds: int, **kwargs):
        super().__init__(
            message=f"Database operation '{operation}' timed out after {timeout_seconds} seconds",
            error_code=ErrorCode.DATABASE_TIMEOUT,
            status_code=504,
            context={"operation": operation, "timeout_seconds": timeout_seconds},
            **kwargs
        )


# System Errors

class InternalServerError(MCPException):
    """Raised for unexpected internal server errors."""

    def __init__(self, message: str, original_error: Exception = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=500,
            cause=original_error,
            **kwargs
        )


class ServiceUnavailableError(MCPException):
    """Raised when the service is temporarily unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable", **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            status_code=503,
            **kwargs
        )


class MemoryLimitExceededError(MCPException):
    """Raised when memory usage exceeds limits."""

    def __init__(self, current_mb: float, limit_mb: float, **kwargs):
        super().__init__(
            message=f"Memory limit exceeded: {current_mb:.1f}MB > {limit_mb}MB",
            error_code=ErrorCode.MEMORY_LIMIT_EXCEEDED,
            status_code=503,
            context={"current_mb": current_mb, "limit_mb": limit_mb},
            **kwargs
        )


# MCP Specific Errors

class MCPProtocolError(MCPException):
    """Raised for MCP protocol violations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=f"MCP protocol error: {message}",
            error_code=ErrorCode.MCP_PROTOCOL_ERROR,
            status_code=400,
            **kwargs
        )


class ToolExecutionError(MCPException):
    """Raised when MCP tool execution fails."""

    def __init__(self, tool_name: str, error_message: str, **kwargs):
        super().__init__(
            message=f"Tool '{tool_name}' execution failed: {error_message}",
            error_code=ErrorCode.TOOL_EXECUTION_ERROR,
            status_code=500,
            context={"tool_name": tool_name},
            **kwargs
        )


class ToolNotFoundError(MCPException):
    """Raised when a requested MCP tool is not found."""

    def __init__(self, tool_name: str, **kwargs):
        super().__init__(
            message=f"Tool '{tool_name}' not found",
            error_code=ErrorCode.TOOL_NOT_FOUND,
            status_code=404,
            context={"tool_name": tool_name},
            **kwargs
        )


# Error Handling Utilities

def handle_exception(
    exception: Exception,
    operation: str = "unknown",
    default_message: str = "An unexpected error occurred"
) -> MCPException:
    """
    Convert any exception to an MCPException with proper context.

    Args:
        exception: The original exception
        operation: Description of the operation that failed
        default_message: Default error message if exception type is unknown

    Returns:
        MCPException with proper error information
    """
    correlation_id = get_correlation_id()

    # If it's already an MCPException, just add context
    if isinstance(exception, MCPException):
        if not exception.context:
            exception.context = {"operation": operation}
        else:
            exception.context["operation"] = operation
        return exception

    # Handle common exception types
    if isinstance(exception, ValueError):
        return ValidationError(
            message=str(exception),
            context={"operation": operation}
        )
    elif isinstance(exception, KeyError):
        return ValidationError(
            message=f"Missing required field: {str(exception)}",
            context={"operation": operation}
        )
    elif isinstance(exception, ConnectionError):
        return DatabaseConnectionError(
            original_error=exception,
            context={"operation": operation}
        )
    elif isinstance(exception, TimeoutError):
        return DatabaseTimeoutError(
            operation=operation,
            timeout_seconds=30,  # Default timeout
            original_error=exception,
            context={"operation": operation}
        )
    else:
        return InternalServerError(
            message=default_message,
            original_error=exception,
            context={"operation": operation, "original_type": type(exception).__name__}
        )


def create_validation_error(
    field: str,
    value: Any,
    reason: str,
    message: str = None
) -> ValidationError:
    """
    Create a validation error with detailed information.

    Args:
        field: Field name that failed validation
        value: The invalid value
        reason: Reason for validation failure
        message: Optional custom error message

    Returns:
        ValidationError with detailed information
    """
    return ValidationError(
        message=message or f"Validation failed for field '{field}'",
        details=[ErrorDetail(
            field=field,
            reason=reason,
            value=value
        )]
    )


def log_exception(exception: MCPException, logger=None):
    """
    Log an MCP exception with full context.

    Args:
        exception: The MCP exception to log
        logger: Optional logger instance
    """
    if not logger:
        from .exceptions import main_logger
        logger = main_logger

    logger.error(
        "MCP Exception occurred",
        **exception.to_log_dict()
    )


# Convenience functions for common errors

def raise_auth_token_missing():
    """Raise exception for missing authentication token."""
    raise AuthenticationError(
        message="JWT authentication token is required",
        error_code=ErrorCode.AUTH_TOKEN_MISSING
    )


def raise_auth_token_invalid():
    """Raise exception for invalid authentication token."""
    raise AuthenticationError(
        message="Invalid JWT authentication token",
        error_code=ErrorCode.AUTH_TOKEN_INVALID
    )


def raise_auth_token_expired():
    """Raise exception for expired authentication token."""
    raise AuthenticationError(
        message="JWT authentication token has expired",
        error_code=ErrorCode.AUTH_TOKEN_EXPIRED
    )


def raise_task_not_found(task_id: Any):
    """Raise exception for task not found."""
    raise TaskNotFoundError(task_id=task_id)


def raise_user_isolation_violation():
    """Raise exception for user isolation violation."""
    raise AuthorizationError(
        message="Access denied: task does not belong to authenticated user",
        error_code=ErrorCode.USER_ISOLATION_VIOLATION
    )


def raise_validation_error(message: str, field: str = None, value: Any = None, reason: str = None):
    """Raise a validation error."""
    details = []
    if field and reason:
        details.append(ErrorDetail(field=field, reason=reason, value=value))

    raise ValidationError(
        message=message,
        details=details if details else None
    )