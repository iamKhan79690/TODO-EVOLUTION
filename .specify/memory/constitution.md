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



# Phase IV: Local Kubernetes Deployment Constitution
## Hackathon II - Cloud Native Architecture

## Core Principles

### I. Infrastructure as Code (IaC) - Spec-Driven Deployment
All infrastructure components MUST originate from specifications before implementation. Use GitHub Spec-Kit Plus for infrastructure specification management.

**Workflow**: infrastructure-spec → containerization → helm-charts → deployment → validation

**Non-Negotiable Rules**:
- No manual YAML writing - use kubectl-ai/kagent to generate manifests
- No manual Dockerfile writing - use Gordon (Docker AI) to generate containers
- All infrastructure changes documented in `/specs/infrastructure/`
- Every deployment decision recorded in ADR (Architecture Decision Record)

### II. Containerization Standards (Docker + Gordon)

**Container Requirements**:
- **Multi-stage builds**: Minimize image size, separate build from runtime
- **Security hardening**: Non-root user (appuser), read-only root filesystem where possible
- **Image tagging**: Use semantic versioning (v1.0.0), never use `latest` tag
- **Base images**: Use official, minimal base images (node:20-alpine, python:3.13-slim)

**Services to Containerize**:
1. **Frontend (Next.js)**: Port 3000, standalone output mode
2. **Backend (FastAPI)**: Port 8000, uvicorn server
3. **MCP Server**: Port 8001, Python service

**Docker AI (Gordon) Usage**:
```bash
# Navigate to service directory, then:
docker ai "Create a production-ready multi-stage Dockerfile for this [Next.js/FastAPI/Python] service with security best practices"
```

**Dockerfile Requirements**:
- Stage 1: Dependencies installation
- Stage 2: Build artifacts
- Stage 3: Runtime with minimal footprint
- USER appuser (non-root)
- HEALTHCHECK directive included
- Explicit EXPOSE ports
- ENV variables for configuration

### III. Kubernetes Architecture (Minikube + Helm)

**Orchestration Stack**:
- **Local Cluster**: Minikube (single-node Kubernetes)
- **Package Manager**: Helm 3.x (chart-based deployment)
- **AI Operations**: kubectl-ai for manifest generation, kagent for cluster management

**Deployment Blueprint**:

| Service | Replicas | Port | Service Type | Health Probes |
|---------|----------|------|--------------|---------------|
| Frontend | 2 | 3000 | LoadBalancer | readiness + liveness |
| Backend | 2 | 8000 | ClusterIP | readiness + liveness |
| MCP Server | 1 | 8001 | ClusterIP | readiness + liveness |

**Resource Allocation Standards**:
- **Requests**: Minimum guaranteed resources (CPU: 100m, Memory: 128Mi)
- **Limits**: Maximum allowed resources (CPU: 500m, Memory: 512Mi)
- **Ratio**: Requests at 50% of Limits for optimal scheduling

### IV. Helm Chart Structure (AI-Generated)

**Chart Organization**:
```
todo-evolution-chart/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default configuration values
├── templates/
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── mcp-deployment.yaml
│   ├── mcp-service.yaml
│   ├── configmap.yaml      # Non-sensitive config
│   ├── secrets.yaml        # Sensitive credentials
│   └── ingress.yaml        # Optional: Load balancing rules
```

**Values.yaml Requirements**:
- Image repositories and tags for all services
- Replica counts (configurable per environment)
- Resource limits/requests
- Environment variables (DATABASE_URL, API keys via secrets)
- Service ports and types

**Generation Command** (kubectl-ai):
```bash
kubectl-ai "Generate a Helm chart for a todo app with frontend (Next.js), backend (FastAPI), and mcp-server deployments. Include services, configmaps, and secrets."
```

### V. Security & Hardening (Zero-Trust Architecture)

**Pod Security Standards** (Mandatory):
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true  # Where possible
  capabilities:
    drop:
      - ALL
```

**Secret Management**:
- Never commit secrets to git (use `.gitignore` for secrets.yaml)
- Use Kubernetes Secrets for sensitive data (DATABASE_URL, JWT_SECRET, OPENAI_API_KEY)
- Secrets mounted as environment variables or volume mounts
- Base64 encoding in secrets.yaml (NOT encryption - Minikube doesn't have KMS)

**RBAC (Role-Based Access Control)**:
- Create dedicated ServiceAccount for each deployment
- Apply "Least Privilege" principle (minimal permissions)
- No use of default ServiceAccount

**Network Policies** (Optional for Phase IV, Recommended):
- Restrict pod-to-pod communication
- Allow only necessary ingress/egress traffic

### VI. High Availability & Resilience

**Health Probes** (Non-Negotiable):
```yaml
# Liveness Probe: Restart pod if app crashes
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

# Readiness Probe: Remove pod from service if not ready
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Update Strategy**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1    # At most 1 pod down during update
    maxSurge: 1          # At most 1 extra pod during update
```

**Graceful Shutdown**:
- `terminationGracePeriodSeconds: 60` for stateful services
- Apps must handle SIGTERM signal for clean shutdown

**Anti-Affinity** (Multi-replica deployments):
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - frontend
          topologyKey: kubernetes.io/hostname
```

### VII. Observability & Monitoring

**Standard Labels** (Kubernetes Recommended):
```yaml
metadata:
  labels:
    app.kubernetes.io/name: todo-frontend
    app.kubernetes.io/instance: todo-prod
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
```

**Logging Standards**:
- Structured logging (JSON format) for backend services
- Log to stdout/stderr (Kubernetes collects automatically)
- Log levels: DEBUG (dev), INFO (prod), ERROR (always)

**Metrics Endpoints** (Phase V, but prepare now):
- `/metrics` endpoint for Prometheus scraping
- Basic metrics: request count, latency, error rate

### VIII. Configuration Management

**ConfigMaps** (Non-sensitive configuration):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-config
data:
  API_BASE_URL: "http://backend-service:8000"
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "development"
```

**Secrets** (Sensitive credentials):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
data:
  DATABASE_URL: <base64-encoded>
  JWT_SECRET: <base64-encoded>
  OPENAI_API_KEY: <base64-encoded>
```

**Environment Variables Injection**:
```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: todo-secrets
        key: DATABASE_URL
  - name: API_BASE_URL
    valueFrom:
      configMapKeyRef:
        name: todo-config
        key: API_BASE_URL
```

### IX. Minikube Local Development

**Minikube Setup**:
```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)
```

**Docker Image Strategy**:
- Build images inside Minikube's Docker daemon (no push to registry needed)
- Use `imagePullPolicy: IfNotPresent` in deployments
- Tag images with version numbers (e.g., `todo-frontend:1.0.0`)

**Service Access**:
- LoadBalancer services exposed via `minikube service <service-name>`
- NodePort services accessible at `<minikube-ip>:<node-port>`
- Ingress accessible at `<minikube-ip>` (if ingress enabled)

### X. AI-Assisted Operations (AIOps)

**Gordon (Docker AI)** - Containerization Assistant:
```bash
# Check Gordon capabilities
docker ai "What can you do?"

# Generate Dockerfiles
docker ai "Create a production-ready Dockerfile for this Next.js app"

# Optimize existing Dockerfile
docker ai "Optimize this Dockerfile for security and size"

# Troubleshoot build issues
docker ai "Why is my Docker build failing?"
```

**kubectl-ai** - Kubernetes Manifest Generator:
```bash
# Generate deployments
kubectl-ai "Deploy the todo frontend with 2 replicas and resource limits"

# Scale services
kubectl-ai "Scale the backend deployment to 3 replicas"

# Troubleshoot pods
kubectl-ai "Check why the backend pods are in CrashLoopBackOff"

# Generate services
kubectl-ai "Create a LoadBalancer service for the frontend on port 3000"
```

**kagent** - Cluster Management AI:
```bash
# Cluster health analysis
kagent "Analyze the cluster health and resource utilization"

# Optimization recommendations
kagent "Suggest optimizations for resource allocation"

# Debugging assistance
kagent "Investigate why the backend service is not reachable"
```

### XI. Deployment Workflow (Spec-Driven)

**Phase IV Implementation Pipeline**:

1. **Specification Stage**:
   - Write infrastructure specifications in `/specs/infrastructure/`
   - Define deployment requirements, resource needs, security policies
   - Create ADRs for major infrastructure decisions

2. **Containerization Stage**:
   - Use Gordon to generate Dockerfiles for each service
   - Build Docker images inside Minikube's Docker daemon
   - Test containers locally with `docker run`

3. **Helm Chart Generation Stage**:
   - Use kubectl-ai to generate Helm chart structure
   - Customize `values.yaml` with project-specific configuration
   - Validate Helm chart with `helm lint`

4. **Deployment Stage**:
   - Install Helm chart: `helm install todo-evolution ./todo-chart`
   - Verify deployments: `kubectl get pods,services,deployments`
   - Access services: `minikube service frontend-service`

5. **Validation Stage**:
   - Health checks passing: `kubectl get pods` (all Running)
   - Services reachable: `curl <service-url>/health`
   - Application functional: Test via browser/Postman
   - Logs clean: `kubectl logs <pod-name>`

### XII. Testing & Validation (Phase IV Scope)

**Container Testing**:
- [ ] Dockerfile builds without errors
- [ ] Container starts successfully: `docker run -p <port>:<port> <image>`
- [ ] Health endpoint responds: `curl http://localhost:<port>/health`
- [ ] Non-root user verified: `docker run <image> whoami` (should not be root)

**Kubernetes Deployment Testing**:
- [ ] Helm chart deploys without errors: `helm install --dry-run --debug`
- [ ] All pods reach Running state: `kubectl get pods`
- [ ] Services created correctly: `kubectl get services`
- [ ] Health probes working: `kubectl describe pod <pod-name>`
- [ ] Resource limits applied: `kubectl describe pod <pod-name>` (check resources)

**Integration Testing**:
- [ ] Frontend can reach Backend: Check network connectivity
- [ ] Backend can reach Database: Verify DATABASE_URL connection
- [ ] MCP Server accessible from Backend: Test inter-service communication
- [ ] Authentication working: Test JWT flow end-to-end
- [ ] CRUD operations functional: Create, read, update, delete tasks

**Security Testing**:
- [ ] Pods running as non-root: `kubectl exec <pod> -- id`
- [ ] Secrets mounted correctly: `kubectl exec <pod> -- env | grep SECRET`
- [ ] No sensitive data in logs: `kubectl logs <pod> | grep -i password`

### XIII. Troubleshooting & Debugging

**Common Issues & Solutions**:

| Issue | Diagnosis Command | Solution |
|-------|------------------|----------|
| ImagePullBackOff | `kubectl describe pod <pod>` | Check image name, ensure image exists in Minikube Docker |
| CrashLoopBackOff | `kubectl logs <pod>` | Check application logs, verify environment variables |
| Pending Pod | `kubectl describe pod <pod>` | Check resource availability, node capacity |
| Service Unreachable | `kubectl get endpoints <service>` | Verify pod labels match service selector |
| 401 Unauthorized | Check backend logs | Verify JWT_SECRET matches between frontend/backend |

**Debugging Commands**:
```bash
# Check pod status
kubectl get pods -o wide

# View pod logs
kubectl logs <pod-name> --tail=100 --follow

# Describe pod (events, conditions)
kubectl describe pod <pod-name>

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/sh

# Port forward for local testing
kubectl port-forward <pod-name> 8000:8000

# Check service endpoints
kubectl get endpoints <service-name>

# View cluster events
kubectl get events --sort-by='.lastTimestamp'
```

### XIV. Documentation Requirements

**README.md Updates** (Phase IV Section):
```markdown
## Phase IV: Kubernetes Deployment

### Prerequisites
- Docker Desktop with Gordon enabled
- Minikube installed
- kubectl and Helm installed
- kubectl-ai and kagent installed

### Setup Minikube Cluster
1. Start Minikube: `minikube start --cpus=4 --memory=8192`
2. Enable addons: `minikube addons enable ingress metrics-server`
3. Point Docker to Minikube: `eval $(minikube docker-env)`

### Build Docker Images
1. Navigate to each service directory
2. Use Gordon to generate Dockerfiles (or use existing)
3. Build images: `docker build -t todo-frontend:1.0.0 ./frontend`

### Deploy with Helm
1. Navigate to Helm chart directory
2. Install chart: `helm install todo-evolution ./todo-chart`
3. Verify deployment: `kubectl get pods,services`

### Access Application
1. Frontend: `minikube service frontend-service --url`
2. Backend: `minikube service backend-service --url`
3. Dashboard: `minikube dashboard`

### Troubleshooting
- Check pod status: `kubectl get pods`
- View logs: `kubectl logs <pod-name>`
- Describe pod: `kubectl describe pod <pod-name>`
```

**Specification Files Required**:
- `/specs/infrastructure/phase-iv-overview.md`: High-level architecture
- `/specs/infrastructure/containerization.md`: Dockerfile specifications
- `/specs/infrastructure/kubernetes-deployment.md`: K8s resource specs
- `/specs/infrastructure/helm-chart.md`: Helm values and structure

### XV. Success Metrics & Evaluation Criteria

**Phase IV Success = 250 Points**:

**Infrastructure Implementation (150 points)**:
- [ ] All three services containerized with multi-stage Dockerfiles (30 points)
- [ ] Non-root user security implemented (20 points)
- [ ] Helm chart created with proper structure (30 points)
- [ ] Deployed to Minikube successfully (30 points)
- [ ] Health probes configured and working (20 points)
- [ ] Resource limits/requests defined (20 points)

**AI Operations (50 points)**:
- [ ] Gordon used for Dockerfile generation (15 points)
- [ ] kubectl-ai used for manifest generation (15 points)
- [ ] kagent used for cluster management (10 points)
- [ ] AI-assisted debugging demonstrated (10 points)

**Documentation & Submission (50 points)**:
- [ ] Updated README with Minikube setup instructions (15 points)
- [ ] Infrastructure specs in `/specs/infrastructure/` (15 points)
- [ ] Demo video showing K8s deployment (15 points)
- [ ] Clear evidence of spec-driven approach (5 points)

### XVI. Timeline & Milestones (Dec 21 - Jan 4)

**Week 1 (Dec 21-27)**:
- **Dec 21-22**: Write infrastructure specifications, study Kubernetes basics
- **Dec 23-24**: Containerize services with Gordon, test locally
- **Dec 25-26**: Generate Helm charts with kubectl-ai, customize values
- **Dec 27**: Deploy to Minikube, troubleshoot issues

**Week 2 (Dec 28 - Jan 4)**:
- **Dec 28-29**: Implement health probes, resource limits
- **Dec 30-31**: Security hardening (non-root, secrets)
- **Jan 1-2**: Integration testing, debugging with kagent
- **Jan 3**: Documentation, demo video recording
- **Jan 4**: Phase IV submission deadline (11:59 PM)

### XVII. Non-Goals (Phase IV Scope)

**Explicitly Excluded**:
- ❌ Production cloud deployment (DigitalOcean DOKS) → Phase V
- ❌ Kafka/Dapr event-driven architecture → Phase V
- ❌ CI/CD pipelines (GitHub Actions) → Phase V
- ❌ Prometheus/Grafana monitoring → Phase V
- ❌ Horizontal Pod Autoscaling (HPA) → Phase V
- ❌ Persistent volumes (StatefulSets) → Acceptable but not required
- ❌ Ingress controllers (beyond basic Minikube ingress) → Phase V

**In-Scope but Optional**:
- ✅ Basic ingress for frontend access (nice-to-have)
- ✅ ConfigMaps for environment-specific config (recommended)
- ✅ Network policies (bonus points)
- ✅ Resource quotas (advanced, bonus points)

### XVIII. Emergency Protocols (Phase IV Specific)

**If Gordon Not Available**:
- Write Dockerfiles manually following multi-stage pattern
- Use existing Dockerfile templates from open-source projects
- Document in ADR: "Why manual Dockerfile creation was necessary"

**If kubectl-ai/kagent Not Working**:
- Generate Helm charts manually using `helm create` command
- Use Kubernetes official documentation for YAML structure
- Document in ADR: "Fallback to manual Helm chart creation"

**If Minikube Resource Issues**:
- Reduce replica counts (frontend: 1, backend: 1)
- Lower resource limits (CPU: 250m, Memory: 256Mi)
- Use `minikube start --cpus=2 --memory=4096` (minimum viable)

**If Deployment Fails**:
1. Check Minikube status: `minikube status`
2. Check pod events: `kubectl describe pod <pod-name>`
3. Check logs: `kubectl logs <pod-name>`
4. Use kubectl-ai: "Why is my deployment failing?"
5. Rollback: `helm rollback todo-evolution`

---

## Constitution Ratification

**Version**: 4.0.0  
**Ratified**: December 20, 2025  
**Scope**: Phase IV - Local Kubernetes Deployment (Hackathon II)  
**Deadline**: Sunday, January 4, 2026, 11:59 PM  
**Points**: 250 (base) + up to 200 (bonuses for Reusable Intelligence/Blueprints)

**Key Technologies**:
- Docker + Gordon (Container AI)
- Minikube (Local Kubernetes)
- Helm 3.x (Package Manager)
- kubectl-ai + kagent (AIOps)

**Deployment Target**: Local Minikube cluster (single-node)

**Next Phase Preview**: Phase V will extend this to DigitalOcean DOKS (cloud), add Kafka/Dapr for event-driven architecture, implement CI/CD, and add advanced monitoring.

---

*"From code to containers to clusters - the cloud-native journey."*  
— Phase IV Mantra