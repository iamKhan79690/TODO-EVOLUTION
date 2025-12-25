# Compliance Report Template

This file contains the template for generating Constitutional compliance reports. Use this as a reference when creating compliance reports for validated configurations.

## Report Structure

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
  • Rule 2.3: Replica count: 2 (appropriate for HA)

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

⚠️  Warnings: None

📌 Next Steps:
  1. Review generated manifest
  2. Apply to Minikube: kubectl apply -f [filename]
  3. Verify deployment: kubectl get pods
  4. Check logs: kubectl logs -l app.kubernetes.io/name=[service]
```

## Customization Guidelines

### For Partial Compliance
When some rules fail, use this structure:

```
❌ Container Security: NON-COMPLIANT
  • Rule 1.1: FAILED - Missing runAsNonRoot: true
  • Rule 1.2: COMPLIANT - Immutable tag present
  • Rule 1.3: COMPLIANT - Using approved registry
  • Rule 1.4: FAILED - Missing capabilities drop

[Continue with other sections...]

📊 Overall Compliance: 75% ⚠️

📝 Deployment Status: REJECTED
🚫 Blocking Issues: Security violations must be fixed

⚠️  Warnings: Single replica creates single point of failure

📌 Required Fixes:
  1. Add runAsNonRoot: true to pod securityContext
  2. Add capabilities.drop: [ALL] to container securityContext
```

### For Warnings
Include warnings for acceptable but non-optimal configurations:

```
⚠️  Warnings:
  • Replica count: 1 (single point of failure, consider 2 for HA)
  • Service type: LoadBalancer for internal service (unnecessary exposure)
  • Memory limit: 256Mi (consider 512Mi for production workloads)
```

### Next Steps Customization
Tailor next steps based on configuration type:

**For Deployments:**
```
📌 Next Steps:
  1. Review deployment manifest
  2. Create secrets: kubectl create secret generic todo-secrets --from-literal=...
  3. Apply deployment: kubectl apply -f deployment.yaml
  4. Verify pods: kubectl get pods -l app.kubernetes.io/name=[service]
  5. Check health: kubectl exec -it [pod] -- curl http://localhost:8080/health
```

**For Services:**
```
📌 Next Steps:
  1. Review service configuration
  2. Apply service: kubectl apply -f service.yaml
  3. Verify service: kubectl get service [service-name]
  4. Test connectivity: kubectl port-forward service/[name] 8080:80
  5. Access service: minikube service [service-name] --url
```

**For Complete Applications:**
```
📌 Next Steps:
  1. Review all manifests
  2. Apply in order: secrets → configmaps → deployments → services
  3. Verify deployment: kubectl get all -l app.kubernetes.io/part-of=[app-name]
  4. Test endpoints: curl [service-url]/health
  5. Monitor logs: kubectl logs -l app.kubernetes.io/name=[service] --follow
```

## Dynamic Content Generation

When generating reports programmatically, use these variables:

### Configuration-Specific Values
- **Service Name**: Extract from `metadata.name` or `app.kubernetes.io/name` label
- **Version**: Extract from `app.kubernetes.io/version` label
- **Resource Values**: Extract from actual `requests` and `limits` values
- **Replica Count**: Extract from `spec.replicas`
- **Health Paths**: Extract from probe configurations
- **Image Tag**: Extract from container image specification

### Status Determination
```python
def determine_compliance_status(validation_results):
    if validation_results.errors:
        return "REJECTED", "🚫"
    elif validation_results.warnings:
        return "APPROVED with warnings", "⚠️"
    else:
        return "APPROVED", "✅"

def calculate_compliance_percentage(total_rules, passed_rules):
    return (passed_rules / total_rules) * 100
```

## Report Examples

### Example 1: Perfect Compliance
```
🛡️ CONSTITUTION COMPLIANCE REPORT

✅ Container Security: COMPLIANT
  • Rule 1.1: Running as non-root (uid 1000)
  • Rule 1.2: Immutable tag (1.0.0-sha256-def45678)
  • Rule 1.3: Using approved registry (Minikube local)
  • Rule 1.4: Security hardening applied

✅ Resource Management: COMPLIANT
  • Rule 2.1: Requests and limits defined
    - CPU: 100m request, 500m limit
    - Memory: 128Mi request, 512Mi limit
  • Rule 2.2: Request-to-limit ratio valid (50%)
  • Rule 2.3: Replica count: 2 (HA configuration)

📊 Overall Compliance: 100% ✅

📝 Deployment Status: APPROVED
🚀 Ready for: Minikube deployment
```

### Example 2: With Warnings
```
🛡️ CONSTITUTION COMPLIANCE REPORT

✅ Container Security: COMPLIANT
  • Rule 1.1: Running as non-root (uid 1000)
  • Rule 1.2: Immutable tag (1.0.0-sha256-abc12345)
  • Rule 1.3: Using approved registry (Minikube local)
  • Rule 1.4: Security hardening applied

✅ Resource Management: COMPLIANT
  • Rule 2.1: Requests and limits defined
    - CPU: 50m request, 200m limit
    - Memory: 64Mi request, 256Mi limit
  • Rule 2.2: Request-to-limit ratio valid (25%)
  • Rule 2.3: Replica count: 1 (acceptable for dev)

📊 Overall Compliance: 100% ✅

📝 Deployment Status: APPROVED
🚀 Ready for: Minikube deployment

⚠️  Warnings:
  • Replica count: 1 (single point of failure, consider 2 for HA)
  • Memory limit: 256Mi (consider increasing for production)
```

### Example 3: Non-Compliant
```
🛡️ CONSTITUTION COMPLIANCE REPORT

❌ Container Security: NON-COMPLIANT
  • Rule 1.1: FAILED - Missing runAsNonRoot: true
  • Rule 1.2: FAILED - Using mutable tag: latest
  • Rule 1.3: COMPLIANT - Using approved registry
  • Rule 1.4: FAILED - Missing security hardening

✅ Resource Management: COMPLIANT
  • Rule 2.1: Requests and limits defined
  • Rule 2.2: Request-to-limit ratio valid
  • Rule 2.3: Replica count: 1 (acceptable for dev)

📊 Overall Compliance: 60% ❌

📝 Deployment Status: REJECTED
🚫 Blocking Issues: Security violations must be fixed

❌ Critical Violations:
  1. Missing runAsNonRoot: true (security risk)
  2. Using latest tag (non-deterministic deployment)
  3. Missing security hardening (privilege escalation risk)

📌 Required Fixes:
  1. Add runAsNonRoot: true to pod securityContext
  2. Use immutable image tag with sha256
  3. Add capabilities.drop: [ALL] to containers
  4. Set allowPrivilegeEscalation: false

💡 Compliant Alternative:
  See full fixed configuration in generated manifest.
```

## Integration with Skills

When called from other skills:

### From blueprint-instantiator
```
Generated from: blueprint-instantiator
Blueprint: microservice-deployment.blueprint.md
Instance: frontend.instance.md
```

### From helm-chart-generator
```
Generated from: helm-chart-generator
Chart: todo-evolution-chart
Values: values.yaml
```

### For Manual Reviews
```
Review Type: Manual validation
Reviewer: constitution-enforcer skill
Timestamp: 2025-12-21T10:30:00Z
```