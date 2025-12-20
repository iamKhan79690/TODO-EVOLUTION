---
title: "MCP Tool Contract: list_tasks"
description: "API contract for the list_tasks MCP tool"
version: "1.0.0"
created: "2025-01-12"
author: "mcp-architect"
tags: ["mcp", "contract", "task", "list", "tool"]
status: "active"
---

# MCP Tool Contract: list_tasks

## Overview
The `list_tasks` tool enables AI agents to retrieve tasks for authenticated users with filtering and pagination capabilities through the MCP protocol. It provides comprehensive filtering options and structured responses suitable for AI agent consumption.

## Input Specification

### Required Parameters
```json
{
  "jwt_token": {
    "type": "string",
    "required": true,
    "description": "JWT authentication token for user identification and authorization",
    "validation": "Valid JWT token with user_id claim"
  }
}
```

### Optional Parameters
```json
{
  "status": {
    "type": "string",
    "required": false,
    "enum": ["all", "pending", "completed"],
    "default": "pending",
    "description": "Filter tasks by completion status",
    "validation": "One of: all, pending, completed"
  },
  "priority": {
    "type": "string",
    "required": false,
    "enum": ["low", "medium", "high", "urgent"],
    "description": "Filter tasks by priority level",
    "validation": "One of: low, medium, high, urgent"
  },
  "limit": {
    "type": "integer",
    "required": false,
    "min": 1,
    "max": 100,
    "default": 20,
    "description": "Maximum number of tasks to return (1-100)",
    "validation": "Integer between 1 and 100"
  },
  "offset": {
    "type": "integer",
    "required": false,
    "min": 0,
    "default": 0,
    "description": "Number of tasks to skip for pagination",
    "validation": "Integer 0 or greater"
  }
}
```

## Output Specification

### Success Response
```json
{
  "success": true,
  "data": {
    "tasks": {
      "type": "array",
      "items": {
        "id": {
          "type": "integer",
          "description": "Unique task identifier"
        },
        "title": {
          "type": "string",
          "description": "Task title"
        },
        "description": {
          "type": "string",
          "description": "Task description (null if not provided)"
        },
        "priority": {
          "type": "string",
          "description": "Task priority level"
        },
        "due_date": {
          "type": "string",
          "format": "ISO 8601",
          "description": "Task due date in ISO format (null if not set)"
        },
        "recurrence_pattern": {
          "type": "string",
          "description": "Task recurrence pattern"
        },
        "is_completed": {
          "type": "boolean",
          "description": "Task completion status"
        },
        "created_at": {
          "type": "string",
          "format": "ISO 8601",
          "description": "Creation timestamp"
        },
        "updated_at": {
          "type": "string",
          "format": "ISO 8601",
          "description": "Last update timestamp"
        }
      }
    },
    "total_count": {
      "type": "integer",
      "description": "Total number of tasks matching the filter criteria"
    },
    "limit": {
      "type": "integer",
      "description": "Limit applied to the current request"
    },
    "offset": {
      "type": "integer",
      "description": "Offset applied to the current request"
    },
    "has_more": {
      "type": "boolean",
      "description": "Whether more tasks are available with the current filters"
    }
  }
}
```

### Error Response

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

### JWT Token Validation
- Must be valid JWT token
- Must contain user_id claim
- Must not be expired
- Must be properly signed

### Status Validation (Optional)
- Must be one of: all, pending, completed
- Default value: pending if not provided
- Case-insensitive validation

### Priority Validation (Optional)
- Must be one of: low, medium, high, urgent
- No default value (returns all priorities if not specified)
- Case-insensitive validation

### Limit Validation (Optional)
- Must be integer between 1 and 100
- Default value: 20 if not provided
- Enforces maximum page size for performance

### Offset Validation (Optional)
- Must be integer 0 or greater
- Default value: 0 if not provided
- Used for pagination navigation

## Business Logic

### User Isolation
- Tasks are returned only for the authenticated user
- No cross-user data access is permitted
- User ownership enforced at database query level

### Filtering Logic
- **Status Filter**:
  - "all": Returns all tasks regardless of completion status
  - "pending": Returns only uncompleted tasks (is_completed = false)
  - "completed": Returns only completed tasks (is_completed = true)
- **Priority Filter**: Filters tasks by specified priority level (if provided)
- **Combined Filters**: Multiple filters are combined with AND logic

### Pagination Logic
- Tasks are ordered by creation date (newest first)
- Offset specifies number of tasks to skip
- Limit specifies maximum number of tasks to return
- has_more indicates if additional pages exist

### Default Behavior
- Returns pending tasks by default (status = "pending")
- Returns 20 tasks per page by default (limit = 20)
- Returns tasks in reverse chronological order (newest first)

## Performance Requirements

- **Response Time**: < 200ms (p95)
- **Database Operations**: Optimized queries with proper indexing
- **Pagination**: Efficient pagination with LIMIT/OFFSET
- **Memory Usage**: < 100MB per request

## Security Requirements

- **Authentication**: JWT token required for all operations
- **Authorization**: Tasks returned only for authenticated user
- **Input Validation**: All inputs validated before processing
- **SQL Injection Protection**: Parameterized queries used throughout
- **Data Privacy**: No cross-user data leakage

## Monitoring & Observability

- **Correlation IDs**: Tracked throughout request lifecycle
- **Structured Logging**: All operations logged with correlation IDs
- **Performance Metrics**: Query execution time monitoring
- **Pagination Metrics**: Page size and offset usage tracking

## Error Handling

### Validation Errors
- Return specific field-level validation errors
- Provide human-readable error messages
- Include field name for UI validation feedback

### Database Errors
- Generic database error message to users
- Detailed error logged internally
- No sensitive database information exposed

### Authentication Errors
- Clear authentication failure messages
- User-friendly error descriptions
- Security-conscious error information disclosure

## Integration Points

### Dependencies
- JWT validation service
- Database connection pool
- Task service layer
- Authentication middleware
- Performance monitoring
- Correlation ID tracking

### Consumers
- AI Chatbot agents
- MCP client applications
- Task management UIs
- Dashboard components
- Export functionality

## Use Cases

### Common Patterns
1. **Get all pending tasks**: `{ "status": "pending" }`
2. **Get completed tasks**: `{ "status": "completed" }`
3. **Get high priority tasks**: `{ "priority": "high" }`
4. **Paginated results**: `{ "limit": 10, "offset": 20 }`
5. **Complex filtering**: `{ "status": "pending", "priority": "urgent", "limit": 5 }`

### AI Agent Scenarios
- Review today's pending tasks
- Check for overdue high-priority items
- Get completed tasks for productivity analysis
- Export task lists for reports

## Test Cases

### Happy Path
1. Default parameters (pending tasks, 20 items)
2. Status filtering (all, pending, completed)
3. Priority filtering (low, medium, high, urgent)
4. Pagination (various limit and offset combinations)
5. Combined status and priority filtering
6. Empty result sets

### Error Cases
1. Invalid JWT token
2. Expired JWT token
3. Invalid status value
4. Invalid priority value
5. Limit < 1 or > 100
6. Negative offset
7. Non-integer limit/offset values

### Edge Cases
1. User with no tasks
2. Pagination beyond available results
3. Very large result sets
4. Special characters in task data

## Database Schema Requirements

### Required Indexes
- `tasks.user_id` (for user isolation)
- `tasks.is_completed` (for status filtering)
- `tasks.priority` (for priority filtering)
- `tasks.created_at` (for chronological ordering)
- Composite index: `(user_id, is_completed, created_at)`
- Composite index: `(user_id, priority, created_at)`

## Version History

- **v1.0.0** (2025-01-12): Initial contract definition with comprehensive filtering and pagination