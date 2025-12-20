"""
Logging Configuration for MCP Server

Provides structured logging with correlation ID support for observability
and debugging in distributed MCP server environments.
"""

import os
import sys
import logging
import logging.handlers
from typing import Any, Dict
import structlog
from contextlib import contextmanager

from .jwt_config import jwt_config
from ..utils.correlation_ids import get_correlation_id


class CorrelationIDFilter(logging.Filter):
    """Filter that adds correlation ID to log records."""

    def filter(self, record):
        """Add correlation ID to log record."""
        record.correlation_id = get_correlation_id()
        return True


class MCPFormatter(logging.Formatter):
    """Custom formatter for MCP server logs."""

    def __init__(self):
        super().__init__()
        self.formatters = {
            logging.DEBUG: logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s"
            ),
            logging.INFO: logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s"
            ),
            logging.WARNING: logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s"
            ),
            logging.ERROR: logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s | %(pathname)s:%(lineno)d"
            ),
            logging.CRITICAL: logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s | %(pathname)s:%(lineno)d"
            ),
        }

    def format(self, record):
        """Format log record with appropriate formatter."""
        formatter = self.formatters.get(record.levelno)
        if formatter:
            return formatter.format(record)
        return super().format(record)


def configure_logging(
    log_level: str = None,
    log_format: str = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True
) -> logging.Logger:
    """
    Configure structured logging for the MCP server.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, text)
        enable_file_logging: Whether to enable file logging
        enable_console_logging: Whether to enable console logging

    Returns:
        Configured logger instance
    """
    # Set defaults from environment
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = log_format or os.getenv("LOG_FORMAT", "text").lower()

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add format-specific processor
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add correlation ID filter
    correlation_filter = CorrelationIDFilter()

    # Console handler
    if enable_console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.addFilter(correlation_filter)
        console_handler.setFormatter(MCPFormatter())
        root_logger.addHandler(console_handler)

    # File handler
    if enable_file_logging:
        try:
            # Create logs directory if it doesn't exist
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)

            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=f"{log_dir}/mcp_server.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setLevel(getattr(logging, log_level))
            file_handler.addFilter(correlation_filter)

            if log_format == "json":
                # Use structlog processor for JSON format
                from structlog.stdlib import LoggerFactory

                class JSONFileHandler(logging.Handler):
                    def __init__(self, filename, max_bytes, backup_count):
                        super().__init__()
                        self.file_handler = logging.handlers.RotatingFileHandler(
                            filename, maxBytes=maxBytes, backupCount=backupCount, encoding="utf-8"
                        )

                    def emit(self, record):
                        try:
                            import json
                            log_entry = {
                                "timestamp": record.created,
                                "level": record.levelname,
                                "correlation_id": getattr(record, "correlation_id", "no-correlation-id"),
                                "logger": record.name,
                                "message": record.getMessage(),
                                "module": record.module,
                                "function": record.funcName,
                                "line": record.lineno,
                            }

                            if record.exc_info:
                                log_entry["exception"] = self.formatter.formatException(record.exc_info)

                            self.file_handler.emit(json.dumps(log_entry))
                        except Exception:
                            # Fallback to regular logging
                            self.file_handler.emit(record.getMessage())

                file_handler = JSONFileHandler(
                    f"{log_dir}/mcp_server.json",
                    maxBytes=10 * 1024 * 1024,
                    backupCount=5
                )
            else:
                file_handler.setFormatter(MCPFormatter())

            root_logger.addHandler(file_handler)

        except Exception as e:
            # Don't fail if file logging setup fails
            print(f"Warning: Could not setup file logging: {e}")

    # Reduce noise from some loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    return structlog.get_logger("mcp_server")


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (defaults to mcp_server)

    Returns:
        Structured logger instance
    """
    logger_name = name or "mcp_server"
    return structlog.get_logger(logger_name)


@contextmanager
def log_function_call(
    logger_name: str = None,
    operation: str = "function_call",
    include_args: bool = False,
    include_result: bool = False,
    log_level: str = "info"
):
    """
    Context manager for logging function calls.

    Args:
        logger_name: Logger name to use
        operation: Description of the operation
        include_args: Whether to log function arguments
        include_result: Whether to log function result
        log_level: Log level to use (info, debug, etc.)

    Usage:
        with log_function_call("my_function", "processing data"):
            result = process_data(data)
            return result
    """
    logger = get_logger(logger_name)
    log_method = getattr(logger, log_level.lower())

    def _serialize_value(value):
        """Serialize value for logging."""
        try:
            import json
            return json.dumps(value, default=str, ensure_ascii=False)
        except Exception:
            return str(value)[:200]  # Truncate if serialization fails

    def _format_args(args, kwargs):
        """Format arguments for logging."""
        if not include_args:
            return "()"

        parts = []
        if args:
            parts.append(f"args={_serialize_value(args)}")
        if kwargs:
            parts.append(f"kwargs={_serialize_value(kwargs)}")
        return f"({', '.join(parts)})"

    def _format_result(result):
        """Format result for logging."""
        if not include_result:
            return "result=<not_shown>"
        return f"result={_serialize_value(result)}"

    correlation_id = get_correlation_id()
    start_time = None

    try:
        import time
        start_time = time.time()

        if include_args:
            # For context manager, we can't easily get args/kwargs
            log_method(
                operation + " started",
                correlation_id=correlation_id
            )
        else:
            log_method(
                operation + " started",
                correlation_id=correlation_id
            )

        yield

    finally:
        if start_time:
            duration = (time.time() - start_time) * 1000
            log_method(
                operation + " completed",
                correlation_id=correlation_id,
                duration_ms=round(duration, 2)
            )
        else:
            log_method(
                operation + " completed",
                correlation_id=correlation_id
            )


class PerformanceLogger:
    """Specialized logger for performance-related events."""

    def __init__(self, name: str = "performance"):
        self.logger = get_logger(name)

    def log_slow_operation(self, operation: str, duration_ms: float, threshold_ms: float = 200):
        """Log slow operations."""
        if duration_ms > threshold_ms:
            self.logger.warning(
                "Slow operation detected",
                operation=operation,
                duration_ms=duration_ms,
                threshold_ms=threshold_ms,
                correlation_id=get_correlation_id()
            )

    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """Log performance metrics."""
        self.logger.info(
            "Performance metrics",
            **metrics,
            correlation_id=get_correlation_id()
        )

    def log_memory_usage(self, memory_mb: float, threshold_mb: float = 100):
        """Log memory usage if above threshold."""
        if memory_mb > threshold_mb:
            self.logger.warning(
                "High memory usage",
                memory_mb=memory_mb,
                threshold_mb=threshold_mb,
                correlation_id=get_correlation_id()
            )

    def log_concurrent_requests(self, current: int, max_concurrent: int):
        """Log concurrent request information."""
        if current > max_concurrent * 0.9:  # Alert at 90% capacity
            self.logger.warning(
                "High concurrent request load",
                current=current,
                max_concurrent=max_concurrent,
                utilization_percent=round((current / max_concurrent) * 100, 1),
                correlation_id=get_correlation_id()
            )


# Global logger instances
main_logger = get_logger("mcp_server")
performance_logger = PerformanceLogger()

# Convenience functions
def log_tool_call(tool_name: str, user_id: str = None, **kwargs):
    """Log MCP tool call."""
    main_logger.info(
        "MCP tool called",
        tool_name=tool_name,
        user_id=user_id,
        correlation_id=get_correlation_id(),
        **kwargs
    )


def log_tool_result(tool_name: str, success: bool, duration_ms: float, **kwargs):
    """Log MCP tool result."""
    main_logger.info(
        "MCP tool completed",
        tool_name=tool_name,
        success=success,
        duration_ms=duration_ms,
        correlation_id=get_correlation_id(),
        **kwargs
    )


def log_error(operation: str, error: Exception, **kwargs):
    """Log error with context."""
    main_logger.error(
        f"Error in {operation}",
        error_type=type(error).__name__,
        error_message=str(error),
        correlation_id=get_correlation_id(),
        **kwargs
    )


def log_jwt_validation(success: bool, user_id: str = None, **kwargs):
    """Log JWT validation result."""
    if success:
        main_logger.info(
            "JWT validation successful",
            user_id=user_id,
            correlation_id=get_correlation_id(),
            **kwargs
        )
    else:
        main_logger.warning(
            "JWT validation failed",
            correlation_id=get_correlation_id(),
            **kwargs
        )


def log_database_operation(operation: str, duration_ms: float, success: bool = True, **kwargs):
    """Log database operation."""
    log_method = main_logger.info if success else main_logger.error

    log_method(
        f"Database {operation}",
        duration_ms=duration_ms,
        success=success,
        correlation_id=get_correlation_id(),
        **kwargs
    )