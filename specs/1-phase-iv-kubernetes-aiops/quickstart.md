# Quick Start Guide: Phase IV - Kubernetes AI-Assisted Deployment

**Feature**: 1-phase-iv-kubernetes-aiops
**Last Updated**: 2025-12-23
**Estimated Time**: 4 days (22 hours total)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11 with WSL2, macOS, or Linux
- **CPU**: 4 cores minimum (8 recommended)
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Disk**: 20GB free space minimum
- **Network**: Stable internet connection for AI tool access and image downloads

### Required Accounts and API Keys

1. **Docker Hub account** (for Gordon access)
2. **OpenAI API key** (for MCP server functionality)
3. **kubectl-ai API key** (check official documentation for access)
4. **kagent API key** (check official documentation for access)
5. **Neon Database account** (or external PostgreSQL instance)

---

## Phase 0: Environment Setup (Day 1 - 2 hours)

### Step 0.1: Install Docker Desktop with Gordon

**Windows/macOS**:
1. Download Docker Desktop 4.53+ from [docker.com](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop
3. Enable Gordon (Docker AI):
   - Open Docker Desktop settings
   - Navigate to **Features in development** or **Beta features**
   - Toggle **Gordon** to ON
   - Restart Docker Desktop

**Verify Gordon**:
```bash
docker ai "What can you do?"
```

**Expected Output**: Gordon responds with its capabilities

---

### Step 0.2: Stop Existing kind Cluster

If you previously deployed using kind:

```bash
kind delete cluster --name todo-cluster
kubectl config use-context docker-desktop  # or minikube
```

---

### Step 0.3: Install Minikube

**Windows (WSL2)**:
```bash
curl -Lo minikube.exe https://storage.googleapis.com/minikube/releases/v1.37.0/minikube-windows-amd64.exe
Move-Item .\minikube.exe C:\Windows\minikube.exe
```

**macOS**:
```bash
brew install minikube
```

**Linux**:
```bash
curl -LO https://storage.googleapis.com/minikube/releases/v1.37.0/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

---

### Step 0.4: Start Minikube Cluster

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

**Verify Minikube**:
```bash
kubectl get nodes
```

**Expected Output**:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.30.0
```

---

### Step 0.5: Enable Minikube Add-ons

```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

---

### Step 0.6: Install kubectl-ai

Visit the official kubectl-ai documentation for installation instructions for your platform.

**Verify kubectl-ai**:
```bash
kubectl-ai "show cluster status"
```

---

### Step 0.7: Install kagent

Visit the official kagent documentation for installation instructions for your platform.

**Verify kagent**:
```bash
kagent "analyze cluster health"
```

---

### Step 0.8: Install Helm CLI

**Windows (WSL2)**:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**macOS**:
```bash
brew install helm
```

**Verify Helm**:
```bash
helm version
```

---

## Phase 1: AI-Assisted Containerization (Day 1-2 - 6 hours)

### Step 1.1: Frontend Container with Gordon

```bash
cd /mnt/d/Hackathon/TODO-Evolution/frontend

# Ask Gordon to create Dockerfile
docker ai "Create a production-ready multi-stage Dockerfile for Next.js 16 with standalone output, non-root user (UID 1000), health checks, and read-only root filesystem. Use node:18-alpine as base image."

# Review generated Dockerfile
cat Dockerfile

# Build image
docker build -t todo-frontend:1.0.0 .

# Test container
docker run --rm -p 3000:3000 todo-frontend:1.0.0

# Verify health endpoint (in another terminal)
curl http://localhost:3000/api/health
```

**Expected**: Container starts and serves frontend on port 3000

---

### Step 1.2: Backend Container with Gordon

```bash
cd /mnt/d/Hackathon/TODO-Evolution/backend

# Ask Gordon to create Dockerfile
docker ai "Create a production Dockerfile for FastAPI backend with Python 3.13-slim, non-root user (UID 1000), uvicorn server, health check endpoint /health/, and all dependencies from requirements-container.txt including redis, structlog, asyncpg, and fastapi."

# Build image
docker build -t todo-backend:1.0.0 .

# Test container
docker run --rm -p 8000:8000 todo-backend:1.0.0

# Verify health endpoint
curl http://localhost:8000/health/
```

**Expected**: JSON response with health status

---

### Step 1.3: MCP Server Container with Gordon

```bash
cd /mnt/d/Hackathon/TODO-Evolution/mcp_server

# Ask Gordon to create Dockerfile
docker ai "Create a production Dockerfile for Python MCP server with FastAPI, structlog, asyncpg, pydantic, uvicorn, health check /health/, non-root user UID 1000."

# Build image
docker build -t todo-mcp-server:1.0.0 .

# Test container
docker run --rm -p 8001:8001 todo-mcp-server:1.0.0

# Verify health endpoint
curl http://localhost:8001/health/
```

**Expected**: JSON response with health status

---

### Step 1.4: Load Images into Minikube

```bash
# Point Docker CLI to Minikube
eval $(minikube docker-env)

# Load images into Minikube
minikube image load todo-frontend:1.0.0
minikube image load todo-backend:1.0.0
minikube image load todo-mcp-server:1.0.0

# Verify images
docker images | grep todo-
```

---

## Phase 2: AI-Generated Kubernetes Manifests (Day 2-3 - 6 hours)

### Step 2.1: Create kubernetes Directory

```bash
mkdir -p /mnt/d/Hackathon/TODO-Evolution/kubernetes
```

---

### Step 2.2: Generate Frontend Deployment

```bash
kubectl-ai "Create a Kubernetes deployment for Next.js frontend with 2 replicas, LoadBalancer service on port 80, target port 3000, liveness probe GET /api/health with initialDelaySeconds=30, periodSeconds=10, readiness probe GET /api/ready, resource limits 500m CPU, 512Mi memory, requests 100m CPU, 128Mi memory, non-root user UID 1000, security context with readOnlyRootFilesystem=true." > /mnt/d/Hackathon/TODO-Evolution/kubernetes/frontend-deployment.yaml

# Validate YAML
kubectl apply --dry-run=client -f /mnt/d/Hackathon/TODO-Evolution/kubernetes/frontend-deployment.yaml
```

---

### Step 2.3: Generate Backend Deployment

```bash
kubectl-ai "Create a Kubernetes deployment for FastAPI backend with 2 replicas, ClusterIP service on port 8000, liveness probe GET /health/ with initialDelaySeconds=15, readiness probe GET /health/, resource limits 500m CPU, 512Mi memory, requests 100m CPU, 128Mi memory, non-root user UID 1000, environment variables for DATABASE_URL, JWT_SECRET, OPENAI_API_KEY from Kubernetes secret named 'todo-secrets', security context with drop ALL capabilities." > /mnt/d/Hackathon/TODO-Evolution/kubernetes/backend-deployment.yaml

# Validate YAML
kubectl apply --dry-run=client -f /mnt/d/Hackathon/TODO-Evolution/kubernetes/backend-deployment.yaml
```

---

### Step 2.4: Generate MCP Server Deployment

```bash
kubectl-ai "Create a Kubernetes deployment for MCP server with 1 replica, ClusterIP service on port 8001, liveness probe GET /health/ with initialDelaySeconds=15, readiness probe GET /health/, resource limits 500m CPU, 512Mi memory, requests 100m CPU, 128Mi memory, non-root user UID 1000, environment variables for BACKEND_URL and OPENAI_API_KEY from secret 'todo-secrets', security context with allowPrivilegeEscalation=false." > /mnt/d/Hackathon/TODO-Evolution/kubernetes/mcp-deployment.yaml

# Validate YAML
kubectl apply --dry-run=client -f /mnt/d/Hackathon/TODO-Evolution/kubernetes/mcp-deployment.yaml
```

---

### Step 2.5: Generate Complete Helm Chart

```bash
kubectl-ai "Generate a complete Helm chart for the TODO Evolution application with frontend (Next.js), backend (FastAPI), and MCP server (Python). Include values.yaml for configurable replica counts, image tags, resource limits, and environment variables. Create templates for deployments, services, configmaps, and secrets. The chart should be production-ready with proper labels (app: todo-evolution, component, version, managed-by: helm), annotations, and security contexts. Include a NOTES.txt with deployment instructions." > /mnt/d/Hackathon/TODO-Evolution/helm-chart/

# Or use helm create (fallback)
helm create todo-evolution-chart

# Validate Helm chart
helm lint /mnt/d/Hackathon/TODO-Evolution/helm-chart/
```

---

### Step 2.6: Customize Helm Chart

Edit `/mnt/d/Hackathon/TODO-Evolution/helm-chart/values.yaml`:

```yaml
# Global settings
global:
  environment: development

# Frontend configuration
frontend:
  enabled: true
  replicas: 2
  image:
    repository: todo-frontend
    tag: 1.0.0
  service:
    type: LoadBalancer
    port: 80

# Backend configuration
backend:
  enabled: true
  replicas: 2
  image:
    repository: todo-backend
    tag: 1.0.0
  env:
    DATABASE_URL: postgresql+asyncpg://todo_user:todo123@postgres.default.svc.cluster.local:5432/todo
    JWT_SECRET: your-jwt-secret-here
    OPENAI_API_KEY: your-openai-api-key-here

# MCP Server configuration
mcpServer:
  enabled: true
  replicas: 1
  image:
    repository: todo-mcp-server
    tag: 1.0.0
```

---

## Phase 3: Deployment (Day 3-4 - 6 hours)

### Step 3.1: Create Kubernetes Secrets

```bash
# Create secret with database URL, JWT secret, and OpenAI API key
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql+asyncpg://todo_user:your-password@your-postgres-host:5432/todo" \
  --from-literal=JWT_SECRET="your-jwt-secret-min-32-chars" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-api-key"

# Verify secret
kubectl get secret todo-secrets -o yaml
```

---

### Step 3.2: Deploy PostgreSQL

**Option A: Use Neon (Managed PostgreSQL)**

Update DATABASE_URL in secret with your Neon connection string.

**Option B: Deploy PostgreSQL via Helm**

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --set auth.database=todo \
  --set auth.password=todo123 \
  --set auth.user=todo_user
```

---

### Step 3.3: Deploy Application with kubectl-ai

```bash
kubectl-ai "Deploy the todo-evolution Helm chart from /mnt/d/Hackathon/TODO-Evolution/helm-chart/ with release name 'todo-evolution' and namespace 'default'. Monitor the deployment and wait for all pods to be ready. If any pods fail, diagnose using logs and events, then provide remediation steps."
```

**Or use Helm directly**:

```bash
helm install todo-evolution /mnt/d/Hackathon/TODO-Evolution/helm-chart/ \
  --values /mnt/d/Hackathon/TODO-Evolution/helm-chart/values.yaml
```

---

### Step 3.4: Monitor Deployment

```bash
# Watch pods status
kubectl get pods -w

# Check services
kubectl get services

# Check deployment status
kubectl rollout status deployment/todo-evolution-frontend
kubectl rollout status deployment/todo-evolution-backend
kubectl rollout status deployment/todo-evolution-mcp-server
```

---

### Step 3.5: Troubleshooting Failing Pods

```bash
# If pods fail, use kubectl-ai
kubectl-ai "Check why the backend pods are crashing and suggest fixes based on logs and events."

# Manual troubleshooting
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

---

### Step 3.6: Access Frontend

```bash
# Get Minikube service URL
minikube service todo-evolution-frontend --url

# Or use tunnel
minikube tunnel
```

Open the URL in your browser (typically: http://localhost:3000)

---

## Phase 4: AI-Assisted Operations (Day 4 - 4 hours)

### Step 4.1: Cluster Health Analysis with kagent

```bash
kagent "Analyze the cluster health, resource utilization, and provide optimization recommendations. Include CPU usage, memory usage, pod health, and scaling recommendations." > cluster-analysis-report.md

# View report
cat cluster-analysis-report.md
```

---

### Step 4.2: Scale Backend Deployment

```bash
kubectl-ai "Scale the backend deployment to 3 replicas to handle increased load. Verify the new replicas are healthy and properly registered with the service."

# Or manually
kubectl scale deployment/todo-evolution-backend --replicas=3

# Verify
kubectl get pods -l app=todo-evolution,component=backend
```

---

### Step 4.3: Resource Optimization

```bash
kubectl-ai "Analyze resource usage across all deployments and suggest optimal resource requests and limits for CPU and memory based on actual consumption patterns from kubectl top pods."

# View current usage
kubectl top pods
```

---

### Step 4.4: Scale Down

```bash
kubectl-ai "Scale the backend deployment back to 2 replicas during low traffic period. Verify the excess replicas are terminated gracefully."

# Or manually
kubectl scale deployment/todo-evolution-backend --replicas=2
```

---

## Validation Checklist

### Environment Setup
- [ ] Docker Desktop 4.53+ installed with Gordon enabled
- [ ] Minikube v1.37.0+ running with 4 CPUs, 8GB RAM
- [ ] kubectl-ai installed and functional
- [ ] kagent installed and functional
- [ ] Helm CLI v3.15.0+ installed

### Containerization
- [ ] All Dockerfiles generated by Gordon
- [ ] All images built successfully (todo-frontend, todo-backend, todo-mcp-server)
- [ ] All images run as non-root user (UID 1000)
- [ ] All health endpoints responding
- [ ] All images loaded into Minikube

### Kubernetes Deployment
- [ ] All manifests generated by kubectl-ai
- [ ] Helm chart passes helm lint
- [ ] Secrets created (DATABASE_URL, JWT_SECRET, OPENAI_API_KEY)
- [ ] PostgreSQL deployed and accessible
- [ ] All pods Running and Ready (2 frontend, 2 backend, 1 MCP)

### Validation
- [ ] Frontend accessible via Minikube service URL
- [ ] Health endpoints responding for all services
- [ ] Inter-service communication working
- [ ] All pods have resource limits configured
- [ ] All pods have liveness and readiness probes
- [ ] All containers running as non-root user

### AI Tool Usage
- [ ] Gordon used for all Dockerfiles
- [ ] kubectl-ai used for all manifests
- [ ] kagent used for cluster analysis
- [ ] At least one scaling operation performed

---

## Common Issues and Solutions

### Issue 1: Gordon Not Available

**Symptoms**: `docker ai` command not found or not responding

**Solutions**:
1. Verify Docker Desktop is running
2. Check Gordon is enabled in Docker Desktop Settings > Beta features
3. Check your Docker Desktop tier (Gordon may be Pro/Team only)
4. Fallback: Use Claude Code to generate Dockerfiles manually

---

### Issue 2: Minikube Fails to Start

**Symptoms**: `minikube start` fails with resource or driver errors

**Solutions**:
1. Verify you have adequate resources (4 CPUs, 8GB RAM)
2. Stop Docker Desktop and restart with more resources allocated
3. Try different driver: `minikube start --driver=docker`
4. Check WSL2 kernel version on Windows
5. Fallback: Use kind (document deviation in completion report)

---

### Issue 3: Pods in CrashLoopBackOff

**Symptoms**: Pods restarting repeatedly

**Solutions**:
1. Check pod logs: `kubectl logs <pod-name>`
2. Describe pod for events: `kubectl describe pod <pod-name>`
3. Use kubectl-ai: `kubectl-ai "Check why pods are failing"`
4. Common causes:
   - Missing environment variables
   - Database connection failure
   - Missing dependencies in Dockerfile
   - Health check failing

---

### Issue 4: Service Not Accessible

**Symptoms**: Frontend URL not accessible

**Solutions**:
1. Check service type (should be LoadBalancer for frontend)
2. Verify pod selector matches pod labels
3. Run `minikube service <service-name> --url`
4. Use `minikube tunnel` for LoadBalancer support
5. Check firewall settings

---

### Issue 5: Database Connection Failed

**Symptoms**: Backend cannot connect to PostgreSQL

**Solutions**:
1. Verify DATABASE_URL in secret is correct
2. Check PostgreSQL pod is running: `kubectl get pods -l app=postgresql`
3. Verify service DNS: `kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup postgres.default.svc.cluster.local`
4. Test connection from pod: `kubectl exec -it <backend-pod> -- curl postgres://...`
5. Update secret if connection string is incorrect

---

## Cleanup

### Remove Deployment

```bash
# Uninstall Helm chart
helm uninstall todo-evolution

# Delete secrets
kubectl delete secret todo-secrets

# Delete PostgreSQL (if deployed via Helm)
helm uninstall postgres
```

### Stop Minikube

```bash
minikube stop
```

### Delete Minikube Cluster

```bash
minikube delete
```

---

## Next Steps

After completing this guide:

1. **Create completion report** documenting all AI tool usage
2. **Validate success criteria** from the plan
3. **Run `/sp.tasks`** to generate implementation tasks
4. **Execute tasks** from tasks.md following the plan

---

## References

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [kubectl-ai](https://github.com/kubectl-ai/kubectl-ai) (check official repo)
- [kagent](https://github.com/kagent-dev/kagent) (check official repo)
- [Neon PostgreSQL](https://neon.tech/)
- [Constitution](./.specify/memory/constitution.md)
- [Full Spec](./specs/1-phase-iv-kubernetes-aiops/spec.md)
- [Implementation Plan](./specs/1-phase-iv-kubernetes-aiops/plan.md)

---

**Quick Start Status**: ✅ COMPLETE
**Estimated Time to Complete**: 4 days (22 hours)
**Difficulty**: Intermediate (requires Kubernetes knowledge)
