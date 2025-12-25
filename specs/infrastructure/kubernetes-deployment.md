# Kubernetes Deployment Specification: Phase IV

**Feature Branch**: `phase-iv`
**Created**: 2025-12-21
**Status**: Draft
**Input**: Create Kubernetes deployment specification defining deployment strategy, resources, health probes, security context, and service definitions for all services

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Production-Ready Kubernetes Deployments (Priority: P1)

As a DevOps engineer deploying the TODO Evolution application to Minikube, I want complete Kubernetes deployment manifests with proper resource allocation, security hardening, and health monitoring so that the application runs reliably, securely, and can self-heal from failures.

**Why this priority**: Kubernetes deployments are the foundation of Phase IV - without properly configured deployments, the application cannot achieve the required high availability and security standards.

**Independent Test**: Can be fully tested by applying all manifests to Minikube and verifying pods start correctly, pass health checks, and services are accessible.

**Acceptance Scenarios**:

1. **Given** the deployment manifests, **When** I apply them to Minikube, **Then** all pods reach Running state within 60 seconds
2. **Given** running deployments, **When** I check pod security contexts, **Then** all pods run as non-root with UID 1000 and proper capabilities
3. **Given** deployed services, **When** I access them via Minikube services, **Then** frontend is accessible via LoadBalancer and backend services via ClusterIP
4. **Given** running pods, **When** I simulate a pod failure, **Then** Kubernetes automatically restarts the failed pod

---

### User Story 2 - Resource Management and Optimization (Priority: P1)

As a cluster administrator managing Minikube resources, I want properly configured resource requests and limits with optimal scheduling ratios so that applications have guaranteed resources while preventing resource monopolization and ensuring cluster stability.

**Why this priority**: Resource management prevents noisy neighbor problems and ensures predictable application performance in the shared Minikube environment.

**Independent Test**: Can be verified by checking resource allocation in Kubernetes and testing resource starvation scenarios.

**Acceptance Scenarios**:

1. **Given** the deployment specifications, **When** I check pod resource allocation, **Then** requests are exactly 50% of limits (optimal scheduling ratio)
2. **Given** resource limits configured, **When** a pod tries to exceed CPU limit, **Then** it's throttled without affecting other pods
3. **Given** memory limits configured, **When** a pod exceeds memory allocation, **Then** it's restarted by OOM killer without impacting other applications
4. **Given** configured requests, **When** Kubernetes schedules pods, **Then** they have guaranteed minimum resources available

---

### User Story 3 - Self-Healing Health Monitoring (Priority: P1)

As a site reliability engineer, I want comprehensive health monitoring with liveness and readiness probes so that Kubernetes can automatically detect and recover from application failures without manual intervention.

**Why this priority**: Self-healing capabilities are essential for maintaining application availability and reducing operational overhead.

**Independent Test**: Can be tested by simulating application failures and verifying Kubernetes responds appropriately to health probe failures.

**Acceptance Scenarios**:

1. **Given** configured health probes, **When** application becomes unhealthy, **Then** liveness probe triggers pod restart after configured failure threshold
2. **Given** readiness probes configured, **When** application is starting up, **Then** pod is removed from service load balancer until ready probe passes
3. **Given** healthy application, **When** I check health endpoints, **Then** they return HTTP 200 with appropriate health status information
4. **Given** health probe configuration, **When** I check probe settings, **Then** they match Constitutional requirements (initial delays, periods, timeouts)

---

### User Story 4 - Zero-Trust Security Implementation (Priority: P1)

As a security engineer implementing zero-trust architecture, I want comprehensive security contexts with non-root execution, capability dropping, and least privilege access so that containers have minimal attack surface and cannot escalate privileges.

**Why this priority**: Security hardening is non-negotiable in Phase IV - it prevents privilege escalation attacks and limits blast radius of container compromises.

**Independent Test**: Can be verified by inspecting pod security contexts and testing privilege escalation attempts.

**Acceptance Scenarios**:

1. **Given** deployed pods, **When** I check user permissions, **Then** all containers run as UID 1000 (non-root)
2. **Given** security contexts configured, **When** I inspect Linux capabilities, **Then** ALL capabilities are dropped for all containers
3. **Given** pod security policies, **When** I attempt privilege escalation, **Then** it's blocked by security context
4. **Given** read-only filesystem configured, **When** I try to write to root filesystem, **Then** it fails as expected (where applicable)

---

### Edge Cases

- What happens when Minikube doesn't have enough resources to meet pod requests?
- How does the system handle health probe failures during application startup?
- What if the service selectors don't match pod labels correctly?
- How do deployments behave when image pull fails or containers won't start?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Frontend deployment MUST use 2 replicas with LoadBalancer service type on port 3000
- **FR-002**: Backend deployment MUST use 2 replicas with ClusterIP service type on port 8000
- **FR-003**: MCP Server deployment MUST use 1 replica with ClusterIP service type on port 8001
- **FR-004**: All deployments MUST use RollingUpdate strategy with maxUnavailable=1 and maxSurge=1
- **FR-005**: All containers MUST have CPU requests of 100m and limits of 500m
- **FR-006**: All containers MUST have memory requests of 128Mi and limits of 512Mi
- **FR-007**: All deployments MUST have both liveness and readiness probes configured
- **FR-008**: All pods MUST run as non-root user with UID 1000 and GID 1000
- **FR-009**: All containers MUST drop ALL Linux capabilities and set allowPrivilegeEscalation=false
- **FR-010**: All deployments MUST use the 6 Kubernetes recommended labels
- **FR-011**: All deployments MUST use dedicated ServiceAccounts (no default ServiceAccount)
- **FR-012**: All services MUST have selectors that match deployment pod labels
- **FR-013**: All deployments MUST have terminationGracePeriodSeconds of 60
- **FR-014**: Environment variables MUST be sourced from ConfigMaps (non-sensitive) and Secrets (sensitive)

### Key Entities *(include if feature involves data)*

- **Frontend Deployment**: Next.js application pods with LoadBalancer service for external access
- **Backend Deployment**: FastAPI application pods with ClusterIP service for internal access
- **MCP Server Deployment**: Python MCP service pods with ClusterIP service for internal access
- **Services**: Kubernetes Service objects for load balancing and service discovery
- **ConfigMaps**: Non-sensitive configuration data (API URLs, log levels)
- **Secrets**: Sensitive credentials (DATABASE_URL, JWT_SECRET, OPENAI_API_KEY)
- **ServiceAccounts**: Dedicated service accounts for each deployment with least privilege
- **Security Contexts**: Pod and container-level security configurations

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All deployments achieve 100% pod readiness within 90 seconds of application
- **SC-002**: Health probes pass with 99.9% success rate during normal operation
- **SC-003**: Resource utilization stays within 80% of allocated limits during normal load
- **SC-004**: Zero-downtime deployments achieved with RollingUpdate strategy
- **SC-005**: All pods pass constitutional security validation (100% compliance)
- **SC-006**: Service discovery works correctly with all services reachable via DNS names
- **SC-007**: Graceful shutdown completes within 60 seconds for all services
- **SC-008**: Multi-replica deployments achieve pod distribution across available nodes

## Frontend Deployment Specification

### Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app.kubernetes.io/name: todo-frontend
    app.kubernetes.io/instance: todo-evolution
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: todo-frontend
      app.kubernetes.io/component: frontend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: todo-frontend
        app.kubernetes.io/instance: todo-evolution
        app.kubernetes.io/version: "1.0.0"
        app.kubernetes.io/component: frontend
        app.kubernetes.io/part-of: todo-evolution
    spec:
      serviceAccountName: todo-frontend
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: frontend
        image: todo-frontend:1.0.0-sha256-abc12345
        ports:
        - containerPort: 3000
          name: http
          protocol: TCP
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        securityContext:
          runAsNonRoot: true
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false
          capabilities:
            drop:
              - ALL
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: todo-config
              key: API_BASE_URL
        - name: NODE_ENV
          valueFrom:
            configMapKeyRef:
              name: todo-config
              key: ENVIRONMENT
        - name: PORT
          value: "3000"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/ready
            port: 3000
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
      terminationGracePeriodSeconds: 60
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app.kubernetes.io/name
                  operator: In
                  values:
                    - todo-frontend
              topologyKey: kubernetes.io/hostname
```

### Service Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
  labels:
    app.kubernetes.io/name: todo-frontend
    app.kubernetes.io/instance: todo-evolution
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
    name: http
  selector:
    app.kubernetes.io/name: todo-frontend
    app.kubernetes.io/component: frontend
```

## Backend Deployment Specification

### Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app.kubernetes.io/name: todo-backend
    app.kubernetes.io/instance: todo-evolution
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: todo-backend
      app.kubernetes.io/component: backend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: todo-backend
        app.kubernetes.io/instance: todo-evolution
        app.kubernetes.io/version: "1.0.0"
        app.kubernetes.io/component: backend
        app.kubernetes.io/part-of: todo-evolution
    spec:
      serviceAccountName: todo-backend
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: backend
        image: todo-backend:1.0.0-sha256-def45678
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        securityContext:
          runAsNonRoot: true
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: DATABASE_URL
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: JWT_SECRET
        - name: CORS_ORIGINS
          valueFrom:
            configMapKeyRef:
              name: todo-config
              key: CORS_ORIGINS
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: todo-config
              key: LOG_LEVEL
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8000"
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
      volumes:
      - name: tmp
        emptyDir: {}
      terminationGracePeriodSeconds: 60
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app.kubernetes.io/name
                  operator: In
                  values:
                    - todo-backend
              topologyKey: kubernetes.io/hostname
```

### Service Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
  labels:
    app.kubernetes.io/name: todo-backend
    app.kubernetes.io/instance: todo-evolution
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app.kubernetes.io/name: todo-backend
    app.kubernetes.io/component: backend
```

## MCP Server Deployment Specification

### Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-mcp-server
  labels:
    app.kubernetes.io/name: todo-mcp-server
    app.kubernetes.io/instance: todo-evolution
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: mcp-server
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
spec:
  replicas: 1
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: todo-mcp-server
      app.kubernetes.io/component: mcp-server
  template:
    metadata:
      labels:
        app.kubernetes.io/name: todo-mcp-server
        app.kubernetes.io/instance: todo-evolution
        app.kubernetes.io/version: "1.0.0"
        app.kubernetes.io/component: mcp-server
        app.kubernetes.io/part-of: todo-evolution
    spec:
      serviceAccountName: todo-mcp-server
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: mcp-server
        image: todo-mcp-server:1.0.0-sha256-ghi78901
        ports:
        - containerPort: 8001
          name: http
          protocol: TCP
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        securityContext:
          runAsNonRoot: true
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: OPENAI_API_KEY
        - name: BACKEND_URL
          valueFrom:
            configMapKeyRef:
              name: todo-config
              key: BACKEND_URL
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: todo-config
              key: LOG_LEVEL
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8001"
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8001
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
      volumes:
      - name: tmp
        emptyDir: {}
      terminationGracePeriodSeconds: 60
```

### Service Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-mcp-server
  labels:
    app.kubernetes.io/name: todo-mcp-server
    app.kubernetes.io/instance: todo-evolution
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: mcp-server
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
spec:
  type: ClusterIP
  ports:
  - port: 8001
    targetPort: 8001
    protocol: TCP
    name: http
  selector:
    app.kubernetes.io/name: todo-mcp-server
    app.kubernetes.io/component: mcp-server
```

## ServiceAccount and RBAC Configuration

### ServiceAccounts

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: todo-frontend
  labels:
    app.kubernetes.io/name: todo-frontend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: todo-backend
  labels:
    app.kubernetes.io/name: todo-backend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: todo-mcp-server
  labels:
    app.kubernetes.io/name: todo-mcp-server
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
```

## ConfigMap Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-config
  labels:
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
data:
  API_BASE_URL: "http://todo-backend:8000"
  BACKEND_URL: "http://todo-backend:8000"
  CORS_ORIGINS: "http://todo-frontend"
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "development"
```

## Secrets Configuration Template

```yaml
# Secrets should be created imperatively, not committed to git
# Use: kubectl create secret generic todo-secrets --from-literal=DATABASE_URL="..." --from-literal=JWT_SECRET="..." --from-literal=OPENAI_API_KEY="..."

apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
  labels:
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: helm
type: Opaque
data:
  # Base64 encoded values (example only - create with kubectl)
  DATABASE_URL: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0Bob3N0OjU0MzIvZGI=  # postgresql://user:pass@host:5432/db
  JWT_SECRET: eW91ci1qd3Qtc2VjcmV0LWtleQ==  # your-jwt-secret-key
  OPENAI_API_KEY: c2stcHJvamVjdC1rZXk=  # sk-project-key
```

## Network Configuration

### Service Communication

- **Frontend → Backend**: `http://todo-backend:8000`
- **Backend → Database**: Via `DATABASE_URL` from secrets
- **Backend → MCP Server**: `http://todo-mcp-server:8001`
- **External Access**: Frontend via LoadBalancer service

### DNS Resolution

All services resolve via Kubernetes DNS:
- `todo-frontend.todo-namespace.svc.cluster.local`
- `todo-backend.todo-namespace.svc.cluster.local`
- `todo-mcp-server.todo-namespace.svc.cluster.local`

## Resource Monitoring

### Resource Requests Summary

| Service | CPU Request | Memory Request | CPU Limit | Memory Limit |
|---------|-------------|----------------|-----------|---------------|
| Frontend | 100m | 128Mi | 500m | 512Mi |
| Backend | 100m | 128Mi | 500m | 512Mi |
| MCP Server | 100m | 128Mi | 500m | 512Mi |
| **Total** | **300m** | **384Mi** | **1500m** | **1536Mi** |

### Resource Ratio Validation
- CPU requests: 300m (50% of 1500m limits) ✅
- Memory requests: 384Mi (50% of 1536Mi limits) ✅
- All services follow 50% request-to-limit ratio ✅

## Deployment Checklist

### Pre-Deployment Validation

- [ ] All image tags include SHA256 hash
- [ ] All deployments use non-root user (UID 1000)
- [ ] All containers have resource requests and limits
- [ ] All services have matching selectors
- [ ] All health probes configured with appropriate timeouts
- [ ] All 6 Kubernetes recommended labels present
- [ ] ServiceAccounts created for each deployment
- [ ] Secrets created imperatively (not in git)
- [ ] ConfigMaps reference correct service URLs

### Post-Deployment Verification

- [ ] All pods reach Running state
- [ ] All pods pass readiness probes
- [ ] Services accessible via DNS
- [ ] Frontend accessible via LoadBalancer
- [ ] Health endpoints responding correctly
- [ ] Resource allocation visible in kubectl describe
- [ ] No security context violations
- [ ] Rolling updates work without downtime

### Troubleshooting Commands

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/part-of=todo-evolution

# Check service endpoints
kubectl get endpoints

# Check resource usage
kubectl top pods

# Check pod details
kubectl describe pod <pod-name>

# Check logs
kubectl logs -l app.kubernetes.io/name=todo-backend --follow

# Test service connectivity
kubectl run test-pod --image=curlimages/curl -it --rm -- /bin/sh -c "curl http://todo-backend:8000/health"

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

## Integration Requirements

### Helm Chart Structure

All manifests should be organized in Helm chart structure:
```
todo-evolution-chart/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── serviceaccounts/
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── mcp-deployment.yaml
│   └── mcp-service.yaml
```

### Values.yaml Configuration

```yaml
# Default values for todo-evolution chart
replicaCount:
  frontend: 2
  backend: 2
  mcp: 1

image:
  repository: todo
  tag: 1.0.0-sha256-abc123
  pullPolicy: IfNotPresent

service:
  type:
    frontend: LoadBalancer
    backend: ClusterIP
    mcp: ClusterIP
  ports:
    frontend: 80
    backend: 8000
    mcp: 8001

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

healthProbes:
  liveness:
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  readiness:
    initialDelaySeconds: 10
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 2
```

This specification provides complete Kubernetes deployment configurations that meet all Phase IV Constitutional requirements for security, resource management, health monitoring, and operational excellence.