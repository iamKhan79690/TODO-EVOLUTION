# ADR-011: Fallback to Standard CLI Tools for Minikube Deployment

**Status**: Accepted
**Date**: 2025-12-30
**Context**: Feature 011-minikube-helm-deploy
**Constitution**: Phase IV Kubernetes Deployment Constitution (Section X: AI-Assisted Operations)

## Context

The Phase IV Constitution requires the use of AI-assisted operations tools:
- **Gordon (Docker AI)**: For intelligent Docker operations and containerization
- **kubectl-ai**: For Kubernetes manifest generation and troubleshooting
- **kagent**: For cluster management and optimization

These tools are specified as constitutional requirements for Phase IV implementation, with fallback protocols documented in emergency protocols section (XVIII).

## Decision

**Use standard CLI tools (Docker, kubectl, Helm) instead of AI tools for Minikube deployment.**

### Rationale

1. **Tool Availability**: Gordon, kubectl-ai, and kagent are NOT available on the development system
   - User confirmed: "you dont have to need yo use all the tec in this only use which tech is availble and install on this laptop and execute it"
   - Geographic or licensing restrictions may prevent access to these tools
   - Installation not possible within current environment constraints

2. **Existing Infrastructure is Compliant**:
   - Dockerfiles already exist and follow all constitutional requirements (multi-stage builds, non-root users, security hardening)
   - Helm chart templates already exist with proper structure
   - No need to generate Dockerfiles or manifests from scratch

3. **Constitution Allows Fallback**:
   - Section XVIII (Emergency Protocols) explicitly states: "If Gordon Not Available: Write Dockerfiles manually following multi-stage pattern"
   - "If kubectl-ai/kagent Not Working: Generate Helm charts manually using helm create command"
   - Standard CLI tools are a valid fallback under emergency protocols

4. **Standard Tools Are Sufficient**:
   - Docker CLI provides all necessary build and image management capabilities
   - kubectl handles all deployment and management operations
   - Helm 3.x provides package management for complex deployments
   - These tools are well-documented, reliable, and industry-standard

## Alternatives Considered

### Alternative 1: Delay Until AI Tools Available
**Rejected because**:
- Would block deployment progress indefinitely
- User explicitly confirmed to use available tools
- No clear timeline for AI tool availability

### Alternative 2: Use AI Tools via Cloud Services
**Rejected because**:
- Would require cloud infrastructure setup (violates local development scope)
- Adds unnecessary complexity and cost
- Network latency would slow development workflow

### Alternative 3: Write Manual YAML and Dockerfiles
**Rejected because**:
- Existing Dockerfiles and Helm charts are already compliant
- No need to recreate existing infrastructure
- Would introduce unnecessary rework

## Consequences

### Positive
- ✅ Deployment can proceed without blocking on AI tool availability
- ✅ Uses industry-standard, well-documented tools
- ✅ Maintains constitutional compliance (via emergency protocols)
- ✅ Leverages existing compliant infrastructure (Dockerfiles, Helm charts)
- ✅ Reduces dependency on external AI services

### Negative
- ❌ Deviates from constitutional requirements (Section X)
- ❌ Loses AI-assisted optimization and suggestions
- ❌ Manual operations may be slower than AI-assisted workflows
- ❌ Requires more manual verification and testing

### Neutral
- → Existing Dockerfiles already follow best practices (no Gordon needed)
- → Helm chart templates already exist (no kubectl-ai generation needed)
- → Documentation will focus on standard CLI commands instead of AI tools

## Implementation

### Tool Replacements

| Constitutional Tool | Standard CLI Replacement | Usage |
|-------------------|------------------------|-------|
| Gordon (Docker AI) | Docker CLI (`docker build`) | Build and manage images |
| kubectl-ai | kubectl (`kubectl apply`, `kubectl get`) | Deploy and manage resources |
| kagent | kubectl (`kubectl describe`, `kubectl logs`) | Debug and monitor cluster |
| - | Helm CLI (`helm install`, `helm upgrade`) | Package and deploy applications |

### Updated Workflow

1. **Containerization** (was Gordon):
   ```bash
   docker build -t todo-frontend:1.0.5 ./frontend
   docker build -t todo-backend:2.0.2 ./backend
   docker build -t todo-mcp-server:1.0.2 ./mcp_server
   ```

2. **Manifest Generation** (was kubectl-ai):
   - Use existing Helm chart templates
   - No manual YAML writing required
   - Update `values.yaml` for configuration changes

3. **Deployment** (was kubectl-ai/kagent):
   ```bash
   helm install todo-evolution ./helm-chart
   kubectl get pods
   kubectl logs <pod-name>
   ```

4. **Troubleshooting** (was kagent):
   ```bash
   kubectl describe pod <pod-name>
   kubectl get events
   kubectl top pods
   ```

### Documentation Updates

- Quickstart guide uses standard CLI commands
- Troubleshooting section focuses on `kubectl` and `docker` commands
- No references to AI tools in deployment procedures

## Compliance

### Constitutional Alignment

**Section X (AI-Assisted Operations)**:
- ⚠️ **Deviated from**: Gordon, kubectl-ai, kagent requirements
- ✅ **Compliant via**: Section XVIII Emergency Protocols fallback

**Section XVIII (Emergency Protocols)**:
- ✅ "If Gordon Not Available: Write Dockerfiles manually following multi-stage pattern" → Dockerfiles already exist and are compliant
- ✅ "If kubectl-ai/kagent Not Working: Generate Helm charts manually using helm create command" → Helm chart already exists
- ✅ Document in ADR: This ADR explains the deviation

### Requirements Met

All constitutional requirements are met:
- ✅ Multi-stage Dockerfiles with security hardening
- ✅ Semantic versioning for image tags
- ✅ Helm chart with proper structure
- ✅ Non-root user containers
- ✅ Health probes and resource limits
- ✅ Kubernetes standard labels
- ✅ Secret management
- ✅ Documentation and quickstart guide

## References

- Constitution: `.specify/memory/constitution.md` (Phase IV, Section X and XVIII)
- Feature Spec: `specs/011-minikube-helm-deploy/spec.md`
- Implementation Plan: `specs/011-minikube-helm-deploy/plan.md`
- Dockerfiles: `frontend/Dockerfile`, `backend/Dockerfile`, `mcp_server/Dockerfile`
- Helm Chart: `helm-chart/`

## Revision History

- **2025-12-30**: Initial acceptance (v1.0.0)
- Author: Claude Code (spec-driven workflow)
- Status: Accepted

---

**ADR Status**: ✅ Accepted and Active

**Next Review**: After successful Minikube deployment completion
