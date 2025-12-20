---
title: "MCP Tool Contract: add_task"
description: "API contract for the add_task MCP tool"
version: "1.0.0"
created: "2025-01-12"
author: "mcp-architect"
tags: ["mcp", "contract", "task", "add", "tool"]
status: "active"
---

# MCP Tool Contract: add_task

## Overview
The `add_task` tool enables AI agents to create new tasks on behalf of authenticated users through the MCP protocol. It provides comprehensive input validation, user isolation, and structured responses suitable for AI agent consumption.

## Input Specification

### Required Parameters
```json
{
  "title": {
    "type": "string",
    "required": true,
    "min_length": 1,
    "max_length": 200,
    "description": "Task title (1-200 characters, required)",
    "validation": "Non-empty string, trimmed, max 200 characters"
  },
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
  "description": {
    "type": "string",
    "required": false,
    "max_length": 1000,
    "description": "Optional task description (max 1000 characters)",
    "validation": "Optional string, max 1000 characters"
  },
  "priority": {
    "type": "string",
    "required": false,
    "enum": ["low", "medium", "high", "urgent"],
    "default": "medium",
    "description": "Task priority level",
    "validation": "One of: low, medium, high, urgent"
  },
  "due_date": {
    "type": "string",
    "required": false,
    "format": "ISO 8601",
    "description": "Optional due date in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
    "validation": "Valid ISO 8601 datetime or date string"
  },
  "recurrence_pattern": {
    "type": "string",
    "required": false,
    "enum": ["none", "daily", "weekly", "monthly", "yearly"],
    "default": "none",
    "description": "Task recurrence pattern",
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
      "description": "Unique identifier for the created task"
    },
    "title": {
      "type": "string",
      "description": "Task title as stored in database"
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
      "description": "Task due date in ISO format (null if not provided)"
    },
    "recurrence_pattern": {
      "type": "string",
      "description": "Task recurrence pattern"
    },
    "is_completed": {
      "type": "boolean",
      "value": false,
      "description": "Task completion status (always false for new tasks)"
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
  },
  "message": {
    "type": "string",
    "description": "Human-readable success message"
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

### Title Validation
- Must be non-empty string
- Must be 1-200 characters long after trimming whitespace
- Leading/trailing whitespace is trimmed before storage
- Cannot be null or undefined

### JWT Token Validation
- Must be valid JWT token
- Must contain user_id claim
- Must not be expired
- Must be properly signed

### Description Validation (Optional)
- Maximum 1000 characters
- Can be null or undefined
- Trailing whitespace is trimmed if provided

### Priority Validation (Optional)
- Must be one of: low, medium, high, urgent
- Default value: medium if not provided
- Case-insensitive validation

### Due Date Validation (Optional)
- Must be valid ISO 8601 format
- Supports both date (YYYY-MM-DD) and datetime (YYYY-MM-DDTHH:MM:SS) formats
- Date-only format defaults to end of day (23:59:59)
- Can be null or undefined

### Recurrence Pattern Validation (Optional)
- Must be one of: none, daily, weekly, monthly, yearly
- Default value: none if not provided
- Case-insensitive validation

## Business Logic

### User Isolation
- Tasks are created for the user identified in the JWT token
- No cross-user data access is permitted
- User ownership is enforced at the database level

### Default Values
- `priority`: "medium"
- `recurrence_pattern`: "none"
- `is_completed`: false
- `created_at`: Current UTC timestamp
- `updated_at`: Current UTC timestamp

### Data Processing
- Title and description are trimmed of leading/trailing whitespace
- Due date parsing supports flexible ISO 8601 formats
- Priority and recurrence patterns are normalized to lowercase

## Performance Requirements

- **Response Time**: < 200ms (p95)
- **Database Operations**: Single transaction with rollback on error
- **Memory Usage**: < 100MB per request

## Security Requirements

- **Authentication**: JWT token required for all operations
- **Authorization**: Tasks created only for authenticated user
- **Input Validation**: All inputs validated before processing
- **SQL Injection Protection**: Parameterized queries used throughout

## Monitoring & Observability

- **Correlation IDs**: Tracked throughout request lifecycle
- **Structured Logging**: All operations logged with correlation IDs
- **Performance Metrics**: Response time monitoring
- **Error Tracking**: Comprehensive error logging and reporting

## Error Handling

### Validation Errors
- Return specific field-level validation errors
- Provide human-readable error messages
- Include field name for UI validation feedback

### Database Errors
- Generic database error message to users
- Detailed error logged internally
- Database rollback on transaction failure

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
- Task management systems
- User interface components

## Test Cases

### Happy Path
1. Valid input with all fields
2. Valid input with required fields only
3. Valid input with optional fields
4. Mixed-case priority and recurrence patterns

### Error Cases
1. Empty title
2. Title > 200 characters
3. Invalid JWT token
4. Expired JWT token
5. Invalid priority value
6. Invalid due date format
7. Description > 1000 characters
8. Invalid recurrence pattern

## Version History

- **v1.0.0** (2025-01-12): Initial contract definition with comprehensive validation and error handling