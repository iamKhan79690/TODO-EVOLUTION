# Constitutional Rules Reference

This document provides a comprehensive reference for all Phase IV Constitutional rules that the constitution-enforcer skill must validate against.

## Quick Reference Cheat Sheet

### Container Security Rules (1.1-1.4)

| Rule | Check | PASS Condition | FAIL Condition |
|------|-------|----------------|----------------|
| 1.1 | Non-root containers | `runAsNonRoot: true`, `runAsUser: ≥1000` | Missing or `runAsUser: <1000` |
| 1.2 | Immutable image tags | Tag includes "sha256" | `:latest`, `:dev`, missing sha256 |
| 1.3 | Approved registries | No registry prefix (local) | `docker.io/`, external registry |
| 1.4 | Security hardening | `capabilities: {drop: [ALL]}` | Missing security hardening |

### Resource Management Rules (2.1-2.3)

| Rule | Check | PASS Condition | FAIL Condition |
|------|-------|----------------|----------------|
| 2.1 | Resource limits | Both requests AND limits defined | Missing either |
| 2.2 | Request-to-limit ratio | requests ≤ limits | requests > limits |
| 2.3 | Replica count | replicas ≥ 1 | replicas = 0 |

### Health & Observability Rules (3.1-3.2)

| Rule | Check | PASS Condition | FAIL Condition |
|------|-------|----------------|----------------|
| 3.1 | Health probes | Both liveness AND readiness present | Either missing |
| 3.2 | Health endpoints | HTTP endpoints at /health, /ready | Missing or wrong paths |

### Deployment Standards Rules (4.1-4.3)

| Rule | Check | PASS Condition | FAIL Condition |
|------|-------|----------------|----------------|
| 4.1 | Standard labels | All 6 k8s recommended labels | Any label missing |
| 4.2 | Update strategy | `type: RollingUpdate` | `type: Recreate` |
| 4.3 | Service selector | Matches deployment pod labels | Selector mismatch |

### Secrets Management Rules (5.1-5.2)

| Rule | Check | PASS Condition | FAIL Condition |
|------|-------|----------------|----------------|
| 5.1 | No plain text secrets | `valueFrom.secretKeyRef` | `value: "plaintext"` |
| 5.2 | Imperative secrets | Create via `kubectl create secret` | Secrets committed to git |

## Detailed Rule Explanations

### Rule 1.1: Non-Root Containers
**Why this exists**: Running containers as root is a major security risk. If compromised, attacker gets root access to the node.

**Required fields**:
```yaml
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true      # Must be exactly true
        runAsUser: 1000         # Must be 1000 or higher
        fsGroup: 1000           # Must be numeric
      containers:
      - securityContext:
          allowPrivilegeEscalation: false  # Must be exactly false
          readOnlyRootFilesystem: true      # Recommended
          capabilities:
            drop:
              - ALL             # Must drop ALL capabilities
```

**Common violations**:
- Missing `securityContext` entirely
- `runAsUser: 0` (root)
- Missing `capabilities.drop: [ALL]`

### Rule 1.2: Immutable Image Tags
**Why this exists**: Mutable tags like `:latest` create non-deterministic deployments and prevent rollback capabilities.

**Valid formats**:
- `todo-frontend:1.0.0-sha256-abc12345`
- `backend:2.1.3-sha256-def45678`
- Format: `{semantic-version}-sha256-{8-char-hash}`

**Invalid formats**:
- `todo-frontend:latest`
- `todo-frontend:dev`
- `todo-frontend:v1.0.0` (missing sha256)

### Rule 2.1: Resource Limits Required
**Why this exists**: Without resource limits, a single pod can monopolize node resources and cause cascading failures.

**Required structure**:
```yaml
containers:
- name: app
  resources:                    # This field is required
    requests:                    # requests are required
      cpu: "100m"                # Must have value
      memory: "128Mi"            # Must have value
    limits:                      # limits are required
      cpu: "500m"                # Must have value
      memory: "512Mi"            # Must have value
```

**Recommended defaults for Phase IV**:
- CPU request: 100m (0.1 core)
- CPU limit: 500m (0.5 core)
- Memory request: 128Mi
- Memory limit: 512Mi

### Rule 3.1: Health Probes Required
**Why this exists**: Health probes enable Kubernetes to automatically restart failed containers and remove unhealthy pods from service.

**Both probes required**:
```yaml
containers:
- name: app
  livenessProbe:               # REQUIRED - restarts container if fails
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 30   # Give app time to start
    periodSeconds: 10          # Check every 10 seconds
    timeoutSeconds: 5          # Timeout after 5 seconds
    failureThreshold: 3        # Fail after 3 consecutive failures

  readinessProbe:              # REQUIRED - removes from service if fails
    httpGet:
      path: /ready
      port: 8080
    initialDelaySeconds: 10   # Start checking sooner
    periodSeconds: 5           # Check more frequently
    timeoutSeconds: 3          # Quicker timeout
    failureThreshold: 2        # Fail after 2 consecutive failures
```

### Rule 4.1: Kubernetes Recommended Labels
**Why this exists**: Standard labels enable tools to identify, manage, and monitor applications consistently.

**All 6 labels required**:
```yaml
metadata:
  labels:
    app.kubernetes.io/name: frontend              # Application name
    app.kubernetes.io/instance: todo-evolution    # Unique instance name
    app.kubernetes.io/version: "1.0.0"            # Version (immutable)
    app.kubernetes.io/component: microservice     # Component type
    app.kubernetes.io/part-of: todo-evolution     # Application it belongs to
    app.kubernetes.io/managed-by: helm            # Tool managing it
```

**Label value requirements**:
- `name`: Lowercase, alphanumeric, hyphens
- `version`: Must match image tag (immutable)
- `instance`: Typically deployment environment
- `component`: frontend, backend, database, etc.

### Rule 5.1: No Plain Text Secrets
**Why this exists**: Secrets in plain text in YAML are visible to anyone with repository access and get logged by Kubernetes.

**Correct approach**:
```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:           # ✅ Correct - from secret
      name: todo-secrets
      key: DATABASE_URL

# PROHIBITED:
- name: DATABASE_URL
  value: "postgresql://user:pass@host/db"  # ❌ Plain text
```

**Secret creation**:
```bash
# Create secret imperatively (never commit)
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=JWT_SECRET="your-secret-here"
```

## Validation Checklist

For every Kubernetes configuration, run through this checklist:

### Deployment Validation
```
□ Image tag includes "sha256"?
□ runAsNonRoot: true present?
□ runAsUser: ≥ 1000?
□ capabilities.drop: [ALL] present?
□ resources.requests defined?
□ resources.limits defined?
□ requests.cpu ≤ limits.cpu?
□ requests.memory ≤ limits.memory?
□ livenessProbe configured?
□ readinessProbe configured?
□ All 6 standard labels present?
□ Rolling update strategy configured?
□ replicas ≥ 1?
```

### Service Validation
```
□ Selector matches deployment labels?
□ Service type appropriate (LoadBalancer for frontend, ClusterIP for backend)?
□ Port numbers match container ports?
□ Target ports correct?
```

### Secret Validation
```
□ No plain text secrets in env variables?
□ No plain text secrets in volume mounts?
□ Secrets created imperatively?
□ Secrets referenced via secretKeyRef?
```

## Common Violation Patterns

### 1. Missing Security Context
**Problem**: No `securityContext` field
**Fix**: Add complete security context at both pod and container level

### 2: Latest Image Tag
**Problem**: `image: nginx:latest`
**Fix**: `image: nginx:1.21.6-sha256-abc12345`

### 3: No Resource Limits
**Problem**: Missing `resources` field
**Fix**: Add both `requests` and `limits` with reasonable values

### 4: Missing Health Probes
**Problem**: No `livenessProbe` or `readinessProbe`
**Fix**: Add both probes with appropriate paths and timeouts

### 5: Incomplete Labels
**Problem**: Missing some of the 6 required labels
**Fix**: Add all standard Kubernetes recommended labels

### 6: Plain Text Secrets
**Problem**: `value: "secret-password"`
**Fix**: Use `valueFrom.secretKeyRef` and create secret imperatively

## Integration Points

### With blueprint-instantiator
- Called after blueprint substitution
- Validates generated manifests before saving
- Returns compliance report

### With helm-chart-generator
- Called after rendering templates
- Validates all resources in rendered chart
- Provides compliance report for each resource

### Manual invocation
- Called when user provides YAML for review
- Validates against all rules
- Provides detailed violation reports with fixes