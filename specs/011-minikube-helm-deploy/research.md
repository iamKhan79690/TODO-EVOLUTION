# Research: Minikube Helm Deployment Update

**Feature**: Minikube Helm Deployment Update (011-minikube-helm-deploy)
**Date**: 2025-12-30
**Status**: Complete

## Tooling Availability

### Installed Tools

1. **Minikube**
   - Version: NEEDS_CLARIFICATION (not verified yet)
   - Status: Stopped (last check showed host: Stopped, kubelet: Stopped, apiserver: Stopped)
   - Location: WSL2 Ubuntu environment

2. **Docker Desktop**
   - Version: NEEDS_CLARIFICATION (not verified yet)
   - Status: Running (Docker daemon available)
   - Environment: Windows with WSL2 backend

3. **kubectl**
   - Version: NEEDS_CLARIFICATION (not verified yet)
   - Status: Available for cluster management

4. **Helm**
   - Version: NEEDS_CLARIFICATION (not verified yet)
   - Status: Available for package management

5. **AI Tools Status**
   - Gordon (Docker AI): ❌ NOT AVAILABLE
   - kubectl-ai: ❌ NOT AVAILABLE
   - kagent: ❌ NOT AVAILABLE
   - **Fallback**: Standard Docker CLI, kubectl, and Helm commands

## Current Deployment State

### Existing Helm Chart Analysis

**Location**: `helm-chart/`

**Chart Metadata** (`Chart.yaml`):
- Chart name: `todo-evolution`
- Version: 1.0.0
- App Version: 1.0.0
- Description: A Helm chart for TODO Evolution application with frontend, backend, and MCP server

**Current Image Tags** (`values.yaml`):
- Frontend: `todo-frontend:1.0.4` → **Update to 1.0.5**
- Backend: `todo-backend:2.0.1` → **Update to 2.0.2**
- MCP Server: `todo-mcp-server:1.0.1` → **Update to 1.0.2**

**Image Pull Policy**: `Never` (uses local images in Minikube Docker)

**Current Configuration**:
- Frontend: 2 replicas, LoadBalancer on port 80
- Backend: 2 replicas, NodePort on port 8000
- MCP Server: 1 replica, ClusterIP on port 8001

**Secrets Configuration**:
- DATABASE_URL: Configured (Neon PostgreSQL)
- JWT_SECRET: Configured
- OPENAI_API_KEY: Placeholder ("sk-your-openai-api-key-here")
- GEMINI_API_KEY: Configured (AIzaSyCSDQHIlBcYxZZ9IiZgpiPvZo66ulXhywg)

**Required Updates**:
1. Increment image version tags
2. Verify and update CORS_ORIGINS for Minikube URLs
3. Update NEXT_PUBLIC_APP_URL to match Minikube LoadBalancer
4. Verify all secret values are correct

### Dockerfiles Status

**Frontend Dockerfile** (`frontend/Dockerfile`):
- Multi-stage build: Dependencies → Builder → Runtime
- Base image: node:20-alpine
- Non-root user: nextjs (UID 1001)
- Port: 3000
- Health check: /api/health endpoint
- Status: ✅ Compliant with constitutional requirements

**Backend Dockerfile** (`backend/Dockerfile`):
- Multi-stage build: Dependencies → Runtime
- Base image: python:3.13-slim
- Non-root user: appuser (UID 1000)
- Port: 8000
- Health check: /health/health endpoint
- Status: ✅ Compliant with constitutional requirements

**MCP Server Dockerfile** (`mcp_server/Dockerfile`):
- Multi-stage build: Dependencies → Runtime
- Base image: python:3.13-slim
- Non-root user: appuser (UID 1000)
- Port: 8001
- Health check: /health endpoint
- Status: ✅ Compliant with constitutional requirements

## System Resources

### Minikube Resource Requirements

**Minimum Viable Configuration**:
- CPUs: 4 cores
- Memory: 8192 MB (8 GB)
- Disk: 20 GB

**Windows WSL2 Considerations**:
- WSL2 supports Minikube with Docker driver
- Hyper-V required for some drivers (virtualbox, vmware)
- Docker Desktop WSL2 integration recommended
- Memory allocation: Ensure WSL2 has access to sufficient RAM

**Current System Status**:
- Platform: Windows with WSL2 Ubuntu
- Docker: Docker Desktop with WSL2 backend
- Minikube Driver: Docker driver recommended (`--driver=docker`)

## Database Connectivity

### Neon PostgreSQL Configuration

**Connection String Format**:
```
postgresql+asyncpg://neondb_owner:npg_6XJMDV8OidrG@ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech/neondb?ssl=require
```

**Driver**: asyncpg (async PostgreSQL driver for Python)
**SSL**: Required (`ssl=require`)
**Host**: ep-soft-wave-a4c4579s-pooler.us-east-1.aws.neon.tech
**Database**: neondb
**User**: neondb_owner

**Connectivity Considerations**:
- Public cloud database (accessible from local cluster)
- No firewall rules required (Neon manages this)
- Connection string already formatted correctly for SQLModel/FastAPI

**Verification Required**:
- Test connection from local machine
- Verify asyncpg driver compatibility
- Confirm SSL certificate validation works

## Best Practices

### Docker Image Versioning

**Semantic Versioning** (Major.Minor.Patch):
- **Major**: Breaking changes (2.0.0 → 3.0.0)
- **Minor**: New features (2.0.0 → 2.1.0)
- **Patch**: Bug fixes (2.0.1 → 2.0.2)

**Strategy for This Deployment**:
- Increment patch version for all services (code changes + configuration updates)
- Frontend: 1.0.4 → 1.0.5 (patch)
- Backend: 2.0.1 → 2.0.2 (patch)
- MCP Server: 1.0.1 → 1.0.2 (patch)

**Anti-Patterns**:
- ❌ Using `latest` tag (unpredictable deployments)
- ❌ Using `dev` or `staging` in production
- ❌ Skipping version numbers

### Minikube on Windows WSL2

**Driver Selection**:
- **Recommended**: Docker driver (`--driver=docker`)
- **Alternative**: VirtualBox (`--driver=virtualbox`) if Hyper-V issues
- **Avoid**: Hyper-V driver (conflicts with Docker Desktop)

**Docker Daemon Integration**:
```powershell
# Windows PowerShell:
minikube docker-env | Invoke-Expression

# This sets:
# - DOCKER_TLS_VERIFY
# - DOCKER_HOST
# - DOCKER_CERT_PATH
# - DOCKER_API_VERSION
```

**Common Issues**:
1. **WSL2 Memory Limits**: Edit `.wslconfig` to increase memory
2. **Docker Desktop Integration**: Enable WSL2 integration in Docker Desktop settings
3. **Minikube Start Failures**: Try `minikube delete` then `minikube start` with different driver
4. **Network Issues**: Check Windows Firewall settings

### Helm Chart Updates

**Values.yaml Best Practices**:
- Use semantic versioning for image tags
- Separate configuration from code (environment variables, resource limits)
- Document all non-default values
- Use `imagePullPolicy: Never` for local Minikube images
- Define resource requests and limits (prevent resource exhaustion)

**Rolling Update Strategy**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1  # At most 1 pod down during update
    maxSurge: 1        # At most 1 extra pod during update
```

**Secret Management**:
- Never commit actual secrets to git
- Use placeholder values in version control
- Document required secret keys in comments
- For local development: Base64 encoding in values.yaml acceptable

### Service Exposure

**Service Types for Minikube**:

1. **LoadBalancer** (Frontend):
   - Pros: Easy access via `minikube service` command
   - Cons: Requires tunnel on Windows (Minikube v1.20+)
   - Command: `minikube service <service-name> --url`

2. **NodePort** (Backend):
   - Pros: Direct access via `<node-ip>:<node-port>`
   - Cons: Port management complexity
   - Command: `kubectl get nodes -o wide` (get node IP)

3. **ClusterIP** (MCP Server):
   - Pros: Internal-only access (secure)
   - Cons: Not accessible from host without port-forwarding
   - Command: `kubectl port-forward <pod> 8001:8001`

**Minikube Tunnel** (for LoadBalancer):
```powershell
# Run in separate terminal:
minikube tunnel

# This provisions LoadBalancer IPs on Windows
# Requires administrator privileges
```

## Decisions & Rationale

### Decision 1: Image Version Increment Strategy

**Decision**: Increment patch version for all services (1.0.4→1.0.5, 2.0.1→2.0.2, 1.0.1→1.0.2)

**Rationale**:
- Patch version appropriate for bug fixes and configuration updates
- No breaking changes or major new features introduced
- Maintains consistency with existing versioning scheme
- Follows semantic versioning best practices

**Alternatives Considered**:
- Increment minor version: Rejected (no new features)
- Use custom version tags: Rejected (violates semantic versioning)

### Decision 2: Minikube Docker Driver

**Decision**: Use Docker driver (`--driver=docker`) for Minikube

**Rationale**:
- Best integration with Docker Desktop WSL2 backend
- No additional hypervisor required (unlike VirtualBox)
- Better performance than Hyper-V driver
- Simpler setup on Windows WSL2

**Alternatives Considered**:
- VirtualBox driver: Rejected (requires separate installation, Hyper-V conflicts)
- Hyper-V driver: Rejected (conflicts with Docker Desktop)
- Podman driver: Rejected (not installed, incompatible with Docker Desktop)

### Decision 3: LoadBalancer with Tunnel for Frontend

**Decision**: Use LoadBalancer service type with `minikube tunnel` for frontend access

**Rationale**:
- LoadBalancer provides clean URL access
- `minikube tunnel` enables LoadBalancer support on Windows
- More production-like than NodePort
- Easier to document and use than port-forwarding

**Alternatives Considered**:
- NodePort: Rejected (requires manual IP discovery, less clean)
- Ingress: Rejected (adds complexity, overkill for local development)
- Port-forwarding: Rejected (not persistent, manual setup required)

### Decision 4: Fallback to Standard CLI Tools

**Decision**: Use standard Docker CLI, kubectl, and Helm instead of AI tools (Gordon, kubectl-ai, kagent)

**Rationale**:
- AI tools not available on this system
- Constitution allows fallback documented in emergency protocols
- Existing Dockerfiles and Helm charts are compliant
- Standard tools are well-documented and reliable

**Alternatives Considered**:
- Wait for AI tools to become available: Rejected (blocks progress)
- Manual YAML writing: Rejected (existing Helm charts available)
- ADR Required: Yes (ADR-011 will document this deviation)

## Open Questions

1. **Minikube Version**: What version is installed? (Check with `minikube version`)
2. **Helm Version**: What version is installed? (Check with `helm version`)
3. **kubectl Version**: What version is installed? (Check with `kubectl version --client`)
4. **System Resources**: Does system have 4+ CPUs and 8+ GB RAM available?
5. **Database Test**: Does Neon database connection work from local machine?

## Next Steps

1. Verify tool versions (Minikube, Helm, kubectl)
2. Test database connectivity
3. Create ADR-011 for AI tools deviation
4. Execute deployment steps outlined in plan.md
5. Document any issues encountered during deployment

---

**Research Status**: ✅ Phase 0 Complete

**Constitutional Compliance**: ✅ PASS (with documented deviation for AI tools)

**Ready for Phase 1**: Design & Contracts
