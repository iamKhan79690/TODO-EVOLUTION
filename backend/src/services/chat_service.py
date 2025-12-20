"""
Conversation Management Service for AI Chat Assistant.

Handles conversation lifecycle, message management, and task operations
triggered by AI commands.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from ..models import (
    Conversation, Message, Task, TaskOperationLog,
    MessageRole, MessageType, OperationStatus
)
from ..services.ai_service import TaskCommand
from ..services.context_service import ContextService
from ..models.models import Priority, RecurrencePattern
import structlog

logger = structlog.get_logger(__name__)


class ChatService:
    """Service for managing chat conversations and AI-powered task operations."""

    def __init__(self, db: Session, user_id: int):
        """
        Initialize the chat service.

        Args:
            db: Database session
            user_id: ID of the authenticated user
        """
        self.db = db
        self.user_id = user_id
        self.context_service = ContextService(db, user_id)

    async def create_conversation(self, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation for the user.

        Args:
            title: Optional title for the conversation

        Returns:
            Created conversation object
        """
        conversation = Conversation(
            user_id=self.user_id,
            title=title or "New Conversation",
            is_active=True,
            messages_count=0
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        logger.info("Conversation created",
                   user_id=self.user_id,
                   conversation_id=conversation.id,
                   title=conversation.title)

        return conversation

    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """
        Get a conversation by ID, ensuring it belongs to the current user.

        Args:
            conversation_id: The conversation ID to retrieve

        Returns:
            Conversation object or None if not found
        """
        return self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == self.user_id
            )
        ).first()

    async def get_user_conversations(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """
        Get all conversations for the current user.

        Args:
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversation objects
        """
        return self.db.query(Conversation).filter(
            Conversation.user_id == self.user_id
        ).order_by(desc(Conversation.updated_at)).offset(offset).limit(limit).all()

    async def create_message(
        self,
        conversation_id: UUID,
        content: str,
        role: str,
        message_type: str = "text",
        operation_type: Optional[str] = None,
        operation_result: Optional[Dict[str, Any]] = None,
        error_details: Optional[str] = None
    ) -> Message:
        """
        Create a new message in a conversation.

        Args:
            conversation_id: The conversation ID
            content: Message content
            role: Message role (user/assistant/system)
            message_type: Type of message
            operation_type: Type of AI operation performed
            operation_result: Result of the operation
            error_details: Error details if operation failed

        Returns:
            Created message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=json.dumps(content) if isinstance(content, (dict, list)) else content,
            timestamp=datetime.utcnow(),
            message_type=message_type,
            operation_status=OperationStatus.DELIVERED,
            operation_type=operation_type,
            operation_result=json.dumps(operation_result) if operation_result else None,
            error_details=json.dumps(error_details) if error_details else None
        )

        self.db.add(message)

        # Update conversation metadata
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.messages_count += 1
            conversation.last_message_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)

        logger.info("Message created",
                   user_id=self.user_id,
                   conversation_id=conversation_id,
                   message_id=message.id,
                   role=role)

        return message

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """
        Get messages from a conversation.

        Args:
            conversation_id: The conversation ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of message objects
        """
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp).offset(offset).limit(limit).all()

    # Task Operations triggered by AI commands

    async def create_task_from_command(self, command: TaskCommand) -> Dict[str, Any]:
        """
        Create a task from an AI command.

        Args:
            command: The parsed AI command

        Returns:
            Created task data
        """
        try:
            # Map priority from command
            priority_map = {
                'URGENT': Priority.URGENT,
                'HIGH': Priority.HIGH,
                'MEDIUM': Priority.MEDIUM,
                'LOW': Priority.LOW
            }
            priority = priority_map.get(command.task_priority, Priority.MEDIUM)

            task = Task(
                title=command.task_title,
                description=command.task_description,
                priority=priority,
                due_date=command.due_date,
                user_id=self.user_id,
                is_completed=False
            )

            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)

            # Log the operation
            await self._log_task_operation(
                command=command,
                task_id=task.id,
                status="success",
                operation_data={
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                }
            )

            # Store context for future suggestions
            await self.context_service.store_task_context(
                conversation_id=command.conversation_id if command.conversation_id else task.id,
                task_id=task.id,
                operation_type="add_task",
                task_data={
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat()
                }
            )

            logger.info("Task created from AI command",
                       user_id=self.user_id,
                       task_id=task.id,
                       title=task.title)

            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "is_completed": task.is_completed,
                "created_at": task.created_at.isoformat()
            }

        except Exception as e:
            await self._log_task_operation(
                command=command,
                status="failed",
                error_message=str(e)
            )
            logger.error("Failed to create task from AI command",
                       user_id=self.user_id,
                       command=command.command_type,
                       error=str(e))
            raise

    async def complete_task_from_command(self, command: TaskCommand) -> Dict[str, Any]:
        """
        Complete a task from an AI command.

        Args:
            command: The parsed AI command

        Returns:
            Updated task data
        """
        try:
            # Find the task by title
            task = self.db.query(Task).filter(
                and_(
                    Task.user_id == self.user_id,
                    Task.title.ilike(f"%{command.task_title}%"),
                    Task.is_completed == False
                )
            ).first()

            if not task:
                raise ValueError(f"No active task found matching: {command.task_title}")

            task.is_completed = True
            task.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(task)

            # Log the operation
            await self._log_task_operation(
                command=command,
                task_id=task.id,
                status="success",
                operation_data={
                    "task_title": task.title,
                    "completed_at": task.updated_at.isoformat()
                }
            )

            logger.info("Task completed from AI command",
                       user_id=self.user_id,
                       task_id=task.id,
                       title=task.title)

            return {
                "id": task.id,
                "title": task.title,
                "is_completed": task.is_completed,
                "completed_at": task.updated_at.isoformat()
            }

        except Exception as e:
            await self._log_task_operation(
                command=command,
                status="failed",
                error_message=str(e)
            )
            logger.error("Failed to complete task from AI command",
                       user_id=self.user_id,
                       command=command.command_type,
                       error=str(e))
            raise

    async def update_task_from_command(self, command: TaskCommand) -> Dict[str, Any]:
        """
        Update a task from an AI command.

        Args:
            command: The parsed AI command

        Returns:
            Updated task data
        """
        try:
            # Find the task by title
            task = self.db.query(Task).filter(
                and_(
                    Task.user_id == self.user_id,
                    Task.title.ilike(f"%{command.task_title}%")
                )
            ).first()

            if not task:
                raise ValueError(f"No task found matching: {command.task_title}")

            # Update task with description
            if command.task_description:
                task.description = command.task_description

            # Update priority if specified
            if command.task_priority:
                priority_map = {
                    'URGENT': Priority.URGENT,
                    'HIGH': Priority.HIGH,
                    'MEDIUM': Priority.MEDIUM,
                    'LOW': Priority.LOW
                }
                task.priority = priority_map.get(command.task_priority, task.priority)

            # Update due date if specified
            if command.due_date:
                task.due_date = command.due_date

            task.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(task)

            # Log the operation
            await self._log_task_operation(
                command=command,
                task_id=task.id,
                status="success",
                operation_data={
                    "task_title": task.title,
                    "updates": {
                        "description": task.description,
                        "priority": task.priority.value,
                        "due_date": task.due_date.isoformat() if task.due_date else None
                    }
                }
            )

            logger.info("Task updated from AI command",
                       user_id=self.user_id,
                       task_id=task.id,
                       title=task.title)

            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "updated_at": task.updated_at.isoformat()
            }

        except Exception as e:
            await self._log_task_operation(
                command=command,
                status="failed",
                error_message=str(e)
            )
            logger.error("Failed to update task from AI command",
                       user_id=self.user_id,
                       command=command.command_type,
                       error=str(e))
            raise

    async def delete_task_from_command(self, command: TaskCommand) -> Dict[str, Any]:
        """
        Delete a task from an AI command.

        Args:
            command: The parsed AI command

        Returns:
            Deleted task data
        """
        try:
            # Find the task by title
            task = self.db.query(Task).filter(
                and_(
                    Task.user_id == self.user_id,
                    Task.title.ilike(f"%{command.task_title}%")
                )
            ).first()

            if not task:
                raise ValueError(f"No task found matching: {command.task_title}")

            # Store task info before deletion
            task_info = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "is_completed": task.is_completed,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }

            # Delete the task
            self.db.delete(task)
            self.db.commit()

            # Log the operation
            await self._log_task_operation(
                command=command,
                task_id=task.id,
                status="success",
                operation_data=task_info
            )

            logger.info("Task deleted from AI command",
                       user_id=self.user_id,
                       task_id=task.id,
                       title=task.title)

            return task_info

        except Exception as e:
            await self._log_task_operation(
                command=command,
                status="failed",
                error_message=str(e)
            )
            logger.error("Failed to delete task from AI command",
                       user_id=self.user_id,
                       command=command.command_type,
                       error=str(e))
            raise

    async def list_tasks_for_user(self) -> Dict[str, Any]:
        """
        List all tasks for the user.

        Returns:
            Task list data
        """
        try:
            tasks = self.db.query(Task).filter(
                Task.user_id == self.user_id
            ).order_by(Task.created_at.desc()).all()

            task_list = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "is_completed": task.is_completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            stats = {
                "total": len(tasks),
                "completed": len([t for t in tasks if t.is_completed]),
                "pending": len([t for t in tasks if not t.is_completed]),
                "by_priority": {
                    "urgent": len([t for t in tasks if t.priority == Priority.URGENT]),
                    "high": len([t for t in tasks if t.priority == Priority.HIGH]),
                    "medium": len([t for t in tasks if t.priority == Priority.MEDIUM]),
                    "low": len([t for t in tasks if t.priority == Priority.LOW])
                }
            }

            return {
                "tasks": task_list,
                "stats": stats,
                "total": len(tasks)
            }

        except Exception as e:
            logger.error("Failed to list tasks",
                       user_id=self.user_id,
                       error=str(e))
            raise

    async def search_tasks(self, query: str) -> Dict[str, Any]:
        """
        Search tasks by query string.

        Args:
            query: Search query

        Returns:
            Matching tasks
        """
        try:
            tasks = self.db.query(Task).filter(
                and_(
                    Task.user_id == self.user_id,
                    or_(
                        Task.title.ilike(f"%{query}%"),
                        Task.description.ilike(f"%{query}%")
                    )
                )
            ).order_by(Task.created_at.desc()).all()

            return {
                "query": query,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority.value,
                        "is_completed": task.is_completed,
                        "due_date": task.due_date.isoformat() if task.due_date else None
                    }
                    for task in tasks
                ],
                "total": len(tasks)
            }

        except Exception as e:
            logger.error("Failed to search tasks",
                       user_id=self.user_id,
                       query=query,
                       error=str(e))
            raise

    async def _log_task_operation(
        self,
        command: TaskCommand,
        task_id: Optional[int] = None,
        status: str = "success",
        operation_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """
        Log a task operation to the audit log.

        Args:
            command: The AI command that triggered the operation
            task_id: ID of the task if applicable
            status: Operation status
            operation_data: Operation input/output data
            error_message: Error message if operation failed
        """
        try:
            operation_log = TaskOperationLog(
                message_id=uuid4(),  # This would be the actual message ID in real implementation
                user_id=self.user_id,
                operation_type=command.command_type,
                task_id=task_id,
                operation_data=json.dumps(operation_data or {}),
                operation_result=json.dumps(operation_data or {}),
                status=status,
                error_message=error_message,
                created_at=datetime.utcnow()
            )

            self.db.add(operation_log)
            self.db.commit()

        except Exception as e:
            logger.error("Failed to log task operation",
                       user_id=self.user_id,
                       operation_type=command.command_type,
                       error=str(e))

    async def get_conversation_context_summary(self, conversation_id: UUID) -> Dict[str, Any]:
        """
        Get a comprehensive summary of conversation context for AI processing.

        Args:
            conversation_id: The conversation ID

        Returns:
            Dictionary containing conversation context and user patterns
        """
        try:
            # Get basic conversation summary
            conversation_summary = await self.context_service.get_conversation_summary(conversation_id)

            # Get task history
            task_history = await self.context_service.get_task_history_context(conversation_id)

            # Get user preferences
            user_preferences = await self.context_service.get_user_preferences(conversation_id)

            # Get recent user tasks for pattern analysis
            recent_tasks = self.db.query(Task).filter(
                Task.user_id == self.user_id
            ).order_by(desc(Task.created_at)).limit(10).all()

            # Analyze user patterns
            active_tasks = len([t for t in recent_tasks if not t.is_completed])
            completed_tasks = len([t for t in recent_tasks if t.is_completed])
            priority_distribution = {}

            for task in recent_tasks:
                if task.priority:
                    priority = task.priority.value
                    priority_distribution[priority] = priority_distribution.get(priority, 0) + 1

            return {
                "conversation_id": str(conversation_id),
                "recent_tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "is_completed": task.is_completed,
                        "priority": task.priority.value if task.priority else None,
                        "due_date": task.due_date.isoformat() if task.due_date else None
                    }
                    for task in recent_tasks
                ],
                "task_history": task_history,
                "user_preferences": user_preferences,
                "user_patterns": {
                    "active_tasks_count": active_tasks,
                    "completed_tasks_count": completed_tasks,
                    "total_tasks_analyzed": len(recent_tasks),
                    "priority_distribution": priority_distribution
                },
                "conversation_stats": conversation_summary.get("context_summary", {}),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Failed to get conversation context summary",
                        conversation_id=conversation_id,
                        user_id=self.user_id,
                        error=str(e))
            return {
                "conversation_id": str(conversation_id),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }