"""
Configuration settings for the Todo Evolution API
"""

import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = Field(default="Todo Evolution API")
    VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=True)
    ENVIRONMENT: str = Field(default="development")

    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/todoapp"
    )
    DATABASE_URL_ASYNC: str = os.getenv(
        "DATABASE_URL_ASYNC",
        "postgresql+asyncpg://user:password@localhost:5432/todoapp"
    )

    # Database connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
    )

    # Authentication
    BETTER_AUTH_SECRET: str = Field(
        default="change-this-secret-key-in-production"
    )
    BETTER_AUTH_URL: str = Field(default="http://localhost:8000/auth")
    BETTER_AUTH_APP_NAME: str = Field(default="Todo Evolution")
    BETTER_AUTH_TRUSTED_ORIGINS: Union[str, List[str]] = Field(
        default=["http://localhost:3000"]
    )

    JWT_SECRET: str = Field(
        default="change-this-jwt-secret-key-in-production"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=30)
    JWT_REFRESH_EXPIRE_DAYS: int = Field(default=7)

    # Frontend URLs
    FRONTEND_URL: str = Field(default="http://localhost:3000")

    # Redis Configuration (for token blacklisting)
    REDIS_URL: str = Field(default="redis://localhost:6379")
    REDIS_ENABLED: bool = Field(default=True)

    # AI API Keys (Groq is preferred for fast inference)
    GROQ_API_KEY: str = Field(default="")  # Groq API key (preferred - fast inference)
    GEMINI_API_KEY: str = Field(default="")  # Google Gemini API key (fallback)
    OPENAI_API_KEY: str = Field(default="")  # OpenAI API key (fallback)

    # MCP Server Configuration
    USE_MCP_TOOLS: bool = Field(default=False)  # Enable MCP HTTP tool calls
    MCP_SERVER_URL: str = Field(default="http://localhost:8001")  # MCP server URL

    # MCP Server Runtime Configuration
    TRANSPORT: str = Field(default="http")  # MCP server transport type
    MCP_HTTP_HOST: str = Field(default="0.0.0.0")  # MCP server host
    MCP_HTTP_PORT: int = Field(default=8001)  # MCP server port

    # AI Agent Configuration
    AI_SYSTEM_PROMPT: str = Field(default="""You are a helpful task management assistant. You help users manage their TODO tasks through natural conversation.

WHEN TO USE TOOLS:
- Use tools ONLY when the user explicitly wants to manage tasks (add, list, complete, delete, update)
- For greetings ("hi", "hello"), questions about yourself, or general chat - just respond conversationally WITHOUT calling any tools

CRITICAL RULES FOR TASK OPERATIONS:
1. For complete_task, delete_task, or update_task - you MUST call list_tasks FIRST to get the actual task IDs
2. NEVER guess task IDs. Always call list_tasks first, then use the real task_id from the result
3. If you don't know a task_id, call list_tasks with status="all" first
4. Task IDs are integers, not strings. Never use "unknown" as a task_id

AVAILABLE TOOLS:
- add_task: Create a new task (requires title as string)
- list_tasks: Get all tasks with their IDs (call this FIRST before complete/delete/update)
- complete_task: Mark a task as done (requires task_id as integer - get from list_tasks first)
- delete_task: Remove a task (requires task_id as integer - get from list_tasks first)
- update_task: Modify a task (requires task_id as integer - get from list_tasks first)

WORKFLOW EXAMPLES:
- "Delete the lunch task" → 1) Call list_tasks() 2) Find task with title "lunch" 3) Call delete_task(task_id=<actual_id>)
- "Complete my shopping task" → 1) Call list_tasks() 2) Find matching task 3) Call complete_task(task_id=<actual_id>)
- "Add task: Buy groceries" → Call add_task(title="Buy groceries")

Keep responses brief and friendly.""")
    AI_MAX_HISTORY_MESSAGES: int = Field(default=10)  # Max messages to include in context
    AI_DYNAMIC_TOOLS: bool = Field(default=False)  # Try to fetch tools from MCP server

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Split comma-separated string into list
            return [origin.strip() for origin in v.split(',')]
        return v

    @field_validator('BETTER_AUTH_TRUSTED_ORIGINS', mode='before')
    @classmethod
    def parse_trusted_origins(cls, v):
        if isinstance(v, str):
            # Split comma-separated string into list
            return [origin.strip() for origin in v.split(',')]
        return v

    # API
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()