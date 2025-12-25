---
name: blueprint-instantiator
description: Instantiates Constitutional-compliant Kubernetes manifests from blueprint templates and instance parameters. Use when applying blueprints, generating deployments from specifications, or creating infrastructure from templates. Ensures consistency and reproducibility across all microservice deployments by using reusable patterns instead of one-off configurations.
---

# Blueprint Instantiator

## Purpose

Generate Constitutional-compliant Kubernetes manifests by instantiating blueprint templates with instance-specific parameters. This skill transforms parameterized templates into concrete YAML configurations while ensuring Constitutional governance.

**Core Principle**: Infrastructure demands reproducibility. Deploy the same blueprint 100 times with different parameters, get 100 identical structures, differing only in values.

## Core Responsibilities

1. **Load Blueprint Templates**: Read reusable blueprint specifications
2. **Load Instance Parameters**: Read service-specific parameter files
3. **Substitute Variables**: Replace `{{parameter}}` with actual values
4. **Invoke Constitution Enforcer**: Validate compliance before output
5. **Generate Manifests**: Write Constitutional-compliant YAML files
6. **Report Success**: Document instantiation and compliance

## Instructions

### Step 1: Validate Inputs

**Required Inputs**:
1. **Instance Specification Path**: Location of instance parameter file
   - Format: `specs/instances/{service-name}.instance.md`
   - Example: `specs/instances/frontend.instance.md`

**Input Validation**:
```
□ Instance file exists?
□ Instance file references blueprint(s)?
□ All required parameters present?
□ Parameter types match blueprint expectations?
```

**If validation fails**, inform user of missing/invalid inputs.

---

### Step 2: Load Instance Specification

**Read instance file** from `specs/instances/{service-name}.instance.md`

**Instance File Structure**:
```markdown
# {Service Name} Instance
Blueprint References:
- Deployment: @specs/blueprints/microservice-deployment.blueprint.md
- Service: @specs/blueprints/microservice-service.blueprint.md

## Deployment Parameters
```yaml
service_name: frontend
image: todo-frontend
tag: 1.0.0-sha256-abc123
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
```

**Extract**:
- Blueprint references (which templates to use)
- Deployment parameters (values for deployment blueprint)
- Service parameters (values for service blueprint)
- Environment variables (if specified)

---

### Step 3: Load Blueprint Templates

**For each referenced blueprint**, read template from `specs/blueprints/{blueprint-name}.blueprint.md`

**Blueprint File Structure**:
```markdown
# Blueprint Name
Version: 1.0.0
Type: kubernetes/deployment

## Parameters
[Table of required/optional parameters]

## Template Structure
[Kubernetes YAML with {{variable}} placeholders]

## Validation Rules
[Rules for parameter values]
```

**Extract**:
- Template YAML structure
- Required parameters list
- Optional parameters with defaults
- Validation rules

---

### Step 4: Invoke Constitution Enforcer

**CRITICAL: Before generating ANY manifest, invoke constitution-enforcer skill**

**Why**: Constitution enforcer loads all governance rules and validates compliance. This ensures generated manifests satisfy security, operational, and organizational requirements.

**Invocation**:
```
constitution-enforcer: I'm about to generate Kubernetes manifests.
Please load Constitutional rules for validation.

Manifest types: Deployment, Service
Service name: {service_name}
```

**Constitution Enforcer Response**: Confirms rules loaded and provides validation checklist.

---

### Step 5: Validate Parameters Against Blueprint Rules

**Before substitution, validate parameters**:

**From Blueprint Validation Rules**, check each parameter:

```yaml
# Example: microservice-deployment.blueprint.md validation rules
1. service_name must be lowercase alphanumeric
2. tag must include "sha256" substring
3. replicas must be >= 1
4. cpu_request <= cpu_limit
5. memory_request <= memory_limit
6. health_path must start with /
```

**Validation Logic**:
```python
# Pseudocode
for rule in blueprint.validation_rules:
    if not rule.check(parameters):
        REFUSE:
          "Parameter validation failed"
          "Rule: {rule.description}"
          "Value: {parameter.value}"
          "Expected: {rule.expected}"
          "Fix: {rule.suggestion}"
```

**If validation fails**: Refuse with specific rule citation and fix suggestion.

---

### Step 6: Substitute Variables

**Replace `{{variable}}` placeholders in blueprint with actual values from instance**

**Substitution Algorithm**:

```python
# Pseudocode
template = load_blueprint_template()
parameters = load_instance_parameters()

for variable in template.find_all_variables():
    if variable in parameters:
        template.replace(f"{{{{variable}}}}", parameters[variable])
    elif variable has default in blueprint:
        template.replace(f"{{{{variable}}}}", default_value)
    else:
        ERROR: Required parameter {variable} missing
```

**Example Substitution**:

**Blueprint Template**:
```yaml
metadata:
  name: {{service_name}}-deployment
  labels:
    app.kubernetes.io/name: {{service_name}}
    app.kubernetes.io/version: "{{tag}}"

spec:
  replicas: {{replicas}}
  template:
    spec:
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
```

**Instance Parameters**:
```yaml
service_name: frontend
image: todo-frontend
tag: 1.0.0-sha256-abc123
port: 3000
replicas: 2
cpu_request: 100m
cpu_limit: 500m
memory_request: 128Mi
memory_limit: 512Mi
```

**Generated Manifest** (after substitution):
```yaml
metadata:
  name: frontend-deployment
  labels:
    app.kubernetes.io/name: frontend
    app.kubernetes.io/version: "1.0.0-sha256-abc123"

spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: frontend
        image: todo-frontend:1.0.0-sha256-abc123
        ports:
        - containerPort: 3000
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

---

### Step 7: Validate Generated Manifest

**After substitution, validate the generated YAML**:

#### A. YAML Syntax Validation
```
□ Valid YAML syntax?
□ Proper indentation?
□ All keys have values?
□ No unresolved {{variables}}?
```

#### B. Kubernetes Resource Validation
```
□ Valid apiVersion?
□ Valid kind?
□ Required metadata present (name, labels)?
□ Valid spec structure for resource type?
```

#### C. Constitutional Compliance Validation

**Invoke constitution-enforcer again** to validate generated manifest:

```
constitution-enforcer: Please validate this generated manifest
against all Constitutional rules.

[Provide generated YAML]
```

**Constitution Enforcer checks**:
- Rule 1.1: Non-root container
- Rule 1.2: Immutable tag
- Rule 2.1: Resource limits
- Rule 3.1: Health probes
- Rule 4.1: Standard labels
- [All other applicable rules]

**If Constitutional violations found**:
- DO NOT save manifest
- Report violations to user
- Suggest parameter adjustments

---

### Step 8: Save Manifest Files

**If all validations pass**, write manifests to disk:

**Output Structure**:
```
manifests/
├── {service-name}-deployment.yaml
└── {service-name}-service.yaml
```

**File Naming Convention**:
- Format: `{service-name}-{resource-type}.yaml`
- Examples:
  - `frontend-deployment.yaml`
  - `frontend-service.yaml`
  - `backend-deployment.yaml`

**Write Operation**:
```python
# Pseudocode
deployment_manifest = generate_from_blueprint(
    blueprint="microservice-deployment",
    parameters=instance.deployment_parameters
)

service_manifest = generate_from_blueprint(
    blueprint="microservice-service",
    parameters=instance.service_parameters
)

write_file(f"manifests/{service_name}-deployment.yaml", deployment_manifest)
write_file(f"manifests/{service_name}-service.yaml", service_manifest)
```

---

### Step 9: Generate Instantiation Report

**For every successful instantiation, provide detailed report**:

```
✅ BLUEPRINT INSTANTIATION SUCCESSFUL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 INSTANTIATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Blueprint Used:
  • microservice-deployment.blueprint.md (v1.0.0)
  • microservice-service.blueprint.md (v1.0.0)

Instance Specification:
  • specs/instances/frontend.instance.md

Generated Manifests:
  • manifests/frontend-deployment.yaml (Deployment)
  • manifests/frontend-service.yaml (Service)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PARAMETERS APPLIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deployment Parameters:
  • service_name: frontend
  • image: todo-frontend
  • tag: 1.0.0-sha256-abc123
  • port: 3000
  • replicas: 2
  • cpu_request: 100m
  • cpu_limit: 500m
  • memory_request: 128Mi
  • memory_limit: 512Mi
  • health_path: /health

Service Parameters:
  • service_name: frontend
  • service_type: LoadBalancer
  • port: 80
  • target_port: 3000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️  CONSTITUTIONAL COMPLIANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Container Security: COMPLIANT
  • Rule 1.1: Running as non-root (uid 1000)
  • Rule 1.2: Immutable tag (includes sha256)
  • Rule 1.3: Approved registry (Minikube local)
  • Rule 1.4: Security hardening applied

✅ Resource Management: COMPLIANT
  • Rule 2.1: Requests and limits defined
  • Rule 2.2: Request-to-limit ratio valid (50%)
  • Rule 2.3: Replica count: 2 (appropriate for HA)

✅ Health & Observability: COMPLIANT
  • Rule 3.1: Liveness probe configured
  • Rule 3.1: Readiness probe configured

✅ Deployment Standards: COMPLIANT
  • Rule 4.1: Kubernetes recommended labels (all 6)
  • Rule 4.2: Rolling update strategy configured
  • Rule 4.3: Service selector matches pod labels

✅ Secrets Management: COMPLIANT
  • Rule 5.1: Secrets from secretKeyRef (when applicable)

📊 Overall Compliance: 100% ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 DEPLOYMENT READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: APPROVED for deployment
Target: Minikube (local Kubernetes)

Next Steps:
  1. Review generated manifests:
     cat manifests/frontend-deployment.yaml
     cat manifests/frontend-service.yaml

  2. Apply to Minikube:
     kubectl apply -f manifests/frontend-deployment.yaml
     kubectl apply -f manifests/frontend-service.yaml

  3. Verify deployment:
     kubectl get pods -l app.kubernetes.io/name=frontend
     kubectl get service frontend-service

  4. Access service:
     minikube service frontend-service --url

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## When to Use This Skill

**Use this skill when**:
- User says "apply blueprint for {service}"
- User says "instantiate {service} deployment"
- User says "generate manifests from blueprints"
- User provides instance specification and asks for manifest generation
- You need to create deployment from template + parameters

**Automatically invoke when**:
- User mentions "blueprint" in request
- User references instance specification file
- Another skill needs template instantiation

**Do NOT use this skill for**:
- Creating blueprints themselves (blueprints are manually designed)
- Modifying existing manifests directly (use for regeneration only)
- Non-blueprint-based configurations
- Ad-hoc YAML generation (discouraged by Constitution Rule 8.3)

---

## Common Workflow Patterns

### Pattern 1: Single Service Instantiation

```
User: "Apply blueprint for frontend service"

Your Process:
1. Locate instance spec: specs/instances/frontend.instance.md
2. Read instance parameters
3. Identify referenced blueprints
4. Load blueprint templates
5. Invoke constitution-enforcer (load rules)
6. Validate parameters
7. Substitute variables
8. Validate generated YAML
9. Invoke constitution-enforcer (validate manifest)
10. Save manifests to manifests/ directory
11. Generate instantiation report
```

### Pattern 2: Batch Instantiation

```
User: "Apply blueprints for all services (frontend, backend, mcp)"

Your Process:
1. For each service in [frontend, backend, mcp-server]:
   a. Load instance spec
   b. Instantiate deployment
   c. Instantiate service
   d. Validate compliance
   e. Save manifests
2. Generate combined report showing all 3 services
```

### Pattern 3: Regeneration After Parameter Change

```
User: "I updated frontend replicas to 3, regenerate"

Your Process:
1. Read updated frontend.instance.md
2. Detect changed parameters (replicas: 2 → 3)
3. Instantiate fresh manifests
4. Show diff from previous version
5. Validate compliance
6. Save new manifests
7. Report changes
```

---

## Error Handling

### Error 1: Instance File Not Found

```
❌ INSTANTIATION FAILED

Error: Instance specification not found
  Path: specs/instances/frontend.instance.md

Resolution:
  1. Check file exists at the path
  2. Ensure correct spelling
  3. Create instance spec if missing

Template for creating instance spec:
  [Provide instance spec template]
```

### Error 2: Blueprint Reference Invalid

```
❌ INSTANTIATION FAILED

Error: Blueprint not found
  Referenced: @specs/blueprints/microservice-deploy.blueprint.md
  Actual name: microservice-deployment.blueprint.md (note: "deployment" not "deploy")

Resolution:
  Fix blueprint reference in instance spec to:
  @specs/blueprints/microservice-deployment.blueprint.md
```

### Error 3: Missing Required Parameter

```
❌ INSTANTIATION FAILED

Error: Required parameter missing
  Blueprint: microservice-deployment.blueprint.md
  Missing: tag
  Required by: Constitution Rule 1.2 (Immutable Image Tags)

Resolution:
  Add to instance spec:

  ```yaml
  tag: 1.0.0-sha256-abc12345  # Format: {semver}-sha256-{hash}
  ```
```

### Error 4: Parameter Validation Failed

```
❌ INSTANTIATION FAILED

Error: Parameter validation failed
  Parameter: replicas
  Value: 0
  Rule: Replicas must be >= 1

Resolution:
  Update instance spec:

  replicas: 1  # Minimum 1 for functional deployment
```

### Error 5: Constitutional Violation in Generated Manifest

```
❌ INSTANTIATION FAILED

Error: Generated manifest violates Constitution
  Rule: 1.2 - Immutable Image Tags
  Issue: Tag "todo-frontend:latest" uses mutable tag

Resolution:
  Fix instance parameter:

  # Current (invalid):
  tag: latest

  # Corrected (valid):
  tag: 1.0.0-sha256-abc12345
```

---

## Integration with Constitution Enforcer

**This skill and constitution-enforcer work together**:

```
┌──────────────────────────┐
│ blueprint-instantiator   │
│                          │
│ 1. Load templates        │
│ 2. Load parameters       │
└────────┬─────────────────┘
         │
         ▼ (invoke)
┌──────────────────────────┐
│ constitution-enforcer    │
│                          │
│ 3. Load Constitution     │
│ 4. Provide validation    │
│    checklist             │
└────────┬─────────────────┘
         │
         ▼ (returns)
┌──────────────────────────┐
│ blueprint-instantiator   │
│                          │
│ 5. Substitute variables  │
│ 6. Generate YAML         │
└────────┬─────────────────┘
         │
         ▼ (invoke)
┌──────────────────────────┐
│ constitution-enforcer    │
│                          │
│ 7. Validate manifest     │
│ 8. Generate report       │
└────────┬─────────────────┘
         │
         ▼ (if compliant)
┌──────────────────────────┐
│ blueprint-instantiator   │
│                          │
│ 9. Save manifests        │
│ 10. Report success       │
└──────────────────────────┘
```

**Key Interactions**:
1. **Pre-instantiation**: Constitution enforcer loads rules
2. **Post-generation**: Constitution enforcer validates output
3. **Refusal coordination**: If enforcer refuses, instantiator doesn't save

---

## Blueprint Version Tracking

**Track which blueprint versions generated which manifests**:

**Add annotation to generated manifests**:
```yaml
metadata:
  name: frontend-deployment
  annotations:
    blueprint.panaversity.org/source: "microservice-deployment.blueprint.md"
    blueprint.panaversity.org/version: "1.0.0"
    blueprint.panaversity.org/instance: "frontend.instance.md"
    blueprint.panaversity.org/generated: "2025-12-21T10:30:00Z"
    constitution.panaversity.org/version: "1.0.0"
    constitution.panaversity.org/compliance: "100%"
```

**Why**: Audit trail. Know exactly which blueprint version produced which manifest.

---

## Reproducibility Guarantee

**This skill's purpose**: Ensure that deploying the same blueprint with the same parameters ALWAYS produces identical manifests.

**Reproducibility Test**:
```
# Generate manifest
blueprint-instantiator: Apply frontend.instance.md
  Output: manifests/frontend-deployment.yaml (SHA256: abc123)

# Generate again (no changes)
blueprint-instantiator: Apply frontend.instance.md
  Output: manifests/frontend-deployment.yaml (SHA256: abc123)

# Verify: SHA256 checksums MUST match
```

**If checksums differ**: Bug in instantiation logic (non-deterministic behavior).

**Guaranteed reproducibility when**:
- Same blueprint version
- Same instance parameters
- Same Constitution version
- Same skill version

---

## Performance Considerations

**Optimization: Blueprint Caching**
```python
# Pseudocode
blueprint_cache = {}

def load_blueprint(path):
    if path in blueprint_cache:
        return blueprint_cache[path]  # Cache hit

    blueprint = read_file(path)
    blueprint_cache[path] = blueprint  # Cache for future
    return blueprint
```

**Why**: If instantiating 100 services, don't re-read same blueprint 100 times.

---

## Advanced Features

### Feature 1: Diff Generation

**Show changes when re-instantiating**:

```
User: "Re-apply frontend blueprint (I changed replicas)"

Output:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 CHANGES DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Previous:
  replicas: 2

Current:
  replicas: 3

Diff:
  spec:
-   replicas: 2
+   replicas: 3

Impact:
  • Will scale up from 2 to 3 pods
  • Additional resource usage: +100m CPU, +128Mi memory
  • Increased availability (can lose 1 pod, still have 2)

Constitutional Compliance: ✅ PASSED (no violations introduced)

Proceed with regeneration? [y/N]
```

### Feature 2: Dry-Run Mode

```
User: "Dry-run: Apply backend blueprint"

Output:
🔍 DRY-RUN MODE (No files will be written)

[Shows full instantiation report]
[Shows generated YAML preview]
[Shows compliance report]

To actually save manifests, confirm: "Apply backend blueprint (confirm)"
```

### Feature 3: Multi-Service Batching

```
User: "Apply all blueprints"

Output:
🔄 BATCH INSTANTIATION: 3 services

Progress:
  ✅ frontend: manifests generated (compliant)
  ✅ backend: manifests generated (compliant)
  ✅ mcp-server: manifests generated (compliant)

Summary:
  • 6 manifests created
  • 100% Constitutional compliance
  • Ready for deployment

[Detailed report for each service]
```

---

## Success Metrics

**This skill is successful when**:

✅ **100% Reproducibility**
- Same inputs → always same outputs
- No non-deterministic behavior

✅ **Zero Manual YAML**
- All manifests generated from blueprints
- No hand-written Kubernetes config

✅ **Constitutional Compliance**
- Every manifest passes constitution-enforcer
- Zero violations in generated code

✅ **Audit Trail**
- Annotations track blueprint source
- Git history shows instance changes
- Compliance reports documented

✅ **Developer Velocity**
- Faster than writing YAML manually
- Fewer errors than hand-crafted manifests
- Consistent patterns across all services

---

## Summary

**This skill transforms infrastructure from art to engineering**:

- **Before**: Each developer writes YAML slightly differently
- **After**: All services use identical patterns, differing only in parameters

**Before**: "Create deployment for new service" (30 minutes of YAML writing)
**After**: "Apply blueprint for new service" (30 seconds of instantiation)

**The Blueprint-Driven Promise**:
1. Create blueprint once
2. Instantiate many times
3. Constitutional compliance guaranteed
4. Reproducibility ensured
5. Consistency maintained

**This is infrastructure as code, done right.**

---

**Blueprint Instantiation = Infrastructure Reproducibility**

When this skill is active, you (Claude) transform parameterized templates into Constitutional-compliant Kubernetes manifests automatically. No manual YAML. No inconsistencies. Just reproducible, governed infrastructure.

**Your role: Instantiate blueprints. Ensure compliance. Guarantee reproducibility.**