"""FastAPI dependency for AI Agent injection."""

from fastapi import Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session_dependency
from ..dependencies.auth import get_current_active_user
from ..models.models import User
from ..services.ai_agent import OpenAIAgentWithMCP, get_task_agent


async def get_ai_agent(
    request: Request,
    session: AsyncSession = Depends(get_session_dependency()),
    current_user: User = Depends(get_current_active_user)
) -> OpenAIAgentWithMCP:
    """
    Dependency injection for AI agent.
    
    Automatically extracts JWT token from Authorization header
    and creates the agent with proper authentication context.
    
    Args:
        request: FastAPI request object
        session: Async database session
        current_user: Authenticated user
        
    Returns:
        Configured OpenAIAgentWithMCP instance
    """
    # Extract JWT token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    jwt_token = None
    if auth_header.startswith("Bearer "):
        jwt_token = auth_header[7:]  # Remove "Bearer " prefix
    
    return get_task_agent(session, current_user.id, jwt_token)
