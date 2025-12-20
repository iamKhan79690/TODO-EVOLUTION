---
title: "MCP Tool Contract: complete_task"
description: "API contract for the complete_task MCP tool"
version: "1.0.0"
created: "2025-01-12"
author: "mcp-architect"
tags: ["mcp", "contract", "task", "complete", "tool"]
status: "active"
---

# MCP Tool Contract: complete_task

## Overview
The `complete_task` tool enables AI agents to mark tasks as completed on behalf of authenticated users through the MCP protocol. It provides task ownership verification and status updates with comprehensive error handling and user isolation.

## Input Specification

### Required Parameters
```json
{
  "task_id": {
    "type": "integer",
    "required": true,
    "min": 1,
    "description": "Unique identifier of the task to complete",
    "validation": "Positive integer representing existing task ID"
  },
  "jwt_token": {
    "type": "string",
    "required": true,
    "description": "JWT authentication token for user identification and authorization",
    "validation": "Valid JWT token with user_id claim"
  }
}
```

## Output Specification

### Success Response
```json
{
  "success": true,
  "data": {
    "task_id": {
      "type": "integer",
      "description": "Unique identifier of the completed task"
    },
    "status": {
      "type": "string",
      "value": "completed",
      "description": "Updated task status"
    },
    "title": {
      "type": "string",
      "description": "Title of the completed task"
    },
    "is_completed": {
      "type": "boolean",
      "value": true,
      "description": "Task completion status (always true after successful operation)"
    },
    "completed_at": {
      "type": "string",
      "format": "ISO 8601",
      "description": "Timestamp when task was marked as completed"
    },
    "updated_at": {
      "type": "string",
      "format": "ISO 8601",
      "description": "Last update timestamp"
    }
  },
  "message": {
    "type": "string",
    "description": "Human-readable success message"
  }
}
```

### Error Response

#### Task Not Found Error
```json
{
  "success": false,
  "error": {
    "code": "task_not_found",
    "message": {
      "type": "string",
      "description": "Human-readable error message indicating task was not found"
    }
  }
}
```

#### Unauthorized Error
```json
{
  "success": false,
  "error": {
    "code": "unauthorized",
    "message": {
      "type": "string",
      "description": "Human-readable error message indicating user does not own the task"
    }
  }
}
```

#### Validation Error
```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": {
      "type": "string",
      "description": "Human-readable validation error message"
    },
    "field": {
      "type": "string",
      "description": "Name of the field that failed validation (if applicable)"
    }
  }
}
```

#### Database Error
```json
{
  "success": false,
  "error": {
    "code": "database_error",
    "message": {
      "type": "string",
      "description": "Human-readable database error message"
    }
  }
}
```

#### Authentication Error
```json
{
  "success": false,
  "error": {
    "code": "authentication_error",
    "message": {
      "type": "string",
      "description": "Authentication or authorization error message"
    }
  }
}
```

## Validation Rules

### Task ID Validation
- Must be positive integer (>= 1)
- Cannot be null, zero, or negative
- Must correspond to existing task in database

### JWT Token Validation
- Must be valid JWT token
- Must contain user_id claim
- Must not be expired
- Must be properly signed

## Business Logic

### Task Ownership Verification
- Task must exist in the database
- Task must belong to the authenticated user (user_id from JWT)
- Cross-user task access is strictly prohibited
- Ownership verification occurs before status update

### Status Update Logic
- **Current Status**: Task must be incomplete (is_completed = false)
- **Target Status**: Task is set to completed (is_completed = true)
- **Timestamps**: updated_at and completed_at are set to current UTC time
- **Idempotency**: Completing an already completed task returns success

### Transaction Safety
- Task retrieval and update occur in a single database transaction
- Database rollback on any failure
- Concurrent operation protection through proper locking

### Response Data
- Returns complete task information after status update
- Includes completion timestamp for audit trail
- Returns original task title for user confirmation

## Performance Requirements

- **Response Time**: < 200ms (p95)
- **Database Operations**: Single transaction with minimal locking
- **Query Optimization**: Efficient lookup by primary key and user_id
- **Memory Usage**: < 100MB per request

## Security Requirements

- **Authentication**: JWT token required for all operations
- **Authorization**: User ownership verification before any action
- **Input Validation**: All inputs validated before processing
- **SQL Injection Protection**: Parameterized queries used throughout
- **Data Privacy**: No cross-user data access permitted

## Monitoring & Observability

- **Correlation IDs**: Tracked throughout request lifecycle
- **Structured Logging**: All operations logged with correlation IDs
- **Performance Metrics**: Task completion time monitoring
- **Audit Trail**: Completion events logged for compliance
- **Error Tracking**: Comprehensive error logging and reporting

## Error Handling

### Task Not Found
- Occurs when task_id does not exist in database
- Returns specific task_not_found error code
- Includes user-friendly message
- Logged with task_id and user_id for debugging

### Unauthorized Access
- Occurs when user tries to complete task they don't own
- Returns unauthorized error code
- No information about whether task exists (security)
- Logged as potential security incident

### Validation Errors
- Invalid task_id format or values
- JWT token validation failures
- Return specific field-level errors

### Database Errors
- Connection issues or constraint violations
- Generic database error message to users
- Detailed error logged internally for debugging

## Integration Points

### Dependencies
- JWT validation service
- Database connection pool
- Task service layer
- Authentication middleware
- Performance monitoring
- Correlation ID tracking
- User ownership verification

### Consumers
- AI Chatbot agents
- Task management UIs
- Productivity tracking systems
- Workflow automation
- Calendar integration

## Use Cases

### Common Patterns
1. **Mark task as done**: Basic task completion
2. **Productivity tracking**: Mark tasks in batch operations
3. **Workflow automation**: Automatic task completion triggers
4. **Progress reporting**: Completion status updates for reports

### AI Agent Scenarios
- Complete tasks based on conversation context
- Mark items as done after user confirmation
- Update task status from external triggers
- Automate repetitive task completion

## Test Cases

### Happy Path
1. Complete pending task successfully
2. Complete task with valid ownership
3. Idempotent completion (already completed task)
4. High-frequency completion operations

### Error Cases
1. Non-existent task_id
2. Task owned by different user
3. Invalid task_id format
4. Invalid JWT token
5. Expired JWT token
6. Negative task_id
7. Zero task_id

### Edge Cases
1. Task completion during database maintenance
2. Concurrent completion attempts
3. Task with complex recurrence patterns
4. Tasks with due dates in the past

## Database Schema Requirements

### Required Indexes
- `tasks.id` (primary key)
- `tasks.user_id` (for ownership verification)
- Composite index: `(id, user_id)` for efficient ownership lookup

### Transaction Requirements
- SERIALIZABLE or READ_COMMITTED isolation level
- Row-level locking during update operations
- Automatic rollback on constraint violations

## Security Considerations

### Authorization Flow
1. Validate JWT token and extract user_id
2. Verify task exists and belongs to user
3. Only then proceed with status update

### Information Disclosure
- Unauthorized requests return generic "not found" or "unauthorized"
- No leakage about task existence to unauthorized users
- Error messages consistent for both not found and unauthorized cases

### Audit Trail
- All completion events logged with:
  - Timestamp
  - User ID
  - Task ID
  - Previous status
  - Correlation ID

## Version History

- **v1.0.0** (2025-01-12): Initial contract definition with comprehensive ownership verification and status management