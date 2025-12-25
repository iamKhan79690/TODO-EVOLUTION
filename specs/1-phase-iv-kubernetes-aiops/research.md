# Research Document: Phase IV - Kubernetes AI-Assisted Deployment

**Feature**: 1-phase-iv-kubernetes-aiops
**Created**: 2025-12-23
**Status**: Final

## Overview

This document consolidates research findings for implementing Phase IV Kubernetes deployment using AI-assisted DevOps tools (Gordon, kubectl-ai, kagent, Minikube).

## Technology Decisions

### 1. Docker Desktop + Gordon (Docker AI)

**Decision**: Use Docker Desktop 4.53+ with Gordon beta feature enabled for containerization

**Rationale**:
- Gordon provides AI-assisted Dockerfile generation optimized for production
- Integrated Docker Desktop experience eliminates context switching
- Multi-stage build generation ensures minimal image sizes
- Security best practices built-in (non-root user, health checks)

**Alternatives Considered**:
- **Manual Dockerfile authoring**: Rejected - violates spec requirement for AI-assisted workflow
- **Buildah/Podman**: Rejected - doesn't have Gordon integration
- **Cloud Native Buildpacks**: Rejected - less control over optimization

**Setup Requirements**:
```bash
# Install Docker Desktop 4.53+
# Enable Gordon: Settings > Beta Features > Toggle "Gordon"

# Verify Gordon availability
docker ai "What can you do?"
```

**Known Limitations**:
- Gordon may not be available in all regions/tiers
- Fallback: Use Claude Code to generate Dockerfiles with explicit documentation

### 2. Minikube (Local Kubernetes)

**Decision**: Use Minikube v1.37.0+ for local Kubernetes cluster

**Rationale**:
- Spec explicitly requires Minikube (not kind, k3d, or others)
- Docker driver integration allows using Docker Desktop's daemon
- Resource-efficient for local development
- Add-ons support (ingress, metrics-server, dashboard)

**Alternatives Considered**:
- **kind (Kubernetes in Docker)**: Rejected - violates spec requirement, currently deployed but must be replaced
- **k3s**: Rejected - not full Kubernetes API compatibility
- **microk8s**: Rejected - lacks advanced features needed
- **Docker Desktop Kubernetes**: Rejected - not configurable enough for development

**Setup Requirements**:
```bash
# System requirements
- 4 CPU cores
- 8GB RAM minimum
- 20GB disk space

# Start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Point Docker CLI to Minikube
eval $(minikube docker-env)
```

**Known Limitations**:
- Single-node cluster (no multi-node testing)
- Limited resource scalability
- Fallback: Document kind only with explicit deviation approval

### 3. kubectl-ai (Kubernetes Manifest Generator)

**Decision**: Use kubectl-ai for generating all Kubernetes manifests and Helm charts

**Rationale**:
- Natural language interface to Kubernetes resource generation
- Best practices automatically applied
- Reduces YAML syntax errors
- Accelerates deployment manifest creation

**Alternatives Considered**:
- **Manual YAML authoring**: Rejected - violates spec requirement
- **Helm create command**: Rejected - generates boilerplate that requires extensive customization
- **kustomize**: Rejected - adds complexity, not AI-assisted

**Setup Requirements**:
```bash
# Install via official channels
# Configure API credentials

# Verify functionality
kubectl-ai "show cluster status"
```

**Known Limitations**:
- Requires API authentication
- Rate limits may apply
- Fallback: Use Claude Code to generate YAML with kubectl apply --dry-run validation

### 4. kagent (Cluster Management AI)

**Decision**: Use kagent for cluster health analysis and optimization

**Rationale**:
- AI-powered cluster diagnostics
- Resource optimization recommendations
- Troubleshooting assistance for complex issues
- Complements kubectl-ai for operations

**Alternatives Considered**:
- **Manual log analysis**: Rejected - time-consuming, error-prone
- **Prometheus/Grafana**: Rejected - overkill for local development, Phase V
- **kubectl top**: Rejected - provides data but no analysis

**Setup Requirements**:
```bash
# Install via official channels
# Configure cluster access

# Verify functionality
kagent "analyze cluster health"
```

**Known Limitations**:
- May not have deep Kubernetes expertise
- Recommendations should be validated before applying
- Fallback: Manual analysis with kubectl commands

## Architecture Decisions

### Container Architecture

**Decision**: Multi-stage builds for all services

**Rationale**:
- Smaller final image sizes (faster pulls, less storage)
- Separation of build dependencies from runtime
- Better caching layer utilization

**Implementation**:
```
Stage 1 (Builder): Install build tools, dependencies
Stage 2 (Runtime): Copy only artifacts, minimal base image
```

### Kubernetes Resource Model

**Decision**: 1 Deployment + 1 Service per application

**Rationale**:
- Simpler than multiple deployments per service
- Matches standard microservice pattern
- Easier to manage with Helm

**Deployment Configuration**:
```yaml
Frontend: 2 replicas, LoadBalancer service
Backend: 2 replicas, ClusterIP service
MCP Server: 1 replica, ClusterIP service
```

### Service Discovery

**Decision**: Kubernetes DNS for inter-service communication

**Rationale**:
- Built-in service discovery
- No external service registry needed
- Automatic endpoint updates

**Service Names**:
```
todo-evolution-frontend:3000
todo-evolution-backend:8000
todo-evolution-mcp-server:8001
```

### Secret Management Strategy

**Decision**: Kubernetes Secrets with base64 encoding

**Rationale**:
- Minikube doesn't have KMS encryption
- Base64 encoding provides basic obfuscation
- Secrets never committed to git

**Implementation**:
```bash
# Create secret with base64 encoding
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$(echo -n 'postgresql://...' | base64)" \
  --from-literal=JWT_SECRET="$(echo -n 'secret' | base64)"
```

## Integration Patterns

### Frontend → Backend Communication

**Pattern**: HTTP requests via Kubernetes Service DNS

**Implementation**:
```typescript
// Frontend environment variable
NEXT_PUBLIC_API_URL=http://todo-evolution-backend:8000
```

### Backend → Database Communication

**Pattern**: PostgreSQL connection via external connection string

**Implementation**:
```python
# Backend environment variable
DATABASE_URL="postgresql+asyncpg://todo_user:todo123@postgresql.default.svc.cluster.local:5432/todo"
```

### Backend → MCP Server Communication

**Pattern**: HTTP requests via Kubernetes Service DNS

**Implementation**:
```python
# Backend configuration
MCP_SERVER_URL="http://todo-evolution-mcp-server:8001"
```

## Security Considerations

### Container Security

**Non-Root User**: All containers run as UID 1000 (appuser)
**Read-Only Root Filesystem**: Applied where possible
**Privilege Escalation**: Disabled (allowPrivilegeEscalation: false)
**Capabilities Drop**: Drop all capabilities (drop: [ALL])

### Network Security

**Service Types**:
- Frontend: LoadBalancer (external access)
- Backend/MCP: ClusterIP (internal only)

**Secrets Management**:
- DATABASE_URL in Kubernetes Secret
- JWT_SECRET in Kubernetes Secret
- OPENAI_API_KEY in Kubernetes Secret
- No secrets in ConfigMaps or environment variables

### Pod Security

**Security Context for All Pods**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

## Operational Procedures

### Environment Setup

1. **Install Docker Desktop** with Gordon enabled
2. **Start Minikube** with adequate resources
3. **Install kubectl-ai** and configure authentication
4. **Install kagent** and configure cluster access
5. **Verify all tools** functional

### Container Building with Gordon

1. Navigate to service directory
2. Invoke Gordon with specific requirements
3. Review generated Dockerfile
4. Build and test image locally
5. Tag with semantic version

### Kubernetes Deployment with kubectl-ai

1. Generate manifests with natural language
2. Validate generated YAML
3. Apply to cluster
4. Monitor deployment status
5. Troubleshoot issues with kubectl-ai

### Cluster Management with kagent

1. Run cluster health analysis
2. Review optimization recommendations
3. Apply valid suggestions
4. Monitor improvements
5. Document changes

## Risk Mitigation

### Risk 1: Gordon Unavailable

**Probability**: Medium
**Impact**: High (blocks containerization)

**Mitigation**:
- Primary: Use Gordon as specified
- Fallback: Claude Code generates Dockerfiles
- Documentation: Record deviation in completion report
- ADR: Create ADR documenting unavailability

### Risk 2: kubectl-ai Rate Limits

**Probability**: Medium
**Impact**: Medium (slows manifest generation)

**Mitigation**:
- Cache all generated manifests in git
- Use natural language efficiently (batch requests)
- Fallback: Use kubectl-ai for initial generation, manual edits for updates
- Documentation: Record all AI-generated YAML

### Risk 3: Minikube Resource Constraints

**Probability**: Low
**Impact**: Medium (limits deployment scale)

**Mitigation**:
- Validate system requirements before starting
- Start with minimum viable resources (2 CPUs, 4GB RAM)
- Scale up if needed (minikube start with different params)
- Monitor resource usage with kagent

### Risk 4: AI Tool Accuracy

**Probability**: Medium
**Impact**: Medium (incorrect manifests)

**Mitigation**:
- Always validate AI-generated YAML before applying
- Use `kubectl apply --dry-run=client` for validation
- Test in isolated environment first
- Manual review of security configurations

## Success Metrics

### Tool Compliance Metrics

- **Gordon Usage**: 100% of Dockerfiles generated by Gordon (or fallback documented)
- **kubectl-ai Usage**: 100% of manifests generated by kubectl-ai
- **kagent Usage**: At least 4 cluster analysis operations
- **Minikube Usage**: 100% (no kind or other distributions)

### Deployment Success Metrics

- **Container Build Success**: All 3 images build without errors
- **Deployment Success**: All 5 pods (2 frontend, 2 backend, 1 MCP) reach Ready state
- **Health Check Success**: All health endpoints responding
- **Service Access**: Frontend accessible via Minikube service

### Quality Metrics

- **Security Compliance**: All pods running as non-root
- **Resource Limits**: All containers have requests and limits
- **Manifest Validation**: All YAML pass kubectl dry-run
- **Documentation**: All AI commands logged and versioned

## Next Steps

1. ✅ Research complete - all technical decisions made
2. ⏭️ Create detailed implementation plan (plan.md)
3. ⏭️ Execute Phase 0: Environment setup
4. ⏭️ Execute Phase 1: Generate data-model and contracts
5. ⏭️ Execute deployment using AI-assisted tools only
6. ⏭️ Validate completion against success criteria

---

**Status**: ✅ COMPLETE - Ready for planning phase
**Unknowns Resolved**: 0
**Decisions Documented**: 4 major technology decisions
