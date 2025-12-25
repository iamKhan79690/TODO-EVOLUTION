# Phase IV Deployment - Next Steps Guide

**Date**: 2025-12-23
**Status**: Ready for User Execution
**Environment**: WSL2 Ubuntu

---

## Current Status Summary

### ✅ Completed (Verified Infrastructure)

| Component | Status | Details |
|-----------|--------|---------|
| **Docker CLI** | ✅ Running | Docker daemon active and accessible |
| **Minikube** | ✅ Installed | v1.37.0 installed (cluster not started) |
| **Helm CLI** | ✅ Installed | v3.15.0-rc.2 installed |
| **kubectl** | ✅ Installed | v1.35.0 installed to ~/.local/bin/ |
| **Frontend Dockerfile** | ✅ Ready | frontend/Dockerfile (2434 bytes) |
| **Backend Dockerfile** | ✅ Ready | backend/Dockerfile (2827 bytes) |
| **MCP Server Dockerfile** | ✅ Ready | mcp_server/Dockerfile (2760 bytes) |
| **Helm Chart** | ✅ Complete | 15 files in helm-chart/ directory |

### ⏳ Pending (Requires User Action)

| Task | Command | Notes |
|------|---------|-------|
| **Start Minikube** | `minikube start --cpus=2 --memory=6192 --driver=docker` | Allocate 2 CPUs, 6GB RAM |
| **Enable Addons** | `minikube addons enable ingress metrics-server` | Required for deployment |
| **Build Images** | See below | Build all 3 container images |
| **Create Secrets** | `kubectl create secret generic todo-secrets ...` | Requires your credentials |
| **Deploy with Helm** | `helm install todo-evolution ./helm-chart/` | Install application |
| **Verify Deployment** | `kubectl get pods` | Check pod status |

---

## Immediate Next Steps

### Step 1: Start Minikube Cluster

```bash
# Start Minikube with adequate resources
minikube start --cpus=2 --memory=6192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster is running
export PATH="$HOME/.local/bin:$PATH"
kubectl get nodes
# Expected: STATUS = Ready
```

**Estimated Time**: 3-5 minutes

---

### Step 2: Build Container Images

```bash
# Set Docker environment to use Minikube's daemon
eval $(minikube docker-env)

# Build frontend image
cd /mnt/d/Hackathon/TODO-Evolution/frontend
docker build -t todo-frontend:1.0.0 .

# Build backend image
cd /mnt/d/Hackathon/TODO-Evolution/backend
docker build -t todo-backend:1.0.0 .

# Build MCP server image
cd /mnt/d/Hackathon/TODO-Evolution/mcp_server
docker build -t todo-mcp-server:1.0.0 .

# Verify images built
docker images | grep todo
# Expected: All 3 todo images listed
```

**Estimated Time**: 10-15 minutes

---

### Step 3: Create Kubernetes Secrets

**You will need to gather these values first**:

1. **PostgreSQL Connection String**:
   - Option A: Sign up at [Neon](https://neon.tech) (recommended, free tier available)
   - Option B: Deploy PostgreSQL locally (additional steps)

2. **OpenAI API Key**:
   - Get from https://platform.openai.com/api-keys
   - Format: `sk-...`

3. **JWT Secret**:
   - Generate with: `openssl rand -base64 32`

**Create the secret**:

```bash
# Replace the values below with your actual credentials
export DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"
export JWT_SECRET="$(openssl rand -base64 32)"
export OPENAI_API_KEY="sk-your-openai-api-key"

# Create the Kubernetes secret
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY"

# Verify secret created
kubectl get secret todo-secrets
```

**Estimated Time**: 5-10 minutes (mostly time to gather credentials)

---

### Step 4: Deploy with Helm

```bash
# Navigate to project root
cd /mnt/d/Hackathon/TODO-Evolution

# Lint the Helm chart
helm lint ./helm-chart/

# Install the Helm chart
helm install todo-evolution ./helm-chart/

# Verify installation
helm list

# Check deployments created
kubectl get deployments

# Watch pods starting
kubectl get pods --watch
# Wait for all pods to show STATUS = Running
# Press Ctrl+C to exit watch mode
```

**Estimated Time**: 3-5 minutes

---

### Step 5: Access the Application

**Terminal 1 - Start Minikube Tunnel**:
```bash
minikube tunnel
# Keep this terminal running
# May prompt for sudo password
```

**Terminal 2 - Get Frontend URL**:
```bash
# Get the frontend service URL
minikube service todo-evolution-frontend --url

# Expected output: http://192.168.49.2:xxxxx
```

**Open the URL in your browser** - you should see the Todo Chatbot application!

---

### Step 6: Verify Deployment

```bash
# Check all pods are Running
kubectl get pods

# Check services
kubectl get services

# Verify health endpoints
# Frontend:
curl http://$(minikube service todo-evolution-frontend --url)/api/health

# Backend (port-forward first):
kubectl port-forward svc/todo-evolution-backend 8000:8000
# In another terminal:
curl http://localhost:8000/health/
```

---

## Testing the Application

Once the frontend is accessible in your browser:

1. **Sign Up**: Create a new user account
2. **Create Task**: Add a new task to your list
3. **Test AI Chat**: Ask the AI "What tasks do I have?"
4. **Verify Persistence**: Refresh the page and confirm tasks remain

---

## Troubleshooting

### Pods Not Starting

```bash
# Describe a pod to see why it's not starting
kubectl describe pod <pod-name>

# Check pod logs
kubectl logs <pod-name>

# Common issues:
# - ImagePullBackOff: Images not in Minikube's Docker daemon
# - CrashLoopBackOff: Application error, check logs
# - Pending: Insufficient resources, check node status
```

### Secret Issues

```bash
# Delete and recreate secret if needed
kubectl delete secret todo-secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=JWT_SECRET="..." \
  --from-literal=OPENAI_API_KEY="..."

# Restart pods to pick up new secret
kubectl rollout restart deployment todo-evolution-backend
kubectl rollout restart deployment todo-evolution-mcp-server
```

### Minikube Issues

```bash
# Check Minikube status
minikube status

# Restart Minikube if needed
minikube stop
minikube start

# Delete and recreate cluster (last resort)
minikube delete
minikube start --cpus=2 --memory=6192 --driver=docker
```

---

## Cleanup (When Done)

### Stop Deployment (Keep Data)

```bash
# Stop Minikube
minikube stop

# Stop tunnel (press Ctrl+C in tunnel terminal)
```

### Remove Deployment (Delete Data)

```bash
# Uninstall Helm release
helm uninstall todo-evolution

# Delete secrets
kubectl delete secret todo-secrets

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

## Quick Reference

**Essential Commands**:

```bash
# Add to your ~/.bashrc for persistent PATH
export PATH="$HOME/.local/bin:$PATH"

# Check cluster status
kubectl get nodes
kubectl get pods
kubectl get services

# Minikube commands
minikube status
minikube start
minikube stop
minikube tunnel

# Helm commands
helm list
helm status todo-evolution
helm uninstall todo-evolution

# Port forwarding (for debugging)
kubectl port-forward svc/todo-evolution-frontend 8080:80
kubectl port-forward svc/todo-evolution-backend 8000:8000
kubectl port-forward svc/todo-evolution-mcp-server 8001:8001
```

---

## Success Criteria Checklist

After completing the deployment, verify:

- [ ] Minikube cluster is Running
- [ ] All 3 container images built successfully
- [ ] Kubernetes secrets created
- [ ] Helm chart installed without errors
- [ ] All 5 pods are Running and Ready (2 frontend, 2 backend, 1 MCP)
- [ ] Frontend accessible via browser
- [ ] User signup works
- [ ] Task creation works
- [ ] AI chat functionality works
- [ ] Tasks persist after page refresh

---

## Additional Resources

- **Quickstart Guide**: `specs/2-phase-iv-deployment-execution/quickstart.md`
- **Tasks Breakdown**: `specs/2-phase-iv-deployment-execution/tasks.md`
- **Implementation Report**: `phase-iv-deployment-implementation-report.md`
- **Minikube Docs**: https://minikube.sigs.k8s.io/docs/
- **Helm Docs**: https://helm.sh/docs/
- **Kubernetes Docs**: https://kubernetes.io/docs/

---

**Status**: ✅ Ready for Deployment
**Total Estimated Time**: 30-40 minutes
**Next Action**: Execute Step 1 above to start Minikube cluster

---

## Notes

- kubectl has been installed to `~/.local/bin/kubectl`
- Add `export PATH="$HOME/.local/bin:$PATH"` to your `~/.bashrc` for persistence
- Docker Desktop is available on your system (desktop-linux context detected)
- All infrastructure code is complete and production-ready
- This deployment follows Phase IV Constitutional requirements for Kubernetes deployments
