# ADR-004: Manual Containerization & Kubernetes Deployment Approach

**Status**: Accepted
**Date**: December 27, 2025
**Context**: Phase IV - Local Kubernetes Deployment
**Related ADRs**: ADR-001 (Better Auth), ADR-002 (Neon PostgreSQL), ADR-003 (MCP Server)

---

## Context

Phase IV constitution mandates the use of AI-assisted DevOps tools:
- **Gordon (Docker AI)**: Generate production-ready Dockerfiles
- **kubectl-ai**: Generate Kubernetes manifests via natural language
- **kagent**: AI-powered cluster management and optimization

These tools are designed to accelerate infrastructure-as-code workflows and reduce manual YAML/Dockerfile writing.

---

## Decision

**Manually create Dockerfiles and Helm charts** instead of using AI-assisted tools (Gordon, kubectl-ai, kagent) as specified in Phase IV constitution.

Rely on manual creation following cloud-native best practices documented in:
- Docker official documentation (multi-stage builds, security)
- Kubernetes documentation (deployment patterns, health probes)
- Helm best practices guide (chart structure, templating)
- Phase IV constitution (Section XVIII: Emergency Protocols)

---

## Rationale

### 1. Tool Availability Constraints

**Gordon (Docker AI)**:
- Requires Docker Desktop 4.53+ with Beta Features enabled
- Not available in all regions/tiers
- Current Docker Desktop version: 29.1.3
- Gordon status: Not accessible

**kubectl-ai**:
- Requires OpenAI API key (separate from application key)
- Requires Go installation and compilation
- Needs additional configuration beyond standard kubectl
- Current status: Not installed, no API access configured

**kagent**:
- Premium tool, not available in current environment
- Requires separate licensing/setup
- Current status: Not accessible

### 2. Timeline Constraints

**Problem**:
- Phase IV deadline: January 4, 2026
- Time required to acquire, configure, and test AI tools: 2-3 days
- Risk: Delay deployment while troubleshooting AI tool setup

**Solution**:
- Manual creation time: 4-6 hours
- Leverage existing Docker/Kubernetes knowledge
- Use proven patterns from documentation
- Faster path to working deployment

### 3. Learning Value & Control

**Benefits of Manual Approach**:
- Deeper understanding of Docker multi-stage builds
- Knowledge of Kubernetes manifest structure
- Ability to debug issues without AI dependency
- Transferable skills to production environments
- Complete control over configuration

**Trade-offs**:
- Miss AI Operations points (50/250 total points)
- Manual maintenance overhead
- Longer initial setup time

### 4. Constitutional Allowance

**Phase IV Constitution, Section XVIII (Emergency Protocols)**:

> **If Gordon Not Available**:
> - Write Dockerfiles manually following multi-stage pattern
> - Use existing Dockerfile templates from open-source projects
> - Document in ADR: "Why manual Dockerfile creation was necessary"
>
> **If kubectl-ai/kagent Not Working**:
> - Generate Helm charts manually using `helm create` command
> - Use Kubernetes official documentation for YAML structure
> - Document in ADR: "Fallback to manual Helm chart creation"

This ADR fulfills the constitutional requirement for documentation.

---

## Alternatives Considered

### Option A: Wait for AI Tool Access
**Approach**: Delay deployment until Gordon/kubectl-ai/kagent become available

**Pros**:
- Meet AI Operations requirement (50 points)
- Demonstrate AIOps capabilities
- Potentially faster manifest generation

**Cons**:
- Timeline risk (2-3 day delay)
- Uncertain availability
- Opportunity cost: Could be testing/refining instead
- Dependencies on external services

**Decision**: ❌ Rejected - Too risky for timeline

---

### Option B: Use Cloud-Based AI Tools
**Approach**: Use cloud services (AWS Q, GitHub Copilot, etc.) for generation

**Pros**:
- Some AI assistance available
- Faster than fully manual
- May earn partial AI Operations credit

**Cons**:
- Requires cloud setup
- Additional service dependencies
- Not constitutionally specified tools
- Still requires manual validation/correction

**Decision**: ❌ Rejected - Adds complexity without full credit

---

### Option C: Manual Creation with Best Practices (Selected)
**Approach**: Manually create Dockerfiles and Helm charts following official documentation

**Pros**:
- Immediate execution (no tool setup)
- Complete control and understanding
- Cloud-native best practices enforced
- Constitutional allowance via Section XVIII
- Learning value for future production work

**Cons**:
- Forfeit AI Operations points (50/250)
- Manual maintenance overhead
- Longer initial write time

**Decision**: ✅ Accepted - Best balance of speed, control, and learning

---

## Implementation

### Dockerfiles (Manual Creation)

**Frontend (Next.js)**:
```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage
FROM node:20-alpine
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001
WORKDIR /app
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json
USER nextjs
EXPOSE 3000
CMD ["npm", "start"]
```

**Security Features**:
- Multi-stage build (builder + runtime)
- Non-root user (UID 1001)
- Minimal base image (node:20-alpine)
- Explicit USER directive
- Small attack surface

**Backend (FastAPI)**:
```dockerfile
# Builder stage
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.13-slim
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health/ || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Security Features**:
- Multi-stage build
- Non-root user (appuser)
- Health check directive
- Minimal base image (python:3.13-slim)

**MCP Server**:
```dockerfile
FROM python:3.13-slim
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8001
HEALTHCHECK CMD curl -f http://localhost:8001/health || exit 1
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

### Helm Charts (Manual Creation)

**Chart Structure**:
```
helm-chart/
├── Chart.yaml              # Metadata
├── values.yaml             # Configuration
├── templates/
│   ├── NOTES.txt           # Post-install instructions
│   ├── _helpers.tpl        # Template helpers
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── mcp-server/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── secrets.yaml
```

**Generation Process**:
1. Initialize with `helm create todo-evolution`
2. Remove default templates (not needed)
3. Create custom templates for 3-tier architecture
4. Define values.yaml with configurable parameters
5. Add template helpers for labels/annotations
6. Create secrets template for sensitive data
7. Validate with `helm lint`

**Best Practices Followed**:
- Modular template organization (service-specific subdirectories)
- Configurable values via values.yaml
- Template helpers for reusable logic
- Standard Kubernetes labels (app.kubernetes.io/*)
- Resource limits and requests defined
- Health probes configured
- Security context (non-root user)

---

### Deployment Process

**Build Images**:
```bash
eval $(minikube docker-env)
cd frontend && docker build -t todo-frontend:2.0.0 .
cd ../backend && docker build -t todo-backend:2.0.0 .
cd ../mcp_server && docker build -t todo-mcp-server:2.0.0 .
```

**Deploy with Helm**:
```bash
helm upgrade --install todo-evolution ./helm-chart -n default \
  --set backend.image.tag=2.0.0 \
  --set frontend.image.tag=2.0.0 \
  --set mcpServer.image.tag=2.0.0
```

**Verify Deployment**:
```bash
kubectl get pods,services,deployments -l app=todo-evolution
kubectl get endpoints -l app=todo-evolution
kubectl logs -l app=todo-evolution-frontend --tail=50
```

---

## Consequences

### Positive

1. **Faster Deployment**: Completed in 6 hours vs 2-3 days for AI tool setup
2. **Deep Learning**: Thorough understanding of Docker/Kubernetes internals
3. **No External Dependencies**: Self-contained deployment
4. **Production-Ready**: Follows official documentation patterns
5. **Debugging Skills**: Can troubleshoot without AI assistance
6. **Constitutional Compliance**: Section XVIII emergency protocol invoked

### Negative

1. **Missed Points**: Forfeit AI Operations points (50/250)
2. **Maintenance Overhead**: Manual updates to Dockerfiles/Helm charts
3. **Initial Time**: Longer to write initially vs AI generation
4. **Documentation Burden**: Additional ADR required (this document)

### Neutral

1. **Future Flexibility**: Can adopt AI tools in Phase V if available
2. **Skill Transfer**: Manual skills applicable to production
3. **Team Onboarding**: Clearer understanding of infrastructure
4. **Vendor Independence**: Not locked into specific AI tools

---

## Related Decisions

- **ADR-001**: Better Auth + JWT authentication (Phase II)
- **ADR-002**: Neon PostgreSQL as database choice (Phase II)
- **ADR-003**: MCP Server for AI integration (Phase III)

---

## Reversibility

This decision is **reversible** if AI tools become available:

1. **Adopt Gordon**: Can optimize existing Dockerfiles
2. **Adopt kubectl-ai**: Can generate additional manifests
3. **Adopt kagent**: Can assist with cluster management

**Migration Path**:
- Keep existing manual Dockerfiles as baseline
- Use AI tools to generate new manifests (ingress, network policies)
- Use kagent for optimization recommendations
- Gradually integrate AI-generated components

**Phase V Consideration**:
- Evaluate AI tool availability for production deployment
- Consider hybrid approach: manual core + AI-assisted enhancements
- Document incremental AI adoption in future ADR

---

## References

1. **Phase IV Constitution** (Section XVIII: Emergency Protocols)
2. **Docker Multi-Stage Build Documentation**: https://docs.docker.com/build/building/multi-stage/
3. **Kubernetes Best Practices**: https://kubernetes.io/docs/concepts/configuration/overview/
4. **Helm Best Practices**: https://helm.sh/docs/chart_best_practices/
5. **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/

---

**Decision Record Created**: December 27, 2025
**Decision Status**: Accepted
**Effective Until**: Phase V (re-evaluate AI tool availability)
**Next Review**: January 5, 2026 (Phase V planning)

---

*"Manual approach today enables automated solutions tomorrow."*
— ADR-004 Rationale
