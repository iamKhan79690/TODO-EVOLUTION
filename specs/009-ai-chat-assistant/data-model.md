# Data Model: AI Chat Assistant Integration

**Date**: 2025-01-15
**Feature**: AI Chat Assistant Integration (009-ai-chat-assistant)
**Database**: PostgreSQL (extending existing schema)

This document defines the data models for the AI Chat Assistant feature, designed to extend the existing TODO application schema while maintaining performance and data integrity.

## Overview

The chat system introduces three new entity types:
1. **Conversations** - Chat sessions between users and AI assistant
2. **Messages** - Individual chat messages with rich metadata
3. **Conversation Contexts** - AI state management and conversation memory

## Database Schema

### Enhanced Users Table Extension

```sql
-- Existing users table extended with chat preferences
ALTER TABLE users ADD COLUMN IF NOT EXISTS chat_preferences JSONB DEFAULT '{}';
```

### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) GENERATED ALWAYS AS (
        CASE
            WHEN messages_count > 0 THEN (
                SELECT LEFT(content::text, 50)
                FROM messages
                WHERE messages.conversation_id = conversations.id
                AND messages.role = 'user'
                ORDER BY messages.timestamp ASC
                LIMIT 1
            )
            ELSE 'New Conversation'
        END
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    messages_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',

    -- Indexes for performance
    CONSTRAINT conversations_user_active_check CHECK (user_id IS NOT NULL),
    CONSTRAINT conversations_updated_check CHECK (updated_at >= created_at)
);

-- Performance indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_active ON conversations(user_id, is_active);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at DESC);
CREATE INDEX idx_conversations_metadata ON conversations USING GIN(metadata);
```

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_type VARCHAR(50) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'operation_result')),
    operation_status VARCHAR(20) DEFAULT 'delivered' CHECK (operation_status IN ('pending', 'processing', 'delivered', 'failed')),
    operation_type VARCHAR(50), -- For AI operations: 'add_task', 'complete_task', etc.
    operation_result JSONB, -- Results of AI operations
    error_details JSONB, -- Error information if operation failed
    metadata JSONB DEFAULT '{}',

    -- Audit fields
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,

    CONSTRAINT messages_content_not_empty CHECK (
        CASE
            WHEN message_type = 'text' THEN jsonb_typeof(content) = 'string' AND content::text <> ''
            ELSE true
        END
    ),
    CONSTRAINT messages_timestamp_order CHECK (timestamp IS NOT NULL),
    CONSTRAINT messages_retry_count_check CHECK (retry_count >= 0 AND retry_count <= 5)
);

-- Performance indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(conversation_id, timestamp DESC);
CREATE INDEX idx_messages_role ON messages(conversation_id, role);
CREATE INDEX idx_messages_operation_status ON messages(operation_status);
CREATE INDEX idx_messages_content ON messages USING GIN(content);
CREATE INDEX idx_messages_metadata ON messages USING GIN(metadata);
CREATE INDEX idx_messages_operation_type ON messages(operation_type) WHERE operation_type IS NOT NULL;

-- Full-text search index
CREATE INDEX idx_messages_content_fts ON messages USING GIN(
    to_tsvector('english', CASE WHEN jsonb_typeof(content) = 'string' THEN content::text ELSE '' END)
);
```

### Conversation Contexts Table

```sql
CREATE TABLE conversation_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    context_key VARCHAR(100) NOT NULL,
    context_value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(conversation_id, context_key),
    CONSTRAINT contexts_value_not_empty CHECK (jsonb_typeof(context_value) != 'null')
);

-- Performance indexes
CREATE INDEX idx_contexts_conversation_key ON conversation_contexts(conversation_id, context_key);
CREATE INDEX idx_contexts_expires ON conversation_contexts(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_contexts_value ON conversation_contexts USING GIN(context_value);
```

### Task Operations Log Table

```sql
CREATE TABLE task_operations_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    operation_type VARCHAR(50) NOT NULL CHECK (operation_type IN ('create_task', 'update_task', 'complete_task', 'delete_task')),
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    operation_data JSONB NOT NULL,
    result_status VARCHAR(20) NOT NULL CHECK (result_status IN ('success', 'failed', 'pending')),
    result_data JSONB,
    error_message TEXT,
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Tracking
    user_id UUID NOT NULL REFERENCES users(id),
    session_id VARCHAR(255),
    correlation_id VARCHAR(255),

    CONSTRAINT operations_log_data_not_empty CHECK (jsonb_typeof(operation_data) != 'null')
);

-- Performance indexes
CREATE INDEX idx_operations_conversation ON task_operations_log(conversation_id);
CREATE INDEX idx_operations_task ON task_operations_log(task_id) WHERE task_id IS NOT NULL;
CREATE INDEX idx_operations_user ON task_operations_log(user_id);
CREATE INDEX idx_operations_type_status ON task_operations_log(operation_type, result_status);
CREATE INDEX idx_operations_performed_at ON task_operations_log(performed_at DESC);
```

## Data Models Documentation

### Conversation Entity

**Purpose**: Represents a chat session between a user and AI assistant.

**Key Attributes**:
- `id`: Unique identifier
- `user_id`: Foreign key to users table (cascading delete)
- `title`: Auto-generated from first user message
- `is_active`: Whether conversation is currently active
- `messages_count`: Cached count of messages
- `last_message_at`: Timestamp of last message for sorting
- `metadata`: Flexible storage for conversation settings, preferences

**State Transitions**:
```
New → Active → Archived
```

### Message Entity

**Purpose**: Individual messages in conversations with rich metadata for AI operations.

**Key Attributes**:
- `id`: Unique identifier
- `conversation_id`: Foreign key to conversations
- `role`: 'user', 'assistant', or 'system'
- `content`: JSONB content (text, structured data, operation results)
- `message_type`: Type of message (text, image, file, operation_result)
- `operation_status`: Delivery and processing status
- `operation_type`: AI operation performed (add_task, complete_task, etc.)
- `operation_result`: Results of AI operations
- `error_details`: Error information if operation failed
- `metadata`: Flexible storage for additional message data

**Content Schema Examples**:
```json
// Text message
{
  "text": "Add task to buy groceries tomorrow",
  "intent_detected": "create_task",
  "entities": {
    "action": "add",
    "item": "groceries",
    "due_date": "tomorrow"
  }
}

// Operation result message
{
  "operation": "create_task",
  "task_id": "uuid",
  "result": "success",
  "task": {
    "id": "uuid",
    "title": "Buy groceries",
    "description": "",
    "completed": false,
    "created_at": "2025-01-15T10:30:00Z"
  }
}

// Error message
{
  "error": "task_creation_failed",
  "message": "Could not create task due to validation error",
  "details": {
    "validation_errors": ["Title is required"],
    "retry_possible": true
  }
}
```

**State Transitions**:
```
pending → processing → delivered/failed
```

### Conversation Context Entity

**Purpose**: AI state management and conversation memory for context-aware assistance.

**Key Attributes**:
- `id`: Unique identifier
- `conversation_id`: Foreign key to conversations
- `context_key`: Type of context (e.g., 'recent_tasks', 'user_preferences', 'conversation_state')
- `context_value`: JSON data storing the context
- `expires_at`: Optional expiration for time-sensitive context

**Common Context Types**:
```json
// Recent tasks context
{
  "context_key": "recent_tasks",
  "context_value": {
    "task_ids": ["uuid1", "uuid2", "uuid3"],
    "last_updated": "2025-01-15T10:30:00Z",
    "completion_count": 2
  }
}

// User preferences
{
  "context_key": "user_preferences",
  "context_value": {
    "preferred_task_view": "list",
    "default_reminder_time": "09:00",
    "task_categories": ["work", "personal", "shopping"]
  }
}

// Conversation state
{
  "context_key": "conversation_state",
  "context_value": {
    "current_topic": "task_management",
    "last_intent": "create_task",
    "pending_operations": ["uuid1"],
    "conversation_stage": "active"
  }
}
```

### Task Operations Log Entity

**Purpose**: Audit trail for all AI-performed task operations.

**Key Attributes**:
- `id`: Unique identifier
- `conversation_id`: Origin conversation
- `message_id`: Origin message
- `operation_type`: Type of operation performed
- `task_id`: Target task (if applicable)
- `operation_data`: Input data for operation
- `result_status`: Success/failure status
- `result_data`: Operation results
- `correlation_id`: For tracing across services

## Performance Optimizations

### Indexing Strategy

1. **Primary Queries**: Composite indexes for common query patterns
2. **JSONB Queries**: GIN indexes for JSON content searching
3. **Time-based Queries**: DESC indexes on timestamp fields
4. **Full-text Search**: Specialized indexes for message content

### Connection Pooling

```python
# Recommended PostgreSQL connection pool settings
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}
```

### Partitioning Strategy

For high-volume deployments (10,000+ messages/day):

```sql
-- Monthly message partitioning
CREATE TABLE messages_y2025m01 PARTITION OF messages
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE messages_y2025m02 PARTITION OF messages
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

## Data Migration Strategy

### Initial Setup

```sql
-- Add chat preferences to existing users
ALTER TABLE users ADD COLUMN IF NOT EXISTS chat_preferences JSONB DEFAULT '{}';

-- Create new chat tables
-- (See schema definitions above)
```

### Migration Scripts

```python
# migrations/001_add_chat_tables.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create conversations table
    op.execute("""
        CREATE TABLE conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_active BOOLEAN DEFAULT true,
            messages_count INTEGER DEFAULT 0,
            last_message_at TIMESTAMP WITH TIME ZONE,
            metadata JSONB DEFAULT '{}'
        );
    """)

    # Create remaining tables...
```

## Validation Rules

### Data Integrity

1. **Foreign Key Constraints**: All relationships properly constrained
2. **Check Constraints**: Enum values and business rules enforced
3. **Unique Constraints**: Prevent duplicate data
4. **JSON Validation**: JSONB content type checking

### Business Rules

1. **Message Ordering**: Messages must be chronologically ordered
2. **User Isolation**: All queries filtered by user_id
3. **Operation Status**: Valid transitions between states
4. **Context Expiration**: Expired contexts automatically cleaned

## Security Considerations

### Access Control

- **Row Level Security**: All tables include user_id for access control
- **Privacy**: Chat conversations isolated per user
- **Audit Trail**: All operations logged with user attribution

### Data Protection

- **Sensitive Data**: PII stored in encrypted JSONB fields
- **Retention**: Configurable data retention policies
- **Backup**: Regular backups of chat data

## Monitoring and Maintenance

### Performance Monitoring

```sql
-- Query performance monitoring
SELECT
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
WHERE schemaname = 'public'
AND tablename IN ('conversations', 'messages', 'conversation_contexts');
```

### Maintenance Tasks

- **Context Cleanup**: Daily cleanup of expired contexts
- **Statistics Update**: Weekly table statistics refresh
- **Index Maintenance**: Monthly index rebuild if needed
- **Partition Management**: Automatic partition creation

---

This data model provides a robust foundation for the AI Chat Assistant feature while maintaining performance, security, and scalability for the existing TODO application.