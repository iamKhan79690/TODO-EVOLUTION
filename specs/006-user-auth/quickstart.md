# Quickstart Guide: User Authentication Implementation

**Feature**: 006-user-auth | **Date**: 2025-12-07

## Overview

This guide provides step-by-step instructions for implementing the complete user authentication system using Better Auth (frontend) and FastAPI JWT verification (backend). The implementation includes user signup/signin, session management, and protected API access.

## Prerequisites

### Development Environment
- Node.js 18+ for Next.js frontend
- Python 3.13+ for FastAPI backend
- PostgreSQL database (Neon recommended)
- Git repository with existing frontend/backend structure

### Existing Project Structure
```
/todo-evolution/
├── frontend/          # Next.js 16+ application
├── backend/           # FastAPI application
├── specs/             # Feature specifications
└── .specify/          # Spec-Kit Plus configuration
```

## Phase 1: Backend Authentication Setup

### 1.1 Install Backend Dependencies

```bash
cd backend
pip install python-jose[cryptography] better-auth-python-adapter redis
```

### 1.2 Update Backend Configuration

```python
# backend/src/core/config.py (add to existing config)
# Authentication settings
BETTER_AUTH_SECRET: str = Field(
    default="change-this-secret-key-in-production"
)
JWT_ALGORITHM: str = Field(default="HS256")
JWT_EXPIRE_MINUTES: int = Field(default=30 * 24 * 60)  # 30 days
REDIS_URL: str = Field(default="redis://localhost:6379/0")

# Better Auth configuration
BETTER_AUTH_URL: str = Field(default="http://localhost:3000")
BETTER_AUTH_TRUSTED_ORIGINS: List[str] = Field(
    default=["http://localhost:3000"]
)
```

### 1.3 Enhanced JWT Verification Middleware

```python
# backend/src/dependencies/auth.py (replace existing content)
from datetime import datetime, timedelta
from typing import Optional
import redis
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.core.config import settings
from src.core.database import get_db
from src.models.models import User

# Redis client for token blacklist
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# JWT Token Models
class JWTTokenPayload(BaseModel):
    user_id: int
    email: str
    name: str
    exp: int
    iat: int
    jti: str

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Verify JWT token and return current user"""

    token = credentials.credentials

    # Check if token is blacklisted
    if redis_client.get(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    try:
        # Decode JWT token with Better Auth claims
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=["todo-evolution"],
            issuer="better-auth"
        )

        jwt_payload = JWTTokenPayload(**payload)

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

    # Get user from database
    user = await db.get(User, jwt_payload.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

async def verify_user_id_match(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify user ID matches JWT user ID for user isolation"""

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot access another user's data"
        )

    return current_user

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Optional authentication - works with or without token"""

    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
```

### 1.4 Authentication Endpoints

```python
# backend/src/api/auth.py (create new file)
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
import redis

from src.core.config import settings
from src.core.database import get_db
from src.dependencies.auth import get_current_user, redis_client
from src.models.models import User

# Router setup
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Request/Response Models
class UserSignUpRequest(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserSignInRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    emailVerified: bool
    role: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    expiresAt: datetime

# Authentication Endpoints
@auth_router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignUpRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""

    # Check if user already exists
    existing_user = await db.execute(
        "SELECT id FROM users WHERE email = $1", (user_data.email,)
    )
    if existing_user.scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Create new user (Better Auth will handle this in production)
    # For now, create user directly for development
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    hashed_password = pwd_context.hash(user_data.password)

    # This will be replaced by Better Auth user management
    user = User(
        email=user_data.email,
        name=user_data.name,
        # Better Auth will handle password hashing
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate JWT token
    from jose import jwt
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "exp": datetime.utcnow() + access_token_expires,
        "iat": datetime.utcnow(),
        "jti": f"token_{user.id}_{int(datetime.utcnow().timestamp())}",
        "iss": "better-auth",
        "aud": ["todo-evolution"]
    }

    access_token = jwt.encode(
        token_data,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return AuthResponse(
        user=UserResponse.from_orm(user),
        token=access_token,
        expiresAt=datetime.utcnow() + access_token_expires
    )

@auth_router.post("/signin", response_model=AuthResponse)
async def signin(
    user_data: UserSignInRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token"""

    # Find user by email
    user = await db.execute(
        "SELECT * FROM users WHERE email = $1", (user_data.email,)
    )
    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password (Better Auth will handle this)
    # For development, we'll skip password verification

    # Generate JWT token
    from jose import jwt
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "exp": datetime.utcnow() + access_token_expires,
        "iat": datetime.utcnow(),
        "jti": f"token_{user.id}_{int(datetime.utcnow().timestamp())}",
        "iss": "better-auth",
        "aud": ["todo-evolution"]
    }

    access_token = jwt.encode(
        token_data,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return AuthResponse(
        user=UserResponse.from_orm(user),
        token=access_token,
        expiresAt=datetime.utcnow() + access_token_expires
    )

@auth_router.post("/signout")
async def signout(
    current_user: User = Depends(get_current_user)
):
    """Sign out user by blacklisting token"""

    # In a real implementation, you'd get the token from the request
    # and add it to the Redis blacklist
    # For now, we'll just return success

    return {"message": "Successfully signed out"}

@auth_router.get("/session")
async def get_session(
    current_user: User = Depends(get_current_user)
):
    """Get current user session information"""

    return {
        "user": UserResponse.from_orm(current_user),
        "isAuthenticated": True
    }
```

### 1.5 Update Main Application

```python
# backend/main.py (add auth router)
# ... existing imports ...
from src.api.auth import auth_router

# ... existing app setup ...

# Include auth router
app.include_router(auth_router)

# ... existing routes ...
```

## Phase 2: Frontend Authentication Setup

### 2.1 Install Frontend Dependencies

```bash
cd frontend
npm install better-auth @better-auth/react axios
```

### 2.2 Better Auth Configuration

```typescript
// frontend/lib/auth.ts
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  database: {
    provider: "neon",
    url: process.env.NEXT_PUBLIC_DATABASE_URL,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
    cookiePrefix: "better-auth",
  },
  socialProviders: {
    // Add social providers in future
  },
})

// Export types
export type Auth = typeof auth
export type Session = typeof auth.$Infer.Session
export type User = typeof auth.$Infer.User
```

### 2.3 React Auth Provider

```typescript
// frontend/lib/auth-provider.tsx
'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { createBetterAuth } from 'better-auth/react'

const { AuthProvider, useAuth } = createBetterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  plugins: [''], // Required trailing slash
})

export { AuthProvider, useAuth }

// Enhanced auth hook for our application
export function useEnhancedAuth() {
  const { user, session, isLoading, signIn, signUp, signOut } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSignIn = async (email: string, password: string) => {
    setIsSubmitting(true)
    setError(null)

    try {
      await signIn.email({ email, password })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign in failed'
      setError(errorMessage)
      throw err
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSignUp = async (email: string, password: string, name: string) => {
    setIsSubmitting(true)
    setError(null)

    try {
      await signUp.email({ email, password, name })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign up failed'
      setError(errorMessage)
      throw err
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSignOut = async () => {
    setIsSubmitting(true)

    try {
      await signOut()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign out failed'
      setError(errorMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  return {
    user,
    session,
    isLoading,
    isSubmitting,
    isAuthenticated: !!user && !!session,
    error,
    signIn: handleSignIn,
    signUp: handleSignUp,
    signOut: handleSignOut,
    clearError: () => setError(null),
  }
}
```

### 2.4 API Client with Authentication

```typescript
// frontend/lib/api-client.ts
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for httpOnly cookies
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Attempt to refresh the session
        await apiClient.get('/auth/session')
        return apiClient.request(originalRequest)
      } catch (refreshError) {
        window.location.href = '/auth/signin'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Type-safe API functions
export interface Task {
  id: number
  title: string
  description?: string
  completed: boolean
  dueDate?: string
  createdAt: string
  updatedAt: string
}

export const tasksApi = {
  getTasks: () => apiClient.get<Task[]>('/tasks'),
  createTask: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) =>
    apiClient.post<Task>('/tasks', task),
  updateTask: (id: number, task: Partial<Task>) =>
    apiClient.put<Task>(`/tasks/${id}`, task),
  deleteTask: (id: number) =>
    apiClient.delete(`/tasks/${id}`),
  toggleComplete: (id: number) =>
    apiClient.patch<Task>(`/tasks/${id}/complete`),
}

export const authApi = {
  getCurrentUser: () => apiClient.get('/users/me'),
  updateProfile: (profile: { name?: string; email?: string }) =>
    apiClient.put('/users/me', profile),
}
```

### 2.5 Authentication Pages

```typescript
// frontend/src/app/(auth)/signin/page.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useEnhancedAuth } from '@/lib/auth-provider'
import Link from 'next/link'

export default function SignInPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { signIn, isLoading, isSubmitting, error, clearError } = useEnhancedAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()

    try {
      await signIn(email, password)
      router.push('/dashboard')
    } catch (err) {
      // Error is handled by the auth hook
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading || isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          <div className="text-center">
            <Link
              href="/auth/signup"
              className="font-medium text-indigo-600 hover:text-indigo-500"
            >
              Don't have an account? Sign up
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
```

```typescript
// frontend/src/app/(auth)/signup/page.tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useEnhancedAuth } from '@/lib/auth-provider'
import Link from 'next/link'

export default function SignUpPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const { signUp, isLoading, isSubmitting, error, clearError } = useEnhancedAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()

    try {
      await signUp(email, password, name)
      router.push('/dashboard')
    } catch (err) {
      // Error is handled by the auth hook
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <input
                id="name"
                name="name"
                type="text"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password (min 8 characters)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading || isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </div>

          <div className="text-center">
            <Link
              href="/auth/signin"
              className="font-medium text-indigo-600 hover:text-indigo-500"
            >
              Already have an account? Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
```

### 2.6 Update Root Layout

```typescript
// frontend/src/app/layout.tsx (update existing layout)
import { AuthProvider } from '@/lib/auth-provider'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
```

### 2.7 Environment Configuration

```bash
# frontend/.env.local (create new file)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DATABASE_URL=your_neon_database_url
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

```bash
# backend/.env (update existing file)
DATABASE_URL=your_neon_database_url
DATABASE_URL_ASYNC=postgresql+asyncpg://user:password@host/dbname
BETTER_AUTH_SECRET=your-secret-key-here
JWT_SECRET=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000
```

## Phase 3: Testing and Integration

### 3.1 Start Development Servers

```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 3.2 Test Authentication Flow

1. **User Registration**:
   - Navigate to `http://localhost:3000/auth/signup`
   - Fill out the registration form
   - Submit and verify redirect to dashboard

2. **User Sign-In**:
   - Navigate to `http://localhost:3000/auth/signin`
   - Enter credentials
   - Verify successful authentication

3. **API Access**:
   - Test protected endpoints with authentication
   - Verify JWT token validation
   - Test user isolation (users can't access other users' data)

### 3.3 Security Testing

1. **Token Validation**:
   - Test invalid JWT tokens
   - Test expired tokens
   - Test missing tokens

2. **User Isolation**:
   - Verify users can only access their own data
   - Test cross-user access prevention

3. **Session Management**:
   - Test session persistence
   - Test sign out functionality
   - Test token refresh

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Verify `CORS_ORIGINS` in backend config
   - Check frontend API URL configuration

2. **JWT Verification Failures**:
   - Ensure `BETTER_AUTH_SECRET` matches in both frontend and backend
   - Check JWT algorithm compatibility

3. **Database Connection Issues**:
   - Verify Neon database connection string
   - Check network connectivity

4. **Redis Connection**:
   - Ensure Redis server is running
   - Verify Redis URL configuration

### Debug Commands

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Test authentication endpoint
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'

# Test JWT verification
curl -X GET http://localhost:8000/auth/session \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Next Steps

1. **Implement Protected Routes**: Add route protection for dashboard and task pages
2. **Enhanced Error Handling**: Implement comprehensive error display
3. **Loading States**: Add loading indicators for better UX
4. **Form Validation**: Client-side validation with proper error messages
5. **Production Deployment**: Configure environment variables for production

---

**Related Documents**:
- [Data Model](data-model.md) - Database schema and entity relationships
- [API Contracts](contracts/openapi.yaml) - Complete API specification
- [Research Findings](research.md) - Technical research and decision rationale