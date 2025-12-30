# Minikube Deployment Quickstart

**Feature**: Minikube Helm Deployment Update (011-minikube-helm-deploy)
**Last Updated**: 2025-12-30
**Prerequisites**: Minikube, Docker Desktop, kubectl, Helm

## Overview

This guide provides step-by-step instructions to deploy the TODO Evolution application to a local Minikube Kubernetes cluster using Helm charts. The application consists of three microservices:
- **Frontend**: Next.js 16 application (port 3000)
- **Backend**: FastAPI application (port 8000)
- **MCP Server**: Python service for AI tools (port 8001)

## Prerequisites

### Required Tools

1. **Minikube** (v1.25+ recommended)
   ```bash
   minikube version
   ```

2. **Docker Desktop** (v4.0+)
   - Ensure Docker daemon is running
   - WSL2 backend enabled on Windows

3. **kubectl** (v1.25+)
   ```bash
   kubectl version --client
   ```

4. **Helm** (v3.0+)
   ```bash
   helm version
   ```

### System Requirements

- **CPUs**: 4 cores minimum (8 recommended)
- **Memory**: 8 GB RAM minimum (16 GB recommended)
- **Disk**: 20 GB free space
- **Platform**: Windows WSL2, macOS, or Linux

### Database Access

- Neon PostgreSQL cloud database connection string
- Valid JWT_SECRET for authentication
- OpenAI API key or Gemini API key for AI features

## Deployment Steps

### Step 1: Start Minikube Cluster

Start Minikube with sufficient resources for the application:

```bash
minikube start --cpus=4 --memory=8192 --disk-size=20g
```

**Expected Output**:
```
😄  minikube v1.x.x on Microsoft Windows
✨  Using the docker driver
📌  Using Docker Desktop driver
🔥  Creating docker container ...
🐳  Preparing Kubernetes v1.x.x on Docker 20.10.x ...
🔎  Verifying Kubernetes components...
🌟  Enabled addons: default-storageclass, storage-provisioner
🏄  Done! kubectl is now configured to use "minikube" cluster
```

**Verify Minikube Status**:
```bash
minikube status
```

**Enable Required Addons**:
```bash
minikube addons enable ingress
minikube addons enable metrics-server
```

---

### Step 2: Point Docker Daemon to Minikube

Configure Docker CLI to use Minikube's internal Docker daemon:

**Windows PowerShell**:
```powershell
minikube docker-env | Invoke-Expression
```

**Linux/macOS**:
```bash
eval $(minikube docker-env)
```

**Verify Docker Environment**:
```bash
docker ps
```

> **Note**: This command must be run in each new terminal session. Consider adding to your PowerShell profile.

---

### Step 3: Build Docker Images

Build Docker images for all three services with the new version tags:

#### 3.1 Build Frontend Image

```bash
docker build -t todo-frontend:1.0.5 ./frontend
```

**Expected Build Time**: 3-5 minutes (first build), 1-2 minutes (subsequent builds)

#### 3.2 Build Backend Image

```bash
docker build -t todo-backend:2.0.2 ./backend
```

**Expected Build Time**: 2-3 minutes (first build), 30-60 seconds (subsequent builds)

#### 3.3 Build MCP Server Image

```bash
docker build -t todo-mcp-server:1.0.2 ./mcp_server
```

**Expected Build Time**: 2-3 minutes (first build), 30-60 seconds (subsequent builds)

#### 3.4 Verify Images

```bash
docker images | grep todo
```

**Expected Output**:
```
todo-frontend   1.0.5   <image-id>   <size>   <time>
todo-backend    2.0.2   <image-id>   <size>   <time>
todo-mcp-server 1.0.2   <image-id>   <size>   <time>
```

---

### Step 4: Update Helm Chart

Edit `helm-chart/values.yaml` to update image tags and configuration:

```yaml
# Frontend configuration
frontend:
  image:
    repository: todo-frontend
    tag: "1.0.5"  # Updated from 1.0.4

# Backend configuration
backend:
  image:
    repository: todo-backend
    tag: "2.0.2"  # Updated from 2.0.1

# MCP Server configuration
mcpServer:
  image:
    repository: todo-mcp-server
    tag: "1.0.2"  # Updated from 1.0.1
```

**Verify Secrets Configuration**:

Ensure `secrets` section in `values.yaml` has valid credentials:

```yaml
secrets:
  databaseURL: "postgresql+asyncpg://user:pass@host/dbname?ssl=require"
  jwtSecret: "your-secure-jwt-secret-min-32-chars"
  openaiAPIKey: "sk-..."  # Or placeholder if not using OpenAI
  geminiAPIKey: "AIzaSy..."  # Your Gemini API key
```

---

### Step 5: Deploy with Helm

#### 5.1 First-Time Installation

If this is the first deployment:

```bash
helm install todo-evolution ./helm-chart
```

**Expected Output**:
```
NAME: todo-evolution
LAST DEPLOYED: Tue Dec 30 12:00:00 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

#### 5.2 Upgrade Existing Release

If updating an existing deployment:

```bash
helm upgrade todo-evolution ./helm-chart
```

**Expected Output**:
```
Release "todo-evolution" has been upgraded
STATUS: deployed
```

#### 5.3 Verify Deployment

```bash
kubectl get pods
kubectl get services
```

**Expected Output**:
```
NAME                                          READY   STATUS    RESTARTS   AGE
todo-evolution-frontend-xxxxxxxxxx-xxxxx      1/1     Running   0          1m
todo-evolution-frontend-xxxxxxxxxx-xxxxx      1/1     Running   0          1m
todo-evolution-backend-xxxxxxxxxx-xxxxx       1/1     Running   0          1m
todo-evolution-backend-xxxxxxxxxx-xxxxx       1/1     Running   0          1m
todo-evolution-mcp-server-xxxxxxxxxx-xxxxx    1/1     Running   0          1m
```

---

### Step 6: Monitor Pod Startup

Watch pods come up:

```bash
kubectl get pods -w
```

**Pod States**:
- `Pending`: Pod is being scheduled
- `ContainerCreating`: Docker image is being pulled/started
- `Running`: Pod is successfully running (should see 1/1 READY)

**Troubleshoot Failed Pods**:
```bash
# View pod logs
kubectl logs <pod-name>

# Describe pod (check events)
kubectl describe pod <pod-name>
```

---

### Step 7: Access Application

#### 7.1 Frontend Access

**Option A: Minikube Service Command (Recommended)**

```bash
minikube service todo-evolution-frontend --url
```

**Option B: Minikube Tunnel (for LoadBalancer)**

In a separate terminal (keep running):
```powershell
minikube tunnel
```

Then access frontend at: `http://localhost:<port>`

**Option C: NodePort Access**

```bash
kubectl get svc todo-evolution-frontend
minikube service todo-evolution-frontend
```

This will open the frontend in your default browser.

#### 7.2 Backend Access

```bash
minikube service todo-evolution-backend --url
```

Backend API will be accessible at: `http://<minikube-ip>:<node-port>`

**Test Backend Health**:
```bash
curl http://<minikube-ip>:<node-port>/health/
```

Expected response: `{"status": "healthy"}`

#### 7.3 MCP Server Access

MCP server is ClusterIP only (internal access):

```bash
# Port forward to local machine
kubectl port-forward deployment/todo-evolution-mcp-server 8001:8001
```

Then access at: `http://localhost:8001`

---

### Step 8: Verify Deployment

#### 8.1 Check Pod Status

```bash
kubectl get pods
```

All pods should show `Running` status with `1/1 READY`.

#### 8.2 Test Frontend

1. Open frontend URL in browser
2. Sign up with a new account
3. Create a test task
4. Verify task appears in list

#### 8.3 Test Backend API

```bash
# Get backend URL
BACKEND_URL=$(minikube service todo-evolution-backend --url)

# Test health endpoint
curl $BACKEND_URL/health/

# Test API docs
curl $BACKEND_URL/docs
```

#### 8.4 Check Environment Variables

```bash
# Check frontend environment
kubectl exec -it deployment/todo-evolution-frontend -- env | grep NEXT_PUBLIC

# Check backend environment
kubectl exec -it deployment/todo-evolution-backend -- env | grep DATABASE_URL
```

## Troubleshooting

### Issue: Minikube Fails to Start

**Symptoms**: Error starting Minikube, hypervisor errors

**Solutions**:
1. Check WSL2 is enabled: `wsl --list --verbose`
2. Try different driver: `minikube start --driver=docker`
3. Delete old cluster: `minikube delete && minikube start`
4. Increase WSL2 memory: Edit `%USERPROFILE%\.wslconfig`:
   ```ini
   [wsl2]
   memory=16GB
   ```

### Issue: ImagePullBackOff Errors

**Symptoms**: Pods stuck in `ImagePullBackOff` state

**Solutions**:
1. Verify Docker environment: `minikube docker-env | Invoke-Expression`
2. Check images exist: `docker images | grep todo`
3. Verify image tags match values.yaml
4. Rebuild images: `docker build -t todo-frontend:1.0.5 ./frontend`

### Issue: Pods Not Starting (CrashLoopBackOff)

**Symptoms**: Pods restart repeatedly

**Solutions**:
1. Check pod logs: `kubectl logs <pod-name>`
2. Check environment variables: `kubectl exec <pod> -- env`
3. Verify database connection string is correct
4. Check resource limits: `kubectl describe pod <pod-name>`

### Issue: Frontend Cannot Reach Backend

**Symptoms**: Frontend shows network errors or CORS errors

**Solutions**:
1. Verify backend service is running: `kubectl get svc`
2. Check CORS_ORIGINS in backend values.yaml
3. Verify frontend BACKEND_URL environment variable
4. Test backend connectivity from frontend pod:
   ```bash
   kubectl exec -it deployment/todo-evolution-frontend -- curl http://todo-evolution-backend:8000/health/
   ```

### Issue: Database Connection Failures

**Symptoms**: Backend logs show database connection errors

**Solutions**:
1. Verify DATABASE_URL is correct in secrets
2. Test connection from local machine:
   ```bash
   psql "postgresql+asyncpg://user:pass@host/dbname?ssl=require"
   ```
3. Check firewall rules
4. Verify asyncpg driver is installed in backend image

### Issue: Minikube Service Tunnel Not Working

**Symptoms**: `minikube tunnel` exits or doesn't work

**Solutions**:
1. Run PowerShell as Administrator
2. Check no other processes using ports
3. Try NodePort instead: `minikube service <name> --url`

## Clean Up

### Stop Services (Keep Data)

```bash
helm uninstall todo-evolution
```

### Stop Minikube

```bash
minikube stop
```

### Delete Cluster (Remove All Data)

```bash
minikube delete
```

### Remove Docker Images

```bash
docker rmi todo-frontend:1.0.5 todo-backend:2.0.2 todo-mcp-server:1.0.2
```

## Advanced Usage

### Scale Replicas

```bash
# Scale frontend to 3 replicas
kubectl scale deployment/todo-evolution-frontend --replicas=3

# Scale backend to 3 replicas
kubectl scale deployment/todo-evolution-backend --replicas=3
```

### View Logs

```bash
# Follow all logs
kubectl logs -f deployment/todo-evolution-frontend

# View logs for specific pod
kubectl logs <pod-name>

# View logs for all containers in pod
kubectl logs <pod-name> --all-containers=true
```

### Execute Commands in Pods

```bash
# Open shell in pod
kubectl exec -it <pod-name> -- /bin/sh

# Run single command
kubectl exec <pod-name> -- env | grep DATABASE_URL
```

### Port Forwarding

```bash
# Forward backend to local port 8000
kubectl port-forward deployment/todo-evolution-backend 8000:8000

# Forward MCP server to local port 8001
kubectl port-forward deployment/todo-evolution-mcp-server 8001:8001
```

## Next Steps

1. **Monitor Application**: Use `kubectl get pods -w` to monitor pod health
2. **Test Features**: Verify all application features work correctly
3. **Check Logs**: Review logs for any errors or warnings
4. **Access Dashboard**: Run `minikube dashboard` for Kubernetes UI
5. **Review Resources**: Run `kubectl top pods` to monitor resource usage

## Support

- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Project Issues**: https://github.com/iamKhan79690/TODO-EVOLUTION/issues

---

**Quickstart Status**: ✅ Complete

**Deployment Time**: ~10-15 minutes (first time), ~5 minutes (subsequent deployments)

**Success Criteria**: All pods Running, frontend accessible, API responding
