"""
Environment Configuration Management for MCP Server

Provides validated environment configuration with type checking,
default values, and validation rules for production deployment.
"""

import os
import re
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass
from enum import Enum

from ..utils.exceptions import ValidationError


class Environment(Enum):
    """Supported environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """Supported log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class JWTConfig:
    """JWT configuration."""
    secret_key: str
    algorithm: str = "RS256"
    token_expiry_minutes: int = 1440  # 24 hours


@dataclass
class MCPServerConfig:
    """MCP server configuration."""
    host: str = "0.0.0.0"
    port: int = 8050
    transport: str = "stdio"  # stdio or sse
    max_concurrent_tools: int = 100


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    response_time_target_ms: float = 200.0
    memory_limit_mb: int = 100
    connection_pool_size: int = 20
    cache_ttl_seconds: int = 300


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "text"  # text or json
    enable_file_logging: bool = True
    enable_console_logging: bool = True
    log_retention_days: int = 7


@dataclass
class EnvironmentConfig:
    """Complete environment configuration."""
    environment: Environment
    debug: bool
    database: DatabaseConfig
    jwt: JWTConfig
    mcp_server: MCPServerConfig
    performance: PerformanceConfig
    logging: LoggingConfig


class EnvironmentValidator:
    """Validates environment configuration values."""

    @staticmethod
    def validate_database_url(url: str) -> str:
        """Validate database URL format."""
        if not url:
            raise ValidationError("DATABASE_URL is required")

        # Basic format validation for PostgreSQL URLs
        pattern = r'^postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/([^/]+)$'
        if not re.match(pattern, url):
            raise ValidationError(
                "DATABASE_URL must be in format: postgresql://user:password@host:port/database"
            )

        return url

    @staticmethod
    def validate_jwt_secret(secret: str) -> str:
        """Validate JWT secret."""
        if not secret:
            raise ValidationError("JWT_SECRET is required")

        if len(secret) < 32:
            raise ValidationError("JWT_SECRET must be at least 32 characters long")

        return secret

    @staticmethod
    def validate_port(port: Union[str, int]) -> int:
        """Validate port number."""
        try:
            port_int = int(port)
            if port_int < 1 or port_int > 65535:
                raise ValidationError("Port must be between 1 and 65535")
            return port_int
        except ValueError:
            raise ValidationError("Port must be a valid integer")

    @staticmethod
    def validate_environment(env: str) -> Environment:
        """Validate environment type."""
        try:
            return Environment(env.lower())
        except ValueError:
            valid_envs = [e.value for e in Environment]
            raise ValidationError(f"Environment must be one of: {', '.join(valid_envs)}")

    @staticmethod
    def validate_log_level(level: str) -> str:
        """Validate log level."""
        try:
            LogLevel(level.lower())
            return level.upper()
        except ValueError:
            valid_levels = [l.value for l in LogLevel]
            raise ValidationError(f"Log level must be one of: {', '.join(valid_levels)}")

    @staticmethod
    def validate_positive_int(value: Union[str, int], field_name: str, min_val: int = 1) -> int:
        """Validate positive integer."""
        try:
            int_val = int(value)
            if int_val < min_val:
                raise ValidationError(f"{field_name} must be {min_val} or greater")
            return int_val
        except ValueError:
            raise ValidationError(f"{field_name} must be a valid integer")

    @staticmethod
    def validate_transport(transport: str) -> str:
        """Validate transport type."""
        valid_transports = ["stdio", "sse"]
        if transport.lower() not in valid_transports:
            raise ValidationError(f"Transport must be one of: {', '.join(valid_transports)}")
        return transport.lower()


class EnvironmentManager:
    """Manages environment configuration with validation."""

    def __init__(self):
        self._config: Optional[EnvironmentConfig] = None

    def load_config(self) -> EnvironmentConfig:
        """
        Load and validate environment configuration.

        Returns:
            Validated EnvironmentConfig instance

        Raises:
            ValidationError: If configuration is invalid
        """
        if self._config:
            return self._config

        # Load and validate environment
        env = EnvironmentValidator.validate_environment(
            os.getenv("ENVIRONMENT", "development")
        )
        debug = os.getenv("DEBUG", "false").lower() == "true"

        # Database configuration
        database = DatabaseConfig(
            url=EnvironmentValidator.validate_database_url(os.getenv("DATABASE_URL")),
            pool_size=EnvironmentValidator.validate_positive_int(
                os.getenv("CONNECTION_POOL_SIZE", "20"), "CONNECTION_POOL_SIZE"
            ),
            max_overflow=EnvironmentValidator.validate_positive_int(
                os.getenv("CONNECTION_POOL_MAX_OVERFLOW", "30"), "CONNECTION_POOL_MAX_OVERFLOW"
            ),
            pool_timeout=EnvironmentValidator.validate_positive_int(
                os.getenv("POOL_TIMEOUT", "30"), "POOL_TIMEOUT"
            ),
            pool_recycle=EnvironmentValidator.validate_positive_int(
                os.getenv("POOL_RECYCLE", "3600"), "POOL_RECYCLE"
            ),
            echo=os.getenv("DATABASE_ECHO", "false").lower() == "true"
        )

        # JWT configuration
        jwt = JWTConfig(
            secret_key=EnvironmentValidator.validate_jwt_secret(os.getenv("JWT_SECRET")),
            algorithm=os.getenv("JWT_ALGORITHM", "RS256"),
            token_expiry_minutes=EnvironmentValidator.validate_positive_int(
                os.getenv("JWT_EXPIRY_MINUTES", "1440"), "JWT_EXPIRY_MINUTES"
            )
        )

        # MCP server configuration
        mcp_server = MCPServerConfig(
            host=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
            port=EnvironmentValidator.validate_port(os.getenv("MCP_SERVER_PORT", "8050")),
            transport=EnvironmentValidator.validate_transport(os.getenv("TRANSPORT", "stdio")),
            max_concurrent_tools=EnvironmentValidator.validate_positive_int(
                os.getenv("MAX_CONCURRENT_TOOLS", "100"), "MAX_CONCURRENT_TOOLS"
            )
        )

        # Performance configuration
        performance = PerformanceConfig(
            response_time_target_ms=float(os.getenv("RESPONSE_TIME_TARGET_MS", "200")),
            memory_limit_mb=EnvironmentValidator.validate_positive_int(
                os.getenv("MEMORY_LIMIT_MB", "100"), "MEMORY_LIMIT_MB"
            ),
            connection_pool_size=database.pool_size,
            cache_ttl_seconds=EnvironmentValidator.validate_positive_int(
                os.getenv("CACHE_TTL", "300"), "CACHE_TTL"
            )
        )

        # Logging configuration
        logging_config = LoggingConfig(
            level=EnvironmentValidator.validate_log_level(os.getenv("LOG_LEVEL", "INFO")),
            format=os.getenv("LOG_FORMAT", "text"),
            enable_file_logging=os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true",
            enable_console_logging=os.getenv("ENABLE_CONSOLE_LOGGING", "true").lower() == "true",
            log_retention_days=EnvironmentValidator.validate_positive_int(
                os.getenv("LOG_RETENTION_DAYS", "7"), "LOG_RETENTION_DAYS", min_val=1
            )
        )

        self._config = EnvironmentConfig(
            environment=env,
            debug=debug,
            database=database,
            jwt=jwt,
            mcp_server=mcp_server,
            performance=performance,
            logging=logging_config
        )

        return self._config

    def get_config(self) -> EnvironmentConfig:
        """
        Get the loaded configuration.

        Returns:
            EnvironmentConfig instance

        Raises:
            RuntimeError: If configuration has not been loaded
        """
        if not self._config:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self._config

    def reload_config(self) -> EnvironmentConfig:
        """
        Force reload of configuration from environment variables.

        Returns:
            Newly loaded EnvironmentConfig instance
        """
        self._config = None
        return self.load_config()

    def validate_production_readiness(self) -> Dict[str, Any]:
        """
        Validate if configuration is ready for production.

        Returns:
            Dictionary with validation results
        """
        config = self.get_config()
        issues = []

        # Check environment
        if config.environment == Environment.PRODUCTION:
            if config.debug:
                issues.append("Debug mode should be disabled in production")

            if config.database.echo:
                issues.append("Database echo should be disabled in production")

            if config.jwt.secret_key == "your-secret-key-here" or len(config.jwt.secret_key) < 64:
                issues.append("JWT secret should be strong and unique in production")

            if config.mcp_server.host == "0.0.0.0" and not os.getenv("FORCE_PROD_HOST"):
                issues.append("Consider binding to specific IP in production")

            if config.logging.level == "DEBUG":
                issues.append("DEBUG log level not recommended for production")

        # Check database URL
        if "localhost" in config.database.url or "127.0.0.1" in config.database.url:
            if config.environment == Environment.PRODUCTION:
                issues.append("Using localhost database in production")

        # Check performance settings
        if config.performance.memory_limit_mb < 50:
            issues.append("Memory limit too low for production (<50MB)")

        return {
            "ready": len(issues) == 0,
            "environment": config.environment.value,
            "issues": issues
        }

    def get_environment_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current environment configuration.

        Returns:
            Dictionary with configuration summary
        """
        config = self.get_config()

        return {
            "environment": config.environment.value,
            "debug": config.debug,
            "database": {
                "url": "***" if config.environment == Environment.PRODUCTION else config.database.url,
                "pool_size": config.database.pool_size,
                "max_overflow": config.database.max_overflow
            },
            "mcp_server": {
                "host": config.mcp_server.host,
                "port": config.mcp_server.port,
                "transport": config.mcp_server.transport,
                "max_concurrent_tools": config.mcp_server.max_concurrent_tools
            },
            "performance": {
                "response_time_target_ms": config.performance.response_time_target_ms,
                "memory_limit_mb": config.performance.memory_limit_mb,
                "cache_ttl_seconds": config.performance.cache_ttl_seconds
            },
            "logging": {
                "level": config.logging.level,
                "format": config.logging.format,
                "enable_file_logging": config.logging.enable_file_logging,
                "enable_console_logging": config.logging.enable_console_logging
            }
        }


# Global environment manager instance
env_manager = EnvironmentManager()


# Convenience functions
def load_environment() -> EnvironmentConfig:
    """Load and validate environment configuration."""
    return env_manager.load_config()


def get_environment() -> EnvironmentConfig:
    """Get current environment configuration."""
    return env_manager.get_config()


def is_development() -> bool:
    """Check if running in development environment."""
    try:
        config = get_environment()
        return config.environment == Environment.DEVELOPMENT
    except:
        return True  # Assume development if config fails


def is_production() -> bool:
    """Check if running in production environment."""
    try:
        config = get_environment()
        return config.environment == Environment.PRODUCTION
    except:
        return False


def get_database_url() -> str:
    """Get database URL."""
    config = get_environment()
    return config.database.url


def get_jwt_secret() -> str:
    """Get JWT secret."""
    config = get_environment()
    return config.jwt.secret_key