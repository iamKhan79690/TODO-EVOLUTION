"""
Database Configuration for MCP Server

Handles async database connection pooling for PostgreSQL with Neon integration.
Supports high-performance operations for concurrent tool executions.
"""

import os
import asyncio
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import asyncpg
from sqlmodel import SQLModel

from backend.src.models.models import Task, User  # Import existing models


class DatabaseConfig:
    """Database configuration and connection management."""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool_size = int(os.getenv("CONNECTION_POOL_SIZE", "20"))
        self.max_overflow = int(os.getenv("CONNECTION_POOL_MAX_OVERFLOW", "30"))

        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Convert postgresql:// to postgresql+asyncpg:// for async operations
        if self.database_url.startswith("postgresql://"):
            self.async_database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            self.async_database_url = self.database_url

        self._engine = None
        self._session_factory = None
        self._asyncpg_pool = None

    async def initialize(self):
        """Initialize database engine and connection pools."""
        try:
            # Create SQLAlchemy async engine
            self._engine = create_async_engine(
                self.async_database_url,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,  # Recycle connections every hour
                echo=False,  # Set to True for SQL logging in development
                future=True
            )

            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=True,
                autocommit=False
            )

            # Create asyncpg pool for direct operations
            self._asyncpg_pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=self.pool_size,
                max_queries=50000,  # Reset connection after N queries
                max_inactive_connection_lifetime=300,  # 5 minutes
                command_timeout=30,  # 30 second timeout
                setup=self._setup_connection,
                init=self._init_connection
            )

            print(f"✅ Database initialized with pool_size={self.pool_size}, max_overflow={self.max_overflow}")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize database: {e}")

    async def _setup_connection(self, conn):
        """Setup connection with optimized parameters."""
        await conn.execute("SET TIME ZONE 'UTC'")
        await conn.execute("SET statement_timeout TO '45s'")  # Slightly under 50ms target per query
        await conn.execute("SET application_name TO 'mcp_server'")

    async def _init_connection(self, conn):
        """Initialize connection with type codecs."""
        import json
        await conn.set_type_codec(
            'jsonb',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )

    async def close(self):
        """Close all database connections."""
        if self._asyncpg_pool:
            await self._asyncpg_pool.close()
            self._asyncpg_pool = None

        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

        print("✅ Database connections closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session from the pool.

        Usage:
            async with db_config.get_session() as session:
                # Use session here
                result = await session.execute(query)
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_asyncpg_connection(self):
        """
        Get a direct asyncpg connection for optimized operations.

        Usage:
            async with db_config.get_asyncpg_connection() as conn:
                result = await conn.fetch("SELECT * FROM tasks WHERE user_id = $1", user_id)
        """
        if not self._asyncpg_pool:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self._asyncpg_pool.acquire() as conn:
            yield conn

    async def create_tables(self):
        """Create database tables if they don't exist."""
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            print("✅ Database tables created/verified")
        except Exception as e:
            raise RuntimeError(f"Failed to create tables: {e}")

    async def health_check(self) -> dict:
        """
        Perform database health check.

        Returns:
            Dictionary with health status information
        """
        try:
            async with self.get_asyncpg_connection() as conn:
                result = await conn.fetchval("SELECT 1")

            pool_stats = {
                "pool_size": self._asyncpg_pool.get_size(),
                "pool_idle": self._asyncpg_pool.get_idle_size(),
                "pool_max": self._asyncpg_pool.get_max_size(),
            }

            return {
                "status": "healthy",
                "database_connected": True,
                "pool_stats": pool_stats
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "database_connected": False,
                "error": str(e)
            }

    def get_engine(self):
        """Get the SQLAlchemy async engine."""
        return self._engine


# Global database configuration instance
db_config = DatabaseConfig()


# Context manager for easy database access
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions."""
    async with db_config.get_session() as session:
        yield session


async def get_asyncpg_connection():
    """Context manager for asyncpg connections."""
    async with db_config.get_asyncpg_connection() as conn:
        yield conn


async def initialize_database():
    """Initialize the database configuration."""
    await db_config.initialize()
    await db_config.create_tables()


async def close_database():
    """Close database connections."""
    await db_config.close()