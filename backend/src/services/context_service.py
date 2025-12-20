"""
Conversation Context Management Service.

Handles persistent conversation context, including task history,
user preferences, and conversation state for AI assistance.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..models import ConversationContext, Message, Task
import structlog

logger = structlog.get_logger(__name__)


class ContextService:
    """Service for managing conversation context and user history."""

    def __init__(self, db: Session, user_id: int):
        """
        Initialize the context service.

        Args:
            db: Database session
            user_id: ID of the authenticated user
        """
        self.db = db
        self.user_id = user_id
        self.context_cache = {}  # Simple in-memory cache

    async def get_conversation_context(
        self,
        conversation_id: UUID,
        context_type: Optional[str] = None,
        context_key: Optional[str] = None
    ) -> List[ConversationContext]:
        """
        Get context for a conversation.

        Args:
            conversation_id: The conversation ID
            context_type: Optional type filter
            context_key: Optional key filter

        Returns:
            List of conversation context objects
        """
        try:
            query = self.db.query(ConversationContext).filter(
                and_(
                    ConversationContext.conversation_id == conversation_id,
                    or_(
                        ConversationContext.expires_at.is_(None),
                        ConversationContext.expires_at > datetime.utcnow()
                    )
                )
            )

            if context_type:
                query = query.filter(ConversationContext.context_type == context_type)

            if context_key:
                query = query.filter(ConversationContext.context_key == context_key)

            return query.order_by(desc(ConversationContext.created_at)).all()

        except Exception as e:
            logger.error("Failed to get conversation context",
                        conversation_id=conversation_id,
                        context_type=context_type,
                        context_key=context_key,
                        error=str(e))
            return []

    async def store_context(
        self,
        conversation_id: UUID,
        context_type: str,
        context_key: str,
        context_value: Dict[str, Any],
        expires_at: Optional[datetime] = None
    ) -> ConversationContext:
        """
        Store context for a conversation.

        Args:
            conversation_id: The conversation ID
            context_type: Type of context (e.g., 'task_history', 'user_preferences')
            context_key: Key for the context
            context_value: The context data
            expires_at: Optional expiration time

        Returns:
            Created conversation context object
        """
        try:
            # Check if context already exists and update it
            existing_context = self.db.query(ConversationContext).filter(
                and_(
                    ConversationContext.conversation_id == conversation_id,
                    ConversationContext.context_type == context_type,
                    ConversationContext.context_key == context_key
                )
            ).first()

            if existing_context:
                # Update existing context
                existing_context.context_value = json.dumps(context_value)
                existing_context.expires_at = expires_at
                existing_context.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing_context)
                logger.info("Context updated",
                           conversation_id=conversation_id,
                           context_type=context_type,
                           context_key=context_key)
                return existing_context
            else:
                # Create new context
                context = ConversationContext(
                    conversation_id=conversation_id,
                    context_type=context_type,
                    context_key=context_key,
                    context_value=json.dumps(context_value),
                    expires_at=expires_at,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                self.db.add(context)
                self.db.commit()
                self.db.refresh(context)

                logger.info("Context created",
                           conversation_id=conversation_id,
                           context_type=context_type,
                           context_key=context_key)
                return context

        except Exception as e:
            logger.error("Failed to store context",
                        conversation_id=conversation_id,
                        context_type=context_type,
                        context_key=context_key,
                        error=str(e))
            raise

    async def store_task_context(
        self,
        conversation_id: UUID,
        task_id: int,
        operation_type: str,
        task_data: Dict[str, Any]
    ) -> ConversationContext:
        """
        Store task-related context.

        Args:
            conversation_id: The conversation ID
            task_id: The task ID
            operation_type: Type of operation (add, update, complete, delete)
            task_data: Task data

        Returns:
            Created conversation context object
        """
        context_key = f"task_{task_id}_{operation_type}"
        context_value = {
            "task_id": task_id,
            "operation_type": operation_type,
            "task_data": task_data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Set expiration to 7 days for task context
        expires_at = datetime.utcnow() + timedelta(days=7)

        return await self.store_context(
            conversation_id=conversation_id,
            context_type="task_history",
            context_key=context_key,
            context_value=context_value,
            expires_at=expires_at
        )

    async def get_task_history_context(
        self,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get task history for a conversation.

        Args:
            conversation_id: The conversation ID
            limit: Maximum number of tasks to return

        Returns:
            List of task history entries
        """
        try:
            contexts = await self.get_conversation_context(
                conversation_id=conversation_id,
                context_type="task_history"
            )

            task_history = []
            for context in contexts[:limit]:
                try:
                    context_data = json.loads(context.context_value) if isinstance(context.context_value, str) else context.context_value
                    task_history.append(context_data)
                except (json.JSONDecodeError, TypeError):
                    logger.warning("Invalid context value format",
                                 context_id=context.id)
                    continue

            return task_history

        except Exception as e:
            logger.error("Failed to get task history context",
                        conversation_id=conversation_id,
                        error=str(e))
            return []

    async def store_user_preference(
        self,
        conversation_id: UUID,
        preference_key: str,
        preference_value: Any
    ) -> ConversationContext:
        """
        Store user preference in conversation context.

        Args:
            conversation_id: The conversation ID
            preference_key: Preference key
            preference_value: Preference value

        Returns:
            Created conversation context object
        """
        context_value = {
            "preference_key": preference_key,
            "preference_value": preference_value,
            "timestamp": datetime.utcnow().isoformat()
        }

        # User preferences don't expire
        return await self.store_context(
            conversation_id=conversation_id,
            context_type="user_preferences",
            context_key=preference_key,
            context_value=context_value,
            expires_at=None
        )

    async def get_user_preferences(
        self,
        conversation_id: UUID
    ) -> Dict[str, Any]:
        """
        Get all user preferences for a conversation.

        Args:
            conversation_id: The conversation ID

        Returns:
            Dictionary of user preferences
        """
        try:
            contexts = await self.get_conversation_context(
                conversation_id=conversation_id,
                context_type="user_preferences"
            )

            preferences = {}
            for context in contexts:
                try:
                    context_data = json.loads(context.context_value) if isinstance(context.context_value, str) else context.context_value
                    if isinstance(context_data, dict) and "preference_key" in context_data:
                        preferences[context_data["preference_key"]] = context_data["preference_value"]
                except (json.JSONDecodeError, TypeError):
                    logger.warning("Invalid preference context format",
                                 context_id=context.id)
                    continue

            return preferences

        except Exception as e:
            logger.error("Failed to get user preferences",
                        conversation_id=conversation_id,
                        error=str(e))
            return {}

    async def cleanup_expired_context(self) -> int:
        """
        Clean up expired context entries.

        Returns:
            Number of cleaned up entries
        """
        try:
            expired_contexts = self.db.query(ConversationContext).filter(
                ConversationContext.expires_at < datetime.utcnow()
            ).all()

            count = len(expired_contexts)

            for context in expired_contexts:
                self.db.delete(context)

            self.db.commit()

            if count > 0:
                logger.info("Cleaned up expired contexts",
                           count=count)

            return count

        except Exception as e:
            logger.error("Failed to cleanup expired context",
                        error=str(e))
            return 0

    async def get_conversation_summary(
        self,
        conversation_id: UUID
    ) -> Dict[str, Any]:
        """
        Get a summary of the conversation context.

        Args:
            conversation_id: The conversation ID

        Returns:
            Conversation summary
        """
        try:
            # Get all context types
            task_contexts = await self.get_conversation_context(
                conversation_id=conversation_id,
                context_type="task_history"
            )

            preference_contexts = await self.get_conversation_context(
                conversation_id=conversation_id,
                context_type="user_preferences"
            )

            # Get recent tasks from database
            recent_tasks = self.db.query(Task).filter(
                Task.user_id == self.user_id
            ).order_by(desc(Task.created_at)).limit(5).all()

            return {
                "conversation_id": str(conversation_id),
                "task_operations_count": len(task_contexts),
                "preferences_count": len(preference_contexts),
                "recent_tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "is_completed": task.is_completed,
                        "priority": task.priority.value if task.priority else None,
                        "created_at": task.created_at.isoformat()
                    }
                    for task in recent_tasks
                ],
                "context_summary": {
                    "task_history": len(task_contexts),
                    "user_preferences": len(preference_contexts)
                }
            }

        except Exception as e:
            logger.error("Failed to get conversation summary",
                        conversation_id=conversation_id,
                        error=str(e))
            return {
                "conversation_id": str(conversation_id),
                "error": str(e)
            }