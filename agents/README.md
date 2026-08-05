# OutSystems to .NET Migration Agent System

A multi-agent system for migrating OutSystems applications to .NET 8.0 using a combination of Python agents and LLM-powered Factory Droids.

   Summary

   Python Agents (7 files in `agents/python/`)

   Agent                    │ Purpose                                │ Lines
   -------------------------│----------------------------------------│------
   `orchestrator.py`        │ Workflow coordinator, state management │ ~400
   `parser_agent.py`        │ OML/OAP extraction to JSON             │ ~500
   `analyzer_agent.py`      │ Complexity scoring, dependency graph   │ ~200
   `configuration_agent.py` │ appsettings, Dockerfile, .csproj       │ ~300
   `compilation_agent.py`   │ dotnet build/test execution            │ ~150
   `review_agent.py`        │ Validation and reporting               │ ~250
   `security_agent.py`      │ Roles, policies (hybrid)               │ ~200

   LLM Droids (6 YAML files in `agents/droids/`)
   •  entity-generator.yaml - C# entities from OutSystems
   •  business-logic-generator.yaml - Services from server actions
   •  ui-generator.yaml - Blazor from screens
   •  integration-generator.yaml - HTTP clients from REST consumes
   •  test-generator.yaml - xUnit tests
   •  background-jobs-generator.yaml - Hangfire from timers/BPT

   Supporting Files
   •  agents/models/types.py - Dataclasses
   •  agents/utils/type_mapper.py - OS to C# type mapping
   •  agents/main.py - Entry point
   •  agents/README.md - Documentation

   Usage

   bash
     python agents/main.py myapp.oap -o ./output -n MyCompany.App

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                             │
│                    (Python - Workflow Control)                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Python Agents  │ │   LLM Agents    │ │  Hybrid Agents  │
│                 │ │  (Factory Droids)│ │                 │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • Parser        │ │ • Entity Gen    │ │ • Security      │
│ • Analyzer      │ │ • Service Gen   │ │                 │
│ • Configuration │ │ • UI Gen        │ │                 │
│ • Compilation   │ │ • Integration   │ │                 │
│ • Review        │ │ • Test Gen      │ │                 │
│                 │ │ • Background    │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Agent Distribution

| Type | Count | Execution |
|------|-------|-----------|
| Python Only | 6 | Local Python runtime |
| LLM Required | 6 | Factory Droids (Claude) |
| Hybrid | 1 | Python + LLM for complex cases |

## Quick Start

```bash
# Run migration from OAP file
python main.py myapp.oap -o ./output -n MyCompany.App

# Run from directory of OML files
python main.py ./exports/ -o ./output -n MyApp

# Python agents only (skip LLM prompts)
python main.py myapp.oap -o ./output --skip-llm
```

## Directory Structure

```
agents/
├── main.py                 # Main entry point
├── README.md               # This file
├── python/                 # Python-only agents
│   ├── __init__.py
│   ├── orchestrator.py     # Workflow coordinator
│   ├── parser_agent.py     # OML XML parser
│   ├── analyzer_agent.py   # Complexity analysis
│   ├── configuration_agent.py  # Config file generation
│   ├── compilation_agent.py    # Build execution
│   ├── review_agent.py     # Validation & reporting
│   └── security_agent.py   # Security code (hybrid)
├── droids/                 # Factory Droid configurations
│   ├── entity-generator.yaml
│   ├── business-logic-generator.yaml
│   ├── ui-generator.yaml
│   ├── integration-generator.yaml
│   ├── test-generator.yaml
│   └── background-jobs-generator.yaml
├── models/                 # Data models
│   ├── __init__.py
│   └── types.py            # Dataclasses
├── utils/                  # Utilities
│   ├── __init__.py
│   └── type_mapper.py      # OS to C# type mapping
└── templates/              # Code templates (future)
```

## Python Agents

### 1. Parser Agent (`parser_agent.py`)
- **Purpose**: Extract and parse OML files
- **Input**: OAP file or OML files
- **Output**: JSON with entities, actions, screens, etc.

```bash
python -m python.parser_agent myapp.oap -o ./parsed
```

### 2. Analyzer Agent (`analyzer_agent.py`)
- **Purpose**: Calculate complexity, build dependency graph
- **Input**: Parsed JSON files
- **Output**: Analysis with migration order

```bash
python -m python.analyzer_agent ./parsed -o analysis.json
```

### 3. Configuration Agent (`configuration_agent.py`)
- **Purpose**: Generate .NET configuration files
- **Output**: appsettings.json, Dockerfile, .csproj, Program.cs

```bash
python -m python.configuration_agent ./parsed -o ./output -n MyApp
```

### 4. Compilation Agent (`compilation_agent.py`)
- **Purpose**: Execute dotnet build/test
- **Output**: Build results with errors/warnings

```bash
python -m python.compilation_agent ./output -c Release --test
```

### 5. Review Agent (`review_agent.py`)
- **Purpose**: Validate migration completeness
- **Output**: Migration report (markdown)

```bash
python -m python.review_agent ./parsed ./output -o ./reports
```

### 6. Security Agent (`security_agent.py`)
- **Purpose**: Generate roles, policies, authorization
- **Output**: Security/*.cs files

```bash
python -m python.security_agent ./parsed -o ./Security -n MyApp
```

## LLM Agents (Factory Droids)

Copy droid configurations to `.factory/droids/` or run with Factory CLI:

### Entity Generator
Generates C# entity classes from OutSystems entities.

### Business Logic Generator
Generates service classes from server actions.

### UI Generator
Generates Blazor components from screens.

### Integration Generator
Generates HTTP clients from REST consumes.

### Test Generator
Generates xUnit tests for generated code.

### Background Jobs Generator
Generates Hangfire jobs from timers/BPT processes.

## Migration Workflow

```
1. EXTRACTION    → Parser Agent reads OML/OAP files
2. ANALYSIS      → Analyzer calculates complexity & order
3. GENERATION    → Configuration + LLM agents generate code
4. COMPILATION   → Compilation Agent builds project
5. VALIDATION    → Review Agent validates completeness
```

## Output Structure

```
output/
├── appsettings.json
├── appsettings.Development.json
├── Dockerfile
├── docker-compose.yml
├── MyApp.csproj
├── Program.cs
├── Directory.Build.props
├── Models/
│   ├── Entities/          # Generated entities
│   ├── Enums/             # Static entities as enums
│   └── DTOs/              # Request/response DTOs
├── Data/
│   ├── AppDbContext.cs
│   ├── Configurations/    # EF Core configurations
│   └── Repositories/      # Repository implementations
├── Services/
│   ├── Interfaces/        # Service interfaces
│   └── *.cs               # Service implementations
├── Controllers/           # API controllers
├── Pages/                 # Blazor pages
├── Components/            # Blazor components
├── Shared/                # Shared components
├── Clients/               # HTTP clients
├── Security/              # Auth code
├── BackgroundJobs/        # Hangfire jobs
├── Tests/
│   ├── Unit/
│   └── Integration/
└── .work/                 # Working directory
    ├── parsed/            # Parsed JSON files
    ├── analysis.json      # Analysis results
    ├── llm_prompts/       # Prompts for LLM agents
    ├── build_results.json
    ├── migration_state.json
    └── reports/
        └── migration-report.md
```

## Configuration Options

Create a config.json file:

```json
{
  "dotnet_version": "8.0",
  "connection_string": "Server=localhost;Database=MyApp;...",
  "jwt_issuer": "MyCompany",
  "jwt_audience": "MyApp.Users"
}
```

Use with:
```bash
python main.py myapp.oap -o ./output --config config.json
```

## Requirements

- Python 3.10+
- .NET 8.0 SDK (for compilation)
- Factory CLI (for LLM agents)

## License

Internal use only.
