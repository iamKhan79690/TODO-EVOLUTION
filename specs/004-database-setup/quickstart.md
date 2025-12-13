# Database Setup Quickstart Guide

**Purpose**: Get Neon PostgreSQL database integrated with Phase II application in 10 minutes
**Feature**: 004-database-setup
**Prerequisites**: Neon account, Phase II development environment

## Prerequisites

### Required Accounts
- [Neon Database Account](https://neon.tech/) (free tier available)
- GitHub account (for repository access)

### Required Tools
- Python 3.12+ installed
- Node.js 18+ installed
- Git configured
- Terminal/Command line access

### Phase II Environment
- Frontend server running (localhost:3000)
- Backend server running (localhost:8000)
- Git repository cloned and on `004-database-setup` branch

## Step 1: Create Neon Database

### 1.1 Sign up for Neon
1. Go to [neon.tech](https://neon.tech)
2. Click "Sign up" and create account
3. Choose free tier for development

### 1.2 Create Database Project
1. After signup, click "New Project"
2. Choose region closest to you (recommended: US East for development)
3. Select PostgreSQL version (latest stable)
4. Name your project (e.g., "todo-evolution-db")
5. Click "Create Project"

### 1.3 Get Connection String
1. From project dashboard, go to "Connection Details"
2. Copy the "Connection string" (looks like: `postgresql://user:pass@host/dbname?sslmode=require`)
3. Save this string - you'll need it for configuration

## Step 2: Configure Backend Database Connection

### 2.1 Update Backend Environment Variables

Edit `backend/.env` file:

```bash
# Database Configuration (replace with your Neon connection string)
DATABASE_URL=postgresql://username:password@ep-xyz.us-east-2.aws.neon.tech/dbname?sslmode=require

# Add async version for SQLModel
DATABASE_URL_ASYNC=postgresql+asyncpg://username:password@ep-xyz.us-east-2.aws.neon.tech/dbname?sslmode=require

# Connection Pool Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Important**: Replace the connection string with your actual Neon credentials from Step 1.3.

### 2.2 Install Additional Dependencies

Navigate to backend directory and install required packages:

```bash
cd backend
# Activate virtual environment if not already active
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Install database dependencies
pip install sqlmodel[asyncpg] asyncpg sqlalchemy pydantic-settings

# Update requirements.txt
pip freeze > requirements.txt
```

### 2.3 Verify Database Connection

Test the connection by running the backend:

```bash
python main.py
```

You should see:
- No database connection errors
- If health endpoint exists, it should show database connectivity

## Step 3: Implement Database Layer

### 3.1 Create Database Configuration

Create `backend/src/core/database.py`:

```python
"""
Database connection and session management for Neon PostgreSQL
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

# Create async engine
engine = create_async_engine(
    os.getenv("DATABASE_URL_ASYNC"),
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
    pool_pre_ping=True,
)

# Create session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_async_session():
    """Get database session with automatic transaction management"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """Create all database tables from SQLModel definitions"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### 3.2 Create SQLModel Models

Create `backend/src/models/models.py`:

```python
"""
SQLModel definitions for User and Task entities
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

# User model (managed by Better Auth, read-only for our app)
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")

    # Core task fields
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM)

    # Phase I features
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = Field(default=None)
    is_recurring: bool = Field(default=False)
    recurrence_pattern: Optional[RecurrencePattern] = Field(default=None)
    recurrence_end_date: Optional[datetime] = Field(default=None)

    # Completion tracking
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="tasks")
```

### 3.3 Update Main Application

Update `backend/main.py` to include database initialization:

```python
"""
Main FastAPI application entry point for Todo Evolution Phase II
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.api.health import health_router
from src.core.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Todo Evolution API starting up...")

    # Create database tables
    await create_tables()
    print("Database tables created successfully")

    yield

    # Shutdown
    print("Todo Evolution API shutting down...")


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
```

## Step 4: Verify Implementation

### 4.1 Restart Backend Server

```bash
# Stop current server (Ctrl+C)
# Restart with database integration
python main.py
```

You should see output like:
```
Todo Evolution API starting up...
Database tables created successfully
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4.2 Verify Database Tables

1. Go to your Neon dashboard
2. Open the "Tables" section
3. You should see:
   - `users` table (created by Better Auth when first user signs up)
   - `tasks` table with all specified columns and indexes

### 4.3 Test Health Endpoint

Visit `http://localhost:8000/api/v1/health` in your browser or with curl:

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-07T..."
}
```

### 4.4 Verify API Documentation

Visit `http://localhost:8000/docs` to see the auto-generated OpenAPI documentation.

## Step 5: Configuration Reference

### Environment Variables

Create a `backend/.env.example` file for reference:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
DATABASE_URL_ASYNC=postgresql+asyncpg://user:pass@host/dbname?sslmode=require

# Connection Pool Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

# Environment
ENVIRONMENT=development
DEBUG=true

# Better Auth (same as frontend)
BETTER_AUTH_SECRET=your-32-character-secret-key
JWT_SECRET=your-jwt-secret-key
```

### Production Settings

For production deployment, update your environment variables:

```bash
# Production database settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_RECYCLE=1800
ENVIRONMENT=production
DEBUG=false
```

## Troubleshooting

### Common Issues

**Connection String Errors**:
- Verify your Neon connection string is correct
- Ensure `sslmode=require` is included
- Check for special characters in password (URL encode if needed)

**Module Import Errors**:
- Ensure all dependencies are installed: `pip install sqlmodel[asyncpg] asyncpg sqlalchemy pydantic-settings`
- Check Python version (3.12+ recommended)

**Table Creation Failures**:
- Verify DATABASE_URL_ASYNC environment variable is set
- Check Neon database is active and accessible
- Review backend server logs for specific error messages

**Performance Issues**:
- Increase DB_POOL_SIZE for more concurrent connections
- Reduce DB_POOL_RECYCLE for serverless environments
- Monitor Neon dashboard for connection usage

### Getting Help

1. Check the [Neon Documentation](https://neon.tech/docs)
2. Review [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
3. Check [FastAPI Database Guide](https://fastapi.tiangolo.com/tutorial/databases/)
4. Review the Phase II constitution for architectural guidelines

## Next Steps

With the database layer configured, you can now:

1. **Implement Task CRUD APIs**: Create endpoints for task management
2. **Add User Authentication**: Integrate Better Auth with database
3. **Build Frontend Integration**: Connect React components to database APIs
4. **Add Advanced Features**: Implement search, filtering, and analytics

The database foundation is now ready for full-stack development!