# Microservice Deployment Blueprint
Version: 1.0.0
Type: kubernetes/deployment

## Description
Creates a secure, production-ready Kubernetes Deployment for microservices with resource limits, health probes, and security hardening.

## Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| service_name | string | Yes | - | Name of the service (lowercase, alphanumeric, max 63 chars) |
| image | string | Yes | - | Container image name |
| tag | string | Yes | - | Image tag with sha256 hash (format: {version}-sha256-{hash}) |
| port | integer | Yes | - | Container port number (1-65535) |
| replicas | integer | Yes | 2 | Number of pod replicas (1-10) |
| cpu_request | string | Yes | 100m | CPU request (e.g., "100m", "0.1") |
| cpu_limit | string | Yes | 500m | CPU limit (e.g., "500m", "0.5") |
| memory_request | string | Yes | 128Mi | Memory request (e.g., "128Mi", "128MiB") |
| memory_limit | string | Yes | 512Mi | Memory limit (e.g., "512Mi", "512MiB") |
| health_path | string | Yes | /health | Health check path (must start with /) |

## Template Structure
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{service_name}}-deployment
  labels:
    app.kubernetes.io/name: {{service_name}}
    app.kubernetes.io/version: "{{tag}}"
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: blueprint
    app.kubernetes.io/created-by: blueprint-instantiator
  annotations:
    blueprint.panaversity.org/source: "microservice-deployment.blueprint.md"
    blueprint.panaversity.org/version: "1.0.0"
spec:
  replicas: {{replicas}}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: {{service_name}}
      app.kubernetes.io/component: backend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{service_name}}
        app.kubernetes.io/version: "{{tag}}"
        app.kubernetes.io/component: backend
        app.kubernetes.io/part-of: todo-evolution
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        allowPrivilegeEscalation: false
      containers:
      - name: {{service_name}}
        image: {{image}}:{{tag}}
        ports:
        - containerPort: {{port}}
          name: http
          protocol: TCP
        resources:
          requests:
            cpu: {{cpu_request}}
            memory: {{memory_request}}
          limits:
            cpu: {{cpu_limit}}
            memory: {{memory_limit}}
        securityContext:
          runAsNonRoot: true
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL
        livenessProbe:
          httpGet:
            path: {{health_path}}
            port: {{port}}
            scheme: HTTP
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: {{port}}
            scheme: HTTP
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
      terminationGracePeriodSeconds: 60
```

## Validation Rules
1. **service_name**:
   - Must be lowercase alphanumeric with hyphens allowed
   - Must not start or end with hyphen
   - Maximum 63 characters
   - Must match Kubernetes DNS label requirements: `^[a-z0-9]([-a-z0-9]*[a-z0-9])?$`

2. **tag**:
   - Must include "sha256" substring
   - Must follow pattern: `{version}-sha256-{hash}`
   - Cannot be "latest" or other mutable tags
   - Example: "1.0.0-sha256-abc123def456"

3. **replicas**:
   - Must be integer between 1 and 10
   - For local development: maximum 3 recommended
   - For production: minimum 2 for high availability

4. **cpu_request/cpu_limit**:
   - Must follow Kubernetes resource format ("100m", "0.1", "1")
   - cpu_request must be <= cpu_limit
   - Minimum request: 100m, Maximum limit: 2000m for local
   - Recommended ratio: request is 50% of limit

5. **memory_request/memory_limit**:
   - Must follow Kubernetes resource format ("128Mi", "1Gi")
   - memory_request must be <= memory_limit
   - Minimum request: 64Mi, Maximum limit: 2Gi for local
   - Recommended ratio: request is 25-50% of limit

6. **health_path**:
   - Must start with "/"
   - Must be a valid HTTP path
   - Cannot be empty string
   - Recommended: "/health", "/api/health", or similar

7. **port**:
   - Must be integer between 1 and 65535
   - Should avoid well-known system ports (1-1023)
   - Recommended: Use ports above 3000 for applications