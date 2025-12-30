# Feature Specification: Minikube Helm Deployment Update

**Feature Branch**: `011-minikube-helm-deploy`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "now please read my whole project then read the contitution.md file in .specify/memory then update the help charts with latest configuration , secrets.yaml etc and more files then i think you have to rebuild or update these images and deploy on minikube cluster as pods and point to docker deamon and give me the deploy url ."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Updated Application to Minikube (Priority: P1)

As a developer working on the TODO Evolution application, I need to deploy the latest version of the application with updated Helm charts and Docker images to my local Minikube cluster so that I can test the complete containerized application stack.

**Why this priority**: This is critical for the development workflow - without proper local deployment, developers cannot test the complete application in a Kubernetes environment that matches production architecture.

**Independent Test**: Can be fully tested by (1) checking that all pods are in Running state, (2) accessing the frontend application through Minikube service URL, (3) verifying backend API health endpoint, and (4) confirming MCP server is accessible from backend.

**Acceptance Scenarios**:

1. **Given** Minikube cluster is running, **When** Helm charts are installed with updated configuration, **Then** all three services (frontend, backend, MCP server) deploy successfully with Running status
2. **Given** Docker daemon is pointed to Minikube, **When** Docker images are built with latest code, **Then** images are available in Minikube's image registry and pods use them without ImagePullBackOff errors
3. **Given** Application is deployed, **When** frontend LoadBalancer service is accessed via Minikube URL, **Then** application loads and is fully functional with authentication and task management working
4. **Given** Secrets are configured in values.yaml, **When** pods start, **Then** environment variables are correctly injected and services can connect to database and authenticate users

---

### User Story 2 - Update Helm Configuration for Latest Application State (Priority: P2)

As a developer, I need to ensure Helm chart configurations (values.yaml, deployment specs, secrets) reflect the latest application requirements including environment variables, service URLs, and resource limits so that the application runs correctly in Kubernetes.

**Why this priority**: Configuration management is essential for proper deployment - outdated configs cause runtime errors and connection failures between services.

**Independent Test**: Can be tested by (1) verifying all required environment variables are present in pod specs, (2) checking service discovery URLs match actual service names, (3) confirming resource limits are appropriate for Minikube.

**Acceptance Scenarios**:

1. **Given** Application has new environment requirements, **When** values.yaml is updated, **Then** all required environment variables are defined including DATABASE_URL, JWT_SECRET, API keys, and CORS origins
2. **Given** Services need to communicate within cluster, **When** service URLs are configured, **Then** backend uses internal service name (todo-evolution-backend) and frontend can reach backend via API proxy
3. **Given** Minikube resource constraints, **When** resource limits are set, **Then** CPU and memory requests/limits allow pods to schedule without resource conflicts

---

### User Story 3 - Rebuild and Update Docker Images (Priority: P3)

As a developer, I need to rebuild Docker images with the latest application code and configuration changes so that the deployed pods run the most recent version of the application.

**Why this priority**: Without updated images, code changes won't be reflected in the running deployment, making this necessary for testing new features.

**Independent Test**: Can be tested by (1) building new images with incremented version tags, (2) verifying images exist in Minikube Docker daemon, (3) updating Helm values to use new image tags, (4) rolling out deployment and verifying new version is running.

**Acceptance Scenarios**:

1. **Given** Application code has changed, **When** Docker images are rebuilt, **Then** new image tags are created (e.g., todo-frontend:1.0.5, todo-backend:2.0.2, todo-mcp-server:1.0.2)
2. **Given** Minikube Docker daemon is active, **When** images are built, **Then** images are stored locally in Minikube and available to Kubernetes without external registry
3. **Given** New images are ready, **When** Helm release is upgraded, **Then** rolling update deploys new pods with fresh images and old pods terminate gracefully

---

### Edge Cases

- What happens when Minikube cluster is not running or Docker daemon is not pointed to Minikube?
- How does system handle port conflicts if LoadBalancer tries to use already-allocated ports?
- What happens if secrets are not properly Base64 encoded or are missing required keys?
- How does deployment behave when resource limits exceed Minikube's available capacity?
- What happens if database connection string is invalid or database is unreachable from cluster?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST update Helm chart values.yaml with current application configuration including all environment variables, service URLs, and resource requirements
- **FR-002**: System MUST rebuild Docker images for frontend, backend, and MCP server with latest application code
- **FR-003**: System MUST point Docker CLI to Minikube's Docker daemon before building images
- **FR-004**: System MUST update image tags in values.yaml to reference newly built images
- **FR-005**: System MUST configure Kubernetes secrets with Base64-encoded values for DATABASE_URL, JWT_SECRET, and API keys
- **FR-006**: System MUST deploy application to Minikube using Helm install or upgrade command
- **FR-007**: System MUST verify all pods reach Running state and services are accessible
- **FR-008**: System MUST provide working access URLs for frontend application and backend API

### Key Entities

- **Helm Chart**: Kubernetes package containing templates for deployments, services, secrets, and configuration values
- **Docker Images**: Container images for frontend (Next.js), backend (FastAPI), and MCP server (Python)
- **Minikube Cluster**: Local single-node Kubernetes environment for development and testing
- **Kubernetes Secrets**: Encrypted storage for sensitive configuration (database URLs, API keys, JWT secrets)
- **Service Endpoints**: Network endpoints for inter-service communication and external access

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three services (frontend, backend, MCP server) deploy successfully with 0 pods in Error or CrashLoopBackOff state
- **SC-002**: Frontend application loads successfully within 30 seconds of accessing Minikube service URL
- **SC-003**: Backend API health endpoint returns 200 OK status within 5 seconds
- **SC-004**: All environment variables are correctly injected into pods (verified via `kubectl exec` env inspection)
- **SC-005**: User can complete end-to-end workflow: sign up → create task → view task → mark complete
- **SC-006**: Docker images are versioned with semantic versioning (e.g., 1.0.5, 2.0.2) and never use `latest` tag
- **SC-007**: Deployment completes within 10 minutes from start to having all services accessible

### Assumptions

- Minikube is already installed on the development machine
- Docker Desktop is installed and operational
- kubectl and Helm CLI tools are installed and configured
- PostgreSQL database (Neon cloud) is accessible and connection string is available
- Application code is ready and builds without errors
- Developer has sufficient privileges to run Docker and Kubernetes commands

### Dependencies

- Existing Helm chart structure in `helm-chart/` directory
- Dockerfiles for all three services (frontend, backend, MCP server)
- Application source code in `frontend/`, `backend/`, and `mcp_server/` directories
- Minikube cluster running with sufficient resources (4 CPUs, 8GB RAM minimum)
- Valid environment variables for database connection and API keys

### Out of Scope

- Production cloud deployment (this is local Minikube only)
- CI/CD pipeline integration
- Monitoring and observability setup (Prometheus, Grafana)
- Advanced Kubernetes features (HPA, network policies, persistent volumes)
- Multi-cluster or high-availability deployment
- Ingress controller configuration beyond basic LoadBalancer services
