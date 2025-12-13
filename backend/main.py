"""
Main FastAPI application entry point for Todo Evolution Phase II
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.api.health import health_router
from src.api.tasks import tasks_router
from src.api.auth import router as auth_router
from src.core.database import create_tables, validate_database_connection
from src.auth.token_store import token_blacklist


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Todo Evolution API starting up...")

    # Initialize database
    try:
        # Validate database connection first
        if await validate_database_connection():
            print("Database connection validated successfully")

            # Create database tables
            await create_tables()
            print("Database initialization complete")
        else:
            print("WARNING: Database connection validation failed")
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")
        raise

    yield

    # Shutdown
    print("Todo Evolution API shutting down...")

    # Cleanup token blacklist
    await token_blacklist.disconnect()


# Create FastAPI application
app = FastAPI(
    title="Todo Evolution API",
    description="Phase II full-stack todo application API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Todo Evolution API - Phase II",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )