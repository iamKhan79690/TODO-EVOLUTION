# Quickstart Guide: MCP Server Implementation

**Date**: 2025-12-16
**Feature**: Complete MCP Server Implementation and Deployment
**Purpose**: Rapid development setup and deployment instructions

## Prerequisites

### System Requirements
- **Node.js**: 18.x or higher
- **Python**: 3.11 or higher
- **PostgreSQL**: 14.x or higher
- **Git**: For version control

### Required Accounts & Services
- **Google AI Studio**: Gemini API access (GEMINI_API_KEY)
- **OpenAI Account**: For OpenAI Agents SDK (OPENAI_API_KEY)
- **GitHub**: For code repository

## Development Environment Setup

### 1. Repository Setup
```bash
# Clone the repository
git clone https://github.com/your-username/TODO-Evolution.git
cd TODO-Evolution

# Create feature branch
git checkout -b 003-mcp-server-complete

# Install dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements.txt
```

### 2. Database Configuration
```bash
# Start PostgreSQL (Docker example)
docker run --name postgres-todo -e POSTGRES_PASSWORD=todoevolution -p 5432:5432 -d postgres:14

# Run database migrations
cd backend
python -m alembic upgrade head
```

### 3. Environment Configuration

#### Backend Environment (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:todoevolution@localhost:5432/todoevolution

# Authentication
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256

# External APIs
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# MCP Server Configuration
MCP_HTTP_PORT=8001
TRANSPORT=http

# Development
DEBUG=true
ENVIRONMENT=development
```

#### Frontend Environment (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_MCP_URL=http://localhost:8001

# Optional
NEXT_PUBLIC_APP_NAME=TODO Evolution
NEXT_PUBLIC_APP_VERSION=3.0.0
```

## Quick Development Workflow

### 1. Start All Services
```bash
# Terminal 1: Start FastAPI Backend
cd backend
python src/main.py
# Expected: Server running on http://0.0.0.0:8000

# Terminal 2: Start MCP Server
cd backend
python src/mcp_server/main.py
# Expected: MCP server listening on port 8001

# Terminal 3: Start Frontend
cd frontend
npm run dev
# Expected: Next.js server on http://localhost:3000
```

### 2. Verify Deployment
```bash
# Check backend health
curl http://localhost:8000/health

# Check MCP server health
curl http://localhost:8001/health

# Check frontend
curl http://localhost:3000
```

### 3. Test Authentication
```bash
# Register a new user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'

# Login and get JWT token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## MCP Server Testing

### 1. Direct Tool Testing
```bash
# Test add_task tool
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Test task", "description": "Test description"}'

# Test list_tasks tool
curl -X GET http://localhost:8001/tools/list_tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test complete_task tool
curl -X POST http://localhost:8001/tools/complete_task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"task_id": 1}'
```

### 2. AI Agent Integration Testing
```bash
# Test AI agent with natural language
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "Add a task to buy groceries"}'

# Test conversation state
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "Show me all my tasks"}'
```

## Troubleshooting Guide

### Common Issues

#### 1. MCP Server Won't Start
```bash
# Check port availability
netstat -an | grep 8001

# Check Python dependencies
pip install -r requirements.txt

# Verify environment variables
echo $MCP_HTTP_PORT
```

#### 2. Authentication Failures
```bash
# Verify JWT secret is set
echo $BETTER_AUTH_SECRET

# Check database connection
python -c "from src.database import engine; print(engine.url)"
```

#### 3. Frontend Connection Issues
```bash
# Verify CORS configuration
curl -H "Origin: http://localhost:3000" http://localhost:8000/health

# Check environment variables
cat frontend/.env.local
```

### Debug Mode Setup
```bash
# Enable debug logging
export DEBUG=true
export ENVIRONMENT=development

# Run with verbose output
python src/mcp_server/main.py --log-level DEBUG
```

## Performance Optimization

### Development Performance
```bash
# Enable hot reload for frontend
cd frontend
npm run dev -- --turbo

# Use in-memory database for testing
DATABASE_URL=sqlite:///./test.db python src/main.py
```

### MCP Server Optimization
```bash
# Configure connection pooling
export DB_POOL_SIZE=10
export DB_MAX_OVERFLOW=20

# Enable response caching
export MCP_CACHE_TTL=300
```

## Production Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps
docker-compose logs mcp-server
```

### Environment Configuration
```bash
# Production environment variables
export ENVIRONMENT=production
export DEBUG=false
export JWT_ALGORITHM=HS256
export BETTER_AUTH_SECRET=your-production-secret-here
```

## Verification Checklist

### Pre-deployment Checks
- [ ] All services start without errors
- [ ] Database migrations applied successfully
- [ ] JWT authentication works correctly
- [ ] MCP tools respond with valid JSON
- [ ] AI agent can call MCP tools
- [ ] Frontend can communicate with all services
- [ ] CORS configuration is working
- [ ] Error handling is functional
- [ ] Logging is configured and working
- [ ] Performance requirements are met

### Post-deployment Monitoring
```bash
# Monitor service health
curl http://localhost:8001/health
curl http://localhost:8000/health
curl http://localhost:3000/api/health

# Check logs for errors
tail -f logs/mcp-server.log
tail -f logs/application.log
```

## Development Tips

### 1. Iterative Development
- Start with one MCP tool at a time
- Test each tool individually before integration
- Use the AI agent to test natural language processing
- Verify database operations after each tool call

### 2. Testing Strategy
- Unit test each MCP tool function
- Integration test with AI agent
- End-to-end test with frontend
- Performance test under load

### 3. Debugging Tools
```bash
# Database query inspection
export DATABASE_ECHO=true

# MCP request/response logging
export MCP_LOG_LEVEL=DEBUG

# AI agent trace logging
export AGENT_TRACE_ENABLED=true
```

## Next Steps

After completing the quickstart:

1. **Run the test suite**: `npm run test` (frontend) and `pytest` (backend)
2. **Verify all MCP tools**: Use the tool testing examples above
3. **Test AI agent integration**: Try natural language commands
4. **Check performance**: Verify response time requirements
5. **Review logs**: Ensure all components are communicating properly

## Support Resources

### Documentation Links
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [OpenAI Agents SDK](https://github.com/openai/agents-sdk)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

### Common Commands Reference
```bash
# Reset development environment
git clean -fd && git checkout .
npm install && pip install -r requirements.txt

# Recreate database
dropdb todoevolution && createdb todoevolution
python -m alembic upgrade head

# Full service restart
pkill -f "python.*main.py" && pkill -f "next"
npm run dev & python src/main.py & python src/mcp_server/main.py &
```

This quickstart guide provides everything needed to get the MCP server implementation running and tested in development and production environments.