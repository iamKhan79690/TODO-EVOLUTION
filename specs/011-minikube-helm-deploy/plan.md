# Implementation Plan: Minikube Helm Deployment Update

**Branch**: `011-minikube-helm-deploy` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-minikube-helm-deploy/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy the TODO Evolution application (Phase III Todo Chatbot) to a local Minikube Kubernetes cluster using Helm charts. This involves updating existing Helm chart configurations, rebuilding Docker images with the latest application code, pointing the Docker daemon to Minikube, and deploying the complete application stack (frontend, backend, MCP server) as Kubernetes pods with proper service exposure.

**Technical Approach**:
1. Verify and start Minikube cluster with sufficient resources (4 CPUs, 8GB RAM)
2. Point Docker CLI to Minikube's internal Docker daemon
3. Build new Docker images for all three services with incremented version tags
4. Update Helm chart values.yaml with new image tags and latest configuration
5. Deploy application using Helm install/upgrade
6. Validate deployment and provide access URLs

## Technical Context

**Language/Version**: Node.js 20 (Frontend), Python 3.13 (Backend & MCP Server)
**Primary Dependencies**: Next.js 16.0.7, FastAPI 0.121.2, SQLModel 0.0.27, PostgreSQL 15+ (Neon cloud)
**Storage**: PostgreSQL cloud database (Neon) - connection via DATABASE_URL
**Testing**: Manual testing via browser and kubectl commands
**Target Platform**: Minikube (local single-node Kubernetes cluster)
**Project Type**: Web application (frontend + backend + MCP server microservices)
**Performance Goals**:
  - Frontend load time: <30 seconds
  - Backend API response: <5 seconds for health endpoint
  - All pods Running: within 10 minutes of deployment start
**Constraints**:
  - Local development environment only
  - Minikube resource limits: 4 CPUs, 8GB RAM (minimum viable)
  - No external container registry (images stored locally in Minikube Docker)
  - imagePullPolicy: Never (use local images)
**Scale/Scope**:
  - Frontend: 2 replicas (LoadBalancer service)
  - Backend: 2 replicas (NodePort service)
  - MCP Server: 1 replica (ClusterIP service)
  - Single-tenant deployment (development/testing)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase IV Constitution Compliance

**✅ I. Infrastructure as Code (IaC)**:
- All infrastructure changes will be documented in this plan and spec
- Existing Helm chart structure will be used and updated
- ADR will be created if any significant deviations from constitutional requirements

**✅ II. Containerization Standards**:
- Dockerfiles exist for all three services (frontend, backend, MCP server)
- Multi-stage builds implemented (Dependencies + Runtime stages)
- Non-root users configured (nextjs:1001, appuser:1000)
- Semantic versioning will be used for image tags (no `latest` tags)
- Base images: node:20-alpine, python:3.13-slim (official minimal images)

**✅ III. Kubernetes Architecture**:
- Minikube as local cluster (single-node)
- Helm 3.x for package management
- No AI tools (kubectl-ai, kagent, Gordon) available - will use standard CLI tools
- Deployment blueprint matches constitutional requirements (2+2+1 replicas)

**✅ IV. Helm Chart Structure**:
- Existing Helm chart in `helm-chart/` directory
- Chart.yaml, values.yaml, and templates/ structure already in place
- Will update values.yaml with new image tags and latest configuration
- Templates include deployments, services, secrets for all services

**✅ V. Security & Hardening**:
- Pod security contexts configured (runAsNonRoot: true, runAsUser: 1000/1001)
- Kubernetes Secrets for sensitive data (DATABASE_URL, JWT_SECRET, API keys)
- ServiceAccounts created for each deployment
- Resource limits and requests defined

**✅ VI. High Availability & Resilience**:
- Health probes configured (liveness and readiness for all services)
- Rolling update strategy: maxUnavailable: 1, maxSurge: 1
- Graceful shutdown with 60s terminationGracePeriodSeconds

**✅ VII. Observability**:
- Standard Kubernetes labels applied (app.kubernetes.io/*)
- Logging to stdout/stderr (collected by Kubernetes)
- Health endpoints available: /api/health (frontend), /health/ (backend), /health (MCP)

**✅ VIII. Configuration Management**:
- ConfigMaps not used (environment variables directly in values.yaml)
- Kubernetes Secrets for sensitive credentials
- Environment variable injection via secretRef

**✅ IX. Minikube Local Development**:
- Minikube start command: `minikube start --cpus=4 --memory=8192 --disk-size=20g`
- Docker environment: `eval $(minikube docker-env)` (WSL: `minikube docker-env | Invoke-Expression`)
- LoadBalancer service exposure via `minikube service <name>`

**⚠️ X. AI-Assisted Operations (DEVIATION)**:
- Gordon (Docker AI), kubectl-ai, and kagent NOT AVAILABLE on this system
- **Justification**: User confirmed to use only available tools and execute with what's installed
- **Fallback**: Use standard Docker CLI, kubectl, and Helm commands
- **ADR Required**: Yes - will document ADR for this deviation from constitutional requirements

**✅ XI. Deployment Workflow**:
- Specification stage: Complete (this plan + spec.md)
- Containerization stage: Dockerfiles exist, will rebuild images
- Helm chart stage: Existing chart will be updated
- Deployment stage: Helm install/upgrade commands
- Validation stage: Pod status checks, service access verification

**Constitutional Compliance Status**: ✅ PASS (with documented deviation for AI tools)

## Project Structure

### Documentation (this feature)

```text
specs/011-minikube-helm-deploy/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (N/A for this feature)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (N/A - no API contracts)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend + mcp_server)
frontend/
├── src/
│   ├── app/             # Next.js App Router pages
│   ├── components/      # React components
│   ├── lib/             # Utilities and API client
│   └── types/           # TypeScript types
├── Dockerfile           # Multi-stage build (exists)
└── package.json

backend/
├── src/
│   ├── api/             # FastAPI route handlers
│   ├── auth/            # JWT authentication
│   ├── core/            # Configuration
│   ├── dependencies/    # FastAPI dependencies
│   ├── models/          # SQLModel database models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── Dockerfile           # Multi-stage build (exists)
├── requirements.txt
└── requirements-container.txt

mcp_server/
├── tools/               # MCP tool implementations
├── services/            # Backend API client
├── config/              # Configuration
├── Dockerfile           # Multi-stage build (exists)
└── requirements.txt

helm-chart/              # Helm chart for Kubernetes deployment
├── Chart.yaml
├── values.yaml          # To be updated with new image tags
└── templates/
    ├── frontend/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── serviceaccount.yaml
    ├── backend/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── serviceaccount.yaml
    ├── mcp-server/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── serviceaccount.yaml
    └── secrets.yaml
```

**Structure Decision**: Web application option with three microservices (frontend, backend, MCP server). All Dockerfiles exist and follow constitutional requirements. Helm chart structure exists and will be updated.

## Complexity Tracking

> **Constitutional Deviation - AI Tools Unavailable**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Gordon (Docker AI) not available | AI Docker assistant not installed or not accessible in region | Constitution requires Gordon for containerization, but user confirmed to use available tools only |
| kubectl-ai not available | AI Kubernetes assistant not installed | Constitution requires kubectl-ai for manifest generation, but existing Helm chart will be used instead |
| kagent not available | AI cluster management not available | Constitution allows fallback to standard tools documented in emergency protocols |

**Mitigation**:
- Use standard Docker CLI commands for image builds
- Use existing Helm chart templates (no need for kubectl-ai generation)
- Use kubectl and Helm CLI for deployment and validation
- Document ADR explaining this deviation from constitutional requirements

**ADR to be created**: "ADR-011: Fallback to Standard CLI Tools for Minikube Deployment"

---

## Phase 0: Research & Analysis

### 0.1 Unknowns to Resolve

From Technical Context, the following clarifications are needed:

1. **Current Minikube State**: Is Minikube installed? What version? Current cluster status?
2. **Docker Environment**: Docker Desktop version? Is Docker daemon running?
3. **Helm Installation**: Is Helm 3.x installed? What version?
4. **kubectl Installation**: Is kubectl installed and configured?
5. **Current Image Versions**: What are the existing image tags in values.yaml? What should new versions be?
6. **Database Connectivity**: Is Neon PostgreSQL accessible from local cluster? Network/firewall considerations?
7. **Available System Resources**: Can system handle Minikube with 4 CPUs and 8GB RAM?

### 0.2 Research Tasks

**Task 1: Verify Tooling Availability**
- Check Minikube installation and version
- Check Docker Desktop status and version
- Check Helm installation and version
- Check kubectl installation and version
- Document all tool versions in research.md

**Task 2: Current Deployment State Analysis**
- Review existing Helm chart values.yaml
- Check current image tags and versioning scheme
- Review deployment templates for any issues
- Check secrets configuration
- Document current state and required updates

**Task 3: Minikube Resource Assessment**
- Check system resources (CPU, RAM, Disk)
- Verify Hyper-V/VMware are available (Windows WSL2 environment)
- Document Minikube driver recommendations (hyperkit, virtualbox, docker, etc.)
- Assess if system meets minimum requirements

**Task 4: Database Connectivity**
- Test Neon PostgreSQL connection string
- Verify network access from local machine
- Document any firewall/proxy considerations
- Confirm connection string format for asyncpg driver

### 0.3 Best Practices Research

**Research: Docker Image Versioning**
- Semantic versioning best practices (Major.Minor.Patch)
- Image tag conventions (avoid `latest`)
- Version increment strategy for this deployment

**Research: Minikube on Windows WSL2**
- Minikube driver recommendations for WSL2
- Docker daemon integration with Minikube
- Common issues and solutions for Windows environments

**Research: Helm Chart Updates**
- Helm values.yaml best practices
- Image update strategies (rolling updates)
- Secret management for local development

**Research: Service Exposure**
- LoadBalancer vs NodePort vs ClusterIP for Minikube
- Accessing LoadBalancer services on Windows
- Minikube tunnel considerations for LoadBalancer

### 0.4 Research Output

Consolidate all findings in `research.md` with the following structure:

```markdown
# Research: Minikube Helm Deployment Update

## Tooling Availability
[Document all installed tools with versions]

## Current Deployment State
[Document existing Helm chart state and required changes]

## System Resources
[Document system capabilities and Minikube configuration]

## Database Connectivity
[Document Neon database access and connection string]

## Best Practices
[Document researched best practices for image versioning, Helm updates, etc.]

## Decisions & Rationale
[Document all technical decisions with justification]
```

---

## Phase 1: Design & Contracts

### 1.1 Data Model

**N/A for this feature** - No new data models. Existing application data structures (users, tasks, conversations) remain unchanged.

### 1.2 API Contracts

**N/A for this feature** - No new API endpoints. Existing FastAPI endpoints remain unchanged:
- Authentication: POST /api/v1/auth/sign-up, /sign-in, /sign-out
- Tasks: GET/POST/PUT/DELETE /api/tasks
- Chat: POST /api/{user_id}/chat
- Health: GET /health/, /api/health

### 1.3 Configuration Design

**Image Versioning Strategy**:
- Current versions (from values.yaml):
  - Frontend: 1.0.4 → **1.0.5** (increment patch version)
  - Backend: 2.0.1 → **2.0.2** (increment patch version)
  - MCP Server: 1.0.1 → **1.0.2** (increment patch version)

**Docker Image Tags**:
- `todo-frontend:1.0.5`
- `todo-backend:2.0.2`
- `todo-mcp-server:1.0.2`

**Environment Variables Update**:
- Update CORS_ORIGINS in backend to include Minikube service URLs
- Update NEXT_PUBLIC_APP_URL in frontend to match Minikube LoadBalancer URL
- Verify all secret references (DATABASE_URL, JWT_SECRET, API keys) are correct

**Service Configuration**:
- Frontend: LoadBalancer on port 80 (targetPort 3000)
- Backend: NodePort on port 8000
- MCP Server: ClusterIP on port 8001

### 1.4 Quickstart Guide

Create `quickstart.md` with step-by-step deployment instructions:

```markdown
# Minikube Deployment Quickstart

## Prerequisites
- Minikube installed
- Docker Desktop running
- kubectl and Helm installed
- Neon PostgreSQL database accessible

## Deployment Steps

### 1. Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --disk-size=20g
```

### 2. Point Docker to Minikube
```bash
# Linux/macOS:
eval $(minikube docker-env)

# Windows PowerShell:
minikube docker-env | Invoke-Expression
```

### 3. Build Docker Images
```bash
# Frontend
docker build -t todo-frontend:1.0.5 ./frontend

# Backend
docker build -t todo-backend:2.0.2 ./backend

# MCP Server
docker build -t todo-mcp-server:1.0.2 ./mcp_server
```

### 4. Update Helm Chart
Edit `helm-chart/values.yaml` with new image tags

### 5. Deploy with Helm
```bash
# First time installation:
helm install todo-evolution ./helm-chart

# Upgrade existing release:
helm upgrade todo-evolution ./helm-chart
```

### 6. Verify Deployment
```bash
kubectl get pods
kubectl get services
```

### 7. Access Application
```bash
# Frontend URL:
minikube service todo-evolution-frontend --url

# Backend URL:
minikube service todo-evolution-backend --url
```

## Troubleshooting
[Common issues and solutions]
```

---

## Phase 2: Implementation Planning

*Note: This section is just a placeholder. The actual tasks.md will be generated by `/sp.tasks` command based on this plan.*

### High-Level Task Breakdown

1. **Infrastructure Setup** (FR-003)
   - Start Minikube cluster
   - Point Docker daemon to Minikube
   - Verify tooling (kubectl, Helm)

2. **Image Building** (FR-002, FR-006)
   - Build frontend image (todo-frontend:1.0.5)
   - Build backend image (todo-backend:2.0.2)
   - Build MCP server image (todo-mcp-server:1.0.2)
   - Verify images exist in Minikube Docker

3. **Helm Chart Updates** (FR-001, FR-004, FR-005)
   - Update image tags in values.yaml
   - Update secrets configuration
   - Validate Helm chart (helm lint)

4. **Deployment** (FR-006)
   - Install/upgrade Helm release
   - Monitor pod startup
   - Verify all pods Running

5. **Validation** (FR-007, FR-008)
   - Check pod status and logs
   - Test service connectivity
   - Provide access URLs

---

## Success Criteria Alignment

From spec.md Success Criteria:

- **SC-001**: All three services deploy successfully → Verified via `kubectl get pods`
- **SC-002**: Frontend loads within 30s → Tested via browser or curl
- **SC-003**: Backend health returns 200 OK → Tested via `minikube service` + curl
- **SC-004**: Environment variables injected → Verified via `kubectl exec env`
- **SC-005**: End-to-end workflow functional → Manual testing in browser
- **SC-006**: Semantic versioning used → Image tags: 1.0.5, 2.0.2, 1.0.2
- **SC-007**: Deployment within 10 minutes → Track deployment time

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Minikube fails to start | High | Medium | Check WSL2/Docker Desktop, try different driver (docker, virtualbox) |
| Insufficient system resources | High | Low | Close other apps, reduce Minikube CPUs/RAM if needed |
| Docker build failures | High | Low | Check Dockerfile syntax, verify dependencies, check logs |
| ImagePullBackOff errors | High | Medium | Verify images in Minikube Docker, check imagePullPolicy: Never |
| Database connection issues | High | Low | Test connection string, check firewall, verify asyncpg format |
| Port conflicts | Medium | Low | Check NodePort assignments, use different ports if needed |
| Helm install/upgrade fails | Medium | Low | Run helm lint first, check values.yaml syntax, review error logs |

---

## Next Steps

1. **Complete Phase 0**: Execute research tasks and create `research.md`
2. **Create ADR**: Document AI tools deviation (ADR-011)
3. **Update Agent Context**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
4. **Generate Tasks**: Run `/sp.tasks` to create detailed `tasks.md`
5. **Execute Implementation**: Follow tasks.md to deploy application

---

**Plan Status**: ✅ Complete (pending Phase 0 research execution)

**Constitutional Compliance**: ✅ PASS (with documented deviation)
