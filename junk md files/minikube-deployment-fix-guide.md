# Minikube Deployment Fix - Deployment Guide

This guide provides step-by-step instructions to redeploy your TODO Evolution application with the fixes applied.

## Summary of Changes

### 1. Fixed Environment Variable Mismatches
- Added `BACKEND_URL` for server-side API proxy
- Set `NEXT_PUBLIC_API_URL` to `/api/proxy` for client-side calls

### 2. Added CORS Configuration
- Added `CORS_ORIGINS` to backend environment variables

### 3. Created Next.js API Proxy
- New API proxy route at `/api/proxy/[...path]`
- Proxies all backend requests server-side
- Solves browser-to-Kubernetes connectivity issue

### 4. Backend Service Type
- Already configured as `NodePort` for external access (if needed)

---

## Pre-Deployment Checklist

### 1. Check Minikube Status

```bash
# Check if Minikube is running
minikube status

# If not running, start Minikube
minikube start --cpus=4 --memory=8192

# Enable addons (if not already enabled)
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Point Docker to Minikube

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify Docker is using Minikube
docker ps
```

---

## Step-by-Step Deployment

### Step 1: Uninstall Existing Helm Release (if deployed)

```bash
# List existing releases
helm list

# Uninstall existing release
helm uninstall todo-evolution

# Wait for pods to be deleted
kubectl get pods -w
```

### Step 2: Rebuild Docker Images (if code changed)

Since we added a new API proxy route, you need to rebuild the frontend image:

```bash
# Navigate to project root
cd /mnt/d/Hackathon/TODO-Evolution

# Build frontend image
docker build -t todo-frontend:1.0.0 ./frontend

# Build backend image (if you made changes)
docker build -t todo-backend:1.0.0 ./backend

# Build MCP server image (if you made changes)
docker build -t todo-mcp-server:1.0.0 ./mcp_server

# Verify images were built
docker images | grep todo-
```

### Step 3: Update Secrets (if needed)

```bash
# Check if secrets exist
kubectl get secrets

# Delete old secrets (to recreate with new values)
kubectl delete secret todo-secrets

# Create secrets from values (update with your actual values)
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://todo_user:your_password@your_database_host:5432/todo' \
  --from-literal=JWT_SECRET='your-secure-jwt-secret-min-32-chars-long' \
  --from-literal=OPENAI_API_KEY='sk-your-openai-api-key'

# Verify secrets were created
kubectl describe secret todo-secrets
```

### Step 4: Deploy with Helm

```bash
# Navigate to Helm chart directory
cd /mnt/d/Hackathon/TODO-Evolution/helm-chart

# Install the Helm chart
helm install todo-evolution . --namespace default

# Watch the deployment
kubectl get pods -w
```

### Step 5: Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Expected output:
# NAME                                          READY   STATUS    RESTARTS   AGE
# todo-evolution-backend-xxxxxxxxxx-xxxxx       1/1     Running   0          2m
# todo-evolution-frontend-xxxxxxxxxx-xxxxx      1/1     Running   0          2m
# todo-evolution-mcp-server-xxxxxxxxxx-xxxxx    1/1     Running   0          2m

# Check services
kubectl get services

# Expected output:
# NAME                          TYPE           PORT(S)          AGE
# todo-evolution-backend        NodePort       8000:30800/TCP   2m
# todo-evolution-frontend       LoadBalancer   80:xxxxx/TCP    2m
# todo-evolution-mcp-server     ClusterIP      8001/TCP        2m

# Check endpoints (backend should have endpoints)
kubectl get endpoints todo-evolution-backend
```

### Step 6: Access the Application

```bash
# Get the frontend URL
minikube service todo-evolution-frontend --url

# Output example: http://192.168.49.2:31768

# Or get the NodePort for frontend
kubectl get svc todo-evolution-frontend
```

Then open the URL in your browser.

---

## Testing the Fixes

### Test 1: API Proxy Health Check

```bash
# Get frontend URL
FRONTEND_URL=$(minikube service todo-evolution-frontend --url)
echo "Frontend URL: $FRONTEND_URL"

# Test API proxy health endpoint
curl "$FRONTEND_URL/api/proxy/health/"

# Expected output:
# {"status":"healthy","database":"connected","timestamp":"...","version":"1.0.0"}
```

### Test 2: Backend Direct Access (from within cluster)

```bash
# Port-forward to backend service
kubectl port-forward svc/todo-evolution-backend 8000:8000

# In another terminal, test backend directly
curl http://localhost:8000/health/

# Expected output:
# {"status":"healthy","database":"connected","timestamp":"...","version":"1.0.0"}
```

### Test 3: Test from Frontend Pod

```bash
# Get frontend pod name
FRONTEND_POD=$(kubectl get pod -l component=frontend -o jsonpath='{.items[0].metadata.name}')

# Exec into frontend pod
kubectl exec -it $FRONTEND_POD -- sh

# Inside the pod, test backend connectivity
wget -qO- http://todo-evolution-backend:8000/health/

# Expected output: JSON health check response

# Exit the pod
exit
```

### Test 4: Browser Test

1. Open the frontend URL in your browser
2. Open Browser DevTools (F12)
3. Go to the Network tab
4. Try to sign in or create a task
5. Check that API calls go to `/api/proxy/*` instead of directly to backend
6. Verify requests are successful (200 status codes)

---

## Debugging Commands

### Check Pod Logs

```bash
# Frontend logs
kubectl logs -l component=frontend --tail=50 -f

# Backend logs
kubectl logs -l component=backend --tail=50 -f

# MCP server logs
kubectl logs -l component=mcp-server --tail=50 -f
```

### Describe Resources

```bash
# Describe frontend pod
kubectl describe pod -l component=frontend

# Describe backend service
kubectl describe svc todo-evolution-backend

# Describe ingress (if using)
kubectl describe ingress todo-evolution
```

### Check Environment Variables

```bash
# Check frontend environment variables
kubectl exec -it $(kubectl get pod -l component=frontend -o jsonpath='{.items[0].metadata.name}') -- env | grep -E "BACKEND_URL|NEXT_PUBLIC_API_URL"

# Expected output:
# BACKEND_URL=http://todo-evolution-backend:8000
# NEXT_PUBLIC_API_URL=/api/proxy

# Check backend environment variables
kubectl exec -it $(kubectl get pod -l component=backend -o jsonpath='{.items[0].metadata.name}') -- env | grep -E "CORS_ORIGINS|DATABASE_URL|JWT_SECRET"
```

### Test Network Connectivity

```bash
# From frontend pod, test backend DNS resolution
kubectl exec -it $(kubectl get pod -l component=frontend -o jsonpath='{.items[0].metadata.name}') -- nslookup todo-evolution-backend

# From frontend pod, test backend port connectivity
kubectl exec -it $(kubectl get pod -l component=frontend -o jsonpath='{.items[0].metadata.name}') -- nc -zv todo-evolution-backend 8000
```

---

## Troubleshooting

### Issue: "backend not running" error in browser

**Possible Causes:**
1. Backend pods are not running
2. Backend service has no endpoints
3. API proxy is not working
4. Environment variables not set correctly

**Solutions:**

```bash
# Check backend pods
kubectl get pods -l component=backend

# If pods are not running, check logs
kubectl logs -l component=backend

# If pods are CrashLoopBackOff, describe pod to see events
kubectl describe pod -l component=backend

# Check if backend service has endpoints
kubectl get endpoints todo-evolution-backend

# If no endpoints, check pod labels match service selector
kubectl get pods -l component=backend --show-labels
kubectl describe svc todo-evolution-backend
```

### Issue: CORS errors in browser console

**Solution:**

```bash
# Check backend CORS configuration
kubectl exec -it $(kubectl get pod -l component=backend -o jsonpath='{.items[0].metadata.name}') -- env | grep CORS_ORIGINS

# Should show: CORS_ORIGINS=http://localhost:3000,http://localhost,http://192.168.49.2

# If not set, update values.yaml and redeploy
helm upgrade todo-evolution ./helm-chart
```

### Issue: API proxy returns 502 error

**Solution:**

```bash
# Check if backend is accessible from frontend pod
kubectl exec -it $(kubectl get pod -l component=frontend -o jsonpath='{.items[0].metadata.name}') -- wget -qO- http://todo-evolution-backend:8000/health/

# If this fails, backend service is not reachable
# Check backend service and endpoints
kubectl get svc todo-evolution-backend
kubectl get endpoints todo-evolution-backend

# Check if backend pods are ready
kubectl get pods -l component=backend
```

### Issue: Images not found (ImagePullBackOff)

**Solution:**

```bash
# Point Docker to Minikube daemon
eval $(minikube docker-env)

# Verify images exist
docker images | grep todo-

# If images don't exist, rebuild them
docker build -t todo-frontend:1.0.0 ./frontend
docker build -t todo-backend:1.0.0 ./backend
docker build -t todo-mcp-server:1.0.0 ./mcp_server

# Restart pods
kubectl rollout restart deployment todo-evolution-frontend
kubectl rollout restart deployment todo-evolution-backend
kubectl rollout restart deployment todo-evolution-mcp-server
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│                   (Your Machine)                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ HTTP Request
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Minikube Kubernetes Cluster                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Frontend Service (LoadBalancer)              │  │
│  │         Port: 80 (NodePort: 31768)                   │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Frontend Pods (Next.js)                        │  │
│  │       - NEXT_PUBLIC_API_URL=/api/proxy               │  │
│  │       - BACKEND_URL=http://todo-evolution-backend:8000│ │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     │ Server-side proxy request              │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       API Proxy Route (/api/proxy/[...path])        │  │
│  │       Server-side code can access K8s services       │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     │ HTTP Request                           │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Backend Service (NodePort)                      │  │
│  │      Port: 8000 (NodePort: 30800)                   │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Backend Pods (FastAPI)                         │  │
│  │       - CORS_ORIGINS configured                      │  │
│  │       - DATABASE_URL from secrets                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      MCP Server Service (ClusterIP)                  │  │
│  │      Port: 8001                                      │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                       │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       MCP Server Pods                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

After following this guide, you should be able to:

✅ Access the frontend from your browser
✅ Sign in / Sign up without errors
✅ Create, read, update, and delete tasks
✅ No "backend not running" errors
✅ API calls visible in browser Network tab going to `/api/proxy/*`
✅ All pods in `Running` state
✅ All services have endpoints

---

## Next Steps

If you encounter any issues:

1. Check the logs: `kubectl logs -l component=<frontend|backend>`
2. Describe the pod: `kubectl describe pod <pod-name>`
3. Test connectivity: `kubectl exec -it <pod> -- wget -qO- http://todo-evolution-backend:8000/health/`
4. Check environment variables: `kubectl exec -it <pod> -- env`

For additional help, refer to:
- Project Constitution: `.specify/memory/constitution.md`
- PHR: `history/prompts/general/002-minikube-deployment-debugging.general.prompt.md`
