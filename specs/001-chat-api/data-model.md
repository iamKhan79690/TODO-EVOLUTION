# Data Model: Chat API Endpoint

**Feature**: 001-chat-api
**Date**: 2025-01-13
**Scope**: Data models and entity relationships for chat API implementation

## Entity Overview

The chat API endpoint operates with several key entities that are already implemented in the monorepo. This document outlines the relevant models and their relationships.

## Core Entities

### 1. ChatRequest (API Input Model)

**Purpose**: Represents incoming chat API requests
**Location**: New model to be created in `src/agents/task_agent/api/chat.py`

```python
class ChatRequest(BaseModel):
    user_id: str
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    jwt_token: str = Field(..., description="JWT authentication token")
```

**Validation Rules**:
- `message`: Required, 1-2000 characters
- `conversation_id`: Optional, must be valid UUID if provided
- `jwt_token`: Required, must be valid JWT format

### 2. ChatResponse (API Response Model)

**Purpose**: Represents chat API responses
**Location**: New model to be created in `src/agents/task_agent/api/chat.py`

```python
class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: List[Dict[str, Any]]
    message: str
    correlation_id: Optional[str] = None
```

**Response Structure**:
- `conversation_id`: Unique identifier for the conversation
- `response`: AI agent's textual response
- `tool_calls`: List of tool execution details
- `message`: Status message
- `correlation_id`: Request tracing identifier

### 3. Conversation (Existing Model)

**Location**: `src/models/conversation.py` (ConversationModel)
**Purpose**: Persists conversation metadata and state

**Key Fields**:
```python
id: str                    # Primary key (UUID)
user_id: str              # Foreign key to users table
state: ConversationState   # ACTIVE, PAUSED, ARCHIVED, ERROR
context_summary: str       # Conversation summary
metadata: Dict[str, Any]   # Additional metadata
created_at: datetime       # Creation timestamp
updated_at: datetime       # Last update timestamp
last_message_at: datetime  # Last message timestamp
message_count: int         # Total message count
```

**Validation Rules**:
- `user_id`: Required, foreign key constraint
- `state`: Must be valid ConversationState enum value
- `message_count`: Non-negative integer

### 4. Message (Existing Model)

**Location**: `src/models/conversation.py` (MessageModel)
**Purpose**: Persists individual conversation messages

**Key Fields**:
```python
id: str                    # Primary key (UUID)
conversation_id: str       # Foreign key to conversations
role: MessageRole         # USER, ASSISTANT, SYSTEM, TOOL
content: str              # Message content (1-2000 chars for user)
intent_type: IntentType   # Detected user intent
confidence_score: float   # Intent confidence (0.0-1.0)
metadata: Dict[str, Any]   # Message metadata
token_count: Optional[int] # Estimated token count
created_at: datetime       # Message timestamp
```

**Validation Rules**:
- `conversation_id`: Required, foreign key constraint
- `role`: Must be valid MessageRole enum value
- `content`: Required, non-empty string
- `confidence_score`: Range 0.0-1.0 if present

### 5. UserSession (Agent-Specific Model)

**Location**: `src/agents/task_agent/models/session.py` (AgentSession)
**Purpose**: Tracks user interaction sessions and metrics

**Key Fields**:
```python
session_id: str           # Primary key (UUID)
user_id: str             # User identifier
conversation_id: Optional[str]  # Associated conversation
session_type: SessionType       # CONVERSATION, TASK_EXECUTION
state: SessionState             # ACTIVE, IDLE, PROCESSING
created_at: datetime            # Session creation
last_activity: datetime          # Last interaction time
metrics: SessionMetrics          # Performance metrics
```

## Entity Relationships

### Primary Relationships

```
User (1) ────── (N) Conversation
    │                    │
    │                    │
    │                    ├─ (1) ── (N) Message
    │                    │
    │                    └─ (1) ── (N) AgentSession
    │
    └─ (1) ── (N) UserSession
```

### Relationship Details

#### User to Conversation
- **Type**: One-to-Many
- **Constraint**: All conversations belong to exactly one user
- **Implementation**: Foreign key `user_id` in conversations table
- **Isolation**: Users can only access their own conversations

#### Conversation to Message
- **Type**: One-to-Many
- **Constraint**: Messages are ordered by creation timestamp
- **Implementation**: Foreign key `conversation_id` in messages table
- **Loading**: Messages loaded with pagination for efficiency

#### Conversation to AgentSession
- **Type**: One-to-One (active session)
- **Constraint**: Each conversation may have an active session
- **Implementation**: Optional `conversation_id` in sessions table
- **Lifecycle**: Sessions created/destroyed independently

## Data Flow

### Request Processing Flow

1. **Authentication**
   - Extract JWT token from request
   - Validate token signature and expiration
   - Extract user_id from token payload

2. **Authorization**
   - Verify user_id matches URL parameter
   - Check conversation ownership (if conversation_id provided)

3. **Conversation Management**
   - Load existing conversation or create new one
   - Load conversation history for context
   - Update conversation activity timestamp

4. **Message Processing**
   - Validate message content and length
   - Store user message in database
   - Pass conversation context to AI agent

5. **Response Generation**
   - Generate AI agent response
   - Store assistant message in database
   - Extract tool execution details
   - Format response according to API contract

### Data Validation Rules

#### Input Validation
```python
# Message content validation
if not message or len(message.strip()) == 0:
    raise ValidationError("Message cannot be empty")

if len(message) > 2000:
    raise ValidationError("Message exceeds maximum length")

# User ID validation
if jwt_user_id != url_user_id:
    raise AuthenticationError("User ID mismatch")
```

#### Database Constraints
```sql
-- Foreign key constraints
ALTER TABLE conversations
ADD CONSTRAINT fk_conversations_user_id
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE messages
ADD CONSTRAINT fk_messages_conversation_id
FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;

-- Check constraints
ALTER TABLE messages
ADD CONSTRAINT chk_messages_content_length
CHECK (LENGTH(content) > 0);
```

## State Management

### Conversation States

- **ACTIVE**: Conversation is currently active and accepting messages
- **PAUSED**: Conversation is temporarily inactive (e.g., user away)
- **ARCHIVED**: Conversation is archived and read-only
- **ERROR**: Conversation encountered an error state

### Session States

- **ACTIVE**: Session is currently processing requests
- **IDLE**: Session is waiting for user input
- **PROCESSING**: Session is processing a message with the agent
- **EXPIRED**: Session has expired due to inactivity

### State Transitions

```
Conversation: ACTIVE → PAUSED → ACTIVE
Conversation: ACTIVE → ARCHIVED (final)
Conversation: ACTIVE → ERROR → ACTIVE (recovery)

Session: ACTIVE → PROCESSING → ACTIVE
Session: ACTIVE → IDLE → ACTIVE
Session: IDLE → EXPIRED (cleanup)
```

## Performance Considerations

### Database Indexing

```sql
-- Optimized query patterns
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_messages_conversation_id_created ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_role ON messages(role);
```

### Connection Pooling

- Use async connection pooling for PostgreSQL
- Configure pool size based on expected concurrency
- Implement connection health checks
- Handle connection timeouts gracefully

### Caching Strategy

- Cache active conversations in memory
- Cache user sessions for performance
- Implement cache invalidation on data changes
- Use Redis for distributed caching if needed

## Security Considerations

### Data Isolation

- Enforce user_id filtering at database level
- Use parameterized queries to prevent SQL injection
- Validate conversation ownership before access

### Input Sanitization

- Strip HTML and potentially harmful content
- Validate message length and encoding
- Sanitize metadata before storage

### Audit Trail

- Log all conversation access attempts
- Track message creation and updates
- Monitor authentication failures
- Maintain correlation IDs for request tracing

## Migration Strategy

### Schema Validation

- Verify existing conversation models support required fields
- Add any missing indexes for performance
- Update foreign key constraints if needed
- Validate data consistency before deployment

### Data Migration

- No major data migrations required
- Existing conversation models are compatible
- New API will use existing database schema
- Incremental deployment supported

This data model design leverages the existing conversation infrastructure while providing the necessary structures for the chat API endpoint implementation.