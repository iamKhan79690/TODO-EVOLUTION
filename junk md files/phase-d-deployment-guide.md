# Phase D: Kubernetes Deployment - Complete Implementation Guide

**Status**: 🚧 REQUIRES ENVIRONMENT SETUP
**Prerequisites**: Docker Desktop, Minikube, Helm CLI
**Target Environment**: Local Minikube Cluster

## Current Environment Status

❌ **Docker**: Not running
❌ **Minikube**: Cluster not started
❌ **Helm**: CLI not available

*Note: This guide provides the complete deployment process that would be executed once the environment is properly set up.*

---

## Phase D.1: Environment Setup and Prerequisites

### Step 1: Start Docker Desktop
```powershell
# Start Docker Desktop (Windows)
# Or ensure Docker service is running (Linux)
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 2: Initialize Minikube Cluster
```powershell
# Start Minikube with recommended resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Verify cluster status
minikube status
kubectl cluster-info
```

### Step 3: Install Helm CLI (if not installed)
```powershell
# Download Helm (Windows)
curl https://get.helm.sh/helm-v3.15.0-windows-amd64.zip -o helm.zip
Expand-Archive helm.zip -DestinationPath .
Move-Item windows-amd64\helm.exe C:\ProgramData\chocolatey\bin\

# Verify installation
helm version
```

## Phase D.2: Secrets Configuration

### Step 4: Configure Application Secrets
```powershell
# Encode your actual values
$DB_URL = "postgresql://user:password@your-neon-host:5432/todo"
$JWT_SECRET = "your-super-secret-jwt-key-here"
$OPENAI_KEY = "sk-your-actual-openai-api-key"

# Encode to base64
$DB_ENCODED = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($DB_URL))
$JWT_ENCODED = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($JWT_SECRET))
$OPENAI_ENCODED = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($OPENAI_KEY))

Write-Host "DATABASE_URL: $DB_ENCODED"
Write-Host "JWT_SECRET: $JWT_ENCODED"
Write-Host "OPENAI_API_KEY: $OPENAI_ENCODED"
```

### Step 5: Create Kubernetes Secrets
```yaml
# Apply this YAML after replacing encoded values
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
data:
  DATABASE_URL: <base64-encoded-db-url>
  JWT_SECRET: <base64-encoded-jwt-secret>
  OPENAI_API_KEY: <base64-encoded-openai-key>
```

```powershell
# Apply the secrets
kubectl apply -f todo-evolution-chart/secrets.yaml
```

## Phase D.3: Helm Chart Deployment

### Step 6: Deploy with Helm
```powershell
# Navigate to project root
cd /mnt/d/Hackathon/TODO-Evolution

# Install the Helm chart
helm install todo-evolution ./todo-evolution-chart \
  --namespace default \
  --create-namespace \
  --timeout 10m \
  --wait

# Expected output:
# NAME: todo-evolution
# LAST DEPLOYED: Tue Dec 22 13:00:00 2025
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# TEST SUITE: None
```

### Step 7: Monitor Pod Startup
```powershell
# Watch pods come up (interactive mode)
kubectl get pods --watch

# Expected progression:
# NAME                                           READY   STATUS              RESTARTS   AGE
# todo-evolution-backend-5f6d7c8d9c-abcde         0/1     ContainerCreating   0          5s
# todo-evolution-frontend-7a8b9c0d1e-fghij         0/1     ContainerCreating   0          5s
# todo-evolution-mcp-server-3b4c5d6e7f-klmno       0/1     ContainerCreating   0          5s

# Then:
# NAME                                           READY   STATUS    RESTARTS   AGE
# todo-evolution-backend-5f6d7c8d9c-abcde         1/1     Running   0          30s
# todo-evolution-frontend-7a8b9c0d1e-fghij         1/1     Running   0          35s
# todo-evolution-mcp-server-3b4c5d6e7f-klmno       1/1     Running   0          40s
```

## Phase D.4: Deployment Verification

### Step 8: Verify All Resources
```powershell
# Check all resources in the namespace
kubectl get all

# Expected output:
# NAME                                               READY   STATUS    RESTARTS   AGE
# pod/todo-evolution-backend-5f6d7c8d9c-abcde         1/1     Running   0          2m
# pod/todo-evolution-frontend-7a8b9c0d1e-fghij         1/1     Running   0          2m
# pod/todo-evolution-mcp-server-3b4c5d6e7f-klmno       1/1     Running   0          2m

# NAME                                          TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
# service/todo-evolution-backend                 ClusterIP      10.96.123.45    <none>        8000/TCP       2m
# service/todo-evolution-frontend                LoadBalancer   10.96.234.56    <pending>     80:30123/TCP   2m
# service/todo-evolution-mcp-server               ClusterIP      10.96.345.67    <none>        8001/TCP       2m
# service/kubernetes                              ClusterIP      10.96.0.1       <none>        443/TCP        45m

# NAME                                          READY   UP-TO-DATE   AVAILABLE   AGE
# deployment.apps/todo-evolution-backend         2/2     2            2           2m
# deployment.apps/todo-evolution-frontend        2/2     2            2           2m
# deployment.apps/todo-evolution-mcp-server       1/1     1            1           2m

# NAME                                                    DESIRED   CURRENT   READY   AGE
# replicaset.apps/todo-evolution-backend-5f6d7c8d9c         2         2         2       2m
# replicaset.apps/todo-evolution-frontend-7a8b9c0d1e         2         2         2       2m
# replicaset.apps/todo-evolution-mcp-server-3b4c5d6e7f       1         1         1       2m
```

### Step 9: Check Pod Details
```powershell
# Get detailed pod information
kubectl get pods -o wide

# Expected output showing node assignment:
# NAME                                           READY   STATUS    RESTARTS   AGE   IP          NODE           NOMINATED NODE   READINESS GATES
# todo-evolution-backend-5f6d7c8d9c-abcde         1/1     Running   0          3m    172.17.0.5   minikube       <none>           <none>
# todo-evolution-backend-5f6d7c8d9c-fghij         1/1     Running   0          3m    172.17.0.6   minikube       <none>           <none>
# todo-evolution-frontend-7a8b9c0d1e-klmno         1/1     Running   0          3m    172.17.0.7   minikube       <none>           <none>
# todo-evolution-frontend-7a8b9c0d1e-mnopq         1/1     Running   0          3m    172.17.0.8   minikube       <none>           <none>
# todo-evolution-mcp-server-3b4c5d6e7f-rstuv       1/1     Running   0          3m    172.17.0.9   minikube       <none>           <none>
```

## Phase D.5: Application Logs Verification

### Step 10: Check Application Logs
```powershell
# Frontend logs
kubectl logs -l app.kubernetes.io/name=todo-frontend --tail=50

# Expected frontend logs:
# > todo-frontend@1.0.0 start
# > next start
#
# Ready on http://0.0.0.0:3000
# [2025-12-22T13:00:00.000Z] INFO: Starting Next.js application
# [2025-12-22T13:00:01.000Z] INFO: API configured: http://todo-evolution-backend:8000

# Backend logs
kubectl logs -l app.kubernetes.io/name=todo-backend --tail=50

# Expected backend logs:
# [2025-12-22 13:00:00] INFO:     Starting FastAPI application
# [2025-12-22 13:00:00] INFO:     Application startup complete.
# [2025-12-22 13:00:00] INFO:     Database connected: postgresql://todo_user:***@postgresql:5432/todo
# [2025-12-22 13:00:01] INFO:     Uvicorn running on http://0.0.0.0:8000

# MCP server logs
kubectl logs -l app.kubernetes.io/name=todo-mcp-server --tail=50

# Expected MCP logs:
# [2025-12-22 13:00:00] INFO:     Starting MCP Server
# [2025-12-22 13:00:00] INFO:     Backend URL: http://todo-evolution-backend:8000
# [2025-12-22 13:00:01] INFO:     OpenAI model: gpt-4
# [2025-12-22 13:00:02] INFO:     MCP Server running on http://0.0.0.0:8001
```

## Phase D.6: Application Accessibility Testing

### Step 11: Access Frontend Application
```powershell
# Get frontend service URL (LoadBalancer type)
minikube service todo-evolution-frontend --url

# Expected output:
# http://192.168.49.2:30123

# Open in browser
start http://192.168.49.2:30123
```

### Step 12: Test Backend API
```powershell
# Check backend service details
kubectl get service todo-evolution-backend

# Port-forward backend to local machine
kubectl port-forward service/todo-evolution-backend 8000:8000 &
# Press Ctrl+C to stop when done

# Test backend health endpoint (in another terminal)
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-12-22T13:00:00Z", "service": "todo-backend"}

# Test FastAPI docs
curl http://localhost:8000/docs
# Should return FastAPI interactive documentation HTML
```

### Step 13: Test MCP Server
```powershell
# Port-forward MCP server
kubectl port-forward service/todo-evolution-mcp-server 8001:8001 &

# Test MCP health
curl http://localhost:8001/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-12-22T13:00:00Z", "service": "mcp-server"}
```

## Phase D.7: Inter-Service Connectivity Testing

### Step 14: Test Service Discovery
```powershell
# Test DNS resolution within cluster
kubectl run test-pod --image=busybox --rm -it -- /bin/sh

# Inside the pod, test service resolution:
# nslookup todo-evolution-backend
# nslookup todo-evolution-frontend
# nslookup todo-evolution-mcp-server

# Test connectivity:
# wget -qO- http://todo-evolution-backend:8000/health
# wget -qO- http://todo-evolution-mcp-server:8001/health
```

### Step 15: Test Application Functionality
```powershell
# Test CRUD operations via API
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Expected response:
# {"message": "User created successfully", "user_id": "123"}

# Test authentication
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Expected response:
# {"access_token": "eyJ...", "token_type": "bearer"}
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: Pods stuck in Pending state
```powershell
# Check pod events
kubectl describe pod <pod-name>

# Common causes and solutions:
# - Insufficient resources: Increase Minikube memory/CPU
# - Image pull issues: Check image names and tags
# - Storage issues: Verify available disk space
```

#### Issue 2: Pods stuck in ContainerCreating state
```powershell
# Check pod logs
kubectl logs <pod-name>

# Common causes:
# - Image pull failures: Check image registry access
# - Volume mounting issues: Check PVC and storage classes
# - Security context issues: Check runAsUser permissions
```

#### Issue 3: Service not accessible
```powershell
# Check service endpoints
kubectl get endpoints

# Debug service connectivity
kubectl run debug --image=busybox --rm -it -- /bin/sh
# Inside pod: wget -qO- http://service-name:port

# Check for network policies blocking traffic
kubectl get networkpolicy
```

#### Issue 4: Frontend can't reach backend
```powershell
# Check environment variables in frontend pod
kubectl exec deployment/todo-evolution-frontend -- env | grep API

# Verify backend service is accessible from frontend
kubectl exec deployment/todo-evolution-frontend -- wget -qO- http://todo-evolution-backend:8000/health
```

## Validation Checklist

### ✅ Deployment Validation
- [ ] All pods are running (2 frontend, 2 backend, 1 MCP)
- [ ] All services are created and have proper endpoints
- [ ] LoadBalancer service has external IP (Minikube tunnel)
- [ ] Health checks are passing for all services
- [ ] No significant errors in pod logs

### ✅ Connectivity Validation
- [ ] Frontend accessible via browser
- [ ] Backend API accessible via curl
- [ ] MCP server accessible via curl
- [ ] Inter-service communication working
- [ ] DNS resolution working within cluster

### ✅ Functionality Validation
- [ ] User registration works
- [ ] User authentication works
- [ ] CRUD operations work
- [ ] AI chat functionality works
- [ ] Error handling working properly

## Cleanup Commands

```powershell
# Uninstall Helm release
helm uninstall todo-evolution

# Delete secrets
kubectl delete secret todo-secrets

# Stop Minikube (optional)
minikube stop

# Reset Minikube (complete cleanup)
minikube delete
```

---

## Environment Setup Requirements

To execute this deployment guide, ensure you have:

1. **Docker Desktop** installed and running
2. **Minikube** installed with sufficient resources
3. **Helm CLI** v3.x installed
4. **kubectl** configured to communicate with Minikube
5. **Application secrets** (Database URL, JWT secret, OpenAI API key)

Once the environment is properly set up, follow this guide step-by-step to successfully deploy the TODO Evolution application to Kubernetes.