#!/usr/bin/env python3
"""
OutSystems to .NET Migration Agent System
Main entry point for running the migration orchestrator.

Usage:
    python main.py <source> -o <output> -n <namespace>
    
Examples:
    python main.py app.oap -o ./output -n MyCompany.App
    python main.py ./oml_files/ -o ./output -n MyApp --skip-llm
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python.orchestrator import Orchestrator, MigrationPhase


def print_banner():
    """Print application banner."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║        OutSystems to .NET Migration Agent System              ║
║                                                               ║
║  Python Agents: Parser, Analyzer, Configuration, Compilation  ║
║  LLM Agents: Entity, Service, UI, Integration, Test, Jobs    ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def on_phase_change(data):
    """Callback for phase changes."""
    phase = data["phase"]
    symbols = {
        "initialization": "🔄",
        "extraction": "📦",
        "analysis": "🔍",
        "generation": "⚙️",
        "compilation": "🔨",
        "validation": "✅",
        "complete": "🎉",
        "failed": "❌"
    }
    print(f"\n{symbols.get(phase, '▶')} Phase: {phase.upper()}")


def on_module_complete(data):
    """Callback for module completion."""
    print(f"  ✓ {data['module']} - {data['phase']}")


def main():
    parser = argparse.ArgumentParser(
        description="OutSystems to .NET Migration Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate from OAP file
  python main.py myapp.oap -o ./output -n MyCompany.App
  
  # Migrate from directory of OML files
  python main.py ./exports/ -o ./output -n MyApp
  
  # Skip LLM prompts (Python agents only)
  python main.py myapp.oap -o ./output --skip-llm
  
  # Resume from saved state
  python main.py myapp.oap -o ./output --resume ./output/.work/migration_state.json
        """
    )
    
    parser.add_argument(
        "source",
        help="Source OAP file, OML file, or directory containing OML files"
    )
    parser.add_argument(
        "-o", "--output",
        default="./output",
        help="Output directory for generated code (default: ./output)"
    )
    parser.add_argument(
        "-n", "--namespace",
        default="MyApp",
        help="Target C# namespace (default: MyApp)"
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM prompt generation (Python agents only)"
    )
    parser.add_argument(
        "--resume",
        metavar="STATE_FILE",
        help="Resume from saved migration state file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration JSON file"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source):
        print(f"Error: Source not found: {args.source}")
        sys.exit(1)
    
    config = {}
    if args.config:
        import json
        with open(args.config) as f:
            config = json.load(f)
    
    print_banner()
    
    print(f"Source: {args.source}")
    print(f"Output: {args.output}")
    print(f"Namespace: {args.namespace}")
    print(f"Skip LLM: {args.skip_llm}")
    
    orchestrator = Orchestrator(
        source_path=args.source,
        output_path=args.output,
        target_namespace=args.namespace,
        config=config
    )
    
    orchestrator.on_phase_change(on_phase_change)
    orchestrator.on_module_complete(on_module_complete)
    
    try:
        if args.resume:
            print(f"\nResuming from: {args.resume}")
            state = orchestrator.resume(args.resume)
        else:
            state = orchestrator.run(skip_llm=args.skip_llm)
        
        print(f"""
════════════════════════════════════════════════════════════════
                     MIGRATION COMPLETE
════════════════════════════════════════════════════════════════
  Migration ID: {state.migration_id}
  Status: {state.status.value.upper()}
  Modules: {len(state.modules)}
  Output: {state.output_path}
  
  Next Steps:
  1. Review generated code in {state.output_path}
  2. Run LLM agents for code generation (see .work/llm_prompts/)
  3. Build: dotnet build
  4. Test: dotnet test
  5. Review migration report: .work/reports/migration-report.md
════════════════════════════════════════════════════════════════
        """)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
