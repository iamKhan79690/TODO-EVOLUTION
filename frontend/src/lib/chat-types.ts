/**
 * TypeScript types and interfaces for ChatKit frontend
 * Based on the data model specifications in the design documents
 */

// Core entity types
export interface Conversation {
  id: string
  title: string
  userId: string
  messageCount: number
  lastMessageAt: string // ISO 8601 date string
  createdAt: string // ISO 8601 date string
  updatedAt: string // ISO 8601 date string
  isArchived: boolean

  // Computed properties
  preview: string
  unreadCount: number
}

export interface Message {
  id: string
  conversationId: string
  content: string
  sender: 'user' | 'assistant'
  senderInfo: SenderInfo
  timestamp: string // ISO 8601 date string
  status: MessageStatus
  metadata: MessageMetadata
}

export interface SenderInfo {
  id: string
  name: string
  avatar?: string
  email?: string
}

export type MessageStatus = 'sending' | 'sent' | 'delivered' | 'failed' | 'processing' | 'completed'

export interface MessageMetadata {
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

// User and session types
export interface User {
  id: string
  email: string
  name: string
  avatar?: string
}

export interface UserSession {
  id: string
  email: string
  name: string
  avatar?: string
  preferences: UserPreferences
  isActive: boolean
  lastActivityAt: string // ISO 8601 date string
  sessionId: string
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  fontSize: 'small' | 'medium' | 'large'
  messageSound: boolean
  desktopNotifications: boolean
  autoSave: boolean
  conversationAutoTitle: boolean
  pollingInterval: number // milliseconds
}

// Real-time and sync types
export interface RealtimeUpdate {
  conversationId: string
  lastMessageId: string
  updateCount: number
  lastUpdatedAt: string // ISO 8601 date string
  isActive: boolean
  newMessages?: Message[]
  updatedMessages?: Message[]
}

export interface SyncStatus {
  lastSyncAt: string // ISO 8601 date string
  pendingMessages: string[]
  failedOperations: FailedOperation[]
  isOnline: boolean
}

export interface FailedOperation {
  id: string
  type: 'send_message' | 'update_conversation' | 'delete_message'
  data: any
  error: string
  retryCount: number
  createdAt: string // ISO 8601 date string
}

// API request/response types
export interface CreateConversationRequest {
  title?: string
}

export interface UpdateConversationRequest {
  title?: string
  isArchived?: boolean
}

export interface SendMessageRequest {
  content: string
}

export interface UpdatePreferencesRequest {
  theme?: 'light' | 'dark' | 'system'
  fontSize?: 'small' | 'medium' | 'large'
  messageSound?: boolean
  desktopNotifications?: boolean
  pollingInterval?: number
}

// UI state types
export interface ChatUIState {
  selectedConversationId: string | null
  messageInput: string
  isTyping: boolean
  sidebarOpen: boolean
  mobileMenuOpen: boolean
  error: string | null
  loading: boolean
}

export interface ChatUIActions {
  selectConversation: (id: string | null) => void
  setMessageInput: (input: string) => void
  setTyping: (typing: boolean) => void
  toggleSidebar: () => void
  setMobileMenuOpen: (open: boolean) => void
  setError: (error: string | null) => void
  setLoading: (loading: boolean) => void
}

// Storage types
export interface StorageKeys {
  CONVERSATION_LIST = 'chatkit_conversations'
  CONVERSATION_PREFIX = 'chatkit_conversation_'
  USER_PREFERENCES = 'chatkit_preferences'
  ACTIVE_CONVERSATION = 'chatkit_active_conversation'
}

// Validation types
export interface ValidationRules {
  message: {
    minLength: number
    maxLength: number
    allowedCharacters: RegExp
  }
  conversation: {
    title: {
      minLength: number
      maxLength: number
      pattern: RegExp
    }
  }
  preferences: {
    pollingInterval: {
      min: number
      max: number
      step: number
    }
  }
}

export interface ValidationError {
  field: string
  message: string
  code: string
}

// Error types
export enum ErrorType {
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR',
  AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR',
  PERMISSION_ERROR = 'PERMISSION_ERROR',
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  STORAGE_ERROR = 'STORAGE_ERROR',
}

export interface ChatError {
  type: ErrorType
  message: string
  code?: string
  details?: any
  timestamp: string // ISO 8601 date string
  conversationId?: string
  messageId?: string
  retryable: boolean
}

// React Query keys
export interface QueryKeys {
  conversations = ['conversations']
  conversation = (id: string) => ['conversation', id]
  messages = (conversationId: string) => ['messages', conversationId]
  user = ['user']
  preferences = ['preferences']
}

// Component props types
export interface MessageBubbleProps {
  message: Message
  isOwn?: boolean
  showTimestamp?: boolean
  className?: string
}

export interface MessageListProps {
  messages: Message[]
  loading?: boolean
  error?: string | null
  onRetry?: () => void
  className?: string
}

export interface InputAreaProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  disabled?: boolean
  placeholder?: string
  maxLength?: number
  className?: string
}

export interface ConversationSidebarProps {
  conversations: Conversation[]
  selectedConversationId: string | null
  onSelectConversation: (id: string) => void
  onNewConversation: () => void
  loading?: boolean
  error?: string | null
  className?: string
}

export interface ChatPageProps {
  className?: string
}

// Hook return types
export interface UseAuthReturn {
  user: User | null
  loading: boolean
  error: string | null
  isAuthenticated: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, name: string) => Promise<void>
  signOut: () => Promise<void>
  updateProfile: (updates: Partial<User>) => Promise<void>
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>
}

export interface UseConversationReturn {
  conversations: Conversation[]
  selectedConversation: Conversation | null
  messages: Message[]
  loading: boolean
  error: string | null
  createConversation: (title?: string) => Promise<Conversation>
  selectConversation: (id: string) => void
  updateConversation: (id: string, updates: Partial<Conversation>) => Promise<void>
  deleteConversation: (id: string) => Promise<void>
  sendMessage: (content: string) => Promise<void>
  refreshConversations: () => void
  refreshMessages: () => void
}

export interface UseRealtimeReturn {
  isConnected: boolean
  lastUpdate: RealtimeUpdate | null
  error: string | null
  startPolling: () => void
  stopPolling: () => void
  forceUpdate: () => void
}