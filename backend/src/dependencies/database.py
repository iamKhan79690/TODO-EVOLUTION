"""
FastAPI dependency for database sessions.

This module provides the database session dependency used across
all API endpoints in the chat database architecture.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from ..database import get_session

# Type alias for database session dependency
DbSession = Annotated[AsyncSession, Depends(get_session)]