"""
Type Mapper Utility
Maps OutSystems types to C# types.
"""

from typing import Dict, Optional, Tuple


class TypeMapper:
    """Maps OutSystems data types to C# equivalents."""
    
    TYPE_MAP: Dict[str, Tuple[str, Optional[str]]] = {
        "Text": ("string", None),
        "Integer": ("int", None),
        "Long Integer": ("long", None),
        "Decimal": ("decimal", None),
        "Boolean": ("bool", None),
        "Date": ("DateTime", None),
        "Time": ("TimeSpan", None),
        "Date Time": ("DateTime", None),
        "Binary Data": ("byte[]", None),
        "Object": ("object", None),
        "Email": ("string", "[EmailAddress]"),
        "Phone Number": ("string", "[Phone]"),
        "Currency": ("decimal", "[Column(TypeName = \"decimal(18,2)\")]"),
    }
    
    ENTITY_ID_MAP: Dict[str, str] = {
        "User Identifier": "int",
        "Entity Identifier": "int",
    }
    
    @classmethod
    def to_csharp(cls, os_type: str, length: Optional[int] = None) -> Tuple[str, list]:
        """
        Convert OutSystems type to C# type.
        
        Returns:
            Tuple of (csharp_type, list_of_attributes)
        """
        attributes = []
        
        if os_type.endswith(" Identifier"):
            return ("int", attributes)
        
        if os_type in cls.TYPE_MAP:
            csharp_type, attr = cls.TYPE_MAP[os_type]
            if attr:
                attributes.append(attr)
            
            if csharp_type == "string" and length:
                attributes.append(f"[MaxLength({length})]")
            
            return (csharp_type, attributes)
        
        if os_type.startswith("Record"):
            return (os_type.replace("Record ", ""), attributes)
        
        if os_type.endswith(" List"):
            inner = os_type.replace(" List", "")
            inner_cs, _ = cls.to_csharp(inner)
            return (f"List<{inner_cs}>", attributes)
        
        return (os_type, attributes)
    
    @classmethod
    def to_sql_type(cls, os_type: str, length: Optional[int] = None, decimals: Optional[int] = None) -> str:
        """Convert OutSystems type to SQL Server type."""
        sql_map = {
            "Text": f"NVARCHAR({length or 'MAX'})",
            "Integer": "INT",
            "Long Integer": "BIGINT",
            "Decimal": f"DECIMAL(18, {decimals or 2})",
            "Boolean": "BIT",
            "Date": "DATE",
            "Time": "TIME",
            "Date Time": "DATETIME2",
            "Binary Data": "VARBINARY(MAX)",
            "Email": "NVARCHAR(255)",
            "Phone Number": "NVARCHAR(50)",
            "Currency": "DECIMAL(18, 2)",
        }
        
        if os_type.endswith(" Identifier"):
            return "INT"
        
        return sql_map.get(os_type, "NVARCHAR(MAX)")
    
    @classmethod
    def get_default_value(cls, csharp_type: str) -> str:
        """Get C# default value for type."""
        defaults = {
            "string": "string.Empty",
            "int": "0",
            "long": "0L",
            "decimal": "0m",
            "bool": "false",
            "DateTime": "DateTime.MinValue",
            "TimeSpan": "TimeSpan.Zero",
            "byte[]": "Array.Empty<byte>()",
            "object": "new object()",
        }
        
        if csharp_type.startswith("List<"):
            inner = csharp_type[5:-1]
            return f"new List<{inner}>()"
        
        return defaults.get(csharp_type, "default!")
    
    @classmethod
    def is_nullable(cls, os_type: str, is_mandatory: bool) -> bool:
        """Determine if the C# type should be nullable."""
        if is_mandatory:
            return False
        
        non_nullable = {"string", "byte[]", "object"}
        csharp_type, _ = cls.to_csharp(os_type)
        
        return csharp_type not in non_nullable


if __name__ == "__main__":
    mapper = TypeMapper()
    
    test_types = [
        ("Text", 100),
        ("Integer", None),
        ("Decimal", None),
        ("Boolean", None),
        ("Date Time", None),
        ("Email", None),
        ("User Identifier", None),
        ("Customer List", None),
    ]
    
    print("OutSystems to C# Type Mapping:")
    print("-" * 50)
    for os_type, length in test_types:
        cs_type, attrs = mapper.to_csharp(os_type, length)
        attrs_str = " ".join(attrs) if attrs else ""
        print(f"{os_type:20} -> {attrs_str} {cs_type}")
