# Blueprint Template Guide

This guide provides detailed specifications for creating blueprint templates that work with the blueprint-instantiator skill.

## Blueprint File Structure

Every blueprint file must follow this structure:

```markdown
# {Blueprint Name}
Version: {semantic-version}
Type: kubernetes/{resource-type}

## Description
{Brief description of what this blueprint creates}

## Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| service_name | string | Yes | - | Name of the service (lowercase, alphanumeric) |
| image | string | Yes | - | Container image name |
| tag | string | Yes | - | Image tag (must include sha256 hash) |
| port | integer | Yes | - | Container port number |
| replicas | integer | Yes | - | Number of pod replicas (>= 1) |
| cpu_request | string | Yes | - | CPU request (e.g., "100m") |
| cpu_limit | string | Yes | - | CPU limit (e.g., "500m") |
| memory_request | string | Yes | - | Memory request (e.g., "128Mi") |
| memory_limit | string | Yes | - | Memory limit (e.g., "512Mi") |
| health_path | string | Yes | - | Health check path (must start with /) |

## Template Structure
```yaml
# Kubernetes YAML with {{parameter}} placeholders
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{service_name}}-deployment
  labels:
    app.kubernetes.io/name: {{service_name}}
    app.kubernetes.io/version: "{{tag}}"
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: todo-evolution
    app.kubernetes.io/managed-by: blueprint
    app.kubernetes.io/created-by: blueprint-instantiator
spec:
  replicas: {{replicas}}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{service_name}}
      app.kubernetes.io/component: frontend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{service_name}}
        app.kubernetes.io/version: "{{tag}}"
        app.kubernetes.io/component: frontend
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
        resources:
          requests:
            cpu: {{cpu_request}}
            memory: {{memory_request}}
          limits:
            cpu: {{cpu_limit}}
            memory: {{memory_limit}}
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
              - ALL
        livenessProbe:
          httpGet:
            path: {{health_path}}
            port: {{port}}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: {{port}}
          initialDelaySeconds: 10
          periodSeconds: 5
```

## Validation Rules
{List of validation rules for parameters}

### Standard Validation Rules

1. **service_name**:
   - Must be lowercase alphanumeric
   - Must not start or end with hyphen
   - Maximum 63 characters
   - Must match Kubernetes DNS label requirements

2. **tag**:
   - Must include "sha256" substring
   - Must follow pattern: {version}-sha256-{hash}
   - Cannot be "latest" or other mutable tags

3. **replicas**:
   - Must be integer >= 1
   - Maximum 10 for local development

4. **cpu_request/cpu_limit**:
   - Must follow Kubernetes resource format
   - cpu_request must be <= cpu_limit
   - Minimum request: 100m, Maximum limit: 2000m

5. **memory_request/memory_limit**:
   - Must follow Kubernetes resource format
   - memory_request must be <= memory_limit
   - Minimum request: 64Mi, Maximum limit: 2Gi

6. **health_path**:
   - Must start with "/"
   - Must be a valid HTTP path
   - Cannot be empty
```

## Blueprint Types

### 1. microservice-deployment.blueprint.md
Creates a Kubernetes Deployment with:
- Security hardening (non-root user)
- Resource limits and requests
- Health probes (liveness and readiness)
- Standard Kubernetes labels
- Rolling update strategy

### 2. microservice-service.blueprint.md
Creates a Kubernetes Service with:
- Service selector matching pod labels
- Optional LoadBalancer for external access
- Standard port mapping
- Appropriate service type (ClusterIP/LoadBalancer)

### 3. configmap.blueprint.md
Creates a ConfigMap with:
- Non-sensitive configuration
- Environment variables
- Configuration files
- Log levels and feature flags

### 4. secret.blueprint.md
Creates a Secret with:
- Sensitive data (base64 encoded)
- Database URLs
- API keys and tokens
- TLS certificates

## Instance Specification Format

Instance specifications link to blueprints and provide values:

```markdown
# Frontend Instance
Blueprint References:
- Deployment: @specs/blueprints/microservice-deployment.blueprint.md
- Service: @specs/blueprints/microservice-service.blueprint.md

## Deployment Parameters
```yaml
service_name: frontend
image: todo-frontend
tag: 1.0.0-sha256-abc123def456
port: 3000
replicas: 2
cpu_request: 100m
cpu_limit: 500m
memory_request: 128Mi
memory_limit: 512Mi
health_path: /health
```

## Service Parameters
```yaml
service_name: frontend
service_type: LoadBalancer
port: 80
target_port: 3000
```

## Environment Variables
```yaml
NEXT_PUBLIC_API_URL: "http://backend-service:8000"
LOG_LEVEL: "info"
ENVIRONMENT: "development"
```
```

## Best Practices

1. **Parameter Naming**: Use snake_case for parameter names
2. **Default Values**: Provide sensible defaults where possible
3. **Validation**: Include comprehensive validation rules
4. **Documentation**: Document all parameters clearly
5. **Versioning**: Use semantic versioning for blueprints
6. **Testing**: Test blueprints with various parameter combinations
7. **Security**: Always include security best practices in templates

## Example Blueprint Files

See the complete blueprint examples in `/specs/blueprints/`:
- `microservice-deployment.blueprint.md`
- `microservice-service.blueprint.md`
- `configmap.blueprint.md`
- `secret.blueprint.md`

These examples demonstrate all the concepts and best practices for creating reusable, secure, and compliant blueprint templates.