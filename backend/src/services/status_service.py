"""
Real-time Status Update Service.

Tracks and manages the status of ongoing operations,
providing real-time updates to clients.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class OperationStatus(Enum):
    """Enumeration for operation statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class StatusService:
    """Service for tracking and managing operation statuses."""

    def __init__(self):
        """Initialize the status service."""
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.operation_history: Dict[str, List[Dict[str, Any]]] = {}  # user_id -> history
        self.cleanup_task = None
        self._start_cleanup_task()

    async def create_operation(
        self,
        operation_id: str,
        user_id: int,
        operation_type: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        conversation_id: Optional[UUID] = None,
        task_id: Optional[int] = None,
        timeout_seconds: int = 300  # 5 minutes default timeout
    ) -> Dict[str, Any]:
        """
        Create a new operation status tracking entry.

        Args:
            operation_id: Unique identifier for the operation
            user_id: User ID performing the operation
            operation_type: Type of operation (add_task, complete_task, etc.)
            title: Optional human-readable title
            description: Optional description
            conversation_id: Optional conversation ID
            task_id: Optional task ID
            timeout_seconds: Timeout in seconds

        Returns:
            Created operation status object
        """
        try:
            operation = {
                "operation_id": operation_id,
                "user_id": user_id,
                "operation_type": operation_type,
                "title": title or operation_type.replace('_', ' ').title(),
                "description": description,
                "status": OperationStatus.PENDING.value,
                "conversation_id": str(conversation_id) if conversation_id else None,
                "task_id": task_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "timeout_at": (datetime.utcnow() + timedelta(seconds=timeout_seconds)).isoformat(),
                "progress": 0,
                "message": "Operation queued",
                "error_message": None,
                "result": None,
                "metadata": {}
            }

            # Store the operation
            self.active_operations[operation_id] = operation

            # Add to user's history
            if str(user_id) not in self.operation_history:
                self.operation_history[str(user_id)] = []
            self.operation_history[str(user_id)].append(operation.copy())

            logger.info("Operation created",
                       operation_id=operation_id,
                       user_id=user_id,
                       operation_type=operation_type)

            return operation

        except Exception as e:
            logger.error("Failed to create operation",
                        operation_id=operation_id,
                        user_id=user_id,
                        error=str(e))
            raise

    async def update_operation_status(
        self,
        operation_id: str,
        status: str,
        message: Optional[str] = None,
        progress: Optional[int] = None,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update the status of an operation.

        Args:
            operation_id: Operation identifier
            status: New status
            message: Optional status message
            progress: Optional progress percentage (0-100)
            result: Optional operation result
            error_message: Optional error message
            metadata: Optional additional metadata

        Returns:
            Updated operation or None if not found
        """
        try:
            if operation_id not in self.active_operations:
                logger.warning("Operation not found for status update",
                            operation_id=operation_id,
                            status=status)
                return None

            operation = self.active_operations[operation_id]

            # Update fields
            operation["status"] = status
            operation["updated_at"] = datetime.utcnow().isoformat()

            if message is not None:
                operation["message"] = message
            if progress is not None:
                operation["progress"] = max(0, min(100, progress))
            if result is not None:
                operation["result"] = result
            if error_message is not None:
                operation["error_message"] = error_message
            if metadata is not None:
                operation["metadata"].update(metadata)

            # Log the update
            logger.info("Operation status updated",
                       operation_id=operation_id,
                       old_status=operation.get("status"),
                       new_status=status,
                       user_id=operation.get("user_id"))

            return operation

        except Exception as e:
            logger.error("Failed to update operation status",
                        operation_id=operation_id,
                        error=str(e))
            return None

    async def complete_operation(
        self,
        operation_id: str,
        result: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Mark an operation as successfully completed.

        Args:
            operation_id: Operation identifier
            result: Optional operation result
            message: Optional success message

        Returns:
            Updated operation or None if not found
        """
        return await self.update_operation_status(
            operation_id=operation_id,
            status=OperationStatus.SUCCESS.value,
            message=message or "Operation completed successfully",
            progress=100,
            result=result
        )

    async def fail_operation(
        self,
        operation_id: str,
        error_message: str,
        result: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Mark an operation as failed.

        Args:
            operation_id: Operation identifier
            error_message: Error message
            result: Optional operation result (may contain error details)

        Returns:
            Updated operation or None if not found
        """
        return await self.update_operation_status(
            operation_id=operation_id,
            status=OperationStatus.FAILED.value,
            message="Operation failed",
            error_message=error_message,
            result=result
        )

    async def start_operation_processing(
        self,
        operation_id: str,
        message: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Mark an operation as currently processing.

        Args:
            operation_id: Operation identifier
            message: Optional processing message

        Returns:
            Updated operation or None if not found
        """
        return await self.update_operation_status(
            operation_id=operation_id,
            status=OperationStatus.PROCESSING.value,
            message=message or "Processing...",
            progress=10
        )

    async def get_operation_status(
        self,
        operation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the current status of an operation.

        Args:
            operation_id: Operation identifier

        Returns:
            Current operation status or None if not found
        """
        return self.active_operations.get(operation_id)

    async def get_user_operations(
        self,
        user_id: int,
        include_completed: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get operations for a specific user.

        Args:
            user_id: User ID
            include_completed: Whether to include completed operations
            limit: Maximum number of operations to return

        Returns:
            List of user operations
        """
        try:
            user_history = self.operation_history.get(str(user_id), [])

            # Filter by completion status
            if not include_completed:
                user_history = [
                    op for op in user_history
                    if op["status"] not in [OperationStatus.SUCCESS.value, OperationStatus.FAILED.value]
                ]

            # Sort by creation time (most recent first) and limit
            user_history.sort(
                key=lambda x: x["created_at"],
                reverse=True
            )

            return user_history[:limit]

        except Exception as e:
            logger.error("Failed to get user operations",
                        user_id=user_id,
                        error=str(e))
            return []

    async def get_conversation_operations(
        self,
        conversation_id: UUID,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get operations related to a specific conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of operations to return

        Returns:
            List of conversation operations
        """
        try:
            conversation_ops = []

            for operation in self.active_operations.values():
                if operation.get("conversation_id") == str(conversation_id):
                    conversation_ops.append(operation.copy())

            # Sort by creation time (most recent first) and limit
            conversation_ops.sort(
                key=lambda x: x["created_at"],
                reverse=True
            )

            return conversation_ops[:limit]

        except Exception as e:
            logger.error("Failed to get conversation operations",
                        conversation_id=conversation_id,
                        error=str(e))
            return []

    async def cancel_operation(
        self,
        operation_id: str,
        reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Cancel an ongoing operation.

        Args:
            operation_id: Operation identifier
            reason: Optional cancellation reason

        Returns:
            Updated operation or None if not found
        """
        return await self.update_operation_status(
            operation_id=operation_id,
            status=OperationStatus.CANCELLED.value,
            message=reason or "Operation cancelled",
            metadata={"cancelled_at": datetime.utcnow().isoformat()}
        )

    async def cleanup_completed_operations(
        self,
        max_age_hours: int = 24
    ) -> int:
        """
        Clean up old completed operations.

        Args:
            max_age_hours: Maximum age in hours for completed operations

        Returns:
            Number of operations cleaned up
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cutoff_str = cutoff_time.isoformat()

            # Find operations to clean up
            operations_to_remove = []
            for operation_id, operation in self.active_operations.items():
                is_complete = operation["status"] in [
                    OperationStatus.SUCCESS.value,
                    OperationStatus.FAILED.value,
                    OperationStatus.CANCELLED.value,
                    OperationStatus.TIMEOUT.value
                ]
                is_old = operation["created_at"] < cutoff_str

                if is_complete and is_old:
                    operations_to_remove.append(operation_id)

            # Remove old operations
            for operation_id in operations_to_remove:
                del self.active_operations[operation_id]

            logger.info("Cleaned up completed operations",
                       count=len(operations_to_remove),
                       max_age_hours=max_age_hours)

            return len(operations_to_remove)

        except Exception as e:
            logger.error("Failed to cleanup operations",
                        max_age_hours=max_age_hours,
                        error=str(e))
            return 0

    def _start_cleanup_task(self):
        """Start the background cleanup task."""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.cleanup_completed_operations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup loop", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def get_service_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.

        Returns:
            Service statistics
        """
        try:
            status_counts = {}
            for operation in self.active_operations.values():
                status = operation["status"]
                status_counts[status] = status_counts.get(status, 0) + 1

            return {
                "active_operations": len(self.active_operations),
                "users_with_history": len(self.operation_history),
                "status_distribution": status_counts,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Failed to get service stats", error=str(e))
            return {"error": str(e)}


# Global instance
status_service: Optional[StatusService] = None


def get_status_service() -> StatusService:
    """Get the global status service instance."""
    global status_service
    if status_service is None:
        status_service = StatusService()
    return status_service


def generate_operation_id(
    operation_type: str,
    user_id: int,
    conversation_id: Optional[UUID] = None
) -> str:
    """
    Generate a unique operation ID.

    Args:
        operation_type: Type of operation
        user_id: User ID
        conversation_id: Optional conversation ID

    Returns:
        Unique operation ID
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid4())[:8]
    conv_suffix = f"_{conversation_id}" if conversation_id else ""
    return f"{operation_type}_{user_id}_{timestamp}_{unique_id}{conv_suffix}"