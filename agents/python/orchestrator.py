"""
Orchestrator - Pure Python Implementation
Execution: Python (No LLM Required)

Purpose: Coordinate the migration workflow, manage state,
and invoke agents in the correct order.
"""

import json
import os
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import asdict
from datetime import datetime
from enum import Enum
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.types import (
    MigrationStatus, MigrationState, ModuleState,
    ParsedModule, AnalysisResult, BuildResult, TestResult, ValidationResult
)
from python.parser_agent import ParserAgent
from python.analyzer_agent import AnalyzerAgent
from python.configuration_agent import ConfigurationAgent
from python.compilation_agent import CompilationAgent
from python.review_agent import ReviewAgent
from python.security_agent import SecurityAgent


class MigrationPhase(Enum):
    """Migration workflow phases."""
    INITIALIZATION = "initialization"
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    COMPILATION = "compilation"
    VALIDATION = "validation"
    COMPLETE = "complete"
    FAILED = "failed"


class Orchestrator:
    """
    Pure Python orchestrator - No LLM required.
    Coordinates the full migration workflow.
    """
    
    def __init__(
        self,
        source_path: str,
        output_path: str,
        target_namespace: str = "MyApp",
        config: Optional[Dict] = None
    ):
        self.source_path = os.path.abspath(source_path)
        self.output_path = os.path.abspath(output_path)
        self.namespace = target_namespace
        self.config = config or {}
        
        self.state = MigrationState(
            migration_id=str(uuid.uuid4())[:8],
            source_path=self.source_path,
            output_path=self.output_path,
            target_namespace=target_namespace,
            config=self.config
        )
        
        self.work_dir = os.path.join(output_path, ".work")
        os.makedirs(self.work_dir, exist_ok=True)
        
        self.parser = ParserAgent(work_dir=self.work_dir)
        self.analyzer = AnalyzerAgent()
        self.config_agent = ConfigurationAgent(target_namespace)
        self.security_agent = SecurityAgent(target_namespace)
        
        self.parsed_modules: Dict[str, ParsedModule] = {}
        self.analysis: Optional[AnalysisResult] = None
        self.callbacks: Dict[str, callable] = {}
    
    def on_phase_change(self, callback: callable):
        """Register callback for phase changes."""
        self.callbacks["phase_change"] = callback
    
    def on_module_complete(self, callback: callable):
        """Register callback for module completion."""
        self.callbacks["module_complete"] = callback
    
    def _emit(self, event: str, data: Any):
        """Emit event to registered callbacks."""
        if event in self.callbacks:
            self.callbacks[event](data)
    
    def _update_phase(self, phase: MigrationPhase):
        """Update current phase and emit event."""
        self.state.current_phase = phase.value
        self._emit("phase_change", {"phase": phase.value, "state": asdict(self.state)})
        self._save_state()
    
    def _save_state(self):
        """Persist migration state to disk."""
        state_path = os.path.join(self.work_dir, "migration_state.json")
        with open(state_path, 'w') as f:
            state_dict = asdict(self.state)
            state_dict["status"] = self.state.status.value if self.state.status else None
            state_dict["started_at"] = str(self.state.started_at) if self.state.started_at else None
            state_dict["completed_at"] = str(self.state.completed_at) if self.state.completed_at else None
            for module in state_dict.get("modules", []):
                for key in ["status", "extraction_status", "generation_status", "validation_status"]:
                    if key in module and hasattr(module[key], 'value'):
                        module[key] = module[key].value
                    elif key in module and isinstance(module[key], MigrationStatus):
                        module[key] = module[key].value
            json.dump(state_dict, f, indent=2, default=str)
    
    def run(self, skip_llm: bool = False) -> MigrationState:
        """Execute the full migration workflow."""
        self.state.started_at = datetime.now()
        self.state.status = MigrationStatus.IN_PROGRESS
        self._save_state()
        
        try:
            self._phase_extraction()
            self._phase_analysis()
            self._phase_generation(skip_llm=skip_llm)
            self._phase_compilation()
            self._phase_validation()
            
            self.state.status = MigrationStatus.COMPLETED
            self.state.completed_at = datetime.now()
            self._update_phase(MigrationPhase.COMPLETE)
            
        except Exception as e:
            self.state.status = MigrationStatus.FAILED
            self._update_phase(MigrationPhase.FAILED)
            raise
        
        return self.state
    
    def _phase_extraction(self):
        """Phase 1: Extract and parse OML files."""
        self._update_phase(MigrationPhase.EXTRACTION)
        
        if self.source_path.endswith(".oap"):
            self.parsed_modules = self.parser.extract_all(self.source_path)
        elif self.source_path.endswith(".oml"):
            module = self.parser.parse_oml(self.source_path)
            self.parsed_modules = {module.module_name: module}
        elif os.path.isdir(self.source_path):
            oml_files = self.parser.find_oml_files(self.source_path)
            for oml_path in oml_files:
                module = self.parser.parse_oml(oml_path)
                self.parsed_modules[module.module_name] = module
        else:
            raise ValueError(f"Unsupported source: {self.source_path}")
        
        for name in self.parsed_modules:
            self.state.modules.append(ModuleState(
                name=name,
                status=MigrationStatus.PENDING,
                extraction_status=MigrationStatus.COMPLETED
            ))
        
        parsed_dir = os.path.join(self.work_dir, "parsed")
        self.parser.save_to_json(self.parsed_modules, parsed_dir)
        
        print(f"Extracted {len(self.parsed_modules)} module(s)")
    
    def _phase_analysis(self):
        """Phase 2: Analyze modules for complexity and dependencies."""
        self._update_phase(MigrationPhase.ANALYSIS)
        
        self.analysis = self.analyzer.analyze(self.parsed_modules)
        self.state.migration_order = self.analysis.migration_order
        
        analysis_path = os.path.join(self.work_dir, "analysis.json")
        self.analyzer.save_analysis(self.analysis, analysis_path)
        
        print(f"Analysis complete: {self.analysis.complexity_level} complexity")
        print(f"Migration order: {' -> '.join(self.analysis.migration_order)}")
    
    def _phase_generation(self, skip_llm: bool = False):
        """Phase 3: Generate .NET code."""
        self._update_phase(MigrationPhase.GENERATION)
        
        self.config_agent.generate_all(
            self.parsed_modules,
            self.analysis,
            self.output_path,
            self.config
        )
        print("Generated configuration files")
        
        security_dir = os.path.join(self.output_path, "Security")
        self.security_agent.generate_all(self.parsed_modules, security_dir)
        print("Generated security files")
        
        self._create_folder_structure()
        
        if not skip_llm:
            self._generate_llm_prompts()
        
        for module_state in self.state.modules:
            module_state.generation_status = MigrationStatus.COMPLETED
            self._emit("module_complete", {"module": module_state.name, "phase": "generation"})
    
    def _create_folder_structure(self):
        """Create standard .NET folder structure."""
        folders = [
            "Models/Entities",
            "Models/Enums",
            "Models/DTOs",
            "Data/Configurations",
            "Data/Repositories",
            "Services",
            "Services/Interfaces",
            "Controllers",
            "Pages",
            "Components",
            "Shared",
            "Clients",
            "BackgroundJobs",
            "Tests/Unit",
            "Tests/Integration"
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(self.output_path, folder), exist_ok=True)
    
    def _generate_llm_prompts(self):
        """Generate prompts for LLM agents."""
        prompts_dir = os.path.join(self.work_dir, "llm_prompts")
        os.makedirs(prompts_dir, exist_ok=True)
        
        for module_name in self.state.migration_order:
            module = self.parsed_modules[module_name]
            module_dir = os.path.join(prompts_dir, module_name)
            os.makedirs(module_dir, exist_ok=True)
            
            if module.entities or module.static_entities:
                self._write_entity_prompt(module, module_dir)
            
            if module.server_actions:
                self._write_service_prompt(module, module_dir)
            
            if module.screens or module.web_blocks:
                self._write_ui_prompt(module, module_dir)
            
            if module.rest_consumes:
                self._write_integration_prompt(module, module_dir)
            
            if module.timers or module.processes:
                self._write_jobs_prompt(module, module_dir)
        
        print(f"Generated LLM prompts in {prompts_dir}")
    
    def _write_entity_prompt(self, module: ParsedModule, output_dir: str):
        """Write entity generation prompt."""
        prompt = f"""Generate C# entity classes for the following OutSystems entities.

Module: {module.module_name}
Target Namespace: {self.namespace}.Models.Entities

## Entities:
{json.dumps(module.entities, indent=2)}

## Static Entities (Enums):
{json.dumps(module.static_entities, indent=2)}

## Requirements:
1. Use Entity Framework Core conventions
2. Include data annotations for validation
3. Generate navigation properties for relationships
4. Create enums for static entities
5. Include XML documentation

Generate the C# code:
"""
        with open(os.path.join(output_dir, "entity_prompt.txt"), 'w') as f:
            f.write(prompt)
    
    def _write_service_prompt(self, module: ParsedModule, output_dir: str):
        """Write service generation prompt."""
        prompt = f"""Generate C# service classes for the following OutSystems server actions.

Module: {module.module_name}
Target Namespace: {self.namespace}.Services

## Server Actions:
{json.dumps(module.server_actions, indent=2)}

## Aggregates (for repository methods):
{json.dumps(module.aggregates, indent=2)}

## Requirements:
1. Create interface and implementation
2. Use repository pattern for data access
3. Include validation logic
4. Handle exceptions appropriately
5. Add logging

Generate the C# code:
"""
        with open(os.path.join(output_dir, "service_prompt.txt"), 'w') as f:
            f.write(prompt)
    
    def _write_ui_prompt(self, module: ParsedModule, output_dir: str):
        """Write UI generation prompt."""
        prompt = f"""Generate Blazor components for the following OutSystems screens.

Module: {module.module_name}
Target Namespace: {self.namespace}.Pages

## Screens:
{json.dumps(module.screens, indent=2)}

## Web Blocks (Components):
{json.dumps(module.web_blocks, indent=2)}

## Requirements:
1. Use Blazor Server or WASM (configurable)
2. Include form validation
3. Handle loading states
4. Implement proper error handling
5. Use dependency injection for services

Generate the Blazor code:
"""
        with open(os.path.join(output_dir, "ui_prompt.txt"), 'w') as f:
            f.write(prompt)
    
    def _write_integration_prompt(self, module: ParsedModule, output_dir: str):
        """Write integration generation prompt."""
        prompt = f"""Generate HTTP client classes for the following OutSystems REST consumes.

Module: {module.module_name}
Target Namespace: {self.namespace}.Clients

## REST APIs:
{json.dumps(module.rest_consumes, indent=2)}

## Requirements:
1. Use Refit or HttpClientFactory
2. Include retry policies with Polly
3. Handle authentication
4. Include request/response logging
5. Generate DTOs for request/response

Generate the C# code:
"""
        with open(os.path.join(output_dir, "integration_prompt.txt"), 'w') as f:
            f.write(prompt)
    
    def _write_jobs_prompt(self, module: ParsedModule, output_dir: str):
        """Write background jobs prompt."""
        prompt = f"""Generate Hangfire background job classes for the following OutSystems timers/processes.

Module: {module.module_name}
Target Namespace: {self.namespace}.BackgroundJobs

## Timers:
{json.dumps(module.timers, indent=2)}

## BPT Processes:
{json.dumps(module.processes, indent=2)}

## Requirements:
1. Use Hangfire for scheduling
2. Include proper error handling and retries
3. Add logging
4. Consider idempotency
5. Include job registration code

Generate the C# code:
"""
        with open(os.path.join(output_dir, "jobs_prompt.txt"), 'w') as f:
            f.write(prompt)
    
    def _phase_compilation(self):
        """Phase 4: Compile generated code."""
        self._update_phase(MigrationPhase.COMPILATION)
        
        csproj_files = [f for f in os.listdir(self.output_path) if f.endswith(".csproj")]
        if not csproj_files:
            print("No .csproj found, skipping compilation")
            return
        
        compiler = CompilationAgent(self.output_path)
        
        restore_result = compiler.restore()
        if not restore_result.success:
            print(f"Restore failed: {len(restore_result.errors)} errors")
            return
        
        build_result = compiler.build()
        
        results_path = os.path.join(self.work_dir, "build_results.json")
        compiler.save_results(build_result, None, results_path)
        
        if build_result.success:
            print("Build successful")
        else:
            print(f"Build failed: {len(build_result.errors)} errors")
            for err in build_result.errors[:5]:
                print(f"  - {err.get('message')}")
    
    def _phase_validation(self):
        """Phase 5: Validate migration completeness."""
        self._update_phase(MigrationPhase.VALIDATION)
        
        reviewer = ReviewAgent(os.path.join(self.work_dir, "reports"))
        
        validation = reviewer.validate(self.parsed_modules, self.output_path)
        
        build_result = None
        results_path = os.path.join(self.work_dir, "build_results.json")
        if os.path.exists(results_path):
            with open(results_path) as f:
                data = json.load(f)
                if data.get("build"):
                    build_result = BuildResult(**data["build"])
        
        report_path = reviewer.generate_report(validation, build_result, None, asdict(self.analysis) if self.analysis else None)
        
        for module_state in self.state.modules:
            module_state.validation_status = MigrationStatus.COMPLETED
        
        print(f"Validation complete: {'COMPLETE' if validation.is_complete else 'INCOMPLETE'}")
        print(f"Report: {report_path}")
    
    def resume(self, state_path: str) -> MigrationState:
        """Resume migration from saved state."""
        with open(state_path) as f:
            state_dict = json.load(f)
        
        self.state = MigrationState(**{
            k: v for k, v in state_dict.items()
            if k not in ["started_at", "completed_at"]
        })
        
        parsed_dir = os.path.join(self.work_dir, "parsed")
        if os.path.exists(parsed_dir):
            for filename in os.listdir(parsed_dir):
                if filename.endswith(".json") and not filename.startswith("_"):
                    with open(os.path.join(parsed_dir, filename)) as f:
                        data = json.load(f)
                        module = ParsedModule(**data)
                        self.parsed_modules[module.module_name] = module
        
        return self.run()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="OutSystems to .NET Migration Orchestrator")
    parser.add_argument("source", help="Source OAP/OML file or directory")
    parser.add_argument("-o", "--output", default="./output", help="Output directory")
    parser.add_argument("-n", "--namespace", default="MyApp", help="Target namespace")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM generation prompts")
    parser.add_argument("--resume", help="Resume from saved state file")
    args = parser.parse_args()
    
    if args.resume:
        orchestrator = Orchestrator(
            source_path=args.source,
            output_path=args.output,
            target_namespace=args.namespace
        )
        state = orchestrator.resume(args.resume)
    else:
        orchestrator = Orchestrator(
            source_path=args.source,
            output_path=args.output,
            target_namespace=args.namespace
        )
        state = orchestrator.run(skip_llm=args.skip_llm)
    
    print(f"\nMigration {state.status.value}")
    print(f"ID: {state.migration_id}")
    print(f"Modules: {len(state.modules)}")
    print(f"Output: {state.output_path}")


if __name__ == "__main__":
    main()
