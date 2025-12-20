# Implementation Plan: Complete MCP Server Implementation and Deployment

**Branch**: `003-mcp-server-complete` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-mcp-server-complete/spec.md`

## Summary

The MCP server implementation requires completing the existing FastMCP server architecture to provide HTTP transport on port 8001 with five task management tools. The implementation leverages existing FastAPI authentication, direct SQLModel database integration, and structured error handling to meet the Phase III AI chatbot requirements. Research confirms FastMCP natively supports HTTP transport, making this a straightforward completion of missing components.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastMCP, SQLModel, OpenAI Agents SDK, FastAPI (existing)
**Storage**: PostgreSQL (existing database with Task and User entities)
**Testing**: pytest, HTTP-based integration tests, AI agent end-to-end tests
**Target Platform**: Linux server (HTTP service on port 8001)
**Project Type**: Web application (backend microservice)
**Performance Goals**: <500ms tool execution, 99.9% uptime, 50+ concurrent requests
**Constraints**: JWT authentication required, user isolation enforced, structured logging
**Scale/Scope**: Single MCP server supporting multiple AI agents and users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Architecture Principle**: Leverages existing FastAPI and SQLModel foundation
✅ **Security Principle**: Maintains JWT authentication and user isolation
✅ **Performance Principle**: Direct database access for optimal response times
✅ **Simplicity Principle**: Uses FastMCP native HTTP transport (no custom server)
✅ **Testing Principle**: Comprehensive test coverage with unit, integration, and e2e tests

## Project Structure

### Documentation (this feature)

```text
specs/003-mcp-server-complete/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command) ✅ COMPLETED
├── data-model.md        # Phase 1 output (/sp.plan command) ✅ COMPLETED
├── quickstart.md        # Phase 1 output (/sp.plan command) ✅ COMPLETED
├── contracts/           # Phase 1 output (/sp.plan command) ✅ COMPLETED
│   └── mcp-tools.json   # OpenAPI specification for MCP tools
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── database.py          # Existing database configuration
│   ├── models/              # Existing SQLModel entities
│   │   ├── user.py
│   │   └── task.py
│   ├── auth.py              # Existing JWT authentication
│   ├── mcp_server/          # MCP server implementation (TO BE COMPLETED)
│   │   ├── __init__.py
│   │   ├── main.py          # FastMCP server entry point
│   │   ├── tools.py         # MCP tool implementations
│   │   ├── auth.py          # JWT authentication middleware
│   │   └── services.py      # Database service layer
│   ├── api/
│   │   └── chat.py          # Existing AI agent integration
│   └── main.py              # FastAPI backend (existing)
└── tests/
    ├── unit/                # Unit tests for MCP tools
    ├── integration/         # Integration tests with database
    └── e2e/                 # End-to-end AI agent tests

frontend/ (existing, no changes required)
├── src/
│   ├── components/
│   │   └── chat/            # Existing chat interface
│   └── pages/
│       └── dashboard.tsx    # Existing dashboard
```

**Structure Decision**: Web application with separate MCP server microservice. The MCP server (`backend/src/mcp_server/`) is a new Python module that integrates with existing FastAPI authentication and database systems while running as an independent HTTP service on port 8001.

## Complexity Tracking

No constitution violations detected. The implementation follows existing architectural patterns and leverages current infrastructure without introducing unnecessary complexity.

## Architecture Overview

### System Boundaries

#### In Scope
- Complete MCP server implementation with HTTP transport on port 8001
- Five MCP task management tools (add_task, list_tasks, complete_task, update_task, delete_task)
- JWT authentication integration with existing FastAPI backend
- Direct database connectivity using shared SQLModel entities
- Comprehensive error handling and structured logging
- Performance optimization for <500ms tool execution
- AI agent integration for natural language task management

#### Out of Scope
- Frontend UI changes (existing interface supports MCP integration)
- Database schema modifications (uses existing Task and User entities)
- Authentication system changes (leverages existing JWT infrastructure)
- New external API integrations (uses existing Gemini and OpenAI APIs)

### External Dependencies

| Dependency | System | Owner | Integration Point | Criticality |
|------------|--------|-------|-------------------|-------------|
| PostgreSQL Database | Database Layer | Development Team | Shared SQLModel entities | Critical |
| FastAPI Backend | Authentication | Development Team | JWT token validation | Critical |
| OpenAI Agents SDK | AI Framework | OpenAI | Agent tool integration | Critical |
| Gemini API | LLM Service | Google | Chat completion | Critical |
| FastMCP Framework | MCP Server | FastMCP | Core MCP functionality | Critical |

## Key Architectural Decisions

### 1. MCP Transport Layer
**Decision**: Use FastMCP HTTP transport on port 8001
**Rationale**: Native HTTP support eliminates need for custom server implementation
**Trade-offs**:
- ✅ Simplified deployment and debugging
- ✅ Direct integration with web architecture
- ❌ Requires additional port management
- ❌ No built-in encryption (handled by JWT)

### 2. Authentication Strategy
**Decision**: Unified JWT validation with existing FastAPI backend
**Rationale**: Maintains security consistency and reduces duplication
**Trade-offs**:
- ✅ Single source of truth for authentication
- ✅ Consistent token lifecycle management
- ❌ Dependency on backend availability for auth validation
- ❌ Shared secret key management

### 3. Database Integration
**Decision**: Direct SQLModel database access from MCP server
**Rationale**: Eliminates HTTP round trips and ensures data consistency
**Trade-offs**:
- ✅ Optimal performance for tool operations
- ✅ Atomic transactions and data integrity
- ❌ Tight coupling with database schema
- ❌ Requires database connection management

## Interface Specifications

### MCP Tool Endpoints

#### Base Configuration
- **Base URL**: `http://localhost:8001`
- **Authentication**: Bearer token (JWT) in Authorization header
- **Content-Type**: `application/json`
- **Response Format**: Structured JSON with correlation IDs

#### Tool Contracts

##### add_task
```yaml
Endpoint: POST /tools/add_task
Authentication: Required (JWT)
Parameters:
  - title: string (required, max 255 chars)
  - description: string (optional, max 2000 chars)
  - priority: enum (low|medium|high|urgent, default: medium)
  - due_date: string (ISO 8601 datetime, optional)
Response:
  success: boolean
  data: { task: Task object }
  correlation_id: string
```

##### list_tasks
```yaml
Endpoint: GET /tools/list_tasks
Authentication: Required (JWT)
Parameters:
  - status: enum (pending|in_progress|completed|cancelled|all, default: all)
  - limit: integer (default: 20, max: 100)
  - offset: integer (default: 0)
Response:
  success: boolean
  data: { tasks: Task[] }
  correlation_id: string
```

##### complete_task
```yaml
Endpoint: POST /tools/complete_task
Authentication: Required (JWT)
Parameters:
  - task_id: integer (required)
Response:
  success: boolean
  data: { task: Task object }
  correlation_id: string
```

##### update_task
```yaml
Endpoint: POST /tools/update_task
Authentication: Required (JWT)
Parameters:
  - task_id: integer (required)
  - updates: object (optional fields: title, description, priority, due_date)
Response:
  success: boolean
  data: { task: Task object }
  correlation_id: string
```

##### delete_task
```yaml
Endpoint: DELETE /tools/delete_task
Authentication: Required (JWT)
Parameters:
  - task_id: integer (required)
Response:
  success: boolean
  data: { message: string }
  correlation_id: string
```

### Error Handling Specification

#### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Valid JWT token required for tool access",
    "details": {}
  },
  "correlation_id": "uuid-v4"
}
```

#### Error Taxonomy
| Error Code | HTTP Status | Description | Retry Strategy |
|------------|-------------|-------------|----------------|
| AUTHENTICATION_REQUIRED | 401 | Missing or invalid JWT | Do not retry |
| AUTHORIZATION_DENIED | 403 | User cannot access resource | Do not retry |
| VALIDATION_ERROR | 400 | Invalid input parameters | Fix and retry |
| TASK_NOT_FOUND | 404 | Task does not exist | Do not retry |
| DATABASE_ERROR | 500 | Database operation failed | Exponential backoff |
| INTERNAL_ERROR | 500 | Server error | Exponential backoff |

## Non-Functional Requirements

### Performance Requirements

#### Response Time Targets
- **Tool Execution**: <500ms (95th percentile)
- **Authentication Validation**: <50ms
- **Database Operations**: <200ms
- **Server Startup**: <10 seconds
- **Health Checks**: <100ms

#### Concurrency Requirements
- **Concurrent Tool Requests**: 50+ simultaneous
- **Database Connection Pool**: 10-20 connections
- **Request Throughput**: 100+ requests/second
- **Memory Usage**: <512MB for MCP server

### Reliability Requirements

#### Service Level Objectives (SLOs)
- **Tool Availability**: 99.9% uptime
- **Error Rate**: <0.1% for authenticated requests
- **Data Consistency**: 100% (ACID transactions)
- **Response Time**: 95% of requests <500ms

#### Error Budgets
- **Monthly Downtime**: <43.2 minutes
- **Failed Requests**: <432 per 432,000 requests
- **Response Time Violations**: <21,600 slow requests

### Security Requirements

#### Authentication & Authorization
- **JWT Token Validation**: HS256 algorithm
- **Token Expiration**: 24 hours
- **User Isolation**: Database-level filtering
- **Audit Logging**: All tool operations with user context

#### Data Protection
- **Input Validation**: Pydantic model validation
- **SQL Injection Prevention**: SQLModel parameterized queries
- **CORS Configuration**: Allow frontend origin only
- **Secure Headers**: X-Content-Type-Options, etc.

## Data Management

### Database Schema Utilization

#### Primary Entities
- **User**: Authentication and task ownership (existing)
- **Task**: Core task entity with lifecycle management (existing)
- **ToolOperation**: Audit trail for MCP operations (new)

#### Connection Management
```python
# Database configuration
DATABASE_URL = "postgresql://user:pass@localhost:5432/todoevolution"
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30

# Connection pattern
async with get_db_session() as session:
    # Database operations
    await session.commit()
```

### Data Integrity
- **Foreign Key Constraints**: Enforced at database level
- **Transaction Atomicity**: All tool operations in transactions
- **Soft Delete**: Tasks marked deleted, not physically removed
- **Audit Trail**: Complete operation logging

## Operational Readiness

### Observability

#### Logging Strategy
```python
# Structured logging with correlation
logger.info(
    "Tool operation completed",
    extra={
        "tool_name": "add_task",
        "user_id": 123,
        "correlation_id": "uuid",
        "execution_time_ms": 150,
        "success": True
    }
)
```

#### Metrics Collection
- **Tool Execution Times**: Histogram by tool type
- **Request Rates**: Counter by endpoint and status
- **Error Rates**: Counter by error type
- **Database Performance**: Connection pool metrics

#### Health Checks
```yaml
Endpoint: GET /health
Response Format:
  status: "healthy" | "degraded" | "unhealthy"
  checks:
    database: "ok" | "error"
    authentication: "ok" | "error"
    memory_usage: percentage
  uptime: seconds
```

### Deployment Strategy

#### Configuration Management
```bash
# Required environment variables
TRANSPORT=http
MCP_HTTP_PORT=8001
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=shared-secret
GEMINI_API_KEY=gemini-key
OPENAI_API_KEY=openai-key
```

#### Process Management
- **Process Supervisor**: systemd or equivalent
- **Graceful Shutdown**: Handle SIGTERM, complete in-flight requests
- **Health Monitoring**: Periodic health checks
- **Log Rotation**: Daily log file rotation

### Monitoring & Alerting

#### Alert Thresholds
- **Error Rate**: >1% for 5 minutes
- **Response Time**: >1 second for 5 minutes
- **Database Connections**: >90% pool utilization
- **Memory Usage**: >80% available memory

#### Runbooks
- **Service Restart**: Graceful restart procedure
- **Database Issues**: Connection troubleshooting
- **Authentication Failures**: JWT token validation
- **Performance Degradation**: Bottleneck identification

## Risk Analysis & Mitigation

### Top 3 Technical Risks

#### 1. Database Connection Exhaustion
**Risk**: High concurrent load exhausts connection pool
**Blast Radius**: MCP server unavailable, tool failures
**Mitigation**:
- Connection pooling with overflow configuration
- Circuit breaker pattern for database failures
- Monitoring and alerting on pool utilization
- Graceful degradation when database unavailable

#### 2. JWT Token Synchronization
**Risk**: Token validation inconsistencies between services
**Blast Radius**: Authentication failures, security vulnerabilities
**Mitigation**:
- Shared secret key via environment variables
- Consistent validation algorithm (HS256)
- Token blacklist synchronization
- Regular secret rotation procedures

#### 3. MCP Tool Performance Bottlenecks
**Risk**: Slow tool operations affecting user experience
**Blast Radius**: Poor AI agent responsiveness
**Mitigation**:
- Database query optimization with proper indexes
- Response time monitoring and alerting
- Tool timeout configuration
- Performance testing under load

### Implementation Risks

#### FastMCP Framework Compatibility
**Risk**: HTTP transport support may be limited or unstable
**Mitigation**: Verify FastMCP version compatibility during development

#### Port Conflicts
**Risk**: Port 8001 may be unavailable in deployment environment
**Mitigation**: Document port requirements and provide configuration options

#### API Contract Breaking
**Risk**: Changes to tool interfaces may break AI agent integration
**Mitigation**: Version API contracts and maintain backward compatibility

## Implementation Validation

### Definition of Done

#### Functional Requirements
- [ ] All 5 MCP tools implemented and tested
- [ ] JWT authentication working for all endpoints
- [ ] User isolation enforced for all operations
- [ ] Structured error handling with correlation IDs
- [ ] Database consistency maintained

#### Performance Requirements
- [ ] Tool execution <500ms (95th percentile)
- [ ] Server startup <10 seconds
- [ ] Health checks <100ms response
- [ ] Support for 50+ concurrent requests

#### Security Requirements
- [ ] All endpoints require valid JWT
- [ ] Input validation on all parameters
- [ ] SQL injection prevention verified
- [ ] Audit logging for all operations

#### Operational Requirements
- [ ] Comprehensive logging implemented
- [ ] Health check endpoint functional
- [ ] Error monitoring and alerting
- [ ] Documentation complete

### Testing Strategy

#### Unit Tests
```python
# Test each MCP tool function
async def test_add_task_success():
    # Arrange: User and test data
    # Act: Call add_task tool
    # Assert: Task created and returned correctly

async def test_add_task_unauthorized():
    # Test with invalid JWT token
```

#### Integration Tests
```python
# Test AI agent integration
async def test_ai_agent_calls_mcp_tools():
    # Test natural language → tool call → database operation
```

#### End-to-End Tests
```bash
# Test complete workflow
curl -X POST http://localhost:8001/tools/add_task \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"title": "Test task"}'

# Verify task appears in database
curl -X GET http://localhost:8001/tools/list_tasks \
  -H "Authorization: Bearer $JWT_TOKEN"
```

#### Performance Tests
```bash
# Load testing with concurrent requests
for i in {1..50}; do
  curl -X POST http://localhost:8001/tools/add_task \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -d '{"title": "Load test task $i"}' &
done
wait
```

## Architecture Decision Records

This implementation plan references the following key architectural decisions:

1. **FastMCP HTTP Transport**: Decision to use native HTTP transport
2. **Unified Authentication**: Shared JWT validation with FastAPI backend
3. **Direct Database Access**: SQLModel integration for optimal performance
4. **Structured Error Handling**: Consistent error format with correlation IDs

Additional ADRs should be created during implementation for any significant deviations or new decisions.

## Success Metrics

### Primary Success Indicators
- **Tool Availability**: 99.9% uptime sustained over 30 days
- **Response Performance**: 95% of tool operations complete <500ms
- **Integration Success**: AI agent can successfully manage tasks via MCP
- **Error Rate**: <0.1% of authenticated requests result in errors

### Secondary Success Indicators
- **Developer Experience**: Clear documentation and easy setup process
- **Maintainability**: Code coverage >90% with comprehensive tests
- **Scalability**: System handles 50+ concurrent requests without degradation
- **Security**: Zero unauthorized access incidents

## Implementation Timeline

The following timeline is provided for planning purposes only:

### Phase 1: Core MCP Server Implementation (Estimated: 3-4 days)
- Configure FastMCP HTTP transport
- Implement JWT authentication middleware
- Create database service layer
- Implement 5 MCP tools
- Add error handling and logging

### Phase 2: Integration & Testing (Estimated: 2-3 days)
- AI agent integration testing
- End-to-end workflow testing
- Performance optimization
- Security validation

### Phase 3: Deployment & Documentation (Estimated: 1-2 days)
- Production deployment preparation
- Monitoring and alerting setup
- Documentation completion
- Knowledge transfer

Total estimated implementation time: 6-9 days

---

This plan provides comprehensive guidance for implementing the MCP server while maintaining alignment with the existing system architecture and meeting all specified functional and non-functional requirements.
