"""
Parser Agent - Pure Python Implementation
Execution: Python (No LLM Required)

Purpose: Extract and parse OML files into structured JSON.
This agent handles all 24 extraction steps from the reverse engineering guide.
"""

import xml.etree.ElementTree as ET
import json
import os
import zipfile
from typing import Dict, List, Optional
from dataclasses import asdict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.types import ParsedModule


class ParserAgent:
    """
    Pure Python agent - No LLM required.
    Parses OML (XML) files into structured JSON.
    """
    
    def __init__(self, work_dir: str = "./work"):
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)
    
    def extract_oap(self, oap_path: str) -> str:
        """Extract OAP file (ZIP) to work directory."""
        extract_dir = os.path.join(self.work_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(oap_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        return extract_dir
    
    def find_oml_files(self, directory: str) -> List[str]:
        """Find all OML files in directory."""
        oml_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.oml'):
                    oml_files.append(os.path.join(root, file))
        return oml_files
    
    def parse_oml(self, oml_path: str) -> ParsedModule:
        """Parse single OML file to structured data."""
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
        """Detect if module is Reactive, Traditional, Service, or Library."""
        if root.find(".//Screen") is not None:
            return "Reactive"
        elif root.find(".//WebScreen") is not None:
            return "Traditional"
        elif root.find(".//RESTExpose") is not None:
            return "Service"
        else:
            return "Library"
    
    def _extract_entities(self, root) -> List[Dict]:
        """Extract entity definitions."""
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
        """Extract static entity (enum) definitions."""
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
        """Extract foreign key relationships."""
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
        """Extract index definitions."""
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
        """Extract structure (DTO) definitions."""
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
        """Extract server action definitions."""
        actions = []
        for action in root.findall(".//Action"):
            if action.get("IsServerAction") == "true":
                action_data = self._extract_action_details(action)
                actions.append(action_data)
        
        for action in root.findall(".//ServerAction"):
            action_data = self._extract_action_details(action)
            actions.append(action_data)
        
        return actions
    
    def _extract_action_details(self, action) -> Dict:
        """Extract details from an action element."""
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
        
        flow_types = [
            "Aggregate", "SQL", "CreateRecord", "UpdateRecord",
            "DeleteRecord", "If", "Switch", "ForEach", "Assign",
            "RaiseException", "Execute", "RunServerAction"
        ]
        for ft in flow_types:
            for node in action.findall(f".//{ft}"):
                action_data["flow"].append({
                    "type": ft,
                    "name": node.get("Name"),
                    "properties": dict(node.attrib)
                })
        
        return action_data
    
    def _extract_client_actions(self, root) -> List[Dict]:
        """Extract client action definitions."""
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
        """Extract aggregate (query) definitions."""
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
        """Extract screen definitions."""
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
            
            widget_types = [
                "Container", "Input", "TextArea", "Button", "Link",
                "Table", "List", "If", "Label", "Expression",
                "Dropdown", "Checkbox", "RadioButton", "Image"
            ]
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
        """Extract web block definitions."""
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
        """Extract REST consume definitions."""
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
        """Extract REST expose definitions."""
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
        """Extract timer definitions."""
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
        """Extract BPT process definitions."""
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
            
            activity_types = [
                "Start", "End", "AutomaticActivity",
                "HumanActivity", "Decision", "Wait"
            ]
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
        """Extract role definitions."""
        roles = []
        for role in root.findall(".//Role"):
            roles.append({
                "name": role.get("Name"),
                "is_persistent": role.get("IsPersistent") == "true"
            })
        return roles
    
    def _extract_site_properties(self, root) -> List[Dict]:
        """Extract site property definitions."""
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
        """Extract resource definitions."""
        resources = []
        for res in root.findall(".//Resource"):
            resources.append({
                "name": res.get("Name"),
                "type": res.get("Type"),
                "filename": res.get("Filename")
            })
        return resources
    
    def _extract_extensions(self, root) -> List[Dict]:
        """Extract extension references."""
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
        """Extract module dependencies."""
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
        """Extract all modules from OAP file."""
        extract_dir = self.extract_oap(oap_path)
        oml_files = self.find_oml_files(extract_dir)
        
        modules = {}
        for oml_path in oml_files:
            parsed = self.parse_oml(oml_path)
            modules[parsed.module_name] = parsed
        
        return modules
    
    def save_to_json(self, modules: Dict[str, ParsedModule], output_dir: str):
        """Save parsed modules to JSON files."""
        os.makedirs(output_dir, exist_ok=True)
        
        for name, module in modules.items():
            output_path = os.path.join(output_dir, f"{name}.json")
            with open(output_path, 'w') as f:
                json.dump(asdict(module), f, indent=2)
        
        summary = {
            "total_modules": len(modules),
            "modules": list(modules.keys())
        }
        with open(os.path.join(output_dir, "_summary.json"), 'w') as f:
            json.dump(summary, f, indent=2)
        
        return output_dir


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse OutSystems OML files")
    parser.add_argument("input", help="OAP file or OML file path")
    parser.add_argument("-o", "--output", default="./output", help="Output directory")
    args = parser.parse_args()
    
    agent = ParserAgent()
    
    if args.input.endswith(".oap"):
        modules = agent.extract_all(args.input)
    else:
        module = agent.parse_oml(args.input)
        modules = {module.module_name: module}
    
    agent.save_to_json(modules, args.output)
    print(f"Parsed {len(modules)} module(s) to {args.output}")
