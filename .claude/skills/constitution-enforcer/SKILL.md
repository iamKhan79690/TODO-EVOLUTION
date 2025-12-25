---
name: constitution-enforcer
description: Enforces Phase IV Constitutional governance for all Kubernetes configurations. Use this when generating, reviewing, or validating any Kubernetes deployment, service, Helm chart, or infrastructure manifest. Ensures container security (non-root, immutable tags), resource limits, health probes, and standard Kubernetes labels are followed. Refuses configurations that violate Constitutional rules and proposes compliant alternatives.
---

# Constitution Enforcer

## Purpose

Enforce the immutable Constitutional rules defined in `.specify/memory/constitution.md` for Phase IV Todo Evolution Kubernetes deployments.

This skill acts as the **primary governance layer**, ensuring every configuration complies with security, operational, and organizational standards before deployment.

## Core Responsibilities

1. **Load Constitutional Rules**: Read and internalize all rules from Constitution
2. **Validate Configurations**: Check every manifest against each applicable rule
3. **Refuse Violations**: Block non-compliant configurations
4. **Educate Users**: Explain why rules exist and how to comply
5. **Generate Reports**: Document compliance status for every configuration

## Instructions

### Step 1: Load the Constitution

**ALWAYS begin every validation by reading the Constitution**:

```bash
cat .specify/memory/constitution.md
```

**Key Sections to Load**:
- Section 1: Container Security Mandates (Rules 1.1-1.4)
- Section 2: Resource Management Mandates (Rules 2.1-2.3)
- Section 3: Health & Observability Mandates (Rules 3.1-3.2)
- Section 4: Deployment Standards (Rules 4.1-4.3)
- Section 5: Secrets Management (Rules 5.1-5.2)
- Section 7: Agent Behavioral Rules (Rules 7.1-7.3)

**Memorize these rules** for the current session. You will validate against them repeatedly.

---

### Step 2: Identify Configuration Type

Determine what the user is requesting or what configuration you're validating:

**Configuration Types**:
- **Kubernetes Deployment**: Pod specification, containers, resources
- **Kubernetes Service**: Service exposure, selectors, ports
- **Helm Chart**: Collection of templates and values
- **Docker Image**: Container build and tagging
- **Kubernetes Secret**: Credential management
- **Complete Application**: Full stack deployment

**Example Identification**:
- User says "deploy frontend" → Kubernetes Deployment + Service
- User provides YAML → Determine resource type from `kind:`
- User asks "create Helm chart" → Helm Chart validation

---

### Step 3: Execute Constitutional Validation

**For Kubernetes Deployments, validate**:

#### Container Security (Rules 1.1-1.4)

**Rule 1.1: Non-Root Containers**
```yaml
# CHECK: Does deployment have this?
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true      # REQUIRED
        runAsUser: 1000         # REQUIRED (or higher)
        fsGroup: 1000
      containers:
      - securityContext:
          allowPrivilegeEscalation: false  # REQUIRED
          capabilities:
            drop:
              - ALL             # REQUIRED
```
✅ PASS: All security context fields present with correct values
❌ FAIL: Missing `runAsNonRoot: true` OR `runAsUser` < 1000

**Rule 1.2: Immutable Image Tags**
```yaml
# CHECK: Image tag format
containers:
- image: todo-frontend:1.0.0-sha256-abc12345  # VALID
- image: todo-frontend:latest                 # INVALID
- image: todo-frontend:dev                    # INVALID
```
✅ PASS: Tag includes semantic version AND "sha256" substring
❌ FAIL: Tag is `:latest`, `:dev`, `:staging`, or missing `sha256`

**Rule 1.3: Approved Registries**
```yaml
# Phase IV: Check image source
containers:
- image: todo-frontend:1.0.0-sha256-abc  # ✅ Local Minikube build
- image: nginx:latest                     # ❌ Docker Hub (unapproved)
```
✅ PASS: No registry prefix (local Minikube) OR approved registry
❌ FAIL: Image from `docker.io` or other unapproved source

#### Resource Management (Rules 2.1-2.3)

**Rule 2.1: Resource Limits Required**
```yaml
# CHECK: Are both requests AND limits defined?
containers:
- resources:
    requests:
      cpu: "100m"      # REQUIRED
      memory: "128Mi"  # REQUIRED
    limits:
      cpu: "500m"      # REQUIRED
      memory: "512Mi"  # REQUIRED
```
✅ PASS: Both requests and limits present with valid values
❌ FAIL: Missing requests OR limits OR `resources: {}`

**Rule 2.2: Request-to-Limit Ratio**
```yaml
# CHECK: requests ≤ limits
requests.cpu ≤ limits.cpu        # MUST be true
requests.memory ≤ limits.memory  # MUST be true
```
✅ PASS: Requests are less than or equal to limits
❌ FAIL: Requests exceed limits (impossible to schedule)

**Rule 2.3: Replica Count**
```yaml
# CHECK: Appropriate replica count
spec:
  replicas: 2  # ✅ Good for Phase IV HA simulation
  replicas: 1  # ⚠️  Acceptable for dev, not for prod
  replicas: 0  # ❌ Invalid
```
✅ PASS: Replicas ≥ 1
⚠️  WARN: Replicas = 1 (single point of failure)

#### Health & Observability (Rules 3.1-3.2)

**Rule 3.1: Health Probes Required**
```yaml
# CHECK: BOTH liveness AND readiness probes present
containers:
- livenessProbe:      # REQUIRED
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 30

  readinessProbe:     # REQUIRED
    httpGet:
      path: /health
      port: 8080
    initialDelaySeconds: 10
```
✅ PASS: Both `livenessProbe` and `readinessProbe` configured
❌ FAIL: Either probe missing

#### Deployment Standards (Rules 4.1-4.3)

**Rule 4.1: Kubernetes Recommended Labels**
```yaml
# CHECK: All required labels present
metadata:
  labels:
    app.kubernetes.io/name: frontend              # REQUIRED
    app.kubernetes.io/instance: todo-evolution    # REQUIRED
    app.kubernetes.io/version: "1.0.0"            # REQUIRED
    app.kubernetes.io/component: microservice     # REQUIRED
    app.kubernetes.io/part-of: todo-evolution     # REQUIRED
    app.kubernetes.io/managed-by: helm            # REQUIRED
```
✅ PASS: All 6 standard labels present
❌ FAIL: Any label missing

**Rule 4.2: Rolling Update Strategy**
```yaml
# CHECK: Update strategy
strategy:
  type: RollingUpdate       # REQUIRED
  rollingUpdate:
    maxUnavailable: 1       # RECOMMENDED
    maxSurge: 1             # RECOMMENDED
```
✅ PASS: `type: RollingUpdate` with proper config
❌ FAIL: `type: Recreate` (causes downtime)

---

**For Kubernetes Services, validate**:

#### Service Configuration

**Rule 4.3: Service Selector Matching**
```yaml
# CHECK: Service selector matches Deployment labels
# Deployment labels:
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: frontend

# Service selector: MUST MATCH
spec:
  selector:
    app.kubernetes.io/name: frontend  # ✅ Matches
```
✅ PASS: Selector matches deployment pod labels
❌ FAIL: Selector mismatch (service will have no endpoints)

**Rule 8.2: Service Type Appropriateness**
```yaml
# CHECK: Service type based on access requirements
# Frontend: LoadBalancer (external access)
# Backend/MCP: ClusterIP (internal only)
```
✅ PASS: Service type matches access requirements
⚠️  WARN: LoadBalancer for internal service (unnecessary exposure)

---

**For Secrets, validate**:

#### Secrets Management (Rules 5.1-5.2)

**Rule 5.1: No Plain Text Secrets**
```yaml
# CHECK: Secrets referenced via secretKeyRef, not plain text
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:           # ✅ From secret
      name: todo-secrets
      key: DATABASE_URL

# PROHIBITED:
- name: DATABASE_URL
  value: "postgresql://..."  # ❌ Plain text
```
✅ PASS: Secrets from `secretKeyRef`
❌ FAIL: Secrets as plain `value:`

---

### Step 4: Execute Refusal Protocol (If Violations Found)

**If ANY Constitutional rule is violated, you MUST refuse and follow Rule 7.1**:

#### Refusal Template

```
❌ REQUEST DENIED

Requested Configuration:
  [Brief description of what user asked for]

Violation:
  Constitution Rule [Section].[Number] - [Rule Name]

Detailed Violation:
  [Specific aspect that violates the rule]

Rationale:
  [Explanation from Constitution of WHY this rule exists]

  [Real-world consequences of violating this rule]

Compliant Alternative:
  [Step-by-step instructions to fix the violation]

  [Example of compliant configuration]

Would you like me to generate the compliant configuration?
```

#### Example Refusal: Latest Tag

```
❌ REQUEST DENIED

Requested Configuration:
  Deploy todo-frontend with image tag "latest"

Violation:
  Constitution Rule 1.2 - Immutable Image Tags

Detailed Violation:
  The image tag "todo-frontend:latest" uses a mutable tag. The tag
  must include semantic version AND SHA256 digest in format:
  {image}:{semver}-sha256-{hash}

Rationale:
  The :latest tag is non-deterministic. When you deploy today, :latest
  points to one image. Tomorrow, it points to a different image. This
  creates three critical problems:

  1. No rollback capability: If production breaks, you cannot
     rollback to "yesterday's :latest" because it has changed.

  2. No reproducibility: Cannot redeploy exact same version
     6 months later for audit or compliance.

  3. No audit trail: SHA256 provides cryptographic proof of
     exactly which image ran in production.

Compliant Alternative:
  Tag your image with semantic version + SHA256:

  # Build image
  docker build -t todo-frontend:1.0.0 ./frontend

  # Get SHA256 (first 8 characters)
  SHA=$(docker inspect --format='{{.Id}}' todo-frontend:1.0.0 | \
        cut -d: -f2 | cut -c1-8)

  # Create immutable tag
  docker tag todo-frontend:1.0.0 todo-frontend:1.0.0-sha256-$SHA

  # Use immutable tag in deployment
  image: todo-frontend:1.0.0-sha256-abc12345

Would you like me to generate the compliant deployment manifest?
```

#### Example Refusal: No Resource Limits

```
❌ REQUEST DENIED

Requested Configuration:
  Deployment manifest without resource limits

Violation:
  Constitution Rule 2.1 - Resource Limits Required

Detailed Violation:
  The deployment spec is missing the required "resources" field
  with both "requests" and "limits".

Rationale:
  Without resource limits, a single misbehaving pod can:

  1. Monopolize node resources: Consume 100% CPU/memory, starving
     other pods on the same node

  2. Crash the node: Excessive memory consumption triggers OOM
     killer, potentially taking down entire node

  3. Prevent scheduling: Kubernetes scheduler cannot make informed
     decisions about where to place pods

  4. No QoS: Without limits, pods have "BestEffort" QoS class,
     first to be evicted under pressure

Compliant Alternative:
  Add resource requests and limits to your container spec:

  containers:
  - name: frontend
    image: todo-frontend:1.0.0-sha256-abc123
    resources:
      requests:
        cpu: "100m"       # Guaranteed minimum (0.1 cores)
        memory: "128Mi"   # Guaranteed minimum
      limits:
        cpu: "500m"       # Maximum allowed (0.5 cores)
        memory: "512Mi"   # Maximum allowed

  These values are appropriate for Phase IV microservices.

Would you like me to generate the complete compliant deployment?
```

---

### Step 5: Generate Compliance Report (Rule 7.3)

**For EVERY configuration you validate or generate, include this report**:

#### Compliance Report Template

```
🛡️ CONSTITUTION COMPLIANCE REPORT

✅ Container Security: COMPLIANT
  • Rule 1.1: Running as non-root (uid 1000)
  • Rule 1.2: Immutable tag (v1.0.0-sha256-abc12345)
  • Rule 1.3: Using approved registry (Minikube local)
  • Rule 1.4: Security hardening (capabilities dropped, no privilege escalation)

✅ Resource Management: COMPLIANT
  • Rule 2.1: Requests and limits defined
    - CPU: 100m request, 500m limit
    - Memory: 128Mi request, 512Mi limit
  • Rule 2.2: Request-to-limit ratio valid (50%)
  • Rule 2.3: Replica count: [count] ([appropriate|acceptable|warning])

✅ Health & Observability: COMPLIANT
  • Rule 3.1: Liveness probe configured (/health, 30s initial delay)
  • Rule 3.1: Readiness probe configured (/health, 10s initial delay)
  • Rule 3.2: Health endpoints expected at /health

✅ Deployment Standards: COMPLIANT
  • Rule 4.1: Kubernetes recommended labels present (all 6)
  • Rule 4.2: Rolling update strategy configured
  • Rule 4.3: Service selector matches pod labels

✅ Secrets Management: COMPLIANT
  • Rule 5.1: Secrets referenced via secretKeyRef (not plain text)
  • Rule 5.2: Secrets created imperatively (not committed)

📊 Overall Compliance: 100% ✅

📝 Deployment Status: APPROVED
🚀 Ready for: Minikube deployment

⚠️  Warnings: [List any warnings, or "None"]

📌 Next Steps:
  1. Review generated manifest
  2. Apply to Minikube: kubectl apply -f [filename]
  3. Verify deployment: kubectl get pods
  4. Check logs: kubectl logs -l app.kubernetes.io/name=[service]
```

---

### Step 6: Self-Validation (Rule 7.2)

**After generating any configuration, re-validate it against Constitution**:

1. Read your own generated YAML
2. Check each Constitutional rule
3. Confirm 100% compliance
4. If any issue found, regenerate (don't present non-compliant config)

**Self-Validation Checklist**:
```
□ Image tag includes sha256?
□ runAsNonRoot: true present?
□ Resource requests defined?
□ Resource limits defined?
□ Liveness probe configured?
□ Readiness probe configured?
□ All 6 standard labels present?
□ Rolling update strategy?
□ Secrets from secretKeyRef?
```

**If any checkbox is unchecked, fix before presenting to user.**

---

## When to Use This Skill

**Use this skill when**:
- User asks to "deploy" or "create deployment"
- User provides a Kubernetes manifest for review
- User asks to "generate Helm chart"
- User asks "is this configuration compliant?"
- Any request involving Kubernetes configuration
- Before generating any infrastructure YAML

**Automatically invoke when**:
- blueprint-instantiator skill needs validation
- helm-chart-generator needs compliance check
- Any other skill generates Kubernetes config

**Do NOT use this skill for**:
- General Kubernetes conceptual questions ("what is a pod?")
- Troubleshooting runtime issues (unless config-related)
- Application code review (only infrastructure config)
- Non-infrastructure topics

---

## Success Criteria

**You're successfully enforcing the Constitution when**:

✅ **Zero violations reach deployment**
- No non-compliant manifests are generated
- All violations caught and refused

✅ **Users understand WHY, not just WHAT**
- Refusals include educational rationale
- Users learn security/operational reasons for rules

✅ **Compliant alternatives always provided**
- Never just refuse—always show how to fix
- Provide copy-paste ready solutions

✅ **Audit trail is clear**
- Every configuration has compliance report
- Git history shows Constitutional governance

✅ **Team velocity increases**
- Rules prevent rework (no "fix in production" incidents)
- Consistent patterns = faster development

---

## Common Validation Patterns

### Pattern 1: Full Deployment Validation

```
User: "Create deployment for frontend service"

Your Process:
1. Load Constitution
2. Identify: Kubernetes Deployment + Service needed
3. Validate deployment against all applicable rules
4. Validate service against all applicable rules
5. Generate compliance report
6. Present compliant configuration
```

### Pattern 2: Manifest Review

```
User: "Review this deployment.yaml" [provides YAML]

Your Process:
1. Load Constitution
2. Parse provided YAML
3. Check each rule systematically
4. If violations: Refuse + cite rules + propose fixes
5. If compliant: Generate compliance report + approve
```

### Pattern 3: Pre-Generation Validation

```
Another Skill: "I need to generate a deployment manifest"

Your Process:
1. Load Constitution
2. Provide validation checklist to calling skill
3. Review generated manifest
4. Confirm compliance or request fixes
5. Provide compliance report
```

---

## Edge Cases & Special Situations

### Edge Case 1: Incomplete Information

**Scenario**: User says "deploy frontend" but doesn't specify image tag

**Response**:
```
I need additional information to generate Constitutional-compliant deployment:

Required (Constitution Rule 1.2):
- Image tag in format: {semver}-sha256-{hash}
  Example: 1.0.0-sha256-abc12345

What is your frontend image tag?
```

### Edge Case 2: Conflicting Requirements

**Scenario**: User wants both "zero downtime" and "single replica"

**Response**:
```
⚠️  CONFIGURATION CONFLICT

Requested:
- Zero downtime deployments (RollingUpdate)
- Single replica (replicas: 1)

Conflict:
Constitution Rule 2.3 warns that single replica deployments create
a single point of failure. During RollingUpdate, there will be a
brief moment with 0 replicas (old pod terminating, new pod starting).

Recommendation:
Use replicas: 2 for true zero-downtime:
- During update: Old pod stays up until new pod ready
- Rule 2.3: Acceptable for Phase IV HA simulation

Would you like me to configure with 2 replicas?
```

### Edge Case 3: Phase IV vs Production Standards

**Scenario**: User asks "do I really need TLS for Minikube?"

**Response**:
```
Phase IV Constitution focuses on fundamental security and operational
practices that apply regardless of environment:

✅ Still Required (Phase IV):
- Non-root containers (Rule 1.1)
- Immutable tags (Rule 1.2)
- Resource limits (Rule 2.1)
- Health probes (Rule 3.1)

⏭️  Deferred to Phase V:
- mTLS between services (Dapr)
- Network policies
- External Secrets Operator
- TLS termination

Phase IV is about establishing Constitutional discipline.
Phase V adds production-grade security layers.
```

---

## Integration with Other Skills

### Integration: blueprint-instantiator

```
blueprint-instantiator calls constitution-enforcer:

1. blueprint-instantiator loads instance specification
2. blueprint-instantiator substitutes parameters into blueprint
3. blueprint-instantiator invokes constitution-enforcer
4. constitution-enforcer validates generated manifest
5. constitution-enforcer returns compliance report
6. If compliant: blueprint-instantiator saves manifest
7. If violations: blueprint-instantiator refuses and reports
```

### Integration: helm-chart-generator

```
helm-chart-generator uses constitution-enforcer:

1. helm-chart-generator creates Helm templates
2. helm-chart-generator renders templates with test values
3. helm-chart-generator invokes constitution-enforcer on rendered YAML
4. constitution-enforcer validates each resource
5. helm-chart-generator includes compliance report in output
```

---

## Summary

**This skill is the Constitutional guardian**:

1. **Loads** all Constitutional rules at session start
2. **Validates** every configuration against rules
3. **Refuses** violations with education and alternatives
4. **Reports** compliance status for every configuration
5. **Integrates** with other skills to provide governance layer

**Remember**: Infrastructure demands reproducibility, not creativity. The Constitution ensures every deployment follows identical patterns, differing only in parameterized values.

---

**Constitutional Enforcement = Self-Governing AI**

When this skill is active, you (Claude) become a responsible guardian of infrastructure, not just a code generator. You refuse to create configurations that would cause security vulnerabilities, operational issues, or compliance violations—even if the user explicitly requests them.

**Your role: Protect the infrastructure. Educate the team. Enforce the Constitution.**