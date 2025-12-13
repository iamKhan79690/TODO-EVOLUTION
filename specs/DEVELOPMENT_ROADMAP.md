# Development Roadmap - Todo Full-Stack Application

## Overview
**Project**: The Evolution of Todo  
**Phase**: Hackathon II - Phase II  
**Deadline**: December 14, 2025, 11:59 PM  
**Points**: 150 (base) + up to 50 (bonuses)

---

## ✅ Phase 0: Project Setup - COMPLETED
**Status**: ✅ Done (Dec 6, 2025)

---

## 📋 Phase 1: Database Layer

### Agent to Use
```
@Database-Architect
```

### Step-by-Step Instructions

**Step 1.1: Create Neon Database**
```
@Database-Architect: Help me create a Neon PostgreSQL database and get the connection string
```
- Go to https://neon.tech
- Create free account
- Create new project named "todo-app"
- Copy connection string

**Step 1.2: Set Up Database Connection**
```
@Database-Architect: Create database.py with Neon PostgreSQL connection
```
This will create:
- `backend/app/database.py` - Connection pooling and session management

**Step 1.3: Create SQLModel Models**
```
@Database-Architect: Create SQLModel models for User and Task tables
```
This will create:
- `backend/app/models.py` - User and Task models with relationships

**Step 1.4: Verify Database**
```
@Database-Architect: Verify database connection and create tables
```
Run: `cd backend && uvicorn app.main:app --reload`
Check logs for "Database tables created successfully"

### Files Created
- `backend/app/database.py`
- `backend/app/models.py`
- `backend/.env` (with DATABASE_URL)

---

## 📋 Phase 2: Backend API

### Agent to Use
```
@Backend-Architect
```

### Step-by-Step Instructions

**Step 2.1: Create Pydantic Schemas**
```
@Backend-Architect: Create Pydantic schemas for Task CRUD operations
```
This will create:
- `backend/app/schemas.py` - TaskCreate, TaskUpdate, TaskResponse

**Step 2.2: Create Health Check Route**
```
@Backend-Architect: Create health check endpoint at GET /api/health
```
This will create:
- `backend/app/routes/health.py`

**Step 2.3: Create Task CRUD Routes**
```
@Backend-Architect: Implement all 6 task CRUD endpoints per constitution
```
This will create:
- `backend/app/routes/tasks.py` with:
  - GET /api/{user_id}/tasks
  - POST /api/{user_id}/tasks
  - GET /api/{user_id}/tasks/{id}
  - PUT /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH /api/{user_id}/tasks/{id}/complete

**Step 2.4: Test API**
```
@Backend-Architect: Verify all endpoints work via Swagger docs
```
- Open http://localhost:8000/docs
- Test each endpoint manually

### Files Created
- `backend/app/schemas.py`
- `backend/app/routes/health.py`
- `backend/app/routes/tasks.py`
- `backend/app/routes/__init__.py`

---

## 📋 Phase 3: Authentication

### Agent to Use
```
@BetterAuth-Engineer
```

### Step-by-Step Instructions

**Step 3.1: Backend JWT Verification**
```
@BetterAuth-Engineer: Create JWT verification middleware for FastAPI
```
This will create:
- `backend/app/auth.py` - JWT verification, user extraction, authorization

**Step 3.2: Protect All Routes**
```
@BetterAuth-Engineer: Add authentication to all task routes
```
This will update:
- `backend/app/routes/tasks.py` - Add auth dependencies

**Step 3.3: Frontend Better Auth Setup**
```
@BetterAuth-Engineer: Set up Better Auth in frontend with Neon PostgreSQL
```
This will create:
- `frontend/lib/auth.ts` - Server configuration
- `frontend/lib/auth-client.ts` - Client configuration
- `frontend/app/api/auth/[...all]/route.ts` - API handler

**Step 3.4: Create Auth Forms**
```
@BetterAuth-Engineer: Create SignIn and SignUp form components
```
This will create:
- `frontend/components/auth/SignInForm.tsx`
- `frontend/components/auth/SignUpForm.tsx`

**Step 3.5: Create Auth Pages**
```
@BetterAuth-Engineer: Create signin and signup pages
```
This will create:
- `frontend/app/auth/signin/page.tsx`
- `frontend/app/auth/signup/page.tsx`

**Step 3.6: Test Auth Flow**
```
@BetterAuth-Engineer: Verify complete authentication flow works
```
- Test signup with new email
- Test signin with existing email
- Verify JWT token is stored
- Verify signout clears token

### Files Created
- `backend/app/auth.py`
- `frontend/lib/auth.ts`
- `frontend/lib/auth-client.ts`
- `frontend/app/api/auth/[...all]/route.ts`
- `frontend/components/auth/SignInForm.tsx`
- `frontend/components/auth/SignUpForm.tsx`
- `frontend/app/auth/signin/page.tsx`
- `frontend/app/auth/signup/page.tsx`

---

## 📋 Phase 4: Frontend UI

### Agent to Use
```
@Frontend-Specialist
```

### Step-by-Step Instructions

**Step 4.1: Create API Client**
```
@Frontend-Specialist: Create centralized API client with JWT handling
```
This will create:
- `frontend/lib/api.ts` - TodoAPI class with all CRUD methods

**Step 4.2: Create TypeScript Types**
```
@Frontend-Specialist: Create TypeScript interfaces for Task and API responses
```
This will create:
- `frontend/lib/types.ts` - Task, TaskCreate, TaskUpdate, ErrorResponse

**Step 4.3: Create Task Components**
```
@Frontend-Specialist: Create TaskList, TaskItem, and TaskForm components
```
This will create:
- `frontend/components/tasks/TaskList.tsx`
- `frontend/components/tasks/TaskItem.tsx`
- `frontend/components/tasks/TaskForm.tsx`

**Step 4.4: Create Dashboard Page**
```
@Frontend-Specialist: Create protected dashboard page with task list
```
This will create:
- `frontend/app/(protected)/dashboard/page.tsx`
- `frontend/app/(protected)/layout.tsx` - Auth check wrapper

**Step 4.5: Create Landing Page**
```
@Frontend-Specialist: Create landing page with signin/signup links
```
This will update:
- `frontend/app/page.tsx` - Landing page

**Step 4.6: Add Styling**
```
@Frontend-Specialist: Apply Tailwind CSS styling to all components
```
This will update all components with proper Tailwind classes

**Step 4.7: Add Loading & Error States**
```
@Frontend-Specialist: Add loading spinners and error handling to all components
```
- Loading states during API calls
- Error messages for failures
- Empty states for no tasks

**Step 4.8: Make Mobile Responsive**
```
@Frontend-Specialist: Ensure all pages work on mobile (375px viewport)
```
- Test in Chrome DevTools mobile view
- Fix any layout issues

### Files Created
- `frontend/lib/api.ts`
- `frontend/lib/types.ts`
- `frontend/components/tasks/TaskList.tsx`
- `frontend/components/tasks/TaskItem.tsx`
- `frontend/components/tasks/TaskForm.tsx`
- `frontend/app/(protected)/dashboard/page.tsx`
- `frontend/app/(protected)/layout.tsx`

---

## 📋 Phase 5: Integration & Testing

### Agent to Use
```
@Testing-Coordinator
```

### Step-by-Step Instructions

**Step 5.1: Run Authentication Tests**
```
@Testing-Coordinator: Execute authentication test suite
```
Tests:
- AUTH-001: Sign up with valid credentials
- AUTH-002: Sign up with invalid email
- AUTH-003: Sign in with valid credentials
- AUTH-004: Sign in with wrong password
- AUTH-005: Sign out
- AUTH-006: Access protected route without auth

**Step 5.2: Run CRUD Tests**
```
@Testing-Coordinator: Execute CRUD test suite
```
Tests:
- CRUD-001: Create task
- CRUD-002: Create task with empty title
- CRUD-003: Read tasks list
- CRUD-004: Update task title
- CRUD-005: Delete task
- CRUD-006: Mark task complete
- CRUD-007: Mark task incomplete

**Step 5.3: Run Security Tests**
```
@Testing-Coordinator: Execute security test suite
```
Tests:
- SEC-001: Access another user's tasks via URL
- SEC-002: Create task for another user
- SEC-003: Access API without JWT
- SEC-004: Access API with invalid JWT

**Step 5.4: Run UI/UX Tests**
```
@Testing-Coordinator: Execute UI/UX test suite
```
Tests:
- UI-001: Responsive design - Mobile
- UI-002: Loading states
- UI-003: Error message display
- UI-004: Empty state
- UI-005: Browser compatibility (Chrome, Firefox, Safari)

**Step 5.5: Fix Issues**
```
@Testing-Coordinator: Document and prioritize issues found
```
Then use appropriate agent to fix:
- Frontend issues → @Frontend-Specialist
- Backend issues → @Backend-Architect
- Auth issues → @BetterAuth-Engineer

### Output
- Test results document
- List of issues to fix

---

## 📋 Phase 6: Deployment

### Agent to Use
```
@Deployment-Coordinator
```

### Step-by-Step Instructions

**Step 6.1: Deploy Frontend to Vercel**
```
@Deployment-Coordinator: Deploy frontend to Vercel
```
Steps:
1. Connect GitHub repo to Vercel
2. Set root directory to `frontend`
3. Set environment variables:
   - NEXT_PUBLIC_API_URL
   - BETTER_AUTH_SECRET
   - BETTER_AUTH_URL
   - DATABASE_URL
4. Deploy

**Step 6.2: Deploy Backend to Railway**
```
@Deployment-Coordinator: Deploy backend to Railway
```
Steps:
1. Connect GitHub repo to Railway
2. Set root directory to `backend`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables:
   - DATABASE_URL
   - BETTER_AUTH_SECRET
   - CORS_ORIGINS
5. Deploy

**Step 6.3: Update Environment Variables**
```
@Deployment-Coordinator: Update frontend with production backend URL
```
- Update NEXT_PUBLIC_API_URL in Vercel to Railway URL
- Update CORS_ORIGINS in Railway to Vercel URL

**Step 6.4: Verify Production**
```
@Deployment-Coordinator: Run production verification tests
```
- Test signup on production
- Test signin on production
- Test all CRUD operations
- Verify no CORS errors

### Output
- Frontend URL: https://your-app.vercel.app
- Backend URL: https://your-backend.railway.app
- Both working correctly

---

## 📋 Phase 7: Documentation & Demo

### Step-by-Step Instructions

**Step 7.1: Complete README**
Update `README.md` with:
- Project overview
- Features list
- Tech stack
- Setup instructions
- Environment variables
- API documentation link
- Deployment URLs

**Step 7.2: Record Demo Video**
Requirements:
- Under 90 seconds
- Show signup flow
- Show signin flow
- Show all CRUD operations
- Show signout

**Step 7.3: Pre-Submission Checklist**
- [ ] All features working
- [ ] README complete
- [ ] Demo video recorded
- [ ] GitHub repo public
- [ ] Deployment URLs accessible

---

## 📋 Phase 8: Submission

**Deadline**: December 14, 2025, 11:59 PM

### Submission Checklist
- [ ] Public GitHub repository URL
- [ ] Frontend deployment URL (Vercel)
- [ ] Backend deployment URL (Railway)
- [ ] Demo video URL (YouTube/Loom)
- [ ] README with setup instructions

---

## 🎯 Quick Reference: Agent Commands

| Phase | Agent | Command |
|-------|-------|---------|
| 1 | @Database-Architect | Set up Neon PostgreSQL and SQLModel |
| 2 | @Backend-Architect | Implement all API endpoints |
| 3 | @BetterAuth-Engineer | Set up authentication |
| 4 | @Frontend-Specialist | Build UI components and pages |
| 5 | @Testing-Coordinator | Run all test suites |
| 6 | @Deployment-Coordinator | Deploy to Vercel + Railway |

---

## 📊 Points Breakdown

| Category | Points | Status |
|----------|--------|--------|
| **Functional** | 100 | ⏳ |
| Sign up | 15 | ⏳ |
| Sign in | 15 | ⏳ |
| Create task | 15 | ⏳ |
| View tasks | 15 | ⏳ |
| Update task | 10 | ⏳ |
| Delete task | 10 | ⏳ |
| Toggle complete | 10 | ⏳ |
| JWT auth | 10 | ⏳ |
| **Technical** | 30 | ⏳ |
| Next.js 16+ | 5 | ⏳ |
| FastAPI | 5 | ⏳ |
| SQLModel + Neon | 5 | ⏳ |
| Better Auth | 5 | ⏳ |
| Monorepo + specs | 5 | ⏳ |
| Deployment | 5 | ⏳ |
| **Documentation** | 20 | ⏳ |
| README | 5 | ⏳ |
| Specs | 5 | ⏳ |
| Demo video | 5 | ⏳ |
| Public repo | 5 | ⏳ |
| **TOTAL** | **150** | ⏳ |

---

## 🚀 Start Now!

**Next Step**: Phase 1 - Database Layer

Run this command to start:
```
@Database-Architect: Help me create a Neon PostgreSQL database and set up the connection
```

---

*"One agent at a time, one phase at a time, 150 points achieved."*
