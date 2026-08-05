# OML Extraction Requirements

## Overview

This document outlines the requirements for fully extracting OutSystems application data from OAP/OML files to enable complete migration to .NET.

## Current Extraction Capability

### What Can Be Extracted (from Manifest.xml)

| Data Type | Source | Detail Level | Usable For Migration |
|-----------|--------|--------------|---------------------|
| Entity Names | Manifest.xml | Name, UID only | Skeleton generation |
| Static Entity Names | Manifest.xml | Name only | Enum skeleton |
| Web Block Names | Manifest.xml | Name only | Component list |
| Action Names | Manifest.xml | Name only | Service method stubs |
| Module Structure | Manifest.xml | Full | Project structure |
| Dependencies | Manifest.xml | Full | Reference mapping |
| Application Metadata | Manifest.xml | Full | Documentation |

### What Cannot Be Extracted (Binary OML)

| Data Type | Required For | Priority |
|-----------|--------------|----------|
| Entity Attributes (columns) | Database schema, EF Core entities | Critical |
| Attribute Data Types | C# type mapping | Critical |
| Foreign Key Relationships | Navigation properties, EF relationships | Critical |
| Indexes | Database performance | High |
| Action Flow Logic | Business logic implementation | Critical |
| Aggregate Definitions | LINQ queries, repository methods | Critical |
| Screen Layouts | Blazor pages/components | High |
| Widget Bindings | UI data binding | High |
| Validation Rules | FluentValidation rules | Medium |
| Site Properties | appsettings.json values | Medium |
| Timer Schedules | Hangfire job configuration | Medium |
| REST API Definitions | HTTP client generation | High |

## OML File Format

### Structure
- **Format**: Binary (not plain XML)
- **Header**: `OML` magic bytes followed by version info
- **Encoding**: Proprietary OutSystems encoding
- **Content**: Compressed/encoded XML fragments

### Sample Header (Trade.oml)
```
4F 4D 4C BF 80 00 00 31 31 2E 30 2E 34 31 35 2E
```
- `4F 4D 4C` = "OML"
- Version info follows

## Solutions for Complete Extraction

### Option 1: OML Utilities Tool (Recommended)

**Repository**: https://github.com/kelter-antunes/oml-utilities

**Requirements**:
- .NET Framework runtime
- OutSystems Service Studio DLLs (from installed Service Studio)

**Command**:
```bash
oml Manipulate "Trade.oml" "Trade.xml" O11 --format xml
```

**Output**: Full XML with all entities, attributes, actions, screens, etc.

### Option 2: OutSystems Service Studio Export

**Steps**:
1. Open module in Service Studio
2. File > Export > Module to XML
3. Results in complete XML representation

**Requirements**:
- OutSystems Service Studio installed
- Access to the OutSystems environment

### Option 3: OutSystems LifeTime API

**Endpoint**: `/lifetimeapi/rest/v2/applications/{AppKey}/versions/{VersionKey}/content`

**Requirements**:
- LifeTime API access
- Authentication token

### Option 4: Database Direct Access

If you have access to the OutSystems platform database:
- Entity definitions in `OSSYS_ENTITY`
- Attributes in `OSSYS_ENTITY_ATTR`
- Actions in `OSSYS_ESPACE_*` tables

**Note**: This requires platform database access and knowledge of internal schema.

## Expected XML Structure (When Decoded)

```xml
<Module Name="Trade" Type="Reactive">
  <Entities>
    <Entity Name="Customer" IsPublic="true">
      <Attribute Name="Id" Type="Integer" IsAutoNumber="true" IsPrimaryKey="true"/>
      <Attribute Name="Name" Type="Text" Length="100" IsMandatory="true"/>
      <Attribute Name="Email" Type="Email"/>
      <Attribute Name="Phone" Type="PhoneNumber"/>
      <Attribute Name="CreatedDate" Type="DateTime"/>
      <Attribute Name="AccountId" Type="Account Identifier">
        <ReferenceAttribute Entity="Account" DeleteRule="Protect"/>
      </Attribute>
    </Entity>
  </Entities>
  
  <Actions>
    <ServerAction Name="CreateCustomer">
      <InputParameter Name="CustomerData" Type="Customer"/>
      <OutputParameter Name="CustomerId" Type="Integer"/>
      <Flow>
        <CreateRecord Entity="Customer"/>
        <Assign Variable="CustomerId" Value="Customer.Id"/>
      </Flow>
    </ServerAction>
  </Actions>
  
  <Screens>
    <Screen Name="CustomerList" Title="Customers">
      <Aggregate Name="GetCustomers" Source="Customer"/>
      <Table Source="GetCustomers.List">
        <Column Header="Name" Value="Customer.Name"/>
        <Column Header="Email" Value="Customer.Email"/>
      </Table>
    </Screen>
  </Screens>
</Module>
```

## Impact Assessment

### With Current Extraction (Manifest Only)

| Migration Phase | Completeness | Effort to Complete |
|-----------------|--------------|-------------------|
| Project Setup | 100% | None |
| Entity Models | 10-15% | High (manual) |
| Database Schema | 0% | Very High |
| Business Logic | 0% | Very High |
| UI Components | 0% | Very High |
| **Overall** | **~15%** | **Very High** |

### With Full OML Extraction

| Migration Phase | Completeness | Effort to Complete |
|-----------------|--------------|-------------------|
| Project Setup | 100% | None |
| Entity Models | 90-95% | Low (review) |
| Database Schema | 85-90% | Low |
| Business Logic | 60-70% | Medium (LLM assist) |
| UI Components | 50-60% | Medium |
| **Overall** | **~75%** | **Medium** |

## Recommendations

1. **Obtain OML Utilities Tool** or install Service Studio to extract full XML
2. **Update Parser Agent** to handle full XML structure once available
3. **Use LLM Agents** to generate code from extracted XML
4. **Manual Review** required for complex business logic and UI

## Next Steps

1. [ ] Install OutSystems Service Studio (free trial available)
2. [ ] Download OML Utilities from GitHub
3. [ ] Extract Trade.oml to XML format
4. [ ] Re-run migration with full XML data
5. [ ] Generate complete entity definitions
6. [ ] Generate business logic from action flows

## References

- OML Utilities: https://github.com/kelter-antunes/oml-utilities
- OutSystems Forge: https://www.outsystems.com/forge/
- OutSystems Documentation: https://success.outsystems.com/documentation/
