# Todo Full-Stack Web Application Constitution
## Phase II - Hackathon II

## Core Principles

### I. Spec-Driven Development (Foundational Mandate)
All features MUST originate from specifications before implementation. Use GitHub Spec-Kit Plus for specification management. Follow the workflow: constitution → spec → plan → tasks → implementation. Every feature requires:
- **Specification Document**: Clear acceptance criteria, user stories, and technical requirements
- **Architecture Decision Records (ADRs)**: Document significant architectural choices
- **Prompt History Records (PHRs)**: Track all major Claude Code work sessions
- **Validation Checkpoints**: Verify spec alignment before, during, and after implementation

**Non-Negotiable**: No code without spec. No spec changes without documented rationale. Claude Code agents MUST reference specs using `@specs/path/to/file.md` syntax.

### II. Monorepo Architecture Excellence
Single repository with clear separation of concerns:
- **/frontend**: Next.js 16+ application (App Router, TypeScript, Tailwind CSS)
- **/backend**: Python FastAPI server (SQLModel, Neon PostgreSQL)
- **/specs**: Organized specifications (features/, api/, database/, ui/)
- **/.spec-kit**: Configuration and spec management
- **CLAUDE.md files**: Layered context (root, frontend/, backend/)

**Root-level Integration**: Both frontend and backend must be developed in single Claude Code context. Cross-cutting changes (auth flow, API contracts) edited together to maintain consistency.

### III. Authentication & Security Framework
**Better Auth + JWT Integration** (Non-Negotiable):
- Better Auth handles frontend authentication (Next.js)
- JWT tokens issued on login, stored securely client-side
- FastAPI backend verifies JWT on every request
- Shared secret (`BETTER_AUTH_SECRET`) between frontend/backend
- User isolation enforced at database level (all queries filtered by user_id)

**Security Standards**:
- No API keys in code (environment variables only)
- HTTPS in production (HTTP localhost in dev)
- Input validation on all endpoints (Pydantic models)
- SQL injection prevention (SQLModel parameterized queries)
- CORS properly configured (allow frontend origin)
- Rate limiting on auth endpoints (prevent brute force)

### IV. Database Design & Data Integrity
**Neon Serverless PostgreSQL** as single source of truth:
- **users table**: Managed by Better Auth (id, email, name, created_at)
- **tasks table**: User-owned tasks (id, user_id FK, title, description, completed, created_at, updated_at)

**Data Integrity Rules**:
- Foreign key constraints enforced (tasks.user_id → users.id)
- NOT NULL on required fields (title, user_id, completed)
- Timestamps auto-managed (created_at on insert, updated_at on update)
- Cascading deletes on user deletion (delete all user's tasks)
- Indexes on query patterns (user_id, completed status)

**Migration Strategy**:
- SQLModel schema definitions are source of truth
- Alembic for database migrations (Phase III onwards)
- Phase II: Direct SQLModel create_all() acceptable for MVP
- Document schema changes in `/specs/database/migrations.md`

### V. API Contract & REST Principles
**RESTful Endpoint Design** (Strict Adherence):

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | /api/{user_id}/tasks | List all user's tasks | Yes (JWT) |
| POST | /api/{user_id}/tasks | Create new task | Yes (JWT) |
| GET | /api/{user_id}/tasks/{id} | Get task details | Yes (JWT) |
| PUT | /api/{user_id}/tasks/{id} | Update task | Yes (JWT) |
| DELETE | /api/{user_id}/tasks/{id} | Delete task | Yes (JWT) |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion | Yes (JWT) |

**API Standards**:
- Return proper HTTP status codes (200, 201, 400, 401, 404, 500)
- JSON responses only (application/json content-type)
- Error responses follow standard format: `{"detail": "error message"}`
- Request validation via Pydantic models (auto-generated docs)
- User in JWT must match user_id in URL (authorization check)
- 401 Unauthorized if JWT missing/invalid
- 404 Not Found if task doesn't exist or doesn't belong to user

### VI. Frontend Architecture & User Experience
**Next.js 16+ App Router** with modern best practices:
- **Server Components by default**: Data fetching on server, less client JS
- **Client Components when needed**: Interactivity, forms, state management
- **API Client Pattern**: Centralized `/lib/api.ts` for all backend calls
- **Tailwind CSS styling**: Utility-first, no inline styles
- **TypeScript strict mode**: Type safety across application
- **Responsive design**: Mobile-first approach, tested on phone viewport

**Component Structure**:
- `/app`: Pages and layouts (App Router structure)
- `/components`: Reusable UI components (TaskList, TaskItem, TaskForm)
- `/lib`: Utilities (api.ts, auth.ts, types.ts)
- `/styles`: Global CSS and Tailwind config

**User Flow Requirements**:
1. **Landing Page**: Sign up / Sign in options
2. **Authentication**: Better Auth signup/signin forms
3. **Dashboard**: List of tasks, add new task form
4. **Task Management**: View, edit, delete, mark complete
5. **Loading States**: Show spinners during API calls
6. **Error Handling**: Display user-friendly error messages

### VII. Backend Architecture & API Design
**FastAPI Best Practices**:
- **main.py**: Application entry point, middleware setup, CORS config
- **models.py**: SQLModel database models (Task, User reference)
- **routes/**: Modular route handlers (tasks.py, auth.py)
- **database.py**: Database connection, session management
- **auth.py**: JWT verification middleware
- **schemas.py**: Pydantic request/response models

**FastAPI Patterns**:
- Dependency injection for database sessions
- JWT verification as dependency (protect routes)
- Async/await for database operations (async session)
- HTTPException for error responses
- Pydantic models for automatic validation
- Auto-generated OpenAPI docs at `/docs`

**Database Session Management**:
```python
from sqlmodel import Session, create_engine, select
from fastapi import Depends

# Engine singleton
engine = create_engine(DATABASE_URL)

# Dependency for sessions
def get_session():
    with Session(engine) as session:
        yield session

# Usage in routes
@app.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, session: Session = Depends(get_session)):
    # Use session for queries
    pass
```

### VIII. Better Auth Integration Architecture
**Authentication Flow**:

1. **Frontend (Better Auth)**:
   - User signs up/signs in via Better Auth UI
   - Better Auth creates session, issues JWT token
   - Token stored in httpOnly cookie or localStorage
   - Token sent in Authorization header on API requests

2. **Backend (FastAPI)**:
   - Extract JWT from Authorization: Bearer <token> header
   - Verify JWT signature using BETTER_AUTH_SECRET
   - Decode JWT to get user_id, email
   - Match user_id from JWT with user_id in URL path
   - Reject if mismatch (user can't access another user's data)

**Configuration Requirements**:
- Frontend: Better Auth config with JWT plugin enabled
- Backend: JWT verification middleware using python-jose or similar
- Shared: BETTER_AUTH_SECRET environment variable (same value both sides)
- Token Expiry: 7 days default, configurable

**Security Enforcement**:
- All /api/* endpoints MUST verify JWT (except public endpoints if any)
- User isolation: WHERE user_id = {jwt_user_id} on all queries
- No task operations without valid, matching JWT

### IX. Development Workflow & Tooling
**Daily Development Cycle**:
1. **Morning**: Review specs in `/specs`, check acceptance criteria
2. **Implementation**: Use Claude Code with spec references (`@specs/features/task-crud.md`)
3. **Testing**: Manual testing via frontend UI + API docs (`/docs`)
4. **Commit**: Git commits reference spec and feature (e.g., "feat: implement task creation - refs #task-crud-spec")
5. **Evening**: Update PHR with session summary, blockers, decisions

**Claude Code Usage**:
- Always reference relevant specs before implementing
- Use layered CLAUDE.md files (root → frontend → backend)
- Ask for implementation: "Implement @specs/features/authentication.md"
- Update specs if requirements change during implementation
- Create ADRs for architectural decisions (e.g., "Why JWT over sessions?")

**Version Control**:
- Git branches: `main` (stable), `develop` (active), `feature/*` (specific features)
- Commit messages: Conventional commits (feat:, fix:, docs:, refactor:)
- No secrets in git (use .gitignore, .env files)
- README.md updated with setup instructions

### X. Quality Standards & Acceptance Criteria
**Code Quality Gates** (Pre-Merge Checklist):
- [ ] TypeScript compiles without errors (frontend)
- [ ] Python type hints correct, mypy passes (backend)
- [ ] ESLint + Prettier passing (frontend)
- [ ] Ruff/Black formatting applied (backend)
- [ ] No hardcoded secrets (API keys, DB strings)
- [ ] All environment variables documented in .env.example
- [ ] CLAUDE.md files updated if patterns changed

**Feature Completeness** (Definition of Done):
- [ ] Spec acceptance criteria ALL met
- [ ] API endpoints tested via FastAPI /docs
- [ ] Frontend UI works on desktop and mobile
- [ ] Authentication flow tested (signup, signin, logout)
- [ ] User isolation verified (can't access other users' tasks)
- [ ] Error handling works (network errors, auth failures)
- [ ] Loading states implemented (no jarring UI changes)

**Performance Targets**:
- Frontend page load: <3 seconds
- API response time: <500ms (simple CRUD)
- Database query time: <100ms (indexed queries)
- Frontend bundle size: <500KB (excluding images)

### XI. Testing Strategy (Phase II Scope)
**Manual Testing Requirements** (Automated tests in Phase III+):
1. **Authentication Testing**:
   - Sign up with new email
   - Sign in with existing email
   - Invalid credentials rejected
   - JWT token issued and stored
   - JWT sent on subsequent requests
   - Expired JWT rejected (401)

2. **CRUD Testing**:
   - Create task → verify in database
   - List tasks → only user's tasks shown
   - Update task → changes persisted
   - Delete task → removed from list
   - Mark complete → status toggled

3. **Security Testing**:
   - Try accessing /api/another-user-id/tasks with your JWT → 403 Forbidden
   - Request without Authorization header → 401 Unauthorized
   - Invalid JWT → 401 Unauthorized

4. **UI/UX Testing**:
   - Test on Chrome, Firefox, Safari
   - Test on mobile viewport (375px width)
   - Forms validate input before submission
   - Error messages display clearly
   - Loading spinners show during API calls

**Testing Documentation**:
- Create `/specs/testing/manual-test-plan.md`
- Document test cases and expected outcomes
- Track bugs in GitHub Issues
- Reproduce bugs before fixing (test case first)

### XII. Deployment & Infrastructure
**Vercel Deployment (Frontend)**:
- Connect GitHub repo to Vercel
- Auto-deploy on push to main branch
- Environment variables set in Vercel dashboard (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET)
- Build command: `npm run build`
- Output directory: `.next`

**Backend Deployment Options**:
- **Railway** (Recommended for Phase II): Easy Python deployment, free tier
- **Render**: Free tier available, automatic HTTPS
- **Fly.io**: Global edge deployment, free tier
- **Self-hosted**: VPS with Docker (DigitalOcean, Linode)

**Environment Variables Required**:

**Frontend (.env.local)**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000  # or deployed backend URL
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000  # or deployed frontend URL
```

**Backend (.env)**:
```
DATABASE_URL=postgresql://user:pass@neon.tech/dbname
BETTER_AUTH_SECRET=your-secret-key-here  # MUST match frontend
CORS_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app
```

**Deployment Checklist**:
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway/Render/Fly.io
- [ ] Neon database created and connected
- [ ] Environment variables set on both platforms
- [ ] CORS configured to allow frontend origin
- [ ] HTTPS enabled on both frontend and backend
- [ ] Database migrations applied (if using Alembic)
- [ ] Test production deployment (sign up, create task, etc.)

### XIII. Documentation Requirements
**README.md Structure**:
```markdown
# Todo Full-Stack Web Application - Phase II

## Overview
Brief description of the application and its purpose.

## Features
- User authentication (Better Auth)
- Task CRUD operations
- User-specific task lists

## Tech Stack
- Frontend: Next.js 16, TypeScript, Tailwind CSS
- Backend: Python FastAPI, SQLModel
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth with JWT

## Setup Instructions
### Prerequisites
- Node.js 18+
- Python 3.13+
- Neon database account

### Installation
1. Clone repository
2. Install frontend dependencies
3. Install backend dependencies
4. Set up environment variables
5. Run database migrations
6. Start development servers

### Running Locally
- Frontend: npm run dev (http://localhost:3000)
- Backend: uvicorn main:app --reload (http://localhost:8000)

## API Documentation
Available at http://localhost:8000/docs

## Deployment
- Frontend: Vercel (auto-deploy from main branch)
- Backend: Railway (auto-deploy from main branch)

## Contributing
Follow spec-driven development workflow (see /specs)

## License
MIT
```

**CLAUDE.md Updates**:
- Root CLAUDE.md: Project overview, how to use specs, monorepo structure
- /frontend/CLAUDE.md: Next.js patterns, component structure, API client usage
- /backend/CLAUDE.md: FastAPI patterns, database operations, auth middleware

### XIV. Non-Goals (Explicitly Excluded from Phase II)
- ❌ Advanced features (recurring tasks, reminders, priorities) → Phase III+
- ❌ Chatbot interface (MCP, OpenAI Agents) → Phase III
- ❌ Real-time updates (WebSockets) → Phase IV/V
- ❌ Kubernetes deployment → Phase IV/V
- ❌ Event-driven architecture (Kafka, Dapr) → Phase V
- ❌ Automated testing (unit, integration tests) → Phase III+ (manual testing sufficient for Phase II)
- ❌ Multi-language support (Urdu translation) → Bonus feature
- ❌ Voice commands → Bonus feature
- ❌ Social features (sharing tasks, collaboration) → Out of scope

### XV. Risk Management & Mitigation
**Known Risks**:

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Better Auth setup complexity | High | Medium | Follow official docs, use example repos, test early |
| JWT verification bugs | High | Medium | Test auth flow thoroughly, log JWT contents (dev only) |
| Neon database connection issues | High | Low | Use connection pooling, handle reconnection, monitor |
| CORS errors in production | Medium | Medium | Test with deployed URLs early, configure properly |
| Vercel/Railway deployment failures | Medium | Low | Test deployment early, have backup deployment option |
| Time management (deadline Dec 14) | High | High | Daily progress tracking, prioritize base features first |

**Mitigation Strategies**:
1. **Early Integration Testing**: Test auth flow day 1, don't wait until end
2. **Incremental Development**: Get one feature fully working before next
3. **Daily Deployments**: Deploy to staging daily to catch deployment issues early
4. **Fallback Plans**: If Better Auth too complex, use simpler email/password with JWT manually
5. **Spec Discipline**: If feature taking too long, revisit spec, simplify if needed

### XVI. Success Metrics & Evaluation Criteria
**Phase II Success = 150 Points**:

**Functional Requirements (100 points)**:
- [ ] User can sign up with email/password (15 points)
- [ ] User can sign in with existing account (15 points)
- [ ] User can create tasks (15 points)
- [ ] User can view own tasks only (15 points)
- [ ] User can update tasks (10 points)
- [ ] User can delete tasks (10 points)
- [ ] User can mark tasks complete/incomplete (10 points)
- [ ] JWT authentication working (10 points)

**Technical Requirements (30 points)**:
- [ ] Next.js 16+ App Router used (5 points)
- [ ] FastAPI backend with proper structure (5 points)
- [ ] SQLModel + Neon PostgreSQL integration (5 points)
- [ ] Better Auth implemented correctly (5 points)
- [ ] Monorepo with spec-driven development (5 points)
- [ ] Deployed to Vercel + backend host (5 points)

**Documentation & Submission (20 points)**:
- [ ] README with complete setup instructions (5 points)
- [ ] Specs folder with all specifications (5 points)
- [ ] Demo video under 90 seconds (5 points)
- [ ] Public GitHub repository (5 points)

**Bonus Points (Not required for 150 base points)**:
- Excellent UI/UX design (+10)
- Comprehensive error handling (+10)
- Performance optimization (+10)
- Extra features beyond basic CRUD (+10)

### XVII. Timeline & Milestones (Dec 1 - Dec 14)
**Week 1 (Dec 1-7)**:
- **Dec 1-2**: Project setup, monorepo structure, database schema
- **Dec 3-4**: Authentication implementation (Better Auth + JWT)
- **Dec 5-6**: Backend API endpoints (CRUD operations)
- **Dec 7**: Phase I due, checkpoint review

**Week 2 (Dec 8-14)**:
- **Dec 8-9**: Frontend UI (Task list, forms, auth pages)
- **Dec 10-11**: Integration testing, bug fixes
- **Dec 12-13**: Deployment, documentation, demo video
- **Dec 14**: Phase II submission deadline (11:59 PM)

**Daily Checklist**:
- [ ] Morning: Review today's spec goals
- [ ] Work: Implement features using Claude Code
- [ ] Test: Verify features work via UI and API
- [ ] Document: Update specs, CLAUDE.md, commit with clear messages
- [ ] Deploy: Push to GitHub, auto-deploy to staging

### XVIII. Governance & Amendment Process
**Constitutional Authority**:
This constitution governs Phase II implementation. Deviations require explicit justification in ADR. Quality bar: "Impressive to judges" not "production-ready for years."

**Amendment Process**:
- **Minor amendments** (wording, clarifications): Document in commit message
  - Example: "docs: clarify JWT verification requirement in backend"
- **Major changes** (principle redefinitions, scope changes): Create ADR + update constitution
  - Example: "ADR-002: Switch from Better Auth to custom JWT implementation due to X"
- **Version bumping**: MAJOR.MINOR.PATCH
  - MAJOR: Breaking changes to principles (e.g., remove monorepo requirement)
  - MINOR: New sections added (e.g., add testing section)
  - PATCH: Wording improvements, typo fixes

**Compliance Review**:
- Before every feature merge: Check alignment with constitution
- Before deployment: Verify all non-negotiables met
- Before submission: Final checklist against success metrics

### XIX. Emergency Protocols
**If Behind Schedule**:
1. **Prioritize Base Features**: 5 basic CRUD operations + auth FIRST
2. **Cut Polish**: Simple UI acceptable, fancy styling is bonus
3. **Simplify Auth**: If Better Auth too complex, use simpler JWT manually
4. **Deploy Early**: Get basic version deployed, iterate from there

**If Blocked on Technical Issue**:
1. **Document**: Write clear issue in GitHub Issues
2. **Research**: Search official docs, Stack Overflow, GitHub Issues
3. **Ask**: Use hackathon Slack/Discord, office hours
4. **Workaround**: Implement alternative approach documented in ADR

**If Spec Conflicts with Reality**:
1. **Identify Conflict**: Clearly state what doesn't match
2. **Analyze**: Why is there a conflict? (Incomplete spec, wrong assumption)
3. **Propose Solution**: Update spec or implementation approach
4. **Document**: Create ADR explaining decision
5. **Update Constitution**: If principle needs changing

---

## Constitution Ratification

**Version**: 2.0.0  
**Ratified**: December 5, 2025  
**Last Amended**: December 5, 2025  
**Scope**: Phase II - Todo Full-Stack Web Application (Hackathon II)  
**Deadline**: Sunday, December 14, 2025, 11:59 PM  
**Points**: 150 (base) + up to 50 (bonuses)

**Next Step**: 
1. Create detailed feature specifications in `/specs/features/`
2. Use Claude Code with `@specs/features/[feature].md` references
3. Implement incrementally: Auth → Create Task → List Tasks → Update/Delete/Complete
4. Test continuously, deploy early, document thoroughly

**Reminder**: Spec-driven development is non-negotiable. No code without spec. Success comes from discipline, not shortcuts.

---

*"Clear specs, clean code, confident deployment."*  
— Phase II Mantra