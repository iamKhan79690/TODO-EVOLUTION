"""
Simplified Chat API endpoints for AI Chat Assistant.

Handles conversation management and message processing using synchronous REST.
WebSocket removed for simplicity - uses direct request-response pattern.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field

from ..core.database import get_session_dependency
from ..dependencies.auth import get_current_active_user
from ..dependencies.agent_dependency import get_ai_agent
from ..models.models import User
from ..models.chat import Conversation, Message, OperationStatus, MessageType, MessageRole
from ..services.ai_agent import OpenAIAgentWithMCP, get_task_agent
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[UUID] = None


class ToolCall(BaseModel):
    """Model for a tool call made by the AI agent."""
    tool: str
    params: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response model for chat messages (Phase III spec compliant)."""
    conversation_id: str  # UUID as string for JSON compatibility
    response: str
    tool_calls: List[Dict[str, Any]] = []  # List of MCP tools invoked


class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Response model for conversations."""
    id: UUID
    title: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool


class MessageResponse(BaseModel):
    """Response model for messages."""
    id: UUID
    content: str
    role: str
    timestamp: datetime
    operation_type: Optional[str] = None


# ============================================================================
# Chat Endpoints (Simplified - No WebSocket)
# ============================================================================

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_with_ai(
    user_id: int,
    request: ChatRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session_dependency())
):
    """
    Send a message to AI and get a synchronous response.
    
    This is the main chat endpoint. It:
    1. Creates/uses a conversation
    2. Stores the user message
    3. Processes with AI agent
    4. Returns the response directly (no WebSocket)
    """
    try:
        # Extract JWT token from Authorization header
        auth_header = http_request.headers.get("Authorization", "")
        jwt_token = auth_header[7:] if auth_header.startswith("Bearer ") else None
        
        # Get or create conversation
        conversation_id = request.conversation_id
        
        if not conversation_id:
            # Create new conversation
            conversation = Conversation(
                id=uuid4(),
                user_id=current_user.id,
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            conversation_id = conversation.id
            logger.info("New conversation created", 
                       conversation_id=str(conversation_id),
                       user_id=current_user.id)
        else:
            # Verify user owns the conversation
            from sqlmodel import select
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
            result = await session.execute(statement)
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Store user message
        user_message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            user_id=current_user.id,  # Required field
            content=request.message,
            role=MessageRole.USER,
            message_type=MessageType.TEXT,
            created_at=datetime.utcnow(),  # Database requires this
            timestamp=datetime.utcnow(),
            operation_status=OperationStatus.DELIVERED
        )
        session.add(user_message)
        await session.commit()
        
        # Process with AI agent (with JWT token for MCP auth)
        agent = get_task_agent(session, current_user.id, jwt_token)
        result = await agent.process_message(request.message, conversation_id)
        
        # Store AI response
        ai_message = Message(
            id=uuid4(),
            conversation_id=conversation_id,
            user_id=current_user.id,  # Required field for audit trail
            content=result["response"],
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT,
            created_at=datetime.utcnow(),  # Database requires this
            timestamp=datetime.utcnow(),
            operation_type=result.get("operation"),
            operation_status=OperationStatus.DELIVERED if result["success"] else OperationStatus.FAILED
        )
        session.add(ai_message)
        await session.commit()
        
        logger.info("Chat processed successfully",
                   conversation_id=str(conversation_id),
                   operation=result.get("operation"),
                   success=result["success"])
        
        # Build tool_calls array for response
        tool_calls = result.get("tool_calls", [])
        
        # Backward compatibility for legacy UI if needed
        if not tool_calls and result.get("operation"):
            tool_calls.append({
                "tool": result.get("operation"),
                "params": {"message": request.message},
                "result": result.get("result", {})
            })
        
        return ChatResponse(
            conversation_id=str(conversation_id),
            response=result["response"],
            tool_calls=tool_calls
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error("Chat processing failed", 
                    user_id=current_user.id, 
                    error=str(e),
                    traceback=traceback.format_exc())
        print(f"CHAT ERROR: {traceback.format_exc()}")  # Also print to console
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


# ============================================================================
# Conversation Management Endpoints
# ============================================================================

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session_dependency())
):
    """Create a new conversation."""
    try:
        conversation = Conversation(
            id=uuid4(),
            user_id=current_user.id,
            title=request.title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            is_active=conversation.is_active
        )
    except Exception as e:
        logger.error("Failed to create conversation", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session_dependency())
):
    """Get all conversations for the current user."""
    try:
        from sqlmodel import select
        
        statement = select(Conversation).where(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.updated_at.desc()).offset(offset).limit(limit)
        
        result = await session.execute(statement)
        conversations = result.scalars().all()
        
        return [
            ConversationResponse(
                id=c.id,
                title=c.title,
                user_id=c.user_id,
                created_at=c.created_at,
                updated_at=c.updated_at,
                is_active=c.is_active
            )
            for c in conversations
        ]
    except Exception as e:
        logger.error("Failed to get conversations", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get conversations")


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session_dependency())
):
    """Get messages from a specific conversation."""
    try:
        from sqlmodel import select
        
        # Verify ownership
        conv_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
        conv_result = await session.execute(conv_statement)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        msg_statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).offset(offset).limit(limit)
        
        msg_result = await session.execute(msg_statement)
        messages = msg_result.scalars().all()
        
        return [
            MessageResponse(
                id=m.id,
                content=m.content,
                role=m.role,
                timestamp=m.timestamp,
                operation_type=m.operation_type
            )
            for m in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get messages", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get messages")


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint for chat service."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "chat-api",
        "version": "2.0.0",  # Updated version - simplified architecture
        "features": {
            "websocket": False,  # WebSocket removed
            "sync_chat": True    # Synchronous chat enabled
        }
    }