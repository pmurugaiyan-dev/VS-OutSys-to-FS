"""
Manifest Parser - Extracts metadata from OAP Manifest.xml
Since OML files are binary and require OutSystems DLLs to decode,
we extract what we can from the Manifest.xml file.
"""

import xml.etree.ElementTree as ET
import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass, field, asdict


@dataclass
class ManifestModule:
    """Parsed module info from Manifest."""
    uid: str
    name: str
    kind: str
    espace_type: str = ""
    entities: List[Dict] = field(default_factory=list)
    static_entities: List[Dict] = field(default_factory=list)
    web_blocks: List[Dict] = field(default_factory=list)
    web_flows: List[Dict] = field(default_factory=list)
    actions: List[Dict] = field(default_factory=list)
    screens: List[Dict] = field(default_factory=list)
    roles: List[Dict] = field(default_factory=list)
    images: List[Dict] = field(default_factory=list)
    themes: List[Dict] = field(default_factory=list)
    structures: List[Dict] = field(default_factory=list)
    dependencies: List[Dict] = field(default_factory=list)


@dataclass
class ManifestApplication:
    """Application info from Manifest."""
    uid: str
    name: str
    description: str
    primary_color: str
    application_kind: str
    modules: List[ManifestModule] = field(default_factory=list)


@dataclass
class ManifestInfo:
    """Complete Manifest information."""
    schema_version: str
    hub_server_version: str
    creation_date: str
    is_application_pack: bool
    applications: List[ManifestApplication] = field(default_factory=list)
    producer_modules: List[Dict] = field(default_factory=list)


class ManifestParser:
    """Parser for OAP Manifest.xml files."""
    
    def __init__(self):
        self.kind_to_category = {
            "Entity": "entities",
            "HiddenEntity": "entities",
            "StaticEntity": "static_entities",
            "WebBlock": "web_blocks",
            "WebFlow": "web_flows",
            "Action": "actions",
            "ServiceAction": "actions",
            "ClientAction": "actions",
            "Screen": "screens",
            "WebScreen": "screens",
            "Role": "roles",
            "Image": "images",
            "Theme": "themes",
            "Structure": "structures",
        }
    
    def parse(self, manifest_path: str) -> ManifestInfo:
        """Parse Manifest.xml file."""
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        
        info = ManifestInfo(
            schema_version=root.get("Schema", ""),
            hub_server_version=root.get("HubServerVersion", ""),
            creation_date=root.get("Creation", ""),
            is_application_pack=root.get("IsApplicationPack", "false").lower() == "true"
        )
        
        # Parse Solutions/Applications
        for solution in root.findall(".//Solution"):
            for app_elem in solution.findall(".//Application"):
                app = self._parse_application(app_elem)
                info.applications.append(app)
        
        # Parse referenced modules (these contain the actual entity/action definitions)
        for ref_module in root.findall(".//ReferencedModules/Module"):
            module = self._parse_referenced_module(ref_module)
            if module and (module.entities or module.actions or module.web_blocks or module.structures):
                # Add to first application's modules or create synthetic one
                if info.applications:
                    info.applications[0].modules.append(module)
        
        # Parse producer modules (dependencies)
        for producer in root.findall(".//ProducerModules/Module"):
            info.producer_modules.append({
                "uid": producer.get("UID", ""),
                "name": producer.get("Name", ""),
                "kind": producer.get("Kind", ""),
            })
        
        return info
    
    def _parse_referenced_module(self, module_elem) -> ManifestModule:
        """Parse referenced module element (contains actual API elements)."""
        module = ManifestModule(
            uid=module_elem.get("UID", ""),
            name=module_elem.get("Name", ""),
            kind=module_elem.get("Kind", ""),
            espace_type=module_elem.get("ESpaceType", "")
        )
        
        # Parse ReferencedAPI elements (this is where entities/actions are)
        for elem in module_elem.findall(".//ReferencedAPI/*"):
            kind = elem.get("Kind", "")
            item = {
                "uid": elem.get("UID", ""),
                "name": elem.get("Name", ""),
                "kind": kind,
                "producer_module": module.name,
            }
            
            category = self.kind_to_category.get(kind)
            if category and hasattr(module, category):
                getattr(module, category).append(item)
        
        return module
    
    def _parse_application(self, app_elem) -> ManifestApplication:
        """Parse application element."""
        app = ManifestApplication(
            uid=app_elem.get("UID", ""),
            name=app_elem.get("Name", ""),
            description=app_elem.get("Description", ""),
            primary_color=app_elem.get("PrimaryColor", ""),
            application_kind=app_elem.get("ApplicationKind", "")
        )
        
        # Parse modules within application
        for module_elem in app_elem.findall(".//Module"):
            module = self._parse_module(module_elem)
            app.modules.append(module)
        
        return app
    
    def _parse_module(self, module_elem) -> ManifestModule:
        """Parse module element."""
        module = ManifestModule(
            uid=module_elem.get("UID", ""),
            name=module_elem.get("Name", ""),
            kind=module_elem.get("Kind", ""),
            espace_type=module_elem.get("ESpaceType", "")
        )
        
        # Parse API public elements
        for elem in module_elem.findall(".//API/PublicElement"):
            kind = elem.get("Kind", "")
            item = {
                "uid": elem.get("UID", ""),
                "name": elem.get("Name", ""),
                "kind": kind,
            }
            
            category = self.kind_to_category.get(kind)
            if category and hasattr(module, category):
                getattr(module, category).append(item)
        
        # Parse dependencies
        for dep in module_elem.findall(".//Dependencies/Dependency"):
            module.dependencies.append({
                "producer_uid": dep.get("ProducerUID", ""),
                "producer_name": dep.get("ProducerName", ""),
            })
        
        return module
    
    def extract_all_entities(self, info: ManifestInfo) -> List[Dict]:
        """Extract all entities across all modules."""
        entities = []
        for app in info.applications:
            for module in app.modules:
                for entity in module.entities:
                    entity["module"] = module.name
                    entity["application"] = app.name
                    entities.append(entity)
        return entities
    
    def extract_all_web_blocks(self, info: ManifestInfo) -> List[Dict]:
        """Extract all web blocks across all modules."""
        blocks = []
        for app in info.applications:
            for module in app.modules:
                for block in module.web_blocks:
                    block["module"] = module.name
                    block["application"] = app.name
                    blocks.append(block)
        return blocks
    
    def save_to_json(self, info: ManifestInfo, output_path: str):
        """Save parsed manifest to JSON."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        # Convert to dict, handling dataclasses
        def to_dict(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return asdict(obj)
            return obj
        
        data = asdict(info)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def generate_summary(self, info: ManifestInfo) -> Dict[str, Any]:
        """Generate a summary of the manifest contents."""
        summary = {
            "server_version": info.hub_server_version,
            "creation_date": info.creation_date,
            "application_count": len(info.applications),
            "applications": [],
            "total_entities": 0,
            "total_web_blocks": 0,
            "total_actions": 0,
            "total_screens": 0,
            "producer_dependencies": len(info.producer_modules),
        }
        
        for app in info.applications:
            app_summary = {
                "name": app.name,
                "description": app.description,
                "kind": app.application_kind,
                "modules": []
            }
            
            for module in app.modules:
                mod_summary = {
                    "name": module.name,
                    "type": module.espace_type,
                    "entities": len(module.entities),
                    "static_entities": len(module.static_entities),
                    "web_blocks": len(module.web_blocks),
                    "actions": len(module.actions),
                    "screens": len(module.screens),
                    "roles": len(module.roles),
                }
                app_summary["modules"].append(mod_summary)
                
                summary["total_entities"] += len(module.entities) + len(module.static_entities)
                summary["total_web_blocks"] += len(module.web_blocks)
                summary["total_actions"] += len(module.actions)
                summary["total_screens"] += len(module.screens)
            
            summary["applications"].append(app_summary)
        
        return summary


def parse_manifest(manifest_path: str, output_dir: str) -> Dict:
    """
    Parse a Manifest.xml file and save results.
    
    Args:
        manifest_path: Path to Manifest.xml
        output_dir: Directory to save output files
        
    Returns:
        Summary dict
    """
    parser = ManifestParser()
    info = parser.parse(manifest_path)
    
    # Save full manifest data
    parser.save_to_json(info, os.path.join(output_dir, "manifest_parsed.json"))
    
    # Save summary
    summary = parser.generate_summary(info)
    with open(os.path.join(output_dir, "manifest_summary.json"), 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Save entities list
    entities = parser.extract_all_entities(info)
    with open(os.path.join(output_dir, "entities.json"), 'w') as f:
        json.dump(entities, f, indent=2)
    
    # Save web blocks list
    blocks = parser.extract_all_web_blocks(info)
    with open(os.path.join(output_dir, "web_blocks.json"), 'w') as f:
        json.dump(blocks, f, indent=2)
    
    return summary


if __name__ == "__main__":
    import argparse
    
    arg_parser = argparse.ArgumentParser(description="Parse OAP Manifest.xml")
    arg_parser.add_argument("manifest", help="Path to Manifest.xml")
    arg_parser.add_argument("-o", "--output", default="./parsed", help="Output directory")
    args = arg_parser.parse_args()
    
    summary = parse_manifest(args.manifest, args.output)
    
    print(f"\nManifest Summary:")
    print(f"  Server Version: {summary['server_version']}")
    print(f"  Created: {summary['creation_date']}")
    print(f"  Applications: {summary['application_count']}")
    print(f"  Total Entities: {summary['total_entities']}")
    print(f"  Total Web Blocks: {summary['total_web_blocks']}")
    print(f"  Total Actions: {summary['total_actions']}")
    print(f"  Total Screens: {summary['total_screens']}")
    print(f"  Producer Dependencies: {summary['producer_dependencies']}")
    
    for app in summary['applications']:
        print(f"\n  Application: {app['name']} ({app['kind']})")
        for mod in app['modules']:
            print(f"    Module: {mod['name']} ({mod['type']})")
            print(f"      Entities: {mod['entities']}, Blocks: {mod['web_blocks']}, Actions: {mod['actions']}")
