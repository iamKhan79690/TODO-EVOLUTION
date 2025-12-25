# Implementation Tasks: Phase IV - Kubernetes AI-Assisted Deployment

**Feature**: 1-phase-iv-kubernetes-aiops
**Branch**: `1-phase-iv-kubernetes-aiops`
**Generated**: 2025-12-23
**Total Tasks**: 97
**Estimated Duration**: 4 days (22 hours)

## Task Format Legend

- `- [ ] T###` - Task ID
- `[P]` - Parallelizable (can run with other P tasks)
- `[US#]` - User Story mapping (US1, US2, US3, US4)
- File paths included for precision

---

## Phase 1: Setup (Environment Prerequisites)

**Goal**: Install and configure all required AI tools and infrastructure components.

**Independent Test Criteria**:
- All tools installed and accessible from command line
- Minikube cluster running with Ready status
- Gordon responds to test command

### Environment Setup Tasks

- [ ] T001 Install Docker Desktop 4.53+ with Gordon beta feature enabled
- [ ] T002 Verify Gordon availability by running `docker ai "What can you do?"` - expect capabilities response
- [ ] T003 Stop existing kind cluster if present: `kind delete cluster --name todo-cluster`
- [ ] T004 Install Minikube v1.37.0+ for platform (Windows/macOS/Linux)
- [ ] T005 Start Minikube cluster: `minikube start --cpus=4 --memory=8192 --driver=docker`
- [ ] T006 Verify Minikube status: `kubectl get nodes` - expect Ready status
- [ ] T007 Enable Minikube ingress addon: `minikube addons enable ingress`
- [ ] T008 Enable Minikube metrics-server addon: `minikube addons enable metrics-server`
- [ ] T009 Install kubectl-ai CLI tool per official documentation
- [ ] T010 Verify kubectl-ai: `kubectl-ai "show cluster status"` - expect cluster info
- [ ] T011 Install kagent CLI tool per official documentation
- [ ] T012 Verify kagent: `kagent "analyze cluster health"` - expect health report
- [ ] T013 Install Helm CLI v3.15.0+ for platform
- [ ] T014 Verify Helm version: `helm version` - expect v3.15.0+

**Phase 1 Output**: Ready development environment with all AI tools functional

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Create kubernetes directory structure and verify source code readiness.

**Independent Test Criteria**:
- Directories created and empty
- Source code exists for all three services

### Foundation Tasks

- [ ] T015 Create kubernetes directory: `mkdir -p /mnt/d/Hackathon/TODO-Evolution/kubernetes`
- [ ] T016 Verify frontend source exists: `ls /mnt/d/Hackathon/TODO-Evolution/frontend/package.json`
- [ ] T017 Verify backend source exists: `ls /mnt/d/Hackathon/TODO-Evolution/backend/requirements.txt`
- [ ] T018 Verify MCP server source exists: `ls /mnt/d/Hackathon/TODO-Evolution/mcp_server/requirements.txt`
- [ ] T019 Create helm-chart directory: `mkdir -p /mnt/d/Hackathon/TODO-Evolution/helm-chart/{templates,charts}`
- [ ] T020 Verify OpenAI API key is available (check environment or .env file)

**Phase 2 Output**: Ready project structure for containerization

---

## Phase 3: User Story 4 - Local Development Environment Setup (Priority: P1)

**Story Goal**: Set up a complete local Kubernetes environment with Minikube so that I can develop and test the application in a production-like environment locally.

**Why First**: This story enables all other AI-assisted operations. Without proper tool setup, Gordon, kubectl-ai, and kagent cannot be utilized.

**Acceptance Criteria**:
- Gordon available via `docker ai` command
- Minikube cluster running with 4 CPUs and 8GB RAM
- kubectl-ai and kagent functional and can query the cluster
- All required addons (ingress, metrics-server) active

**Independent Test**: Run `minikube status` and verify all components show "Running" or "Enabled"

**Note**: This story is completed in Phase 1 (tasks T001-T014). Proceed to User Story 1.

---

## Phase 4: User Story 1 - AI-Assisted Containerization (Priority: P1)

**Story Goal**: Use Gordon (Docker AI) to containerize the frontend and backend applications so that I can generate optimized container images without manually writing Dockerfiles.

**Why Priority**: Containerization is the foundation for Kubernetes deployment. Using Gordon accelerates this process and ensures best practices.

**Acceptance Criteria**:
- Gordon generates Dockerfiles for all 3 services without manual editing
- All images run as non-root user (UID 1000)
- All images include health check endpoints
- All images build successfully and can run locally

**Independent Test**: Run each container independently with `docker run` and verify health endpoints respond

### Frontend Container Tasks

- [ ] T021 [US1] Use Gordon to generate frontend Dockerfile: `cd frontend && docker ai "Create a production-ready multi-stage Dockerfile for Next.js 16 with standalone output, non-root user (UID 1000), health checks, and read-only root filesystem. Use node:18-alpine as base image."` - output to `frontend/Dockerfile`
- [ ] T022 [US1] Review generated `frontend/Dockerfile` for multi-stage build, non-root user UID 1000, health check, read-only root filesystem
- [ ] T023 [US1] Build frontend image: `docker build -t todo-frontend:1.0.0 .` from `frontend/` directory
- [ ] T024 [US1] Run frontend container test: `docker run --rm -p 3000:3000 todo-frontend:1.0.0`
- [ ] T025 [US1] Verify frontend health endpoint responds: `curl http://localhost:3000/api/health`
- [ ] T026 [US1] Stop frontend test container

### Backend Container Tasks

- [ ] T027 [P] [US1] Use Gordon to generate backend Dockerfile: `cd backend && docker ai "Create a production Dockerfile for FastAPI backend with Python 3.13-slim, non-root user (UID 1000), uvicorn server, health check endpoint /health/, and all dependencies from requirements-container.txt including redis, structlog, asyncpg, and fastapi."` - output to `backend/Dockerfile`
- [ ] T028 [P] [US1] Review generated `backend/Dockerfile` for Python 3.13 base, non-root user UID 1000, health check /health/, all dependencies
- [ ] T029 [P] [US1] Build backend image: `docker build -t todo-backend:1.0.0 .` from `backend/` directory
- [ ] T030 [P] [US1] Run backend container test: `docker run --rm -p 8000:8000 todo-backend:1.0.0`
- [ ] T031 [P] [US1] Verify backend health endpoint responds: `curl http://localhost:8000/health/`
- [ ] T032 [P] [US1] Stop backend test container

### MCP Server Container Tasks

- [ ] T033 [P] [US1] Use Gordon to generate MCP server Dockerfile: `cd mcp_server && docker ai "Create a production Dockerfile for Python MCP server with FastAPI, structlog, asyncpg, pydantic, uvicorn, health check /health/, non-root user UID 1000."` - output to `mcp_server/Dockerfile`
- [ ] T034 [P] [US1] Review generated `mcp_server/Dockerfile` for Python base, non-root user UID 1000, health check /health/
- [ ] T035 [P] [US1] Build MCP server image: `docker build -t todo-mcp-server:1.0.0 .` from `mcp_server/` directory
- [ ] T036 [P] [US1] Run MCP server container test: `docker run --rm -p 8001:8001 todo-mcp-server:1.0.0`
- [ ] T037 [P] [US1] Verify MCP server health endpoint responds: `curl http://localhost:8001/health/`
- [ ] T038 [P] [US1] Stop MCP server test container

### Image Loading Tasks

- [ ] T039 [US1] Point Docker CLI to Minikube: `eval $(minikube docker-env)`
- [ ] T040 [US1] Load frontend image into Minikube: `minikube image load todo-frontend:1.0.0`
- [ ] T041 [P] [US1] Load backend image into Minikube: `minikube image load todo-backend:1.0.0`
- [ ] T042 [P] [US1] Load MCP server image into Minikube: `minikube image load todo-mcp-server:1.0.0`
- [ ] T043 [US1] Verify images in Minikube: `docker images | grep todo-`

**Phase 4 Output**: 3 container images built, tested, and loaded into Minikube

---

## Phase 5: User Story 2 - AI-Generated Kubernetes Manifests (Priority: P1)

**Story Goal**: Use kubectl-ai to generate deployment manifests and Helm charts so that I can deploy the application without manually writing YAML files.

**Why Priority**: Kubernetes manifest generation is complex and error-prone. AI assistance ensures best practices and reduces configuration errors.

**Acceptance Criteria**:
- kubectl-ai generates valid deployment YAML for all 3 services
- kubectl-ai generates complete Helm chart structure
- All YAML passes kubectl dry-run validation
- Helm chart passes helm lint validation

**Independent Test**: Run `kubectl apply --dry-run=client -f <yaml>` and `helm lint` - expect no errors

### Frontend Manifest Tasks

- [ ] T044 [US2] Use kubectl-ai to generate frontend deployment: `kubectl-ai "Create a Kubernetes deployment for Next.js frontend with 2 replicas, LoadBalancer service on port 80, target port 3000, liveness probe GET /api/health with initialDelaySeconds=30, periodSeconds=10, readiness probe GET /api/ready, resource limits 500m CPU, 512Mi memory, requests 100m CPU, 128Mi memory, non-root user UID 1000, security context with readOnlyRootFilesystem=true."` - output to `kubernetes/frontend-deployment.yaml`
- [ ] T045 [US2] Validate frontend YAML: `kubectl apply --dry-run=client -f kubernetes/frontend-deployment.yaml`

### Backend Manifest Tasks

- [ ] T046 [P] [US2] Use kubectl-ai to generate backend deployment: `kubectl-ai "Create a Kubernetes deployment for FastAPI backend with 2 replicas, ClusterIP service on port 8000, liveness probe GET /health/ with initialDelaySeconds=15, readiness probe GET /health/, resource limits 500m CPU, 512Mi memory, requests 100m CPU, 128Mi memory, non-root user UID 1000, environment variables for DATABASE_URL, JWT_SECRET, OPENAI_API_KEY from Kubernetes secret named 'todo-secrets', security context with drop ALL capabilities."` - output to `kubernetes/backend-deployment.yaml`
- [ ] T047 [P] [US2] Validate backend YAML: `kubectl apply --dry-run=client -f kubernetes/backend-deployment.yaml`

### MCP Server Manifest Tasks

- [ ] T048 [P] [US2] Use kubectl-ai to generate MCP deployment: `kubectl-ai "Create a Kubernetes deployment for MCP server with 1 replica, ClusterIP service on port 8001, liveness probe GET /health/ with initialDelaySeconds=15, readiness probe GET /health/, resource limits 500m CPU, 512Mi memory, requests 100m CPU, 128Mi memory, non-root user UID 1000, environment variables for BACKEND_URL and OPENAI_API_KEY from secret 'todo-secrets', security context with allowPrivilegeEscalation=false."` - output to `kubernetes/mcp-deployment.yaml`
- [ ] T049 [P] [US2] Validate MCP YAML: `kubectl apply --dry-run=client -f kubernetes/mcp-deployment.yaml`

### Helm Chart Generation Tasks

- [ ] T050 [US2] Use kubectl-ai to generate complete Helm chart: `kubectl-ai "Generate a complete Helm chart for the TODO Evolution application with frontend (Next.js), backend (FastAPI), and MCP server (Python). Include values.yaml for configurable replica counts, image tags, resource limits, and environment variables. Create templates for deployments, services, configmaps, and secrets. The chart should be production-ready with proper labels (app: todo-evolution, component, version, managed-by: helm), annotations, and security contexts. Include a NOTES.txt with deployment instructions."` - output to `helm-chart/`
- [ ] T051 [US2] Run helm lint validation: `helm lint helm-chart/` - expect 0 errors, 0 warnings
- [ ] T052 [US2] Review and update `helm-chart/values.yaml` with proper defaults for replicas, image tags, resource limits, environment variables
- [ ] T053 [US2] Review generated templates in `helm-chart/templates/` for proper labels, annotations, security contexts
- [ ] T054 [US2] Add `_helpers.tpl` to `helm-chart/templates/` with standard label definitions (app, component, version, managed-by)

**Phase 5 Output**: Complete Helm chart with validated templates

---

## Phase 6: User Story 3 - AI-Assisted Deployment and Troubleshooting (Priority: P2)

**Story Goal**: Use kagent to deploy, monitor, and troubleshoot the application so that I can quickly identify and resolve issues without manually analyzing logs and metrics.

**Why Priority**: Operations and monitoring are critical for production readiness. AI-assisted analysis reduces mean time to resolution (MTTR).

**Acceptance Criteria**:
- Application deploys successfully with all pods becoming ready
- kubectl-ai can troubleshoot failing pods and provide remediation
- kagent provides cluster health analysis with recommendations
- Scaling operations work via kubectl-ai

**Independent Test**: Run `kagent "analyze cluster health"` and verify report contains CPU/memory usage and recommendations

### Secret Creation Tasks

- [ ] T055 [US3] Create Kubernetes secret for database: `kubectl create secret generic todo-secrets --from-literal=DATABASE_URL="postgresql+asyncpg://todo_user:your-password@your-postgres-host:5432/todo"`
- [ ] T056 [P] [US3] Add JWT secret: `kubectl patch secret todo-secrets --from-literal=JWT_SECRET="your-jwt-secret-min-32-chars"`
- [ ] T057 [P] [US3] Add OpenAI API key: `kubectl patch secret todo-secrets --from-literal=OPENAI_API_KEY="sk-your-openai-api-key"`
- [ ] T058 [US3] Verify secret created: `kubectl get secret todo-secrets -o yaml`

### PostgreSQL Deployment Tasks

- [ ] T059 [US3] Add bitnami Helm repo: `helm repo add bitnami https://charts.bitnami.com/bitnami`
- [ ] T060 [US3] Update Helm repos: `helm repo update`
- [ ] T061 [US3] Deploy PostgreSQL via Helm: `helm install postgres bitnami/postgresql --set auth.database=todo --set auth.password=todo123 --set auth.user=todo_user`
- [ ] T062 [US3] Wait for PostgreSQL pod ready: `kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql --timeout=300s`
- [ ] T063 [US3] Update todo-secrets with Neon/PostgreSQL connection string if using external database

### Application Deployment Tasks

- [ ] T064 [US3] Use kubectl-ai to deploy Helm chart: `kubectl-ai "Deploy the todo-evolution Helm chart from ./helm-chart/ with release name 'todo-evolution' and namespace 'default'. Monitor the deployment and wait for all pods to be ready. If any pods fail, diagnose using logs and events, then provide remediation steps."`
- [ ] T065 [US3] Or deploy with Helm directly: `helm install todo-evolution ./helm-chart/ --values ./helm-chart/values.yaml`
- [ ] T066 [US3] Monitor deployment progress: `kubectl get pods -w`
- [ ] T067 [US3] Wait for frontend deployment ready: `kubectl rollout status deployment/todo-evolution-frontend`
- [ ] T068 [P] [US3] Wait for backend deployment ready: `kubectl rollout status deployment/todo-evolution-backend`
- [ ] T069 [P] [US3] Wait for MCP deployment ready: `kubectl rollout status deployment/todo-evolution-mcp-server`
- [ ] T070 [US3] Verify all 5 pods Running and Ready: `kubectl get pods` - expect 2 frontend, 2 backend, 1 MCP, 1 postgres

### Validation Tasks

- [ ] T071 [US3] Get frontend service URL: `minikube service todo-evolution-frontend --url`
- [ ] T072 [US3] Open frontend URL in browser and verify application loads
- [ ] T073 [P] [US3] Verify frontend health endpoint: `curl http://$(minikube service todo-evolution-frontend --url)/api/health`
- [ ] T074 [P] [US3] Verify backend health endpoint: `kubectl exec -it deployment/todo-evolution-backend -- curl http://localhost:8000/health/`
- [ ] T075 [P] [US3] Verify MCP health endpoint: `kubectl exec -it deployment/todo-evolution-mcp-server -- curl http://localhost:8001/health/`

### Troubleshooting and Operations Tasks

- [ ] T076 [US3] If any pods failing, use kubectl-ai: `kubectl-ai "Check why the backend pods are crashing and suggest fixes based on logs and events"`
- [ ] T077 [US3] If connectivity issues, use kubectl-ai: `kubectl-ai "Verify service endpoints and troubleshoot connectivity issues between frontend and backend"`
- [ ] T078 [US3] Use kagent for cluster analysis: `kagent "Analyze the cluster health, resource utilization, and provide optimization recommendations. Include CPU usage, memory usage, pod health, and scaling recommendations."` - output to `cluster-analysis-report.md`
- [ ] T079 [US3] Review cluster-analysis-report.md for recommendations

### Scaling Operations Tasks

- [ ] T080 [US3] Use kubectl-ai to scale backend: `kubectl-ai "Scale the backend deployment to 3 replicas to handle increased load. Verify the new replicas are healthy and properly registered with the service."`
- [ ] T081 [US3] Verify scaled replicas: `kubectl get pods -l app=todo-evolution,component=backend` - expect 3 pods
- [ ] T082 [US3] Scale backend back to 2 replicas: `kubectl-ai "Scale the backend deployment back to 2 replicas during low traffic period. Verify the excess replicas are terminated gracefully."`
- [ ] T083 [US3] Verify scale down: `kubectl get pods -l app=todo-evolution,component=backend` - expect 2 pods

**Phase 6 Output**: Fully deployed application on Minikube with all pods Running and Ready

---

## Phase 7: Polish & Documentation

**Goal**: Create completion documentation and validate constitutional compliance.

**Acceptance Criteria**:
- Completion report created with all AI tool commands
- Fallback procedures documented
- Constitutional compliance validated
- 80%+ AI tool usage documented

### Documentation Tasks

- [ ] T084 Create completion report: `phase-iv-completion-report.md` documenting all AI tool commands, image sizes, deployment times, and validation results
- [ ] T085 Calculate AI tool usage metrics: Count Gordon commands, kubectl-ai commands, kagent commands vs total operations - aim for 80%+
- [ ] T086 [P] Create fallback procedures document: `phase-iv-fallback-procedures.md` with procedures for when Gordon, kubectl-ai, or kagent are unavailable
- [ ] T087 [P] Document deviation report if any manual steps were required (kind instead of Minikube, manual Docker instead of Gordon, etc.)

### Constitutional Compliance Validation

- [ ] T088 Verify all containers run as non-root user: `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].securityContext.runAsUser}{"\n"}{end}'` - expect 1000 for all
- [ ] T089 [P] Verify all pods have resource limits: `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].resources.limits}{"\n"}{end}'` - expect CPU and memory for all
- [ ] T090 [P] Verify all pods have liveness probes: `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].livenessProbe}{"\n"}{end}'` - expect probes for all
- [ ] T091 [P] Verify all pods have readiness probes: `kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].readinessProbe}{"\n"}{end}'` - expect probes for all
- [ ] T092 [P] Verify all secrets in Kubernetes Secrets (not plain text): `kubectl get secrets -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'` - expect todo-secrets present
- [ ] T093 [P] Verify standard Kubernetes labels: `kubectl get all -o jsonpath='{range .items[*]}{.kind}/{"\t"}{.metadata.name}{"\t"}{.metadata.labels}{"\n"}{end}'` - expect app, component, version, managed-by labels

### Final Validation

- [ ] T094 Run validation checklist from `specs/1-phase-iv-kubernetes-aiops/checklists/requirements.md`
- [ ] T095 Verify success criteria SC-001 through SC-010 from spec.md
- [ ] T096 Update completion report with validation results
- [ ] T097 Create PHR for task generation completion

**Phase 7 Output**: Complete documentation package with validated constitutional compliance

---

## Dependencies

### User Story Dependencies

```
US4 (Environment Setup)
  ├─→ Must complete first (blocks all other stories)
  │
US1 (Containerization)
  ├─→ Depends on US4 (needs tools installed)
  │
US2 (Manifest Generation)
  ├─→ Depends on US1 (needs container images)
  │
US3 (Deployment & Operations)
  ├─→ Depends on US2 (needs Helm charts)
  └─→ Depends on US1 (needs images loaded in Minikube)
```

**Execution Order**: US4 → US1 → US2 → US3

### Parallel Execution Opportunities

**Within US1 (Containerization)**:
- Tasks T027-T032 (Backend container) can run in parallel with T033-T038 (MCP container)

**Within US2 (Manifest Generation)**:
- Tasks T046-T047 (Backend manifest) can run in parallel with T048-T049 (MCP manifest)

**Within US3 (Deployment)**:
- Tasks T073-T075 (Health checks) can run in parallel

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Phase 1 MVP**: Deploy application to Minikube with AI tools

Include:
- US4: Environment Setup (complete)
- US1: Containerization (complete)
- US2: Manifest Generation (complete)
- US3: Deployment (basic deployment, no scaling operations)

**Estimated Time**: 2-3 days

### Full Scope

Include all phases with scaling, optimization, and complete documentation.

**Estimated Time**: 4 days (22 hours)

### Incremental Delivery

1. **Increment 1**: Environment setup + containerization (T001-T043)
2. **Increment 2**: Manifest generation (T044-T054)
3. **Increment 3**: Deployment (T055-T075)
4. **Increment 4**: Operations and scaling (T076-T083)
5. **Increment 5**: Documentation and validation (T084-T097)

---

## Task Summary

| Phase | Tasks | Story | Estimated Time |
|-------|-------|-------|----------------|
| Phase 1: Setup | T001-T014 | US4 | 2 hours |
| Phase 2: Foundational | T015-T020 | - | 30 minutes |
| Phase 3: US4 | - | US4 | Complete (Phase 1) |
| Phase 4: US1 | T021-T043 | US1 | 6 hours |
| Phase 5: US2 | T044-T054 | US2 | 6 hours |
| Phase 6: US3 | T055-T083 | US3 | 6 hours |
| Phase 7: Polish | T084-T097 | - | 2.5 hours |
| **Total** | **97 tasks** | **4 stories** | **22 hours** |

---

## Format Validation

✅ All tasks follow checklist format: `- [ ] T### [P] [US#] Description with file path`
✅ Task IDs sequential and unique
✅ Parallelizable tasks marked with `[P]`
✅ User story tasks marked with `[US#]`
✅ File paths included where applicable
✅ Independent test criteria for each phase
✅ Dependencies documented

---

## Next Steps

1. **Start Phase 1**: Execute environment setup tasks (T001-T014)
2. **Validate each increment**: Ensure acceptance criteria met before proceeding
3. **Document AI interactions**: Record all Gordon, kubectl-ai, kagent commands for completion report
4. **Create PHRs**: Generate prompt history records after major milestones

---

**Tasks Status**: ✅ READY FOR EXECUTION
**Total Tasks**: 97
**Parallel Opportunities**: 15 tasks marked as parallelizable
**Estimated Duration**: 4 days (22 hours)
