# Helm Chart Specification: Phase IV

**Feature Branch**: `phase-iv`
**Created**: 2025-12-21
**Status**: Draft
**Input**: Create Helm chart specification defining chart structure, values configuration, and template files for all services following Phase IV Constitutional standards

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Production-Ready Helm Chart (Priority: P1)

As a DevOps engineer deploying the TODO Evolution application to Minikube, I want a complete Helm chart that packages all Kubernetes manifests with proper templating, parameterization, and configuration management so that I can deploy the entire application stack with a single command while maintaining flexibility for different environments.

**Why this priority**: Helm charts are the standard for Kubernetes application packaging - they provide reproducible deployments, environment-specific configuration, and simplified lifecycle management.

**Independent Test**: Can be fully tested by installing the chart with different values files and verifying all resources are created correctly with the specified configurations.

**Acceptance Scenarios**:

1. **Given** the Helm chart, **When** I run `helm install todo-evolution ./todo-evolution-chart`, **Then** all services deploy successfully with default values
2. **Given** custom values file, **When** I run `helm install -f values-prod.yaml`, **Then** deployments use production-specific configurations (higher replicas, different resource limits)
3. **Given** installed chart, **When** I run `helm upgrade todo-evolution ./todo-evolution-chart`, **Then** rolling updates perform without downtime
4. **Given** chart installation, **When** I run `helm test todo-evolution`, **Then** all tests pass confirming application health

---

### User Story 2 - Environment-Specific Configuration (Priority: P1)

As a platform engineer managing multiple deployment environments (development, staging, production), I want parameterized values that allow me to customize replica counts, resource allocations, and feature flags per environment while maintaining a single chart codebase.

**Why this priority**: Environment-specific configuration is essential for optimizing resource usage and enabling progressive deployment strategies across different environments.

**Independent Test**: Can be verified by creating multiple values files for different environments and testing chart installation with each.

**Acceptance Scenarios**:

1. **Given** development values file, **When** I install with development configuration, **Then** replicas are set to 1 and resources are minimized for cost efficiency
2. **Given** production values file, **When** I install with production configuration, **Then** replicas are set to 3+ with appropriate resource scaling
3. **Given** staging values file, **When** I install with staging configuration, **Then** configuration balances between development and production settings
4. **Given** custom values override, **When** I install with `--set` parameters, **Then** specific values are overridden without affecting other configurations

---

### User Story 3 - Templated Resource Generation (Priority: P1)

As a Kubernetes administrator, I want properly templated Kubernetes manifests using Helm template functions and best practices so that the chart can generate valid YAML for different scenarios while avoiding common templating pitfalls.

**Why this priority**: Proper templating ensures the chart works reliably across different Kubernetes versions and configurations while maintaining readability and maintainability.

**Independent Test**: Can be verified by running `helm template` with different values and checking generated YAML for correctness and completeness.

**Acceptance Scenarios**:

1. **Given** the chart templates, **When** I run `helm template ./todo-evolution-chart`, **Then** valid Kubernetes YAML is generated for all resources
2. **Given** different values, **When** I template with custom configuration, **Then** generated YAML reflects all template substitutions correctly
3. **Given** template functions, **When** I review template files, **Then** they use appropriate Helm functions (default, required, quote, etc.)
4. **Given** complex templates, **When** I generate manifests, **Then** conditional blocks work correctly based on enabled/disabled features

---

### User Story 4 - AI-Assisted Chart Generation (Priority: P2)

As a developer exploring modern infrastructure-as-code tools, I want to use kubectl-ai to generate the initial Helm chart structure that I can then review and customize so that I can accelerate chart development while learning Helm best practices.

**Why this priority**: Demonstrating AI-assisted infrastructure generation is a core Phase IV requirement and shows how modern tools can improve developer productivity.

**Independent Test**: Can be demonstrated by using kubectl-ai to generate chart templates and comparing them against manual specifications.

**Acceptance Scenarios**:

1. **Given** service specifications, **When** I use kubectl-ai to generate Helm chart, **Then** it creates all required template files with proper structure
2. **Given** AI-generated chart, **When** I compare to specification requirements, **Then** all Constitutional requirements are met in generated templates
3. **Given** AI-generated templates, **When** I install the chart, **Then** all services deploy correctly with proper configurations
4. **Given** AI assistance, **When** I request optimizations, **Then** kubectl-ai suggests improvements for security and performance

---

### Edge Cases

- What happens when required values are not provided in values.yaml?
- How does the chart handle image tag updates across multiple services?
- What if certain optional features (like ingress) are enabled/disabled?
- How does the chart behave when deployed to resource-constrained clusters?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chart MUST include Chart.yaml with proper metadata, version, and dependencies
- **FR-002**: Chart MUST include comprehensive values.yaml with all configurable parameters
- **FR-003**: Chart MUST include templates for all three services (frontend, backend, mcp-server)
- **FR-004**: Chart MUST include ServiceAccount templates for each deployment
- **FR-005**: Chart MUST include ConfigMap template for non-sensitive configuration
- **FR-006**: Chart MUST include Secrets template for sensitive credentials
- **FR-007**: Chart MUST support environment-specific configuration through values overrides
- **FR-008**: Chart MUST implement all Constitutional security requirements in templates
- **FR-009**: Chart MUST include health probe configurations in deployment templates
- **FR-010**: Chart MUST use proper Helm template functions and best practices
- **FR-011**: Chart MUST support conditional feature enabling/disabling
- **FR-012**: Chart MUST include proper labels and selectors for service discovery
- **FR-013**: Chart MUST implement rolling update strategy in deployments
- **FR-014**: Chart MUST include NOTES.txt for post-installation instructions

### Key Entities *(include if feature involves data)*

- **Helm Chart**: Complete package containing all Kubernetes manifests and templates
- **Chart.yaml**: Chart metadata including version, dependencies, and maintainers
- **values.yaml**: Default configuration values for all customizable parameters
- **Templates Directory**: Contains all Kubernetes manifest templates with Helm templating
- **Helper Templates**: Shared template functions and partials for reuse
- **Values Files**: Environment-specific configuration overrides
- **Release Management**: Helm release lifecycle management and upgrade strategies

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Helm chart installs successfully in under 2 minutes with default values
- **SC-002**: Chart templates generate valid Kubernetes YAML for all values combinations
- **SC-003**: Chart supports at least 3 different environment configurations (dev, staging, prod)
- **SC-004**: Rolling upgrades complete without application downtime (zero-downtime deployment)
- **SC-005**: Chart passes all Constitutional compliance checks (100% validation)
- **SC-006**: Chart size remains under 1MB for efficient distribution
- **SC-007**: Chart dependency resolution works correctly for external charts
- **SC-008**: kubectl-ai can generate compliant chart templates for comparison

## Chart Structure

### Directory Organization

```
todo-evolution-chart/
├── Chart.yaml                    # Chart metadata and configuration
├── values.yaml                   # Default configuration values
├── values-dev.yaml              # Development environment overrides
├── values-prod.yaml             # Production environment overrides
├── values-staging.yaml          # Staging environment overrides
├── templates/                    # Kubernetes manifest templates
│   ├── _helpers.tpl             # Helper template functions
│   ├── NOTES.txt                # Post-installation notes
│   ├── serviceaccounts/
│   │   ├── frontend.yaml        # Frontend service account
│   │   ├── backend.yaml         # Backend service account
│   │   └── mcp-server.yaml      # MCP server service account
│   ├── configmaps/
│   │   └── configmap.yaml        # Application configuration
│   ├── secrets/
│   │   └── secrets.yaml          # Sensitive data (referenced, not created)
│   ├── deployments/
│   │   ├── frontend-deployment.yaml
│   │   ├── backend-deployment.yaml
│   │   └── mcp-deployment.yaml
│   ├── services/
│   │   ├── frontend-service.yaml
│   │   ├── backend-service.yaml
│   │   └── mcp-service.yaml
│   ├── ingress.yaml             # Optional ingress configuration
│   ├── hpa.yaml                 # Optional Horizontal Pod Autoscaler
│   └── networkpolicy.yaml        # Optional network policies
└── tests/
    ├── test-connection.yaml      # Connection tests
    └── test-health.yaml          # Health check tests
```

### Chart.yaml Configuration

```yaml
apiVersion: v2
name: todo-evolution
description: A Helm chart for TODO Evolution application with Next.js frontend, FastAPI backend, and MCP server
type: application
version: 1.0.0
appVersion: "1.0.0"
home: https://github.com/todo-evolution/todo-evolution
sources:
  - https://github.com/todo-evolution/todo-evolution
maintainers:
  - name: TODO Evolution Team
    email: team@todo-evolution.com
keywords:
  - todo
  - nextjs
  - fastapi
  - mcp
  - kubernetes
  - helm
annotations:
  category: Application
  licenses: MIT
dependencies: []
kubeVersion: ">=1.24.0"
```

## Values.yaml Configuration

### Global Configuration

```yaml
# Global values applied to all resources
global:
  # Image registry and pull policy
  imageRegistry: ""
  imagePullPolicy: IfNotPresent
  imagePullSecrets: []

  # Common annotations
  annotations: {}

  # Common labels
  labels: {}

  # Security context
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
    allowPrivilegeEscalation: false
    capabilities:
      drop:
        - ALL

  # Resource defaults
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
```

### Frontend Configuration

```yaml
frontend:
  # Deployment configuration
  enabled: true
  replicaCount: 2

  # Image configuration
  image:
    repository: todo-frontend
    tag: 1.0.0-sha256-abc12345
    pullPolicy: IfNotPresent

  # Service configuration
  service:
    type: LoadBalancer
    port: 80
    targetPort: 3000
    annotations: {}
    loadBalancerIP: ""

  # Resource configuration
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Health check configuration
  livenessProbe:
    httpGet:
      path: /api/health
      port: http
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3

  readinessProbe:
    httpGet:
      path: /api/ready
      port: http
    initialDelaySeconds: 10
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 2

  # Environment variables
  env:
    NEXT_PUBLIC_API_URL: "http://todo-backend:8000"
    NODE_ENV: "production"
    PORT: "3000"

  # Ingress configuration
  ingress:
    enabled: false
    className: ""
    annotations: {}
    hosts:
      - host: todo.local
        paths:
          - path: /
            pathType: Prefix
    tls: []

  # Autoscaling
  autoscaling:
    enabled: false
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80

  # Node selector and tolerations
  nodeSelector: {}
  tolerations: []
  affinity: {}

  # Pod annotations
  podAnnotations: {}
```

### Backend Configuration

```yaml
backend:
  # Deployment configuration
  enabled: true
  replicaCount: 2

  # Image configuration
  image:
    repository: todo-backend
    tag: 1.0.0-sha256-def45678
    pullPolicy: IfNotPresent

  # Service configuration
  service:
    type: ClusterIP
    port: 8000
    annotations: {}

  # Resource configuration
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Health check configuration
  livenessProbe:
    httpGet:
      path: /health
      port: http
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3

  readinessProbe:
    httpGet:
      path: /ready
      port: http
    initialDelaySeconds: 10
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 2

  # Environment variables
  env:
    HOST: "0.0.0.0"
    PORT: "8000"
    CORS_ORIGINS: "http://todo-frontend"
    LOG_LEVEL: "INFO"

  # Database configuration
  database:
    host: "postgresql"
    port: 5432
    name: "todo"
    user: "todo_user"

  # Autoscaling
  autoscaling:
    enabled: false
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80

  # Node selector and tolerations
  nodeSelector: {}
  tolerations: []
  affinity: {}

  # Pod annotations
  podAnnotations: {}
```

### MCP Server Configuration

```yaml
mcp:
  # Deployment configuration
  enabled: true
  replicaCount: 1

  # Image configuration
  image:
    repository: todo-mcp-server
    tag: 1.0.0-sha256-ghi78901
    pullPolicy: IfNotPresent

  # Service configuration
  service:
    type: ClusterIP
    port: 8001
    annotations: {}

  # Resource configuration
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Health check configuration
  livenessProbe:
    httpGet:
      path: /health
      port: http
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3

  readinessProbe:
    httpGet:
      path: /ready
      port: http
    initialDelaySeconds: 10
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 2

  # Environment variables
  env:
    HOST: "0.0.0.0"
    PORT: "8001"
    LOG_LEVEL: "INFO"
    BACKEND_URL: "http://todo-backend:8000"

  # OpenAI configuration
  openai:
    model: "gpt-4"
    maxTokens: 1000
    temperature: 0.7

  # Autoscaling
  autoscaling:
    enabled: false
    minReplicas: 1
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80

  # Node selector and tolerations
  nodeSelector: {}
  tolerations: []
  affinity: {}

  # Pod annotations
  podAnnotations: {}
```

### ServiceAccount Configuration

```yaml
serviceAccount:
  # Create service accounts
  create: true
  # Annotations to add to the service accounts
  annotations: {}
  # The name of the service account to use.
  # If not set and create is true, a name is generated using the fullname template
  name: ""
```

### Secrets Configuration

```yaml
secrets:
  # External secrets (created outside of Helm)
  external:
    # Database connection
    databaseUrl:
      name: todo-secrets
      key: DATABASE_URL

    # JWT secret
    jwtSecret:
      name: todo-secrets
      key: JWT_SECRET

    # OpenAI API key
    openaiApiKey:
      name: todo-secrets
      key: OPENAI_API_KEY

  # Internal secrets (managed by Helm)
  internal:
    # Note: Production secrets should be managed externally
    # These are for development/testing only
    enabled: false
    databaseUrl: ""
    jwtSecret: ""
    openaiApiKey: ""
```

### Network Policies Configuration

```yaml
networkPolicy:
  enabled: false
  ingress:
    enabled: false
    namespaces: []
  egress:
    enabled: false
    ports: []
```

### Pod Disruption Budget

```yaml
podDisruptionBudget:
  enabled: false
  minAvailable: 1
  maxUnavailable: ""
```

## Template Files

### Helper Templates (_helpers.tpl)

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-evolution.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "todo-evolution.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-evolution.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-evolution.labels" -}}
helm.sh/chart: {{ include "todo-evolution.chart" . }}
{{ include "todo-evolution.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-evolution.selectorLabels" -}}
{{ include "todo-evolution.selectorLabels.common" . }}
{{- if .component }}
app.kubernetes.io/component: {{ .component | quote }}
{{- end }}
{{- end }}

{{/*
Common selector labels
*/}}
{{- define "todo-evolution.selectorLabels.common" -}}
app.kubernetes.io/name: {{ include "todo-evolution.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/part-of: {{ include "todo-evolution.fullname" . }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "todo-evolution.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "todo-evolution.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create image name
*/}}
{{- define "todo-evolution.image" -}}
{{- $registry := .Values.global.imageRegistry -}}
{{- $repository := .repository -}}
{{- $tag := .tag | default .Chart.AppVersion -}}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repository $tag -}}
{{- else }}
{{- printf "%s:%s" $repository $tag -}}
{{- end }}
{{- end }}

{{/*
Security context for pods
*/}}
{{- define "todo-evolution.podSecurityContext" -}}
{{- with .Values.global.securityContext }}
{{- toYaml . }}
{{- end }}
{{- end }}

{{/*
Security context for containers
*/}}
{{- define "todo-evolution.securityContext" -}}
{{- with .Values.global.securityContext }}
{{- toYaml . }}
{{- end }}
{{- end }}
```

### NOTES.txt Template

```yaml
{{/*
Modernized NOTES.txt with better formatting and instructions
*/}}
{{- $releaseName := .Release.Name -}}
{{- $serviceName := include "todo-evolution.fullname" . -}}

Thank you for installing {{ $serviceName }}.

Your TODO Evolution application has been deployed to Kubernetes.

## Services

{{- if .Values.frontend.enabled }}
### Frontend Service
The frontend service is available at:
{{- if .Values.frontend.service.type == "LoadBalancer" }}
{{- range $service := .Values.frontend.service }}
  LoadBalancer IP: {{ $service.loadBalancerIP | default "pending" }}
  External URL: http://{{ $service.loadBalancerIP | default "pending" }}:{{ $service.port }}
{{- end }}
{{- else if .Values.frontend.service.type == "NodePort" }}
  NodePort: Access via <NodeIP>:<NodePort>
{{- else }}
  ClusterIP Service: http://{{ $serviceName }}-frontend:{{ .Values.frontend.service.port }}
{{- end }}
{{- end }}

{{- if .Values.backend.enabled }}
### Backend Service
The backend service is available at:
  ClusterIP: http://{{ $serviceName }}-backend:{{ .Values.backend.service.port }}
{{- end }}

{{- if .Values.mcp.enabled }}
### MCP Server Service
The MCP server is available at:
  ClusterIP: http://{{ $serviceName }}-mcp:{{ .Values.mcp.service.port }}
{{- end }}

## Accessing the Application

{{- if .Values.frontend.enabled }}
### Web Interface
1. Get the LoadBalancer IP:
   kubectl get svc {{ $serviceName }}-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

2. Access the application:
   http://<LOAD_BALANCER_IP>

3. Or use Minikube service:
   minikube service {{ $serviceName }}-frontend --url
{{- end }}

### API Endpoints
- Frontend Health: http://{{ $serviceName }}-frontend/api/health
- Backend Health: http://{{ $serviceName }}-backend/health
- MCP Health: http://{{ $serviceName }}-mcp/health

## Management Commands

### Get all resources
```bash
kubectl get all -l app.kubernetes.io/part-of={{ $serviceName }}
```

### Check pod status
```bash
kubectl get pods -l app.kubernetes.io/part-of={{ $serviceName }}
```

### View logs
```bash
kubectl logs -l app.kubernetes.io/name=todo-backend --follow
kubectl logs -l app.kubernetes.io/name=todo-frontend --follow
kubectl logs -l app.kubernetes.io/name=todo-mcp --follow
```

### Scale deployments
```bash
kubectl scale deployment {{ $serviceName }}-backend --replicas=3
kubectl scale deployment {{ $serviceName }}-frontend --replicas=3
```

### Update the application
```bash
helm upgrade {{ $releaseName }} ./todo-evolution-chart
```

### Rollback
```bash
helm rollback {{ $releaseName }}
```

### Uninstall
```bash
helm uninstall {{ $releaseName }}
```

## Configuration

The application configuration can be customized by:
1. Creating custom values files
2. Using --set flags during installation
3. Modifying the secrets

### Example: Custom values file
```yaml
frontend:
  replicaCount: 3
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi

backend:
  replicaCount: 3
  env:
    LOG_LEVEL: DEBUG
```

### Example: Install with custom values
```bash
helm install {{ $releaseName }} ./todo-evolution-chart -f custom-values.yaml
```

## Secrets

{{- if not .Values.secrets.external.enabled }}
For development, the chart can manage secrets. For production, create secrets manually:

```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=JWT_SECRET="your-jwt-secret" \
  --from-literal=OPENAI_API_KEY="your-openai-key"
```

{{- end }}

## Troubleshooting

### Check pod events
```bash
kubectl describe pod -l app.kubernetes.io/name=todo-backend
```

### Check service endpoints
```bash
kubectl get endpoints
```

### Port forwarding for debugging
```bash
kubectl port-forward svc/{{ $serviceName }}-backend 8080:8000
```

### Access pod shell
```bash
kubectl exec -it deployment/{{ $serviceName }}-backend -- /bin/sh
```

## Documentation

For more information:
- Chart documentation: https://github.com/todo-evolution/todo-evolution
- Kubernetes documentation: https://kubernetes.io/docs/
- Helm documentation: https://helm.sh/docs/
```

## Environment-Specific Values Files

### Development Environment (values-dev.yaml)

```yaml
# Development environment - minimal resources for cost efficiency
frontend:
  replicaCount: 1
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi

backend:
  replicaCount: 1
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi

mcp:
  replicaCount: 1
  resources:
    requests:
      cpu: 50m
      memory: 64Mi
    limits:
      cpu: 200m
      memory: 256Mi

# Enable development-specific features
global:
  annotations:
    environment: development

# Development ingress for local testing
frontend:
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: todo-dev.local
        paths:
          - path: /
            pathType: Prefix
```

### Production Environment (values-prod.yaml)

```yaml
# Production environment - high availability and resources
frontend:
  replicaCount: 3
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

backend:
  replicaCount: 3
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

mcp:
  replicaCount: 2
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

# Production security settings
serviceAccount:
  annotations:
    eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/todo-evolution"

# Production ingress
frontend:
  ingress:
    enabled: true
    className: nginx
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt-prod
      nginx.ingress.kubernetes.io/rate-limit: "100"
    hosts:
      - host: todo.example.com
        paths:
          - path: /
            pathType: Prefix
    tls:
      - hosts:
          - todo.example.com
        secretName: todo-tls

# Pod disruption budget for high availability
podDisruptionBudget:
  enabled: true
  minAvailable: 1

# Network policies for security
networkPolicy:
  enabled: true
  ingress:
    enabled: true
  egress:
    enabled: true
```

### Staging Environment (values-staging.yaml)

```yaml
# Staging environment - balanced between dev and prod
frontend:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

backend:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

mcp:
  replicaCount: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

# Staging-specific configuration
global:
  annotations:
    environment: staging

frontend:
  env:
    NODE_ENV: "staging"

backend:
  env:
    LOG_LEVEL: "DEBUG"
```

## Chart Installation and Management

### Installation Commands

#### Basic Installation
```bash
# Install with default values
helm install todo ./todo-evolution-chart

# Install with custom values file
helm install todo ./todo-evolution-chart -f values-prod.yaml

# Install with set parameters
helm install todo ./todo-evolution-chart \
  --set frontend.replicaCount=3 \
  --set backend.resources.limits.cpu=1000m
```

#### Upgrade Commands
```bash
# Upgrade with new chart version
helm upgrade todo ./todo-evolution-chart

# Upgrade with new values
helm upgrade todo ./todo-evolution-chart -f values-prod.yaml

# Upgrade with specific parameter changes
helm upgrade todo ./todo-evolution-chart \
  --set frontend.image.tag=1.1.0-sha256-newhash
```

### Testing and Validation

#### Lint and Template Validation
```bash
# Lint the chart
helm lint ./todo-evolution-chart

# Template rendering test
helm template todo ./todo-evolution-chart -f values-prod.yaml

# Dry run installation
helm install todo ./todo-evolution-chart --dry-run --debug
```

#### Installation Testing
```bash
# Install with test
helm install todo ./todo-evolution-chart --wait --timeout=10m

# Run tests
helm test todo

# Verify installation
helm status todo
```

## Dependencies and Integration

### External Chart Dependencies

```yaml
# Chart.yaml dependencies example
dependencies:
  - name: postgresql
    version: 12.1.9
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: 17.3.7
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

### Subchart Integration

```yaml
# Subchart values configuration
postgresql:
  enabled: true
  auth:
    postgresPassword: "secure-password"
    database: "todo"
  primary:
    persistence:
      enabled: true
      size: 20Gi

redis:
  enabled: true
  auth:
    enabled: false
  master:
    persistence:
      enabled: true
      size: 8Gi
```

## Troubleshooting Guide

### Common Issues

#### Template Rendering Errors
- Check syntax with `helm lint`
- Validate values with `helm template --dry-run`
- Review helper template functions

#### Resource Creation Failures
- Check namespace exists: `kubectl get ns`
- Verify RBAC permissions: `kubectl auth can-i create deployments`
- Check resource quotas: `kubectl describe namespace`

#### Service Connection Issues
- Verify service selectors match pod labels
- Check network policies allow traffic
- Test with pod-to-pod communication

#### Image Pull Issues
- Verify image registry access
- Check imagePullSecrets configuration
- Validate image tag format (SHA256 required)

### Debug Commands

```bash
# Get chart values
helm get values todo

# Get chart manifest
helm get manifest todo

# Get chart hooks
helm get hooks todo

# Debug template rendering
helm template todo --debug
```

## Release Management

### Versioning Strategy
- Chart version follows semantic versioning (1.0.0)
- AppVersion matches application version
- Use `helm chart version` for compatibility

### Release Lifecycle
1. **Development**: Test in development environment
2. **Staging**: Validate in staging environment
3. **Production**: Deploy to production
4. **Monitoring**: Track release performance

### Rollback Strategy
- Use `helm rollback` for quick rollbacks
- Maintain previous chart versions
- Document rollback procedures

This specification provides a complete Helm chart that packages all Kubernetes manifests for the TODO Evolution application with proper templating, configuration management, and operational best practices.