# Specification: Phase 2 - Backend API

**Feature**: 005-backend-api
**Status**: Draft
**Version**: 1.0
**Date**: 2025-12-07
**Author**: AI Assistant

---

## 1. Overview

This specification defines the backend API implementation for task management, building on the completed database infrastructure (004-database-setup). The API will provide RESTful endpoints for Task CRUD operations with proper authentication, validation, and user isolation.

### 1.1 Scope

**In Scope:**
- Pydantic schemas for Task operations (TaskCreate, TaskUpdate, TaskResponse)
- Health check endpoint for API monitoring
- 6 Task CRUD endpoints following constitutional requirements
- JWT authentication integration
- User isolation and access control
- Request validation and error handling
- OpenAPI/Swagger documentation

**Out of Scope:**
- User authentication endpoints (handled by Better Auth)
- Frontend integration
- Real-time updates
- Bulk operations
- Advanced filtering/searching (future enhancement)

### 1.2 Dependencies

- **Database Layer**: SQLModel models and database connection (completed in 004-database-setup)
- **Authentication**: Better Auth integration (completed in 004-database-setup)
- **Configuration**: Environment-based configuration (completed in 004-database-setup)

---

## 2. Requirements

### 2.1 API Design Requirements

**RESTful API Design** (Constitution Section 11):
- All endpoints follow RESTful patterns
- Proper HTTP status codes and error responses
- Consistent URL structure with user isolation
- Statelessness and proper caching headers

**Authentication & Authorization** (Constitution Section 8):
- JWT-based authentication with Better Auth
- User-scoped endpoints: `/api/{user_id}/tasks/*`
- Proper access control and data isolation

**Data Validation** (Constitution Section 12):
- Pydantic schemas for request/response validation
- Comprehensive error messages
- Input sanitization and security validation

### 2.2 Functional Requirements

#### FR1: Health Check Endpoint
- **Endpoint**: `GET /api/health`
- **Purpose**: API health monitoring and uptime checking
- **Response**: API status, version, and connectivity information

#### FR2: Task CRUD Endpoints
All endpoints require JWT authentication and user-scoped access:

1. **List Tasks**: `GET /api/{user_id}/tasks`
   - Returns all tasks for the authenticated user
   - Supports optional query parameters for filtering
   - Pagination support (future enhancement)

2. **Create Task**: `POST /api/{user_id}/tasks`
   - Creates a new task for the authenticated user
   - Validates required fields and business rules
   - Returns created task with assigned ID

3. **Get Task**: `GET /api/{user_id}/tasks/{task_id}`
   - Returns a specific task by ID
   - Validates user ownership (403 if not owner)
   - Returns 404 if task not found

4. **Update Task**: `PUT /api/{user_id}/tasks/{task_id}`
   - Updates all task fields
   - Validates user ownership and input data
   - Returns updated task

5. **Delete Task**: `DELETE /api/{user_id}/tasks/{task_id}`
   - Soft deletes the task (archives instead of physical deletion)
   - Validates user ownership
   - Returns success confirmation

6. **Complete Task**: `PATCH /api/{user_id}/tasks/{task_id}/complete`
   - Toggles task completion status
   - Validates user ownership
   - Returns updated task

### 2.3 Data Models

#### TaskCreate Schema
```python
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Priority = Field(Priority.MEDIUM)
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
```

#### TaskUpdate Schema
```python
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    is_completed: Optional[bool] = None
```

#### TaskResponse Schema
```python
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: Priority
    due_date: Optional[datetime]
    recurrence_pattern: Optional[RecurrencePattern]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: int
```

---

## 3. Technical Requirements

### 3.1 API Architecture

**FastAPI Router Structure**:
```python
# backend/src/api/tasks.py
tasks_router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

# backend/src/api/health.py
health_router = APIRouter(prefix="/api", tags=["health"])
```

**Dependency Injection**:
- Database session dependency
- Authentication dependency (Better Auth)
- User validation dependency

### 3.2 Error Handling

**Standardized Error Responses**:
```python
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Human-readable error message",
        "details": {...}
    },
    "timestamp": "2025-12-07T10:30:00Z",
    "path": "/api/123/tasks"
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Input validation failures (400)
- `UNAUTHORIZED`: Authentication required (401)
- `FORBIDDEN`: Access denied (403)
- `NOT_FOUND`: Resource not found (404)
- `CONFLICT`: Data conflict (409)
- `INTERNAL_ERROR`: Server error (500)

### 3.3 Validation Rules

**Task Title**:
- Required field
- 1-200 characters
- No leading/trailing whitespace
- No HTML/script tags

**Task Description**:
- Optional field
- Maximum 1000 characters
- Stripped of dangerous content

**Due Date**:
- Optional field
- Must be future datetime if provided
- ISO 8601 format

**Priority**:
- Enum: LOW, MEDIUM, HIGH, URGENT
- Default: MEDIUM
- Case-insensitive input

**Recurrence Pattern**:
- Enum: NONE, DAILY, WEEKLY, MONTHLY, YEARLY
- Default: NONE
- Requires due_date if not NONE

---

## 4. Implementation Details

### 4.1 File Structure
```
backend/src/
├── api/
│   ├── __init__.py
│   ├── tasks.py          # Task CRUD endpoints
│   └── health.py         # Health endpoints (existing)
├── schemas/
│   ├── __init__.py
│   ├── task.py           # Task Pydantic schemas
│   └── common.py         # Common schemas
├── services/
│   ├── __init__.py
│   └── task_service.py   # Business logic layer
└── dependencies/
    ├── __init__.py
    ├── auth.py           # Authentication dependencies
    └── database.py       # Database dependencies
```

### 4.2 API Endpoint Specifications

#### Health Check
```http
GET /api/health
Authorization: Bearer {jwt_token}

Response:
{
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-12-07T10:30:00Z",
    "database": "connected"
}
```

#### List Tasks
```http
GET /api/{user_id}/tasks
Authorization: Bearer {jwt_token}

Response:
{
    "tasks": [TaskResponse, ...],
    "count": 42,
    "page": 1,
    "total_pages": 5
}
```

#### Create Task
```http
POST /api/{user_id}/tasks
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for the API",
    "priority": "HIGH",
    "due_date": "2025-12-15T23:59:59Z",
    "recurrence_pattern": "NONE"
}

Response:
{
    "task": TaskResponse,
    "message": "Task created successfully"
}
```

#### Get Task
```http
GET /api/{user_id}/tasks/{task_id}
Authorization: Bearer {jwt_token}

Response:
{
    "task": TaskResponse
}
```

#### Update Task
```http
PUT /api/{user_id}/tasks/{task_id}
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
    "title": "Updated task title",
    "priority": "MEDIUM"
}

Response:
{
    "task": TaskResponse,
    "message": "Task updated successfully"
}
```

#### Delete Task
```http
DELETE /api/{user_id}/tasks/{task_id}
Authorization: Bearer {jwt_token}

Response:
{
    "message": "Task deleted successfully",
    "task_id": 123
}
```

#### Complete Task
```http
PATCH /api/{user_id}/tasks/{task_id}/complete
Authorization: Bearer {jwt_token}

Response:
{
    "task": TaskResponse,
    "message": "Task completion status updated"
}
```

### 4.3 Database Operations

**Service Layer Pattern**:
- All database operations abstracted through `TaskService`
- Transaction management with proper rollback
- User access validation at service layer
- Audit logging for data changes

**Query Examples**:
```python
# Get user tasks with optional filters
async def get_user_tasks(
    session: AsyncSession,
    user_id: int,
    completed: Optional[bool] = None,
    priority: Optional[Priority] = None
) -> List[Task]:
    query = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        query = query.where(Task.is_completed == completed)
    if priority is not None:
        query = query.where(Task.priority == priority)
    result = await session.execute(query)
    return result.scalars().all()
```

---

## 5. Quality Assurance

### 5.1 Testing Requirements

**Unit Tests**:
- Pydantic schema validation tests
- Service layer business logic tests
- Error handling and edge cases

**Integration Tests**:
- API endpoint tests with authentication
- Database operations tests
- End-to-end request/response validation

**Manual Testing**:
- Swagger UI interactive testing
- Postman/curl command testing
- Cross-origin requests testing

### 5.2 Performance Requirements

**Response Time Targets**:
- Health check: <50ms
- Task CRUD operations: <200ms
- Task list with pagination: <300ms

**Database Performance**:
- Optimized queries with proper indexing
- Connection pooling efficiency
- Query result caching where appropriate

### 5.3 Security Requirements

**Input Validation**:
- All inputs validated through Pydantic schemas
- SQL injection prevention through ORM
- XSS protection in string fields

**Authentication Security**:
- JWT token validation on all endpoints
- User isolation enforcement
- Rate limiting consideration (future enhancement)

---

## 6. Success Criteria

### 6.1 Functional Acceptance

✅ **API Functionality**:
- All 6 CRUD endpoints implemented and functional
- Health check endpoint responds correctly
- Authentication and authorization working
- Proper HTTP status codes and error responses

✅ **Data Validation**:
- All Pydantic schemas validate input correctly
- Error messages are clear and actionable
- Business rules enforced consistently

✅ **Documentation**:
- OpenAPI/Swagger documentation complete
- API examples and descriptions provided
- Error response format documented

### 6.2 Technical Acceptance

✅ **Code Quality**:
- Clean, maintainable code structure
- Proper separation of concerns
- Comprehensive error handling
- Type hints and documentation

✅ **Performance**:
- All endpoints meet response time targets
- Database queries optimized
- No memory leaks or resource issues

✅ **Security**:
- Authentication properly implemented
- Input validation prevents injection attacks
- User data isolation enforced

---

## 7. Post-Implementation

### 7.1 Verification Checklist

- [ ] All API endpoints accessible via Swagger UI at http://localhost:8000/docs
- [ ] Health check returns healthy status with database connectivity
- [ ] Task CRUD operations work with valid authentication
- [ ] Error responses return proper HTTP status codes
- [ ] Input validation rejects invalid data appropriately
- [ ] User isolation prevents cross-user data access
- [ ] Database operations complete successfully with audit trails

### 7.2 Documentation Updates

- Update README.md with API endpoint documentation
- Create API usage examples in docs/
- Update quickstart guide with API testing instructions
- Document authentication setup process

### 7.3 Next Steps

- Consider implementing advanced filtering and search
- Add bulk operations for efficiency
- Implement real-time updates with WebSockets
- Add API rate limiting and caching
- Create comprehensive API client libraries