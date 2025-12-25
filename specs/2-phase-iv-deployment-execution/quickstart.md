# Quickstart Guide: Phase IV - Deployment Execution

**Feature**: 2-phase-iv-deployment-execution
**Created**: 2025-12-23
**Status**: Final
**Estimated Time**: 80 minutes

## Overview

This guide provides step-by-step instructions to deploy the Todo Chatbot application to a local Minikube Kubernetes cluster. Follow these phases in order to complete the deployment.

## Prerequisites

### System Requirements
- **CPU**: 4 cores minimum
- **RAM**: 8GB minimum
- **Disk**: 20GB free space
- **OS**: Windows 10/11, macOS, or Linux with WSL2
- **Internet**: Stable connection for downloads
- **Access**: Administrator/sudo privileges

### Required Accounts & Keys
- OpenAI API key for MCP server functionality
- PostgreSQL database (Neon recommended) or willingness to deploy locally

---

## Phase 0: Pre-Flight Check (5 minutes)

### Verify System Resources

**Linux/WSL2**:
```bash
# Check CPU cores
nproc

# Check available memory
free -h

# Check disk space
df -h
```

**Windows**:
- Open Task Manager > Performance
- Verify 4+ CPU cores and 8GB+ RAM available

**macOS**:
```bash
# Check CPU cores
sysctl -n hw.ncpu

# Check memory
sysctl -n hw.memsize
```

**Success Criteria**:
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 20GB+ free

---

## Phase 1: Tool Installation (30 minutes)

### Step 1.1: Install Docker Desktop with Gordon (10 minutes)

**Download Docker Desktop**:
- Windows: https://www.docker.com/products/docker-desktop/
- macOS: https://www.docker.com/products/docker-desktop/
- Linux: Use Docker Engine (Gordon not available on Linux)

**Installation**:
1. Run installer with admin privileges
2. Restart machine when prompted
3. Start Docker Desktop after installation

**Enable Gordon (Docker AI)**:
1. Open Docker Desktop
2. Go to **Settings** > **Beta Features**
3. Toggle **"Gordon"** to enabled
4. Restart Docker Desktop

**Verify Installation**:
```bash
# Check Docker version
docker --version
# Expected: Docker version 24.0.0 or later

# Verify Gordon (if available)
docker ai "What can you do?"
# Expected: Gordon responds with capabilities
```

**Troubleshooting**:
- If Gordon unavailable, proceed with standard Docker CLI
- Ensure virtualization is enabled in BIOS/UEFI
- Windows: Enable WSL2 feature if prompted

---

### Step 1.2: Install Minikube (10 minutes)

**Download Minikube**:

**Linux**:
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**macOS**:
```bash
brew install minikube
```

**Windows**:
```powershell
# Download from https://minikube.sigs.k8s.io/docs/start/
# Run installer as administrator
```

**Verify Installation**:
```bash
minikube version
# Expected: minikube version: v1.37.0 or later
```

**Start Minikube Cluster**:
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

**Enable Required Addons**:
```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

**Verify Cluster Status**:
```bash
# Check node status
kubectl get nodes
# Expected: STATUS = Ready

# List addons
minikube addons list
# Expected: ingress = enabled, metrics-server = enabled
```

**Troubleshooting**:
- If start fails: `minikube delete` then retry
- Ensure Docker Desktop is running before starting Minikube
- Check virtualization is enabled in BIOS/UEFI

---

### Step 1.3: Install Helm CLI (5 minutes)

**Download Helm**:

**Linux/macOS**:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Windows**:
```powershell
# Download from https://helm.sh/docs/intro/install/
# Add to PATH
```

**Verify Installation**:
```bash
helm version
# Expected: version.BuildInfo{Version:"v3.15.0" or later}
```

---

### Step 1.4: Install AI Tools (Optional, 5 minutes)

**kubectl-ai** (if available):
```bash
# Follow official installation from kubectl-ai repository
# Verify:
kubectl-ai "show cluster status"
```

**kagent** (if available):
```bash
# Follow official installation from kagent repository
# Verify:
kagent "analyze cluster health"
```

**Note**: If unavailable, standard kubectl commands will be used throughout this guide.

---

## Phase 2: Container Image Building (15 minutes)

### Step 2.1: Build Frontend Image (5 minutes)

```bash
# Navigate to frontend directory
cd frontend

# Build image with semantic version tag
docker build -t todo-frontend:1.0.0 .

# Verify image exists
docker images | grep todo-frontend
# Expected: todo-frontend 1.0.0
```

**Success Criteria**:
- Build completes with exit code 0
- Image appears in `docker images` list
- Image size < 500MB

---

### Step 2.2: Build Backend Image (5 minutes)

```bash
# Navigate to backend directory
cd ../backend

# Build image
docker build -t todo-backend:1.0.0 .

# Verify image exists
docker images | grep todo-backend
# Expected: todo-backend 1.0.0
```

**Success Criteria**:
- Build completes with exit code 0
- Image appears in `docker images` list
- Image size < 500MB

---

### Step 2.3: Build MCP Server Image (5 minutes)

```bash
# Navigate to MCP server directory
cd ../mcp_server

# Build image
docker build -t todo-mcp-server:1.0.0 .

# Verify image exists
docker images | grep todo-mcp-server
# Expected: todo-mcp-server 1.0.0
```

**Success Criteria**:
- Build completes with exit code 0
- Image appears in `docker images` list
- Image size < 500MB

---

### Step 2.4: Test Images Locally (Optional, 5 minutes)

```bash
# Test frontend (quick health check)
docker run --rm -p 3000:3000 todo-frontend:1.0.0 &
sleep 5
curl http://localhost:3000/api/health
# Expected: {"status":"healthy"}
pkill -f "todo-frontend"
```

---

## Phase 3: Minikube Deployment (20 minutes)

### Step 3.1: Load Images into Minikube (5 minutes)

```bash
# Set Docker environment to Minikube's daemon
eval $(minikube docker-env)

# Verify Docker is using Minikube daemon
docker context ls
# Current context should show minikube

# Load images (using docker save/load)
docker save todo-frontend:1.0.0 | minikube image load -
docker save todo-backend:1.0.0 | minikube image load -
docker save todo-mcp-server:1.0.0 | minikube image load -

# Verify images are in Minikube
minikube image ls | grep todo
# Expected: All three todo images listed
```

**Alternative Method** (if above fails):
```bash
# Build directly in Minikube context
eval $(minikube docker-env)

cd frontend
docker build -t todo-frontend:1.0.0 .

cd ../backend
docker build -t todo-backend:1.0.0 .

cd ../mcp_server
docker build -t todo-mcp-server:1.0.0 .
```

---

### Step 3.2: Create Kubernetes Secrets (5 minutes)

**Gather Required Values**:
- **DATABASE_URL**: PostgreSQL connection string (format: `postgresql+asyncpg://user:password@host:port/database`)
- **JWT_SECRET**: Minimum 32 characters (generate: `openssl rand -base64 32`)
- **OPENAI_API_KEY**: Your OpenAI API key (format: `sk-...`)

**Create Secret**:
```bash
# Create secret with all required values
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql+asyncpg://todo_user:password@host:5432/todo" \
  --from-literal=JWT_SECRET="$(openssl rand -base64 32)" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-api-key"

# Verify secret created
kubectl get secret todo-secrets
# Expected: NAME = todo-secrets, TYPE = Opaque

# Decode and verify values (optional)
kubectl get secret todo-secrets -o jsonpath='{.data}' | jq .
```

**Security Notes**:
- Never commit secrets to git
- Use strong, randomly generated JWT secrets
- Rotate credentials periodically

---

### Step 3.3: Deploy PostgreSQL (if using local, 5 minutes)

**Option A: Use Neon (Recommended)**
Skip this step. Use Neon connection string in DATABASE_URL secret.

**Option B: Deploy PostgreSQL via Helm**:
```bash
# Add Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install PostgreSQL
helm install postgres bitnami/postgresql \
  --set auth.database=todo \
  --set auth.password=todo123 \
  --set auth.user=todo_user

# Get PostgreSQL connection details
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default postgres-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
export POSTGRES_HOST=$(kubectl get nodes --namespace default -o jsonpath="{.items[0].status.addresses[0].address}")

# Update DATABASE_URL in secret
kubectl delete secret todo-secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql+asyncpg://todo_user:todo123@${POSTGRES_HOST}:5432/todo" \
  --from-literal=JWT_SECRET="$(openssl rand -base64 32)" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-api-key"
```

---

### Step 3.4: Install Helm Chart (5 minutes)

```bash
# Navigate to project root
cd /mnt/d/Hackathon/TODO-Evolution

# Verify chart exists
ls helm-chart/
# Expected: Chart.yaml, values.yaml, templates/

# Lint the chart
helm lint ./helm-chart/
# Expected: Configuration looks valid

# Install the chart
helm install todo-evolution ./helm-chart/

# Verify installation
helm list
# Expected: NAME = todo-evolution, STATUS = deployed

# Check deployment status
kubectl get deployments
# Expected: 3 deployments (frontend, backend, mcp-server)
```

**Installation Output**:
```
NAME: todo-evolution
LAST DEPLOYED: <date>
NAMESPACE: default
STATUS: deployed
REVISION: 1
```

---

## Phase 4: Verification (15 minutes)

### Step 4.1: Verify Pod Status (5 minutes)

```bash
# Watch pods starting
kubectl get pods --watch

# Wait until all pods show:
# STATUS = Running
# READY = 1/1 or 2/2
# Press Ctrl+C to exit watch mode
```

**Expected Output**:
```
NAME                                      READY   STATUS    RESTARTS   AGE
todo-evolution-frontend-xxxxxxxxxx-xxxxx  1/1     Running   0          2m
todo-evolution-frontend-xxxxxxxxxx-xxxxx  1/1     Running   0          2m
todo-evolution-backend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
todo-evolution-backend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
todo-evolution-mcp-server-xxxxxxxxxx-xxxx 1/1     Running   0          2m
```

**Troubleshooting**:
- If pods not Running: `kubectl describe pod <pod-name>`
- Check logs: `kubectl logs <pod-name>`
- Common issues: Image pull errors, secret missing, database unreachable

---

### Step 4.2: Verify Services (3 minutes)

```bash
# Check services
kubectl get services

# Expected output:
# NAME                          TYPE           EXTERNAL-IP   PORT(S)
# todo-evolution-frontend       LoadBalancer   <pending>     80:xxxxx/TCP
# todo-evolution-backend        ClusterIP      10.x.x.x      8000/TCP
# todo-evolution-mcp-server     ClusterIP      10.x.x.x      8001/TCP
```

---

### Step 4.3: Access Application (5 minutes)

**Terminal 1 - Start Minikube Tunnel**:
```bash
minikube tunnel
# Keep this terminal running
# May prompt for sudo password
```

**Terminal 2 - Get Frontend URL**:
```bash
# Get frontend service URL
minikube service todo-evolution-frontend --url

# Expected output:
# http://192.168.49.2:xxxxx

# Open in browser
# On Linux/WSL2: Use the URL directly
# On Windows/macOS: Open URL in browser
```

**Alternative: Port Forwarding**:
```bash
# Forward frontend port to localhost
kubectl port-forward svc/todo-evolution-frontend 8080:80

# Access at: http://localhost:8080
```

---

### Step 4.4: Test Application Features (5 minutes)

1. **Open Frontend**:
   - Navigate to Minikube service URL in browser
   - Expected: Todo application homepage loads

2. **Sign Up**:
   - Create new user account
   - Expected: Successful signup, redirected to dashboard

3. **Create Task**:
   - Click "Add Task"
   - Enter task title and description
   - Expected: Task appears in list

4. **Test AI Chat**:
   - Open AI chat widget
   - Ask: "What tasks do I have?"
   - Expected: AI responds with task list

5. **Verify Health Endpoints**:
   ```bash
   # Frontend health
   curl http://$(minikube service todo-evolution-frontend --url)/api/health

   # Backend health (port-forward first)
   kubectl port-forward svc/todo-evolution-backend 8000:8000
   curl http://localhost:8000/health/

   # MCP health (port-forward first)
   kubectl port-forward svc/todo-evolution-mcp-server 8001:8001
   curl http://localhost:8001/health
   ```

---

### Step 4.5: Verify Resource Usage (2 minutes)

```bash
# Check pod resource usage
kubectl top pods

# Expected output:
# NAME                              CPU(cores)   MEMORY(bytes)
# todo-evolution-frontend-xxxxx     50m          128Mi
# todo-evolution-backend-xxxxx      30m          96Mi
# todo-evolution-mcp-server-xxxxx   20m          64Mi

# Verify within limits:
# CPU < 500m
# Memory < 512Mi
```

---

## Phase 5: Troubleshooting Guide

### Common Issues and Solutions

**Issue 1: Pods Not Starting**
```bash
# Check pod status
kubectl get pods

# Describe pod for details
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Common fixes:
# - Image pull error: Ensure images loaded into Minikube
# - CrashLoopBackOff: Check application logs for errors
# - Pending state: Check resource availability
```

---

**Issue 2: Secret Not Found**
```bash
# Verify secret exists
kubectl get secret todo-secrets

# Recreate if missing
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=JWT_SECRET="..." \
  --from-literal=OPENAI_API_KEY="..."

# Restart pods to pick up new secret
kubectl rollout restart deployment todo-evolution-backend
kubectl rollout restart deployment todo-evolution-mcp-server
```

---

**Issue 3: Database Connection Failed**
```bash
# If using local PostgreSQL:
kubectl get pods -l app=postgresql
kubectl logs -l app=postgresql

# If using Neon:
# Verify DATABASE_URL format is correct
# Test connection from backend pod:
kubectl exec -it <backend-pod-name> -- nc -zv <db-host> 5432
```

---

**Issue 4: Minikube Tunnel Not Working**
```bash
# Ensure running with sudo
sudo minikube tunnel

# Alternative: Use port-forwarding
kubectl port-forward svc/todo-evolution-frontend 8080:80

# Access at: http://localhost:8080
```

---

**Issue 5: Frontend Cannot Reach Backend**
```bash
# Verify backend service exists
kubectl get svc todo-evolution-backend

# Check service endpoints
kubectl get endpoints todo-evolution-backend

# Test from frontend pod:
kubectl exec -it <frontend-pod-name> -- curl http://todo-evolution-backend:8000/health/
```

---

## Phase 6: Cleanup

### Stop Deployment (Keep Data)

```bash
# Stop Minikube (keeps cluster state)
minikube stop

# Stop tunnel
# Press Ctrl+C in tunnel terminal
```

### Remove Deployment (Delete Data)

```bash
# Uninstall Helm release
helm uninstall todo-evolution

# Delete secrets
kubectl delete secret todo-secrets

# Delete PostgreSQL (if deployed locally)
helm uninstall postgres

# Stop Minikube
minikube stop
```

### Complete Cleanup

```bash
# Delete Minikube cluster (deletes all data)
minikube delete

# Remove built images (optional)
docker rmi todo-frontend:1.0.0
docker rmi todo-backend:1.0.0
docker rmi todo-mcp-server:1.0.0
```

---

## Success Criteria Checklist

- [ ] All tools installed (Docker Desktop, Minikube, Helm)
- [ ] All 3 container images built successfully
- [ ] All images loaded into Minikube
- [ ] Kubernetes secrets created
- [ ] Helm chart installed without errors
- [ ] All 5 pods Running and Ready (2 frontend, 2 backend, 1 MCP)
- [ ] Frontend accessible via Minikube service URL
- [ ] Application features working (signup, CRUD, AI chat)
- [ ] Health endpoints responding for all services
- [ ] Resource usage within limits (CPU < 500m, Memory < 512Mi)

---

## Next Steps

After successful deployment:

1. **Explore Application**: Test all features and AI chatbot functionality
2. **Monitor Resources**: Use `kubectl top pods` to monitor usage
3. **View Logs**: `kubectl logs -f <pod-name>` to watch application logs
4. **Scale Up**: `kubectl scale deployment todo-evolution-backend --replicas=3`
5. **Development**: Edit code, rebuild images, redeploy with `helm upgrade`

---

## Additional Resources

- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Docker Documentation**: https://docs.docker.com/

---

**Status**: ✅ COMPLETE
**Estimated Completion Time**: 80 minutes
**Difficulty**: Intermediate

---

**Constitutional Compliance**: All deployments follow Phase IV Constitutional requirements:
- Non-root user execution (UID 1000/1001)
- Resource limits enforced (CPU: 100m-500m, Memory: 128Mi-512Mi)
- Health probes configured (liveness and readiness)
- Semantic versioning (1.0.0, no 'latest' tags)
- Standard Kubernetes labels (app, component, version, managed-by)
