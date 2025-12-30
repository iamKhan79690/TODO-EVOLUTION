"""
Simple Chat API endpoint for AI Chat Assistant.

This is a simplified version that bypasses complex session handling
and directly uses Google Gemini API for chat functionality.
"""

import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
import openai

from ..dependencies.auth import get_current_active_user
from ..models.models import User
from ..core.config import settings
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/api/simple", tags=["simple-chat"])


# ============================================================================
# Request/Response Models
# ============================================================================

class SimpleChatRequest(BaseModel):
    """Simple chat request."""
    message: str = Field(..., min_length=1, max_length=10000)


class SimpleChatResponse(BaseModel):
    """Simple chat response."""
    response: str
    success: bool = True
    timestamp: str


# ============================================================================
# Gemini Chat Function
# ============================================================================

SYSTEM_PROMPT = """You are a helpful TODO assistant. You help users manage their tasks.
When users want to add, list, complete, or delete tasks, acknowledge their request and 
provide a helpful response. Be concise and friendly.

Examples of what you can help with:
- Adding new tasks
- Listing existing tasks  
- Marking tasks as complete
- Deleting tasks
- Providing task management tips"""


async def chat_with_groq(message: str, user_id: int) -> dict:
    """
    Direct chat with Groq API using OpenAI SDK compatibility.
    
    Args:
        message: User's message
        user_id: User ID for context
        
    Returns:
        dict with response and success status
    """
    try:
        # Get Groq API key
        api_key = settings.GROQ_API_KEY
        if not api_key:
            # Fallback: try environment variable
            api_key = os.getenv("GROQ_API_KEY", "")
        
        if not api_key:
            logger.error("No Groq API key configured")
            return {
                "response": "I'm sorry, the AI service is not configured. Please contact the administrator.",
                "success": False
            }
        
        # Create OpenAI client pointing to Groq
        import openai
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Generate response using Groq (fast 8B model for simple chat)
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        
        ai_response = response.choices[0].message.content or "I'm here to help!"
        
        logger.info("Simple chat successful", 
                   user_id=user_id, 
                   message_len=len(message),
                   response_len=len(ai_response))
        
        return {
            "response": ai_response,
            "success": True
        }
        
    except Exception as e:
        logger.error("Simple chat failed", user_id=user_id, error=str(e))
        return {
            "response": f"Sorry, I couldn't process your message: {str(e)}",
            "success": False
        }


# ============================================================================
# Simple Chat Endpoint
# ============================================================================

@router.post("/chat", response_model=SimpleChatResponse)
async def simple_chat(
    request: SimpleChatRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Simple chat endpoint - direct Gemini call without complex session handling.
    
    This endpoint:
    1. Authenticates the user via JWT
    2. Sends message directly to Google Gemini
    3. Returns the response
    
    No conversation history, no database writes, just simple chat.
    """
    logger.info("Simple chat request", 
               user_id=current_user.id, 
               message=request.message[:50])
    
    result = await chat_with_groq(request.message, current_user.id)
    
    return SimpleChatResponse(
        response=result["response"],
        success=result["success"],
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/health")
async def simple_chat_health():
    """Health check for simple chat endpoint."""
    has_key = bool(settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY"))
    return {
        "status": "healthy" if has_key else "degraded",
        "endpoint": "simple-chat",
        "model": "llama-3.1-8b-instant",
        "provider": "groq",
        "api_configured": has_key,
        "timestamp": datetime.utcnow().isoformat()
    }
