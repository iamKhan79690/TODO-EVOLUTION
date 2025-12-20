---
title: "MCP Tool Contract: delete_task"
description: "API contract for the delete_task MCP tool"
version: "1.0.0"
created: "2025-01-12"
author: "mcp-architect"
tags: ["mcp", "contract", "task", "delete", "tool"]
status: "active"
---

# MCP Tool Contract: delete_task

## Overview
The `delete_task` tool enables AI agents to remove tasks on behalf of authenticated users through the MCP protocol. It implements soft delete functionality to preserve data integrity while providing user isolation and comprehensive audit trails.

## Input Specification

### Required Parameters
```json
{
  "task_id": {
    "type": "integer",
    "required": true,
    "min": 1,
    "description": "Unique identifier of the task to delete",
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
      "description": "Unique identifier of the deleted task"
    },
    "status": {
      "type": "string",
      "value": "deleted",
      "description": "Task deletion status"
    },
    "title": {
      "type": "string",
      "description": "Title of the deleted task"
    },
    "deleted_at": {
      "type": "string",
      "format": "ISO 8601",
      "description": "Timestamp when task was marked as deleted"
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
- Ownership verification occurs before deletion

### Soft Delete Implementation
- **Preservation**: Task data is preserved in database
- **Status Update**: `is_deleted` flag set to true
- **Timestamps**: `deleted_at` and `updated_at` set to current UTC time
- **Visibility**: Deleted tasks excluded from normal queries
- **Recovery**: Deletion can be reversed if needed

### Transaction Safety
- Task retrieval and soft delete occur in single database transaction
- Database rollback on any failure
- Concurrent operation protection through proper locking
- Atomic status transition to prevent partial states

### Response Data
- Returns complete task information before deletion
- Includes deletion timestamp for audit trail
- Returns original task title for user confirmation
- Maintains record of what was deleted

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
- **Audit Trail**: All deletions logged for compliance

## Monitoring & Observability

- **Correlation IDs**: Tracked throughout request lifecycle
- **Structured Logging**: All operations logged with correlation IDs
- **Performance Metrics**: Task deletion time monitoring
- **Audit Trail**: Deletion events logged for compliance and recovery
- **Error Tracking**: Comprehensive error logging and reporting

## Error Handling

### Task Not Found
- Occurs when task_id does not exist in database
- Returns specific task_not_found error code
- Includes user-friendly message
- Logged with task_id and user_id for debugging

### Unauthorized Access
- Occurs when user tries to delete task they don't own
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
- Soft delete implementation

### Consumers
- AI Chatbot agents
- Task management UIs
- Productivity tracking systems
- Workflow automation
- Data retention systems
- Compliance reporting tools

## Use Cases

### Common Patterns
1. **Remove completed tasks**: Clean up finished work
2. **Remove irrelevant tasks**: Delete unnecessary items
3. **Data cleanup**: Bulk deletion of old tasks
4. **User management**: Remove tasks during account cleanup

### AI Agent Scenarios
- Delete tasks based on conversation context
- Remove completed items after user confirmation
- Clean up task lists based on criteria
- Automate task management workflows

## Database Schema Requirements

### Required Fields for Soft Delete
- `is_deleted` (boolean) - Flag indicating deletion status
- `deleted_at` (timestamp) - Deletion timestamp
- `updated_at` (timestamp) - Last update timestamp

### Required Indexes
- `tasks.id` (primary key)
- `tasks.user_id` (for ownership verification)
- `tasks.is_deleted` (for filtering deleted tasks)
- Composite index: `(id, user_id, is_deleted)` for efficient lookups

### Query Modifications
- All task queries must include `WHERE is_deleted = false`
- Admin queries may include deleted tasks with explicit flag
- Restore operations require is_deleted flag manipulation

## Data Retention & Recovery

### Soft Delete Benefits
- **Data Recovery**: Deleted tasks can be restored
- **Audit Trail**: Complete history preserved
- **Compliance**: Meets data retention requirements
- **Analytics**: Historical data available for analysis

### Recovery Procedures
- Admin tools to restore accidentally deleted tasks
- Time-based recovery windows
- User-initiated restore with confirmation
- Bulk restore operations for data recovery

## Security Considerations

### Authorization Flow
1. Validate JWT token and extract user_id
2. Verify task exists and belongs to user
3. Only then proceed with soft delete

### Information Disclosure
- Unauthorized requests return generic "not found" or "unauthorized"
- No leakage about task existence to unauthorized users
- Error messages consistent for both not found and unauthorized cases

### Audit Trail
- All deletion events logged with:
  - Timestamp
  - User ID
  - Task ID
  - Task title (before deletion)
  - Correlation ID
  - Deletion reason (if available)

## Test Cases

### Happy Path
1. Delete existing task successfully
2. Delete task with valid ownership
3. Idempotent deletion (already deleted task)
4. High-frequency deletion operations

### Error Cases
1. Non-existent task_id
2. Task owned by different user
3. Invalid task_id format
4. Invalid JWT token
5. Expired JWT token
6. Negative task_id
7. Zero task_id

### Edge Cases
1. Task deletion during database maintenance
2. Concurrent deletion attempts
3. Task with complex recurrence patterns
4. Tasks with dependencies or relationships
5. Recently completed tasks

## Compliance & Governance

### Data Protection
- GDPR compliance through soft delete
- User right to be forgotten (permanent delete option)
- Data retention policies enforcement
- Audit trail for regulatory compliance

### Retention Policies
- Configurable retention periods for deleted tasks
- Automated cleanup of old deleted tasks
- Export functionality for data portability
- Legal hold capabilities for litigation

## Version History

- **v1.0.0** (2025-01-12): Initial contract definition with comprehensive soft delete implementation and audit trail