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