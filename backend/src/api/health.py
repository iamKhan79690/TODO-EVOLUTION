"""
Health check endpoints for the Todo Evolution API
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.config import settings
from src.core.database import validate_database_connection, get_pool_status
from src.schemas.common import HealthResponse


# Create router
health_router = APIRouter()


class DatabaseHealthResponse(BaseModel):
    """Database health check response model"""
    status: str
    database: str
    timestamp: datetime
    response_time_ms: int = 0


class PoolHealthResponse(BaseModel):
    """Connection pool health check response model"""
    pool_size: int
    checked_in: int
    checked_out: int
    overflow: int
    invalid: int
    total_connections: int
    timestamp: datetime


@health_router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint
    Returns the API status and basic information
    """
    # Check database connectivity
    try:
        is_db_connected = await validate_database_connection()
        database_status = "connected" if is_db_connected else "disconnected"
    except Exception:
        database_status = "error"

    return HealthResponse(
        status="healthy" if database_status == "connected" else "unhealthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        database=database_status
    )


@health_router.get("/health/database", response_model=DatabaseHealthResponse)
async def database_health_check():
    """
    Database health check endpoint
    Checks if the database connection is working
    """
    import time
    start_time = time.time()

    try:
        is_connected = await validate_database_connection()
        response_time_ms = int((time.time() - start_time) * 1000)

        if is_connected:
            return DatabaseHealthResponse(
                status="healthy",
                database="connected",
                timestamp=datetime.utcnow(),
                response_time_ms=response_time_ms
            )
        else:
            return DatabaseHealthResponse(
                status="unhealthy",
                database="disconnected",
                timestamp=datetime.utcnow(),
                response_time_ms=response_time_ms
            )
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return DatabaseHealthResponse(
            status="unhealthy",
            database="error",
            timestamp=datetime.utcnow(),
            response_time_ms=response_time_ms
        )


@health_router.get("/health/pool", response_model=PoolHealthResponse)
async def pool_health_check():
    """
    Connection pool health check endpoint
    Returns current connection pool statistics
    """
    try:
        pool_stats = await get_pool_status()
        return PoolHealthResponse(
            timestamp=datetime.utcnow(),
            **pool_stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to retrieve pool statistics: {str(e)}"
        )


@health_router.get("/ping")
async def ping():
    """
    Simple ping endpoint for connectivity testing
    """
    return {"message": "pong", "timestamp": datetime.utcnow()}


@health_router.get("/")
async def api_info():
    """
    API information endpoint
    Returns basic API metadata
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }