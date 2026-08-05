# Agentic Migration System Design

## OutSystems to .NET Migration using AI Agents

---

## Design Considerations

Before finalizing the agent architecture, the following elements from existing documentation must be covered:

### From Reverse Engineering Guide (27 Steps, 7 Iterations)
- OML parsing and extraction for all component types
- Module dependency analysis and migration order
- Cross-module reference mapping
- Iterative extraction process

### From Component Mapping
- Data Layer: Entities, Static Entities, Relationships, Indexes, Structures
- Business Logic: Server Actions, Client Actions, Aggregates, Timers, BPT
- User Interface: Screens, Widgets, Web Blocks, Events
- Integration: REST Consume/Expose, SOAP, External DB
- Security: Roles, Permissions, Authentication
- Configuration: Site Properties, Resources, Extensions

### From Migration Process (12 Phases)
- Discovery & Assessment
- Architecture Design
- Infrastructure Setup
- Data/Logic/UI/Integration Migration
- Security, Cross-Cutting Concerns
- Testing & Validation
- Deployment & Go-Live

### From POC Steps
- Simplified 11-step workflow for quick demonstration
- Client-facing deliverables

---

## Agent Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATOR AGENT                                 │
│         (Workflow Control, State Management, Agent Coordination)            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│   EXTRACTION  │           │   GENERATION  │           │   VALIDATION  │
│    AGENTS     │           │    AGENTS     │           │    AGENTS     │
└───────────────┘           └───────────────┘           └───────────────┘
        │                             │                             │
   ┌────┴────┐                 ┌──────┴──────┐              ┌───────┴───────┐
   ▼         ▼                 ▼      ▼      ▼              ▼       ▼       ▼
Parser   Analyzer          Entity  Logic    UI          Compile  Test   Review
Agent    Agent             Agent   Agent   Agent        Agent   Agent   Agent
```

---

## Agent Definitions

### 1. Orchestrator Agent

**Role:** Central coordinator that manages the entire migration workflow

**Responsibilities:**
- Receive and validate input (OAP/OML files)
- Determine migration order based on dependencies
- Dispatch tasks to specialized agents
- Track progress and state
- Handle errors and retries
- Aggregate results and generate reports

**Inputs:**
- OAP file path or extracted OML directory
- Target configuration (stack, architecture, output path)
- Migration scope (full or selective)

**Outputs:**
- Migration status and progress
- Final .NET solution
- Migration report

**State Management:**
```json
{
  "migration_id": "uuid",
  "status": "in_progress",
  "current_phase": "extraction",
  "modules": [
    {
      "name": "CustomerModule",
      "status": "completed",
      "extraction": "completed",
      "generation": "in_progress",
      "validation": "pending"
    }
  ],
  "errors": [],
  "artifacts": {}
}
```

---

### 2. Parser Agent

**Role:** Extract and parse OML files into structured JSON

**Responsibilities:**
- Extract OAP to OML files
- Parse XML structure of each OML
- Extract all component metadata
- Generate structured JSON output

**Covers Reverse Engineering Steps:**
- Step 1: Export Application Package
- Step 2: Extract and Inventory OML Files
- Step 3: Parse Module Dependencies
- Steps 4-24: Extract all component types

**Inputs:**
- OML file path

**Outputs:**
```json
{
  "module_name": "CustomerModule",
  "type": "Reactive",
  "entities": [...],
  "static_entities": [...],
  "relationships": [...],
  "indexes": [...],
  "structures": [...],
  "server_actions": [...],
  "client_actions": [...],
  "aggregates": [...],
  "screens": [...],
  "web_blocks": [...],
  "rest_consumes": [...],
  "rest_exposes": [...],
  "timers": [...],
  "processes": [...],
  "roles": [...],
  "site_properties": [...],
  "resources": [...],
  "extensions": [...],
  "dependencies": [...]
}
```

**Tools Required:**
- File system access
- XML parser
- JSON serializer

---

### 3. Analyzer Agent

**Role:** Analyze extracted data for complexity, dependencies, and migration strategy

**Responsibilities:**
- Calculate complexity scores
- Build dependency graph
- Determine migration order (topological sort)
- Identify high-risk components
- Map cross-module references
- Document business rules

**Covers:**
- Step 25: Map Cross-Module References
- Step 26: Document Business Rules and Logic
- Step 27: Validate Completeness
- Complexity Assessment from Migration Process

**Inputs:**
- Parsed JSON from all modules

**Outputs:**
```json
{
  "complexity_score": 450,
  "complexity_level": "Medium",
  "migration_order": ["CoreModule", "CustomerModule", "OrderModule"],
  "dependency_graph": {...},
  "risk_assessment": [
    {"component": "PaymentProcess", "risk": "High", "reason": "BPT with external integration"}
  ],
  "business_rules": [...],
  "cross_references": [...]
}
```

---

### 4. Entity Generation Agent

**Role:** Generate C# entity classes from OutSystems entities

**Responsibilities:**
- Convert entities to C# classes with EF Core attributes
- Generate static entities as enums or lookup tables
- Create navigation properties for relationships
- Generate indexes via Fluent API
- Create DTOs from structures
- Generate DbContext

**Covers Component Mapping:**
- Entity → EF Core Model
- Entity Attribute → Property with [Column]
- Entity Identifier → [Key]
- Foreign Key → Navigation properties
- Index → [Index] / Fluent API
- Static Entity → Enum or lookup table
- Structure → DTO class

**Inputs:**
- Entities JSON
- Static entities JSON
- Relationships JSON
- Indexes JSON
- Structures JSON

**Outputs:**
- Entity class files (.cs)
- Enum files (.cs)
- DTO files (.cs)
- DbContext file (.cs)
- EF Core configuration files

**AI Prompt Template:**
```
Convert the following OutSystems entity to a C# EF Core entity class:

Entity: {entity_json}
Relationships: {relationships_json}
Indexes: {indexes_json}

Requirements:
- Use data annotations
- Include navigation properties
- Add XML documentation
- Follow naming conventions
```

---

### 5. Business Logic Agent

**Role:** Convert server actions, client actions, and aggregates to C# code

**Responsibilities:**
- Convert server actions to service methods
- Generate service interfaces
- Convert aggregates to LINQ queries
- Convert client actions to frontend functions
- Generate repository methods

**Covers Component Mapping:**
- Server Action → Service method
- Client Action → Frontend function
- Aggregate → LINQ query
- Input/Output Parameter → Method parameters/return types
- Exception Handler → try-catch / middleware

**Inputs:**
- Server actions JSON
- Client actions JSON
- Aggregates JSON
- Entity context (for type references)

**Outputs:**
- Service interface files (.cs)
- Service implementation files (.cs)
- Repository interface files (.cs)
- Repository implementation files (.cs)
- Frontend action files (.ts/.js)

**AI Prompt Template:**
```
Convert the following OutSystems Server Action to a C# service method:

Action: {action_json}
Available Entities: {entities_list}
Available Aggregates: {aggregates_list}

Requirements:
- Async method
- Include logging
- Include error handling
- Use repository pattern
- Return appropriate DTO
```

---

### 6. UI Generation Agent

**Role:** Convert screens and web blocks to Blazor/React components

**Responsibilities:**
- Convert screens to page components
- Convert web blocks to reusable components
- Map widgets to UI elements
- Wire up data bindings
- Generate event handlers
- Apply styling

**Covers Component Mapping:**
- Screen → Blazor/React component
- Web Block → Reusable component
- Input Widget → Form control
- Button → Button with onClick
- Table Records → Data grid
- List Records → Loop/map
- If Widget → Conditional rendering

**Inputs:**
- Screens JSON
- Web blocks JSON
- Widgets and bindings JSON
- Screen actions JSON
- Available services (for API calls)

**Outputs:**
- Page component files (.razor/.tsx)
- Reusable component files (.razor/.tsx)
- CSS/SCSS files
- Navigation configuration

**AI Prompt Template:**
```
Convert the following OutSystems Screen to a Blazor component:

Screen: {screen_json}
Widgets: {widgets_json}
Data Actions: {data_actions_json}
Available APIs: {api_endpoints}

Requirements:
- Use Bootstrap 5 styling
- Include loading states
- Include error handling
- Wire to API endpoints
```

---

### 7. Integration Agent

**Role:** Generate integration services for REST/SOAP APIs

**Responsibilities:**
- Generate HttpClient services for REST consumes
- Generate API controllers for REST exposes
- Handle SOAP services (if any)
- Configure authentication
- Add retry policies

**Covers Component Mapping:**
- REST API Consume → HttpClient service
- REST API Expose → API Controller
- SOAP Web Service → CoreWCF or adapter

**Inputs:**
- REST consumes JSON
- REST exposes JSON
- SOAP services JSON
- Authentication requirements

**Outputs:**
- HttpClient service files (.cs)
- API controller files (.cs)
- Request/Response DTO files (.cs)
- API configuration

**AI Prompt Template:**
```
Generate a typed HttpClient service for the following REST API:

API: {rest_consume_json}
Authentication: {auth_type}

Requirements:
- Use IHttpClientFactory
- Include Polly retry policy
- Generate request/response DTOs
- Include error handling
```

---

### 8. Security Agent

**Role:** Implement authentication, authorization, and security features

**Responsibilities:**
- Generate role definitions
- Configure authorization policies
- Set up authentication (Identity/JWT/OAuth)
- Map screen/action access to policies
- Implement CSRF protection

**Covers Component Mapping:**
- User → ASP.NET Identity User
- Role → ASP.NET Core Role
- Login/Logout → Identity methods
- Check Role → [Authorize] attributes

**Inputs:**
- Roles JSON
- Permissions JSON
- Screen access rules
- Action access rules

**Outputs:**
- Role enum/constants
- Authorization policies configuration
- Identity configuration
- Attribute decorations for controllers/pages

---

### 9. Background Jobs Agent

**Role:** Convert timers and BPT processes to background jobs/workflows

**Responsibilities:**
- Convert timers to Hangfire/Quartz jobs
- Convert BPT processes to workflows (Elsa/Step Functions)
- Generate scheduled job configurations
- Map human activities to task queues

**Covers Component Mapping:**
- Timer → Hangfire / IHostedService
- BPT Process → Elsa Workflows / Step Functions
- Human Activity → Approval queue
- Wait → Durable timer

**Inputs:**
- Timers JSON
- Processes JSON
- Associated actions

**Outputs:**
- Background job classes (.cs)
- Workflow definitions
- Scheduler configuration
- Human task handlers

---

### 10. Configuration Agent

**Role:** Generate configuration and infrastructure setup

**Responsibilities:**
- Convert site properties to appsettings
- Generate environment-specific configs
- Set up dependency injection
- Configure logging
- Generate Docker/deployment files

**Covers:**
- Site Property → appsettings.json / IConfiguration
- Logging configuration
- DI registration
- Infrastructure as Code (optional)

**Inputs:**
- Site properties JSON
- Target environment (Dev/Staging/Prod)
- Infrastructure choices (AWS/Azure/on-prem)

**Outputs:**
- appsettings.json files
- Program.cs configuration
- Dockerfile
- docker-compose.yml
- Terraform/CDK (if cloud-native)

---

### 11. Compilation Agent

**Role:** Compile and verify generated code

**Responsibilities:**
- Run dotnet build
- Collect and report errors
- Identify missing references
- Suggest fixes

**Inputs:**
- Solution path

**Outputs:**
- Build result (success/failure)
- Error list with file/line references
- Suggested fixes

**Tools Required:**
- dotnet CLI
- File system access

---

### 12. Test Generation Agent

**Role:** Generate unit and integration tests

**Responsibilities:**
- Generate unit tests for services
- Generate integration tests for APIs
- Generate E2E test scenarios
- Calculate expected coverage

**Inputs:**
- Generated services
- Generated controllers
- Business rules documentation

**Outputs:**
- Unit test files (.cs)
- Integration test files (.cs)
- Test configuration

---

### 13. Review Agent

**Role:** Review generated code for quality and completeness

**Responsibilities:**
- Compare generated code with source OML
- Verify all components are migrated
- Check code quality
- Identify gaps
- Generate migration report

**Inputs:**
- Original parsed JSON
- Generated code files
- Test results

**Outputs:**
- Migration completeness report
- Code quality assessment
- Gap analysis
- Recommendations

---

## Workflow Sequence

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: EXTRACTION                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. Orchestrator receives OAP file                                       │
│ 2. Parser Agent extracts OML files                                      │
│ 3. Parser Agent parses each OML to JSON                                 │
│ 4. Analyzer Agent calculates complexity                                 │
│ 5. Analyzer Agent determines migration order                            │
│ 6. Orchestrator stores extraction results                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: GENERATION (Per Module, in dependency order)                   │
├─────────────────────────────────────────────────────────────────────────┤
│ For each module:                                                         │
│   7. Entity Agent generates domain models                               │
│   8. Business Logic Agent generates services                            │
│   9. UI Agent generates components                                       │
│  10. Integration Agent generates API clients/controllers                │
│  11. Security Agent configures auth                                     │
│  12. Background Jobs Agent generates jobs/workflows                     │
│  13. Configuration Agent generates config files                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: VALIDATION                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ 14. Compilation Agent builds solution                                    │
│ 15. If errors → route back to relevant Generation Agent for fixes      │
│ 16. Test Generation Agent creates tests                                 │
│ 17. Compilation Agent runs tests                                        │
│ 18. Review Agent validates completeness                                 │
│ 19. Review Agent generates final report                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Communication Protocol

### Message Format
```json
{
  "message_id": "uuid",
  "from_agent": "orchestrator",
  "to_agent": "entity_agent",
  "task_type": "generate_entities",
  "payload": {
    "module_name": "CustomerModule",
    "entities": [...],
    "relationships": [...],
    "output_path": "./src/Domain/Entities"
  },
  "context": {
    "migration_id": "uuid",
    "phase": "generation"
  }
}
```

### Response Format
```json
{
  "message_id": "uuid",
  "in_response_to": "original_message_id",
  "from_agent": "entity_agent",
  "status": "completed",
  "result": {
    "files_generated": [
      "Customer.cs",
      "Order.cs",
      "CustomerDbContext.cs"
    ],
    "warnings": [],
    "errors": []
  }
}
```

---

## Error Handling Strategy

### Retry Logic
```
For each agent task:
  1. Attempt task
  2. If failure:
     a. Log error
     b. If retryable → retry up to 3 times
     c. If not retryable → escalate to Orchestrator
  3. Orchestrator decides:
     a. Route to different agent
     b. Request human intervention
     c. Skip component and document gap
```

### Error Categories
| Category | Handling |
|----------|----------|
| Parse Error | Retry with different parser settings |
| Generation Error | Retry with simplified prompt |
| Compilation Error | Route error back to relevant agent for fix |
| Test Failure | Flag for review, continue if non-critical |
| Validation Gap | Document in report, continue |

---

## State Persistence

### Migration State Store
```json
{
  "migration_id": "uuid",
  "started_at": "2026-07-24T10:00:00Z",
  "status": "in_progress",
  "source": {
    "oap_path": "/input/app.oap",
    "modules": ["Core", "Customer", "Order"]
  },
  "target": {
    "output_path": "/output/MyApp",
    "stack": ".NET 8",
    "frontend": "Blazor"
  },
  "progress": {
    "extraction": {
      "status": "completed",
      "modules_extracted": 3
    },
    "generation": {
      "status": "in_progress",
      "modules_completed": 1,
      "current_module": "Customer"
    },
    "validation": {
      "status": "pending"
    }
  },
  "artifacts": {
    "parsed_json_path": "/work/parsed/",
    "generated_code_path": "/output/MyApp/src/"
  }
}
```

---

## Implementation Options

### Option 1: Factory Droids
- Create custom droids for each agent
- Use Factory's built-in orchestration
- Leverage existing tools (Read, Edit, Execute)

### Option 2: Python Multi-Agent Framework
- Use LangChain/AutoGen/CrewAI
- Custom agent implementations
- More flexibility, more setup

### Option 3: Hybrid Approach
- Orchestrator as Factory droid
- Specialized agents as Python scripts
- Best of both worlds

---

## Deliverables from Agent System

| Deliverable | Generated By |
|-------------|--------------|
| Parsed JSON (all modules) | Parser Agent |
| Complexity Report | Analyzer Agent |
| Entity Classes | Entity Agent |
| Service Classes | Business Logic Agent |
| UI Components | UI Agent |
| API Controllers | Integration Agent |
| Auth Configuration | Security Agent |
| Background Jobs | Background Jobs Agent |
| Config Files | Configuration Agent |
| Unit Tests | Test Generation Agent |
| Migration Report | Review Agent |

---

## Next Steps

1. **Finalize Agent Specifications** - Detail prompts and I/O for each agent
2. **Choose Implementation Approach** - Droids vs Python vs Hybrid
3. **Build Parser Agent First** - Foundation for all other agents
4. **Implement Orchestrator** - Workflow coordination
5. **Implement Generation Agents** - One at a time, validate each
6. **Implement Validation Agents** - Ensure quality
7. **End-to-End Testing** - Test with sample OutSystems app

---

*Document Version: 1.0*  
*Created: 2026-07-24*
