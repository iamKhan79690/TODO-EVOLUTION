# EVOLUTION-OF-TODO-006-user-auth - Complete Project Documentation

> **Last Updated:** December 11, 2025  
> **Project Type:** Full-Stack Todo Application (Phase II)  
> **Status:** Development Ready ✅

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Backend Documentation](#4-backend-documentation)
5. [Frontend Documentation](#5-frontend-documentation)
6. [Authentication System](#6-authentication-system)
7. [Database Schema](#7-database-schema)
8. [API Reference](#8-api-reference)
9. [Environment Configuration](#9-environment-configuration)
10. [Development Setup](#10-development-setup)
11. [Deployment Guide](#11-deployment-guide)
12. [File Structure](#12-file-structure)

---

## 1. Project Overview

**EVOLUTION-OF-TODO** is a sophisticated task management application that evolved from a console application (Phase I) to a full-stack web application (Phase II). It features user authentication, persistent cloud storage, and a modern responsive interface.

### Key Features
- ✅ **User Authentication**: Sign up, sign in, sign out with JWT tokens
- ✅ **Task CRUD Operations**: Create, read, update, delete tasks
- ✅ **Priority Levels**: Low, Medium, High, Urgent
- ✅ **Due Dates & Recurrence**: Set deadlines and recurring patterns
- ✅ **Filtering & Pagination**: Filter by status, priority; paginated results
- ✅ **Cloud Storage**: Neon PostgreSQL for data persistence
- ✅ **Real-time UI**: Modern responsive design with Tailwind CSS

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Next.js 16 Frontend (Port 3000)                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │   │
│  │  │  Pages/App  │  │  Components │  │   Hooks/Context     │ │   │
│  │  │  - Landing  │  │  - TaskForm │  │  - useAuth          │ │   │
│  │  │  - Dashboard│  │  - TaskItem │  │  - useTasks         │ │   │
│  │  │  - Auth     │  │  - UI       │  │  - AuthProvider     │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │   │
│  │          │               │                 │                │   │
│  │          └───────────────┼─────────────────┘                │   │
│  │                          ▼                                  │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              API Clients (lib/)                      │   │   │
│  │  │  - auth-client.ts  (JWT token management)           │   │   │
│  │  │  - api.ts          (Task API requests)              │   │   │
│  │  │  - types.ts        (TypeScript interfaces)          │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼ HTTP/REST (JSON)
┌─────────────────────────────────────────────────────────────────────┐
│                         SERVER LAYER                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (Port 8000)                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │   │
│  │  │  API Routes │  │  Services   │  │   Dependencies      │ │   │
│  │  │  /api/v1/   │  │  TaskService│  │  - get_current_user │ │   │
│  │  │  /api/tasks │  │             │  │  - JWT validation   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │   │
│  │          │               │                 │                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │   │
│  │  │   Schemas   │  │   Models    │  │   Core/Config       │ │   │
│  │  │  - auth.py  │  │  - User     │  │  - settings         │ │   │
│  │  │  - task.py  │  │  - Task     │  │  - database.py      │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼ SQL (asyncpg)
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │          Neon PostgreSQL (Serverless)                       │   │
│  │  ┌─────────────┐  ┌─────────────────────────────────────┐  │   │
│  │  │  user table │  │          task table                 │  │   │
│  │  │  - id       │◄─┤  - id, user_id (FK)                │  │   │
│  │  │  - email    │  │  - title, description               │  │   │
│  │  │  - name     │  │  - priority, is_completed           │  │   │
│  │  │  - password │  │  - due_date, recurrence_pattern     │  │   │
│  │  └─────────────┘  └─────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.0.7 | React framework with App Router |
| React | 19.2.0 | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 4.x | Utility-first CSS |
| TanStack Query | 5.x | Data fetching, caching, mutations |
| react-hook-form | 7.51+ | Form management |
| Zod | 3.22+ | Schema validation |
| date-fns | 3.x | Date formatting |
| lucide-react | 0.400+ | Icons |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.121+ | Web framework |
| SQLModel | 0.0.27 | ORM (SQLAlchemy + Pydantic) |
| SQLAlchemy | 2.0+ | Database toolkit |
| asyncpg | 0.30+ | Async PostgreSQL driver |
| python-jose | 3.5+ | JWT handling |
| passlib | 1.7+ | Password hashing (bcrypt) |
| pydantic-settings | 2.8+ | Configuration management |
| uvicorn | 0.34+ | ASGI server |

### Database & Infrastructure
| Service | Purpose |
|---------|---------|
| Neon PostgreSQL | Serverless cloud database |
| Vercel | Frontend hosting |
| Render | Backend hosting |

---

## 4. Backend Documentation

### 4.1 Entry Point (`backend/main.py`)

```python
# FastAPI application with lifespan manager
app = FastAPI(
    title="Todo Evolution API",
    description="Phase II full-stack todo application API",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, ...)

# Route prefixes
- health_router: "/api/v1" → /api/v1/health
- tasks_router:  "/api"    → /api/tasks
- auth_router:   "/api/v1" → /api/v1/auth/*
```

### 4.2 Core Configuration (`backend/src/core/config.py`)

```python
class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Todo Evolution API"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database (Neon PostgreSQL)
    DATABASE_URL: str = "postgresql://..."
    DATABASE_URL_ASYNC: str = "postgresql+asyncpg://..."
    DB_POOL_SIZE: int = 10
    
    # JWT Configuration
    BETTER_AUTH_SECRET: str = "..."
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
```

### 4.3 Database Layer (`backend/src/core/database.py`)

```python
# Async SQLAlchemy engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Key functions:
- get_async_session()          # Context manager for transactions
- get_session_dependency()     # FastAPI dependency injection
- create_tables()              # Auto-create tables on startup
- validate_database_connection() # Health check
```

### 4.4 Models (`backend/src/models/models.py`)

```python
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RecurrencePattern(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    description: Optional[str]
    priority: Priority = Priority.MEDIUM
    is_completed: bool = False
    due_date: Optional[datetime]
    recurrence_pattern: RecurrencePattern = RecurrencePattern.NONE
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="tasks")
```

### 4.5 Services (`backend/src/services/task_service.py`)

```python
class TaskService:
    def __init__(self, session: AsyncSession): ...
    
    async def create_task(task_create, user_id) -> Task
    async def get_user_tasks(user_id, completed?, priority?, skip, limit) -> List[Task]
    async def get_task_by_id(task_id, user_id) -> Task
    async def update_task(task_id, task_update, user_id) -> Task
    async def delete_task(task_id, user_id) -> bool
    async def toggle_task_complete(task_id, user_id) -> Task
    async def get_user_task_stats(user_id) -> dict
```

---

## 5. Frontend Documentation

### 5.1 App Structure (`frontend/src/app/`)

```
app/
├── layout.tsx          # Root layout with AuthProvider
├── page.tsx            # Landing page (marketing)
├── globals.css         # Global Tailwind styles
├── auth/
│   ├── signin/page.tsx # Sign in form
│   └── signup/page.tsx # Sign up form
└── dashboard/
    └── page.tsx        # Main task management UI
```

### 5.2 Key Components

#### `TaskForm.tsx` - Task Creation/Editing
```tsx
// Features:
- react-hook-form + zod validation
- Fields: title*, description, priority, dueDate, tags, estimatedTime
- Validation: title required, max lengths, future due dates
- Modes: 'create' | 'edit'
```

#### `TaskItem.tsx` - Task Display
```tsx
// Features:
- Status toggle (checkbox)
- Priority badge (color-coded)
- Due date display (overdue detection)
- Edit/Delete actions
- Compact and Grid variants
```

### 5.3 API Clients (`frontend/src/lib/`)

#### `auth-client.ts`
```typescript
class AuthClient {
    baseURL: string = 'http://localhost:8000'
    
    getAccessToken(): string | null
    getRefreshToken(): string | null
    setTokens(accessToken, refreshToken): void
    clearTokens(): void
    
    signIn(email, password): Promise<{user, accessToken, refreshToken}>
    signUp(email, password, name): Promise<{user, accessToken, refreshToken}>
    signOut(): Promise<void>
    refreshToken(): Promise<boolean>
}
```

#### `api.ts`
```typescript
class TaskAPI {
    baseURL: string = 'http://localhost:8000'
    
    getTasks(params?): Promise<PaginatedResponse<Task>>
    getTask(id): Promise<ApiResponse<Task>>
    createTask(data): Promise<ApiResponse<Task>>
    updateTask(id, data): Promise<ApiResponse<Task>>
    deleteTask(id): Promise<ApiResponse<void>>
    bulkUpdate(ids, data): Promise<ApiResponse<Task[]>>
    bulkDelete(ids): Promise<ApiResponse<void>>
}
```

### 5.4 State Management

#### `AuthProvider` (Context)
```tsx
// Provides:
- user: User | null
- status: 'idle' | 'loading' | 'authenticated' | 'unauthenticated'
- login(email, password)
- register(email, password, name)
- logout()
- refreshToken()
```

#### `useTasks` Hook (TanStack Query)
```tsx
// Returns:
- tasks: Task[]
- isLoading, error
- createTask, updateTask, deleteTask
- bulkUpdate, bulkDelete
- refetch

// Features:
- Optimistic updates
- Automatic cache invalidation
- Background refetching
```

---

## 6. Authentication System

### 6.1 Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                          │
└─────────────────────────────────────────────────────────────────┘

1. SIGN UP
   Client                          Server
   ──────                          ──────
   POST /api/v1/auth/sign-up ────► Validate email uniqueness
   {email, password, name}         Hash password (bcrypt)
                                   Create User record
                           ◄────── Generate JWT tokens
   Store tokens in localStorage    Return {user, token}
   
2. SIGN IN
   POST /api/v1/auth/sign-in ────► Find user by email
   {email, password}               Verify password hash
                           ◄────── Generate JWT tokens
   Store tokens                    Return {user, token}
   
3. AUTHENTICATED REQUESTS
   GET /api/tasks ─────────────► Extract Bearer token
   Authorization: Bearer <token>   Verify JWT signature
                                   Check expiration
                                   Check blacklist
                           ◄────── Load user from DB
   Receive response                Process request
   
4. TOKEN REFRESH
   POST /api/v1/auth/refresh ───► Verify refresh token
   {refreshToken}                  Blacklist old token
                           ◄────── Generate new tokens
   Update stored tokens            Return {access, refresh}
   
5. SIGN OUT
   POST /api/v1/auth/sign-out ──► Blacklist access token
   {refreshToken}                  Blacklist refresh token
   Authorization: Bearer <token>
                           ◄────── Return success
   Clear localStorage
```

### 6.2 JWT Token Structure

```javascript
// Access Token (30 min expiry)
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1702234567,
  "iat": 1702232767,
  "type": "access"
}

// Refresh Token (7 days expiry)
{
  "sub": "user_id",
  "exp": 1702837567,
  "iat": 1702232767,
  "type": "refresh"
}
```

---

## 7. Database Schema

```sql
-- User Table
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_user_email ON "user"(email);

-- Task Table
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    priority VARCHAR(10) DEFAULT 'medium',  -- enum: low, medium, high, urgent
    is_completed BOOLEAN DEFAULT FALSE,
    due_date TIMESTAMP,
    recurrence_pattern VARCHAR(10) DEFAULT 'none', -- enum: none, daily, weekly, monthly, yearly
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
);
CREATE INDEX ix_task_user_id ON task(user_id);
```

---

## 8. API Reference

### 8.1 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/sign-up` | Register new user | No |
| POST | `/api/v1/auth/sign-in` | Login user | No |
| POST | `/api/v1/auth/sign-out` | Logout user | Yes |
| POST | `/api/v1/auth/refresh` | Refresh tokens | No |
| GET | `/api/v1/auth/me` | Get current user | Yes |
| GET | `/api/v1/auth/verify` | Verify token | Yes |

### 8.2 Task Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tasks` | List user's tasks | Yes |
| POST | `/api/tasks` | Create new task | Yes |
| GET | `/api/tasks/{id}` | Get task by ID | Yes |
| PUT | `/api/tasks/{id}` | Full update task | Yes |
| PATCH | `/api/tasks/{id}` | Partial update task | Yes |
| DELETE | `/api/tasks/{id}` | Delete task | Yes |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion | Yes |

### 8.3 Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Basic health check |
| GET | `/api/v1/health/database` | Database connectivity |
| GET | `/api/v1/health/pool` | Connection pool stats |
| GET | `/api/v1/ping` | Simple ping |

### 8.4 Request/Response Examples

#### Create Task
```bash
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Complete documentation",
  "description": "Write comprehensive project docs",
  "priority": "high",
  "due_date": "2025-12-15T10:00:00Z"
}

# Response 201
{
  "id": 1,
  "title": "Complete documentation",
  "description": "Write comprehensive project docs",
  "priority": "high",
  "is_completed": false,
  "due_date": "2025-12-15T10:00:00Z",
  "recurrence_pattern": "none",
  "created_at": "2025-12-11T09:30:00Z",
  "updated_at": "2025-12-11T09:30:00Z",
  "user_id": 1
}
```

---

## 9. Environment Configuration

### 9.1 Required Environment Variables

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
DATABASE_URL_ASYNC=postgresql+asyncpg://user:pass@host/db?ssl=require

# Authentication Secrets (generate with: openssl rand -base64 32)
BETTER_AUTH_SECRET=your-32-char-secret
JWT_SECRET=your-jwt-secret

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
ENVIRONMENT=development

# CORS (comma-separated for production)
CORS_ORIGINS=http://localhost:3000

# Frontend (Next.js public vars)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 9.2 File Locations
- Root: `.env.example`, `.env.local.example`
- Backend: `backend/.env`
- Frontend: `frontend/.env.local` (create from example)

---

## 10. Development Setup

### 10.1 Prerequisites
- Node.js 18+
- Python 3.11+
- Git

### 10.2 Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd EVOLUTION-OF-TODO-006-user-auth

# 2. Install frontend dependencies
cd frontend
npm install
cd ..

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# 4. Configure environment
# Copy .env.example to backend/.env and configure DATABASE_URL

# 5. Start servers
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 10.3 Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## 11. Deployment Guide

### 11.1 Architecture
```
Vercel (Frontend) ──► Render (Backend) ──► Neon (Database)
```

### 11.2 Backend Deployment (Render)
1. Create Web Service on Render
2. Connect GitHub repository
3. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (DATABASE_URL, JWT secrets, CORS_ORIGINS)

### 11.3 Frontend Deployment (Vercel)
1. Import project on Vercel
2. Configure:
   - Root Directory: `frontend`
   - Framework Preset: Next.js
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`

### 11.4 Production Checklist
- [ ] Generate new production secrets
- [ ] Update CORS_ORIGINS with production frontend URL
- [ ] Remove debug logs
- [ ] Set ENVIRONMENT=production
- [ ] Test full auth flow

---

## 12. File Structure

```
EVOLUTION-OF-TODO-006-user-auth/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment config
│   └── src/
│       ├── api/
│       │   ├── auth.py            # Auth endpoints
│       │   ├── tasks.py           # Task CRUD endpoints
│       │   └── health.py          # Health check endpoints
│       ├── auth/
│       │   ├── better_auth_config.py  # JWT token functions
│       │   └── token_store.py     # Token blacklist
│       ├── core/
│       │   ├── config.py          # Settings management
│       │   └── database.py        # DB connection & sessions
│       ├── dependencies/
│       │   └── auth.py            # Auth dependency injection
│       ├── models/
│       │   └── models.py          # User & Task SQLModels
│       ├── schemas/
│       │   ├── auth.py            # Auth request/response schemas
│       │   └── task.py            # Task request/response schemas
│       └── services/
│           └── task_service.py    # Task business logic
│
├── frontend/
│   ├── package.json               # Node dependencies
│   ├── next.config.ts             # Next.js config
│   ├── tailwind.config.ts         # Tailwind config
│   ├── lib/
│   │   ├── api-client.ts          # Generic API client
│   │   └── auth.ts                # Better Auth client
│   └── src/
│       ├── app/
│       │   ├── layout.tsx         # Root layout
│       │   ├── page.tsx           # Landing page
│       │   ├── dashboard/page.tsx # Task dashboard
│       │   └── auth/
│       │       ├── signin/page.tsx
│       │       └── signup/page.tsx
│       ├── components/
│       │   ├── tasks/
│       │   │   ├── TaskForm.tsx
│       │   │   └── TaskItem.tsx
│       │   └── ui/
│       │       └── loading-spinner.tsx
│       ├── hooks/
│       │   └── useTasks.ts        # TanStack Query hooks
│       └── lib/
│           ├── api.ts             # TaskAPI class
│           ├── auth-client.ts     # AuthClient class
│           ├── auth-provider.tsx  # React Context
│           └── types.ts           # TypeScript interfaces
│
├── .env.example                   # Environment template
├── .env.local.example             # Local env template
├── package.json                   # Root package.json
├── README.md                      # Project readme
├── DATABASE_SETUP.md              # Database setup guide
└── DEPLOYMENT.md                  # Deployment guide
```

---

## Quick Reference Card

| Action | Frontend | Backend |
|--------|----------|---------|
| **Start Dev Server** | `npm run dev` | `uvicorn main:app --reload` |
| **Default Port** | 3000 | 8000 |
| **API Base URL** | `http://localhost:8000` | N/A |
| **Auth Header** | `Authorization: Bearer <token>` | N/A |
| **Token Storage** | localStorage | N/A |
| **Task Endpoint** | `/api/tasks` | `/api/tasks` |
| **Auth Endpoint** | `/api/v1/auth/*` | `/api/v1/auth/*` |

---

*This documentation was generated by analyzing all source files in the project.*
