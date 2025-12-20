# MCP Server Quickstart Guide

**Feature**: 002-mcp-server
**Date**: 2025-01-12
**Target Audience**: Developers implementing Phase III AI Chatbot integration

---

## Overview

This guide provides step-by-step instructions for setting up, running, and integrating the Task Management MCP server with the Phase III AI Chatbot. The MCP server exposes 5 core tools for task management operations.

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Database**: PostgreSQL (Neon recommended)
- **Authentication**: Better Auth with JWT tokens
- **Memory**: Minimum 100MB available per server instance
- **Network**: Internet access for package installation

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@neon.tech/dbname

# Authentication (must match FastAPI backend)
JWT_SECRET=your-jwt-secret-key-here
JWT_ALGORITHM=RS256

# MCP Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8050
TRANSPORT=stdio

# Performance Tuning
MAX_CONCURRENT_TOOLS=100
CONNECTION_POOL_SIZE=20
CACHE_TTL=300

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Development
DEBUG=false
ENVIRONMENT=production
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/your-org/TODO-Evolution.git
cd TODO-Evolution
```

### 2. Create Virtual Environment

```bash
# Using Python venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Using uv (recommended)
uv venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install MCP SDK and dependencies
pip install "mcp[cli]"

# Install additional dependencies
pip install fastapi sqlmodel asyncpg python-jose uvicorn
pip install psutil  # For memory monitoring

# Using requirements.txt (if available)
pip install -r requirements-mcp.txt

# Using uv (recommended)
uv add "mcp[cli]" fastapi sqlmodel asyncpg python-jose uvicorn psutil
```

### 4. Verify Installation

```bash
# Check MCP installation
python -c "import mcp; print(f'MCP version: {mcp.__version__}')"

# Test database connection
python -c "
from sqlmodel import create_engine
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    print('Database connection successful')
except Exception as e:
    print(f'Database error: {e}')
"
```

---

## Configuration

### 1. Database Setup

Ensure PostgreSQL database is accessible and has the required schema:

```bash
# Run database migrations (if using Alembic)
cd backend
alembic upgrade head

# Or create tables directly
python -c "
from src.database import create_tables
import asyncio
asyncio.run(create_tables())
"
```

### 2. JWT Authentication

Configure JWT validation to match your FastAPI backend:

```python
# config/jwt_config.py
import os
from jwt import PyJWT

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "RS256")

def validate_jwt_token(token: str) -> dict:
    """Validate JWT token and extract user context."""
    try:
        payload = PyJWT().decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return {
            "user_id": payload["sub"],
            "email": payload.get("email", ""),
            "name": payload.get("name", "")
        }
    except Exception as e:
        raise ValueError(f"Invalid JWT token: {e}")
```

### 3. Performance Optimization

Configure connection pooling and caching:

```python
# config/database_config.py
import os
from asyncpg import create_pool
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")

async def create_database_pool():
    """Create optimized database connection pool."""
    return await create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=20,
        max_queries=50000,
        max_inactive_connection_lifetime=300,
        command_timeout=10
    )

def create_async_engine():
    """Create SQLAlchemy async engine."""
    return create_async_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600
    )
```

---

## Running the MCP Server

### 1. Development Mode

```bash
# Run with default configuration
python mcp_server/main.py

# Run with specific configuration
TRANSPORT=sse python mcp_server/main.py

# Run with debugging enabled
DEBUG=true python mcp_server/main.py
```

### 2. Production Mode

```bash
# Using uvicorn (for SSE transport)
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8050

# Using gunicorn
gunicorn mcp_server.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8050

# Using Docker
docker build -t todo-mcp-server .
docker run -p 8050:8050 --env-file .env todo-mcp-server
```

### 3. Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "todo-task-manager": {
      "command": "python",
      "args": ["mcp_server/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:password@neon.tech/dbname",
        "JWT_SECRET": "your-jwt-secret-key-here"
      }
    }
  }
}
```

---

## Testing the MCP Server

### 1. MCP Inspector Testing

```bash
# Run MCP inspector for interactive testing
mcp-inspector python mcp_server/main.py

# Test specific tool
mcp-inspector python mcp_server/main.py --tool add_task
```

### 2. Manual Tool Testing

```python
# test_mcp_server.py
import asyncio
import jwt
from datetime import datetime, timedelta

async def test_mcp_tools():
    """Test all MCP server tools."""

    # Generate test JWT token
    test_token = jwt.encode(
        {
            "sub": "123",
            "email": "test@example.com",
            "name": "Test User",
            "exp": datetime.utcnow() + timedelta(hours=1)
        },
        "your-test-secret",
        algorithm="HS256"
    )

    # Test add_task
    result = await call_mcp_tool("add_task", {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "medium",
        "jwt_token": test_token
    })
    print("add_task result:", result)

    # Test list_tasks
    result = await call_mcp_tool("list_tasks", {
        "jwt_token": test_token,
        "limit": 10
    })
    print("list_tasks result:", result)

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
```

### 3. Integration Testing

```bash
# Run comprehensive test suite
python -m pytest tests/mcp_server/ -v

# Run with coverage
pytest --cov=mcp_server tests/ -v

# Run performance tests
python -m pytest tests/performance/ -v
```

---

## MCP Tool Usage Examples

### 1. Add Task

```python
# Create a new task
result = await mcp_server.call_tool("add_task", {
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for MCP server",
    "priority": "high",
    "due_date": "2025-01-15T17:00:00Z",
    "jwt_token": "user-jwt-token-here"
})

# Expected response
{
    "success": true,
    "data": {
        "id": 123,
        "title": "Complete project documentation",
        "description": "Write comprehensive docs for MCP server",
        "priority": "high",
        "due_date": "2025-01-15T17:00:00Z",
        "is_completed": false,
        "created_at": "2025-01-12T10:30:00Z",
        "updated_at": "2025-01-12T10:30:00Z",
        "user_id": 42
    },
    "message": "Task created successfully",
    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
    "execution_time_ms": 45,
    "timestamp": "2025-01-12T10:30:00Z"
}
```

### 2. List Tasks

```python
# Get all pending tasks
result = await mcp_server.call_tool("list_tasks", {
    "status": "pending",
    "priority": "high",
    "limit": 20,
    "offset": 0,
    "jwt_token": "user-jwt-token-here"
})

# Expected response
{
    "success": true,
    "data": {
        "tasks": [
            {
                "id": 123,
                "title": "Complete project documentation",
                "priority": "high",
                "is_completed": false,
                "created_at": "2025-01-12T10:30:00Z"
            }
        ],
        "total_count": 1,
        "has_more": false
    },
    "correlation_id": "550e8400-e29b-41d4-a716-446655440001",
    "execution_time_ms": 23,
    "timestamp": "2025-01-12T10:30:00Z"
}
```

### 3. Complete Task

```python
# Mark task as completed
result = await mcp_server.call_tool("complete_task", {
    "task_id": 123,
    "jwt_token": "user-jwt-token-here"
})

# Expected response
{
    "success": true,
    "data": {
        "id": 123,
        "title": "Complete project documentation",
        "is_completed": true,
        "completed_at": "2025-01-12T11:00:00Z",
        "updated_at": "2025-01-12T11:00:00Z"
    },
    "message": "Task marked as completed",
    "correlation_id": "550e8400-e29b-41d4-a716-446655440002",
    "execution_time_ms": 18,
    "timestamp": "2025-01-12T11:00:00Z"
}
```

---

## Integration with Phase III AI Chatbot

### 1. Token Exchange

Configure the AI Chatbot to obtain JWT tokens:

```python
# phase3_integration.py
import requests

def get_jwt_token(user_credentials):
    """Obtain JWT token from Phase III authentication."""
    response = requests.post(
        "https://your-api.com/auth/login",
        json=user_credentials
    )
    return response.json()["access_token"]

# Use in MCP server calls
jwt_token = get_jwt_token({
    "email": "user@example.com",
    "password": "user-password"
})
```

### 2. Error Handling Integration

```python
# phase3_error_handling.py
class MCPClient:
    def __init__(self, mcp_server_url):
        self.server_url = mcp_server_url

    async def call_tool_with_retry(self, tool_name, params, max_retries=3):
        """Call MCP tool with retry logic."""
        for attempt in range(max_retries):
            try:
                return await self.call_tool(tool_name, params)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                # Handle specific error cases
                if "TOKEN_EXPIRED" in str(e):
                    params["jwt_token"] = await self.refresh_jwt_token()

                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 3. Performance Monitoring

```python
# phase3_monitoring.py
import time
from typing import Dict

class MCPMetrics:
    def __init__(self):
        self.metrics = {
            "tool_calls": 0,
            "total_response_time": 0,
            "error_count": 0,
            "cache_hits": 0
        }

    def record_tool_call(self, tool_name: str, response_time: float, success: bool):
        """Record MCP tool call metrics."""
        self.metrics["tool_calls"] += 1
        self.metrics["total_response_time"] += response_time

        if not success:
            self.metrics["error_count"] += 1

    def get_performance_summary(self) -> Dict:
        """Get current performance metrics."""
        if self.metrics["tool_calls"] == 0:
            return {"status": "No data"}

        return {
            "total_calls": self.metrics["tool_calls"],
            "avg_response_time": self.metrics["total_response_time"] / self.metrics["tool_calls"],
            "error_rate": self.metrics["error_count"] / self.metrics["tool_calls"],
            "cache_hit_rate": self.metrics["cache_hits"] / max(self.metrics["tool_calls"], 1)
        }
```

---

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   ```bash
   # Check JWT token format
   python -c "import jwt; print(jwt.decode(token, options={'verify_signature': False}))"
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   python -c "
   import asyncpg
   import asyncio

   async def test_db():
       try:
           conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
           print('Database connected successfully')
           await conn.close()
       except Exception as e:
           print(f'Database error: {e}')

   asyncio.run(test_db())
   "
   ```

3. **Performance Issues**
   ```bash
   # Monitor resource usage
   python -c "
   import psutil
   print(f'Memory usage: {psutil.virtual_memory().percent}%')
   print(f'CPU usage: {psutil.cpu_percent()}%')
   "
   ```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
# Enable debug logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable SQL query logging (for development)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Health Checks

Monitor server health:

```bash
# Check MCP server status
curl http://localhost:8050/health

# Check performance metrics
curl http://localhost:8050/metrics

# Test specific tool
curl -X POST http://localhost:8050/tools/list_tasks \
  -H "Content-Type: application/json" \
  -d '{"jwt_token": "test-token"}'
```

---

## Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-mcp.txt .
RUN pip install --no-cache-dir -r requirements-mcp.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mcpuser
USER mcpuser

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/health || exit 1

# Run application
CMD ["python", "mcp_server/main.py"]
```

### Environment Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8050:8050"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/tododb
      - JWT_SECRET=your-production-jwt-secret
      - LOG_LEVEL=INFO
      - ENVIRONMENT=production
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=tododb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## Next Steps

1. **Customization**: Modify tool schemas for specific use cases
2. **Caching**: Implement Redis for distributed caching
3. **Monitoring**: Set up comprehensive monitoring and alerting
4. **Scaling**: Configure load balancing for multiple instances
5. **Security**: Implement additional security measures as needed

---

*This quickstart guide provides everything needed to get the MCP server running and integrated with Phase III AI Chatbot. For additional support, refer to the full specification and API documentation.*