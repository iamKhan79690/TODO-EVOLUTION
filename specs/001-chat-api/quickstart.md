# Quickstart Guide: Chat API Endpoint

**Feature**: 001-chat-api
**Date**: 2025-01-13
**Target**: Developers integrating with the chat API

## Overview

The Chat API endpoint enables users to interact with the AI task management agent through natural language conversations. The API supports conversation continuity, tool execution tracking, and comprehensive error handling.

## Prerequisites

- Python 3.11+ environment
- Valid JWT authentication token
- Network access to the API endpoint
- Basic understanding of REST APIs

## Endpoint Details

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.todo-evolution.com`

### Authentication
- **Type**: Bearer Token (JWT)
- **Header**: `Authorization: Bearer <jwt_token>`
- **Validation**: Token must be valid, non-expired, and match user_id in URL

## Getting Started

### 1. Authentication Setup

Obtain a JWT token from your authentication system:

```bash
# Example: Get token from login endpoint
curl -X POST "https://auth.todo-evolution.com/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```

### 2. Send Your First Message

Start a new conversation:

```bash
curl -X POST "http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Create a task to review the project proposal",
    "jwt_token": "<your_jwt_token>"
  }'
```

**Response:**
```json
{
  "conversation_id": "conv_1234567890abcdef",
  "response": "I've created a task to review the project proposal. What would you like the deadline to be?",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "parameters": {
        "title": "Review project proposal",
        "description": "Review and analyze the project proposal document"
      },
      "execution_time_ms": 245.3,
      "status": "success"
    }
  ],
  "message": "Message processed successfully",
  "correlation_id": "req_1234567890abcdef"
}
```

### 3. Continue the Conversation

Use the `conversation_id` to continue the chat:

```bash
curl -X POST "http://localhost:8000/api/550e8400-e29b-41d4-a716-446655440000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "conversation_id": "conv_1234567890abcdef",
    "message": "Set the deadline for Friday at 2 PM",
    "jwt_token": "<your_jwt_token>"
  }'
```

## Request Format

### Required Fields
- `user_id` (string, UUID): User identifier
- `message` (string, 1-2000 chars): Your message to the AI agent
- `jwt_token` (string): Valid JWT authentication token

### Optional Fields
- `conversation_id` (string, UUID): Continue existing conversation

### Example Request Body
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_id": "conv_1234567890abcdef",
  "message": "List all my high-priority tasks for this week",
  "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Response Format

### Success Response (200 OK)
```json
{
  "conversation_id": "conv_1234567890abcdef",
  "response": "Here are your high-priority tasks for this week...",
  "tool_calls": [
    {
      "tool_name": "list_tasks",
      "parameters": {
        "priority": "high",
        "limit": 10
      },
      "execution_time_ms": 156.7,
      "status": "success"
    }
  ],
  "message": "Message processed successfully",
  "correlation_id": "req_1234567890abcdef"
}
```

### Error Responses

#### Validation Error (400 Bad Request)
```json
{
  "error": "validation_error",
  "message": "Message cannot be empty",
  "correlation_id": "req_1234567890abcdef",
  "details": {
    "field": "message",
    "constraint": "min_length=1"
  }
}
```

#### Authentication Error (401 Unauthorized)
```json
{
  "error": "authentication_error",
  "message": "Invalid or expired JWT token",
  "correlation_id": "req_1234567890abcdef"
}
```

#### Rate Limit Error (429 Too Many Requests)
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Please wait 60 seconds before sending another message.",
  "retry_after": 60,
  "correlation_id": "req_1234567890abcdef"
}
```

## Common Use Cases

### Task Management
```bash
curl -X POST "http://localhost:8000/api/{user_id}/chat" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "message": "Create a task to call the client about the quarterly report",
    "jwt_token": "{token}"
  }'
```

### Task Queries
```bash
curl -X POST "http://localhost:8000/api/{user_id}/chat" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "message": "Show me all tasks due this week",
    "jwt_token": "{token}"
  }'
```

### Task Updates
```bash
curl -X POST "http://localhost:8000/api/{user_id}/chat" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "message": "Mark the project review task as completed",
    "jwt_token": "{token}"
  }'
```

## Rate Limiting

- **Limit**: 60 messages per minute per user
- **Window**: Rolling 60-second window
- **Response**: HTTP 429 with `retry_after` header
- **Recovery**: Wait specified seconds before retrying

## Error Handling Best Practices

### 1. Always Check HTTP Status
```python
import requests

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"Response: {data['response']}")
else:
    error = response.json()
    print(f"Error {response.status_code}: {error['message']}")
```

### 2. Implement Retry Logic
```python
import time
import requests

def send_with_retry(url, payload, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            error = response.json()
            retry_after = error.get('retry_after', 60)
            if attempt < max_retries - 1:
                time.sleep(retry_after)
                continue
        else:
            raise Exception(f"Request failed: {response.status_code} - {response.text}")

    raise Exception("Max retries exceeded")
```

### 3. Use Correlation IDs for Debugging
```python
# Log correlation_id for support and debugging
if 'correlation_id' in data:
    print(f"Correlation ID: {data['correlation_id']}")
```

## Integration Examples

### JavaScript/Node.js
```javascript
const chatAPI = {
  baseURL: 'https://api.todo-evolution.com',
  token: 'your_jwt_token',
  userId: '550e8400-e29b-41d4-a716-446655440000',

  async sendMessage(message, conversationId = null) {
    const payload = {
      user_id: this.userId,
      message: message,
      jwt_token: this.token
    };

    if (conversationId) {
      payload.conversation_id = conversationId;
    }

    const response = await fetch(`${this.baseURL}/api/${this.userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Chat API Error: ${error.message}`);
    }

    return response.json();
  }
};

// Usage
try {
  const result = await chatAPI.sendMessage('Create a task for team meeting');
  console.log('AI Response:', result.response);
  console.log('Tool Calls:', result.tool_calls);
} catch (error) {
  console.error('Chat failed:', error.message);
}
```

### Python
```python
import requests
import json

class ChatAPI:
    def __init__(self, base_url, user_id, jwt_token):
        self.base_url = base_url
        self.user_id = user_id
        self.token = jwt_token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def send_message(self, message, conversation_id=None):
        payload = {
            'user_id': self.user_id,
            'message': message,
            'jwt_token': self.token
        }

        if conversation_id:
            payload['conversation_id'] = conversation_id

        response = requests.post(
            f'{self.base_url}/api/{self.user_id}/chat',
            json=payload,
            headers=self.headers
        )

        response.raise_for_status()
        return response.json()

# Usage
chat = ChatAPI('https://api.todo-evolution.com', 'user123', 'jwt_token_here')
result = chat.send_message('What are my upcoming deadlines?')
print(f"AI Response: {result['response']}")
```

## Testing

### Basic Connectivity Test
```bash
# Test basic connectivity
curl -v -X POST "http://localhost:8000/api/{user_id}/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Authentication Test
```bash
# Test with invalid token
curl -X POST "http://localhost:8000/api/{user_id}/chat" \
  -H "Authorization: Bearer invalid_token" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Rate Limit Test
```bash
# Send rapid requests to test rate limiting
for i in {1..70}; do
  curl -X POST "http://localhost:8000/api/{user_id}/chat" \
    -H "Authorization: Bearer {token}" \
    -H "Content-Type: application/json" \
    -d '{"message": "test message"}' &
done
wait
```

## Support

### Documentation
- [API Specification](./contracts/openapi.yaml) - Complete OpenAPI specification
- [Data Models](./data-model.md) - Entity relationships and validation rules

### Getting Help
- Check response `correlation_id` for debugging
- Monitor HTTP status codes for error types
- Review rate limiting headers for request limits
- Contact support with conversation_id and correlation_id

### Common Issues
- **401 Unauthorized**: Check JWT token validity and user_id match
- **429 Too Many Requests**: Implement retry logic with `retry_after` delay
- **400 Bad Request**: Validate message length (1-2000 characters)
- **500 Internal Server Error**: Report correlation_id to support team

## Next Steps

1. **Integrate with your application** using the provided examples
2. **Implement error handling** for all HTTP status codes
3. **Add logging** with correlation IDs for debugging
4. **Test rate limiting** behavior in your integration
5. **Monitor performance** and adjust retry logic as needed

For more advanced integration patterns, see the complete [OpenAPI specification](./contracts/openapi.yaml).