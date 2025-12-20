# Agent API Contracts

**Date**: 2025-01-12
**Feature**: OpenAI Agent Architecture
**Purpose**: Define API contracts for agent service integration

## Agent Service API

### Base URL
```
POST /api/v1/agent/chat
```

### Request Schema

```json
{
  "user_id": "uuid",
  "message": "string",
  "conversation_id": "string|null",
  "jwt_token": "string"
}
```

**Parameters**:
- `user_id`: UUID - User identifier (required)
- `message`: String - User's natural language input (required, max 2000 chars)
- `conversation_id`: String/null - Existing conversation identifier (optional, null for new conversation)
- `jwt_token`: String - Authentication token (required)

### Response Schema

#### Success Response (200 OK)

```json
{
  "success": true,
  "data": {
    "conversation_id": "string",
    "agent_response": "string",
    "actions_taken": [
      {
        "type": "tool_call",
        "tool_name": "string",
        "parameters": "object",
        "result": "object",
        "confirmation_required": boolean
      }
    ],
    "suggested_followup": "string|null",
    "context_summary": "string|null"
  },
  "metadata": {
    "conversation_turn": "number",
    "processing_time_ms": "number",
    "intent_confidence": "number"
  }
}
```

#### Error Response (4xx/5xx)

```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "object|null"
  },
  "metadata": {
    "request_id": "string",
    "timestamp": "string"
  }
}
```

**Error Codes**:
- `authentication_error`: Invalid or expired JWT token
- `rate_limit_exceeded`: Too many requests from user
- `conversation_not_found`: Invalid conversation_id provided
- `message_too_long`: Input message exceeds character limit
- `agent_unavailable`: Agent service temporarily unavailable
- `validation_error`: Request validation failed
- `internal_error`: Unexpected server error

## Conversation Management API

### Get Conversation History

```
GET /api/v1/agent/conversations/{conversation_id}/history
```

**Query Parameters**:
- `user_id`: UUID (required)
- `jwt_token`: String (required)
- `limit`: Integer (optional, default 50, max 100)
- `offset`: Integer (optional, default 0)

**Response**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "string",
    "messages": [
      {
        "role": "user|assistant|system",
        "content": "string",
        "timestamp": "string",
        "metadata": "object"
      }
    ],
    "total_messages": "number",
    "has_more": "boolean"
  }
}
```

### Delete Conversation

```
DELETE /api/v1/agent/conversations/{conversation_id}
```

**Request Body**:
```json
{
  "user_id": "uuid",
  "jwt_token": "string"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "string",
    "deleted_at": "string"
  }
}
```

## Tool Integration Contracts

### MCP Tool Wrapper Interface

The agent will integrate with existing MCP tools through a standardized wrapper interface:

```python
class MCPToolWrapper:
    def __init__(self, tool_name: str, mcp_endpoint: str):
        self.tool_name = tool_name
        self.mcp_endpoint = mcp_endpoint

    async def call(self, parameters: dict, jwt_token: str) -> dict:
        """Call MCP tool with parameters and return result"""
        pass

    def get_schema(self) -> dict:
        """Return tool schema for OpenAI function calling"""
        pass
```

### Supported MCP Tools

1. **add_task**: Create new tasks
2. **list_tasks**: Retrieve and filter tasks
3. **complete_task**: Mark tasks as completed
4. **update_task**: Modify existing tasks
5. **delete_task**: Remove tasks (soft delete)

### Tool Schema Format

```json
{
  "name": "tool_name",
  "description": "Tool description for the agent",
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "Parameter description"
      }
    },
    "required": ["param1"]
  }
}
```

## Intent Recognition Contracts

### Intent Categories

```json
{
  "intents": {
    "create_task": {
      "description": "User wants to create a new task",
      "required_params": ["title"],
      "optional_params": ["description", "priority", "due_date", "recurrence_pattern"],
      "tool_mapping": "add_task"
    },
    "list_tasks": {
      "description": "User wants to see their tasks",
      "required_params": [],
      "optional_params": ["status", "priority", "limit", "offset"],
      "tool_mapping": "list_tasks"
    },
    "complete_task": {
      "description": "User wants to mark a task as completed",
      "required_params": ["task_id"],
      "optional_params": [],
      "tool_mapping": "complete_task"
    },
    "update_task": {
      "description": "User wants to modify an existing task",
      "required_params": ["task_id"],
      "optional_params": ["title", "description", "priority", "due_date"],
      "tool_mapping": "update_task"
    },
    "delete_task": {
      "description": "User wants to remove a task",
      "required_params": ["task_id"],
      "optional_params": [],
      "tool_mapping": "delete_task"
    },
    "clarification": {
      "description": "User input is ambiguous and needs clarification",
      "required_params": ["question"],
      "optional_params": [],
      "tool_mapping": null
    }
  }
}
```

### Parameter Extraction Patterns

```json
{
  "patterns": {
    "task_title": [
      "create a task to (.+)",
      "add (.+) to my tasks",
      "remind me to (.+)",
      "I need to (.+)"
    ],
    "priority": [
      "(high|urgent|low|medium) priority",
      "priority:?(high|urgent|low|medium)"
    ],
    "due_date": [
      "by (.+)",
      "due (.+)",
      "on (.+)",
      "before (.+)"
    ],
    "recurrence": [
      "every (day|week|month|year)",
      "repeat (daily|weekly|monthly|yearly)"
    ]
  }
}
```

## Error Handling Contracts

### Validation Errors

```json
{
  "validation_error": {
    "field": "string",
    "message": "string",
    "allowed_values": "array|null"
  }
}
```

### Tool Execution Errors

```json
{
  "tool_error": {
    "tool_name": "string",
    "error_code": "string",
    "message": "string",
    "retry_possible": "boolean",
    "suggested_action": "string|null"
  }
}
```

### Conversation Errors

```json
{
  "conversation_error": {
    "error_type": "context_limit|state_mismatch|persistence_failure",
    "message": "string",
    "recovery_options": "array"
  }
}
```

## Performance Contracts

### Response Time SLA

- **Agent Processing**: < 2000ms (p95)
- **Context Loading**: < 500ms (p95)
- **Tool Execution**: < 1000ms (p95)
- **Database Operations**: < 100ms (p95)

### Rate Limits

- **Requests per User**: 100 requests per minute
- **Concurrent Conversations**: 10 per user
- **Message Size**: 2000 characters per request

### Monitoring Contracts

### Required Metrics

- **Request Response Time**: Distribution and percentiles
- **Error Rates**: By error type and tool
- **Conversation Length**: Messages per conversation
- **Tool Usage**: Call frequency and success rates
- **User Satisfaction**: Implicit feedback through conversation completion

### Alerting Thresholds

- **High Error Rate**: > 5% error rate over 5 minutes
- **Slow Response**: p95 response time > 3000ms
- **Service Unavailability**: > 1% downtime over 1 hour
- **Database Issues**: Connection pool exhaustion

## Integration Testing Contracts

### Test Scenarios

1. **Happy Path Tests**
   - Task creation with various input formats
   - Multi-turn conversations with context retention
   - Error recovery and retry scenarios

2. **Edge Case Tests**
   - Very long conversations (>100 messages)
   - Ambiguous user inputs
   - Tool execution failures

3. **Performance Tests**
   - Concurrent user load testing
   - Memory usage under sustained load
   - Database query performance

### Mock Contracts

For testing, the following mocks should be available:

- **OpenAI API Mock**: Simulate GPT responses and tool calling
- **MCP Tool Mock**: Simulate tool execution and responses
- **Database Mock**: Simulate conversation persistence
- **JWT Validation Mock**: Simulate authentication scenarios