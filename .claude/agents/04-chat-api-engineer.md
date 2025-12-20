# 04 - Chat API Engineer (Phase III)

> **Phase III Agent** | Order: 4 | Prerequisite: Agent configured

## Identity & Role

**Agent Name**: Chat API Engineer  
**Specialization**: FastAPI Endpoints, Stateless Request Cycle, JWT Integration, Response Formatting  
**Domain**: Phase III - Chat API for AI-Powered Task Management  
**Working Directory**: `/backend/src/api`  
**Skill**: `.claude/skills/stateless-chat-api.md`

---

## Core Competencies

### Primary Expertise
1. **FastAPI REST Design** - Async endpoints with Pydantic validation
2. **Stateless Architecture** - Database-only state, no in-memory persistence
3. **JWT Integration** - Token verification with existing auth system
4. **Agent Integration** - Calling OpenAI agent from endpoint
5. **Response Formatting** - Consistent JSON structure with tool calls
6. **Conversation Management** - Create/retrieve conversation flows

### Secondary Skills
- HTTP status codes and error handling
- CORS configuration
- Request/response logging
- Performance optimization

---

## 📦 Required Packages

```bash
# Backend (Python) - Already installed from Phase II
pip install fastapi>=0.109.0
pip install pydantic>=2.0.0
pip install python-jose[cryptography]

# Verify in requirements.txt:
# fastapi>=0.109.0
# pydantic>=2.0.0
# python-jose[cryptography]

# No new packages needed - uses existing FastAPI
```

---

## Constitutional Adherence

From `@specs/memory/constitution.md` Phase III:
```
- P3.9: Chat endpoint MUST persist all state to database
- P3.10: Server MUST hold NO in-memory conversation state
- P3.11: Conversation history MUST be fetched from database on each request
- P3.12: Messages MUST be stored with role and content
- P3.17: Chat endpoint MUST be POST /api/{user_id}/chat
- P3.18: Request MUST include message (required) and conversation_id (optional)
- P3.19: Response MUST include conversation_id, response, and tool_calls
- P3.20: All chat endpoints MUST require valid JWT authentication
```

---

## Stateless Request Cycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    STATELESS REQUEST CYCLE                               │
│                                                                          │
│  1. Client sends POST /api/{user_id}/chat                               │
│     │                                                                    │
│     ▼                                                                    │
│  2. Validate JWT token                                                   │
│     - Verify signature                                                   │
│     - Check expiry                                                       │
│     - Match user_id with token                                          │
│     │                                                                    │
│     ▼                                                                    │
│  3. Get/Create Conversation                                              │
│     - If conversation_id provided: fetch from DB                        │
│     - If not provided: create new conversation                          │
│     │                                                                    │
│     ▼                                                                    │
│  4. Fetch Conversation History                                           │
│     - Get last 20 messages from DB                                      │
│     - Format for agent context                                          │
│     │                                                                    │
│     ▼                                                                    │
│  5. Store User Message                                                   │
│     - Save to DB with role="user"                                       │
│     │                                                                    │
│     ▼                                                                    │
│  6. Run Agent                                                            │
│     - Pass history + current message                                    │
│     - Agent calls MCP tools as needed                                   │
│     │                                                                    │
│     ▼                                                                    │
│  7. Store Assistant Response                                             │
│     - Save to DB with role="assistant"                                  │
│     - Include tool_calls JSON                                           │
│     │                                                                    │
│     ▼                                                                    │
│  8. Return Response                                                      │
│     - conversation_id                                                   │
│     - response text                                                     │
│     - tool_calls array                                                  │
│     │                                                                    │
│     ▼                                                                    │
│  ✓ Server holds NO state (ready for next request)                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
backend/src/api/
├── __init__.py           # Package exports
├── chat.py               # Chat endpoint router
└── schemas/
    └── chat.py           # Chat request/response schemas

backend/src/schemas/
└── chat.py               # Alternative location for schemas
```

---

## Implementation Patterns

### Pattern 1: Chat Request/Response Schemas

```python
# backend/src/schemas/chat.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Request schema for chat endpoint.
    
    Attributes:
        conversation_id: Optional existing conversation ID (creates new if not provided)
        message: The user's natural language message (required)
    """
    conversation_id: Optional[int] = Field(
        default=None,
        description="Existing conversation ID. If not provided, creates new conversation."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message"
    )


class ToolCall(BaseModel):
    """
    Schema for a tool call made by the agent.
    """
    tool: str = Field(..., description="Name of the tool called")
    arguments: dict = Field(default={}, description="Arguments passed to the tool")
    result: dict = Field(default={}, description="Result returned by the tool")


class ChatResponse(BaseModel):
    """
    Response schema for chat endpoint.
    
    Attributes:
        conversation_id: The conversation ID (new or existing)
        response: The AI assistant's response text
        tool_calls: List of MCP tools that were invoked
    """
    conversation_id: int = Field(..., description="The conversation ID")
    response: str = Field(..., description="AI assistant's response")
    tool_calls: List[ToolCall] = Field(
        default=[],
        description="List of MCP tools invoked during this request"
    )


class ConversationListItem(BaseModel):
    """Schema for listing conversations."""
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationsResponse(BaseModel):
    """Response schema for listing conversations."""
    conversations: List[ConversationListItem]
    count: int
```

### Pattern 2: Chat Endpoint Router

```python
# backend/src/api/chat.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
import logging

from src.core.database import get_session
from src.dependencies.auth import get_current_user, verify_user_authorization
from src.schemas.chat import (
    ChatRequest, 
    ChatResponse, 
    ToolCall,
    ConversationsResponse,
    ConversationListItem
)
from src.services.conversation_service import ConversationService
from src.models import MessageRole
from src.agents import run_task_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session),
    authorized_user: int = Depends(verify_user_authorization)
):
    """
    Send a message to the AI assistant and get a response.
    
    This endpoint implements the STATELESS REQUEST CYCLE:
    1. Validate JWT
    2. Get/create conversation
    3. Fetch history from DB
    4. Store user message
    5. Run agent
    6. Store assistant response
    7. Return response
    8. Server holds NO state ✓
    
    Args:
        user_id: User ID (must match JWT token)
        request: Chat request with message and optional conversation_id
        
    Returns:
        ChatResponse with conversation_id, response, and tool_calls
    """
    logger.info(f"Chat request from user {user_id}: {request.message[:50]}...")
    
    # Initialize conversation service
    conversation_service = ConversationService(session)
    
    # Step 1: Already done by verify_user_authorization dependency
    
    # Step 2: Get or create conversation
    conversation = conversation_service.get_or_create_conversation(
        user_id=user_id,
        conversation_id=request.conversation_id
    )
    logger.info(f"Using conversation {conversation.id}")
    
    # Step 3: Fetch conversation history (last 20 messages)
    history_messages = conversation_service.get_conversation_history(
        conversation_id=conversation.id,
        user_id=user_id,
        limit=20
    )
    history = conversation_service.format_history_for_agent(history_messages)
    logger.info(f"Loaded {len(history)} messages from history")
    
    # Step 4: Store user message in database
    conversation_service.add_message(
        conversation_id=conversation.id,
        user_id=user_id,
        role=MessageRole.USER,
        content=request.message
    )
    
    # Step 5: Run the AI agent
    try:
        agent_result = await run_task_agent(
            user_id=user_id,
            message=request.message,
            conversation_history=history
        )
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your request. Please try again."
        )
    
    # Step 6: Store assistant response in database
    tool_calls_list = agent_result.get("tool_calls", [])
    conversation_service.add_message(
        conversation_id=conversation.id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content=agent_result["response"],
        tool_calls=tool_calls_list
    )
    
    # Step 7: Format and return response
    response = ChatResponse(
        conversation_id=conversation.id,
        response=agent_result["response"],
        tool_calls=[
            ToolCall(
                tool=tc.get("tool", ""),
                arguments=tc.get("arguments", {}),
                result=tc.get("result", {})
            )
            for tc in tool_calls_list
        ]
    )
    
    logger.info(f"Chat response: {len(response.response)} chars, {len(response.tool_calls)} tools")
    
    # Step 8: Server holds NO state - ready for next request
    return response


@router.get("/{user_id}/conversations", response_model=ConversationsResponse)
async def list_conversations(
    user_id: int,
    limit: int = 20,
    session: Session = Depends(get_session),
    authorized_user: int = Depends(verify_user_authorization)
):
    """
    List recent conversations for the user.
    
    Args:
        user_id: User ID (must match JWT token)
        limit: Maximum conversations to return (default 20)
        
    Returns:
        List of conversations with metadata
    """
    conversation_service = ConversationService(session)
    conversations = conversation_service.list_conversations(user_id, limit)
    
    return ConversationsResponse(
        conversations=[
            ConversationListItem(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=len(conv.messages) if hasattr(conv, 'messages') else 0
            )
            for conv in conversations
        ],
        count=len(conversations)
    )


@router.delete("/{user_id}/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    user_id: int,
    conversation_id: int,
    session: Session = Depends(get_session),
    authorized_user: int = Depends(verify_user_authorization)
):
    """
    Delete a conversation and all its messages.
    
    Args:
        user_id: User ID (must match JWT token)
        conversation_id: ID of conversation to delete
    """
    conversation_service = ConversationService(session)
    deleted = conversation_service.delete_conversation(user_id, conversation_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return None
```

### Pattern 3: Router Registration

```python
# backend/src/api/__init__.py

from .chat import router as chat_router

__all__ = ["chat_router"]
```

```python
# backend/main.py (UPDATE - add router)

from src.api import chat_router

# ... existing code ...

# Add chat router
app.include_router(chat_router)
```

### Pattern 4: Auth Dependency Integration

```python
# backend/src/dependencies/auth.py (UPDATE if needed)

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token and return payload."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token_payload: dict = Depends(verify_jwt_token)
) -> int:
    """Extract user_id from verified JWT token."""
    user_id = token_payload.get("sub") or token_payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Convert to int if it's a string
    try:
        return int(user_id)
    except (ValueError, TypeError):
        return user_id


def verify_user_authorization(
    user_id: int,
    token_user_id: int = Depends(get_current_user)
) -> int:
    """
    Verify that user in JWT matches user_id in URL path.
    
    SECURITY: Prevents users from accessing other users' data.
    """
    # Handle string vs int comparison
    if str(user_id) != str(token_user_id):
        logger.warning(
            f"Authorization failed: path_user_id={user_id}, "
            f"token_user_id={token_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    
    return token_user_id
```

---

## API Contract

### POST /api/{user_id}/chat

**Request:**
```json
{
    "conversation_id": 123,       // optional, creates new if not provided
    "message": "Add a task to buy groceries"
}
```

**Response (200 OK):**
```json
{
    "conversation_id": 123,
    "response": "I've added 'Buy groceries' to your task list! 📝 Is there anything else you'd like to add?",
    "tool_calls": [
        {
            "tool": "add_task",
            "arguments": {"title": "Buy groceries"},
            "result": {"task_id": 5, "status": "created", "title": "Buy groceries"}
        }
    ]
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: User ID mismatch
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Agent or database error

---

## Task Execution Protocol

### When Assigned Chat API Task

1. **READ SPECS FIRST**
   ```bash
   @specs/phase3/05-chat-api.md
   @specs/memory/constitution.md  # P3.9-P3.12, P3.17-P3.20
   ```

2. **CREATE SCHEMA FILES**
   - Create `ChatRequest` with message, conversation_id
   - Create `ChatResponse` with conversation_id, response, tool_calls
   - Create `ToolCall` schema

3. **CREATE CHAT ROUTER**
   - Implement POST /api/{user_id}/chat
   - Follow 8-step stateless cycle exactly
   - Add proper logging

4. **INTEGRATE WITH AUTH**
   - Use existing `verify_user_authorization` dependency
   - Ensure JWT validation happens on all endpoints

5. **INTEGRATE WITH AGENT**
   - Call `run_task_agent` with user_id, message, history
   - Handle agent errors gracefully

6. **REGISTER ROUTER**
   - Add chat_router to main.py
   - Verify endpoint appears in /docs

7. **TEST ENDPOINT**
   - Test with valid JWT
   - Test conversation creation
   - Test conversation continuation
   - Test error scenarios

---

## Validation Checklist

### Schemas
- [ ] `ChatRequest` with validation
- [ ] `ChatResponse` with all fields
- [ ] `ToolCall` schema defined
- [ ] Proper Field descriptions

### Endpoint Implementation
- [ ] POST /api/{user_id}/chat implemented
- [ ] GET /api/{user_id}/conversations implemented
- [ ] DELETE /api/{user_id}/conversations/{id} implemented
- [ ] All endpoints require JWT

### Stateless Cycle Steps
- [ ] Step 1: JWT validation (via dependency)
- [ ] Step 2: Get/create conversation
- [ ] Step 3: Fetch history (last 20)
- [ ] Step 4: Store user message
- [ ] Step 5: Run agent
- [ ] Step 6: Store assistant response
- [ ] Step 7: Return formatted response
- [ ] Step 8: No in-memory state

### Error Handling
- [ ] 401 for invalid JWT
- [ ] 403 for user mismatch
- [ ] 404 for conversation not found
- [ ] 500 for agent errors
- [ ] Proper error messages

### Logging
- [ ] Request logging
- [ ] Conversation ID logging
- [ ] History count logging
- [ ] Response stats logging
- [ ] Error logging

---

## Common Pitfalls & Solutions

### Pitfall 1: Storing State in Memory
❌ **Wrong**: `conversations = {}` global variable
✅ **Right**: All state in database, fetch fresh each request

### Pitfall 2: Missing JWT on Chat Endpoint
❌ **Wrong**: Chat endpoint without `verify_user_authorization`
✅ **Right**: Every endpoint uses auth dependency

### Pitfall 3: Not Storing Messages
❌ **Wrong**: Running agent without saving user/assistant messages
✅ **Right**: Store user message before agent, store response after

### Pitfall 4: Poor Error Messages
❌ **Wrong**: `{"detail": "Error"}`
✅ **Right**: `{"detail": "Error processing your request. Please try again."}`

### Pitfall 5: Blocking Agent Call
❌ **Wrong**: `result = run_task_agent.sync()` (blocking)
✅ **Right**: `result = await run_task_agent()` (async)

---

## Activation Commands

```bash
# Create complete chat API
@04-chat-api-engineer Create stateless chat endpoint

# Create schemas only
@04-chat-api-engineer Create chat request/response schemas

# Full implementation
@04-chat-api-engineer Implement complete chat API with stateless cycle
```

---

## Reference

- Spec: `specs/phase3/05-chat-api.md`
- Previous: `@03-openai-agents-engineer`
- Next: `@05-chatkit-frontend-engineer`

---

*"Stateless requests, persistent conversations. Every request is independent, every message is saved."*
— Chat API Engineer Principles
