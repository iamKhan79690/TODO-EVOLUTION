# Data Model: Phase IV - Deployment Execution

**Feature**: 2-phase-iv-deployment-execution
**Created**: 2025-12-23
**Status**: Final

## Overview

This document defines the key entities and resources for the Phase IV deployment execution. Unlike application features that define database models, this deployment specification defines deployment artifacts, configuration entities, and operational state.

## Core Entities

### 1. Tool Installation

**Description**: Development tools that must be installed on the local machine before deployment can begin.

**Attributes**:
- `name`: Tool identifier (docker-desktop, minikube, helm, kubectl-ai, kagent)
- `version`: Minimum version required (Docker Desktop 4.53+, Minikube v1.37.0+, Helm v3.15.0+)
- `platform`: Supported platforms (Windows, macOS, Linux)
- `install_method`: Installation approach (installer, script, binary)
- `verification_command`: Command to verify installation (`docker ai "What can you do?"`, `minikube status`, `helm version`)
- `status`: Installation state (not-installed, installed, verified, failed)
- `fallback`: Alternative approach if primary installation fails

**Relationships**:
- Tool Installation → Minikube Cluster: Tools must be installed before cluster creation
- Tool Installation → Container Build: Docker Desktop must be installed before building images

**Validation Rules**:
- Docker Desktop MUST be version 4.53+ for Gordon support
- Minikube MUST have 4 CPUs and 8GB RAM available
- Helm CLI MUST be compatible with Minikube Kubernetes version

---

### 2. Container Image

**Description**: Docker image built from application source code using existing Dockerfiles.

**Attributes**:
- `name`: Image identifier (todo-frontend, todo-backend, todo-mcp-server)
- `tag`: Semantic version (1.0.0) - never uses 'latest'
- `registry`: Docker registry (local for Minikube deployment)
- `dockerfile_path`: Path to Dockerfile (frontend/Dockerfile, backend/Dockerfile, mcp_server/Dockerfile)
- `context`: Build context directory
- `base_image`: Parent image (node:20-alpine for frontend, python:3.13-slim for backend/MCP)
- `size`: Image size in MB (target: < 500MB per image)
- `health_check`: HTTP endpoint for container validation (/api/health, /health/)
- `user_id`: Non-root user ID (1001 for frontend, 1000 for backend/MCP)

**Relationships**:
- Container Image → Build Process: Created from Dockerfile and source code
- Container Image → Minikube Image Load: Loaded into Minikube's Docker daemon
- Container Image → Kubernetes Pod: Deployed as container in pod

**State Transitions**:
```
[source code] → [Dockerfile exists] → [docker build] → [image:tag created] → [tested locally] → [loaded into Minikube]
```

**Validation Rules**:
- Tag MUST be semantic version (MAJOR.MINOR.PATCH)
- Image MUST run as non-root user (UID 1000 or 1001)
- Image MUST include health check endpoint
- Image MUST be tested locally before deployment

---

### 3. Minikube Cluster

**Description**: Local single-node Kubernetes environment for development and testing.

**Attributes**:
- `name`: Cluster name (minikube)
- `driver`: Container driver (docker)
- `cpus`: Number of CPUs allocated (4)
- `memory`: Memory allocated in MB (8192 = 8GB)
- `disk_size`: Disk size in GB (20GB)
- `kubernetes_version`: Kubernetes version (v1.30.0)
- `status`: Cluster state (Stopped, Starting, Running, Error)
- `addons_enabled`: List of enabled addons (ingress, metrics-server)

**Relationships**:
- Minikube Cluster → Pod Deployment: Hosts all application pods
- Minikube Cluster → Service: Exposes services via LoadBalancer (tunnel)
- Minikube Cluster → Container Image Load: Uses Docker daemon for image loading

**State Transitions**:
```
[not exists] → [minikube start] → [Starting] → [Running] → [minikube stop] → [Stopped] → [minikube delete] → [not exists]
```

**Validation Rules**:
- MUST have minimum 4 CPUs and 8GB RAM
- MUST be in Running state before deployment
- MUST have ingress and metrics-server addons enabled
- MUST use Docker driver for image loading

---

### 4. Kubernetes Secret

**Description**: Kubernetes Secret for storing sensitive configuration data.

**Attributes**:
- `name`: Secret name (todo-secrets)
- `namespace`: Kubernetes namespace (default)
- `type`: Secret type (Opaque for generic secrets)
- `data`: Key-value pairs with base64-encoded values

**Secret Keys**:
- `DATABASE_URL`: PostgreSQL connection string for backend
  - Format: `postgresql+asyncpg://todo_user:password@host:port/database`
  - Source: Neon or local PostgreSQL
  - Encoding: base64 when stored in Secret

- `JWT_SECRET`: Shared secret for Better Auth JWT token validation
  - Requirements: Minimum 32 characters
  - Used by: Frontend Better Auth and backend JWT middleware
  - Encoding: base64 when stored in Secret

- `OPENAI_API_KEY`: OpenAI API key for MCP server AI functionality
  - Format: sk-...
  - Used by: MCP server for AI chat
  - Encoding: base64 when stored in Secret

**Relationships**:
- Kubernetes Secret → Deployment: Referenced by backend and MCP deployments
- Kubernetes Secret → Environment Variables: Injected as environment variables

**Validation Rules**:
- MUST be created before Helm installation
- Values MUST be base64 encoded
- MUST NOT be committed to git
- All three keys MUST be present

---

### 5. Helm Release

**Description**: Helm chart deployment instance managing application resources.

**Attributes**:
- `name`: Release name (todo-evolution)
- `namespace`: Kubernetes namespace (default)
- `chart`: Helm chart reference (./helm-chart/)
- `version`: Chart version (1.0.0)
- `status`: Deployment state (deployed, pending, failed, superseded)
- `revision`: Deployment revision number (incremented on each update)
- `updated`: Timestamp of last update

**Relationships**:
- Helm Release → Deployment: Creates and manages Kubernetes deployments
- Helm Release → Service: Creates and manages Kubernetes services
- Helm Release → Secret: References existing Kubernetes secrets

**State Transitions**:
```
[not deployed] → [helm install] → [deployed] → [helm upgrade] → [deployed (new revision)] → [helm uninstall] → [not deployed]
```

**Validation Rules**:
- Chart MUST pass `helm lint` validation before installation
- Secrets MUST exist before installation
- Images MUST be available in Minikube's Docker daemon
- All pods MUST be Running and Ready after installation

---

### 6. Kubernetes Pod

**Description**: Smallest deployable Kubernetes unit running one or more containers.

**Attributes**:
- `name`: Pod name (auto-generated by deployment)
- `namespace`: Kubernetes namespace (default)
- `labels`: Key-value pairs for identification (app, component, version)
- `status`: Pod phase (Pending, Running, Succeeded, Failed, Unknown)
- `restart_count`: Number of pod restarts
- `ready`: Boolean indicating readiness
- `container_count`: Number of containers in pod (typically 1)

**Pod Types**:
- `frontend`: Next.js application pods (2 replicas)
  - Container: todo-frontend:1.0.0
  - Port: 3000
  - Replicas: 2

- `backend`: FastAPI application pods (2 replicas)
  - Container: todo-backend:1.0.0
  - Port: 8000
  - Replicas: 2

- `mcp-server`: MCP server pods (1 replica)
  - Container: todo-mcp-server:1.0.0
  - Port: 8001
  - Replicas: 1

- `postgresql`: Database pod (if deployed locally)
  - Container: postgresql (bitnami chart)
  - Port: 5432
  - Replicas: 1

**Relationships**:
- Pod → Deployment: Managed by ReplicaSet controlled by Deployment
- Pod → Service: Selected by service selector
- Pod → Container Image: Runs container from built image

**State Transitions**:
```
[pending] → [container creating] → [running] → [ready] → [terminated]
[error] → [crash loop back off] → [restart]
```

**Validation Rules**:
- All pods MUST be in Running state
- All pods MUST be Ready (readiness probe passing)
- Restart count SHOULD be 0 (indicates stability)
- Resource usage MUST stay within limits

---

### 7. Kubernetes Service

**Description**: Network abstraction for pod access and service discovery.

**Attributes**:
- `name`: Service name (todo-evolution-frontend, todo-evolution-backend, todo-evolution-mcp-server)
- `namespace`: Kubernetes namespace (default)
- `type`: Service type (LoadBalancer for frontend, ClusterIP for backend/MCP)
- `selector`: Label selector for pods (app=todo-evolution, component=<type>)
- `ports`: List of port mappings
- `cluster_ip`: Cluster IP address (for ClusterIP services)
- `external_ip`: External IP address (for LoadBalancer services)

**Service Types**:

**Frontend Service**:
- Name: `todo-evolution-frontend`
- Type: LoadBalancer
- Port: 80 (external) → 3000 (target)
- Accessible via: Minikube tunnel or minikube service URL

**Backend Service**:
- Name: `todo-evolution-backend`
- Type: ClusterIP
- Port: 8000
- Accessible via: Kubernetes DNS (todo-evolution-backend.default.svc.cluster.local:8000)

**MCP Server Service**:
- Name: `todo-evolution-mcp-server`
- Type: ClusterIP
- Port: 8001
- Accessible via: Kubernetes DNS (todo-evolution-mcp-server.default.svc.cluster.local:8001)

**Relationships**:
- Service → Pod: Selects pods via label selector
- Service → Service Discovery: Provides DNS name for inter-service communication
- Service → External Access: LoadBalancer exposes frontend externally

**Validation Rules**:
- Selector MUST match pod labels exactly
- Service MUST have endpoints (pods selected)
- Frontend service MUST be accessible via Minikube tunnel
- Backend/MCP services MUST be accessible via Kubernetes DNS

---

## Entity Relationships Summary

```
┌─────────────────────┐
│   Tool Installation  │───▶ [Docker Desktop] ───▶ [Container Images]
│   (Prerequisites)     │
│                       │───▶ [Minikube] ───────▶ [Kubernetes Cluster]
│                       │                          │
│                       │───▶ [Helm CLI] ───────▶ [Helm Release]
│                       │                          │
│                       │───▶ [kubectl-ai/kagent]┤
└─────────────────────┘                          │
                                                     │
┌─────────────────────┐                          ▼
│   Container Images   │                   ┌─────────────────────┐
│   (Build Artifacts)  │                   │   Kubernetes Cluster │
└─────────────────────┘                   │   (Minikube)          │
                     │                   └─────────────────────┘
                     ▼                                    │
┌─────────────────────┐                   ┌─────────────────────┐
│  Kubernetes Secret   │                   │   Kubernetes Pods   │
│  (Configuration)     │                   │   (Applications)    │
└─────────────────────┘                   │   - Frontend (2x)     │
                     │                   │   - Backend (2x)     │
                     ▼                   │   - MCP (1x)         │
┌─────────────────────┐                   └─────────────────────┘
│    Helm Release     │
│   (Deployment)      │
└─────────────────────┘
```

## Configuration Management

### Environment-Specific Values

**Development (values-dev.yaml)** - Not applicable, single environment

**Production (values.yaml)** - Configurable defaults in helm-chart/

### Secret Management

**Creation**:
```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=JWT_SECRET="..." \
  --from-literal=OPENAI_API_KEY="..."
```

**Usage in Deployment**:
- Backend deployment references: `DATABASE_URL`, `JWT_SECRET`, `OPENAI_API_KEY`
- MCP deployment references: `OPENAI_API_KEY`
- Environment variables injected from secret at pod startup

---

## Glossary

- **Docker Desktop**: Container runtime with GUI management and Gordon AI integration
- **Gordon (Docker AI)**: AI agent for intelligent Docker operations (containerize, analyze, optimize)
- **Minikube**: Local single-node Kubernetes cluster for development
- **Helm**: Kubernetes package manager for deploying charts
- **kubectl-ai**: AI agent for Kubernetes operations (deploy, scale, troubleshoot)
- **kagent**: AI agent for cluster analysis and optimization
- **Container Image**: Executable package containing application code and dependencies
- **Kubernetes Pod**: Smallest deployable unit running one or more containers
- **Kubernetes Service**: Network abstraction for service discovery and load balancing
- **Kubernetes Secret**: Encrypted storage for sensitive data
- **Helm Release**: Instance of a Helm chart deployed to Kubernetes
- **LoadBalancer**: Service type that exposes service externally (requires minikube tunnel)
- **ClusterIP**: Service type for internal cluster communication

---

**Status**: ✅ COMPLETE
**Next Steps**: Generate quickstart.md with step-by-step deployment instructions
