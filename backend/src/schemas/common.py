"""Common schemas for API responses."""

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: datetime
    version: str
    database: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: dict
    timestamp: datetime
    path: str


class DeleteResponse(BaseModel):
    """Delete operation response schema."""
    message: str
    task_id: int


class PaginationInfo(BaseModel):
    """Pagination information schema."""
    skip: int
    limit: int
    has_more: bool
    total: Optional[int] = None