"""
OML XML Parser - Parses full XML exported from OML files
Extracts entities, attributes, actions, screens, and other components.
"""

import xml.etree.ElementTree as ET
import json
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class EntityAttribute:
    """Entity attribute definition."""
    name: str
    type: str
    type_mapped: str = ""
    is_mandatory: bool = False
    is_auto_number: bool = False
    length: Optional[int] = None
    decimals: Optional[int] = None
    description: str = ""
    is_primary_key: bool = False
    foreign_key_entity: str = ""


@dataclass
class Entity:
    """Entity definition."""
    name: str
    pretty_name: str = ""
    pretty_name_plural: str = ""
    description: str = ""
    is_public: bool = False
    attributes: List[EntityAttribute] = field(default_factory=list)
    created_by: str = ""
    last_modified: str = ""


@dataclass
class Structure:
    """Structure (DTO) definition."""
    name: str
    is_public: bool = False
    attributes: List[Dict] = field(default_factory=list)


@dataclass
class UserAction:
    """User action (server/client action) definition."""
    name: str
    is_public: bool = False
    is_function: bool = False
    description: str = ""
    inputs: List[Dict] = field(default_factory=list)
    outputs: List[Dict] = field(default_factory=list)


@dataclass
class Screen:
    """Screen definition."""
    name: str
    title: str = ""
    is_default: bool = False
    inputs: List[Dict] = field(default_factory=list)


@dataclass 
class ParsedOML:
    """Complete parsed OML data."""
    module_name: str
    description: str = ""
    entities: List[Entity] = field(default_factory=list)
    structures: List[Structure] = field(default_factory=list)
    user_actions: List[UserAction] = field(default_factory=list)
    screens: List[Screen] = field(default_factory=list)
    site_properties: List[Dict] = field(default_factory=list)
    references: List[Dict] = field(default_factory=list)
    widgets_count: int = 0
    client_actions_count: int = 0


class OMLXMLParser:
    """Parser for OML XML files (converted from binary OML)."""
    
    # OutSystems type to C# type mapping
    TYPE_MAP = {
        "Text": "string",
        "Integer": "int",
        "LongInteger": "long",
        "Decimal": "decimal",
        "Boolean": "bool",
        "Date": "DateTime",
        "Time": "TimeSpan",
        "DateTime": "DateTime",
        "BinaryData": "byte[]",
        "Email": "string",
        "PhoneNumber": "string",
        "Currency": "decimal",
        "Object": "object",
    }
    
    def __init__(self):
        self.type_refs = {}  # Cache for type references
    
    def parse(self, xml_path: str) -> ParsedOML:
        """Parse OML XML file."""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Get module name from first entity or structure
        module_name = self._get_module_name(root)
        
        result = ParsedOML(module_name=module_name)
        
        # Parse entities
        result.entities = self._parse_entities(root)
        
        # Parse structures
        result.structures = self._parse_structures(root)
        
        # Parse user actions
        result.user_actions = self._parse_user_actions(root)
        
        # Parse site properties
        result.site_properties = self._parse_site_properties(root)
        
        # Parse references
        result.references = self._parse_references(root)
        
        # Count widgets and client actions
        result.widgets_count = len(root.findall(".//eSpaceFragment[@FragmentName]"))
        result.client_actions_count = len([f for f in root.findall(".//eSpaceFragment") 
                                           if f.get("FragmentName", "").startswith("ClientActionFlows")])
        
        return result
    
    def _get_module_name(self, root) -> str:
        """Extract module name."""
        # Try to get from EspaceConfigurations
        config = root.find(".//EspaceConfiguration")
        if config is not None:
            return config.get("Name", "Unknown")
        
        # Try from first entity
        entity = root.find(".//Entity")
        if entity is not None:
            return entity.get("Name", "Unknown").split(".")[0] if "." in entity.get("Name", "") else "Trade"
        
        return "Trade"
    
    def _parse_entities(self, root) -> List[Entity]:
        """Parse all entities."""
        entities = []
        
        for entity_elem in root.findall(".//Entity"):
            entity = Entity(
                name=entity_elem.get("Name", ""),
                pretty_name=entity_elem.get("PrettyName", ""),
                pretty_name_plural=entity_elem.get("PrettyNamePlural", ""),
                is_public=entity_elem.get("ExposeReadOnly") == "Yes",
                created_by=entity_elem.get("CreatedBy", ""),
                last_modified=entity_elem.get("LastModifiedDate", "")
            )
            
            # Parse attributes
            for attr_elem in entity_elem.findall(".//EntityAttribute"):
                attr = self._parse_entity_attribute(attr_elem)
                if attr:
                    entity.attributes.append(attr)
            
            if entity.name:
                entities.append(entity)
        
        return entities
    
    def _parse_entity_attribute(self, attr_elem) -> Optional[EntityAttribute]:
        """Parse entity attribute."""
        name = attr_elem.get("Name", "")
        if not name:
            return None
        
        raw_type = attr_elem.get("Type", "")
        mapped_type = self._map_type(raw_type)
        
        # Check for length
        length_elem = attr_elem.find("Length")
        length = None
        if length_elem is not None and length_elem.text:
            try:
                length = int(length_elem.text)
            except:
                pass
        
        # Check for decimals
        decimals_elem = attr_elem.find("Decimals")
        decimals = None
        if decimals_elem is not None and decimals_elem.text:
            try:
                decimals = int(decimals_elem.text)
            except:
                pass
        
        return EntityAttribute(
            name=name,
            type=raw_type,
            type_mapped=mapped_type,
            is_mandatory=attr_elem.get("IsMandatory") == "Yes",
            is_auto_number=attr_elem.get("IsAutoNumber") == "Yes",
            length=length,
            decimals=decimals,
            is_primary_key=name.lower() == "id"
        )
    
    def _map_type(self, os_type: str) -> str:
        """Map OutSystems type reference to C# type."""
        # Handle type references like %H6G+eTAigEi7LPUbg3Ey0g
        if os_type.startswith("%"):
            # These are internal type references
            # Common patterns:
            if "Integer" in os_type or os_type.endswith("0g"):
                return "int"
            elif "Text" in os_type or "String" in os_type:
                return "string"
            elif "Boolean" in os_type:
                return "bool"
            elif "DateTime" in os_type:
                return "DateTime"
            elif "Decimal" in os_type:
                return "decimal"
            else:
                return "string"  # Default to string
        
        # Handle direct type names
        for os_name, cs_name in self.TYPE_MAP.items():
            if os_name.lower() in os_type.lower():
                return cs_name
        
        # Handle entity references
        if "Entity:" in os_type or "Identifier" in os_type:
            return "int"
        
        return "string"
    
    def _parse_structures(self, root) -> List[Structure]:
        """Parse structures."""
        structures = []
        
        for struct_elem in root.findall(".//Structure"):
            struct = Structure(
                name=struct_elem.get("Name", ""),
                is_public=struct_elem.get("IsPublic") == "Yes"
            )
            
            for attr_elem in struct_elem.findall(".//StructureAttribute"):
                struct.attributes.append({
                    "name": attr_elem.get("Name", ""),
                    "type": attr_elem.get("Type", ""),
                })
            
            if struct.name:
                structures.append(struct)
        
        return structures
    
    def _parse_user_actions(self, root) -> List[UserAction]:
        """Parse user actions."""
        actions = []
        
        for action_elem in root.findall(".//UserAction"):
            action = UserAction(
                name=action_elem.get("Name", ""),
                is_public=action_elem.get("IsPublic") == "Yes",
                is_function=action_elem.get("IsFunction") == "Yes"
            )
            
            # Parse inputs
            for inp in action_elem.findall(".//InputParameter"):
                action.inputs.append({
                    "name": inp.get("Name", ""),
                    "type": inp.get("Type", ""),
                    "is_mandatory": inp.get("IsMandatory") == "Yes"
                })
            
            # Parse outputs
            for out in action_elem.findall(".//OutputParameter"):
                action.outputs.append({
                    "name": out.get("Name", ""),
                    "type": out.get("Type", "")
                })
            
            if action.name:
                actions.append(action)
        
        return actions
    
    def _parse_site_properties(self, root) -> List[Dict]:
        """Parse site properties."""
        properties = []
        
        for prop_elem in root.findall(".//SiteProperty"):
            properties.append({
                "name": prop_elem.get("Name", ""),
                "type": prop_elem.get("Type", ""),
                "default": prop_elem.get("DefaultValue", ""),
                "is_public": prop_elem.get("IsPublic") == "Yes"
            })
        
        return properties
    
    def _parse_references(self, root) -> List[Dict]:
        """Parse module references."""
        references = []
        
        for ref_elem in root.findall(".//Reference"):
            references.append({
                "name": ref_elem.get("Name", ""),
                "type": ref_elem.get("Type", ""),
                "uid": ref_elem.get("UniqueId", "")
            })
        
        return references
    
    def save_to_json(self, result: ParsedOML, output_path: str):
        """Save parsed result to JSON."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        data = asdict(result)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse OML XML file")
    parser.add_argument("xml_file", help="Path to OML XML file")
    parser.add_argument("-o", "--output", default="./parsed_oml.json", help="Output JSON file")
    args = parser.parse_args()
    
    xml_parser = OMLXMLParser()
    result = xml_parser.parse(args.xml_file)
    xml_parser.save_to_json(result, args.output)
    
    print(f"\nParsed OML XML:")
    print(f"  Module: {result.module_name}")
    print(f"  Entities: {len(result.entities)}")
    for entity in result.entities:
        print(f"    - {entity.name} ({len(entity.attributes)} attributes)")
        for attr in entity.attributes[:5]:
            print(f"        {attr.name}: {attr.type_mapped}")
        if len(entity.attributes) > 5:
            print(f"        ... and {len(entity.attributes) - 5} more")
    print(f"  Structures: {len(result.structures)}")
    print(f"  User Actions: {len(result.user_actions)}")
    print(f"  Site Properties: {len(result.site_properties)}")
    print(f"  References: {len(result.references)}")
    print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
