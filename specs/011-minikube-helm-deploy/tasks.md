# Tasks: Minikube Helm Deployment Update

**Input**: Design documents from `/specs/011-minikube-helm-deploy/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, quickstart.md ✅

**Tests**: Manual testing via kubectl and browser (no automated test tasks required)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a deployment/infrastructure feature with three microservices:
- Frontend: `frontend/` (Next.js)
- Backend: `backend/` (FastAPI)
- MCP Server: `mcp_server/` (Python)
- Helm Chart: `helm-chart/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify and prepare deployment environment

- [ ] T001 Verify Minikube installation and check version
- [ ] T002 Verify Docker Desktop is running and check version
- [ ] T003 Verify kubectl installation and check version
- [ ] T004 Verify Helm installation and check version
- [ ] T005 Check system resources (CPU, RAM, Disk) meet minimum requirements (4 CPUs, 8GB RAM, 20GB disk)
- [ ] T006 Verify Neon PostgreSQL database connection string is accessible
- [ ] T007 Document tool versions in deployment notes

**Checkpoint**: Deployment environment verified and ready

---

## Phase 2: Foundational (Infrastructure Setup)

**Purpose**: Core infrastructure that MUST be complete before ANY deployment steps

**⚠️ CRITICAL**: No image building or deployment can begin until this phase is complete

- [ ] T008 Start Minikube cluster with Docker driver: `minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker`
- [ ] T009 Enable Minikube addons: `minikube addons enable ingress metrics-server`
- [ ] T010 Verify Minikube status: `minikube status` (all components should be Running)
- [ ] T011 Point Docker CLI to Minikube daemon (PowerShell): `minikube docker-env | Invoke-Expression`
- [ ] T012 Verify Docker environment is correctly pointing to Minikube: `docker ps`
- [ ] T013 Check existing Helm chart structure in helm-chart/
- [ ] T014 Review current image tags in helm-chart/values.yaml (document existing versions)

**Checkpoint**: Minikube running, Docker daemon configured, Helm chart ready for updates

---

## Phase 3: User Story 1 - Deploy Updated Application to Minikube (Priority: P1) 🎯 MVP

**Goal**: Deploy the complete TODO Evolution application stack (frontend, backend, MCP server) to Minikube with updated Helm charts and Docker images

**Independent Test**: Can be verified by (1) all pods in Running state via `kubectl get pods`, (2) frontend accessible via `minikube service todo-evolution-frontend --url`, (3) backend health check returns 200 OK, (4) MCP server accessible from backend pod

### Manual Testing for User Story 1

> **NOTE**: These are manual verification steps to perform after deployment

- [ ] T015 [US1] Manual Test: Verify all pods are Running - `kubectl get pods` should show 5/5 pods (2 frontend + 2 backend + 1 MCP server)
- [ ] T016 [US1] Manual Test: Verify all services are created - `kubectl get services` should show frontend, backend, and MCP server services
- [ ] T017 [US1] Manual Test: Access frontend LoadBalancer - `minikube service todo-evolution-frontend --url` and open in browser
- [ ] T018 [US1] Manual Test: Test backend health endpoint - `curl http://$(minikube service todo-evolution-backend --url)/health/` should return 200 OK
- [ ] T019 [US1] Manual Test: Verify MCP server connectivity from backend - `kubectl exec -it deployment/todo-evolution-backend -- curl http://todo-evolution-mcp-server:8001/health`

### Implementation for User Story 1

- [ ] T020 [P] [US1] Build frontend Docker image with version 1.0.5: `docker build -t todo-frontend:1.0.5 ./frontend`
- [ ] T021 [P] [US1] Build backend Docker image with version 2.0.2: `docker build -t todo-backend:2.0.2 ./backend`
- [ ] T022 [P] [US1] Build MCP server Docker image with version 1.0.2: `docker build -t todo-mcp-server:1.0.2 ./mcp_server`
- [ ] T023 [US1] Verify all three images exist in Minikube Docker: `docker images | grep todo`
- [ ] T024 [US1] Update frontend image tag in helm-chart/values.yaml from 1.0.4 to 1.0.5
- [ ] T025 [US1] Update backend image tag in helm-chart/values.yaml from 2.0.1 to 2.0.2
- [ ] T026 [US1] Update MCP server image tag in helm-chart/values.yaml from 1.0.1 to 1.0.2
- [ ] T027 [US1] Verify secrets configuration in helm-chart/values.yaml (DATABASE_URL, JWT_SECRET, API keys)
- [ ] T028 [US1] Validate Helm chart syntax: `helm lint ./helm-chart`
- [ ] T029 [US1] Deploy application with Helm (first time or upgrade): `helm install todo-evolution ./helm-chart` or `helm upgrade todo-evolution ./helm-chart`
- [ ] T030 [US1] Monitor pod startup: `kubectl get pods -w` (wait for all pods to reach Running state, ~2-5 minutes)
- [ ] T031 [US1] Verify no pods in Error/CrashLoopBackOff state: `kubectl get pods`
- [ ] T032 [US1] Check pod logs for any errors: `kubectl logs -l app=todo-evolution --all-containers=true`
- [ ] T033 [US1] Get frontend service URL: `minikube service todo-evolution-frontend --url`
- [ ] T034 [US1] Get backend service URL: `minikube service todo-evolution-backend --url`
- [ ] T035 [US1] Document deployment URLs in deployment notes

**Checkpoint**: At this point, User Story 1 (P1 MVP) should be fully functional - complete application deployed and accessible

---

## Phase 4: User Story 2 - Update Helm Configuration for Latest Application State (Priority: P2)

**Goal**: Ensure Helm chart configurations reflect the latest application requirements with proper environment variables, service URLs, and resource limits

**Independent Test**: Can be verified by (1) checking all environment variables are present in pods via `kubectl exec`, (2) verifying service discovery URLs work, (3) confirming resource limits are appropriate

### Manual Testing for User Story 2

- [ ] T036 [US2] Manual Test: Verify frontend environment variables - `kubectl exec -it deployment/todo-evolution-frontend -- env | grep NEXT_PUBLIC`
- [ ] T037 [US2] Manual Test: Verify backend environment variables - `kubectl exec -it deployment/todo-evolution-backend -- env | grep DATABASE_URL`
- [ ] T038 [US2] Manual Test: Verify backend CORS_ORIGINS includes Minikube service URLs - check backend pod environment
- [ ] T039 [US2] Manual Test: Verify resource limits are applied - `kubectl describe pod <frontend-pod> | grep -A 5 Limits`
- [ ] T040 [US2] Manual Test: Test frontend-to-backend connectivity - `kubectl exec -it deployment/todo-evolution-frontend -- curl http://todo-evolution-backend:8000/health/`

### Implementation for User Story 2

- [ ] T041 [P] [US2] Review and update CORS_ORIGINS in helm-chart/values.yaml backend section to include Minikube LoadBalancer URLs
- [ ] T042 [P] [US2] Review and update NEXT_PUBLIC_APP_URL in helm-chart/values.yaml frontend section to match Minikube LoadBalancer
- [ ] T043 [P] [US2] Verify DATABASE_URL format includes asyncpg driver and ssl=require in helm-chart/values.yaml secrets section
- [ ] T044 [P] [US2] Verify JWT_SECRET is at least 32 characters in helm-chart/values.yaml secrets section
- [ ] T045 [P] [US2] Verify resource requests and limits in helm-chart/values.yaml (CPU: 100m-500m, Memory: 128Mi-512Mi)
- [ ] T046 [US2] Update Helm chart if configuration changes were made: `helm upgrade todo-evolution ./helm-chart`
- [ ] T047 [US2] Verify rolling update completed successfully: `kubectl rollout status deployment/todo-evolution-frontend`
- [ ] T048 [US2] Verify rolling update completed successfully: `kubectl rollout status deployment/todo-evolution-backend`
- [ ] T049 [US2] Verify rolling update completed successfully: `kubectl rollout status deployment/todo-evolution-mcp-server`
- [ ] T050 [US2] Confirm all pods restarted with new configuration: `kubectl get pods -o wide`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - application deployed with correct configuration

---

## Phase 5: User Story 3 - Rebuild and Update Docker Images (Priority: P3)

**Goal**: Rebuild Docker images with latest application code and configuration changes to ensure deployed pods run the most recent version

**Independent Test**: Can be verified by (1) confirming new image tags exist, (2) verifying pods use new images, (3) testing new features are working

### Manual Testing for User Story 3

- [ ] T051 [US3] Manual Test: Verify images are using correct tags - `kubectl get deployment todo-evolution-frontend -o jsonpath='{.spec.template.spec.containers[0].image}'`
- [ ] T052 [US3] Manual Test: Verify images are using correct tags - `kubectl get deployment todo-evolution-backend -o jsonpath='{.spec.template.spec.containers[0].image}'`
- [ ] T053 [US3] Manual Test: Verify images are using correct tags - `kubectl get deployment todo-evolution-mcp-server -o jsonpath='{.spec.template.spec.containers[0].image}'`
- [ ] T054 [US3] Manual Test: Verify new application features are working in deployed frontend (check for latest code changes)
- [ ] T055 [US3] Manual Test: Verify new application features are working in deployed backend (check for latest API changes)

### Implementation for User Story 3

> **NOTE**: This user story is about ensuring image rebuilds work correctly. If T020-T022 in Phase 3 already built images correctly, these tasks validate that process.

- [ ] T056 [P] [US3] Review frontend Dockerfile for any needed updates: `frontend/Dockerfile`
- [ ] T057 [P] [US3] Review backend Dockerfile for any needed updates: `backend/Dockerfile`
- [ ] T058 [P] [US3] Review MCP server Dockerfile for any needed updates: `mcp_server/Dockerfile`
- [ ] T059 [US3] If Dockerfiles were modified, rebuild frontend image: `docker build -t todo-frontend:1.0.5 ./frontend`
- [ ] T060 [US3] If Dockerfiles were modified, rebuild backend image: `docker build -t todo-backend:2.0.2 ./backend`
- [ ] T061 [US3] If Dockerfiles were modified, rebuild MCP server image: `docker build -t todo-mcp-server:1.0.2 ./mcp_server`
- [ ] T062 [US3] If images were rebuilt, update Helm deployment: `helm upgrade todo-evolution ./helm-chart`
- [ ] T063 [US3] Monitor rolling update: `kubectl rollout status deployment/todo-evolution-frontend`
- [ ] T064 [US3] Monitor rolling update: `kubectl rollout status deployment/todo-evolution-backend`
- [ ] T065 [US3] Monitor rolling update: `kubectl rollout status deployment/todo-evolution-mcp-server`
- [ ] T066 [US3] Verify old pods terminated and new pods are running: `kubectl get pods`

**Checkpoint**: All user stories should now be independently functional - images rebuilt with latest code and deployed

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and cleanup

- [ ] T067 [P] Run comprehensive end-to-end test: Sign up → Create task → View task → Mark complete (via browser)
- [ ] T068 [P] Verify all success criteria from spec.md (SC-001 through SC-007)
- [ ] T069 [P] Check pod resource usage: `kubectl top pods`
- [ ] T070 [P] Review pod logs for any warnings or errors: `kubectl logs -l app=todo-evolution --tail=50`
- [ ] T071 [P] Document deployment URLs and access credentials in deployment report
- [ ] T072 [P] Create deployment summary with pod status, service URLs, and any issues encountered
- [ ] T073 [P] Update README.md with Minikube deployment instructions if not already present
- [ ] T074 [P] Test Minikube tunnel for LoadBalancer access (optional): Run `minikube tunnel` in separate terminal
- [ ] T075 [P] Verify Kubernetes dashboard access: `minikube dashboard`
- [ ] T076 [P] Clean up any failed or orphaned resources: `kubectl delete pod --field-selector=status.phase.failed`
- [ ] T077 Create final deployment validation report

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3 - P1 MVP)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4 - P2)**: Depends on User Story 1 completion (reuses deployed application)
- **User Story 3 (Phase 5 - P3)**: Depends on User Story 1 completion (validates image rebuild process)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Deploy Application)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2 - Update Configuration)**: Depends on User Story 1 - updates configuration of already-deployed application
- **User Story 3 (P3 - Rebuild Images)**: Depends on User Story 1 - validates and rebuilds images for deployed application

### Within Each User Story

- Manual tests should be performed after implementation tasks
- Image builds (T020-T022 in US1) can run in parallel
- Image tag updates (T024-T026 in US1) are sequential (same file)
- Configuration reviews (T041-T045 in US2) can run in parallel (different sections)
- Rolling updates (T047-T049 in US2) can run in parallel (different deployments)

### Parallel Opportunities

- **Phase 1**: All verification tasks (T001-T006) can run in parallel
- **Phase 3**: Image builds (T020-T022) can run in parallel (different services)
- **Phase 4**: Configuration reviews (T041-T045) can run in parallel (different sections)
- **Phase 5**: Dockerfile reviews (T056-T058) can run in parallel (different services)
- **Phase 6**: Most polish tasks (T067-T075) can run in parallel

---

## Parallel Example: User Story 1 Image Builds

```bash
# Terminal 1:
docker build -t todo-frontend:1.0.5 ./frontend

# Terminal 2 (simultaneously):
docker build -t todo-backend:2.0.2 ./backend

# Terminal 3 (simultaneously):
docker build -t todo-mcp-server:1.0.2 ./mcp_server
```

All three images can be built in parallel since they are independent services.

---

## Parallel Example: User Story 2 Configuration Updates

```bash
# Single worker (sequential file edits):
# T041: Update CORS_ORIGINS in values.yaml
# T042: Update NEXT_PUBLIC_APP_URL in values.yaml
# T043-T045: Verify secrets and resource limits in values.yaml

# After values.yaml updated:
helm upgrade todo-evolution ./helm-chart

# Then in parallel (different rollouts):
# Terminal 1: kubectl rollout status deployment/todo-evolution-frontend
# Terminal 2: kubectl rollout status deployment/todo-evolution-backend
# Terminal 3: kubectl rollout status deployment/todo-evolution-mcp-server
```

---

## Implementation Strategy

### MVP Scope (First Deliverable)

**Minimum Viable Product = User Story 1 (Phase 3) completion**

After completing Phase 1 (Setup) and Phase 2 (Foundational), focus on User Story 1 tasks (T015-T035). This delivers:
- Complete application deployed to Minikube
- All three services running and accessible
- Frontend, backend, and MCP server functional

**MVP Success Criteria**:
- ✅ All pods Running (5/5)
- ✅ Frontend accessible in browser
- ✅ Backend API responding
- ✅ MCP server accessible from backend

### Incremental Delivery

1. **MVP (User Story 1)**: Deploy working application to Minikube
2. **Enhancement (User Story 2)**: Update and verify configuration
3. **Validation (User Story 3)**: Ensure image rebuild process works
4. **Polish (Phase 6)**: Final validation and documentation

### Rollback Strategy

If any phase fails:
- **Deployment issues**: `helm rollback todo-evolution` (reverts to previous version)
- **Image build issues**: Delete image and rebuild (check Dockerfile, check logs)
- **Configuration issues**: Revert values.yaml changes and `helm upgrade`
- **Minikube issues**: `minikube delete && minikube start` (clean slate)

---

## Success Criteria Validation

From `spec.md` Success Criteria:

- **SC-001**: ✅ All services deploy successfully (T015, T031 verify this)
- **SC-002**: ✅ Frontend loads within 30 seconds (T017, T067 verify this)
- **SC-003**: ✅ Backend health returns 200 OK (T018 verifies this)
- **SC-004**: ✅ Environment variables injected (T036-T037 verify this)
- **SC-005**: ✅ End-to-end workflow functional (T067 verifies this)
- **SC-006**: ✅ Semantic versioning used (T024-T026 implement this)
- **SC-007**: ✅ Deployment within 10 minutes (tracked during Phase 3 execution)

---

## Task Summary

- **Total Tasks**: 77 tasks
- **Setup Phase**: 7 tasks (T001-T007)
- **Foundational Phase**: 7 tasks (T008-T014)
- **User Story 1 (P1 MVP)**: 21 tasks (T015-T035)
- **User Story 2 (P2)**: 15 tasks (T036-T050)
- **User Story 3 (P3)**: 16 tasks (T051-T066)
- **Polish Phase**: 11 tasks (T067-T077)

**Parallel Opportunities**: 25+ tasks marked [P] can run in parallel within their phases

**Estimated Execution Time**:
- First-time deployment: 15-20 minutes (includes image builds)
- Subsequent deployments: 8-10 minutes (images cached, faster builds)

---

**Tasks Status**: ✅ Ready for execution

**Next Step**: Begin with Phase 1 (Setup) tasks T001-T007
