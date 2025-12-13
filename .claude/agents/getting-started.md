# Phase II Todo App - Complete Setup & Getting Started Guide

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Sub-Agents & Skills Summary](#sub-agents--skills-summary)
3. [Installation & Setup](#installation--setup)
4. [Spec-Driven Development Workflow](#spec-driven-development-workflow)
5. [Claude Code Commands](#claude-code-commands)
6. [Daily Development Workflow](#daily-development-workflow)
7. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Phase**: II - Full-Stack Web Application  
**Deadline**: Sunday, December 14, 2025  
**Points**: 150 (base) + bonuses  
**Stack**: Next.js 16 + FastAPI + Neon PostgreSQL + Better Auth  

### Success Criteria
- ✅ User authentication (signup/signin) with Better Auth + JWT
- ✅ 5 basic CRUD operations for tasks (Create, Read, Update, Delete, Toggle Complete)
- ✅ User isolation (can only access own tasks)
- ✅ Deployed (Vercel frontend + Railway/Render backend)
- ✅ Spec-driven development followed throughout

---

## Sub-Agents & Skills Summary

### Your 7 Sub-Agents

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| **Frontend Specialist** | Next.js, TypeScript, Tailwind CSS | Building UI, components, pages |
| **Backend Architect** | FastAPI, SQLModel, Neon DB | API endpoints, database queries |
| **Spec Validator** | Validate implementation vs spec | Before marking feature complete |
| **Database Architect** | Schema design, query optimization | Database changes, performance |
| **API Contract Manager** | Frontend-backend alignment | API integration issues |
| **Security Auditor** | Auth, JWT, input validation | Before deployment, security review |
| **Deployment Coordinator** | Vercel, Railway/Render deployment | Final deployment phase |

### Key Skills (To Create)

| Skill | Description | Used By |
|-------|-------------|---------|
| **better-auth-jwt-integration** | JWT token handling, Better Auth setup | Frontend, Backend, Security |
| **neon-postgres-optimization** | Connection pooling, query patterns | Backend, Database |
| **api-contract-validation** | Type alignment, contract testing | Frontend, Backend, API Manager |
| **spec-driven-workflow** | How to work with specs effectively | All agents |
| **error-handling-patterns** | Consistent error handling | Frontend, Backend |

---

## Installation & Setup

### Step 1: Install Claude Code & Spec-Kit

```bash
# Install Spec-Kit Plus (spec-driven development toolkit)
npm install -g @github/spec-kit

# Verify installation
spec-kit --version

# Install UV for Python (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify UV installation
uv --version
```

### Step 2: Initialize Your Project

```bash
# Create project directory
mkdir hackathon-todo-phase2
cd hackathon-todo-phase2

# Initialize Git
git init
git branch -M main

# Initialize Spec-Kit in monorepo mode
spec-kit init . --monorepo

# This creates:
# /.spec-kit/config.yaml
# /specs/ (with subdirectories)
# /CLAUDE.md
# /.gitignore
```

### Step 3: Set Up Sub-Agents Directory

```bash
# Create Claude Code agents directory
mkdir -p .claude/agents
mkdir -p .claude/skills

# Copy the 7 sub-agent .md files you received to:
# .claude/agents/frontend-specialist.md
# .claude/agents/backend-architect.md
# .claude/agents/spec-validator.md
# .claude/agents/database-architect.md
# .claude/agents/api-contract-manager.md
# .claude/agents/security-auditor.md
# .claude/agents/deployment-coordinator.md
```

### Step 4: Create Skill Files

```bash
# Create skills directory structure
mkdir -p .claude/skills/better-auth-jwt
mkdir -p .claude/skills/neon-postgres
mkdir -p .claude/skills/api-contract
mkdir -p .claude/skills/spec-workflow
mkdir -p .claude/skills/error-handling
```

Create `SKILL.md` in each directory with skill content (I'll provide templates below).

### Step 5: Set Up Monorepo Structure

```bash
# Create monorepo directories
mkdir -p frontend backend specs/features specs/api specs/database specs/ui

# Copy constitution.md to root
# Copy Hackathon II DOCX content to /docs/ (for reference)

# Initialize frontend (Next.js)
cd frontend
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
npm install

# Initialize backend (FastAPI with UV)
cd ../backend
uv init
uv add fastapi sqlmodel psycopg2-binary python-jose[cryptography]
uv add --dev uvicorn[standard]

cd ..
```

### Step 6: Configure Spec-Kit

```yaml
# .spec-kit/config.yaml
name: hackathon-todo-phase2
version: "1.0"

structure:
  specs_dir: specs
  features_dir: specs/features
  api_dir: specs/api
  database_dir: specs/database
  ui_dir: specs/ui

phases:
  - name: phase2-web-app
    features:
      - authentication
      - task-crud
    
agents:
  - frontend-specialist
  - backend-architect
  - spec-validator
  - database-architect
  - api-contract-manager
  - security-auditor
  - deployment-coordinator

workflows:
  feature-development:
    steps:
      - validate-spec
      - implement-backend
      - implement-frontend
      - validate-implementation
      - test-integration
```

---

## Spec-Driven Development Workflow

### Core Principle
**NEVER write code before writing the spec.**

```
❌ Wrong Flow:
User wants feature → Start coding → Realize unclear requirements → Refactor → Bug fixes → Technical debt

✅ Correct Flow:
User wants feature → Write spec → Validate spec → Implement from spec → Verify against spec → Done
```

### Workflow Phases

#### Phase 1: Constitutional Setup (Once)
```bash
# Step 1: Create constitution.md at root
# (You already have this - constitution.md from earlier)

# Step 2: Review constitution with Claude Code
claude code

> @constitution.md Review and confirm understanding of Phase II requirements

# Claude will:
# - Analyze constitution
# - Ask clarifying questions
# - Confirm understanding
# - Be ready to enforce rules
```

#### Phase 2: Create Feature Specifications (Per Feature)

```bash
# Activate Claude Code in project root
claude code

# Command 1: Create feature spec
> /spec-kit create authentication

# Claude will:
# 1. Ask clarifying questions about the feature
# 2. Generate specs/features/authentication.md with:
#    - User stories
#    - Acceptance criteria
#    - API endpoints needed
#    - Database schema changes
#    - UI requirements
#    - Error scenarios
# 3. Ask for your review/approval

# Example conversation:
Claude: "I'll create the authentication feature spec. Let me ask some questions:

1. Authentication method: Better Auth with JWT or custom?
2. JWT expiry time: 7 days or custom?
3. Password requirements: Minimum length, special chars?
4. Session management: LocalStorage or httpOnly cookies?
5. Social auth needed? (Google, GitHub, etc.)

Please answer these questions."

You: "Better Auth with JWT, 7 days expiry, minimum 8 chars password, httpOnly cookies preferred, no social auth for Phase II."

Claude: "Perfect. Generating authentication.md spec..."

# [Claude generates comprehensive spec]

Claude: "I've created specs/features/authentication.md. Please review:
- User stories (3 stories)
- Acceptance criteria (12 criteria)
- API endpoints (signup, signin, signout)
- Database requirements (Better Auth tables)
- Security requirements (JWT verification, user isolation)

Would you like me to modify anything?"

You: "Looks good. Proceed."
```

#### Phase 3: Validate Specification

```bash
# Command 2: Validate spec
> @Spec-Validator: Validate @specs/features/authentication.md completeness

# Spec Validator checks:
# - All acceptance criteria testable?
# - API contracts defined?
# - Database changes documented?
# - Security requirements stated?
# - Error scenarios covered?

# Output example:
Spec Validator: "✅ Specification Validation Report

Completeness: 95% ✅

Missing Elements:
- Error message format for signup validation failures (add example)
- JWT refresh token strategy (clarify or state N/A for Phase II)

Ambiguities:
- 'Password must be secure' - define specific requirements

Recommendations:
1. Add example error responses
2. Clarify JWT expiry behavior on client
3. Add loading state requirements for forms

Overall: APPROVED with minor improvements suggested"

# Refine spec based on feedback
> @specs/features/authentication.md Update with validator feedback

# Validator re-checks
> @Spec-Validator: Re-validate @specs/features/authentication.md

Spec Validator: "✅ 100% Complete. Ready for implementation."
```

#### Phase 4: Create Implementation Plan

```bash
# Command 3: Generate implementation tasks
> /spec-kit plan authentication

# Claude (with Database Architect + API Contract Manager input) generates:
# specs/plans/authentication-plan.md with:
# - Task breakdown (8-12 tasks)
# - Dependency order (what must be done first)
# - File locations (which files to create/modify)
# - Agent assignments (which sub-agent does what)

# Example plan:
Implementation Plan: Authentication Feature

Task 1: Database Schema [Database Architect] (30 mins)
- Create users table (if not exists, Better Auth may create)
- Verify user_id field in tasks table
- Files: backend/app/models.py

Task 2: Backend JWT Middleware [Backend Architect] (45 mins)
- Implement JWT verification
- Create get_current_user dependency
- Files: backend/app/auth.py

Task 3: Backend Auth Routes [Backend Architect] (1 hour)
- Integrate with Better Auth
- Verify JWT issuance on signin
- Files: backend/app/routes/auth.py

Task 4: API Contract Definition [API Contract Manager] (20 mins)
- Document auth endpoints
- Define request/response schemas
- Files: specs/api/rest-endpoints.md

Task 5: Frontend Auth Client [Frontend Specialist] (1 hour)
- Configure Better Auth
- Create auth utilities
- Files: frontend/lib/auth.ts

Task 6: Frontend Auth Forms [Frontend Specialist] (1.5 hours)
- Create SignUpForm component
- Create SignInForm component
- Create auth pages
- Files: frontend/components/auth/, frontend/app/auth/

Task 7: Integration Testing [API Contract Manager] (45 mins)
- Test signup flow
- Test signin flow
- Test JWT verification
- Verify user isolation

Task 8: Security Audit [Security Auditor] (30 mins)
- Verify JWT secret strong
- Test auth bypass attempts
- Verify user isolation
- Check secrets not in code

Total Estimated Time: 6 hours 20 minutes
Dependencies: Tasks 1-2-3 must be sequential, 4-5-6 can be parallel after 3
```

#### Phase 5: Implement Feature (Task by Task)

```bash
# Command 4: Start implementation
> @Backend-Architect: Implement @specs/plans/authentication-plan.md Task 1-3

# Backend Architect will:
# 1. Read spec: @specs/features/authentication.md
# 2. Read plan: @specs/plans/authentication-plan.md
# 3. Implement Task 1: Database Schema
# 4. Implement Task 2: JWT Middleware
# 5. Implement Task 3: Auth Routes
# 6. Test via FastAPI /docs
# 7. Report completion

Backend Architect: "✅ Tasks 1-3 Complete

Implemented:
- users table (Better Auth managed)
- JWT verification middleware (backend/app/auth.py)
- Auth route handlers (backend/app/routes/auth.py)

Testing:
- POST /auth/signup: ✅ Working
- POST /auth/signin: ✅ Working, returns JWT
- JWT verification: ✅ Working, tested with test token

Files Modified:
- backend/app/models.py (User model reference)
- backend/app/auth.py (NEW - JWT verification)
- backend/app/routes/auth.py (NEW - auth endpoints)
- backend/app/main.py (registered auth router)

Next: Frontend implementation (Tasks 5-6)"

# Command 5: Continue with frontend
> @Frontend-Specialist: Implement @specs/plans/authentication-plan.md Task 5-6

Frontend Specialist: "✅ Tasks 5-6 Complete

Implemented:
- Better Auth configuration (frontend/lib/auth.ts)
- SignUpForm component (frontend/components/auth/SignUpForm.tsx)
- SignInForm component (frontend/components/auth/SignInForm.tsx)
- Signup page (frontend/app/auth/signup/page.tsx)
- Signin page (frontend/app/auth/signin/page.tsx)

Testing:
- Signup form: ✅ Validation working
- Signin form: ✅ Redirects after success
- JWT stored: ✅ In httpOnly cookie via Better Auth

Files Created:
- frontend/lib/auth.ts
- frontend/components/auth/SignUpForm.tsx
- frontend/components/auth/SignInForm.tsx
- frontend/app/auth/signup/page.tsx
- frontend/app/auth/signin/page.tsx

Next: Integration testing (Task 7)"
```

#### Phase 6: Validate Implementation

```bash
# Command 6: Validate against spec
> @Spec-Validator: Validate authentication feature implementation against @specs/features/authentication.md

Spec Validator: "📊 Implementation Validation Report

Acceptance Criteria Status: 11/12 ✅ (92%)

✅ PASS:
- AC-001: User can sign up with email/password
- AC-002: User can sign in with existing account
- AC-003: JWT token issued on successful signin
- AC-004: JWT token stored securely (httpOnly cookie)
- AC-005: JWT sent on API requests (Authorization header)
- AC-006: Invalid JWT rejected (401 Unauthorized)
- AC-007: User can access only own tasks (user isolation)
- AC-008: Signup form validates input
- AC-009: Error messages displayed clearly
- AC-010: Loading states during auth requests
- AC-011: User redirected to dashboard after signin

❌ FAIL:
- AC-012: User can sign out and JWT invalidated

Gap Details:
- AC-012: No signout functionality implemented
  - Missing: Signout button in UI
  - Missing: POST /auth/signout endpoint
  - Missing: Better Auth session clearing

Priority: HIGH (required for Phase II submission)
Estimated Fix Time: 30 minutes

Recommendation: Implement signout before marking feature complete."

# Fix missing functionality
> @Frontend-Specialist @Backend-Architect: Implement signout per AC-012

[Agents implement signout]

# Re-validate
> @Spec-Validator: Re-validate authentication feature

Spec Validator: "✅ 100% PASS. All 12 acceptance criteria met. Feature complete."
```

#### Phase 7: Security Audit

```bash
# Command 7: Security review
> @Security-Auditor: Audit authentication feature security

Security Auditor: "🔒 Security Audit Report

Overall: PASS ✅ with 1 recommendation

✅ Secure:
- JWT secret is strong (32+ chars, random)
- JWT stored in httpOnly cookie (XSS protection)
- JWT verification on all protected endpoints
- User isolation enforced (user_id filtering)
- Input validation via Pydantic (SQL injection prevented)
- No secrets in source code
- CORS configured correctly

⚠️ Recommendation:
- Add rate limiting on /auth/signin to prevent brute force attacks
  - Severity: MEDIUM
  - Impact: Production security
  - Effort: 20 minutes
  - Phase: Defer to Phase III (not required for Phase II)

Critical Issues: NONE ✅

Phase II Submission: APPROVED ✅"
```

#### Phase 8: Integration Testing

```bash
# Command 8: Test integration
> @API-Contract-Manager: Test authentication integration end-to-end

API Contract Manager: "🔌 Integration Test Report

Frontend ↔️ Backend ↔️ Database

✅ Test 1: User Signup
- Frontend form → POST /auth/signup → Database
- Result: User created, JWT returned ✅

✅ Test 2: User Signin
- Frontend form → POST /auth/signin → JWT issued
- Result: JWT stored in cookie, user redirected ✅

✅ Test 3: Authenticated API Request
- Frontend → GET /api/{user_id}/tasks (with JWT) → Backend verifies
- Result: Tasks returned (empty for new user) ✅

✅ Test 4: Invalid JWT
- Frontend → API request with invalid JWT
- Result: 401 Unauthorized, redirect to signin ✅

✅ Test 5: User Isolation
- User alice → Try accessing user bob's tasks
- Result: 403 Forbidden ✅

✅ Test 6: Signout
- User → Signout button → JWT cleared
- Result: Redirect to signin, subsequent requests fail ✅

All Integration Tests: PASSED ✅

Ready for next feature implementation."
```

---

## Claude Code Commands Reference

### Spec Management Commands

```bash
# Create new feature spec
/spec-kit create <feature-name>

# Validate spec completeness
@Spec-Validator: Validate @specs/features/<feature>.md

# Generate implementation plan
/spec-kit plan <feature-name>

# Update existing spec
/spec-kit update <feature-name>

# List all specs
/spec-kit list
```

### Agent Invocation Commands

```bash
# Frontend work
@Frontend-Specialist: Implement @specs/features/<feature>.md

# Backend work
@Backend-Architect: Implement @specs/features/<feature>.md

# Database changes
@Database-Architect: Design schema for @specs/features/<feature>.md

# Validate implementation
@Spec-Validator: Validate <feature> implementation

# Security review
@Security-Auditor: Audit <feature> security

# API alignment check
@API-Contract-Manager: Verify contract for <feature>

# Deploy
@Deployment-Coordinator: Deploy Phase II application
```

### Multi-Agent Coordination

```bash
# Assign multiple agents to complex task
@Backend-Architect @Frontend-Specialist: Implement authentication feature
- @Backend-Architect: Handle Tasks 1-3 (backend)
- @Frontend-Specialist: Handle Tasks 5-6 (frontend)
- Coordinate on API contract (Task 4)

# Request validation from multiple perspectives
@Spec-Validator @Security-Auditor: Review authentication feature before deployment
```

### Debugging & Troubleshooting

```bash
# Ask specific agent for help
@Backend-Architect: Why is POST /api/tasks returning 422?

# Get multiple perspectives
@API-Contract-Manager @Backend-Architect: Frontend sends {name: "Task"} but backend expects {title: "Task"}. Fix API contract mismatch.

# Security issue
@Security-Auditor: User can see other users' tasks. Audit user isolation.
```

---

## Daily Development Workflow

### Morning Routine (9:00 AM)
```bash
1. Review yesterday's work
   > @Spec-Validator: Status report on all features

2. Check today's plan
   > @specs/plans/[current-feature]-plan.md Review remaining tasks

3. Set priority
   > Today I'll implement tasks 4-6 of task-crud feature
```

### Implementation Loop (9:30 AM - 5:00 PM)
```bash
For each task:
1. Read spec: @specs/features/<feature>.md
2. Implement with agent: @<Agent>: Implement Task N
3. Test: Verify feature works locally
4. Validate: @Spec-Validator: Check Task N
5. Commit: git commit -m "feat: implement Task N per spec"
6. Next task

# Example 3-hour implementation session:
09:30 > @Backend-Architect: Implement Task 4 - Create task endpoint
10:15 > Test via /docs, verify task created in database
10:30 > @Spec-Validator: Validate Task 4
10:45 > git commit -m "feat(backend): implement create task endpoint"

11:00 > @Frontend-Specialist: Implement Task 5 - Task creation form
12:00 > Test in browser, create a task
12:15 > @Spec-Validator: Validate Task 5
12:30 > git commit -m "feat(frontend): implement task creation form"

[Lunch break]

13:30 > @API-Contract-Manager: Test create task integration
13:45 > Fix any contract mismatches found
14:00 > git commit -m "fix: align API contract for task creation"

14:15 > @Backend-Architect: Implement Task 6 - List tasks endpoint
15:00 > Test via /docs, verify tasks returned
15:15 > @Spec-Validator: Validate Task 6
15:30 > git commit -m "feat(backend): implement list tasks endpoint"
```

### Evening Wrap-up (5:00 PM)
```bash
1. Validate day's work
   > @Spec-Validator: Daily validation report

2. Security check (if auth/sensitive feature)
   > @Security-Auditor: Quick audit of today's changes

3. Update documentation
   > Update CLAUDE.md with any new patterns learned

4. Push to GitHub
   > git push origin main

5. Plan tomorrow
   > Tomorrow: Tasks 7-9, then integration testing
```

---

## Project Milestones & Timeline

### Week 1 (Dec 1-7) - Foundation

**Dec 1-2**: Setup
- [ ] Initialize monorepo
- [ ] Set up sub-agents and skills
- [ ] Create constitution.md
- [ ] Write authentication.md spec
- [ ] Write task-crud.md spec

**Dec 3-4**: Authentication
- [ ] Implement backend JWT verification
- [ ] Integrate Better Auth frontend
- [ ] Test signup/signin flows
- [ ] Security audit

**Dec 5-6**: Task CRUD (Backend)
- [ ] Implement all 5 backend endpoints
- [ ] Test via FastAPI /docs
- [ ] Database schema complete

**Dec 7**: Phase I Due (if doing)
- [ ] Console app checkpoint (if applicable)

### Week 2 (Dec 8-14) - Integration & Deployment

**Dec 8-9**: Task CRUD (Frontend)
- [ ] Implement TaskList component
- [ ] Implement TaskForm component
- [ ] Implement TaskItem component
- [ ] Test all CRUD operations

**Dec 10-11**: Integration & Polish
- [ ] Full integration testing
- [ ] Fix any contract mismatches
- [ ] Error handling comprehensive
- [ ] Loading states all working
- [ ] Mobile responsive testing

**Dec 12**: Deployment
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway/Render
- [ ] Verify production works
- [ ] Final security audit

**Dec 13**: Documentation & Demo
- [ ] README complete
- [ ] Record demo video (<90 seconds)
- [ ] Final validation against specs
- [ ] Pre-submission checklist

**Dec 14**: SUBMISSION DEADLINE
- [ ] Submit via form before 11:59 PM
- [ ] All acceptance criteria met
- [ ] Deployment working
- [ ] Demo video uploaded

---

## Troubleshooting Guide

### Issue: Agent Not Responding
```bash
# Problem: @Frontend-Specialist not acknowledging commands

# Solution 1: Check agent exists
ls .claude/agents/
# Should show: frontend-specialist.md

# Solution 2: Reinitialize Claude Code
claude code --reload-agents

# Solution 3: Explicitly reference agent file
> @.claude/agents/frontend-specialist.md Implement task
```

### Issue: Spec Validation Failing
```bash
# Problem: Spec Validator says "Incomplete spec"

# Solution: Ask for specific gaps
> @Spec-Validator: List missing elements in @specs/features/task-crud.md

# Fix gaps one by one
> @specs/features/task-crud.md Add error scenarios for all operations

# Re-validate
> @Spec-Validator: Re-validate @specs/features/task-crud.md
```

### Issue: API Contract Mismatch
```bash
# Problem: Frontend and backend not aligning

# Solution: Use API Contract Manager
> @API-Contract-Manager: Diagnose mismatch in task creation

# Output will show exact mismatches:
# Frontend sends: {name: "Task"}
# Backend expects: {title: "Task"}
# Fix: Update frontend to use "title"

# After fix, verify
> @API-Contract-Manager: Verify task creation contract
```

### Issue: Security Vulnerability Found
```bash
# Problem: Security Auditor found critical issue

# Solution: Address immediately
> @Security-Auditor: Provide detailed fix for user isolation issue

# Implement fix with relevant agent
> @Backend-Architect: Implement fix: Add user_id filter to all queries

# Verify fix
> @Security-Auditor: Re-audit user isolation
```

### Issue: Deployment Failing
```bash
# Problem: Vercel build fails

# Solution: Check logs
> @Deployment-Coordinator: Analyze Vercel build logs

# Common fixes:
# - Missing environment variables
# - Incorrect build command
# - Type errors in TypeScript
# - Missing dependencies in package.json

# Fix and redeploy
> Fix issues, then git push origin main
```

---

## Additional Resources

### Spec Templates Location
- `/specs/templates/feature-template.md` - Feature spec template
- `/specs/templates/api-template.md` - API endpoint template
- `/specs/templates/plan-template.md` - Implementation plan template

### Example Specs (Reference)
- `/specs/features/authentication.md` - Complete auth spec
- `/specs/features/task-crud.md` - Complete CRUD spec
- `/specs/api/rest-endpoints.md` - API contract spec

### Documentation
- `/CLAUDE.md` - Root-level Claude Code instructions
- `/frontend/CLAUDE.md` - Frontend-specific patterns
- `/backend/CLAUDE.md` - Backend-specific patterns
- `/constitution.md` - Non-negotiable project rules

### Learning Resources
- [GitHub Spec-Kit Docs](https://github.com/github/spec-kit)
- [Claude Code Sub-Agents Guide](https://docs.claude.com/en/docs/claude-code/sub-agents)
- [Better Auth Documentation](https://better-auth.com/docs)
- [Neon PostgreSQL Docs](https://neon.tech/docs)

---

## Quick Start Checklist

Before starting development, ensure:

- [ ] All 7 sub-agents created in `.claude/agents/`
- [ ] All skills created in `.claude/skills/`
- [ ] Spec-Kit installed and initialized
- [ ] Constitution.md at project root
- [ ] Monorepo structure set up (frontend/, backend/, specs/)
- [ ] Git initialized and .gitignore configured
- [ ] Environment variables templates created (.env.example)
- [ ] First spec created (authentication.md or task-crud.md)

**You're ready to start!** 🚀

```bash
# First command to give Claude Code:
> @constitution.md @specs/features/authentication.md

I'm ready to start Phase II development. Let's implement the authentication feature following spec-driven development principles. Please confirm you understand the constitution and the authentication spec, then we'll proceed with the implementation plan.
```

---

## Success Tips

1. **Spec First, Always**: Never skip spec creation. It saves time later.
2. **Validate Early**: Use Spec Validator after every major task.
3. **Test Incrementally**: Don't wait until end to test integration.
4. **Security Reviews**: Run security audit before any deployment.
5. **Commit Often**: Small, frequent commits with clear messages.
6. **Document Decisions**: Update CLAUDE.md when you discover new patterns.
7. **Ask Agents for Help**: Don't debug alone—use sub-agents.
8. **Follow Constitution**: It's not bureaucracy—it's quality guarante