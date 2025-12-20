---
title: "MCP Tool Contract: update_task"
description: "API contract for the update_task MCP tool"
version: "1.0.0"
created: "2025-01-12"
author: "mcp-architect"
tags: ["mcp", "contract", "task", "update", "tool"]
status: "active"
---

# MCP Tool Contract: update_task

## Overview
The `update_task` tool enables AI agents to modify existing tasks on behalf of authenticated users through the MCP protocol. It implements partial update functionality with comprehensive validation, user isolation, and audit trails.

## Input Specification

### Required Parameters
```json
{
  "task_id": {
    "type": "integer",
    "required": true,
    "min": 1,
    "description": "Unique identifier of the task to update",
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

### Optional Update Parameters
**At least one of the following parameters must be provided:**

```json
{
  "title": {
    "type": "string",
    "required": false,
    "min_length": 1,
    "max_length": 200,
    "description": "Updated task title (1-200 characters)",
    "validation": "Non-empty string, trimmed, max 200 characters"
  },
  "description": {
    "type": "string",
    "required": false,
    "max_length": 1000,
    "description": "Updated task description (max 1000 characters, null to clear)",
    "validation": "String up to 1000 characters or null"
  },
  "priority": {
    "type": "string",
    "required": false,
    "enum": ["low", "medium", "high", "urgent"],
    "description": "Updated task priority level",
    "validation": "One of: low, medium, high, urgent"
  },
  "due_date": {
    "type": ["string", "null"],
    "required": false,
    "format": "ISO 8601",
    "description": "Updated due date in ISO 8601 format, or null to remove due date",
    "validation": "Valid ISO 8601 datetime/date string or null"
  },
  "recurrence_pattern": {
    "type": "string",
    "required": false,
    "enum": ["none", "daily", "weekly", "monthly", "yearly"],
    "description": "Updated task recurrence pattern",
    "validation": "One of: none, daily, weekly, monthly, yearly"
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
      "description": "Unique identifier of the updated task"
    },
    "status": {
      "type": "string",
      "value": "updated",
      "description": "Task update status"
    },
    "title": {
      "type": "string",
      "description": "Updated task title"
    },
    "description": {
      "type": "string",
      "description": "Updated task description (null if cleared)"
    },
    "priority": {
      "type": "string",
      "description": "Updated task priority level"
    },
    "due_date": {
      "type": "string",
      "format": "ISO 8601",
      "description": "Updated due date in ISO format (null if removed)"
    },
    "recurrence_pattern": {
      "type": "string",
      "description": "Updated task recurrence pattern"
    },
    "is_completed": {
      "type": "boolean",
      "description": "Task completion status (unchanged by this operation)"
    },
    "created_at": {
      "type": "string",
      "format": "ISO 8601",
      "description": "Original creation timestamp"
    },
    "updated_at": {
      "type": "string",
      "format": "ISO 8601",
      "description": "Last update timestamp"
    }
  },
  "updated_fields": {
    "type": "array",
    "items": {
      "type": "string",
      "description": "List of fields that were actually updated"
    },
    "description": "Fields that were modified during the operation"
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
      "description": "Name of the field that failed validation"
    }
  }
}
```

#### No Updates Error
```json
{
  "success": false,
  "error": {
    "code": "no_updates",
    "message": {
      "type": "string",
      "description": "No valid update fields provided"
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

### Update Parameters Validation
- **At least one update field required**
- **Title**: 1-200 characters if provided, non-empty
- **Description**: Maximum 1000 characters, can be null to clear
- **Priority**: Must be one of: low, medium, high, urgent
- **Due Date**: Valid ISO 8601 format, can be null to remove
- **Recurrence Pattern**: Must be one of: none, daily, weekly, monthly, yearly

## Business Logic

### Task Ownership Verification
- Task must exist in the database
- Task must belong to the authenticated user (user_id from JWT)
- Cross-user task access is strictly prohibited
- Ownership verification occurs before any updates

### Partial Update Implementation
- **Selective Updates**: Only provided fields are updated
- **No-change Detection**: Unchanged fields are not modified
- **Null Values**: Explicit null values clear the field
- **Field Validation**: Each updated field validated independently

### Update Processing Logic
1. **Load Current Task**: Retrieve existing task data
2. **Validate Ownership**: Ensure user owns the task
3. **Process Updates**: Apply each provided update field
4. **Validate Each Field**: Field-specific validation rules
5. **Track Changes**: Record which fields were actually modified
6. **Update Timestamps**: Set updated_at to current UTC time
7. **Return Updated Data**: Complete task state after updates

### Special Cases
- **No Changes**: If all provided values match current values, returns success with no updated_fields
- **Empty Update**: If no update fields provided, returns no_updates error
- **Conflict Resolution**: Last update wins in concurrent scenarios
- **Immutable Fields**: created_at, user_id cannot be modified

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
- **Field Protection**: Sensitive fields (user_id, created_at) are immutable

## Monitoring & Observability

- **Correlation IDs**: Tracked throughout request lifecycle
- **Structured Logging**: All operations logged with correlation IDs
- **Performance Metrics**: Task update time monitoring
- **Audit Trail**: Update events logged with field-level changes
- **Error Tracking**: Comprehensive error logging and reporting

## Error Handling

### Task Not Found
- Occurs when task_id does not exist in database
- Returns specific task_not_found error code
- Includes user-friendly message
- Logged with task_id and user_id for debugging

### Unauthorized Access
- Occurs when user tries to update task they don't own
- Returns unauthorized error code
- No information about whether task exists (security)
- Logged as potential security incident

### Validation Errors
- Invalid task_id format or values
- Invalid field values for updates
- Missing required update fields
- Return specific field-level errors

### No Updates Error
- Occurs when no update fields are provided
- Returns no_updates error code
- Clear error message indicating requirement
- Helpful for API client development

## Integration Points

### Dependencies
- JWT validation service
- Database connection pool
- Task service layer
- Authentication middleware
- Performance monitoring
- Correlation ID tracking
- User ownership verification
- Field validation service

### Consumers
- AI Chatbot agents
- Task management UIs
- Productivity tracking systems
- Workflow automation
- Synchronization services
- Mobile applications

## Use Cases

### Common Patterns
1. **Edit task title**: Update task name
2. **Add description**: Add or modify task details
3. **Change priority**: Update task urgency
4. **Set due date**: Add or modify deadline
5. **Clear fields**: Remove description or due date
6. **Modify recurrence**: Update task repetition pattern

### AI Agent Scenarios
- Update tasks based on conversation context
- Modify task details after user input
- Adjust priorities based on new information
- Set due dates from calendar events
- Update task descriptions with additional context

## Test Cases

### Happy Path
1. Update single field successfully
2. Update multiple fields simultaneously
3. Clear optional fields with null values
4. Update with same values (no actual change)
5. Partial updates with various field combinations

### Error Cases
1. Non-existent task_id
2. Task owned by different user
3. Invalid task_id format
4. Invalid JWT token
5. No update fields provided
6. Invalid title (empty or >200 chars)
7. Invalid priority value
8. Invalid due date format
9. Invalid recurrence pattern
10. Description > 1000 characters

### Edge Cases
1. Task update during database maintenance
2. Concurrent update attempts
3. Update completed tasks
4. Tasks with complex recurrence patterns
5. Tasks with external dependencies
6. Unicode characters in fields

## Database Schema Requirements

### Required Indexes
- `tasks.id` (primary key)
- `tasks.user_id` (for ownership verification)
- Composite index: `(id, user_id)` for efficient ownership lookup

### Audit Trail Requirements
- Track field-level changes for compliance
- Maintain update history for recovery
- Log user actions for security auditing

## Security Considerations

### Authorization Flow
1. Validate JWT token and extract user_id
2. Verify task exists and belongs to user
3. Only then proceed with updates

### Field Protection
- Immutable fields cannot be modified
- Sensitive fields require additional validation
- Field updates are tracked for audit purposes

### Information Disclosure
- Unauthorized requests return generic "not found" or "unauthorized"
- No leakage about task existence to unauthorized users
- Error messages consistent for both not found and unauthorized cases

## Version History

- **v1.0.0** (2025-01-12): Initial contract definition with comprehensive partial update implementation and field-level validation