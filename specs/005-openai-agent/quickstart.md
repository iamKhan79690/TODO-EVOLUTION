# Quickstart Guide: OpenAI Agent Architecture

**Date**: 2025-01-12
**Feature**: OpenAI Agent Architecture
**Purpose**: Quick setup and development guide for the task management agent

## Prerequisites

### System Requirements

- Python 3.11+
- PostgreSQL 14+
- OpenAI API key with GPT-4o access
- Existing TODO-Evolution backend with MCP tools
- Node.js 18+ (for development tools)

### Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd TODO-Evolution

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-agent.txt  # Agent-specific dependencies

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/todo_evolution

# JWT Configuration
JWT_SECRET=your_jwt_secret

# Agent Configuration
AGENT_MAX_CONVERSATION_TURNS=50
AGENT_CONTEXT_RETENTION_DAYS=30
AGENT_RESPONSE_TIMEOUT_MS=2000

# MCP Tool Configuration
MCP_SERVER_URL=http://localhost:8050
MCP_TIMEOUT_MS=1000
```

## Installation

### 1. Database Setup

```bash
# Run database migrations
python -m alembic upgrade head

# Create agent-specific tables
python scripts/create_agent_tables.py
```

### 2. Agent Service Setup

```bash
# Navigate to agent directory
cd src/agents/task_agent

# Install agent dependencies
pip install -r requirements.txt

# Run initial setup
python setup_agent.py
```

### 3. MCP Tool Integration

```bash
# Ensure MCP server is running
cd mcp_server
python main.py

# Test tool integration
python scripts/test_mcp_integration.py
```

## Development

### Running the Agent Service

```bash
# Development server
python src/agents/task_agent/main.py

# With auto-reload
uvicorn src.agents.task_agent.main:app --reload --host 0.0.0.0 --port 8001
```

### Testing the Agent

```bash
# Run unit tests
pytest tests/agent/unit/

# Run integration tests
pytest tests/agent/integration/

# Run conversation tests
pytest tests/agent/conversation/
```

### Example Usage

```python
from src.agents.task_agent.client import AgentClient

# Initialize agent client
client = AgentClient(
    base_url="http://localhost:8001",
    jwt_token="your_jwt_token"
)

# Start a conversation
response = await client.chat(
    user_id="user-uuid",
    message="Create a task to review the project proposal by Friday at 2 PM"
)

print(response["agent_response"])
```

## Architecture Overview

### Core Components

1. **Agent Core**: Main agent logic using OpenAI Agents SDK
2. **Conversation Manager**: Handles conversation context and persistence
3. **Intent Processor**: Extracts user intents and parameters
4. **Tool Wrapper**: Integrates with existing MCP tools
5. **Error Handler**: Manages errors and recovery scenarios

### Directory Structure

```
src/agents/task_agent/
├── main.py                 # FastAPI application entry point
├── core/
│   ├── __init__.py
│   ├── agent.py           # Main agent implementation
│   ├── conversation.py    # Conversation management
│   └── intent.py          # Intent processing
├── tools/
│   ├── __init__.py
│   ├── mcp_wrapper.py     # MCP tool integration
│   └── parameter_extractor.py
├── models/
│   ├── __init__.py
│   ├── conversation.py    # Conversation data models
│   └── intent.py          # Intent data models
├── services/
│   ├── __init__.py
│   ├── conversation_service.py
│   ├── intent_service.py
│   └── tool_service.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conversation/
└── requirements.txt
```

## API Usage

### Basic Chat Endpoint

```bash
curl -X POST "http://localhost:8001/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid",
    "message": "Create a high priority task: Call the client about budget issues",
    "jwt_token": "your-jwt-token"
  }'
```

### Response Format

```json
{
  "success": true,
  "data": {
    "conversation_id": "conv-uuid",
    "agent_response": "I've created a high priority task for you to call the client about budget issues.",
    "actions_taken": [
      {
        "type": "tool_call",
        "tool_name": "add_task",
        "parameters": {
          "title": "Call the client about budget issues",
          "priority": "high"
        },
        "result": {
          "task_id": 123,
          "success": true
        },
        "confirmation_required": false
      }
    ],
    "suggested_followup": "Would you like me to set a due date for this task?",
    "context_summary": null
  }
}
```

## Configuration

### Agent Configuration

```python
# src/agents/task_agent/config.py
class AgentConfig:
    # OpenAI Settings
    OPENAI_MODEL = "gpt-4o"
    OPENAI_TEMPERATURE = 0.1
    OPENAI_MAX_TOKENS = 1000

    # Conversation Settings
    MAX_CONVERSATION_TURNS = 50
    CONTEXT_RETENTION_DAYS = 30
    CONTEXT_SUMMARY_THRESHOLD = 40

    # Performance Settings
    RESPONSE_TIMEOUT_MS = 2000
    MCP_TIMEOUT_MS = 1000
    MAX_CONCURRENT_REQUESTS = 100

    # Security Settings
    JWT_SECRET = os.getenv("JWT_SECRET")
    MAX_MESSAGE_LENGTH = 2000
    RATE_LIMIT_PER_MINUTE = 100
```

### Tool Registration

```python
# src/agents/task_agent/tools/registry.py
from .mcp_wrapper import MCPToolWrapper

# Register MCP tools with the agent
TOOL_REGISTRY = {
    "add_task": MCPToolWrapper("add_task", "http://localhost:8050"),
    "list_tasks": MCPToolWrapper("list_tasks", "http://localhost:8050"),
    "complete_task": MCPToolWrapper("complete_task", "http://localhost:8050"),
    "update_task": MCPToolWrapper("update_task", "http://localhost:8050"),
    "delete_task": MCPToolWrapper("delete_task", "http://localhost:8050"),
}
```

## Monitoring and Debugging

### Logging Configuration

```python
# src/agents/task_agent/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### Health Checks

```bash
# Agent health check
curl "http://localhost:8001/health"

# Check MCP tool connectivity
curl "http://localhost:8001/health/mcp-tools"

# Check database connectivity
curl "http://localhost:8001/health/database"
```

### Performance Monitoring

```bash
# View agent metrics
curl "http://localhost:8001/metrics"

# Conversation statistics
curl "http://localhost:8001/api/v1/agent/stats"
```

## Troubleshooting

### Common Issues

1. **Agent Not Responding**
   ```bash
   # Check agent service status
   curl "http://localhost:8001/health"

   # Check logs
   tail -f logs/agent.log
   ```

2. **MCP Tool Integration Issues**
   ```bash
   # Test MCP server
   curl "http://localhost:8050/health"

   # Test tool connectivity
   python scripts/test_mcp_tools.py
   ```

3. **Database Connection Issues**
   ```bash
   # Test database connection
   python scripts/test_database.py

   # Check connection pool status
   curl "http://localhost:8001/health/database"
   ```

4. **Conversation Context Issues**
   ```bash
   # Check conversation storage
   python scripts/test_conversation_persistence.py

   # Verify database tables
   python scripts/verify_agent_tables.py
   ```

### Debug Mode

```bash
# Run agent in debug mode
DEBUG=true python src/agents/task_agent/main.py

# Enable verbose logging
LOG_LEVEL=DEBUG python src/agents/task_agent/main.py
```

## Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/

EXPOSE 8001
CMD ["uvicorn", "src.agents.task_agent.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Environment Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  agent:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - mcp-server
```

## Contributing

### Development Workflow

1. Create feature branch from `main`
2. Implement changes with tests
3. Run full test suite
4. Submit pull request for review

### Code Standards

- Follow PEP 8 for Python code
- Use type hints for all functions
- Include docstrings for all modules and functions
- Write comprehensive tests for new features
- Use structlog for structured logging

### Testing Guidelines

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/agents/task_agent

# Run specific test categories
pytest tests/agent/unit/
pytest tests/agent/integration/
pytest tests/agent/conversation/
```