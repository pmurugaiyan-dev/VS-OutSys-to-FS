# Agentic Migration System Design v2

## OutSystems to .NET Migration using AI Agents

### Compatible with: Factory Droids / Claude Code

---

## Agent Execution Model

### Execution Types

| Type | Description | When to Use |
|------|-------------|-------------|
| **Python** | Pure Python code, no LLM | Deterministic tasks, parsing, calculations |
| **LLM** | Requires AI for generation | Complex code generation, natural language |
| **Hybrid** | Python + LLM fallback | Template-based with LLM for edge cases |

### Agent Classification

| # | Agent | Execution | Reason |
|---|-------|-----------|--------|
| 1 | Orchestrator | **Python** | Workflow control, state management |
| 2 | Parser | **Python** | XML parsing is deterministic |
| 3 | Analyzer | **Python** | Calculations, graph algorithms |
| 4 | Entity Generation | **LLM** | Complex C# code generation |
| 5 | Business Logic | **LLM** | Service method generation |
| 6 | UI Generation | **LLM** | Component generation |
| 7 | Integration | **LLM** | HTTP client generation |
| 8 | Security | **Hybrid** | Templates + LLM for complex policies |
| 9 | Background Jobs | **LLM** | Workflow/job generation |
| 10 | Configuration | **Python** | Template-based, deterministic |
| 11 | Compilation | **Python** | CLI execution |
| 12 | Test Generation | **LLM** | Test code generation |
| 13 | Review | **Python** | Comparison, validation logic |

**Summary:** 6 Python agents, 5 LLM agents, 2 Hybrid agents

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT (Python)                               │
│              Workflow Control, State Management, Coordination                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
     ┌────────────────────────────────┼────────────────────────────────┐
     ▼                                ▼                                ▼
┌─────────────┐              ┌─────────────────┐              ┌─────────────┐
│  EXTRACTION │              │   GENERATION    │              │ VALIDATION  │
│   (Python)  │              │  (LLM + Python) │              │  (Python)   │
└─────────────┘              └─────────────────┘              └─────────────┘
     │                                │                                │
┌────┴────┐              ┌────────────┴────────────┐          ┌───────┴───────┐
▼         ▼              ▼      ▼      ▼      ▼    ▼          ▼       ▼       ▼
Parser  Analyzer      Entity Logic   UI   Integ  Jobs     Compile  Test   Review
(Py)    (Py)          (LLM)  (LLM) (LLM) (LLM) (LLM)      (Py)    (LLM)   (Py)
```

---

## Detailed Agent Specifications

---

## 1. Orchestrator Agent

**Execution:** Python  
**LLM Required:** No

### Purpose
Central coordinator managing the migration workflow.

### Implementation

```python
# orchestrator.py
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

class MigrationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ModuleState:
    name: str
    status: MigrationStatus = MigrationStatus.PENDING
    extraction_status: MigrationStatus = MigrationStatus.PENDING
    generation_status: MigrationStatus = MigrationStatus.PENDING
    validation_status: MigrationStatus = MigrationStatus.PENDING
    errors: List[str] = field(default_factory=list)

@dataclass
class MigrationState:
    migration_id: str
    source_path: str
    output_path: str
    status: MigrationStatus = MigrationStatus.PENDING
    current_phase: str = "initialization"
    modules: List[ModuleState] = field(default_factory=list)
    migration_order: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Orchestrator:
    def __init__(self, config: dict):
        self.config = config
        self.state = None
        self.agents = {}
    
    def initialize_migration(self, oap_path: str, output_path: str) -> MigrationState:
        """Initialize a new migration"""
        import uuid
        self.state = MigrationState(
            migration_id=str(uuid.uuid4()),
            source_path=oap_path,
            output_path=output_path,
            started_at=datetime.utcnow()
        )
        return self.state
    
    def run_extraction_phase(self):
        """Execute extraction phase"""
        self.state.current_phase = "extraction"
        self.state.status = MigrationStatus.IN_PROGRESS
        
        # 1. Parser Agent extracts OML files
        parser = self.agents['parser']
        parsed_modules = parser.extract_all(self.state.source_path)
        
        # 2. Analyzer Agent determines migration order
        analyzer = self.agents['analyzer']
        analysis = analyzer.analyze(parsed_modules)
        
        self.state.migration_order = analysis['migration_order']
        for module_name in analysis['modules']:
            self.state.modules.append(ModuleState(name=module_name))
        
        return analysis
    
    def run_generation_phase(self):
        """Execute generation phase for each module"""
        self.state.current_phase = "generation"
        
        for module_name in self.state.migration_order:
            module_state = self._get_module_state(module_name)
            module_state.generation_status = MigrationStatus.IN_PROGRESS
            
            try:
                # Run generation agents in sequence
                self._generate_entities(module_name)
                self._generate_services(module_name)
                self._generate_ui(module_name)
                self._generate_integrations(module_name)
                self._generate_security(module_name)
                self._generate_jobs(module_name)
                self._generate_config(module_name)
                
                module_state.generation_status = MigrationStatus.COMPLETED
            except Exception as e:
                module_state.generation_status = MigrationStatus.FAILED
                module_state.errors.append(str(e))
    
    def run_validation_phase(self):
        """Execute validation phase"""
        self.state.current_phase = "validation"
        
        # 1. Compile
        compiler = self.agents['compiler']
        build_result = compiler.build(self.state.output_path)
        
        if not build_result['success']:
            # Route errors back to relevant agents
            self._handle_build_errors(build_result['errors'])
        
        # 2. Generate tests
        test_gen = self.agents['test_generator']
        test_gen.generate_tests(self.state.output_path)
        
        # 3. Run tests
        test_result = compiler.run_tests(self.state.output_path)
        
        # 4. Review
        reviewer = self.agents['reviewer']
        report = reviewer.generate_report(self.state)
        
        return report
    
    def save_state(self, path: str):
        """Persist migration state"""
        with open(path, 'w') as f:
            json.dump(self.state.__dict__, f, indent=2, default=str)
    
    def load_state(self, path: str):
        """Resume from saved state"""
        with open(path, 'r') as f:
            data = json.load(f)
            self.state = MigrationState(**data)
    
    def _get_module_state(self, module_name: str) -> ModuleState:
        for m in self.state.modules:
            if m.name == module_name:
                return m
        return None
```

### Factory Droid Configuration
```yaml
# .factory/droids/migration-orchestrator.yaml
name: migration-orchestrator
description: Orchestrates the OutSystems to .NET migration workflow
model: inherit
system_prompt: |
  You are the migration orchestrator. You coordinate the migration workflow
  by invoking other agents in the correct sequence. You track state and
  handle errors. Use the provided Python code for workflow control.
  
  Available tools:
  - Execute: Run Python scripts
  - Read/Write: File operations
  - Task: Invoke other agents
```

---

## 2. Parser Agent

**Execution:** Python  
**LLM Required:** No

### Purpose
Extract and parse OML files into structured JSON.

### Implementation

```python
# parser_agent.py
import xml.etree.ElementTree as ET
import json
import os
import zipfile
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class ParsedModule:
    module_name: str
    module_type: str
    entities: List[Dict]
    static_entities: List[Dict]
    relationships: List[Dict]
    indexes: List[Dict]
    structures: List[Dict]
    server_actions: List[Dict]
    client_actions: List[Dict]
    aggregates: List[Dict]
    screens: List[Dict]
    web_blocks: List[Dict]
    rest_consumes: List[Dict]
    rest_exposes: List[Dict]
    timers: List[Dict]
    processes: List[Dict]
    roles: List[Dict]
    site_properties: List[Dict]
    resources: List[Dict]
    extensions: List[Dict]
    dependencies: List[Dict]

class ParserAgent:
    """
    Pure Python agent - No LLM required
    Parses OML (XML) files into structured JSON
    """
    
    def __init__(self, work_dir: str = "./work"):
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)
    
    def extract_oap(self, oap_path: str) -> str:
        """Extract OAP file (ZIP) to work directory"""
        extract_dir = os.path.join(self.work_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(oap_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        return extract_dir
    
    def find_oml_files(self, directory: str) -> List[str]:
        """Find all OML files in directory"""
        oml_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.oml'):
                    oml_files.append(os.path.join(root, file))
        return oml_files
    
    def parse_oml(self, oml_path: str) -> ParsedModule:
        """Parse single OML file to structured data"""
        tree = ET.parse(oml_path)
        root = tree.getroot()
        
        return ParsedModule(
            module_name=root.get("Name", "Unknown"),
            module_type=self._detect_module_type(root),
            entities=self._extract_entities(root),
            static_entities=self._extract_static_entities(root),
            relationships=self._extract_relationships(root),
            indexes=self._extract_indexes(root),
            structures=self._extract_structures(root),
            server_actions=self._extract_server_actions(root),
            client_actions=self._extract_client_actions(root),
            aggregates=self._extract_aggregates(root),
            screens=self._extract_screens(root),
            web_blocks=self._extract_web_blocks(root),
            rest_consumes=self._extract_rest_consumes(root),
            rest_exposes=self._extract_rest_exposes(root),
            timers=self._extract_timers(root),
            processes=self._extract_processes(root),
            roles=self._extract_roles(root),
            site_properties=self._extract_site_properties(root),
            resources=self._extract_resources(root),
            extensions=self._extract_extensions(root),
            dependencies=self._extract_dependencies(root)
        )
    
    def _detect_module_type(self, root) -> str:
        """Detect if module is Reactive, Traditional, Service, or Library"""
        if root.find(".//Screen") is not None:
            return "Reactive"
        elif root.find(".//WebScreen") is not None:
            return "Traditional"
        elif root.find(".//RESTExpose") is not None:
            return "Service"
        else:
            return "Library"
    
    def _extract_entities(self, root) -> List[Dict]:
        """Extract entity definitions"""
        entities = []
        for entity in root.findall(".//Entity"):
            entity_data = {
                "name": entity.get("Name"),
                "is_public": entity.get("IsPublic") == "true",
                "description": entity.get("Description", ""),
                "attributes": []
            }
            
            for attr in entity.findall(".//Attribute"):
                attr_data = {
                    "name": attr.get("Name"),
                    "type": attr.get("Type"),
                    "length": attr.get("Length"),
                    "decimals": attr.get("Decimals"),
                    "is_mandatory": attr.get("IsMandatory") == "true",
                    "is_auto_number": attr.get("IsAutoNumber") == "true",
                    "default_value": attr.get("DefaultValue"),
                    "description": attr.get("Description", "")
                }
                
                # Check for foreign key
                ref = attr.find(".//ReferenceAttribute")
                if ref is not None:
                    attr_data["foreign_key"] = {
                        "entity": ref.get("Entity"),
                        "delete_rule": ref.get("DeleteRule", "Protect")
                    }
                
                entity_data["attributes"].append(attr_data)
            
            entities.append(entity_data)
        
        return entities
    
    def _extract_static_entities(self, root) -> List[Dict]:
        """Extract static entity (enum) definitions"""
        static_entities = []
        for se in root.findall(".//StaticEntity"):
            se_data = {
                "name": se.get("Name"),
                "is_public": se.get("IsPublic") == "true",
                "attributes": [],
                "records": []
            }
            
            for attr in se.findall("./Attribute"):
                se_data["attributes"].append({
                    "name": attr.get("Name"),
                    "type": attr.get("Type")
                })
            
            for record in se.findall(".//Record"):
                record_data = {}
                for attr in record.findall(".//Attribute"):
                    record_data[attr.get("Name")] = attr.get("Value")
                se_data["records"].append(record_data)
            
            static_entities.append(se_data)
        
        return static_entities
    
    def _extract_relationships(self, root) -> List[Dict]:
        """Extract foreign key relationships"""
        relationships = []
        for entity in root.findall(".//Entity"):
            entity_name = entity.get("Name")
            for attr in entity.findall(".//Attribute"):
                ref = attr.find(".//ReferenceAttribute")
                if ref is not None:
                    relationships.append({
                        "from_entity": entity_name,
                        "from_attribute": attr.get("Name"),
                        "to_entity": ref.get("Entity"),
                        "delete_rule": ref.get("DeleteRule", "Protect"),
                        "is_mandatory": attr.get("IsMandatory") == "true"
                    })
        return relationships
    
    def _extract_indexes(self, root) -> List[Dict]:
        """Extract index definitions"""
        indexes = []
        for entity in root.findall(".//Entity"):
            entity_name = entity.get("Name")
            for idx in entity.findall(".//Index"):
                index_data = {
                    "entity": entity_name,
                    "name": idx.get("Name"),
                    "is_unique": idx.get("IsUnique") == "true",
                    "attributes": []
                }
                for attr in idx.findall(".//IndexAttribute"):
                    index_data["attributes"].append({
                        "name": attr.get("Attribute"),
                        "order": attr.get("Order", "Ascending")
                    })
                indexes.append(index_data)
        return indexes
    
    def _extract_structures(self, root) -> List[Dict]:
        """Extract structure (DTO) definitions"""
        structures = []
        for struct in root.findall(".//Structure"):
            struct_data = {
                "name": struct.get("Name"),
                "is_public": struct.get("IsPublic") == "true",
                "attributes": []
            }
            for attr in struct.findall(".//Attribute"):
                struct_data["attributes"].append({
                    "name": attr.get("Name"),
                    "type": attr.get("Type"),
                    "is_list": attr.get("IsList") == "true"
                })
            structures.append(struct_data)
        return structures
    
    def _extract_server_actions(self, root) -> List[Dict]:
        """Extract server action definitions"""
        actions = []
        for action in root.findall(".//Action"):
            if action.get("IsServerAction") == "true":
                action_data = {
                    "name": action.get("Name"),
                    "is_public": action.get("IsPublic") == "true",
                    "description": action.get("Description", ""),
                    "inputs": [],
                    "outputs": [],
                    "variables": [],
                    "flow": []
                }
                
                for param in action.findall(".//InputParameter"):
                    action_data["inputs"].append({
                        "name": param.get("Name"),
                        "type": param.get("Type"),
                        "is_mandatory": param.get("IsMandatory") == "true",
                        "default": param.get("DefaultValue")
                    })
                
                for param in action.findall(".//OutputParameter"):
                    action_data["outputs"].append({
                        "name": param.get("Name"),
                        "type": param.get("Type")
                    })
                
                for var in action.findall(".//Variable"):
                    action_data["variables"].append({
                        "name": var.get("Name"),
                        "type": var.get("Type")
                    })
                
                # Extract flow nodes
                flow_types = ["Aggregate", "SQL", "CreateRecord", "UpdateRecord",
                             "DeleteRecord", "If", "Switch", "ForEach", "Assign",
                             "RaiseException", "Execute", "RunServerAction"]
                for ft in flow_types:
                    for node in action.findall(f".//{ft}"):
                        action_data["flow"].append({
                            "type": ft,
                            "name": node.get("Name"),
                            "properties": dict(node.attrib)
                        })
                
                actions.append(action_data)
        return actions
    
    def _extract_client_actions(self, root) -> List[Dict]:
        """Extract client action definitions"""
        actions = []
        for action in root.findall(".//ClientAction"):
            action_data = {
                "name": action.get("Name"),
                "inputs": [],
                "outputs": [],
                "flow": []
            }
            
            for param in action.findall(".//InputParameter"):
                action_data["inputs"].append({
                    "name": param.get("Name"),
                    "type": param.get("Type")
                })
            
            for param in action.findall(".//OutputParameter"):
                action_data["outputs"].append({
                    "name": param.get("Name"),
                    "type": param.get("Type")
                })
            
            actions.append(action_data)
        return actions
    
    def _extract_aggregates(self, root) -> List[Dict]:
        """Extract aggregate (query) definitions"""
        aggregates = []
        for agg in root.findall(".//Aggregate"):
            agg_data = {
                "name": agg.get("Name"),
                "sources": [],
                "joins": [],
                "filters": [],
                "sorts": [],
                "max_records": agg.get("MaxRecords"),
                "outputs": []
            }
            
            for source in agg.findall(".//Source"):
                agg_data["sources"].append(source.get("Entity"))
            
            for join in agg.findall(".//Join"):
                agg_data["joins"].append({
                    "entity": join.get("Entity"),
                    "type": join.get("JoinType", "Inner"),
                    "condition": join.get("Condition")
                })
            
            for flt in agg.findall(".//Filter"):
                agg_data["filters"].append(flt.get("Condition"))
            
            for sort in agg.findall(".//Sort"):
                agg_data["sorts"].append({
                    "attribute": sort.get("Attribute"),
                    "direction": sort.get("Direction", "Ascending")
                })
            
            aggregates.append(agg_data)
        return aggregates
    
    def _extract_screens(self, root) -> List[Dict]:
        """Extract screen definitions"""
        screens = []
        for screen in list(root.findall(".//Screen")) + list(root.findall(".//WebScreen")):
            screen_data = {
                "name": screen.get("Name"),
                "title": screen.get("Title", ""),
                "type": screen.tag,
                "is_default": screen.get("IsDefault") == "true",
                "inputs": [],
                "variables": [],
                "data_actions": [],
                "widgets": []
            }
            
            for param in screen.findall(".//InputParameter"):
                screen_data["inputs"].append({
                    "name": param.get("Name"),
                    "type": param.get("Type"),
                    "is_mandatory": param.get("IsMandatory") == "true"
                })
            
            for var in screen.findall(".//LocalVariable"):
                screen_data["variables"].append({
                    "name": var.get("Name"),
                    "type": var.get("Type")
                })
            
            # Extract widgets
            widget_types = ["Container", "Input", "TextArea", "Button", "Link",
                          "Table", "List", "If", "Label", "Expression",
                          "Dropdown", "Checkbox", "RadioButton", "Image"]
            for wt in widget_types:
                for widget in screen.findall(f".//{wt}"):
                    screen_data["widgets"].append({
                        "type": wt,
                        "name": widget.get("Name"),
                        "variable": widget.get("Variable"),
                        "action": widget.get("Action"),
                        "source": widget.get("Source")
                    })
            
            screens.append(screen_data)
        return screens
    
    def _extract_web_blocks(self, root) -> List[Dict]:
        """Extract web block definitions"""
        blocks = []
        for block in list(root.findall(".//WebBlock")) + list(root.findall(".//Block")):
            block_data = {
                "name": block.get("Name"),
                "is_public": block.get("IsPublic") == "true",
                "inputs": [],
                "outputs": [],
                "placeholders": []
            }
            
            for param in block.findall(".//InputParameter"):
                block_data["inputs"].append({
                    "name": param.get("Name"),
                    "type": param.get("Type")
                })
            
            for ph in block.findall(".//Placeholder"):
                block_data["placeholders"].append(ph.get("Name"))
            
            blocks.append(block_data)
        return blocks
    
    def _extract_rest_consumes(self, root) -> List[Dict]:
        """Extract REST consume definitions"""
        rest_apis = []
        for rest in root.findall(".//RESTConsume"):
            api_data = {
                "name": rest.get("Name"),
                "base_url": rest.get("BaseURL"),
                "authentication": None,
                "methods": []
            }
            
            auth = rest.find(".//Authentication")
            if auth is not None:
                api_data["authentication"] = {
                    "type": auth.get("Type"),
                    "username": auth.get("Username"),
                    "header_name": auth.get("HeaderName")
                }
            
            for method in rest.findall(".//Method"):
                method_data = {
                    "name": method.get("Name"),
                    "http_method": method.get("HTTPMethod"),
                    "url_path": method.get("URLPath"),
                    "inputs": [],
                    "outputs": []
                }
                
                for inp in method.findall(".//Input"):
                    method_data["inputs"].append({
                        "name": inp.get("Name"),
                        "type": inp.get("Type"),
                        "send_in": inp.get("SendIn", "Body")
                    })
                
                for out in method.findall(".//Output"):
                    method_data["outputs"].append({
                        "name": out.get("Name"),
                        "type": out.get("Type")
                    })
                
                api_data["methods"].append(method_data)
            
            rest_apis.append(api_data)
        return rest_apis
    
    def _extract_rest_exposes(self, root) -> List[Dict]:
        """Extract REST expose definitions"""
        exposed_apis = []
        for rest in root.findall(".//RESTExpose"):
            api_data = {
                "name": rest.get("Name"),
                "base_path": rest.get("BasePath"),
                "methods": []
            }
            
            for method in rest.findall(".//Method"):
                method_data = {
                    "name": method.get("Name"),
                    "http_method": method.get("HTTPMethod"),
                    "url_path": method.get("URLPath"),
                    "inputs": [],
                    "outputs": []
                }
                
                for inp in method.findall(".//Input"):
                    method_data["inputs"].append({
                        "name": inp.get("Name"),
                        "type": inp.get("Type"),
                        "source": inp.get("Source")
                    })
                
                for out in method.findall(".//Output"):
                    method_data["outputs"].append({
                        "name": out.get("Name"),
                        "type": out.get("Type")
                    })
                
                api_data["methods"].append(method_data)
            
            exposed_apis.append(api_data)
        return exposed_apis
    
    def _extract_timers(self, root) -> List[Dict]:
        """Extract timer definitions"""
        timers = []
        for timer in root.findall(".//Timer"):
            action = timer.find(".//Action")
            timers.append({
                "name": timer.get("Name"),
                "schedule": timer.get("Schedule"),
                "timeout": timer.get("Timeout"),
                "action": action.get("Name") if action is not None else None,
                "is_active": timer.get("IsActive", "true") == "true"
            })
        return timers
    
    def _extract_processes(self, root) -> List[Dict]:
        """Extract BPT process definitions"""
        processes = []
        for proc in root.findall(".//Process"):
            proc_data = {
                "name": proc.get("Name"),
                "inputs": [],
                "activities": []
            }
            
            for inp in proc.findall(".//ProcessInput"):
                proc_data["inputs"].append({
                    "name": inp.get("Name"),
                    "type": inp.get("Type")
                })
            
            activity_types = ["Start", "End", "AutomaticActivity", 
                            "HumanActivity", "Decision", "Wait"]
            for at in activity_types:
                for act in proc.findall(f".//{at}"):
                    proc_data["activities"].append({
                        "type": at,
                        "name": act.get("Name"),
                        "role": act.get("Role") if at == "HumanActivity" else None
                    })
            
            processes.append(proc_data)
        return processes
    
    def _extract_roles(self, root) -> List[Dict]:
        """Extract role definitions"""
        roles = []
        for role in root.findall(".//Role"):
            roles.append({
                "name": role.get("Name"),
                "is_persistent": role.get("IsPersistent") == "true"
            })
        return roles
    
    def _extract_site_properties(self, root) -> List[Dict]:
        """Extract site property definitions"""
        properties = []
        for prop in root.findall(".//SiteProperty"):
            properties.append({
                "name": prop.get("Name"),
                "type": prop.get("Type"),
                "default_value": prop.get("DefaultValue"),
                "is_public": prop.get("IsPublic") == "true"
            })
        return properties
    
    def _extract_resources(self, root) -> List[Dict]:
        """Extract resource definitions"""
        resources = []
        for res in root.findall(".//Resource"):
            resources.append({
                "name": res.get("Name"),
                "type": res.get("Type"),
                "filename": res.get("Filename")
            })
        return resources
    
    def _extract_extensions(self, root) -> List[Dict]:
        """Extract extension references"""
        extensions = []
        for ext in root.findall(".//Extension"):
            ext_data = {
                "name": ext.get("Name"),
                "actions": [],
                "structures": []
            }
            for action in ext.findall(".//Action"):
                ext_data["actions"].append(action.get("Name"))
            for struct in ext.findall(".//Structure"):
                ext_data["structures"].append(struct.get("Name"))
            extensions.append(ext_data)
        return extensions
    
    def _extract_dependencies(self, root) -> List[Dict]:
        """Extract module dependencies"""
        dependencies = []
        for ref in root.findall(".//Reference"):
            dependencies.append({
                "name": ref.get("Name"),
                "type": ref.get("Type")
            })
        for dep in root.findall(".//Dependency"):
            dependencies.append({
                "producer": dep.get("Producer"),
                "type": "producer"
            })
        return dependencies
    
    def extract_all(self, oap_path: str) -> Dict[str, ParsedModule]:
        """Extract all modules from OAP file"""
        extract_dir = self.extract_oap(oap_path)
        oml_files = self.find_oml_files(extract_dir)
        
        modules = {}
        for oml_path in oml_files:
            parsed = self.parse_oml(oml_path)
            modules[parsed.module_name] = parsed
        
        return modules
    
    def save_to_json(self, modules: Dict[str, ParsedModule], output_dir: str):
        """Save parsed modules to JSON files"""
        os.makedirs(output_dir, exist_ok=True)
        
        for name, module in modules.items():
            output_path = os.path.join(output_dir, f"{name}.json")
            with open(output_path, 'w') as f:
                json.dump(asdict(module), f, indent=2)
        
        # Save combined summary
        summary = {
            "total_modules": len(modules),
            "modules": list(modules.keys())
        }
        with open(os.path.join(output_dir, "_summary.json"), 'w') as f:
            json.dump(summary, f, indent=2)
```

---

## 3. Analyzer Agent

**Execution:** Python  
**LLM Required:** No

### Purpose
Analyze parsed data for complexity and dependencies.

### Implementation

```python
# analyzer_agent.py
from typing import Dict, List, Tuple
from collections import defaultdict
import json

class AnalyzerAgent:
    """
    Pure Python agent - No LLM required
    Analyzes complexity and determines migration order
    """
    
    # Complexity weights
    WEIGHTS = {
        "entity": 1,
        "static_entity": 0.5,
        "screen": 2,
        "server_action": 1.5,
        "client_action": 1,
        "aggregate": 0.5,
        "rest_consume": 3,
        "rest_expose": 2,
        "timer": 2,
        "process": 5,
        "extension": 4
    }
    
    def analyze(self, modules: Dict) -> Dict:
        """Full analysis of all modules"""
        return {
            "modules": list(modules.keys()),
            "complexity_scores": self._calculate_complexity(modules),
            "total_complexity": self._total_complexity(modules),
            "complexity_level": self._complexity_level(modules),
            "migration_order": self._determine_migration_order(modules),
            "dependency_graph": self._build_dependency_graph(modules),
            "risk_assessment": self._assess_risks(modules),
            "statistics": self._gather_statistics(modules)
        }
    
    def _calculate_complexity(self, modules: Dict) -> Dict[str, float]:
        """Calculate complexity score per module"""
        scores = {}
        for name, module in modules.items():
            score = 0
            if hasattr(module, '__dict__'):
                module = module.__dict__
            
            score += len(module.get("entities", [])) * self.WEIGHTS["entity"]
            score += len(module.get("static_entities", [])) * self.WEIGHTS["static_entity"]
            score += len(module.get("screens", [])) * self.WEIGHTS["screen"]
            score += len(module.get("server_actions", [])) * self.WEIGHTS["server_action"]
            score += len(module.get("client_actions", [])) * self.WEIGHTS["client_action"]
            score += len(module.get("aggregates", [])) * self.WEIGHTS["aggregate"]
            score += len(module.get("rest_consumes", [])) * self.WEIGHTS["rest_consume"]
            score += len(module.get("rest_exposes", [])) * self.WEIGHTS["rest_expose"]
            score += len(module.get("timers", [])) * self.WEIGHTS["timer"]
            score += len(module.get("processes", [])) * self.WEIGHTS["process"]
            score += len(module.get("extensions", [])) * self.WEIGHTS["extension"]
            
            scores[name] = score
        
        return scores
    
    def _total_complexity(self, modules: Dict) -> float:
        """Calculate total complexity"""
        scores = self._calculate_complexity(modules)
        return sum(scores.values())
    
    def _complexity_level(self, modules: Dict) -> str:
        """Determine complexity level"""
        total = self._total_complexity(modules)
        if total < 100:
            return "Low"
        elif total < 500:
            return "Medium"
        elif total < 1000:
            return "High"
        else:
            return "Very High"
    
    def _build_dependency_graph(self, modules: Dict) -> Dict[str, List[str]]:
        """Build module dependency graph"""
        graph = defaultdict(list)
        
        for name, module in modules.items():
            if hasattr(module, '__dict__'):
                module = module.__dict__
            
            for dep in module.get("dependencies", []):
                producer = dep.get("producer") or dep.get("name")
                if producer and producer in modules:
                    graph[name].append(producer)
        
        return dict(graph)
    
    def _determine_migration_order(self, modules: Dict) -> List[str]:
        """Topological sort to determine migration order"""
        graph = self._build_dependency_graph(modules)
        
        # Kahn's algorithm for topological sort
        in_degree = defaultdict(int)
        for node in modules.keys():
            in_degree[node] = 0
        
        for node, deps in graph.items():
            for dep in deps:
                in_degree[node] += 1
        
        # Start with nodes that have no dependencies
        queue = [node for node in modules.keys() if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Find nodes that depend on this one
            for other_node, deps in graph.items():
                if node in deps:
                    in_degree[other_node] -= 1
                    if in_degree[other_node] == 0 and other_node not in result:
                        queue.append(other_node)
        
        # Add any remaining modules (circular dependencies)
        for node in modules.keys():
            if node not in result:
                result.append(node)
        
        return result
    
    def _assess_risks(self, modules: Dict) -> List[Dict]:
        """Identify high-risk components"""
        risks = []
        
        for name, module in modules.items():
            if hasattr(module, '__dict__'):
                module = module.__dict__
            
            # BPT processes are high risk
            for proc in module.get("processes", []):
                risks.append({
                    "module": name,
                    "component": proc.get("name"),
                    "type": "BPT Process",
                    "risk": "High",
                    "reason": "Business process requires workflow engine"
                })
            
            # Extensions are high risk
            for ext in module.get("extensions", []):
                risks.append({
                    "module": name,
                    "component": ext.get("name"),
                    "type": "Extension",
                    "risk": "High",
                    "reason": "Custom code requires manual review"
                })
            
            # Complex integrations
            for rest in module.get("rest_consumes", []):
                if rest.get("authentication"):
                    risks.append({
                        "module": name,
                        "component": rest.get("name"),
                        "type": "REST Consume",
                        "risk": "Medium",
                        "reason": "Authentication required"
                    })
        
        return risks
    
    def _gather_statistics(self, modules: Dict) -> Dict:
        """Gather overall statistics"""
        stats = {
            "total_modules": len(modules),
            "total_entities": 0,
            "total_screens": 0,
            "total_server_actions": 0,
            "total_client_actions": 0,
            "total_integrations": 0,
            "total_timers": 0,
            "total_processes": 0
        }
        
        for module in modules.values():
            if hasattr(module, '__dict__'):
                module = module.__dict__
            
            stats["total_entities"] += len(module.get("entities", []))
            stats["total_screens"] += len(module.get("screens", []))
            stats["total_server_actions"] += len(module.get("server_actions", []))
            stats["total_client_actions"] += len(module.get("client_actions", []))
            stats["total_integrations"] += len(module.get("rest_consumes", []))
            stats["total_integrations"] += len(module.get("rest_exposes", []))
            stats["total_timers"] += len(module.get("timers", []))
            stats["total_processes"] += len(module.get("processes", []))
        
        return stats
```

---

## 4. Entity Generation Agent

**Execution:** LLM  
**LLM Required:** Yes

### Purpose
Generate C# entity classes from OutSystems entities.

### Why LLM is Needed
- Complex type mapping with edge cases
- Generating meaningful XML documentation
- Handling naming conventions
- Creating appropriate validation attributes

### Factory Droid Configuration

```yaml
# .factory/droids/entity-generator.yaml
name: entity-generator
description: Generates C# entity classes from OutSystems entity definitions
model: inherit
system_prompt: |
  You are a .NET entity generation specialist. You convert OutSystems entity 
  definitions to C# EF Core entity classes.
  
  Rules:
  1. Use data annotations for validation and mapping
  2. Include XML documentation comments
  3. Generate navigation properties for relationships
  4. Use PascalCase for all names
  5. Map OutSystems types correctly:
     - Integer → int
     - Long Integer → long
     - Decimal → decimal
     - Text → string with [MaxLength]
     - Date → DateOnly
     - DateTime → DateTime
     - Boolean → bool
     - Binary Data → byte[]
     - Email → string with [EmailAddress]
     - Phone Number → string
  
  Output only the C# code, no explanations.
```

### Input Format
```json
{
  "entity": {
    "name": "Customer",
    "attributes": [
      {"name": "Id", "type": "Integer", "is_auto_number": true},
      {"name": "Name", "type": "Text", "length": "100", "is_mandatory": true}
    ]
  },
  "relationships": [
    {"from_entity": "Order", "from_attribute": "CustomerId", "to_entity": "Customer"}
  ]
}
```

### Output Format
```csharp
// Customer.cs
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MyApp.Domain.Entities;

/// <summary>
/// Represents a customer in the system.
/// </summary>
[Table("Customer")]
public class Customer
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    [Required]
    [MaxLength(100)]
    public string Name { get; set; } = string.Empty;

    // Navigation properties
    public virtual ICollection<Order> Orders { get; set; } = new List<Order>();
}
```

---

## 5. Business Logic Agent

**Execution:** LLM  
**LLM Required:** Yes

### Purpose
Convert server actions to C# service methods.

### Why LLM is Needed
- Understanding action flow logic
- Converting visual programming to imperative code
- Generating appropriate error handling
- Creating meaningful method signatures

### Factory Droid Configuration

```yaml
# .factory/droids/business-logic-generator.yaml
name: business-logic-generator
description: Converts OutSystems server actions to C# service methods
model: inherit
system_prompt: |
  You are a .NET service layer specialist. You convert OutSystems server 
  actions to C# service methods.
  
  Rules:
  1. Create async methods
  2. Use repository pattern for data access
  3. Include proper logging with ILogger
  4. Include try-catch with appropriate exception handling
  5. Use DTOs for input/output
  6. Follow SOLID principles
  
  Flow node mappings:
  - Aggregate → _repository.GetAsync() with LINQ
  - CreateRecord → _repository.AddAsync()
  - UpdateRecord → _repository.UpdateAsync()
  - DeleteRecord → _repository.DeleteAsync()
  - If → if statement
  - ForEach → foreach loop
  - Assign → variable assignment
  - RaiseException → throw new Exception()
  
  Output the complete service interface and implementation.
```

---

## 6. UI Generation Agent

**Execution:** LLM  
**LLM Required:** Yes

### Purpose
Convert screens to Blazor/React components.

### Why LLM is Needed
- Complex widget-to-component mapping
- Understanding data bindings
- Generating event handlers
- Creating responsive layouts

### Factory Droid Configuration

```yaml
# .factory/droids/ui-generator.yaml
name: ui-generator
description: Converts OutSystems screens to Blazor components
model: inherit
system_prompt: |
  You are a Blazor UI specialist. You convert OutSystems screens to 
  Blazor components.
  
  Rules:
  1. Use Bootstrap 5 for styling
  2. Include loading states
  3. Include error handling
  4. Wire to injected services
  5. Use @code section for logic
  
  Widget mappings:
  - Input → <InputText> or <input>
  - Button → <button @onclick>
  - Table → <table> with @foreach
  - List → @foreach
  - If → @if
  - Container → <div>
  - Link → <NavLink>
  
  Output complete .razor file.
```

---

## 7. Integration Agent

**Execution:** LLM  
**LLM Required:** Yes

### Purpose
Generate HttpClient services for REST APIs.

### Factory Droid Configuration

```yaml
# .factory/droids/integration-generator.yaml
name: integration-generator
description: Generates HttpClient services for REST API integration
model: inherit
system_prompt: |
  You are a .NET HTTP integration specialist. You generate typed 
  HttpClient services for REST API consumption.
  
  Rules:
  1. Use IHttpClientFactory pattern
  2. Include Polly retry policies
  3. Generate request/response DTOs
  4. Handle authentication (Basic, Bearer, API Key)
  5. Include proper error handling
  6. Use System.Text.Json for serialization
  
  Output interface, implementation, and DTOs.
```

---

## 8. Security Agent

**Execution:** Hybrid (Python + LLM)  
**LLM Required:** For complex policies

### Purpose
Configure authentication and authorization.

### Python Part (Template-Based)

```python
# security_agent.py
from typing import Dict, List
import os

class SecurityAgent:
    """
    Hybrid agent - Python for templates, LLM for complex policies
    """
    
    def generate_roles_enum(self, roles: List[Dict]) -> str:
        """Generate roles enum - Pure Python"""
        lines = [
            "namespace MyApp.Domain.Constants;",
            "",
            "public static class Roles",
            "{"
        ]
        
        for role in roles:
            name = role["name"].replace(" ", "")
            lines.append(f'    public const string {name} = "{role["name"]}";')
        
        lines.append("}")
        return "\n".join(lines)
    
    def generate_authorization_config(self, permissions: List[Dict]) -> str:
        """Generate authorization configuration - Pure Python"""
        lines = [
            "// In Program.cs",
            "builder.Services.AddAuthorization(options =>",
            "{"
        ]
        
        # Group permissions by resource
        by_resource = {}
        for perm in permissions:
            resource = perm["resource"]
            if resource not in by_resource:
                by_resource[resource] = []
            by_resource[resource].append(perm["role"])
        
        for resource, roles in by_resource.items():
            roles_str = ", ".join([f'"{r}"' for r in roles])
            lines.append(f'    options.AddPolicy("CanAccess{resource}", policy =>')
            lines.append(f'        policy.RequireRole({roles_str}));')
        
        lines.append("});")
        return "\n".join(lines)
    
    def needs_llm(self, permissions: List[Dict]) -> bool:
        """Determine if LLM is needed for complex policies"""
        # LLM needed for complex conditional policies
        for perm in permissions:
            if perm.get("condition") or perm.get("custom_logic"):
                return True
        return False
```

---

## 9. Background Jobs Agent

**Execution:** LLM  
**LLM Required:** Yes

### Purpose
Convert timers and BPT processes to Hangfire jobs and workflows.

### Factory Droid Configuration

```yaml
# .factory/droids/background-jobs-generator.yaml
name: background-jobs-generator
description: Converts OutSystems timers and BPT to Hangfire jobs and Elsa workflows
model: inherit
system_prompt: |
  You are a background job specialist. You convert OutSystems timers 
  to Hangfire recurring jobs and BPT processes to Elsa workflows.
  
  For Timers:
  1. Create job class with Execute method
  2. Configure Hangfire recurring job with cron expression
  3. Include logging and error handling
  
  For BPT Processes:
  1. Create Elsa workflow definition
  2. Map activities to workflow steps
  3. Handle human activities with task queues
  4. Implement wait conditions
  
  Output complete job/workflow classes.
```

---

## 10. Configuration Agent

**Execution:** Python  
**LLM Required:** No

### Purpose
Generate configuration files from site properties.

### Implementation

```python
# configuration_agent.py
import json
import os
from typing import Dict, List

class ConfigurationAgent:
    """
    Pure Python agent - No LLM required
    Generates configuration files from site properties
    """
    
    def generate_appsettings(self, site_properties: List[Dict], 
                             environment: str = "Development") -> str:
        """Generate appsettings.json"""
        config = {
            "Logging": {
                "LogLevel": {
                    "Default": "Information",
                    "Microsoft.AspNetCore": "Warning"
                }
            },
            "AllowedHosts": "*",
            "AppSettings": {}
        }
        
        for prop in site_properties:
            name = prop["name"]
            value = prop.get("default_value", "")
            prop_type = prop.get("type", "Text")
            
            # Convert value based on type
            if prop_type == "Boolean":
                value = value.lower() == "true"
            elif prop_type == "Integer":
                value = int(value) if value else 0
            elif prop_type == "Decimal":
                value = float(value) if value else 0.0
            
            config["AppSettings"][name] = value
        
        return json.dumps(config, indent=2)
    
    def generate_program_cs_config(self, modules: List[str]) -> str:
        """Generate Program.cs DI configuration"""
        lines = [
            "// Service Registration",
            "builder.Services.AddDbContext<ApplicationDbContext>(options =>",
            "    options.UseNpgsql(builder.Configuration.GetConnectionString(\"Default\")));",
            "",
            "// Repositories"
        ]
        
        # Add repository registrations
        lines.append("builder.Services.AddScoped(typeof(IRepository<>), typeof(Repository<>));")
        lines.append("")
        lines.append("// Services")
        
        for module in modules:
            lines.append(f"builder.Services.AddScoped<I{module}Service, {module}Service>();")
        
        return "\n".join(lines)
    
    def generate_dockerfile(self, project_name: str) -> str:
        """Generate Dockerfile"""
        return f"""FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["{project_name}.csproj", "."]
RUN dotnet restore "{project_name}.csproj"
COPY . .
RUN dotnet build "{project_name}.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "{project_name}.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "{project_name}.dll"]
"""
    
    def generate_docker_compose(self, project_name: str) -> str:
        """Generate docker-compose.yml"""
        return f"""version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__Default=Host=postgres;Database=appdb;Username=appuser;Password=secret
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
"""
```

---

## 11. Compilation Agent

**Execution:** Python  
**LLM Required:** No

### Purpose
Build and verify generated code.

### Implementation

```python
# compilation_agent.py
import subprocess
import os
import json
from typing import Dict, List, Tuple

class CompilationAgent:
    """
    Pure Python agent - No LLM required
    Executes dotnet CLI commands for building and testing
    """
    
    def __init__(self):
        self.dotnet_path = "dotnet"
    
    def build(self, solution_path: str) -> Dict:
        """Build the solution"""
        result = subprocess.run(
            [self.dotnet_path, "build", solution_path, "--no-restore"],
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": self._parse_errors(result.stderr + result.stdout)
        }
    
    def restore(self, solution_path: str) -> Dict:
        """Restore NuGet packages"""
        result = subprocess.run(
            [self.dotnet_path, "restore", solution_path],
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr
        }
    
    def run_tests(self, solution_path: str) -> Dict:
        """Run unit tests"""
        result = subprocess.run(
            [self.dotnet_path, "test", solution_path, "--no-build", "--verbosity", "normal"],
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "test_results": self._parse_test_results(result.stdout)
        }
    
    def _parse_errors(self, output: str) -> List[Dict]:
        """Parse build errors from output"""
        errors = []
        for line in output.split('\n'):
            if ': error ' in line or ': warning ' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    errors.append({
                        "file": parts[0].strip(),
                        "location": parts[1].strip() if len(parts) > 1 else "",
                        "type": "error" if ": error " in line else "warning",
                        "message": ':'.join(parts[2:]).strip()
                    })
        return errors
    
    def _parse_test_results(self, output: str) -> Dict:
        """Parse test results from output"""
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        
        for line in output.split('\n'):
            if "Passed:" in line:
                try:
                    results["passed"] = int(line.split("Passed:")[1].split()[0])
                except:
                    pass
            if "Failed:" in line:
                try:
                    results["failed"] = int(line.split("Failed:")[1].split()[0])
                except:
                    pass
            if "Total:" in line:
                try:
                    results["total"] = int(line.split("Total:")[1].split()[0])
                except:
                    pass
        
        return results
```

---

## 12. Test Generation Agent

**Execution:** LLM  
**LLM Required:** Yes

### Purpose
Generate unit and integration tests.

### Factory Droid Configuration

```yaml
# .factory/droids/test-generator.yaml
name: test-generator
description: Generates unit and integration tests for migrated code
model: inherit
system_prompt: |
  You are a .NET testing specialist. You generate comprehensive tests 
  using xUnit and Moq.
  
  Rules:
  1. Use xUnit for test framework
  2. Use Moq for mocking
  3. Use FluentAssertions for assertions
  4. Follow Arrange-Act-Assert pattern
  5. Test happy path and edge cases
  6. Include async test methods
  
  For each service method, generate tests for:
  - Valid input returns expected output
  - Invalid input throws appropriate exception
  - Edge cases (null, empty, boundary values)
  
  Output complete test class.
```

---

## 13. Review Agent

**Execution:** Python  
**LLM Required:** No

### Purpose
Validate completeness and generate migration report.

### Implementation

```python
# review_agent.py
import os
import json
from typing import Dict, List
from datetime import datetime

class ReviewAgent:
    """
    Pure Python agent - No LLM required
    Validates migration completeness and generates reports
    """
    
    def validate_completeness(self, parsed_data: Dict, 
                              generated_files: List[str]) -> Dict:
        """Validate all components were migrated"""
        validation = {
            "entities": {"expected": 0, "generated": 0, "missing": []},
            "services": {"expected": 0, "generated": 0, "missing": []},
            "screens": {"expected": 0, "generated": 0, "missing": []},
            "integrations": {"expected": 0, "generated": 0, "missing": []}
        }
        
        # Count expected
        for module in parsed_data.values():
            if hasattr(module, '__dict__'):
                module = module.__dict__
            validation["entities"]["expected"] += len(module.get("entities", []))
            validation["services"]["expected"] += len(module.get("server_actions", []))
            validation["screens"]["expected"] += len(module.get("screens", []))
            validation["integrations"]["expected"] += len(module.get("rest_consumes", []))
        
        # Count generated (by file pattern)
        for file in generated_files:
            if "/Entities/" in file and file.endswith(".cs"):
                validation["entities"]["generated"] += 1
            elif "/Services/" in file and file.endswith(".cs"):
                validation["services"]["generated"] += 1
            elif file.endswith(".razor"):
                validation["screens"]["generated"] += 1
            elif "/Integration/" in file and file.endswith(".cs"):
                validation["integrations"]["generated"] += 1
        
        return validation
    
    def generate_report(self, state: Dict, validation: Dict, 
                        build_result: Dict, test_result: Dict) -> str:
        """Generate migration report"""
        report = []
        report.append("# Migration Report")
        report.append(f"\nGenerated: {datetime.utcnow().isoformat()}")
        report.append(f"\nMigration ID: {state.get('migration_id', 'N/A')}")
        
        report.append("\n## Summary")
        report.append(f"- Status: {state.get('status', 'Unknown')}")
        report.append(f"- Modules: {len(state.get('modules', []))}")
        
        report.append("\n## Completeness")
        for component, data in validation.items():
            expected = data["expected"]
            generated = data["generated"]
            pct = (generated / expected * 100) if expected > 0 else 100
            report.append(f"- {component.title()}: {generated}/{expected} ({pct:.1f}%)")
        
        report.append("\n## Build Status")
        report.append(f"- Success: {build_result.get('success', False)}")
        if build_result.get('errors'):
            report.append(f"- Errors: {len(build_result['errors'])}")
        
        report.append("\n## Test Results")
        if test_result:
            tr = test_result.get('test_results', {})
            report.append(f"- Total: {tr.get('total', 0)}")
            report.append(f"- Passed: {tr.get('passed', 0)}")
            report.append(f"- Failed: {tr.get('failed', 0)}")
        
        report.append("\n## Recommendations")
        if validation["entities"]["generated"] < validation["entities"]["expected"]:
            report.append("- Review missing entity migrations")
        if build_result.get('errors'):
            report.append("- Fix build errors before deployment")
        if test_result and test_result.get('test_results', {}).get('failed', 0) > 0:
            report.append("- Fix failing tests")
        
        return "\n".join(report)
```

---

## Summary: Agent Execution Matrix

| Agent | Execution | Python Code | LLM Prompts | Factory Droid |
|-------|-----------|-------------|-------------|---------------|
| Orchestrator | Python | ✅ Full | ❌ None | Optional |
| Parser | Python | ✅ Full | ❌ None | Not needed |
| Analyzer | Python | ✅ Full | ❌ None | Not needed |
| Entity Generator | LLM | ❌ None | ✅ Full | Required |
| Business Logic | LLM | ❌ None | ✅ Full | Required |
| UI Generator | LLM | ❌ None | ✅ Full | Required |
| Integration | LLM | ❌ None | ✅ Full | Required |
| Security | Hybrid | ✅ Templates | ⚠️ Complex | Optional |
| Background Jobs | LLM | ❌ None | ✅ Full | Required |
| Configuration | Python | ✅ Full | ❌ None | Not needed |
| Compilation | Python | ✅ Full | ❌ None | Not needed |
| Test Generator | LLM | ❌ None | ✅ Full | Required |
| Review | Python | ✅ Full | ❌ None | Not needed |

**Totals:**
- Python-only: 6 agents (46%)
- LLM-required: 5 agents (38%)
- Hybrid: 2 agents (15%)

---

## Implementation Recommendations

### Phase 1: Build Python Agents First
1. Parser Agent - Foundation for all extraction
2. Analyzer Agent - Determines workflow
3. Configuration Agent - Generates config files
4. Compilation Agent - Build verification
5. Review Agent - Validation and reporting

### Phase 2: Build LLM Agents
1. Entity Generator - Data layer foundation
2. Business Logic Generator - Core services
3. UI Generator - User interface
4. Integration Generator - External APIs
5. Test Generator - Quality assurance

### Phase 3: Orchestration
1. Implement Orchestrator with state management
2. Connect all agents
3. End-to-end testing

---

*Document Version: 2.0*  
*Created: 2026-07-24*
