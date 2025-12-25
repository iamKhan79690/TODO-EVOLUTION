# Multi-stage build for production-ready MCP Server application
# Following Phase IV Constitutional requirements

# Stage 1: Dependencies
FROM python:3.13-slim AS dependencies
# Add labels for constitutional compliance
LABEL maintainer="TODO Evolution Team" \
      version="1.0.0" \
      description="Dependencies stage for MCP server"

# Set environment variables for non-interactive builds
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim AS runtime
# Add labels for constitutional compliance
LABEL maintainer="TODO Evolution Team" \
      version="1.0.0" \
      description="Production MCP server runtime" \
      org.label-schema.name="todo-mcp-server" \
      org.label-schema.version="1.0.0" \
      org.label-schema.schema-version="1.0"

# Set environment variables for production
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/appuser/.local/bin:$PATH"

# Security: Create non-root user
RUN groupadd -r appuser --gid=1000 && \
    useradd -r -g appuser --uid=1000 --home-dir /home/appuser appuser && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /home/appuser

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code with proper ownership
COPY --chown=appuser:appuser . .

# Create necessary directories and set permissions
RUN mkdir -p /app/tmp /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables for the application
ENV HOST=0.0.0.0 \
    PORT=8001 \
    MCP_HTTP_PORT=8001 \
    LOG_LEVEL=INFO \
    PYTHONPATH=/app

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Graceful shutdown handling
STOPSIGNAL SIGTERM

# Start the application
CMD ["uvicorn", "http_server:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]