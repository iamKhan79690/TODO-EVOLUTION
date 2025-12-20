"""
AI Suggestion Service.

Intelligent task suggestions based on user behavior, patterns,
and conversation context.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from ..models import Task, Message, ConversationContext
from ..services.ai_service import AIService
from ..services.context_service import ContextService
import structlog

logger = structlog.get_logger(__name__)


class SuggestionService:
    """Service for generating intelligent task suggestions."""

    def __init__(self, db: Session, user_id: int, ai_service: Optional[AIService] = None):
        """
        Initialize the suggestion service.

        Args:
            db: Database session
            user_id: ID of the authenticated user
            ai_service: Optional AI service for enhanced suggestions
        """
        self.db = db
        self.user_id = user_id
        self.ai_service = ai_service
        self.context_service = ContextService(db, user_id)

    async def generate_suggestions(
        self,
        conversation_id: UUID,
        suggestion_type: str = "general",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate task suggestions based on context and user patterns.

        Args:
            conversation_id: The conversation ID
            suggestion_type: Type of suggestions (general, context_aware, deadline_based)
            limit: Maximum number of suggestions

        Returns:
            List of suggestions with metadata
        """
        try:
            # Get user's task history and patterns
            user_tasks = await self._get_user_task_patterns()
            recent_context = await self._get_recent_conversation_context(conversation_id)

            suggestions = []

            # Generate different types of suggestions
            if suggestion_type in ["general", "pattern_based"]:
                pattern_suggestions = await self._generate_pattern_based_suggestions(user_tasks, recent_context)
                suggestions.extend(pattern_suggestions)

            if suggestion_type in ["general", "deadline_aware"]:
                deadline_suggestions = await self._generate_deadline_aware_suggestions(user_tasks)
                suggestions.extend(deadline_suggestions)

            if suggestion_type in ["general", "context_aware"]:
                context_suggestions = await self._generate_context_aware_suggestions(recent_context, user_tasks)
                suggestions.extend(context_suggestions)

            # Use AI service for enhanced suggestions if available
            if self.ai_service and suggestion_type in ["general", "ai_enhanced"]:
                ai_suggestions = await self._generate_ai_suggestions(user_tasks, recent_context)
                suggestions.extend(ai_suggestions)

            # Deduplicate and rank suggestions
            unique_suggestions = await self._deduplicate_and_rank(suggestions, limit)

            logger.info("Generated suggestions",
                       conversation_id=conversation_id,
                       suggestion_type=suggestion_type,
                       total_generated=len(suggestions),
                       unique_count=len(unique_suggestions))

            return unique_suggestions

        except Exception as e:
            logger.error("Failed to generate suggestions",
                        conversation_id=conversation_id,
                        suggestion_type=suggestion_type,
                        error=str(e))
            return await self._get_fallback_suggestions(limit)

    async def _get_user_task_patterns(self) -> Dict[str, Any]:
        """Analyze user's task patterns."""
        try:
            # Get last 30 days of completed tasks
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_tasks = self.db.query(Task).filter(
                and_(
                    Task.user_id == self.user_id,
                    Task.created_at >= thirty_days_ago
                )
            ).all()

            # Analyze patterns
            patterns = {
                "total_tasks": len(recent_tasks),
                "completed_tasks": len([t for t in recent_tasks if t.is_completed]),
                "common_keywords": await self._extract_common_keywords(recent_tasks),
                "priority_distribution": await self._analyze_priority_distribution(recent_tasks),
                "completion_rate": len([t for t in recent_tasks if t.is_completed]) / max(len(recent_tasks), 1),
                "active_tasks": len([t for t in recent_tasks if not t.is_completed])
            }

            return patterns

        except Exception as e:
            logger.error("Failed to analyze user task patterns", error=str(e))
            return {"total_tasks": 0, "completed_tasks": 0}

    async def _extract_common_keywords(self, tasks: List[Task]) -> List[str]:
        """Extract common keywords from task titles."""
        try:
            # Simple keyword extraction from task titles
            all_words = []
            for task in tasks:
                words = task.title.lower().split()
                # Filter out common stop words
                meaningful_words = [w for w in words if len(w) > 3 and w not in ['task', 'need', 'will', 'make', 'get']]
                all_words.extend(meaningful_words)

            # Count word frequency
            word_counts = {}
            for word in all_words:
                word_counts[word] = word_counts.get(word, 0) + 1

            # Return top 5 most common words
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            return [word for word, count in sorted_words[:5]]

        except Exception as e:
            logger.error("Failed to extract keywords", error=str(e))
            return []

    async def _analyze_priority_distribution(self, tasks: List[Task]) -> Dict[str, int]:
        """Analyze distribution of task priorities."""
        priority_counts = {"URGENT": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

        for task in tasks:
            if task.priority:
                priority_counts[task.priority.value] += 1

        return priority_counts

    async def _get_recent_conversation_context(self, conversation_id: UUID) -> Dict[str, Any]:
        """Get recent conversation context."""
        try:
            # Get task history from context
            task_history = await self.context_service.get_task_history_context(conversation_id)

            # Get user preferences
            user_preferences = await self.context_service.get_user_preferences(conversation_id)

            return {
                "task_history": task_history[-10:],  # Last 10 task operations
                "user_preferences": user_preferences,
                "recent_tasks": len(task_history)
            }

        except Exception as e:
            logger.error("Failed to get conversation context", error=str(e))
            return {"task_history": [], "user_preferences": {}}

    async def _generate_pattern_based_suggestions(
        self,
        user_patterns: Dict[str, Any],
        recent_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on user patterns."""
        suggestions = []

        try:
            # Suggest based on common keywords
            common_keywords = user_patterns.get("common_keywords", [])
            if common_keywords:
                for keyword in common_keywords[:2]:  # Top 2 keywords
                    suggestions.append({
                        "type": "pattern_based",
                        "title": f"Consider {keyword} related task",
                        "description": f"You frequently work on {keyword} tasks",
                        "confidence": 0.6,
                        "source": "user_patterns"
                    })

            # Suggest based on completion rate
            completion_rate = user_patterns.get("completion_rate", 0)
            if completion_rate < 0.5:
                suggestions.append({
                    "type": "pattern_based",
                    "title": "Focus on completing existing tasks",
                    "description": "Your completion rate could be improved",
                    "confidence": 0.7,
                    "source": "completion_analysis"
                })

            # Suggest based on active tasks
            active_tasks = user_patterns.get("active_tasks", 0)
            if active_tasks > 10:
                suggestions.append({
                    "type": "pattern_based",
                    "title": "Review and prioritize your tasks",
                    "description": "You have many active tasks, consider prioritizing",
                    "confidence": 0.8,
                    "source": "workload_analysis"
                })

        except Exception as e:
            logger.error("Failed to generate pattern-based suggestions", error=str(e))

        return suggestions

    async def _generate_deadline_aware_suggestions(
        self,
        user_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on upcoming deadlines."""
        suggestions = []

        try:
            # Get tasks with due dates
            upcoming_tasks = self.db.query(Task).filter(
                and_(
                    Task.user_id == self.user_id,
                    Task.is_completed == False,
                    Task.due_date.isnot(None)
                )
            ).order_by(Task.due_date).limit(5).all()

            for task in upcoming_tasks:
                days_until_due = (task.due_date - datetime.utcnow()).days
                if days_until_due <= 3:  # Tasks due in 3 days
                    suggestions.append({
                        "type": "deadline_aware",
                        "title": f"Focus on: {task.title}",
                        "description": f"Due in {days_until_due} days",
                        "confidence": 0.9,
                        "source": "deadline_analysis",
                        "task_id": task.id
                    })

            # Suggest planning for the week ahead
            week_ahead = datetime.utcnow() + timedelta(days=7)
            week_tasks = self.db.query(Task).filter(
                and_(
                    Task.user_id == self.user_id,
                    Task.is_completed == False,
                    Task.due_date <= week_ahead
                )
            ).count()

            if week_tasks > 5:
                suggestions.append({
                    "type": "deadline_aware",
                    "title": "Plan your week ahead",
                    "description": f"You have {week_tasks} tasks due this week",
                    "confidence": 0.7,
                    "source": "weekly_planning"
                })

        except Exception as e:
            logger.error("Failed to generate deadline-aware suggestions", error=str(e))

        return suggestions

    async def _generate_context_aware_suggestions(
        self,
        recent_context: Dict[str, Any],
        user_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions based on conversation context."""
        suggestions = []

        try:
            task_history = recent_context.get("task_history", [])
            user_preferences = recent_context.get("user_preferences", {})

            # Analyze recent task operations
            recent_additions = [op for op in task_history if op.get("operation_type") == "add_task"]
            recent_completions = [op for op in task_history if op.get("operation_type") == "complete_task"]

            # Suggest follow-up tasks
            if recent_additions and not recent_completions:
                suggestions.append({
                    "type": "context_aware",
                    "title": "Consider breaking down your new tasks",
                    "description": "You recently added tasks, consider breaking them into smaller steps",
                    "confidence": 0.6,
                    "source": "conversation_flow"
                })

            # Suggest task review
            if len(recent_completions) > 2:
                suggestions.append({
                    "type": "context_aware",
                    "title": "Review your completed work",
                    "description": "Great progress! Consider what worked well for future planning",
                    "confidence": 0.5,
                    "source": "productivity_pattern"
                })

            # Use user preferences
            preferred_priority = user_preferences.get("preferred_priority")
            if preferred_priority:
                suggestions.append({
                    "type": "context_aware",
                    "title": f"Add {preferred_priority.lower()} priority task",
                    "description": f"Based on your preference for {preferred_priority} priority tasks",
                    "confidence": 0.6,
                    "source": "user_preferences"
                })

        except Exception as e:
            logger.error("Failed to generate context-aware suggestions", error=str(e))

        return suggestions

    async def _generate_ai_suggestions(
        self,
        user_patterns: Dict[str, Any],
        recent_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-enhanced suggestions."""
        if not self.ai_service:
            return []

        try:
            # Prepare context for AI
            context_prompt = f"""
            User Task Patterns:
            - Total tasks: {user_patterns.get('total_tasks', 0)}
            - Completion rate: {user_patterns.get('completion_rate', 0):.2%}
            - Active tasks: {user_patterns.get('active_tasks', 0)}
            - Common keywords: {', '.join(user_patterns.get('common_keywords', []))}

            Recent Context:
            - Recent task operations: {len(recent_context.get('task_history', []))}
            - User has preferences: {bool(recent_context.get('user_preferences'))}

            Generate 3 personalized task suggestions based on this user's patterns and context.
            Focus on actionable, relevant suggestions that would genuinely help them be more productive.
            Return as a JSON array of suggestion objects.
            """

            # Generate suggestions using AI service
            if hasattr(self.ai_service, 'generate_task_suggestions'):
                ai_suggestions = await self.ai_service.generate_task_suggestions(
                    self.user_id,
                    []  # Pass empty task list as we're providing context
                )

                # Convert AI suggestions to our format
                formatted_suggestions = []
                for i, suggestion in enumerate(ai_suggestions[:3]):
                    formatted_suggestions.append({
                        "type": "ai_enhanced",
                        "title": suggestion,
                        "description": "AI-generated suggestion based on your patterns",
                        "confidence": 0.7,
                        "source": "ai_analysis",
                        "suggestion_index": i
                    })

                return formatted_suggestions

        except Exception as e:
            logger.error("Failed to generate AI suggestions", error=str(e))

        return []

    async def _deduplicate_and_rank(
        self,
        suggestions: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Deduplicate suggestions and rank by confidence."""
        try:
            # Simple deduplication based on title
            seen_titles = set()
            unique_suggestions = []

            for suggestion in suggestions:
                title = suggestion.get("title", "").lower()
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_suggestions.append(suggestion)

            # Sort by confidence
            unique_suggestions.sort(key=lambda x: x.get("confidence", 0), reverse=True)

            return unique_suggestions[:limit]

        except Exception as e:
            logger.error("Failed to deduplicate and rank suggestions", error=str(e))
            return suggestions[:limit]

    async def _get_fallback_suggestions(self, limit: int) -> List[Dict[str, Any]]:
        """Get fallback suggestions when everything else fails."""
        fallback_suggestions = [
            {
                "type": "fallback",
                "title": "Review your weekly goals",
                "description": "Take time to review and adjust your goals for this week",
                "confidence": 0.3,
                "source": "fallback"
            },
            {
                "type": "fallback",
                "title": "Organize your workspace",
                "description": "A clean workspace can improve productivity",
                "confidence": 0.3,
                "source": "fallback"
            },
            {
                "type": "fallback",
                "title": "Plan tomorrow's priorities",
                "description": "Identify your top 3 priorities for tomorrow",
                "confidence": 0.3,
                "source": "fallback"
            },
            {
                "type": "fallback",
                "title": "Schedule a break",
                "description": "Regular breaks help maintain productivity",
                "confidence": 0.3,
                "source": "fallback"
            },
            {
                "type": "fallback",
                "title": "Update task statuses",
                "description": "Review and update your current task statuses",
                "confidence": 0.3,
                "source": "fallback"
            }
        ]

        return fallback_suggestions[:limit]