"""
Compilation Agent - Pure Python Implementation
Execution: Python (No LLM Required)

Purpose: Execute dotnet build/test commands and parse results.
"""

import subprocess
import json
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.types import BuildResult, TestResult


class CompilationAgent:
    """
    Pure Python agent - No LLM required.
    Executes compilation and test commands.
    """
    
    def __init__(self, project_dir: str):
        self.project_dir = os.path.abspath(project_dir)
    
    def build(self, configuration: str = "Debug") -> BuildResult:
        """Execute dotnet build and return results."""
        cmd = ["dotnet", "build", "--configuration", configuration, "--no-incremental"]
        
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        
        errors = self._parse_build_errors(result.stdout + result.stderr)
        warnings = self._parse_build_warnings(result.stdout + result.stderr)
        
        return BuildResult(
            success=result.returncode == 0,
            output=result.stdout + result.stderr,
            errors=errors,
            warnings=warnings
        )
    
    def restore(self) -> BuildResult:
        """Execute dotnet restore."""
        cmd = ["dotnet", "restore"]
        
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        
        return BuildResult(
            success=result.returncode == 0,
            output=result.stdout + result.stderr,
            errors=self._parse_build_errors(result.stderr) if result.returncode != 0 else [],
            warnings=[]
        )
    
    def test(self, filter_pattern: Optional[str] = None) -> TestResult:
        """Execute dotnet test and return results."""
        cmd = ["dotnet", "test", "--logger", "trx", "--results-directory", "./TestResults"]
        
        if filter_pattern:
            cmd.extend(["--filter", filter_pattern])
        
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        
        total, passed, failed, skipped = self._parse_test_results(result.stdout)
        
        return TestResult(
            success=result.returncode == 0,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            output=result.stdout + result.stderr
        )
    
    def publish(self, configuration: str = "Release", output_dir: str = "./publish") -> BuildResult:
        """Execute dotnet publish."""
        cmd = [
            "dotnet", "publish",
            "--configuration", configuration,
            "--output", output_dir,
            "--no-self-contained"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        
        return BuildResult(
            success=result.returncode == 0,
            output=result.stdout + result.stderr,
            errors=self._parse_build_errors(result.stderr) if result.returncode != 0 else [],
            warnings=self._parse_build_warnings(result.stdout)
        )
    
    def format_check(self) -> Tuple[bool, List[str]]:
        """Check code formatting with dotnet format."""
        cmd = ["dotnet", "format", "--verify-no-changes", "--verbosity", "diagnostic"]
        
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        
        issues = []
        for line in result.stdout.split('\n'):
            if 'would be formatted' in line.lower():
                issues.append(line.strip())
        
        return result.returncode == 0, issues
    
    def _parse_build_errors(self, output: str) -> List[Dict]:
        """Parse build errors from output."""
        errors = []
        error_pattern = r'(.+)\((\d+),(\d+)\): error (\w+): (.+)'
        
        for line in output.split('\n'):
            match = re.search(error_pattern, line)
            if match:
                errors.append({
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "column": int(match.group(3)),
                    "code": match.group(4),
                    "message": match.group(5)
                })
            elif 'error' in line.lower() and ':' in line:
                errors.append({
                    "file": "",
                    "line": 0,
                    "column": 0,
                    "code": "BUILD",
                    "message": line.strip()
                })
        
        return errors
    
    def _parse_build_warnings(self, output: str) -> List[Dict]:
        """Parse build warnings from output."""
        warnings = []
        warning_pattern = r'(.+)\((\d+),(\d+)\): warning (\w+): (.+)'
        
        for line in output.split('\n'):
            match = re.search(warning_pattern, line)
            if match:
                warnings.append({
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "column": int(match.group(3)),
                    "code": match.group(4),
                    "message": match.group(5)
                })
        
        return warnings
    
    def _parse_test_results(self, output: str) -> Tuple[int, int, int, int]:
        """Parse test results from output."""
        total = passed = failed = skipped = 0
        
        patterns = {
            'total': r'Total tests:\s*(\d+)',
            'passed': r'Passed:\s*(\d+)',
            'failed': r'Failed:\s*(\d+)',
            'skipped': r'Skipped:\s*(\d+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                value = int(match.group(1))
                if key == 'total':
                    total = value
                elif key == 'passed':
                    passed = value
                elif key == 'failed':
                    failed = value
                elif key == 'skipped':
                    skipped = value
        
        if total == 0:
            total = passed + failed + skipped
        
        return total, passed, failed, skipped
    
    def save_results(
        self,
        build_result: BuildResult,
        test_result: Optional[TestResult],
        output_path: str
    ):
        """Save compilation results to JSON."""
        results = {
            "build": asdict(build_result),
            "test": asdict(test_result) if test_result else None
        }
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build and test .NET project")
    parser.add_argument("project_dir", help="Project directory")
    parser.add_argument("-c", "--configuration", default="Debug", help="Build configuration")
    parser.add_argument("--test", action="store_true", help="Run tests after build")
    parser.add_argument("-o", "--output", default="./build-results.json", help="Output file")
    args = parser.parse_args()
    
    agent = CompilationAgent(args.project_dir)
    
    print("Restoring packages...")
    restore_result = agent.restore()
    if not restore_result.success:
        print(f"Restore failed: {restore_result.output}")
        exit(1)
    
    print(f"Building ({args.configuration})...")
    build_result = agent.build(args.configuration)
    
    test_result = None
    if args.test and build_result.success:
        print("Running tests...")
        test_result = agent.test()
    
    agent.save_results(build_result, test_result, args.output)
    
    print(f"\nBuild: {'SUCCESS' if build_result.success else 'FAILED'}")
    print(f"  Errors: {len(build_result.errors)}")
    print(f"  Warnings: {len(build_result.warnings)}")
    
    if test_result:
        print(f"\nTests: {'PASSED' if test_result.success else 'FAILED'}")
        print(f"  Total: {test_result.total}")
        print(f"  Passed: {test_result.passed}")
        print(f"  Failed: {test_result.failed}")
        print(f"  Skipped: {test_result.skipped}")
