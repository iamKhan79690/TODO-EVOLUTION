"""
SQLModel definition for ToolOperation audit logging.

This model tracks all MCP tool operations for auditing and debugging purposes.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, JSON, Column
from sqlalchemy import String, DateTime, Boolean, Integer

class ToolOperation(SQLModel, table=True):
    """
    Audit log for MCP tool operations.

    Tracks all tool executions with user context, request/response data,
    execution metrics, and correlation IDs for tracing.
    """

    __tablename__ = "tool_operation"

    # Primary identification
    id: Optional[int] = Field(default=None, primary_key=True)

    # Operation details
    tool_name: str = Field(max_length=100, description="Name of the MCP tool that was executed")
    operation_type: str = Field(max_length=50, description="Type of operation (CREATE, READ, UPDATE, DELETE)")

    # Authentication context
    user_id: int = Field(description="ID of the user who performed the operation")
    jwt_token_hash: Optional[str] = Field(max_length=255, default=None, description="Hashed JWT token for audit purposes")

    # Request/response data (stored as JSON)
    request_data: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict, description="Input parameters sent to the tool")
    response_data: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict, description="Tool response data")

    # Performance metrics
    execution_time_ms: Optional[int] = Field(default=None, description="Execution time in milliseconds")

    # Status tracking
    success: bool = Field(description="Whether the tool execution was successful")
    error_code: Optional[str] = Field(max_length=100, default=None, description="Error code if operation failed")
    error_message: Optional[str] = Field(max_length=1000, default=None, description="Error message if operation failed")

    # Correlation and timing
    correlation_id: str = Field(max_length=100, description="Unique ID for request tracing across systems")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When the operation started")
    completed_at: Optional[datetime] = Field(default=None, description="When the operation completed")

    # Additional metadata
    ip_address: Optional[str] = Field(max_length=45, default=None, description="Client IP address")
    user_agent: Optional[str] = Field(max_length=500, default=None, description="Client user agent string")

    class Config:
        """SQLModel configuration."""
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"ToolOperation(id={self.id}, tool_name='{self.tool_name}', "
            f"user_id={self.user_id}, success={self.success}, "
            f"correlation_id='{self.correlation_id}')"
        )

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate operation duration in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "operation_type": self.operation_type,
            "user_id": self.user_id,
            "execution_time_ms": self.execution_time_ms,
            "success": self.success,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "correlation_id": self.correlation_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }