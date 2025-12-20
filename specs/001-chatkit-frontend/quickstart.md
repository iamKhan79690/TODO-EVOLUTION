# ChatKit Frontend Quickstart Guide

**Version**: 1.0.0
**Date**: 2025-01-14
**Feature**: ChatKit Frontend Architecture

## Overview

This guide shows how to quickly integrate the ChatKit frontend components into your Next.js application. The frontend provides a complete chat interface with real-time updates, conversation management, and authentication using Better Auth.

## Prerequisites

- Node.js 18+ and npm
- Next.js 15 with App Router
- TypeScript 5.x
- Tailwind CSS 3.x
- Better Auth configured for authentication
- Backend API for chat functionality

## Quick Start

### 1. Install Dependencies

```bash
npm install @tanstack/react-query react-hot-toast
npm install lucide-react
npm install date-fns
```

### 2. Environment Configuration

Create a `.env.local` file:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-key
NEXTAUTH_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000

# ChatKit Configuration
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000
NEXT_PUBLIC_POLLING_INTERVAL=2000
```

### 3. Basic Setup

Create the authentication configuration:

```typescript
// lib/auth.ts
import { auth } from "@/lib/auth"

export const { handlers, signIn, signOut, auth } = BetterAuth({
  providers: [
    {
      id: "credentials",
      name: "Credentials",
      type: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      authorize: async (credentials) => {
        // Your authentication logic here
        const user = await validateUser(credentials)
        if (user) return user
        return null
      },
    },
  ],
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
})
```

### 4. API Client Setup

Create the centralized API client:

```typescript
// lib/api.ts
import { createApiClient } from "@/lib/api-client"

export const chatApi = createApiClient({
  baseURL: process.env.NEXT_PUBLIC_CHAT_API_URL,
  timeout: 10000,
  retryAttempts: 3,
})

// API functions
export const conversationsApi = {
  getAll: () => chatApi.get('/api/conversations'),
  getById: (id: string) => chatApi.get(`/api/conversations/${id}`),
  create: (title?: string) => chatApi.post('/api/conversations', { title }),
  update: (id: string, updates: any) => chatApi.put(`/api/conversations/${id}`, updates),
  delete: (id: string) => chatApi.delete(`/api/conversations/${id}`),
}

export const messagesApi = {
  getByConversationId: (conversationId: string) =>
    chatApi.get(`/api/conversations/${conversationId}/messages`),
  send: (conversationId: string, content: string) =>
    chatApi.post(`/api/conversations/${conversationId}/messages`, { content }),
  delete: (conversationId: string, messageId: string) =>
    chatApi.delete(`/api/conversations/${conversationId}/messages/${messageId}`),
}

export const realtimeApi = {
  getUpdates: (conversationId: string, lastMessageId?: string) =>
    chatApi.get(`/api/conversations/${conversationId}/updates`, {
      params: { lastMessageId }
    }),
}
```

### 5. React Query Setup

Configure React Query for server state management:

```typescript
// app/providers/react-query-provider.tsx
"use client"

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function ReactQueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            refetchOnWindowFocus: true,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

### 6. Use the Chat Components

Create the main chat page:

```typescript
// app/(chat)/page.tsx
"use client"

import { ChatPage } from "@/components/chat/chat-page"

export default function ChatRoute() {
  return <ChatPage />
}
```

### 7. Add Root Layout

Update your root layout:

```typescript
// app/layout.tsx
import { ReactQueryProvider } from "@/app/providers/react-query-provider"
import { Toaster } from "react-hot-toast"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <ReactQueryProvider>
          {children}
          <Toaster position="top-right" />
        </ReactQueryProvider>
      </body>
    </html>
  )
}
```

## Component Examples

### Chat Page Component

```typescript
// components/chat/chat-page.tsx
"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { conversationsApi, messagesApi } from "@/lib/api"
import { ConversationSidebar } from "./conversation-sidebar"
import { MessageList } from "./message-list"
import { InputArea } from "./input-area"

export function ChatPage() {
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)

  // Fetch conversations
  const {
    data: conversations,
    isLoading: isLoadingConversations,
    refetch: refetchConversations,
  } = useQuery({
    queryKey: ["conversations"],
    queryFn: conversationsApi.getAll,
  })

  // Fetch selected conversation
  const {
    data: conversationDetail,
    isLoading: isLoadingConversation,
  } = useQuery({
    queryKey: ["conversation", selectedConversationId],
    queryFn: () =>
      selectedConversationId
        ? conversationsApi.getById(selectedConversationId)
        : Promise.resolve(null),
    enabled: !!selectedConversationId,
  })

  // Fetch messages for selected conversation
  const {
    data: messages,
    isLoading: isLoadingMessages,
    refetch: refetchMessages,
  } = useQuery({
    queryKey: ["messages", selectedConversationId],
    queryFn: () =>
      selectedConversationId
        ? messagesApi.getByConversationId(selectedConversationId)
        : Promise.resolve([]),
    enabled: !!selectedConversationId,
  })

  return (
    <div className="flex h-full bg-gray-50">
      {/* Conversation Sidebar */}
      <ConversationSidebar
        conversations={conversations || []}
        selectedId={selectedConversationId}
        onSelectConversation={setSelectedConversationId}
        isLoading={isLoadingConversations}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversationId ? (
          <>
            {/* Message List */}
            <MessageList
              messages={messages || []}
              conversation={conversationDetail}
              isLoading={isLoadingMessages || isLoadingConversation}
            />

            {/* Input Area */}
            <InputArea
              conversationId={selectedConversationId}
              onMessageSent={refetchMessages}
              onConversationUpdated={refetchConversations}
            />
          </>
        ) : (
          /* Empty State */
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Select a conversation
              </h3>
              <p className="text-gray-500">
                Choose a conversation from the sidebar or start a new one
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
```

### Message List Component

```typescript
// components/chat/message-list.tsx
"use client"

import { useEffect, useRef } from "react"
import { MessageBubble } from "./message-bubble"
import { TypingIndicator } from "./typing-indicator"
import { Message } from "@/types"

interface MessageListProps {
  messages: Message[]
  conversation: any
  isLoading?: boolean
}

export function MessageList({ messages, conversation, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollTop = messagesEndRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {/* Date separator */}
      {messages.length > 0 && (
        <div className="text-center text-sm text-gray-500 mb-4">
          {new Date(messages[0].timestamp).toLocaleDateString()}
        </div>
      )}

      {/* Messages */}
      <div className="space-y-4">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            isOwn={message.sender === "user"}
          />
        ))}
      </div>

      {/* Typing indicator */}
      {isLoading && <TypingIndicator />}

      {/* Auto-scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  )
}
```

### Input Area Component

```typescript
// components/chat/input-area.tsx
"use client"

import { useState } from "react"
import { Send } from "lucide-react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { messagesApi, conversationsApi } from "@/lib/api"
import { toast } from "react-hot-toast"

interface InputAreaProps {
  conversationId: string
  onMessageSent: () => void
  onConversationUpdated: () => void
}

export function InputArea({ conversationId, onMessageSent, onConversationUpdated }: InputAreaProps) {
  const [inputValue, setInputValue] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const queryClient = useQueryClient()

  const sendMessageMutation = useMutation({
    mutationFn: (content: string) =>
      messagesApi.send(conversationId, content),
    onSuccess: () => {
      setInputValue("")
      onMessageSent()
      onConversationUpdated()
      queryClient.invalidateQueries({ queryKey: ["messages", conversationId] })
      queryClient.invalidateQueries({ queryKey: ["conversation", conversationId] })
    },
    onError: (error) => {
      toast.error(`Failed to send message: ${error.message}`)
    },
    onSettled: () => {
      setIsSubmitting(false)
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!inputValue.trim() || isSubmitting) return

    setIsSubmitting(true)
    await sendMessageMutation.mutateAsync(inputValue.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="border-t bg-white p-4">
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
            disabled={isSubmitting}
          />
        </div>
        <button
          type="submit"
          disabled={!inputValue.trim() || isSubmitting}
          className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="h-4 w-4" />
          <span className="sr-only">Send</span>
        </button>
      </div>
    </form>
  )
}
```

### Conversation Sidebar Component

```typescript
// components/chat/conversation-sidebar.tsx
"use client"

import { useState } from "react"
import { Plus, MessageSquare, MoreHorizontal, Archive } from "lucide-react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { conversationsApi } from "@/lib/api"
import { Conversation } from "@/types"
import { formatDistanceToNow } from "date-fns"

interface ConversationSidebarProps {
  conversations: Conversation[]
  selectedId: string | null
  onSelectConversation: (id: string) => void
  isLoading?: boolean
}

export function ConversationSidebar({
  conversations,
  selectedId,
  onSelectConversation,
  isLoading,
}: ConversationSidebarProps) {
  const [isCreating, setIsCreating] = useState(false)
  const queryClient = useQueryClient()

  const createConversationMutation = useMutation({
    mutationFn: (title?: string) => conversationsApi.create(title),
    onSuccess: (newConversation) => {
      onSelectConversation(newConversation.id)
      queryClient.invalidateQueries({ queryKey: ["conversations"] })
      setIsCreating(false)
    },
    onError: (error) => {
      console.error("Failed to create conversation:", error)
      setIsCreating(false)
    },
  })

  const handleCreateConversation = () => {
    setIsCreating(true)
    createConversationMutation.mutate()
  }

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={handleCreateConversation}
          disabled={isCreating}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="h-4 w-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-16 bg-gray-200 rounded-lg"></div>
              </div>
            ))}
          </div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center">
            <MessageSquare className="mx-auto h-12 w-12 text-gray-400 mb-2" />
            <h3 className="text-sm font-medium text-gray-900 mb-1">
              No conversations yet
            </h3>
            <p className="text-sm text-gray-500">
              Start a new conversation to begin chatting
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => onSelectConversation(conversation.id)}
                className={`p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-200 transition-colors ${
                  selectedId === conversation.id ? "bg-blue-50 border-l-4 border-l-blue-500" : ""
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900 truncate">
                      {conversation.title}
                    </h4>
                    <p className="text-sm text-gray-500 truncate">
                      {conversation.preview}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {conversation.messageCount} messages •
                      {formatDistanceToNow(new Date(conversation.lastMessageAt), {
                        addSuffix: true,
                      })}
                    </p>
                  </div>
                  <button
                    className="ml-2 p-1 hover:bg-gray-100 rounded-md"
                    onClick={(e) => {
                      e.stopPropagation()
                      // Handle conversation options (archive, delete, etc.)
                    }}
                  >
                    <MoreHorizontal className="h-4 w-4 text-gray-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

## Testing

### Unit Testing Example

```typescript
// components/chat/__tests__/message-bubble.test.tsx
import { render, screen } from "@testing-library/react"
import { MessageBubble } from "../message-bubble"
import { Message } from "@/types"

describe("MessageBubble", () => {
  const mockMessage: Message = {
    id: "msg_123",
    conversationId: "conv_123",
    content: "Hello world",
    sender: "user",
    senderInfo: {
      id: "user_123",
      name: "John Doe",
      email: "john@example.com",
    },
    timestamp: new Date("2025-01-14T10:00:00Z"),
    status: "sent",
    metadata: {
      wordCount: 2,
      characterCount: 11,
      hasAttachments: false,
    },
  }

  it("renders user message correctly", () => {
    render(<MessageBubble message={mockMessage} isOwn={true} />)

    expect(screen.getByText("Hello world")).toBeInTheDocument()
    expect(screen.getByTestId("user-message")).toBeInTheDocument()
    expect(screen.getByText("John Doe")).toBeInTheDocument()
  })

  it("renders assistant message correctly", () => {
    const assistantMessage = { ...mockMessage, sender: "assistant" }
    render(<MessageBubble message={assistantMessage} isOwn={false} />)

    expect(screen.getByText("Hello world")).toBeInTheDocument()
    expect(screen.getByTestId("assistant-message")).toBeInTheDocument()
  })
})
```

### End-to-End Testing Example

```typescript
// e2e/chat.spec.ts
import { test, expect } from "@playwright/test"

test.describe("Chat Interface", () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto("/api/auth/signin")
    await page.fill('[name="email"]', "test@example.com")
    await page.fill('[name="password"]', "password123")
    await page.click('button[type="submit"]')
    await page.waitForURL("/chat")
  })

  test("can create and use conversation", async ({ page }) => {
      await page.click('[data-testid="new-conversation"]')
      await page.waitFor('[data-testid="conversation-item"]')

      // Send a message
      await page.fill('[data-testid="message-input"]', "Hello AI!")
      await page.click('[data-testid="send-button"]')

      // Verify message appears
      await expect(page.getByText("Hello AI!")).toBeVisible()

      // Wait for AI response
      await expect(page.getByText(/AI response/)).toBeVisible({ timeout: 10000 })
    })

  test("can navigate between conversations", async ({ page }) => {
      // Create first conversation
      await page.click('[data-testid="new-conversation"]')
      await page.fill('[data-testid="message-input"]', "First chat")
      await page.click('[data-testid="send-button"]')

      // Create second conversation
      await page.click('[data-testid="new-conversation"]')
      await page.fill('[data-testid="message-input"]', "Second chat")
      await page.click('[data-testid="send-button"]')

      // Switch back to first conversation
      await page.click('[data-testid="conversation-item"]:first-child')
      await expect(page.getByText("First chat")).toBeVisible()

      // Verify second conversation still exists
      expect(page.getByText("Second chat")).toBeVisible()
    })
})
```

## Customization

### Styling

The components use Tailwind CSS classes. You can customize the appearance by:

1. **Modifying Tailwind Config**: Update `tailwind.config.ts`
2. **Overriding Styles**: Use CSS modules for custom styling
3. **Theme Support**: Leverage the built-in theme system

### Theming

```typescript
// styles/theme.ts
export const theme = {
  colors: {
    primary: {
      50: "#eff6ff",
      500: "#3b82f6",
      600: "#2563eb",
      700: "#1d4ed8",
    },
    user: {
      bubble: "#f3f4f6",
      text: "#111827",
    },
    assistant: {
      bubble: "#e5e7eb",
      text: "#374151",
    },
  },
}
```

### Custom Hooks

```typescript
// hooks/use-realtime-updates.ts
import { useQuery } from "@tanstack/react-query"
import { realtimeApi } from "@/lib/api"

export const useRealtimeUpdates = (conversationId: string, pollingInterval = 2000) => {
  const [lastMessageId, setLastMessageId] = useState<string | null>(null)

  return useQuery({
    queryKey: ["realtime-updates", conversationId, lastMessageId],
    queryFn: () => realtimeApi.getUpdates(conversationId, lastMessageId || undefined),
    refetchInterval: pollingInterval,
    enabled: !!conversationId,
    onSuccess: (data) => {
      if (data.newMessages && data.newMessages.length > 0) {
        const latestMessage = data.newMessages[data.newMessages.length - 1]
        setLastMessageId(latestMessage.id)
      }
    },
  })
}
```

## Deployment

### Environment Variables

```bash
# Production
NEXT_PUBLIC_CHAT_API_URL=https://api.yourapp.com
NEXT_PUBLIC_POLLING_INTERVAL=3000

# Development
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000
NEXT_PUBLIC_POLLING_INTERVAL=2000
```

### Build Command

```bash
npm run build
npm run start
```

This quickstart guide provides everything you need to integrate the ChatKit frontend components into your Next.js application. The components are designed to be flexible and customizable while maintaining a consistent user experience.