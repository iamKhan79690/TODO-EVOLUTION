#!/usr/bin/env python3
"""
Blueprint Validation Helper

Validates blueprint templates against specification requirements.
This script checks blueprint structure, parameters, and validation rules.

Usage:
    python validate_blueprint.py <blueprint-file>
"""

import sys
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class BlueprintValidationError(Exception):
    """Raised when blueprint validation fails."""
    pass


class BlueprintValidator:
    """Validates blueprint templates."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_file(self, blueprint_path: Path) -> bool:
        """Validate a blueprint file."""
        try:
            content = blueprint_path.read_text()
            return self.validate_content(content, blueprint_path)
        except Exception as e:
            self.errors.append(f"Failed to read blueprint file: {e}")
            return False

    def validate_content(self, content: str, file_path: Optional[Path] = None) -> bool:
        """Validate blueprint content."""
        self.errors.clear()
        self.warnings.clear()

        # Parse markdown sections
        sections = self._parse_markdown_sections(content)

        # Validate required sections
        self._validate_required_sections(sections)

        # Validate version
        if 'Version' in sections:
            self._validate_version(sections['Version'])

        # Validate parameters table
        if 'Parameters' in sections:
            self._validate_parameters(sections['Parameters'])

        # Validate template structure
        if 'Template Structure' in sections:
            self._validate_template_structure(sections['Template Structure'])

        # Validate validation rules
        if 'Validation Rules' in sections:
            self._validate_validation_rules(sections['Validation Rules'])

        # Print results
        self._print_results(file_path)

        return len(self.errors) == 0

    def _parse_markdown_sections(self, content: str) -> Dict[str, str]:
        """Parse markdown content into sections."""
        sections = {}
        current_section = None
        current_content = []

        for line in content.split('\n'):
            # Check for section headers
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = line[3:].strip()
                current_content = []
            elif line.startswith('# '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section (title)
                current_section = line[2:].strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def _validate_required_sections(self, sections: Dict[str, str]) -> None:
        """Validate that required sections exist."""
        required_sections = [
            'Parameters',
            'Template Structure',
            'Validation Rules'
        ]

        for section in required_sections:
            if section not in sections:
                self.errors.append(f"Missing required section: {section}")

    def _validate_version(self, version_content: str) -> None:
        """Validate version format."""
        version_match = re.search(r'(\d+\.\d+\.\d+)', version_content)
        if not version_match:
            self.errors.append("Version must follow semantic versioning (e.g., 1.0.0)")

    def _validate_parameters(self, parameters_content: str) -> None:
        """Validate parameters table."""
        # Check for required parameters
        required_params = [
            'service_name',
            'image',
            'tag',
            'port'
        ]

        for param in required_params:
            if param not in parameters_content:
                self.errors.append(f"Missing required parameter: {param}")

        # Check for parameter types
        if 'Type' not in parameters_content:
            self.errors.append("Parameters table must include Type column")

        if 'Required' not in parameters_content:
            self.errors.append("Parameters table must include Required column")

    def _validate_template_structure(self, template_content: str) -> None:
        """Validate template YAML structure."""
        # Extract YAML block
        yaml_match = re.search(r'```yaml\n(.*?)\n```', template_content, re.DOTALL)
        if not yaml_match:
            self.errors.append("Template Structure must contain YAML code block")
            return

        yaml_content = yaml_match.group(1)

        try:
            # Parse YAML to check syntax
            yaml_data = yaml.safe_load(yaml_content)

            # Check for required placeholders
            required_placeholders = [
                '{{service_name}}',
                '{{image}}',
                '{{tag}}',
                '{{port}}'
            ]

            yaml_str = str(yaml_data)
            for placeholder in required_placeholders:
                if placeholder not in yaml_str:
                    self.errors.append(f"Template missing required placeholder: {placeholder}")

            # Check for security best practices
            if 'securityContext' not in yaml_str:
                self.warnings.append("Template should include securityContext for security hardening")

            if 'resources:' not in yaml_str:
                self.warnings.append("Template should include resource limits and requests")

            if 'livenessProbe:' not in yaml_str:
                self.warnings.append("Template should include livenessProbe")

            if 'readinessProbe:' not in yaml_str:
                self.warnings.append("Template should include readinessProbe")

        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML in template: {e}")

    def _validate_validation_rules(self, rules_content: str) -> None:
        """Validate validation rules section."""
        # Check for common validation rules
        common_rules = [
            'service_name',
            'tag',
            'replicas'
        ]

        for rule in common_rules:
            if rule not in rules_content:
                self.warnings.append(f"Consider adding validation rules for: {rule}")

    def _print_results(self, file_path: Optional[Path] = None) -> None:
        """Print validation results."""
        filename = str(file_path) if file_path else "content"

        if self.errors:
            print(f"❌ Blueprint validation FAILED for {filename}:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"⚠️  Blueprint warnings for {filename}:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print(f"✅ Blueprint validation PASSED for {filename}")
        elif not self.errors:
            print(f"✅ Blueprint validation PASSED with warnings for {filename}")


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python validate_blueprint.py <blueprint-file>")
        sys.exit(1)

    blueprint_path = Path(sys.argv[1])

    if not blueprint_path.exists():
        print(f"❌ Blueprint file not found: {blueprint_path}")
        sys.exit(1)

    validator = BlueprintValidator()
    success = validator.validate_file(blueprint_path)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()