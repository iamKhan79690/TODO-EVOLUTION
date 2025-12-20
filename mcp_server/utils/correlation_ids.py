"""
Correlation ID Tracking System for MCP Server

Provides unique request tracking across MCP tool executions for observability
and debugging in distributed environments.
"""

import uuid
import contextvars
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass


# Context variable for correlation IDs
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default='no-correlation-id')


@dataclass
class RequestMetadata:
    """Metadata for tracking requests across the MCP server."""
    correlation_id: str
    request_id: str
    start_time: float
    user_id: Optional[str] = None
    tool_name: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

    @property
    def elapsed_time_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return (time.time() - self.start_time) * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "correlation_id": self.correlation_id,
            "request_id": self.request_id,
            "start_time": self.start_time,
            "user_id": self.user_id,
            "tool_name": self.tool_name,
            "elapsed_time_ms": self.elapsed_time_ms,
            **(self.additional_data or {})
        }


class CorrelationManager:
    """Manages correlation IDs and request metadata."""

    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a unique correlation ID."""
        return str(uuid.uuid4())

    @staticmethod
    def generate_request_id() -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())

    @staticmethod
    def set_correlation_id(correlation_id: Optional[str] = None) -> str:
        """
        Set correlation ID in the current context.

        Args:
            correlation_id: Optional correlation ID. If None, generates one.

        Returns:
            The correlation ID that was set
        """
        if correlation_id is None:
            correlation_id = CorrelationManager.generate_correlation_id()

        correlation_id_var.set(correlation_id)
        return correlation_id

    @staticmethod
    def get_correlation_id() -> str:
        """Get the current correlation ID from context."""
        return correlation_id_var.get()

    @staticmethod
    def get_request_metadata(
        user_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> RequestMetadata:
        """
        Get request metadata for the current context.

        Args:
            user_id: Optional user ID
            tool_name: Optional tool name
            additional_data: Additional metadata

        Returns:
            RequestMetadata object
        """
        return RequestMetadata(
            correlation_id=CorrelationManager.get_correlation_id(),
            request_id=CorrelationManager.generate_request_id(),
            start_time=time.time(),
            user_id=user_id,
            tool_name=tool_name,
            additional_data=additional_data
        )


class CorrelationContext:
    """Context manager for correlation IDs."""

    def __init__(self, correlation_id: Optional[str] = None):
        """
        Initialize correlation context.

        Args:
            correlation_id: Optional correlation ID. If None, generates one.
        """
        self.correlation_id = correlation_id or CorrelationManager.generate_correlation_id()
        self._token = None

    def __enter__(self) -> str:
        """Enter the correlation context."""
        self._token = correlation_id_var.set(self.correlation_id)
        return self.correlation_id

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the correlation context."""
        if self._token:
            correlation_id_var.reset(self._token)


def with_correlation_id(func):
    """
    Decorator to add correlation ID to async function calls.

    Usage:
        @with_correlation_id
        async def my_function(param1, param2, correlation_id=None):
            # correlation_id will be available
            pass
    """
    async def wrapper(*args, **kwargs):
        """Wrapper function that adds correlation ID."""
        correlation_id = kwargs.get('correlation_id') or CorrelationManager.generate_correlation_id()

        with CorrelationContext(correlation_id):
            kwargs['correlation_id'] = correlation_id
            return await func(*args, **kwargs)

    return wrapper


def get_current_context() -> Dict[str, Any]:
    """
    Get current correlation context information.

    Returns:
        Dictionary with correlation context
    """
    return {
        "correlation_id": CorrelationManager.get_correlation_id(),
        "timestamp": time.time()
    }


def extract_correlation_from_headers(headers: Dict[str, str]) -> Optional[str]:
    """
    Extract correlation ID from HTTP headers.

    Args:
        headers: Dictionary of HTTP headers

    Returns:
        Correlation ID if found, None otherwise
    """
    # Check common correlation ID header names
    correlation_headers = [
        'x-correlation-id',
        'x-request-id',
        'correlation-id',
        'request-id'
    ]

    for header in correlation_headers:
        if header.lower() in [h.lower() for h in headers.keys()]:
            for header_name, header_value in headers.items():
                if header_name.lower() == header.lower():
                    return header_value

    return None


def add_correlation_to_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Add correlation ID to HTTP headers.

    Args:
        headers: Dictionary of HTTP headers

    Returns:
        Updated headers with correlation ID
    """
    headers = headers.copy()
    correlation_id = CorrelationManager.get_correlation_id()

    if correlation_id and correlation_id != 'no-correlation-id':
        headers['X-Correlation-ID'] = correlation_id

    return headers


# Convenience functions
def get_correlation_id() -> str:
    """Get current correlation ID."""
    return CorrelationManager.get_correlation_id()


def set_correlation_id(correlation_id: str) -> str:
    """Set current correlation ID."""
    return CorrelationManager.set_correlation_id(correlation_id)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return CorrelationManager.generate_correlation_id()