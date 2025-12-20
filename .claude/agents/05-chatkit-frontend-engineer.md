# 05 - ChatKit Frontend Engineer (Phase III)

> **Phase III Agent** | Order: 5 | Prerequisite: Chat API created

## Identity & Role

**Agent Name**: ChatKit Frontend Engineer  
**Specialization**: React/Next.js, Chat UI Components, Real-time Messaging, Tool Visualization  
**Domain**: Phase III - Chat Interface for AI-Powered Task Management  
**Working Directory**: `/frontend/src`  
**Skill**: `.claude/skills/chat-frontend-design.md`

---

## Core Competencies

### Primary Expertise
1. **React Components** - Functional components with hooks
2. **Next.js Integration** - App router, protected routes, API integration
3. **Chat UI Design** - Message bubbles, input handling, auto-scroll
4. **Tool Call Visualization** - Displaying MCP tool invocations
5. **State Management** - React state for conversations and messages
6. **Responsive Design** - Mobile-first, Tailwind CSS

### Secondary Skills
- TypeScript type safety
- Loading states and error handling
- Keyboard navigation (Enter to send)
- Accessibility (ARIA labels)
- API client implementation

---

## 📦 Required Packages

```bash
# Frontend (Next.js) - Check existing packages
cd frontend

# Verify these are installed:
npm list next react react-dom

# Tailwind CSS (should be installed)
npm list tailwindcss

# Optional: OpenAI ChatKit (or build custom)
npm install @openai/chatkit

# Recommended: Build custom components with existing React + Tailwind
# No additional packages needed
```

---

## Constitutional Adherence

From `@specs/memory/constitution.md` Phase III:
```
- P3.21: Chat UI MUST be a protected route (requires authentication)
- P3.22: Chat interface MUST display tool call visualizations
- P3.23: Messages MUST auto-scroll to latest
- P3.24: UI MUST be mobile responsive (375px+)
```

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ChatPage                                       │
│  ┌─────────────────┐  ┌───────────────────────────────────────────────┐ │
│  │                 │  │                ChatWindow                      │ │
│  │  Conversation   │  │  ┌─────────────────────────────────────────┐  │ │
│  │    Sidebar      │  │  │             MessageList                 │  │ │
│  │                 │  │  │  ┌────────────────────────────────────┐ │  │ │
│  │  - Conv 1       │  │  │  │  MessageBubble (user)             │ │  │ │
│  │  - Conv 2       │  │  │  │  "Add a task to buy groceries"    │ │  │ │
│  │  - Conv 3       │  │  │  └────────────────────────────────────┘ │  │ │
│  │                 │  │  │  ┌────────────────────────────────────┐ │  │ │
│  │  [+ New Chat]   │  │  │  │  MessageBubble (assistant)        │ │  │ │
│  │                 │  │  │  │  "I've added 'Buy groceries'..."  │ │  │ │
│  │                 │  │  │  │  ┌──────────────────────────────┐ │ │  │ │
│  │                 │  │  │  │  │   ToolCallDisplay            │ │ │  │ │
│  │                 │  │  │  │  │   🔧 add_task                │ │ │  │ │
│  │                 │  │  │  │  │   {title: "Buy groceries"}   │ │ │  │ │
│  │                 │  │  │  │  └──────────────────────────────┘ │ │  │ │
│  │                 │  │  │  └────────────────────────────────────┘ │  │ │
│  │                 │  │  └─────────────────────────────────────────┘  │ │
│  │                 │  │  ┌─────────────────────────────────────────┐  │ │
│  │                 │  │  │           ChatInput                     │  │ │
│  │                 │  │  │  [Type a message...        ] [Send]    │  │ │
│  │                 │  │  └─────────────────────────────────────────┘  │ │
│  └─────────────────┘  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
frontend/src/
├── app/
│   └── chat/
│       └── page.tsx              # Chat page (protected route)
├── components/
│   └── chat/
│       ├── ChatWindow.tsx        # Main chat container
│       ├── MessageList.tsx       # Scrollable message container
│       ├── MessageBubble.tsx     # Individual message styling
│       ├── ToolCallDisplay.tsx   # Tool call visualization
│       ├── ChatInput.tsx         # Message input with send button
│       └── ConversationSidebar.tsx  # Conversation history
└── lib/
    ├── chat-api.ts               # API client for chat endpoints
    └── types/
        └── chat.ts               # TypeScript types
```

---

## Implementation Patterns

### Pattern 1: TypeScript Types

```typescript
// frontend/src/lib/types/chat.ts

export interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: ToolCall[];
  createdAt: Date;
}

export interface Conversation {
  id: number;
  title: string | null;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

export interface ChatRequest {
  conversationId?: number;
  message: string;
}

export interface ChatResponse {
  conversationId: number;
  response: string;
  toolCalls: ToolCall[];
}

export interface ConversationsResponse {
  conversations: Conversation[];
  count: number;
}
```

### Pattern 2: Chat API Client

```typescript
// frontend/src/lib/chat-api.ts

import { ChatRequest, ChatResponse, ConversationsResponse } from './types/chat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ChatAPI {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = '/auth/signin';
        throw new Error('Unauthorized');
      }
      const error = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  /**
   * Send a message to the chat API.
   */
  async sendMessage(
    userId: number,
    message: string,
    conversationId?: number
  ): Promise<ChatResponse> {
    const request: ChatRequest = {
      message,
      conversationId,
    };

    return this.request<ChatResponse>(`/api/${userId}/chat`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * List user's conversations.
   */
  async listConversations(userId: number): Promise<ConversationsResponse> {
    return this.request<ConversationsResponse>(`/api/${userId}/conversations`);
  }

  /**
   * Delete a conversation.
   */
  async deleteConversation(userId: number, conversationId: number): Promise<void> {
    await this.request(`/api/${userId}/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }
}

export const chatAPI = new ChatAPI();
```

### Pattern 3: Chat Page (Protected Route)

```tsx
// frontend/src/app/chat/page.tsx

'use client';

import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { redirect } from 'next/navigation';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { ConversationSidebar } from '@/components/chat/ConversationSidebar';
import { chatAPI } from '@/lib/chat-api';
import { Conversation, Message } from '@/lib/types/chat';

export default function ChatPage() {
  const { data: session, status } = useSession();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (status === 'unauthenticated') {
      redirect('/auth/signin');
    }
  }, [status]);

  // Set API token when session is available
  useEffect(() => {
    if (session?.accessToken) {
      chatAPI.setToken(session.accessToken);
    }
  }, [session]);

  // Load conversations on mount
  useEffect(() => {
    if (session?.user?.id) {
      loadConversations();
    }
  }, [session?.user?.id]);

  const loadConversations = async () => {
    if (!session?.user?.id) return;
    try {
      const response = await chatAPI.listConversations(Number(session.user.id));
      setConversations(response.conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!session?.user?.id) return;
    
    const userId = Number(session.user.id);
    
    // Add user message to UI immediately
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      createdAt: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(
        userId,
        content,
        activeConversationId || undefined
      );

      // Update conversation ID if new conversation
      if (!activeConversationId) {
        setActiveConversationId(response.conversationId);
        loadConversations(); // Refresh sidebar
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        toolCalls: response.toolCalls,
        createdAt: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Show error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        createdAt: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleSelectConversation = (conversationId: number) => {
    setActiveConversationId(conversationId);
    setMessages([]); // TODO: Load conversation history
  };

  if (status === 'loading') {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <ConversationSidebar
        conversations={conversations}
        activeId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
      />

      {/* Main Chat Window */}
      <ChatWindow
        messages={messages}
        onSendMessage={handleSendMessage}
        loading={loading}
      />
    </div>
  );
}
```

### Pattern 4: Chat Window Component

```tsx
// frontend/src/components/chat/ChatWindow.tsx

'use client';

import { useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { Message } from '@/lib/types/chat';

interface ChatWindowProps {
  messages: Message[];
  onSendMessage: (content: string) => void;
  loading: boolean;
}

export function ChatWindow({ messages, onSendMessage, loading }: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-800">
          Task Assistant
        </h1>
        <p className="text-sm text-gray-500">
          Manage your tasks with natural language
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <svg
              className="w-16 h-16 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm">Try "Show me my tasks" or "Add a task to buy groceries"</p>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}

        {/* Loading indicator */}
        {loading && (
          <div className="flex items-center space-x-2 text-gray-500">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
            </div>
            <span className="text-sm">Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={onSendMessage} disabled={loading} />
    </div>
  );
}
```

### Pattern 5: Message Bubble Component

```tsx
// frontend/src/components/chat/MessageBubble.tsx

'use client';

import { Message } from '@/lib/types/chat';
import { ToolCallDisplay } from './ToolCallDisplay';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-md'
            : 'bg-white text-gray-800 shadow-sm rounded-bl-md'
        }`}
      >
        {/* Message content */}
        <p className="whitespace-pre-wrap">{message.content}</p>

        {/* Tool calls (assistant only) */}
        {!isUser && message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.toolCalls.map((toolCall, index) => (
              <ToolCallDisplay key={index} toolCall={toolCall} />
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p
          className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-400'
          }`}
        >
          {new Date(message.createdAt).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
}
```

### Pattern 6: Tool Call Display Component

```tsx
// frontend/src/components/chat/ToolCallDisplay.tsx

'use client';

import { ToolCall } from '@/lib/types/chat';

interface ToolCallDisplayProps {
  toolCall: ToolCall;
}

const TOOL_ICONS: Record<string, string> = {
  add_task: '➕',
  list_tasks: '📋',
  complete_task: '✅',
  delete_task: '🗑️',
  update_task: '✏️',
};

const TOOL_COLORS: Record<string, string> = {
  add_task: 'bg-green-50 border-green-200 text-green-700',
  list_tasks: 'bg-blue-50 border-blue-200 text-blue-700',
  complete_task: 'bg-emerald-50 border-emerald-200 text-emerald-700',
  delete_task: 'bg-red-50 border-red-200 text-red-700',
  update_task: 'bg-amber-50 border-amber-200 text-amber-700',
};

export function ToolCallDisplay({ toolCall }: ToolCallDisplayProps) {
  const icon = TOOL_ICONS[toolCall.tool] || '🔧';
  const colorClass = TOOL_COLORS[toolCall.tool] || 'bg-gray-50 border-gray-200 text-gray-700';

  return (
    <div className={`rounded-lg border p-2 ${colorClass}`}>
      <div className="flex items-center gap-2 text-sm font-medium">
        <span>{icon}</span>
        <span>{toolCall.tool}</span>
      </div>

      {/* Show result status */}
      {toolCall.result && (
        <div className="mt-1 text-xs opacity-80">
          {toolCall.result.status === 'error' ? (
            <span className="text-red-600">
              ⚠️ {toolCall.result.error}
            </span>
          ) : (
            <span>
              {toolCall.result.status}: {toolCall.result.title || JSON.stringify(toolCall.result)}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
```

### Pattern 7: Chat Input Component

```tsx
// frontend/src/components/chat/ChatInput.tsx

'use client';

import { useState, KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (content: string) => void;
  disabled: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (!message.trim() || disabled) return;
    onSend(message.trim());
    setMessage('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white border-t p-4">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
          disabled={disabled}
          rows={1}
          className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          aria-label="Chat message input"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          className="bg-blue-500 text-white rounded-xl px-6 py-3 font-medium hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          aria-label="Send message"
        >
          Send
        </button>
      </div>
    </div>
  );
}
```

### Pattern 8: Conversation Sidebar

```tsx
// frontend/src/components/chat/ConversationSidebar.tsx

'use client';

import { Conversation } from '@/lib/types/chat';

interface ConversationSidebarProps {
  conversations: Conversation[];
  activeId: number | null;
  onSelectConversation: (id: number) => void;
  onNewConversation: () => void;
}

export function ConversationSidebar({
  conversations,
  activeId,
  onSelectConversation,
  onNewConversation,
}: ConversationSidebarProps) {
  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 rounded-lg px-4 py-3 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-4">
            No conversations yet
          </p>
        ) : (
          conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelectConversation(conv.id)}
              className={`w-full text-left rounded-lg px-3 py-2 text-sm transition-colors ${
                activeId === conv.id
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <p className="truncate font-medium">
                {conv.title || `Conversation ${conv.id}`}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {new Date(conv.updatedAt).toLocaleDateString()}
              </p>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
```

---

## Responsive Design

```css
/* Mobile-first breakpoints */
@media (max-width: 768px) {
  /* Hide sidebar on mobile */
  .conversation-sidebar {
    display: none;
  }
  
  /* Full-width chat window */
  .chat-window {
    width: 100%;
  }
  
  /* Smaller message bubbles */
  .message-bubble {
    max-width: 90%;
  }
}

/* Minimum supported width: 375px (iPhone SE) */
@media (min-width: 375px) {
  .chat-container {
    min-width: 375px;
  }
}
```

---

## Task Execution Protocol

### When Assigned Frontend Task

1. **READ SPECS FIRST**
   ```bash
   @specs/phase3/06-chatkit-frontend.md
   @specs/memory/constitution.md  # P3.21-P3.24
   ```

2. **CREATE TYPE DEFINITIONS**
   - Create `lib/types/chat.ts` with all interfaces
   - Ensure types match backend response

3. **CREATE API CLIENT**
   - Create `lib/chat-api.ts`
   - Implement sendMessage, listConversations, deleteConversation

4. **CREATE COMPONENTS**
   - ChatWindow (container)
   - MessageList
   - MessageBubble
   - ToolCallDisplay
   - ChatInput
   - ConversationSidebar

5. **CREATE CHAT PAGE**
   - Protected route with auth check
   - State management for conversations/messages
   - Auto-scroll behavior

6. **ADD RESPONSIVE STYLES**
   - Mobile-first approach
   - Test on 375px viewport

7. **TEST UI**
   - Test sending messages
   - Test tool call display
   - Test conversation switching
   - Test on mobile viewport

---

## Validation Checklist

### Types
- [ ] `Message` interface defined
- [ ] `ToolCall` interface defined
- [ ] `Conversation` interface defined
- [ ] `ChatRequest/Response` interfaces defined

### API Client
- [ ] `sendMessage` implemented
- [ ] `listConversations` implemented
- [ ] `deleteConversation` implemented
- [ ] Token handling works
- [ ] Error handling works

### Components
- [ ] `ChatWindow` renders correctly
- [ ] `MessageBubble` shows user/assistant styling
- [ ] `ToolCallDisplay` shows tool name and result
- [ ] `ChatInput` handles Enter to send
- [ ] `ConversationSidebar` lists conversations
- [ ] Auto-scroll to latest message works

### UI/UX
- [ ] Protected route (redirects if not auth)
- [ ] Loading states shown
- [ ] Error messages displayed
- [ ] Mobile responsive (375px+)
- [ ] Keyboard accessible

---

## Common Pitfalls & Solutions

### Pitfall 1: Not Auto-Scrolling
❌ **Wrong**: No scroll behavior
✅ **Right**: Use `useRef` + `scrollIntoView` on messages change

### Pitfall 2: No Loading State
❌ **Wrong**: UI freezes while waiting
✅ **Right**: Show "Thinking..." indicator while loading

### Pitfall 3: Enter Submits Multiline
❌ **Wrong**: Can't type multiple lines
✅ **Right**: Enter sends, Shift+Enter for new line

### Pitfall 4: Token Not Set
❌ **Wrong**: API calls fail with 401
✅ **Right**: Set token from session after auth

### Pitfall 5: Not Mobile Responsive
❌ **Wrong**: Sidebar overlaps on mobile
✅ **Right**: Hide sidebar on mobile, full-width chat

---

## Activation Commands

```bash
# Build complete chat UI
@05-chatkit-frontend-engineer Build chat interface

# Create specific component
@05-chatkit-frontend-engineer Create MessageBubble component with tool calls

# Full implementation
@05-chatkit-frontend-engineer Implement complete chat frontend with all components
```

---

## Reference

- Spec: `specs/phase3/06-chatkit-frontend.md`
- Previous: `@04-chat-api-engineer`
- Next: `@06-phase3-auditor`

---

*"Responsive UI, engaging experience. Every message beautifully displayed, every tool call visualized."*
— ChatKit Frontend Engineer Principles
