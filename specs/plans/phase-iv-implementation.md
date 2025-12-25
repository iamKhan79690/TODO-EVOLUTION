# Phase IV Implementation Plan: Local Kubernetes Deployment

**Plan Created**: 2025-12-21
**Status**: Draft
**Based On**: Infrastructure specifications in `/specs/infrastructure/`
**Target**: Local Minikube Kubernetes deployment with AI-assisted operations

## Executive Summary

This plan outlines the complete implementation strategy for Phase IV of the TODO Evolution project, transforming the application from a development setup to a production-ready Kubernetes deployment running locally on Minikube. The implementation follows Constitutional requirements for security, reproducibility, and AI-assisted operations.

## Technical Context

### Current State
- ✅ Phase III complete: AI chatbot functionality integrated
- ✅ Application running in development mode
- ✅ Basic containerization may exist but not Constitutional-compliant
- ✅ No Kubernetes deployment strategy implemented

### Target State
- ✅ All services containerized with Constitutional compliance
- ✅ Kubernetes deployment on Minikube with proper security
- ✅ Helm chart for reproducible deployments
- ✅ AI-assisted operations (Gordon, kubectl-ai, kagent)
- ✅ Complete infrastructure as code implementation

### Key Technologies
- **Container Platform**: Docker with Gordon AI assistance
- **Orchestration**: Minikube (local Kubernetes)
- **Package Management**: Helm 3.x
- **AI Operations**: Gordon (Docker), kubectl-ai (manifests), kagent (cluster management)
- **Security**: Non-root containers, immutable tags, read-only filesystems
- **Monitoring**: Health probes, resource limits, rolling updates

### Dependencies
- Docker Desktop with Gordon enabled
- Minikube with appropriate resource allocation
- kubectl and Helm CLI tools
- kubectl-ai and kagent for AI operations
- Python 3.13+, Node.js 20+ build environments

## Constitution Check

### Phase IV Constitutional Requirements Validation

#### ✅ Containerization Standards (Section II)
- **Multi-stage builds**: Specified in containerization.md
- **Security hardening**: Non-root user, read-only filesystem - ✅ Planned
- **Image tagging**: Semantic versioning with SHA256 - ✅ Specified
- **Base images**: Official minimal images (node:20-alpine, python:3.13-slim) - ✅ Required

#### ✅ Kubernetes Architecture (Section III)
- **Minikube cluster**: Single-node Kubernetes - ✅ Planned
- **Helm 3.x**: Chart-based deployment - ✅ Planned
- **AI operations**: kubectl-ai and kagent usage - ✅ Planned
- **Resource allocation**: CPU 100m/500m, Memory 128Mi/512Mi - ✅ Specified

#### ✅ Security & Hardening (Section V)
- **Non-root containers**: UID 1000, drop ALL capabilities - ✅ Required
- **Secret management**: Kubernetes Secrets, no git commits - ✅ Required
- **RBAC**: Dedicated ServiceAccounts - ✅ Required

#### ✅ High Availability & Resilience (Section VI)
- **Health probes**: Both liveness and readiness - ✅ Required
- **Rolling updates**: Zero-downtime deployment strategy - ✅ Required

#### ✅ Deployment Standards (Section VII)
- **Standard labels**: All 6 Kubernetes recommended labels - ✅ Required

**Result**: ✅ All Constitutional requirements addressed and planned

## Implementation Phases

### Phase A: Environment Setup (Days 1-2)

#### A.1 Development Environment Preparation
**Estimated Time**: 2 hours

**Tasks**:
1. Verify Docker Desktop installation and Gordon AI availability
2. Install and configure Minikube with appropriate resource allocation
   - `minikube start --cpus=4 --memory=8192 --disk-size=20g`
   - Enable required addons: `ingress`, `metrics-server`, `dashboard`
3. Install Helm 3.x client
   - Download from official Helm releases
   - Verify installation: `helm version`
4. Install kubectl-ai and kagent for AI-assisted operations
5. Configure Docker CLI to point to Minikube's daemon
   - `eval $(minikube docker-env)`
6. Create project structure for Helm chart
   ```bash
   mkdir -p todo-evolution-chart/{templates,tests}
   ```

#### A.2 Prerequisites Validation
**Estimated Time**: 1 hour

**Tasks**:
1. Verify Minikube cluster health
   - `minikube status`
   - `kubectl cluster-info`
2. Test Docker integration with Minikube
   - `docker run --rm nginx:alpine`
   - Verify image runs in Minikube environment
3. Validate Gordon AI functionality
   - Test Gordon with simple Dockerfile generation
4. Test kubectl-ai availability
   - `kubectl-ai "generate a simple nginx deployment"`
5. Verify resource allocation
   - Check available memory and CPU in Minikube
   - Ensure sufficient resources for all three services

### Phase B: Containerization (Days 3-4)

#### B.1 Frontend Containerization (Next.js)
**Estimated Time**: 4 hours

**Tasks**:
1. **Use Gordon AI to generate initial Dockerfile**:
   ```bash
   cd frontend
   docker ai "Create a production-ready multi-stage Dockerfile for Next.js 16 with TypeScript and Tailwind CSS. Include security best practices, non-root user, health endpoints, and minimal attack surface."
   ```

2. **Review and customize Gordon-generated Dockerfile**:
   - Verify multi-stage build structure
   - Ensure non-root user (UID 1000) configuration
   - Add health check endpoints if missing
   - Optimize for Next.js standalone output mode
   - Validate against containerization.md requirements

3. **Build and test container**:
   - `docker build -t todo-frontend:1.0.0-sha256-temp ./frontend`
   - Get SHA256 hash and retag with proper format
   - Test container startup and health endpoints
   - Verify non-root user execution

4. **Finalize production image**:
   ```bash
   SHA=$(docker inspect --format='{{.Id}}' todo-frontend:1.0.0 | cut -d: -f2 | cut -c1-8)
   docker tag todo-frontend:1.0.0 todo-frontend:1.0.0-sha256-$SHA
   docker tag todo-frontend:1.0.0-sha256-$SHA todo-frontend:latest
   ```

#### B.2 Backend Containerization (FastAPI)
**Estimated Time**: 4 hours

**Tasks**:
1. **Use Gordon AI to generate Dockerfile**:
   ```bash
   cd backend
   docker ai "Create a production-ready multi-stage Dockerfile for FastAPI Python application with SQLModel and PostgreSQL. Include security hardening, non-root user, health endpoints, and minimal runtime footprint."
   ```

2. **Review and customize Dockerfile**:
   - Verify Python 3.13-slim base image usage
   - Ensure proper dependency installation with pip
   - Add health check endpoints (/health, /ready)
   - Configure read-only filesystem with tmp volume
   - Validate against containerization.md requirements

3. **Build and test container**:
   - `docker build -t todo-backend:1.0.0-sha256-temp ./backend`
   - Get SHA256 and retag properly
   - Test FastAPI startup and API endpoints
   - Verify database connectivity

4. **Production image preparation**:
   ```bash
   SHA=$(docker inspect --format='{{.Id}}' todo-backend:1.0.0 | cut -d: -f2 | cut -c1-8)
   docker tag todo-backend:1.0.0 todo-backend:1.0.0-sha256-$SHA
   ```

#### B.3 MCP Server Containerization
**Estimated Time**: 3 hours

**Tasks**:
1. **Use Gordon AI to generate Dockerfile**:
   ```bash
   cd mcp_server
   docker ai "Create a production-ready multi-stage Dockerfile for Python MCP server with OpenAI integration. Include security hardening, non-root user, health endpoints, and minimal resource usage."
   ```

2. **Review and optimize Dockerfile**:
   - Verify Python 3.13-slim base image
   - Optimize for single-replica deployment
   - Add health endpoints for monitoring
   - Configure read-only filesystem
   - Validate against containerization.md requirements

3. **Build and test container**:
   - `docker build -t todo-mcp-server:1.0.0-sha256-temp ./mcp_server`
   - Test MCP server startup and communication
   - Verify OpenAI API integration
   - Test health check endpoints

4. **Production image tagging**:
   ```bash
   SHA=$(docker inspect --format='{{.Id}}' todo-mcp-server:1.0.0 | cut -d: -f2 | cut -c1-8)
   docker tag todo-mcp-server:1.0.0 todo-mcp-server:1.0.0-sha256-$SHA
   ```

#### B.4 Container Security Validation
**Estimated Time**: 2 hours

**Tasks**:
1. **Run constitution-enforcer validation**:
   ```bash
   constitution-enforcer: Please validate these container images against Constitutional rules
   Images: todo-frontend:1.0.0-sha256-*, todo-backend:1.0.0-sha256-*, todo-mcp-server:1.0.0-sha256-*
   ```

2. **Verify security contexts**:
   - Check all containers run as non-root (UID 1000)
   - Verify capabilities are dropped
   - Test read-only filesystem functionality

3. **Image scanning**:
   - Scan for vulnerabilities if tools available
   - Address any critical security findings
   - Document any acceptable risks

### Phase C: Helm Chart Creation (Days 5-6)

#### C.1 Initial Chart Structure
**Estimated Time**: 2 hours

**Tasks**:
1. **Use kubectl-ai to generate base Helm chart**:
   ```bash
   kubectl-ai "Generate a Helm chart for a todo app with frontend (Next.js), backend (FastAPI), and mcp-server deployments. Include services, configmaps, secrets, proper labels, and security contexts according to Kubernetes best practices."
   ```

2. **Set up chart metadata**:
   - Create `Chart.yaml` with proper metadata
   - Define appVersion and chart version
   - Add maintainers and repository information

3. **Create values.yaml structure**:
   - Define default configuration values
   - Parameterize image repositories and tags
   - Configure replica counts and resources
   - Set up environment variables

#### C.2 Template Generation
**Estimated Time**: 4 hours

**Tasks**:
1. **Generate deployment templates**:
   - `frontend-deployment.yaml` with kubectl-ai assistance
   - `backend-deployment.yaml` with security contexts
   - `mcp-deployment.yaml` with minimal resources

2. **Generate service templates**:
   - `frontend-service.yaml` (LoadBalancer)
   - `backend-service.yaml` (ClusterIP)
   - `mcp-service.yaml` (ClusterIP)

3. **Create configuration templates**:
   - `configmap.yaml` for non-sensitive configuration
   - `secrets.yaml` template for sensitive data references
   - ServiceAccount templates for each deployment

4. **Add helper functions**:
   - Create `_helpers.tpl` with standard label functions
   - Implement name generation and image functions
   - Add security context helpers

#### C.3 Chart Customization and Validation
**Estimated Time**: 3 hours

**Tasks**:
1. **Customize templates to match kubernetes-deployment.md**:
   - Ensure all security contexts are properly applied
   - Verify resource allocations match specifications
   - Add all required Kubernetes labels

2. **Create environment-specific values files**:
   - `values-dev.yaml` (development configuration)
   - `values-prod.yaml` (production configuration)
   - `values-staging.yaml` (staging configuration)

3. **Add documentation and helper files**:
   - Create comprehensive `NOTES.txt` template
   - Add chart documentation
   - Include troubleshooting guides

4. **Validate chart with constitution-enforcer**:
   - Test chart rendering: `helm template todo-evolution ./todo-evolution-chart`
   - Validate generated manifests
   - Ensure 100% Constitutional compliance

### Phase D: Deployment (Days 7-8)

#### D.1 Kubernetes Resource Preparation
**Estimated Time**: 2 hours

**Tasks**:
1. **Create secrets manually** (production requirement):
   ```bash
   kubectl create secret generic todo-secrets \
     --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db" \
     --from-literal=JWT_SECRET="your-jwt-secret-key" \
     --from-literal=OPENAI_API_KEY="your-openai-api-key"
   ```

2. **Configure ConfigMap**:
   - Apply default configuration from chart
   - Customize for Minikube environment
   - Validate service URLs and endpoints

3. **Validate cluster readiness**:
   - Check Minikube resource allocation
   - Verify networking configuration
   - Test DNS resolution

#### D.2 Helm Chart Installation
**Estimated Time**: 3 hours

**Tasks**:
1. **Install chart with default values**:
   ```bash
   helm install todo-evolution ./todo-evolution-chart \
     --namespace default \
     --create-namespace
   ```

2. **Monitor deployment progress**:
   - `kubectl get pods -l app.kubernetes.io/part-of=todo-evolution`
   - Check pod startup logs
   - Verify all pods reach Running state

3. **Validate service connectivity**:
   - Test frontend → backend communication
   - Verify service discovery via DNS
   - Test all health check endpoints

#### D.3 Service Access Configuration
**Estimated Time**: 2 hours

**Tasks**:
1. **Configure LoadBalancer access**:
   - Get frontend service URL: `minikube service todo-evolution-frontend-service --url`
   - Test external access to frontend
   - Verify LoadBalancer functionality

2. **Set up port forwarding for internal services**:
   - `kubectl port-forward svc/todo-evolution-backend-service 8080:8000`
   - `kubectl port-forward svc/todo-evolution-mcp-service 8001:8001`

3. **Test complete application functionality**:
   - Verify frontend can reach backend API
   - Test CRUD operations through UI
   - Validate MCP server integration

### Phase E: Validation & Testing (Days 9-10)

#### E.1 Constitutional Compliance Validation
**Estimated Time**: 2 hours

**Tasks**:
1. **Run comprehensive constitution-enforcer validation**:
   ```bash
   constitution-enforcer: Validate complete deployment against all Phase IV Constitutional rules
   ```

2. **Validate all security requirements**:
   - Check non-root container execution
   - Verify capability dropping
   - Test read-only filesystem constraints

3. **Generate compliance reports**:
   - Document 100% compliance status
   - Create detailed compliance report for each service
   - Archive validation results

#### E.2 Integration Testing
**Estimated Time**: 4 hours

**Tasks**:
1. **Deploy application tests**:
   - Install chart with test suite
   - Run connection tests
   - Execute health check validations

2. **End-to-end application testing**:
   - Test user registration and authentication
   - Verify CRUD operations work correctly
   - Test MCP server AI functionality

3. **Performance and scalability testing**:
   - Test resource utilization under load
   - Verify rolling update functionality
   - Test graceful shutdown behavior

#### E.3 Troubleshooting and Documentation
**Estimated Time**: 3 hours

**Tasks**:
1. **Create comprehensive troubleshooting guide**:
   - Common deployment issues and solutions
   - Debug commands and log analysis
   - Recovery procedures for common failures

2. **Document deployment procedures**:
   - Step-by-step installation guide
   - Environment-specific configuration
   - Rollback and upgrade procedures

3. **Create operational runbooks**:
   - Daily health check procedures
   - Monitoring and alerting setup
   - Backup and recovery procedures

## Success Criteria

### Technical Success Metrics
- [ ] All three containers built and running with Constitutional compliance (100%)
- [ ] Helm chart installs successfully with all resources (100%)
- [ ] Application fully functional in Minikube environment (100%)
- [ ] Health monitoring and self-healing working (100%)
- [ ] Zero-downtime rolling updates verified (100%)
- [ ] AI-assisted operations demonstrated (Gordon, kubectl-ai, kagent) (100%)

### Operational Success Metrics
- [ ] Deployment completes within specified timeframe (Day 8)
- [ ] All Constitutional rules validated and documented (100%)
- [ ] Documentation complete and comprehensive (100%)
- [ ] Troubleshooting procedures tested and validated (100%)

### Quality Gates
- [ ] Constitution-enforcer approval for all configurations
- [ ] All images use immutable tags with SHA256
- [ ] All pods run as non-root with proper security contexts
- [ ] All services have working health probes
- [ ] Helm chart follows best practices and standards

## Risk Assessment

### High Risk Items
1. **Minikube Resource Constraints**: Insufficient CPU/memory for all services
   - **Mitigation**: Configure Minikube with 4 CPUs, 8GB RAM, 20GB disk
   - **Monitoring**: Resource utilization checks during deployment

2. **AI Tool Availability**: Gordon or kubectl-ai not working as expected
   - **Mitigation**: Manual fallback procedures documented
   - **Monitoring**: Early validation of AI tool functionality

3. **Complex Application Dependencies**: Database connection issues or API integration problems
   - **Mitigation**: Thorough integration testing in Phase E
   - **Monitoring**: Comprehensive connection testing

### Medium Risk Items
1. **Container Build Failures**: Gordon-generated Dockerfiles may require adjustments
   - **Mitigation**: Manual review and customization of generated files
   - **Timeline**: Buffer time included in Phase B

2. **Helm Chart Complexity**: Template rendering errors or configuration issues
   - Mitigation: Use `helm lint` and `helm template` for validation
   - **Testing**: Multiple test iterations in Phase C

3. **Service Discovery Issues**: DNS resolution or network connectivity problems
   - Mitigation: Kubernetes networking validation in Phase D
   - **Debugging**: Network policy and service configuration review

### Low Risk Items
1. **Documentation Accuracy**: Documentation may not match final implementation
   - **Mitigation**: Final documentation update in Phase E
   - **Validation**: Peer review of all documentation

## Resource Requirements

### Hardware Requirements
- **CPU**: 4 cores minimum for Minikube
- **RAM**: 8GB minimum for Minikube
- **Storage**: 20GB minimum for Minikube
- **Network**: Stable internet connection for AI tool usage

### Software Requirements
- Docker Desktop with Gordon AI enabled
- Minikube version 1.28+
- Helm 3.8+
- kubectl 1.28+
- kubectl-ai and kagent
- Python 3.13+ (for backend/MCP)
- Node.js 20+ (for frontend)

### Time Allocation
- **Phase A**: 3 days (Environment Setup)
- **Phase B**: 4 days (Containerization)
- **Phase C**: 3 days (Helm Chart)
- **Phase D**: 3 days (Deployment)
- **Phase E**: 3 days (Validation)
- **Buffer Time**: 2 days
- **Total**: 18 days

## Dependencies

### External Dependencies
- Gordon AI for Dockerfile generation
- kubectl-ai for Kubernetes manifest generation
- kagent for cluster management
- Docker Hub or container registry
- GitHub repository for chart storage

### Internal Dependencies
- Phase III application source code
- Database configuration (Neon PostgreSQL)
- Authentication configuration (Better Auth setup)
- All Phase IV infrastructure specifications

## Next Steps

1. **Begin Phase A**: Environment Setup and tool verification
2. **Start Phase B**: Containerization with Gordon AI assistance
3. **Proceed to Phase C**: Helm chart development with kubectl-ai
4. **Execute Phase D**: Kubernetes deployment and service configuration
5. **Complete Phase E**: Validation, testing, and documentation

## Contingency Plans

### If Gordon AI Unavailable
- Manual Dockerfile creation following specification requirements
- Use standard Dockerfile patterns as templates
- Document manual processes in ADR (Architecture Decision Record)

### If Minikube Resource Issues
- Reduce replica counts temporarily (frontend: 1, backend: 1, mcp: 1)
- Lower resource limits within acceptable ranges
- Document resource optimization strategies

### If AI Tools Fail
- Manual Kubernetes manifest creation
- Use `kubectl create --dry-run` for validation
- Leverage standard Helm chart templates as starting point

---

**Prepared By**: Constitution-Driven Development Team
**Next Review**: Constitution validation gate before Phase A implementation
**Timeline**: 18-day implementation window
**Success Definition**: 100% Constitutional compliance with production-ready Kubernetes deployment