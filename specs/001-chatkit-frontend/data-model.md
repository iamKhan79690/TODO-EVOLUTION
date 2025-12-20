# Data Model: ChatKit Frontend Architecture

**Date**: 2025-01-14
**Feature**: ChatKit Frontend Architecture
**Status**: Complete

## Overview

The ChatKit frontend manages three primary data entities: Conversations, Messages, and User Sessions. The data model is designed to support real-time chat functionality, conversation persistence, and seamless synchronization between client-side storage and backend APIs.

## Key Data Structures

### Conversation Model

The conversation entity represents a complete chat session between a user and the AI assistant.

```typescript
interface Conversation {
  id: string
  title: string
  userId: string
  messageCount: number
  lastMessageAt: Date
  createdAt: Date
  updatedAt: Date
  isArchived: boolean

  // Computed properties
  preview: string
  unreadCount: number
}
```

**Validation Rules**:
- `id`: Required, unique identifier (UUID or server-generated ID)
- `title`: Required, minimum 1 character, maximum 100 characters
- `userId`: Required, must match authenticated user ID
- `messageCount`: Required, non-negative integer
- `lastMessageAt`: Required, ISO 8601 date string
- `createdAt`: Required, ISO 8601 date string
- `updatedAt`: Required, ISO 8601 date string
- `isArchived`: Required, boolean, defaults to false

**State Transitions**:
- `Created` → `Active` → `Archived` → `Deleted`
- `messageCount` increments with each new message
- `updatedAt` updates with each message or conversation change
- `lastMessageAt` updates with each new message

### Message Model

The message entity represents individual chat messages exchanged between users and the AI.

```typescript
interface Message {
  id: string
  conversationId: string
  content: string
  sender: 'user' | 'assistant'
  senderInfo: SenderInfo
  timestamp: Date
  status: MessageStatus
  metadata: MessageMetadata
}

interface SenderInfo {
  id: string
  name: string
  avatar?: string
  email?: string
}

interface MessageMetadata {
  wordCount: number
  characterCount: number
  hasAttachments: boolean
  processingTime?: number
  model?: string
  tokens?: {
    input: number
    output: number
  }
}

type MessageStatus = 'sending' | 'sent' | 'delivered' | 'failed' | 'processing' | 'completed'
```

**Validation Rules**:
- `id`: Required, unique identifier (UUID or server-generated ID)
- `conversationId`: Required, must reference existing conversation
- `content`: Required, minimum 1 character, maximum 10000 characters
- `sender`: Required, must be 'user' or 'assistant'
- `timestamp`: Required, ISO 8601 date string
- `status`: Required, must be valid MessageStatus enum value
- `senderInfo.id`: Required for both user and assistant messages
- `senderInfo.name`: Required for both user and assistant messages

**State Transitions**:
- User message: `sending` → `sent` → `delivered` → `failed`
- Assistant message: `processing` → `completed` → `failed`
- Status transitions are irreversible except for retry scenarios

### User Session Model

The user session entity manages authentication state and user preferences.

```typescript
interface UserSession {
  id: string
  email: string
  name: string
  avatar?: string
  preferences: UserPreferences
  isActive: boolean
  lastActivityAt: Date
  sessionId: string
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  fontSize: 'small' | 'medium' | 'large'
  messageSound: boolean
  desktopNotifications: boolean
  autoSave: boolean
  conversationAutoTitle: boolean
  pollingInterval: number // milliseconds
}
```

**Validation Rules**:
- `id`: Required, must match Better Auth user ID
- `email`: Required, valid email format
- `name`: Required, minimum 2 characters, maximum 50 characters
- `sessionId`: Required, unique session identifier
- `isActive`: Required, boolean
- `lastActivityAt`: Required, ISO 8601 date string
- `preferences.theme`: Required, must be valid theme value
- `preferences.pollingInterval`: Required, between 1000 and 10000 milliseconds

### Real-time Update Model

The real-time update model handles polling and synchronization data.

```typescript
interface RealtimeUpdate {
  conversationId: string
  lastMessageId: string
  updateCount: number
  lastUpdatedAt: Date
  isActive: boolean
}

interface SyncStatus {
  lastSyncAt: Date
  pendingMessages: string[]
  failedOperations: FailedOperation[]
  isOnline: boolean
}

interface FailedOperation {
  id: string
  type: 'send_message' | 'update_conversation' | 'delete_message'
  data: any
  error: string
  retryCount: number
  createdAt: Date
}
```

## Data Flow and Relationships

### Conversation-Message Relationship

- **One-to-Many**: Each conversation contains multiple messages
- **Cascade Delete**: Deleting a conversation removes all associated messages
- **Message Ordering**: Messages are ordered chronologically by timestamp
- **Conversation Updates**: New messages update conversation metadata

### User-Conversation Relationship

- **One-to-Many**: Each user has multiple conversations
- **User Isolation**: Users can only access their own conversations
- **Privacy Enforcement**: Backend enforces user_id filtering for all queries

### Session-Persistence Relationship

- **Session Scope**: User session manages authentication state
- **Conversation Access**: Valid session required to access conversations
- **Local Storage**: Conversations cached locally for offline access
- **Sync Logic**: Changes synchronized when connectivity restored

## Data Persistence Strategy

### Client-side Storage

```typescript
interface StorageKeys {
  CONVERSATION_LIST = 'chatkit_conversations'
  CONVERSATION_PREFIX = 'chatkit_conversation_'
  USER_PREFERENCES = 'chatkit_preferences'
  ACTIVE_CONVERSATION = 'chatkit_active_conversation'
}

interface StorageManager {
  // Conversation management
  saveConversation(conversation: Conversation): Promise<void>
  getConversation(id: string): Promise<Conversation | null>
  deleteConversation(id: string): Promise<void>
  getConversationList(): Promise<Conversation[]>

  // Message management
  saveMessages(conversationId: string, messages: Message[]): Promise<void>
  getMessages(conversationId: string): Promise<Message[]>
  addMessage(conversationId: string, message: Message): Promise<void>

  // User preferences
  savePreferences(preferences: UserPreferences): Promise<void>
  getPreferences(): Promise<UserPreferences>
}
```

### API Integration

```typescript
interface ChatAPI {
  // Conversation endpoints
  getConversations(): Promise<Conversation[]>
  getConversation(id: string): Promise<Conversation>
  createConversation(title?: string): Promise<Conversation>
  updateConversation(id: string, updates: Partial<Conversation>): Promise<Conversation>
  deleteConversation(id: string): Promise<void>

  // Message endpoints
  getMessages(conversationId: string): Promise<Message[]>
  sendMessage(conversationId: string, content: string): Promise<Message>
  deleteMessage(conversationId: string, messageId: string): Promise<void>

  // Real-time updates
  getUpdates(conversationId: string, lastMessageId?: string): Promise<RealtimeUpdate>
}

// API client configuration
interface APIConfig {
  baseURL: string
  timeout: number
  retryAttempts: number
  retryDelay: number
  headers: Record<string, string>
}
```

## State Management Architecture

### React Query Configuration

```typescript
interface QueryKeys {
  conversations = ['conversations']
  conversation = (id: string) => ['conversation', id]
  messages = (conversationId: string) => ['messages', conversationId]
  user = ['user']
  preferences = ['preferences']
}

interface QueryOptions {
  // Conversation queries
  conversations: {
    staleTime: 5 * 60 * 1000 // 5 minutes
    refetchOnWindowFocus: true
    refetchInterval: 30 * 1000 // 30 seconds
  }

  // Message queries
  messages: {
    staleTime: 2 * 60 * 1000 // 2 minutes
    refetchInterval: (data: Message[]) => {
      if (!data.length) return false
      const lastMessage = data[data.length - 1]
      const age = Date.now() - new Date(lastMessage.timestamp).getTime()
      return age < 5 * 60 * 1000 // Poll for 5 minutes after last message
    }
  }
}
```

### Local State Management

```typescript
// Component state for UI interactions
interface ChatUIState {
  selectedConversationId: string | null
  messageInput: string
  isTyping: boolean
  sidebarOpen: boolean
  mobileMenuOpen: boolean
  error: string | null
  loading: boolean
}

// Actions for UI state updates
interface ChatUIActions {
  selectConversation: (id: string | null) => void
  setMessageInput: (input: string) => void
  setTyping: (typing: boolean) => void
  toggleSidebar: () => void
  setMobileMenuOpen: (open: boolean) => void
  setError: (error: string | null) => void
  setLoading: (loading: boolean) => void
}
```

## Validation and Error Handling

### Client-side Validation

```typescript
interface ValidationRules {
  message: {
    minLength: 1
    maxLength: 10000
    allowedCharacters: /^[\s\S]*$/ // Any characters including spaces and newlines
  }

  conversation: {
    title: {
      minLength: 1
      maxLength: 100
      pattern: /^[a-zA-Z0-9\s\-_.,!?]+$/
    }
  }

  preferences: {
    pollingInterval: {
      min: 1000
      max: 10000
      step: 500
    }
  }
}

interface ValidationError {
  field: string
  message: string
  code: string
}
```

### Error Types

```typescript
enum ErrorType {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  PERMISSION_ERROR = 'PERMISSION_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  STORAGE_ERROR = 'STORAGE_ERROR'
}

interface ChatError {
  type: ErrorType
  message: string
  code?: string
  details?: any
  timestamp: Date
  conversationId?: string
  messageId?: string
  retryable: boolean
}
```

## Performance Considerations

### Data Optimization

- **Message Pagination**: Load messages in batches for large conversations
- **Conversation Caching**: Cache conversation metadata for faster sidebar rendering
- **Lazy Loading**: Load conversation details only when selected
- **Debounced Input**: Prevent excessive API calls during typing

### Memory Management

- **Message Limiting**: Limit number of messages kept in memory for large conversations
- **Storage Quota**: Monitor localStorage usage and implement cleanup
- **Component Unmounting**: Clean up subscriptions and timers on component unmount

### Performance Metrics

- **Initial Load**: <2 seconds to display conversation list
- **Message Send**: <1 second from send to display
- **Real-time Updates**: <2 seconds polling interval
- **Storage Operations**: <500ms for localStorage operations

This data model provides a comprehensive foundation for implementing the ChatKit frontend with robust state management, data persistence, and real-time capabilities while maintaining performance and scalability.