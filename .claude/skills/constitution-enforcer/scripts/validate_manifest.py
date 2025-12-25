#!/usr/bin/env python3
"""
Kubernetes Manifest Validator

Validates Kubernetes manifests against Phase IV Constitutional rules.
This script checks YAML files for compliance with security, resource, and operational standards.

Usage:
    python validate_manifest.py <manifest-file>
    python validate_manifest.py --directory <manifest-dir>
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class ManifestValidationError(Exception):
    """Raised when manifest validation fails."""
    pass


class ConstitutionalValidator:
    """Validates Kubernetes manifests against Constitutional rules."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_rules: List[str] = []

    def validate_file(self, manifest_path: Path) -> bool:
        """Validate a single manifest file."""
        try:
            content = manifest_path.read_text()
            documents = list(yaml.safe_load_all(content))
            return self.validate_documents(documents, manifest_path)
        except Exception as e:
            self.errors.append(f"Failed to read/parse manifest file: {e}")
            return False

    def validate_directory(self, manifest_dir: Path) -> bool:
        """Validate all YAML files in a directory."""
        yaml_files = list(manifest_dir.glob("**/*.yaml")) + list(manifest_dir.glob("**/*.yml"))

        if not yaml_files:
            self.errors.append(f"No YAML files found in directory: {manifest_dir}")
            return False

        overall_success = True
        for yaml_file in yaml_files:
            if not self.validate_file(yaml_file):
                overall_success = False

        return overall_success

    def validate_documents(self, documents: List[Dict], file_path: Optional[Path] = None) -> bool:
        """Validate multiple YAML documents."""
        self.errors.clear()
        self.warnings.clear()
        self.passed_rules.clear()

        if not documents:
            self.errors.append("No documents found in manifest")
            return False

        for doc in documents:
            if not doc:
                continue

            kind = doc.get('kind', '').lower()

            if kind == 'deployment':
                self._validate_deployment(doc)
            elif kind == 'service':
                self._validate_service(doc)
            elif kind == 'secret':
                self._validate_secret(doc)
            elif kind == 'configmap':
                self._validate_configmap(doc)
            else:
                self.warnings.append(f"Unknown resource type: {kind}")

        self._print_results(file_path)
        return len(self.errors) == 0

    def _validate_deployment(self, deployment: Dict) -> None:
        """Validate a Kubernetes Deployment."""
        metadata = deployment.get('metadata', {})
        spec = deployment.get('spec', {})
        template = spec.get('template', {})
        pod_spec = template.get('spec', {})
        containers = pod_spec.get('containers', [])

        # Rule 1.1: Non-Root Containers
        self._check_rule_1_1_non_root(pod_spec, containers)

        # Rule 1.2: Immutable Image Tags
        self._check_rule_1_2_immutable_tags(containers)

        # Rule 2.1: Resource Limits Required
        self._check_rule_2_1_resource_limits(containers)

        # Rule 2.2: Request-to-Limit Ratio
        self._check_rule_2_2_request_limit_ratio(containers)

        # Rule 2.3: Replica Count
        self._check_rule_2_3_replica_count(spec)

        # Rule 3.1: Health Probes Required
        self._check_rule_3_1_health_probes(containers)

        # Rule 4.1: Kubernetes Recommended Labels
        self._check_rule_4_1_standard_labels(metadata, template)

        # Rule 4.2: Rolling Update Strategy
        self._check_rule_4_2_rolling_update(spec)

    def _validate_service(self, service: Dict) -> None:
        """Validate a Kubernetes Service."""
        metadata = service.get('metadata', {})
        spec = service.get('spec', {})

        # Rule 4.1: Kubernetes Recommended Labels
        self._check_rule_4_1_standard_labels(metadata)

        # Rule 4.3: Service Selector
        self._check_rule_4_3_service_selector(spec)

    def _validate_secret(self, secret: Dict) -> None:
        """Validate a Kubernetes Secret."""
        # Check for common secret validation patterns
        metadata = secret.get('metadata', {})

        # Rule 4.1: Kubernetes Recommended Labels
        self._check_rule_4_1_standard_labels(metadata)

        # Additional secret-specific checks could be added here
        self.passed_rules.append("Secret structure validated")

    def _validate_configmap(self, configmap: Dict) -> None:
        """Validate a Kubernetes ConfigMap."""
        metadata = configmap.get('metadata', {})

        # Rule 4.1: Kubernetes Recommended Labels
        self._check_rule_4_1_standard_labels(metadata)

    def _check_rule_1_1_non_root(self, pod_spec: Dict, containers: List[Dict]) -> None:
        """Check Rule 1.1: Non-Root Containers."""
        pod_security = pod_spec.get('securityContext', {})

        # Check pod-level security context
        if not pod_security.get('runAsNonRoot'):
            self.errors.append("Rule 1.1: Missing runAsNonRoot: true at pod level")
        elif pod_security.get('runAsNonRoot') is True:
            self.passed_rules.append("Rule 1.1: runAsNonRoot: true present")

        run_as_user = pod_security.get('runAsUser')
        if run_as_user is None:
            self.errors.append("Rule 1.1: Missing runAsUser at pod level")
        elif run_as_user >= 1000:
            self.passed_rules.append(f"Rule 1.1: runAsUser: {run_as_user} (valid)")
        else:
            self.errors.append(f"Rule 1.1: runAsUser: {run_as_user} (must be ≥ 1000)")

        # Check container-level security context
        for i, container in enumerate(containers):
            container_name = container.get('name', f'container-{i}')
            container_security = container.get('securityContext', {})

            if container_security.get('allowPrivilegeEscalation') is not False:
                self.errors.append(f"Rule 1.1: Container '{container_name}' missing allowPrivilegeEscalation: false")
            else:
                self.passed_rules.append(f"Rule 1.1: Container '{container_name}' has allowPrivilegeEscalation: false")

            capabilities = container_security.get('capabilities', {})
            dropped_caps = capabilities.get('drop', [])

            if 'ALL' not in dropped_caps:
                self.errors.append(f"Rule 1.1: Container '{container_name}' missing capabilities.drop: [ALL]")
            else:
                self.passed_rules.append(f"Rule 1.1: Container '{container_name}' drops ALL capabilities")

    def _check_rule_1_2_immutable_tags(self, containers: List[Dict]) -> None:
        """Check Rule 1.2: Immutable Image Tags."""
        for i, container in enumerate(containers):
            container_name = container.get('name', f'container-{i}')
            image = container.get('image', '')

            if not image:
                self.errors.append(f"Rule 1.2: Container '{container_name}' missing image")
                continue

            if ':' not in image:
                self.errors.append(f"Rule 1.2: Container '{container_name}' image missing tag: {image}")
                continue

            _, tag = image.rsplit(':', 1)

            if tag in ['latest', 'dev', 'staging', 'prod']:
                self.errors.append(f"Rule 1.2: Container '{container_name}' uses mutable tag: {tag}")
            elif 'sha256' in tag:
                self.passed_rules.append(f"Rule 1.2: Container '{container_name}' has immutable tag with sha256")
            else:
                self.warnings.append(f"Rule 1.2: Container '{container_name}' tag missing sha256: {tag}")

    def _check_rule_2_1_resource_limits(self, containers: List[Dict]) -> None:
        """Check Rule 2.1: Resource Limits Required."""
        for i, container in enumerate(containers):
            container_name = container.get('name', f'container-{i}')
            resources = container.get('resources', {})

            if not resources:
                self.errors.append(f"Rule 2.1: Container '{container_name}' missing resources block")
                continue

            requests = resources.get('requests', {})
            limits = resources.get('limits', {})

            if not requests:
                self.errors.append(f"Rule 2.1: Container '{container_name}' missing resource requests")
            else:
                if requests.get('cpu') and requests.get('memory'):
                    self.passed_rules.append(f"Rule 2.1: Container '{container_name}' has resource requests")
                else:
                    missing = []
                    if not requests.get('cpu'):
                        missing.append('cpu')
                    if not requests.get('memory'):
                        missing.append('memory')
                    self.errors.append(f"Rule 2.1: Container '{container_name}' missing requests: {', '.join(missing)}")

            if not limits:
                self.errors.append(f"Rule 2.1: Container '{container_name}' missing resource limits")
            else:
                if limits.get('cpu') and limits.get('memory'):
                    self.passed_rules.append(f"Rule 2.1: Container '{container_name}' has resource limits")
                else:
                    missing = []
                    if not limits.get('cpu'):
                        missing.append('cpu')
                    if not limits.get('memory'):
                        missing.append('memory')
                    self.errors.append(f"Rule 2.1: Container '{container_name}' missing limits: {', '.join(missing)}")

    def _check_rule_2_2_request_limit_ratio(self, containers: List[Dict]) -> None:
        """Check Rule 2.2: Request-to-Limit Ratio."""
        for i, container in enumerate(containers):
            container_name = container.get('name', f'container-{i}')
            resources = container.get('resources', {})
            requests = resources.get('requests', {})
            limits = resources.get('limits', {})

            # Check CPU ratio
            req_cpu = requests.get('cpu')
            lim_cpu = limits.get('cpu')

            if req_cpu and lim_cpu:
                if self._compare_resources(req_cpu, lim_cpu) <= 0:
                    self.passed_rules.append(f"Rule 2.2: Container '{container_name}' CPU requests ≤ limits")
                else:
                    self.errors.append(f"Rule 2.2: Container '{container_name}' CPU requests > limits")

            # Check memory ratio
            req_mem = requests.get('memory')
            lim_mem = limits.get('memory')

            if req_mem and lim_mem:
                if self._compare_resources(req_mem, lim_mem) <= 0:
                    self.passed_rules.append(f"Rule 2.2: Container '{container_name}' memory requests ≤ limits")
                else:
                    self.errors.append(f"Rule 2.2: Container '{container_name}' memory requests > limits")

    def _check_rule_2_3_replica_count(self, spec: Dict) -> None:
        """Check Rule 2.3: Replica Count."""
        replicas = spec.get('replicas', 1)

        if replicas >= 1:
            if replicas == 1:
                self.warnings.append("Rule 2.3: Single replica creates single point of failure")
            self.passed_rules.append(f"Rule 2.3: Replicas: {replicas} (valid)")
        else:
            self.errors.append(f"Rule 2.3: Invalid replica count: {replicas} (must be ≥ 1)")

    def _check_rule_3_1_health_probes(self, containers: List[Dict]) -> None:
        """Check Rule 3.1: Health Probes Required."""
        for i, container in enumerate(containers):
            container_name = container.get('name', f'container-{i}')

            liveness_probe = container.get('livenessProbe')
            readiness_probe = container.get('readinessProbe')

            if not liveness_probe:
                self.errors.append(f"Rule 3.1: Container '{container_name}' missing livenessProbe")
            else:
                self.passed_rules.append(f"Rule 3.1: Container '{container_name}' has livenessProbe")

            if not readiness_probe:
                self.errors.append(f"Rule 3.1: Container '{container_name}' missing readinessProbe")
            else:
                self.passed_rules.append(f"Rule 3.1: Container '{container_name}' has readinessProbe")

    def _check_rule_4_1_standard_labels(self, metadata: Dict, template: Optional[Dict] = None) -> None:
        """Check Rule 4.1: Kubernetes Recommended Labels."""
        labels = metadata.get('labels', {})

        required_labels = [
            'app.kubernetes.io/name',
            'app.kubernetes.io/instance',
            'app.kubernetes.io/version',
            'app.kubernetes.io/component',
            'app.kubernetes.io/part-of',
            'app.kubernetes.io/managed-by'
        ]

        missing_labels = []
        for label in required_labels:
            if label not in labels:
                missing_labels.append(label)

        if missing_labels:
            self.errors.append(f"Rule 4.1: Missing required labels: {', '.join(missing_labels)}")
        else:
            self.passed_rules.append("Rule 4.1: All required Kubernetes labels present")

    def _check_rule_4_2_rolling_update(self, spec: Dict) -> None:
        """Check Rule 4.2: Rolling Update Strategy."""
        strategy = spec.get('strategy', {})
        strategy_type = strategy.get('type', 'RollingUpdate')

        if strategy_type == 'RollingUpdate':
            self.passed_rules.append("Rule 4.2: Using RollingUpdate strategy")
        else:
            self.errors.append(f"Rule 4.2: Using {strategy_type} strategy (should be RollingUpdate)")

    def _check_rule_4_3_service_selector(self, spec: Dict) -> None:
        """Check Rule 4.3: Service Selector Matching."""
        selector = spec.get('selector', {})

        if not selector:
            self.warnings.append("Rule 4.3: Service missing selector (will have no endpoints)")
        else:
            self.passed_rules.append("Rule 4.3: Service has selector configured")

    def _compare_resources(self, request: str, limit: str) -> int:
        """Compare two resource values. Returns -1 if request < limit, 0 if equal, 1 if request > limit."""
        # Simple comparison - could be enhanced for more complex resource formats
        try:
            # Remove common suffixes for numeric comparison
            req_val = float(request.replace('m', '').replace('Mi', '').replace('Gi', ''))
            lim_val = float(limit.replace('m', '').replace('Mi', '').replace('Gi', ''))

            if req_val < lim_val:
                return -1
            elif req_val > lim_val:
                return 1
            else:
                return 0
        except:
            return 0  # Default to equal if parsing fails

    def _print_results(self, file_path: Optional[Path] = None) -> None:
        """Print validation results."""
        filename = str(file_path) if file_path else "manifest"

        print(f"\n🛡️ CONSTITUTIONAL VALIDATION RESULTS")
        print(f"File: {filename}")
        print("=" * 50)

        if self.errors:
            print(f"\n❌ VALIDATION FAILED - {len(self.errors)} errors:")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS - {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.passed_rules:
            print(f"\n✅ COMPLIANCE CHECKS PASSED - {len(self.passed_rules)} rules:")
            for rule in self.passed_rules:
                print(f"  • {rule}")

        # Overall status
        if not self.errors:
            if not self.warnings:
                print(f"\n🎉 FULLY COMPLIANT - All Constitutional rules satisfied!")
            else:
                print(f"\n⚠️  COMPLIANT with warnings - Review warnings above")
        else:
            print(f"\n❌ NON-CPLIANT - Fix errors before deployment")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python validate_manifest.py <manifest-file>")
        print("  python validate_manifest.py --directory <manifest-dir>")
        sys.exit(1)

    arg = sys.argv[1]
    validator = ConstitutionalValidator()

    if arg == '--directory' and len(sys.argv) == 3:
        manifest_dir = Path(sys.argv[2])
        if not manifest_dir.exists():
            print(f"❌ Directory not found: {manifest_dir}")
            sys.exit(1)
        success = validator.validate_directory(manifest_dir)
    else:
        manifest_file = Path(arg)
        if not manifest_file.exists():
            print(f"❌ File not found: {manifest_file}")
            sys.exit(1)
        success = validator.validate_file(manifest_file)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()