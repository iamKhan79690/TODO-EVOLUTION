# Data Model: OpenAI Agent Architecture

**Date**: 2025-01-12
**Feature**: OpenAI Agent Architecture
**Purpose**: Define data structures for conversation management and agent operation

## Core Entities

### ConversationContext

Represents the conversational state between a user and the AI agent, enabling stateless operation through persistent storage.

**Fields**:
- `id`: UUID - Primary key
- `user_id`: UUID - Foreign key to users table (user isolation)
- `conversation_id`: String - Unique identifier for conversation thread
- `message_index`: Integer - Sequential position in conversation
- `role`: Enum (user, assistant, system) - Message sender role
- `content`: Text - Message content
- `metadata`: JSON - Additional message metadata (timestamps, tool calls, etc.)
- `created_at`: Timestamp - Message creation time
- `updated_at`: Timestamp - Last update time

**Relationships**:
- Many-to-one with User (user_id)
- One-to-many with AgentSession (conversation_id)

**Constraints**:
- Unique constraint on (user_id, conversation_id, message_index)
- Foreign key constraint to users table
- NOT NULL on required fields (user_id, conversation_id, role, content)

### AgentSession

Manages user sessions and conversation metadata for the agent.

**Fields**:
- `id`: UUID - Primary key
- `user_id`: UUID - Foreign key to users table
- `conversation_id`: String - Unique conversation identifier
- `last_activity`: Timestamp - Last interaction timestamp
- `session_metadata`: JSON - Session preferences and context
- `created_at`: Timestamp - Session creation time
- `updated_at`: Timestamp - Last update time

**Relationships**:
- Many-to-one with User (user_id)
- One-to-many with ConversationContext (conversation_id)

**Constraints**:
- Unique constraint on (user_id, conversation_id)
- Foreign key constraint to users table
- NOT NULL on required fields

### UserIntent

Captures extracted user intents from natural language processing.

**Fields**:
- `id`: UUID - Primary key
- `conversation_context_id`: UUID - Foreign key to ConversationContext
- `intent_type`: String - Intent classification (create_task, list_tasks, complete_task, etc.)
- `confidence_score`: Float - Confidence in intent classification (0.0-1.0)
- `extracted_parameters`: JSON - Parameters extracted from user input
- `tool_mapping`: String - Target MCP tool for this intent
- `validation_status`: Enum (pending, validated, failed) - Parameter validation status
- `created_at`: Timestamp - Intent extraction time

**Relationships**:
- Many-to-one with ConversationContext (conversation_context_id)

**Constraints**:
- Foreign key constraint to conversation_contexts table
- NOT NULL on required fields (intent_type, tool_mapping)

### ToolExecution

Tracks execution of MCP tools triggered by the agent.

**Fields**:
- `id`: UUID - Primary key
- `user_intent_id`: UUID - Foreign key to UserIntent
- `tool_name`: String - Name of executed MCP tool
- `tool_parameters`: JSON - Parameters passed to tool
- `execution_status`: Enum (pending, success, failed, timeout)
- `execution_result`: JSON - Tool execution response
- `error_details`: JSON - Error information if execution failed
- `execution_duration_ms`: Integer - Execution time in milliseconds
- `created_at`: Timestamp - Tool execution start time
- `completed_at`: Timestamp - Tool completion time

**Relationships**:
- Many-to-one with UserIntent (user_intent_id)

**Constraints**:
- Foreign key constraint to user_intents table
- NOT NULL on required fields (tool_name, execution_status)

### ConversationSummary

Stores compressed summaries of long conversations for context management.

**Fields**:
- `id`: UUID - Primary key
- `user_id`: UUID - Foreign key to users table
- `conversation_id`: String - Conversation identifier
- `summary_text`: Text - AI-generated conversation summary
- `summary_metadata`: JSON - Summary generation metadata
- `covers_message_range`: JSON - Range of messages summarized (start_index, end_index)
- `created_at`: Timestamp - Summary generation time
- `expires_at`: Timestamp - Summary expiration time

**Relationships**:
- Many-to-one with User (user_id)

**Constraints**:
- Foreign key constraint to users table
- Unique constraint on (user_id, conversation_id, covers_message_range)

## Entity Relationships

```
User (1) ←→ (N) AgentSession (1) ←→ (N) ConversationContext (1) ←→ (N) UserIntent (1) ←→ (N) ToolExecution
User (1) ←→ (N) ConversationSummary
```

## Database Schema

### Create Statements

```sql
-- Conversation Context Storage
CREATE TABLE conversation_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    message_index INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_conversation_message UNIQUE(user_id, conversation_id, message_index),
    CONSTRAINT fk_conversation_contexts_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Agent Session Management
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT unique_user_conversation UNIQUE(user_id, conversation_id),
    CONSTRAINT fk_agent_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User Intent Tracking
CREATE TABLE user_intents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_context_id UUID NOT NULL,
    intent_type VARCHAR(100) NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    extracted_parameters JSONB NOT NULL DEFAULT '{}',
    tool_mapping VARCHAR(100) NOT NULL,
    validation_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (validation_status IN ('pending', 'validated', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT fk_user_intents_context FOREIGN KEY (conversation_context_id) REFERENCES conversation_contexts(id) ON DELETE CASCADE
);

-- Tool Execution Tracking
CREATE TABLE tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_intent_id UUID NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    tool_parameters JSONB NOT NULL DEFAULT '{}',
    execution_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (execution_status IN ('pending', 'success', 'failed', 'timeout')),
    execution_result JSONB,
    error_details JSONB,
    execution_duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_tool_executions_intent FOREIGN KEY (user_intent_id) REFERENCES user_intents(id) ON DELETE CASCADE
);

-- Conversation Summaries
CREATE TABLE conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    conversation_id VARCHAR(255) NOT NULL,
    summary_text TEXT NOT NULL,
    summary_metadata JSONB DEFAULT '{}',
    covers_message_range JSONB NOT NULL, -- {"start_index": 0, "end_index": 50}
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT unique_conversation_summary UNIQUE(user_id, conversation_id, covers_message_range),
    CONSTRAINT fk_conversation_summaries_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Indexes

```sql
-- Performance Indexes
CREATE INDEX idx_conversation_contexts_lookup ON conversation_contexts(user_id, conversation_id, message_index);
CREATE INDEX idx_conversation_contexts_user ON conversation_contexts(user_id, created_at);
CREATE INDEX idx_conversation_contexts_conversation ON conversation_contexts(conversation_id, message_index);

CREATE INDEX idx_agent_sessions_user ON agent_sessions(user_id, last_activity);
CREATE INDEX idx_agent_sessions_conversation ON agent_sessions(conversation_id);

CREATE INDEX idx_user_intents_context ON user_intents(conversation_context_id);
CREATE INDEX idx_user_intents_type ON user_intents(intent_type, created_at);

CREATE INDEX idx_tool_executions_intent ON tool_executions(user_intent_id);
CREATE INDEX idx_tool_executions_status ON tool_executions(execution_status, created_at);

CREATE INDEX idx_conversation_summaries_user ON conversation_summaries(user_id, expires_at);
CREATE INDEX idx_conversation_summaries_conversation ON conversation_summaries(conversation_id);
```

## Validation Rules

### ConversationContext Validation
- `message_index` must be sequential for each conversation
- `role` must be one of: user, assistant, system
- `content` cannot be empty
- `metadata` must be valid JSON

### AgentSession Validation
- `conversation_id` must be unique per user
- `last_activity` cannot be in the future
- `session_metadata` must be valid JSON

### UserIntent Validation
- `confidence_score` must be between 0.0 and 1.0
- `intent_type` must match defined intent categories
- `extracted_parameters` must be valid JSON
- `tool_mapping` must correspond to available MCP tools

### ToolExecution Validation
- `execution_status` must be one of: pending, success, failed, timeout
- `execution_duration_ms` must be non-negative
- `tool_parameters` must be valid JSON

## Data Retention Policies

### Conversation Context
- Retain active conversation context for 30 days
- Archive conversations older than 30 days
- Delete archived conversations after 90 days

### Agent Sessions
- Clean up inactive sessions after 7 days
- Maintain session statistics for analytics

### Tool Executions
- Retain execution logs for 30 days for debugging
- Aggregate performance metrics for monitoring

### Conversation Summaries
- Keep summaries for 90 days
- Expire and regenerate summaries as needed

## Privacy and Security

### Data Encryption
- Encrypt conversation content at rest
- Hash conversation identifiers for privacy
- Secure metadata storage with sensitive data masking

### Access Controls
- User isolation enforced at database level
- Role-based access for conversation analytics
- Audit logging for conversation access

### Data Minimization
- Store only necessary conversation data
- Regular cleanup of temporary data
- User-controlled conversation deletion