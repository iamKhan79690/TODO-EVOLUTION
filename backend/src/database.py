"""
Database configuration and connection management for chat database architecture.
Provides async database session management with connection pooling.
"""

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel
from typing import AsyncGenerator

# Load environment variables from .env file
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL_ASYNC", "postgresql+asyncpg://user:password@localhost/dbname")

# Create async engine with connection pooling for Phase III performance requirements
# Supports 10,000 concurrent conversations (SC-006)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=20,           # Base connections for concurrency
    max_overflow=30,        # Additional connections under load
    pool_timeout=30,        # Wait time for connection
    pool_recycle=3600,      # Recycle connections every hour
    pool_pre_ping=True,     # Test connections before use
)

# Session factory for dependency injection
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.

    Provides an async database session with proper cleanup.
    Supports the performance requirements for 10,000 concurrent conversations.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """Create all database tables from SQLModel metadata."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)