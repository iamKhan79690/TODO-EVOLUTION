# Containerization Specification: Phase IV Kubernetes Deployment

**Feature Branch**: `phase-iv`
**Created**: 2025-12-21
**Status**: Draft
**Input**: Create detailed containerization specification for Frontend (Next.js), Backend (FastAPI), and MCP Server services following Phase IV Constitutional standards

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Production-Ready Container Images (Priority: P1)

As a DevOps engineer deploying the TODO Evolution application, I want production-ready container images for all services with multi-stage builds, security hardening, and minimal attack surfaces so that the application can be safely deployed to Kubernetes with enterprise-grade security standards.

**Why this priority**: Container security is foundational - without properly secured containers, the entire Kubernetes deployment is vulnerable to attacks and non-compliant with Constitutional requirements.

**Independent Test**: Can be fully tested by building all three container images and verifying they run with non-root users, pass security scans, and respond to health checks.

**Acceptance Scenarios**:

1. **Given** service source code, **When** I build containers using the specification, **Then** all containers run as non-root user with UID 1000
2. **Given** built container images, **When** I scan for vulnerabilities, **Then** no critical vulnerabilities are found and all security contexts are properly configured
3. **Given** running containers, **When** I check filesystem permissions, **Then** root filesystem is read-only where possible
4. **Given** container startup, **When** health checks are executed, **Then** all health endpoints respond appropriately within timeout periods

---

### User Story 2 - Multi-Stage Build Optimization (Priority: P1)

As a developer managing container deployments, I want optimized multi-stage Docker builds that minimize image size and separate build-time dependencies from runtime so that containers start quickly, use less storage, and have reduced attack surfaces.

**Why this priority**: Image size directly impacts deployment speed, storage costs, and security - smaller images with fewer layers mean faster downloads and fewer vulnerabilities.

**Independent Test**: Can be tested by building images with the multi-stage Dockerfiles and comparing sizes against single-stage equivalents.

**Acceptance Scenarios**:

1. **Given** the multi-stage Dockerfile, **When** I build the frontend image, **Then** final image size is under 200MB (excluding node_modules)
2. **Given** the multi-stage build process, **When** I inspect the final image, **Then** no build tools (npm, compilers) are present in runtime layers
3. **Given** the built container, **When** I list installed packages, **Then** only runtime dependencies are included
4. **Given** different build environments, **When** I rebuild images, **Then** runtime layers remain unchanged (better caching)

---

### User Story 3 - Health Check Implementation (Priority: P2)

As a Kubernetes cluster administrator, I want standardized health check endpoints (/health, /ready) implemented in all services so that Kubernetes can automatically detect and handle unhealthy pods without manual intervention.

**Why this priority**: Health probes are essential for self-healing Kubernetes deployments - they enable automatic restarts and traffic routing based on application health.

**Independent Test**: Can be verified by deploying containers and checking that health probes respond correctly and trigger appropriate Kubernetes actions.

**Acceptance Scenarios**:

1. **Given** a running container, **When** I access /health endpoint, **Then** it returns HTTP 200 with service health status
2. **Given** a running container, **When** I access /ready endpoint, **Then** it returns HTTP 200 when service is ready to accept traffic
3. **Given** Kubernetes deployment with health probes, **When** a container becomes unhealthy, **Then** Kubernetes restarts it automatically
4. **Given** service startup, **When** initial health checks run, **Then** they respect configured initial delay periods

---

### User Story 4 - AI-Assisted Container Generation (Priority: P2)

As a developer exploring modern development workflows, I want to use Gordon (Docker AI) to generate initial Dockerfile templates that I can then review and customize so that I can accelerate container development while learning best practices.

**Why this priority**: Demonstrating AI-assisted development is a core Phase IV requirement and shows how modern tools can improve developer productivity while maintaining security standards.

**Independent Test**: Can be demonstrated by using Gordon to generate Dockerfiles and comparing them against the manual specification requirements.

**Acceptance Scenarios**:

1. **Given** service source code, **When** I use Gordon to generate a Dockerfile, **Then** it includes multi-stage builds and security best practices
2. **Given** AI-generated Dockerfile, **When** I compare it to specification requirements, **Then** all Constitutional requirements are met
3. **Given** AI-generated Dockerfile, **When** I build the container, **Then** it runs successfully with proper security contexts
4. **Given** AI assistance, **When** I request optimizations, **Then** Gordon suggests security and performance improvements

---

### Edge Cases

- What happens when health check endpoints are not implemented in the application code?
- How does the system handle container startup failures due to missing environment variables?
- What if the base image specified in the constitution is not available or compatible?
- How do containers behave when required dependencies cannot be installed during build?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Frontend container MUST use Next.js with standalone output mode and expose port 3000
- **FR-002**: Backend container MUST use FastAPI with uvicorn server and expose port 8000
- **FR-003**: MCP Server container MUST be Python-based and expose port 8001
- **FR-004**: All containers MUST use multi-stage Docker builds with separate build and runtime stages
- **FR-005**: All containers MUST run as non-root user with UID 1000 (appuser)
- **FR-006**: All containers MUST implement both /health and /ready endpoints for Kubernetes probes
- **FR-007**: All containers MUST use read-only root filesystem where possible
- **FR-008**: All containers MUST drop ALL Linux capabilities in security context
- **FR-009**: All containers MUST use base images: node:20-alpine (frontend), python:3.13-slim (backend/MCP)
- **FR-010**: All containers MUST include HEALTHCHECK directive with appropriate intervals and timeouts
- **FR-011**: All containers MUST use semantic versioning for image tags (v1.0.0-sha256-{hash})
- **FR-012**: All containers MUST configure environment variables for service discovery and database connections
- **FR-013**: All containers MUST handle SIGTERM signals for graceful shutdown
- **FR-014**: Build process MUST separate development dependencies from production dependencies

### Key Entities *(include if feature involves data)*

- **Frontend Container**: Next.js 16+ application with TypeScript, Tailwind CSS, standalone output
- **Backend Container**: FastAPI Python application with SQLModel, Neon PostgreSQL integration
- **MCP Server Container**: Python service providing AI chatbot capabilities via MCP protocol
- **Dockerfile Templates**: Multi-stage build specifications for each service type
- **Security Context**: Kubernetes pod and container security configurations
- **Health Endpoints**: Application-level health check implementations
- **Environment Variables**: Configuration values for service communication and secrets

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three container images build successfully under 5 minutes each on standard development machine
- **SC-002**: Frontend container image size under 200MB (runtime layers only)
- **SC-003**: Backend container image size under 150MB (runtime layers only)
- **SC-004**: MCP Server container image size under 100MB (runtime layers only)
- **SC-005**: All containers pass constitutional security validation (100% compliance)
- **SC-006**: Health endpoints respond within 200ms for all services
- **SC-007**: Containers start up and become ready within 30 seconds on average
- **SC-008**: Gordon AI can generate compliant Dockerfile templates for all three services

## Technical Specifications

### Frontend Container (Next.js)

#### Base Image Requirements
- **Build Stage**: `node:20-alpine` for dependency installation and build
- **Runtime Stage**: `node:20-alpine` for production runtime
- **Security**: Non-root user `appuser` with UID 1000

#### Multi-Stage Build Structure
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runtime
# Security setup and application copy
```

#### Port Exposures
- **Primary Port**: 3000 (Next.js application server)
- **Health Check Port**: 3000 (same port, different paths)

#### Environment Variables Required
```bash
NEXT_PUBLIC_API_URL=http://backend-service:8000
NODE_ENV=production
PORT=3000
```

#### Health Check Endpoints
- **Liveness**: `GET /api/health` - Application health status
- **Readiness**: `GET /api/ready` - Ready to serve traffic

### Backend Container (FastAPI)

#### Base Image Requirements
- **Build Stage**: `python:3.13-slim` for dependency installation
- **Runtime Stage**: `python:3.13-slim` for production runtime
- **Security**: Non-root user `appuser` with UID 1000

#### Multi-Stage Build Structure
```dockerfile
# Stage 1: Dependencies
FROM python:3.13-slim AS dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim AS runtime
# Security setup and application copy
```

#### Port Exposures
- **Primary Port**: 8000 (FastAPI/uvicorn server)
- **Health Check Port**: 8000 (same port, different paths)

#### Environment Variables Required
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET=your-jwt-secret-key
CORS_ORIGINS=http://frontend-service:3000
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

#### Health Check Endpoints
- **Liveness**: `GET /health` - Service health and database connectivity
- **Readiness**: `GET /ready` - Ready to handle API requests

### MCP Server Container

#### Base Image Requirements
- **Build Stage**: `python:3.13-slim` for dependency installation
- **Runtime Stage**: `python:3.13-slim` for production runtime
- **Security**: Non-root user `appuser` with UID 1000

#### Multi-Stage Build Structure
```dockerfile
# Stage 1: Dependencies
FROM python:3.13-slim AS dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim AS runtime
# Security setup and application copy
```

#### Port Exposures
- **Primary Port**: 8001 (MCP server)
- **Health Check Port**: 8001 (same port, different paths)

#### Environment Variables Required
```bash
OPENAI_API_KEY=your-openai-api-key
BACKEND_URL=http://backend-service:8000
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8001
```

#### Health Check Endpoints
- **Liveness**: `GET /health` - MCP service health status
- **Readiness**: `GET /ready` - Ready to handle MCP requests

## Security Requirements

### Container Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

### User Management
- Create `appuser` with UID 1000 and GID 1000
- Set appropriate ownership for application files
- Ensure no SUID/SGID binaries in container

### Filesystem Permissions
- Application directory: `/app` owned by `appuser`
- Temporary directories: `/tmp` with appropriate permissions
- Log directories: Writable by `appuser` if needed
- Read-only root filesystem with necessary writeable mounts

### Network Security
- No privileged ports (< 1024) unless absolutely required
- Container networking isolation per Kubernetes standards
- No host network access unless explicitly needed

## Build Process

### Build Arguments
```dockerfile
# Common build arguments for all services
ARG VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF
```

### Label Standards
```dockerfile
LABEL org.label-schema.name="todo-frontend" \
      org.label-schema.version=$VERSION \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0"
```

### Health Check Configuration
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1
```

### Signal Handling
- Implement SIGTERM handler for graceful shutdown
- Configure appropriate termination grace periods
- Ensure in-flight requests complete before termination

## Integration Requirements

### Service Discovery
- Frontend: Environment variable `NEXT_PUBLIC_API_URL` pointing to backend service
- Backend: Environment variable `DATABASE_URL` for PostgreSQL connection
- MCP Server: Environment variable `BACKEND_URL` for backend communication

### Configuration Management
- Use environment variables for all configuration
- Support for both development and production configurations
- No hardcoded values in application code

### Logging Standards
- Structured JSON logging for backend services
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Container logs to stdout/stderr for Kubernetes collection

## Quality Assurance

### Image Scanning
- Scan all images for security vulnerabilities
- Address any critical or high-severity vulnerabilities
- Maintain vulnerability scan reports

### Compliance Validation
- Verify all containers pass constitutional-enforcer validation
- Check security contexts are properly applied
- Validate health probe configurations

### Performance Testing
- Test container startup times
- Verify memory usage within expected bounds
- Test health check response times