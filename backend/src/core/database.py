"""
Database connection and session management for Neon PostgreSQL
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from sqlalchemy import text
from contextlib import asynccontextmanager
import logging

from src.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create async engine using settings (which loads from .env)
engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
)

# Create session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with automatic transaction management.

    Yields:
        AsyncSession: Database session with automatic commit/rollback
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


def get_session_dependency():
    """
    FastAPI dependency for database session.

    Returns:
        AsyncSession: Database session
    """
    async def dependency() -> AsyncGenerator[AsyncSession, None]:
        async with get_async_session() as session:
            yield session

    return dependency


async def create_tables() -> None:
    """
    Create all database tables from SQLModel definitions.

    This should be called during application startup.
    """
    try:
        async with engine.begin() as conn:
            # checkfirst=True skips creating objects that already exist
            await conn.run_sync(SQLModel.metadata.create_all, checkfirst=True)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


async def validate_database_connection() -> bool:
    """
    Validate database connectivity.

    Returns:
        bool: True if connection is successful
    """
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection validation failed: {e}")
        return False


async def get_pool_status() -> dict:
    """
    Get connection pool statistics.

    Returns:
        dict: Pool status information
    """
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalidatedcount(),
        "total_connections": pool.size() + pool.overflow()
    }