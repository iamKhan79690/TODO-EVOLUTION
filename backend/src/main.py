"""
FastAPI main application entry point for TODO-Evolution with chat database architecture.

Configures the FastAPI application with middleware, routes, and database setup
for Phase III AI Chatbot functionality.
"""

import os
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import create_tables
from src.api import auth, tasks, health
from src.api.chat import router as chat_router

# Configuration from environment
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
APP_NAME = os.getenv("APP_NAME", "TODO-Evolution API")
VERSION = os.getenv("VERSION", "1.0.0")

# CORS configuration for frontend integration (T010)
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:3001,https://your-vercel-app.vercel.app"
).split(",")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for database initialization
    and other application lifecycle management.
    """
    # Startup
    print(f"🚀 Starting {APP_NAME} v{VERSION} in {ENVIRONMENT} mode")
    print(f"🌐 Server will be available on http://{HOST}:{PORT}")

    try:
        # Create database tables
        await create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        raise

    yield

    # Shutdown
    print("🛑 Shutting down application...")

# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="FastAPI application for TODO-Evolution with Phase III AI Chatbot support",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    lifespan=lifespan,
)

# Add CORS middleware for frontend integration (T010)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(tasks.tasks_router, prefix="/api", tags=["Tasks"])
app.include_router(health.health_router, prefix="/health", tags=["Health"])
app.include_router(chat_router, tags=["Chat"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic application information."""
    return {
        "name": APP_NAME,
        "version": VERSION,
        "environment": ENVIRONMENT,
        "docs": "/docs" if DEBUG else "Documentation disabled in production",
        "status": "healthy"
    }

# Application info endpoint
@app.get("/info")
async def app_info():
    """Detailed application information."""
    return {
        "name": APP_NAME,
        "version": VERSION,
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "features": {
            "tasks": "✅ Available",
            "authentication": "✅ Available",
            "health_checks": "✅ Available",
            "chat_api": "✅ Available (Phase III AI Chatbot)",
        },
        "documentation": {
            "openapi": "/openapi.json",
            "docs": "/docs" if DEBUG else "Disabled in production",
            "redoc": "/redoc" if DEBUG else "Disabled in production",
        }
    }

def signal_handler(signum, frame):
    """Handle graceful shutdown signals"""
    print(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    import uvicorn

    print(f"🎯 Starting {APP_NAME} server...")
    print(f"📍 Host: {HOST}")
    print(f"🔌 Port: {PORT}")
    print(f"🔧 Debug: {DEBUG}")
    print(f"🌍 Environment: {ENVIRONMENT}")
    print(f"📖 API Docs: http://{HOST}:{PORT}/docs" if DEBUG else "📖 API Docs: Disabled")

    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info",
        access_log=True,
    )