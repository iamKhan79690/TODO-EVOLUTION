"""
Pydantic schema definitions for API request/response models.

This package contains all Pydantic schemas for validating
API requests and formatting responses.
"""

from .task import (
    Priority,
    RecurrencePattern,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskBase,
)
from .common import (
    HealthResponse,
    ErrorResponse,
    DeleteResponse,
    PaginationInfo,
)

__all__ = [
    # Task-related schemas
    'Priority',
    'RecurrencePattern',
    'TaskCreate',
    'TaskUpdate',
    'TaskResponse',
    'TaskListResponse',
    'TaskBase',
    # Common schemas
    'HealthResponse',
    'ErrorResponse',
    'DeleteResponse',
    'PaginationInfo',
]