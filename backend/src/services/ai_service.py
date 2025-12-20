"""
AI Processing Service for Natural Language TODO Management.

Handles natural language processing, OpenAI API integration, and command
interpretation for the AI chat assistant functionality.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4

import openai
import structlog
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError

logger = structlog.get_logger(__name__)

# Command patterns for natural language processing
COMMAND_PATTERNS = {
    'add_task': [
        r'add\s+(?:a\s+)?task\s+(?:to\s+)?(.+?)(?:\s+(?:for|on|at)\s+(.+?))?(?:\s+(?:due|by)\s+(.+?))?$',
        r'create\s+(?:a\s+)?task\s+(?:to\s+)?(.+?)(?:\s+(?:for|on|at)\s+(.+?))?(?:\s+(?:due|by)\s+(.+?))?$',
        r'new\s+task\s+(?:to\s+)?(.+?)(?:\s+(?:for|on|at)\s+(.+?))?(?:\s+(?:due|by)\s+(.+?))?$',
        r'I\s+need\s+to\s+(.+?)(?:\s+(?:for|on|at)\s+(.+?))?(?:\s+(?:due|by)\s+(.+?))?$',
        r'remind\s+me\s+to\s+(.+?)(?:\s+(?:for|on|at)\s+(.+?))?(?:\s+(?:due|by)\s+(.+?))?$'
    ],
    'complete_task': [
        r'(?:mark\s+)?(?:task\s+)?(.+?)\s+(?:as\s+)?(?:completed|done|finished)$',
        r'(?:complete|finish|done)\s+(?:task\s+)?(.+?)$',
        r'I\s+(?:completed|finished|done)\s+(?:task\s+)?(.+?)$',
        r'(?:task\s+)?(.+?)\s+(?:is\s+)?(?:completed|done|finished)$'
    ],
    'update_task': [
        r'update\s+(?:task\s+)?(.+?)\s+(?:to|as)\s+(.+?)$',
        r'change\s+(?:task\s+)?(.+?)\s+(?:to|as)\s+(.+?)$',
        r'modify\s+(?:task\s+)?(.+?)\s+(?:to|as)\s+(.+?)$',
        r'set\s+(?:task\s+)?(.+?)\s+(?:to|as)\s+(.+?)$'
    ],
    'delete_task': [
        r'delete\s+(?:task\s+)?(.+?)$',
        r'remove\s+(?:task\s+)?(.+?)$',
        r'get\s+rid\s+of\s+(?:task\s+)?(.+?)$',
        r'(?:task\s+)?(.+?)\s+(?:no\s+longer\s+)?(?:needed|required)$'
    ],
    'list_tasks': [
        r'show\s+(?:me\s+)?(?:my\s+)?tasks?(?:\s+(?:for|on|at)\s+(.+?))?$',
        r'list\s+(?:my\s+)?tasks?(?:\s+(?:for|on|at)\s+(.+?))?$',
        r'what\s+tasks?\s+do\s+I\s+have(?:\s+(?:for|on|at)\s+(.+?))?$',
        r'display\s+(?:my\s+)?tasks?(?:\s+(?:for|on|at)\s+(.+?))?$'
    ],
    'search_tasks': [
        r'find\s+(?:tasks?\s+)?(?:containing|with)\s+(.+?)$',
        r'search\s+(?:for\s+)?(.+?)$',
        r'look\s+for\s+(?:tasks?\s+)?(?:with|containing)\s+(.+?)$',
        r'filter\s+(?:tasks?\s+)?(?:by|with)\s+(.+?)$'
    ]
}

# Priority mappings
PRIORITY_MAPPINGS = {
    'urgent': 'URGENT',
    'high': 'HIGH',
    'important': 'HIGH',
    'medium': 'MEDIUM',
    'normal': 'MEDIUM',
    'low': 'LOW',
    'minor': 'LOW'
}


class TaskCommand(BaseModel):
    """Structured task command from natural language input."""
    command_type: str
    task_title: Optional[str] = None
    task_description: Optional[str] = None
    task_priority: Optional[str] = None
    due_date: Optional[datetime] = None
    task_id: Optional[int] = None
    search_query: Optional[str] = None
    confidence: float = 0.0
    original_text: str
    conversation_id: Optional[UUID] = None


class AIService:
    """Service for processing natural language commands and managing AI interactions.
    
    Supports both OpenAI and Google Gemini APIs. Gemini is accessed via OpenAI-compatible
    endpoint, allowing use of the same OpenAI SDK with Gemini's models.
    """

    # Google Gemini OpenAI-compatible endpoint
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
    
    # Gemini model mappings (use these model names with Gemini)
    GEMINI_MODELS = {
        "gemini-2.0-flash": "gemini-2.0-flash-exp",  # Latest and fastest
        "gemini-1.5-flash": "gemini-1.5-flash",      # Fast and efficient
        "gemini-1.5-pro": "gemini-1.5-pro",          # Most capable
    }

    def __init__(
        self, 
        openai_api_key: str = "",
        gemini_api_key: str = "",
        use_gemini: bool = True  # Default to Gemini if available
    ):
        """
        Initialize the AI service with OpenAI or Gemini client.
        
        Args:
            openai_api_key: OpenAI API key (optional)
            gemini_api_key: Google Gemini API key (optional, preferred)
            use_gemini: Whether to prefer Gemini over OpenAI when both are available
        """
        import os
        
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY", "")
        
        self.client = None
        self.model = None
        self.provider = None
        
        # Try Gemini first if preferred and key is available
        if use_gemini and self.gemini_api_key and self.gemini_api_key.strip():
            self.client = openai.AsyncOpenAI(
                api_key=self.gemini_api_key,
                base_url=self.GEMINI_BASE_URL
            )
            self.model = "gemini-2.0-flash-exp"  # Use the latest Gemini model
            self.provider = "gemini"
            logger.info("AI Service initialized with Google Gemini (via OpenAI-compatible endpoint)")
        
        # Fall back to OpenAI if Gemini not available
        elif self.openai_api_key and self.openai_api_key.strip():
            self.client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            self.model = "gpt-3.5-turbo"
            self.provider = "openai"
            logger.info("AI Service initialized with OpenAI client")
        
        else:
            self.client = None
            self.provider = "pattern_matching"
            logger.warning("AI Service initialized without API keys - using pattern matching only")

    async def process_natural_language_command(
        self,
        message: str,
        user_id: int,
        conversation_id: Optional[UUID] = None
    ) -> TaskCommand:
        """
        Process a natural language message and extract task command.

        Args:
            message: The user's natural language message
            user_id: The user's ID
            conversation_id: Optional conversation ID for context

        Returns:
            Structured TaskCommand with extracted information
        """
        try:
            # First try pattern-based extraction
            pattern_command = await self._extract_command_from_patterns(message)

            if pattern_command.confidence > 0.6:
                logger.info("Command extracted from patterns",
                           command_type=pattern_command.command_type,
                           confidence=pattern_command.confidence)
                return pattern_command

            # Fall back to AI-based extraction if patterns don't work well
            if self.client:
                ai_command = await self._extract_command_with_ai(message)
                logger.info("Command extracted with AI",
                           command_type=ai_command.command_type,
                           confidence=ai_command.confidence)
                return ai_command
            else:
                # If no OpenAI client available, return pattern command even with lower confidence
                logger.info("Using pattern-based extraction only (no OpenAI client)",
                           command_type=pattern_command.command_type,
                           confidence=pattern_command.confidence)
                return pattern_command

        except Exception as e:
            logger.error("Error processing natural language command",
                        message=message,
                        user_id=user_id,
                        error=str(e))
            return TaskCommand(
                command_type="unknown",
                original_text=message,
                confidence=0.0
            )

    async def _extract_command_from_patterns(self, message: str) -> TaskCommand:
        """Extract command using regex patterns."""
        message_lower = message.lower().strip()

        for command_type, patterns in COMMAND_PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, message_lower, re.IGNORECASE)
                if match:
                    return await self._parse_command_match(command_type, match, message)

        return TaskCommand(
            command_type="unknown",
            original_text=message,
            confidence=0.0
        )

    async def _parse_command_match(
        self,
        command_type: str,
        match: re.Match,
        original_message: str
    ) -> TaskCommand:
        """Parse a regex match into a structured command."""
        groups = match.groups()

        command = TaskCommand(
            command_type=command_type,
            original_text=original_message,
            confidence=0.8  # High confidence for pattern matches
        )

        if command_type == 'add_task':
            command.task_title = groups[0].strip() if groups[0] else None
            if groups[1]:
                command.task_description = f"Context: {groups[1].strip()}"
            if groups[2]:
                command.due_date = self._parse_due_date(groups[2].strip())

        elif command_type in ['complete_task', 'delete_task']:
            command.task_title = groups[0].strip() if groups[0] else None

        elif command_type == 'update_task':
            command.task_title = groups[0].strip() if groups[0] else None
            command.task_description = groups[1].strip() if groups[1] else None

        elif command_type in ['list_tasks', 'search_tasks']:
            if command_type == 'search_tasks':
                command.search_query = groups[0].strip() if groups[0] else None

        # Extract priority from message
        priority = self._extract_priority(original_message)
        if priority:
            command.task_priority = PRIORITY_MAPPINGS.get(priority.lower(), None)

        return command

    async def _extract_command_with_ai(self, message: str) -> TaskCommand:
        """Extract command using AI when patterns fail."""
        if not self.client:
            # Fallback to basic pattern matching if no OpenAI client
            return await self._extract_command_from_patterns(message)

        system_prompt = """
        You are a task management assistant. Extract structured commands from natural language messages.
        Analyze the user's message and determine what action they want to perform with their tasks.

        Possible command types:
        - add_task: Create a new task
        - complete_task: Mark a task as completed
        - update_task: Modify an existing task
        - delete_task: Remove a task
        - list_tasks: Show all tasks
        - search_tasks: Find specific tasks

        Also extract any relevant details like task title, description, priority (urgent/high/medium/low), and due dates.
        Respond with only a JSON object.

        Example response format:
        {
            "command_type": "add_task",
            "task_title": "Buy groceries",
            "task_description": "Milk, eggs, bread",
            "task_priority": "MEDIUM",
            "due_date": "2025-01-20",
            "confidence": 0.9
        }
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract command from: {message}"}
                ],
                temperature=0.1,
                max_tokens=500
            )

            content = response.choices[0].message.content
            ai_data = json.loads(content)

            return TaskCommand(
                command_type=ai_data.get('command_type', 'unknown'),
                task_title=ai_data.get('task_title'),
                task_description=ai_data.get('task_description'),
                task_priority=ai_data.get('task_priority'),
                due_date=self._parse_due_date(ai_data.get('due_date')) if ai_data.get('due_date') else None,
                confidence=ai_data.get('confidence', 0.5),
                original_text=message
            )

        except Exception as e:
            logger.error("AI command extraction failed", error=str(e))
            return TaskCommand(
                command_type="unknown",
                original_text=message,
                confidence=0.0
            )

    def _extract_priority(self, message: str) -> Optional[str]:
        """Extract priority keywords from message."""
        priority_keywords = ['urgent', 'high', 'medium', 'low', 'important', 'minor', 'normal']
        message_lower = message.lower()

        for keyword in priority_keywords:
            if keyword in message_lower:
                return keyword
        return None

    def _parse_due_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats into datetime objects."""
        if not date_str:
            return None

        date_str = date_str.strip().lower()
        now = datetime.now()

        try:
            # Today, tomorrow, yesterday
            if date_str == 'today':
                return now
            elif date_str == 'tomorrow':
                return now + timedelta(days=1)
            elif date_str == 'yesterday':
                return now - timedelta(days=1)

            # Days of the week
            days = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }

            for day_name, day_num in days.items():
                if day_name in date_str:
                    days_ahead = (day_num - now.weekday()) % 7
                    if days_ahead == 0:
                        days_ahead = 7  # Next week
                    return now + timedelta(days=days_ahead)

            # "in X days/weeks"
            in_match = re.match(r'in\s+(\d+)\s+(day|days|week|weeks)', date_str)
            if in_match:
                num = int(in_match.group(1))
                unit = in_match.group(2)
                if 'week' in unit:
                    return now + timedelta(weeks=num)
                else:
                    return now + timedelta(days=num)

            # Relative dates like "next monday", "this friday"
            if 'next' in date_str:
                for day_name, day_num in days.items():
                    if day_name in date_str:
                        days_ahead = (day_num - now.weekday() + 7) % 7
                        if days_ahead == 0:
                            days_ahead = 7
                        return now + timedelta(days=days_ahead)

            # Try to parse specific date formats
            # MM/DD, MM/DD/YYYY, etc.
            date_formats = [
                '%m/%d',
                '%m/%d/%Y',
                '%Y-%m-%d',
                '%m-%d',
                '%m-%d-%Y',
                '%B %d',      # January 15
                '%B %d, %Y', # January 15, 2025
            ]

            for fmt in date_formats:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    # If no year provided, use current year
                    if parsed.year == 1900 and '%Y' not in fmt:
                        parsed = parsed.replace(year=now.year)
                        if parsed < now:
                            parsed = parsed.replace(year=now.year + 1)
                    return parsed
                except ValueError:
                    continue

        except Exception as e:
            logger.debug("Could not parse date", date_str=date_str, error=str(e))

        return None

    async def generate_task_suggestions(
        self,
        user_id: int,
        existing_tasks: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate task suggestions based on user's existing tasks and patterns."""
        if not self.client:
            # Return generic suggestions if no OpenAI client
            return [
                "Review your pending tasks for the week",
                "Add a personal wellness activity",
                "Plan your goals for tomorrow",
                "Organize your workspace",
                "Schedule some relaxation time"
            ]

        try:
            task_list = "\n".join([f"- {task.get('title', '')}" for task in existing_tasks[:10]])

            system_prompt = """
            Based on the user's current tasks, suggest 3-5 new tasks they might want to add.
            Consider patterns, related activities, or logical next steps.
            Return only a JSON array of suggestion strings.
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Current tasks:\n{task_list}"}
                ],
                temperature=0.7,
                max_tokens=300
            )

            content = response.choices[0].message.content
            suggestions = json.loads(content)

            return suggestions if isinstance(suggestions, list) else []

        except Exception as e:
            logger.error("Failed to generate task suggestions", error=str(e))
            return []

    async def format_task_response(
        self,
        command: TaskCommand,
        operation_result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> str:
        """Format a user-friendly response for task operations."""
        try:
            if error:
                return f"❌ Sorry, I couldn't {command.command_type.replace('_', ' ')}: {error}"

            if not operation_result:
                return f"⚠️ I understood you want to {command.command_type.replace('_', ' ')} but need more information."

            success_responses = {
                'add_task': f"✅ I've added the task: {operation_result.get('title', 'Your task')}",
                'complete_task': f"✅ Marked as completed: {operation_result.get('title', 'Task')}",
                'update_task': f"✅ Updated task: {operation_result.get('title', 'Task')}",
                'delete_task': f"✅ Deleted task: {operation_result.get('title', 'Task')}",
                'list_tasks': "📋 Here are your tasks:",
                'search_tasks': f"🔍 Found tasks matching: {command.search_query}"
            }

            base_response = success_responses.get(command.command_type, "✅ Operation completed")

            # Add additional details for specific operations
            if command.command_type == 'list_tasks' and operation_result:
                tasks = operation_result.get('tasks', [])
                if tasks:
                    task_list = "\n".join([f"• {task.get('title', '')}" for task in tasks[:5]])
                    base_response += f"\n\n{task_list}"
                    if len(tasks) > 5:
                        base_response += f"\n\n... and {len(tasks) - 5} more"
                else:
                    base_response += "\n\nNo tasks found!"

            return base_response

        except Exception as e:
            logger.error("Failed to format response", error=str(e))
            return "✅ Operation completed successfully"

    async def is_task_related_message(self, message: str) -> bool:
        """Determine if a message is related to task management."""
        task_keywords = [
            'task', 'todo', 'remember', 'remind', 'add', 'create', 'delete', 'remove',
            'complete', 'finish', 'done', 'list', 'show', 'find', 'search', 'update',
            'change', 'modify', 'priority', 'due', 'deadline', 'schedule'
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in task_keywords)