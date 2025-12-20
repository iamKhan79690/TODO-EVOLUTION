# Quick Start Guide: AI Chat Assistant Integration

**Feature**: AI Chat Assistant Integration
**Branch**: `009-ai-chat-assistant`
**Target Date**: 2025-01-22

This guide provides step-by-step instructions for implementing the AI Chat Assistant feature in the TODO-Evolution application.

## Prerequisites

### Development Environment
- **Node.js** 18+ for frontend
- **Python** 3.11+ for backend
- **PostgreSQL** 14+ (Neon recommended)
- **Redis** 6+ for WebSocket connection pooling

### Required Services
- FastAPI backend (already implemented)
- Next.js frontend (already implemented)
- MCP server (already implemented)
- OpenAI API key for AI processing

### Environment Variables

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-here
```

**Backend (.env)**:
```bash
DATABASE_URL=postgresql://user:pass@neon.tech/dbname
BETTER_AUTH_SECRET=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
CORS_ORIGINS=http://localhost:3000
REDIS_URL=redis://localhost:6379
```

**MCP Server (.env)**:
```bash
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET=your-jwt-secret
FASTAPI_BASE_URL=http://localhost:8000
```

## Implementation Steps

### Step 1: Database Schema Setup

**Time**: 30 minutes
**Files**:
- `backend/migrations/001_add_chat_tables.py`

```bash
# Create and run migration
cd backend
alembic revision -m "Add chat tables"
alembic upgrade head
```

**Verification**:
```sql
-- Verify tables created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('conversations', 'messages', 'conversation_contexts', 'task_operations_log');
```

### Step 2: Backend Chat API Implementation

**Time**: 2-3 days
**Files**:
- `backend/src/api/chat.py` - Chat endpoints
- `backend/src/api/websocket.py` - WebSocket handler
- `backend/src/models/chat.py` - SQLModel chat models
- `backend/src/services/chat_service.py` - Chat business logic
- `backend/src/services/ai_service.py` - AI integration service

**Key Implementation Points**:

```python
# backend/src/api/chat.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/ai/process")
async def process_with_ai(
    request: AIProcessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat_service = ChatService(db, current_user.id)
    return await chat_service.process_message_with_ai(request.message)
```

**Verification**:
```bash
# Test chat endpoints
curl -X POST http://localhost:8000/api/chat/ai/process \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to buy groceries"}'
```

### Step 3: WebSocket Implementation

**Time**: 1-2 days
**Files**:
- `backend/src/api/websocket.py` - WebSocket endpoint
- `backend/src/services/websocket_manager.py` - Connection management
- `backend/src/services/websocket_events.py` - Event handlers

**Installation**:
```bash
cd backend
pip install fastapi-socketio python-socketio
```

**Implementation**:
```python
# backend/src/api/websocket.py
from fastapi_socketio import SocketManager
from ..services.websocket_manager import WebSocketManager

sio = SocketManager(app=app, cors_allowed_origins="*")
ws_manager = WebSocketManager(sio)

@sio.on('join_conversation')
async def handle_join_conversation(sid, data):
    user_id = await validate_websocket_auth(sid)
    await ws_manager.join_conversation(sid, user_id, data['conversation_id'])
```

**Verification**:
```javascript
// Test WebSocket connection
const socket = io('ws://localhost:8000/ws/chat', {
  auth: { token: 'your-jwt-token' }
});

socket.emit('join_conversation', { conversation_id: 'uuid' });
```

### Step 4: MCP Tool Integration

**Time**: 1-2 days
**Files**:
- `mcp_server/tools/task_tools.py` - Implement real MCP tools
- `mcp_server/services/fastapi_client.py` - HTTP client for backend
- `mcp_server/config.py` - Configuration management

**Implementation**:
```python
# mcp_server/tools/task_tools.py
from .fastapi_client import FastAPIClient

class TaskTools:
    def __init__(self):
        self.client = FastAPIClient()

    async def add_task(self, user_id: str, task_data: dict):
        return await self.client.post(f"/api/{user_id}/tasks", task_data)
```

**Verification**:
```python
# Test MCP tools
python -m mcp_server.main
# Test with MCP client
```

### Step 5: Frontend Chat Interface

**Time**: 2-3 days
**Files**:
- `frontend/src/components/chat/FloatingChatButton.tsx` - Floating button component
- `frontend/src/components/chat/ChatInterface.tsx` - Main chat interface
- `frontend/src/hooks/useWebSocket.ts` - WebSocket hook
- `frontend/src/lib/websocket.ts` - WebSocket client
- `frontend/src/app/dashboard/page.tsx` - Add chat button to dashboard

**Installation**:
```bash
cd frontend
npm install socket.io-client
```

**Implementation**:
```tsx
// frontend/src/components/chat/FloatingChatButton.tsx
import { useState } from 'react';
import { ChatInterface } from './ChatInterface';

export function FloatingChatButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors z-50"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </button>

      {isOpen && (
        <ChatInterface onClose={() => setIsOpen(false)} />
      )}
    </>
  );
}
```

**Integration with Dashboard**:
```tsx
// frontend/src/app/dashboard/page.tsx
import { FloatingChatButton } from '@/components/chat/FloatingChatButton';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Existing dashboard content */}

      {/* Add floating chat button */}
      <FloatingChatButton />
    </div>
  );
}
```

**Verification**:
```bash
# Start frontend
cd frontend
npm run dev

# Visit http://localhost:3000/dashboard
# Should see floating chat button in bottom-right corner
```

### Step 6: Mobile Optimization

**Time**: 1 day
**Files**:
- `frontend/src/components/chat/MobileChatInterface.tsx` - Mobile-specific chat
- `frontend/src/styles/chat.css` - Responsive chat styles

**Implementation**:
```css
/* frontend/src/styles/chat.css */
@media (max-width: 768px) {
  .chat-interface {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    height: 100vh;
    z-index: 50;
  }

  .floating-chat-button {
    bottom: 1rem;
    right: 1rem;
    width: 3rem;
    height: 3rem;
  }
}
```

### Step 7: Testing and Validation

**Time**: 1-2 days
**Files**:
- `tests/api/test_chat.py` - API tests
- `tests/websocket/test_websocket.py` - WebSocket tests
- `tests/integration/test_chat_flow.py` - End-to-end tests

**Test Cases**:
1. **Authentication**: Verify JWT validation
2. **Message Flow**: User message → AI response → Task operation
3. **Real-time Updates**: WebSocket message delivery
4. **Error Handling**: Network failures, AI errors
5. **Mobile**: Touch interactions, responsive design

**Validation Script**:
```python
# tests/validation/validation_script.py
async def validate_chat_feature():
    # Test conversation creation
    # Test message sending
    # Test AI response
    # Test task operation
    # Test real-time updates
    # Test mobile responsiveness
    pass
```

## Success Criteria Verification

### Performance Requirements
- [ ] Chat interface opens within 2 seconds of clicking button
- [ ] Task operations complete within 3 seconds
- [ ] WebSocket latency <50ms
- [ ] Support for 500 concurrent connections

### Functional Requirements
- [ ] Floating chat button visible on authenticated dashboard
- [ ] Natural language task commands work (add, complete, delete, list)
- [ ] AI responses with task operation results
- [ ] Real-time status indicators for operations
- [ ] Conversation history persists across sessions
- [ ] Mobile-optimized interface works on all devices

### Integration Requirements
- [ ] JWT authentication propagates through all services
- [ ] MCP tools integrate with FastAPI backend
- [ ] Error handling covers all failure scenarios
- [ ] Database maintains consistency across operations

## Troubleshooting

### Common Issues

**WebSocket Connection Fails**:
```bash
# Check CORS configuration
# Verify JWT token format
# Check WebSocket server is running
# Test with WebSocket client tool
```

**AI Processing Errors**:
```bash
# Verify OpenAI API key
# Check MCP server connectivity
# Review MCP tool implementations
# Check FastAPI backend health
```

**Database Performance Issues**:
```sql
-- Check table indexes
EXPLAIN ANALYZE SELECT * FROM messages WHERE conversation_id = 'uuid';

-- Check connection pool
SELECT count(*) FROM pg_stat_activity;
```

**Memory Leaks**:
```bash
# Monitor WebSocket connections
# Check for unclosed database sessions
# Review JavaScript event listeners
# Monitor process memory usage
```

## Monitoring and Maintenance

### Health Checks
```bash
# Chat service health
curl http://localhost:8000/api/chat/health

# WebSocket status
curl http://localhost:8000/api/health

# MCP server status
curl http://localhost:8001/health
```

### Performance Monitoring
- WebSocket connection count
- Message throughput rates
- AI processing times
- Database query performance
- Memory usage patterns

### Log Analysis
```bash
# Backend logs
tail -f backend/logs/app.log

# WebSocket logs
tail -f backend/logs/websocket.log

# MCP server logs
tail -f mcp_server/logs/mcp.log
```

## Rollback Plan

If implementation fails:

1. **Database**: Drop chat tables via migration rollback
2. **Backend**: Remove chat endpoints from API router
3. **Frontend**: Remove chat components from dashboard
4. **Services**: Stop WebSocket and MCP server services

```bash
# Database rollback
alembic downgrade -1

# Code rollback
git checkout previous-stable-commit
```

## Next Steps

After successful implementation:

1. **Performance Optimization**: Caching, connection pooling
2. **Advanced Features**: File attachments, message search
3. **Analytics**: User interaction tracking, usage metrics
4. **Security**: Rate limiting, content moderation
5. **Scaling**: Load testing, horizontal scaling

---

**Estimated Total Implementation Time**: 7-10 days
**Team Size**: 1-2 developers
**Risk Level**: Medium (integrates multiple existing services)

For questions or issues, refer to the detailed technical documentation in `data-model.md`, `research.md`, and API contracts in the `contracts/` directory.