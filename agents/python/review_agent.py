"""
Review Agent - Pure Python Implementation
Execution: Python (No LLM Required)

Purpose: Validate migration completeness and generate reports.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from datetime import datetime
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.types import ParsedModule, ValidationResult, BuildResult, TestResult


class ReviewAgent:
    """
    Pure Python agent - No LLM required.
    Validates migration and generates reports.
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
    
    def validate(
        self,
        source_modules: Dict[str, ParsedModule],
        generated_dir: str
    ) -> ValidationResult:
        """Validate migration completeness."""
        entities = self._validate_entities(source_modules, generated_dir)
        services = self._validate_services(source_modules, generated_dir)
        screens = self._validate_screens(source_modules, generated_dir)
        integrations = self._validate_integrations(source_modules, generated_dir)
        
        missing = []
        if entities.get("missing"):
            missing.extend([f"Entity: {e}" for e in entities["missing"]])
        if services.get("missing"):
            missing.extend([f"Service: {s}" for s in services["missing"]])
        if screens.get("missing"):
            missing.extend([f"Screen: {s}" for s in screens["missing"]])
        if integrations.get("missing"):
            missing.extend([f"Integration: {i}" for i in integrations["missing"]])
        
        is_complete = len(missing) == 0
        
        return ValidationResult(
            is_complete=is_complete,
            entities=entities,
            services=services,
            screens=screens,
            integrations=integrations,
            missing_components=missing
        )
    
    def _validate_entities(
        self,
        modules: Dict[str, ParsedModule],
        generated_dir: str
    ) -> Dict[str, Any]:
        """Validate entity generation."""
        expected = []
        for module in modules.values():
            for entity in module.entities:
                expected.append(entity.get("name"))
            for se in module.static_entities:
                expected.append(se.get("name"))
        
        generated = self._find_generated_entities(generated_dir)
        
        found = [e for e in expected if e in generated]
        missing = [e for e in expected if e not in generated]
        
        return {
            "expected": len(expected),
            "found": len(found),
            "missing": missing,
            "coverage": round(len(found) / max(len(expected), 1) * 100, 1)
        }
    
    def _validate_services(
        self,
        modules: Dict[str, ParsedModule],
        generated_dir: str
    ) -> Dict[str, Any]:
        """Validate service generation."""
        expected = []
        for module in modules.values():
            for action in module.server_actions:
                expected.append(action.get("name"))
        
        generated = self._find_generated_services(generated_dir)
        
        found = [s for s in expected if any(s.lower() in g.lower() for g in generated)]
        missing = [s for s in expected if not any(s.lower() in g.lower() for g in generated)]
        
        return {
            "expected": len(expected),
            "found": len(found),
            "missing": missing[:10],
            "coverage": round(len(found) / max(len(expected), 1) * 100, 1)
        }
    
    def _validate_screens(
        self,
        modules: Dict[str, ParsedModule],
        generated_dir: str
    ) -> Dict[str, Any]:
        """Validate screen/component generation."""
        expected = []
        for module in modules.values():
            for screen in module.screens:
                expected.append(screen.get("name"))
            for block in module.web_blocks:
                expected.append(block.get("name"))
        
        generated = self._find_generated_components(generated_dir)
        
        found = [s for s in expected if any(s.lower() in g.lower() for g in generated)]
        missing = [s for s in expected if not any(s.lower() in g.lower() for g in generated)]
        
        return {
            "expected": len(expected),
            "found": len(found),
            "missing": missing[:10],
            "coverage": round(len(found) / max(len(expected), 1) * 100, 1)
        }
    
    def _validate_integrations(
        self,
        modules: Dict[str, ParsedModule],
        generated_dir: str
    ) -> Dict[str, Any]:
        """Validate integration generation."""
        expected = []
        for module in modules.values():
            for rest in module.rest_consumes:
                expected.append(rest.get("name"))
            for rest in module.rest_exposes:
                expected.append(rest.get("name"))
        
        generated = self._find_generated_integrations(generated_dir)
        
        found = [i for i in expected if any(i.lower() in g.lower() for g in generated)]
        missing = [i for i in expected if not any(i.lower() in g.lower() for g in generated)]
        
        return {
            "expected": len(expected),
            "found": len(found),
            "missing": missing[:10],
            "coverage": round(len(found) / max(len(expected), 1) * 100, 1)
        }
    
    def _find_generated_entities(self, generated_dir: str) -> List[str]:
        """Find generated entity files."""
        entities = []
        models_dir = os.path.join(generated_dir, "Models")
        if os.path.exists(models_dir):
            for f in os.listdir(models_dir):
                if f.endswith(".cs"):
                    entities.append(f.replace(".cs", ""))
        return entities
    
    def _find_generated_services(self, generated_dir: str) -> List[str]:
        """Find generated service files."""
        services = []
        services_dir = os.path.join(generated_dir, "Services")
        if os.path.exists(services_dir):
            for f in os.listdir(services_dir):
                if f.endswith("Service.cs"):
                    services.append(f.replace("Service.cs", ""))
        return services
    
    def _find_generated_components(self, generated_dir: str) -> List[str]:
        """Find generated UI components."""
        components = []
        for dirname in ["Pages", "Components", "Shared"]:
            comp_dir = os.path.join(generated_dir, dirname)
            if os.path.exists(comp_dir):
                for f in os.listdir(comp_dir):
                    if f.endswith(".razor") or f.endswith(".cshtml"):
                        components.append(f.split(".")[0])
        return components
    
    def _find_generated_integrations(self, generated_dir: str) -> List[str]:
        """Find generated integration files."""
        integrations = []
        for dirname in ["Clients", "Api", "Controllers"]:
            int_dir = os.path.join(generated_dir, dirname)
            if os.path.exists(int_dir):
                for f in os.listdir(int_dir):
                    if f.endswith(".cs"):
                        integrations.append(f.replace(".cs", ""))
        return integrations
    
    def generate_report(
        self,
        validation: ValidationResult,
        build_result: Optional[BuildResult],
        test_result: Optional[TestResult],
        analysis: Optional[Dict] = None
    ) -> str:
        """Generate comprehensive migration report."""
        report = f"""# Migration Validation Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Status**: {'COMPLETE' if validation.is_complete else 'INCOMPLETE'}
- **Entity Coverage**: {validation.entities.get('coverage', 0)}%
- **Service Coverage**: {validation.services.get('coverage', 0)}%
- **UI Coverage**: {validation.screens.get('coverage', 0)}%
- **Integration Coverage**: {validation.integrations.get('coverage', 0)}%

## Entity Migration
- Expected: {validation.entities.get('expected', 0)}
- Generated: {validation.entities.get('found', 0)}
"""
        
        if validation.entities.get('missing'):
            report += "\n### Missing Entities\n"
            for entity in validation.entities['missing'][:20]:
                report += f"- {entity}\n"
        
        report += f"""
## Service Migration
- Expected: {validation.services.get('expected', 0)}
- Generated: {validation.services.get('found', 0)}
"""
        
        if validation.services.get('missing'):
            report += "\n### Missing Services\n"
            for svc in validation.services['missing'][:20]:
                report += f"- {svc}\n"
        
        report += f"""
## UI Migration
- Expected: {validation.screens.get('expected', 0)}
- Generated: {validation.screens.get('found', 0)}
"""
        
        if validation.screens.get('missing'):
            report += "\n### Missing Screens/Components\n"
            for screen in validation.screens['missing'][:20]:
                report += f"- {screen}\n"
        
        report += f"""
## Integration Migration
- Expected: {validation.integrations.get('expected', 0)}
- Generated: {validation.integrations.get('found', 0)}
"""
        
        if build_result:
            report += f"""
## Build Results
- **Status**: {'SUCCESS' if build_result.success else 'FAILED'}
- **Errors**: {len(build_result.errors)}
- **Warnings**: {len(build_result.warnings)}
"""
            if build_result.errors:
                report += "\n### Build Errors\n"
                for err in build_result.errors[:10]:
                    report += f"- `{err.get('code')}`: {err.get('message')}\n"
        
        if test_result:
            report += f"""
## Test Results
- **Status**: {'PASSED' if test_result.success else 'FAILED'}
- **Total**: {test_result.total}
- **Passed**: {test_result.passed}
- **Failed**: {test_result.failed}
- **Skipped**: {test_result.skipped}
"""
        
        if validation.missing_components:
            report += "\n## Missing Components Summary\n"
            for comp in validation.missing_components[:30]:
                report += f"- {comp}\n"
        
        report += """
## Next Steps
"""
        if not validation.is_complete:
            report += "1. Review missing components and generate manually or with LLM agents\n"
            report += "2. Fix any build errors before proceeding\n"
        if build_result and not build_result.success:
            report += "3. Address compilation errors\n"
        if test_result and not test_result.success:
            report += "4. Fix failing tests\n"
        if validation.is_complete and (not build_result or build_result.success):
            report += "Migration appears complete. Proceed with integration testing.\n"
        
        output_path = os.path.join(self.output_dir, "migration-report.md")
        os.makedirs(self.output_dir, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        
        return output_path
    
    def save_validation(self, validation: ValidationResult, output_path: str):
        """Save validation results to JSON."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(asdict(validation), f, indent=2)
        return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate migration and generate report")
    parser.add_argument("parsed_dir", help="Directory with parsed JSON files")
    parser.add_argument("generated_dir", help="Directory with generated code")
    parser.add_argument("-o", "--output", default="./reports", help="Output directory")
    args = parser.parse_args()
    
    modules = {}
    for filename in os.listdir(args.parsed_dir):
        if filename.endswith(".json") and not filename.startswith("_"):
            filepath = os.path.join(args.parsed_dir, filename)
            with open(filepath) as f:
                data = json.load(f)
                module = ParsedModule(**data)
                modules[module.module_name] = module
    
    agent = ReviewAgent(args.output)
    validation = agent.validate(modules, args.generated_dir)
    
    report_path = agent.generate_report(validation, None, None)
    agent.save_validation(validation, os.path.join(args.output, "validation.json"))
    
    print(f"Validation complete:")
    print(f"  Complete: {validation.is_complete}")
    print(f"  Entity Coverage: {validation.entities.get('coverage', 0)}%")
    print(f"  Service Coverage: {validation.services.get('coverage', 0)}%")
    print(f"  Report: {report_path}")
