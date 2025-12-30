"""
OpenAI Agents SDK Integration with MCP Tools.

Implements the Phase III spec: AI agent with function calling that invokes MCP tools.
This uses OpenAI's function calling feature to automatically determine which MCP tool
to call based on natural language commands.
"""

import os
import json
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID

import openai
import structlog
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.config import settings
from ..models.models import Task, Priority
from ..models.chat import Message, Conversation

logger = structlog.get_logger(__name__)

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

# Define MCP tools for OpenAI function calling
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task to create"
                    },
                    "description": {
                        "type": "string",
                        "description": "Human-readable notes ONLY. NEVER put priority levels (high/medium/low/urgent) or dates here. Leave null if user didn't provide notes."
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "MANDATORY: Set this when user mentions priority. 'high priority' = 'high', 'urgent' = 'urgent', etc. NEVER put in description field."
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format. Convert 'tomorrow' to '2025-12-20', 'next week' to actual date. NEVER put in description."
                    },
                    "tags": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "List of tags for the task"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed. Use this tool when the user asks to complete, finish, mark done, or check off a task. You MUST call this tool to actually complete a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as completed (e.g., 30)"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "REQUIRED for changing task priority, due date, title, or description. When user says 'set priority to high', 'make it urgent', 'change due date to tomorrow', or similar - you MUST call this tool with the appropriate field. First call list_tasks to find the task_id, then call update_task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The numeric ID of the task to update. Get this from list_tasks first."
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task. Only set if user wants to rename the task."
                    },
                    "description": {
                        "type": "string",
                        "description": "Human-readable notes about the task. NEVER put priority levels or dates here. Leave empty/null unless user explicitly provides a description."
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "MANDATORY for priority changes. Use 'low', 'medium', 'high', or 'urgent'. When user says 'high priority', 'make it urgent', 'low priority' etc., you MUST set this field. NEVER write priority in description."
                    },
                    "due_date": {
                        "type": "string",
                        "description": "MANDATORY for due date changes. Use ISO format YYYY-MM-DD. When user says 'due tomorrow', 'due next week', 'set deadline' etc., you MUST set this field. Convert 'tomorrow' to actual date like '2025-12-20'."
                    },
                    "tags": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "List of category tags for the task"
                    }
                },
                "required": ["task_id"]
            }
        }
    }
]

# Default MCP tools (fallback if dynamic loading fails)
DEFAULT_MCP_TOOLS = MCP_TOOLS


class MCPClient:
    """HTTP client for calling MCP tools."""
    
    def __init__(self, base_url: str = MCP_SERVER_URL, user_id: int = 0, jwt_token: Optional[str] = None):
        self.base_url = base_url
        self.user_id = user_id
        self.jwt_token = jwt_token or ""
        self.timeout = 30.0
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool via HTTP.
        
        Args:
            tool_name: Name of the MCP tool (add_task, list_tasks, etc.)
            params: Parameters to pass to the tool
            
        Returns:
            Tool result dictionary
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # MCP tools are exposed at /tools/{tool_name}
                # Handle None params by defaulting to empty dict
                safe_params = params if params is not None else {}
                request_data = {
                    "user_id": self.user_id,
                    "jwt_token": self.jwt_token,
                    **safe_params
                }
                
                response = await client.post(
                    f"{self.base_url}/tools/{tool_name}",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(
                        "MCP tool call successful",
                        tool=tool_name,
                        success=result.get("success", False)
                    )
                    return result
                else:
                    logger.warning(
                        "MCP tool call failed",
                        tool=tool_name,
                        status=response.status_code,
                        response=response.text[:200]
                    )
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except httpx.ConnectError:
            logger.warning("MCP server not available", url=self.base_url)
            return {"success": False, "error": "MCP server unavailable", "fallback": True}
        except Exception as e:
            logger.error("MCP tool call error", tool=tool_name, error=str(e))
            return {"success": False, "error": str(e)}


class OpenAIAgentWithMCP:
    """
    OpenAI Agent with MCP Tool Integration.
    
    Uses OpenAI's function calling to determine which MCP tool to invoke,
    then calls the MCP server to execute the operation.
    """
    
    # AI Provider endpoints (OpenAI-compatible)
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
    
    def __init__(
        self,
        session: AsyncSession,
        user_id: int,
        jwt_token: Optional[str] = None
    ):
        """
        Initialize the OpenAI Agent with MCP tools.
        
        Args:
            session: Async database session (for fallback)
            user_id: ID of the authenticated user
            jwt_token: JWT token for MCP authentication
        """
        self.session = session
        self.user_id = user_id
        self.jwt_token = jwt_token
        self.mcp_client = MCPClient(user_id=user_id, jwt_token=jwt_token)
        self.use_mcp = settings.USE_MCP_TOOLS
        self.tool_calls_made = []
        
        # Initialize OpenAI client (prefer Groq for fast inference)
        groq_key = settings.GROQ_API_KEY
        openai_key = settings.OPENAI_API_KEY
        gemini_key = settings.GEMINI_API_KEY
        
        # Prefer Groq (ultra-fast inference)
        if groq_key:
            self.client = openai.AsyncOpenAI(
                api_key=groq_key,
                base_url=self.GROQ_BASE_URL
            )
            self.model = "llama-3.3-70b-versatile"  # Official Groq model with superior tool use
            self.provider = "groq"
        elif openai_key:
            self.client = openai.AsyncOpenAI(api_key=openai_key)
            self.model = "gpt-4o-mini"  # Cost-effective model
            self.provider = "openai"
        elif gemini_key:
            self.client = openai.AsyncOpenAI(
                api_key=gemini_key,
                base_url=self.GEMINI_BASE_URL
            )
            self.model = "gemini-1.5-flash"  # Stable model with better quota limits
            self.provider = "gemini"
        else:
            raise ValueError("No AI API key configured (GROQ_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY)")
        
        # Cache for dynamically loaded tools
        self._tools_cache: Optional[List[Dict]] = None
        
        logger.info(
            "OpenAIAgentWithMCP initialized",
            user_id=user_id,
            use_mcp=self.use_mcp,
            provider=self.provider,
            model=self.model,
            jwt_token_provided=bool(jwt_token)
        )
    
    async def _load_conversation_history(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Load recent conversation history from database.
        
        Args:
            conversation_id: UUID of the conversation
            limit: Maximum messages to fetch (defaults to settings.AI_MAX_HISTORY_MESSAGES)
            
        Returns:
            List of message dicts in OpenAI format
        """
        if not conversation_id:
            return []
        
        limit = limit or settings.AI_MAX_HISTORY_MESSAGES
        
        try:
            statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp.desc()).limit(limit)
            
            result = await self.session.execute(statement)
            messages = result.scalars().all()
            
            # Convert to OpenAI format (reverse to get chronological order)
            history = []
            for msg in reversed(messages):
                role = msg.role if isinstance(msg.role, str) else msg.role.value
                history.append({
                    "role": role,
                    "content": msg.content
                })
            
            logger.debug(
                "Loaded conversation history",
                conversation_id=str(conversation_id),
                message_count=len(history)
            )
            return history
            
        except Exception as e:
            logger.warning(
                "Failed to load conversation history",
                conversation_id=str(conversation_id),
                error=str(e)
            )
            return []
    
    async def _get_mcp_tools(self) -> List[Dict]:
        """
        Get MCP tools, trying dynamic loading first if enabled.
        
        Returns:
            List of tool definitions for OpenAI function calling
        """
        # Return cached tools if available
        if self._tools_cache is not None:
            return self._tools_cache
        
        # Try dynamic loading if enabled
        if settings.AI_DYNAMIC_TOOLS:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        f"{settings.MCP_SERVER_URL}/tools"
                    )
                    if response.status_code == 200:
                        tools_data = response.json()
                        # Convert MCP tools to OpenAI format if needed
                        if isinstance(tools_data, list) and len(tools_data) > 0:
                            self._tools_cache = tools_data
                            logger.info(
                                "Loaded tools dynamically from MCP server",
                                tool_count=len(tools_data)
                            )
                            return self._tools_cache
            except Exception as e:
                logger.warning(
                    "Failed to fetch dynamic tools, using defaults",
                    error=str(e)
                )
        
        # Fallback to default tools
        self._tools_cache = DEFAULT_MCP_TOOLS
        return self._tools_cache
    
    async def process_message(
        self,
        message: str,
        conversation_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Process a user message using OpenAI function calling.
        
        This is the main entry point. It:
        1. Sends the message to OpenAI with tool definitions
        2. If OpenAI calls a tool, executes it via MCP
        3. Returns the final response
        
        Args:
            message: User's natural language message
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dictionary containing response, tool_calls, and success status
        """
        self.tool_calls_made = []
        
        try:
            # Load conversation history if available
            history = []
            if conversation_id:
                history = await self._load_conversation_history(conversation_id)
            
            # Build messages with system prompt from config
            messages = [
                {"role": "system", "content": settings.AI_SYSTEM_PROMPT}
            ]
            
            # Add conversation history (excluding system messages)
            for hist_msg in history:
                if hist_msg["role"] != "system":
                    messages.append(hist_msg)
            
            # Add current user message
            messages.append({"role": "user", "content": message})
            
            # Get tools (dynamic or fallback)
            tools = await self._get_mcp_tools()
            
            # Call OpenAI with tools (temperature=0 for reliable tool calling)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0
            )
            
            assistant_message = response.choices[0].message
            
            # Multi-step tool call loop (max 3 iterations for safety)
            max_iterations = 3
            iteration = 0
            
            while assistant_message.tool_calls and iteration < max_iterations:
                iteration += 1
                # Process each tool call
                tool_results = []
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(
                        "TRACE: AI requested tool call",
                        tool=function_name,
                        args=function_args,
                        iteration=iteration
                    )
                    
                    # Call MCP tool
                    result = await self.mcp_client.call_tool(function_name, function_args)
                    
                    self.tool_calls_made.append({
                        "tool": function_name,
                        "params": function_args,
                        "result": result
                    })
                    
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": json.dumps(result)
                    })
                
                # Add tool results and get next response (with tools enabled for multi-step)
                messages.append(assistant_message)
                messages.extend(tool_results)
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,  # Keep tools enabled for multi-step operations
                    tool_choice="auto",
                    temperature=0
                )
                
                assistant_message = response.choices[0].message
            
            # Get final text response
            response_text = assistant_message.content
            
            # Determine the operation type from tool calls (use the LAST one as the primary outcome)
            operation = None
            result_data = None
            if self.tool_calls_made:
                operation = self.tool_calls_made[-1]["tool"]
                result_data = self.tool_calls_made[-1]["result"]
                logger.info("TRACE: Final operation determined", operation=operation)
            
            return {
                "success": True,
                "response": response_text or "I've processed your request.",
                "operation": operation,
                "result": result_data,
                "tool_calls": self.tool_calls_made
            }
            
        except Exception as e:
            logger.error("Error processing message", error=str(e))
            return {
                "success": False,
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "operation": None,
                "result": None,
                "tool_calls": self.tool_calls_made,
                "error": str(e)
            }


def get_task_agent(session: AsyncSession, user_id: int, jwt_token: Optional[str] = None) -> OpenAIAgentWithMCP:
    """
    Factory function to create an OpenAI Agent with MCP tools.
    
    Args:
        session: Async database session
        user_id: User ID
        jwt_token: Optional JWT token for MCP authentication
        
    Returns:
        Configured OpenAIAgentWithMCP instance
    """
    return OpenAIAgentWithMCP(session, user_id, jwt_token)
