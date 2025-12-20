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

    # AI API Keys (Gemini is preferred if available)
    GEMINI_API_KEY: str = Field(default="")  # Google Gemini API key (recommended)
    OPENAI_API_KEY: str = Field(default="")  # OpenAI API key (fallback)

    # MCP Server Configuration
    USE_MCP_TOOLS: bool = Field(default=False)  # Enable MCP HTTP tool calls
    MCP_SERVER_URL: str = Field(default="http://localhost:8001")  # MCP server URL

    # MCP Server Runtime Configuration
    TRANSPORT: str = Field(default="http")  # MCP server transport type
    MCP_HTTP_HOST: str = Field(default="0.0.0.0")  # MCP server host
    MCP_HTTP_PORT: int = Field(default=8001)  # MCP server port

    # AI Agent Configuration
    AI_SYSTEM_PROMPT: str = Field(default="""You are a high-speed, decisive task management engine. Your ONLY objective is to execute user commands immediately and precisely.

ABSOLUTE RULES:
1. NO PRE-COMMAND CHATTER: Do NOT ask "Would you like me to...?" or "I can do that, should I proceed?". Just execute.
2. NO CONFIRMATION: Never ask for confirmation. If a user says "Delete my tasks", delete them immediately. If they say "Update priority", do it.
3. IMMEDIATE ACTION: Your first response to any actionable request MUST be the appropriate tool call(s).
4. MULTI-STEP EXECUTION: If you need to find a task ID first, call 'list_tasks', find the ID, then immediately call the required tool (update_task, delete_task, complete_task).
5. PARAMETER PRECISION:
   - Priority: 'low', 'medium', 'high', 'urgent'. PUT THESE IN THE priority FIELD, NEVER in description.
   - Dates: Convert to YYYY-MM-DD format and PUT IN due_date FIELD, NEVER in description.
   - Description: ONLY for human notes. NEVER put "high priority" or "due tomorrow" in description.

CRITICAL SCENARIO GUIDES:
- "Set task X to high priority": list_tasks -> update_task(task_id=ID, priority='high') -> "Priority updated."
- "Make X urgent": list_tasks -> update_task(task_id=ID, priority='urgent') -> "Done."
- "Change priority to low": list_tasks -> update_task(task_id=ID, priority='low') -> "Updated."
- "Set due date to tomorrow": list_tasks -> update_task(task_id=ID, due_date='2025-12-20') -> "Due date set."
- "Add high priority task X": add_task(title='X', priority='high') -> "Task added."
- "Delete everything": list_tasks -> delete_task for each -> "All tasks deleted."

Response Style: Extremely brief. "Updated.", "Done.", "Priority set.", "Task added." Focus on action.
""")
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