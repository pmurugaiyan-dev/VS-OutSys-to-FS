# OutSystems Application Reverse Engineering Guide

## Objective
Extract all application details from OutSystems OML files through an iterative process to enable complete reconstruction in .NET.

---

## Reverse Engineering Steps by Iteration

### Iteration 1: Structure
| Step | Description |
|------|-------------|
| 1 | Export Application Package |
| 2 | Extract and Inventory OML Files |
| 3 | Parse Module Dependencies |

### Iteration 2: Data Model
| Step | Description |
|------|-------------|
| 4 | Extract Entities and Data Model |
| 5 | Extract Static Entities (Enums) |
| 6 | Extract Entity Relationships and Foreign Keys |
| 7 | Extract Indexes and Constraints |
| 8 | Extract Structures (DTOs) |

### Iteration 3: Business Logic
| Step | Description |
|------|-------------|
| 9 | Extract Server Actions |
| 10 | Extract Client Actions |
| 11 | Extract Aggregates and Queries |

### Iteration 4: User Interface
| Step | Description |
|------|-------------|
| 12 | Extract Screen Definitions |
| 13 | Extract Screen Widgets and Bindings |
| 14 | Extract Screen Actions and Events |
| 15 | Extract Web Blocks (Reusable Components) |

### Iteration 5: Integrations
| Step | Description |
|------|-------------|
| 16 | Extract REST API Consumes |
| 17 | Extract REST API Exposes |
| 18 | Extract SOAP Web Services |

### Iteration 6: Background & Security
| Step | Description |
|------|-------------|
| 19 | Extract Timers (Scheduled Jobs) |
| 20 | Extract BPT Processes (Workflows) |
| 21 | Extract Roles and Permissions |
| 22 | Extract Site Properties (Configuration) |

### Iteration 7: Finalization
| Step | Description |
|------|-------------|
| 23 | Extract Resources (Images, CSS, JS) |
| 24 | Extract Extensions (Custom C#/Java) |
| 25 | Map Cross-Module References |
| 26 | Document Business Rules and Logic |
| 27 | Validate Completeness |

---

## Detailed Steps

### Step 1: Export Application Package

**Action:**
- Export OAP from Service Studio or LifeTime
- Document application version and environment

**Output:**
- `ApplicationName.oap` file
- Export metadata (date, version, environment)

**Command:**
```
Service Studio → Application → Export → Save OAP
```

Or via API:
```bash
curl -X GET "https://{env}/lifetimeapi/rest/v2/applications/{key}/versions/{ver}/content" \
  -H "Authorization: Bearer {token}" -o app.oap
```

---

### Step 2: Extract and Inventory OML Files

**Action:**
- Extract OAP (it's a ZIP file)
- List all OML files
- Identify module types (Reactive, Traditional, Service, Library)

**Output:**
- List of modules with types
- Module hierarchy

**Script:**
```powershell
Rename-Item app.oap app.zip
Expand-Archive app.zip -DestinationPath ./extracted

# List all OML files
Get-ChildItem -Path ./extracted -Filter "*.oml" -Recurse | 
    Select-Object Name, FullName, Length
```

**Inventory Template:**
| Module Name | Type | OML File | Size | Description |
|-------------|------|----------|------|-------------|
| | | | | |

---

### Step 3: Parse Module Dependencies

**Action:**
- Identify producer/consumer relationships
- Map module dependencies
- Determine migration order (dependencies first)

**Extract From OML:**
```xml
<References>
  <Reference Name="ModuleName" ... />
</References>
<Dependencies>
  <Dependency Producer="OtherModule" ... />
</Dependencies>
```

**Script:**
```python
def extract_dependencies(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    dependencies = {
        "module": root.get("Name"),
        "references": [],
        "producers": [],
        "consumers": []
    }
    
    for ref in root.findall(".//Reference"):
        dependencies["references"].append({
            "name": ref.get("Name"),
            "type": ref.get("Type")
        })
    
    for dep in root.findall(".//Dependency"):
        dependencies["producers"].append(dep.get("Producer"))
    
    return dependencies
```

**Output:**
- Dependency graph
- Migration order (topological sort)

---

### Step 4: Extract Entities and Data Model

**Action:**
- Extract all entity definitions
- Document each attribute with data type
- Identify primary keys (Id attributes)
- Note auto-number fields

**Extract From OML:**
```xml
<Entity Name="Customer" IsPublic="true">
  <Attribute Name="Id" Type="Integer" IsAutoNumber="true" />
  <Attribute Name="Name" Type="Text" Length="100" IsMandatory="true" />
  <Attribute Name="Email" Type="Email" IsMandatory="true" />
  <Attribute Name="CreatedDate" Type="DateTime" />
  <Attribute Name="IsActive" Type="Boolean" DefaultValue="true" />
</Entity>
```

**Script:**
```python
def extract_entities(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    entities = []
    for entity in root.findall(".//Entity"):
        entity_data = {
            "name": entity.get("Name"),
            "is_public": entity.get("IsPublic") == "true",
            "description": entity.get("Description"),
            "attributes": []
        }
        
        for attr in entity.findall(".//Attribute"):
            entity_data["attributes"].append({
                "name": attr.get("Name"),
                "type": attr.get("Type"),
                "length": attr.get("Length"),
                "decimals": attr.get("Decimals"),
                "is_mandatory": attr.get("IsMandatory") == "true",
                "is_auto_number": attr.get("IsAutoNumber") == "true",
                "default_value": attr.get("DefaultValue"),
                "description": attr.get("Description")
            })
        
        entities.append(entity_data)
    
    return entities
```

**Output Template:**
| Entity | Attribute | Type | Length | Mandatory | Auto | Default |
|--------|-----------|------|--------|-----------|------|---------|
| | | | | | | |

---

### Step 5: Extract Static Entities (Enums)

**Action:**
- Extract static entity definitions
- Extract all records (enum values)
- Note the identifier attribute

**Extract From OML:**
```xml
<StaticEntity Name="OrderStatus">
  <Attribute Name="Id" Type="Integer" />
  <Attribute Name="Label" Type="Text" Length="50" />
  <Attribute Name="Order" Type="Integer" />
  <Record>
    <Attribute Name="Id" Value="1" />
    <Attribute Name="Label" Value="Pending" />
  </Record>
  <Record>
    <Attribute Name="Id" Value="2" />
    <Attribute Name="Label" Value="Approved" />
  </Record>
</StaticEntity>
```

**Script:**
```python
def extract_static_entities(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    static_entities = []
    for se in root.findall(".//StaticEntity"):
        se_data = {
            "name": se.get("Name"),
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
```

**Output:**
```json
{
  "name": "OrderStatus",
  "records": [
    {"Id": 1, "Label": "Pending"},
    {"Id": 2, "Label": "Approved"}
  ]
}
```

---

### Step 6: Extract Entity Relationships and Foreign Keys

**Action:**
- Identify reference attributes (foreign keys)
- Document relationship type (1:1, 1:N, N:M)
- Note delete rules (Protect, Delete, Ignore)

**Extract From OML:**
```xml
<Attribute Name="CustomerId" Type="Customer Identifier">
  <ReferenceAttribute Entity="Customer" DeleteRule="Protect" />
</Attribute>
```

**Script:**
```python
def extract_relationships(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
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
                    "delete_rule": ref.get("DeleteRule"),
                    "is_mandatory": attr.get("IsMandatory") == "true"
                })
    
    return relationships
```

**Output Template:**
| From Entity | Attribute | To Entity | Delete Rule | Mandatory |
|-------------|-----------|-----------|-------------|-----------|
| Order | CustomerId | Customer | Protect | Yes |

---

### Step 7: Extract Indexes and Constraints

**Action:**
- Extract all entity indexes
- Document index columns
- Note unique constraints

**Extract From OML:**
```xml
<Entity Name="Customer">
  <Index Name="IX_Customer_Email" IsUnique="true">
    <IndexAttribute Attribute="Email" />
  </Index>
  <Index Name="IX_Customer_Name_Created">
    <IndexAttribute Attribute="Name" />
    <IndexAttribute Attribute="CreatedDate" Order="Descending" />
  </Index>
</Entity>
```

**Script:**
```python
def extract_indexes(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
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
```

---

### Step 8: Extract Structures (DTOs)

**Action:**
- Extract structure definitions
- These map to DTOs in .NET
- Document all attributes

**Extract From OML:**
```xml
<Structure Name="CustomerDTO">
  <Attribute Name="Id" Type="Integer" />
  <Attribute Name="Name" Type="Text" />
  <Attribute Name="OrderCount" Type="Integer" />
</Structure>
```

**Script:**
```python
def extract_structures(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
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
```

---

### Step 9: Extract Server Actions

**Action:**
- Extract all server action definitions
- Document input/output parameters
- Extract logic flow nodes
- Identify database operations (Create, Update, Delete, Aggregate)

**Extract From OML:**
```xml
<Action Name="CreateOrder" IsPublic="true">
  <InputParameter Name="CustomerId" Type="Integer" IsMandatory="true" />
  <InputParameter Name="Items" Type="OrderItem List" />
  <OutputParameter Name="OrderId" Type="Integer" />
  
  <Flow>
    <Aggregate Name="GetCustomer">...</Aggregate>
    <If Condition="GetCustomer.Count = 0">...</If>
    <CreateRecord Entity="Order">...</CreateRecord>
    <ForEach>...</ForEach>
    <Assign Variable="OrderId" Value="Order.Id" />
  </Flow>
</Action>
```

**Script:**
```python
def extract_server_actions(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    actions = []
    for action in root.findall(".//Action"):
        if action.get("IsServerAction") == "true" or action.find(".//ServerAction") is not None:
            action_data = {
                "name": action.get("Name"),
                "is_public": action.get("IsPublic") == "true",
                "description": action.get("Description"),
                "inputs": [],
                "outputs": [],
                "variables": [],
                "flow_nodes": []
            }
            
            # Input parameters
            for param in action.findall(".//InputParameter"):
                action_data["inputs"].append({
                    "name": param.get("Name"),
                    "type": param.get("Type"),
                    "is_mandatory": param.get("IsMandatory") == "true",
                    "default": param.get("DefaultValue")
                })
            
            # Output parameters
            for param in action.findall(".//OutputParameter"):
                action_data["outputs"].append({
                    "name": param.get("Name"),
                    "type": param.get("Type")
                })
            
            # Local variables
            for var in action.findall(".//Variable"):
                action_data["variables"].append({
                    "name": var.get("Name"),
                    "type": var.get("Type")
                })
            
            # Flow nodes (simplified extraction)
            flow_node_types = [
                "Aggregate", "SQL", "CreateRecord", "UpdateRecord", 
                "DeleteRecord", "If", "Switch", "ForEach", "Assign",
                "RaiseException", "ExceptionHandler", "Execute"
            ]
            
            for node_type in flow_node_types:
                for node in action.findall(f".//{node_type}"):
                    action_data["flow_nodes"].append({
                        "type": node_type,
                        "name": node.get("Name"),
                        "details": dict(node.attrib)
                    })
            
            actions.append(action_data)
    
    return actions
```

**Output Template:**
| Action | Inputs | Outputs | Operations |
|--------|--------|---------|------------|
| CreateOrder | CustomerId, Items | OrderId | Aggregate, CreateRecord, ForEach |

---

### Step 10: Extract Client Actions

**Action:**
- Extract client-side actions (for Reactive apps)
- Document JavaScript-equivalent logic
- Identify screen interactions

**Extract From OML:**
```xml
<ClientAction Name="ValidateForm">
  <InputParameter Name="FormData" Type="CustomerForm" />
  <OutputParameter Name="IsValid" Type="Boolean" />
  <OutputParameter Name="ErrorMessage" Type="Text" />
  
  <Flow>
    <If Condition="FormData.Name = ''">
      <Assign Variable="IsValid" Value="false" />
      <Assign Variable="ErrorMessage" Value="Name is required" />
    </If>
  </Flow>
</ClientAction>
```

**Script:**
```python
def extract_client_actions(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    client_actions = []
    for action in root.findall(".//ClientAction"):
        action_data = {
            "name": action.get("Name"),
            "inputs": [],
            "outputs": [],
            "flow_nodes": []
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
        
        client_actions.append(action_data)
    
    return client_actions
```

---

### Step 11: Extract Aggregates and Queries

**Action:**
- Extract aggregate definitions (visual queries)
- Document source entities
- Extract joins, filters, sorts
- Extract calculated/computed attributes

**Extract From OML:**
```xml
<Aggregate Name="GetActiveCustomerOrders">
  <Source Entity="Customer" />
  <Join Entity="Order" Type="Inner" Condition="Customer.Id = Order.CustomerId" />
  <Filter Condition="Customer.IsActive = true" />
  <Filter Condition="Order.CreatedDate >= StartDate" />
  <Sort Attribute="Order.CreatedDate" Direction="Descending" />
  <MaxRecords>100</MaxRecords>
  <OutputAttribute Name="CustomerName" Expression="Customer.Name" />
  <OutputAttribute Name="OrderTotal" Expression="Order.TotalAmount" />
</Aggregate>
```

**Script:**
```python
def extract_aggregates(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    aggregates = []
    for agg in root.findall(".//Aggregate"):
        agg_data = {
            "name": agg.get("Name"),
            "sources": [],
            "joins": [],
            "filters": [],
            "sorts": [],
            "max_records": agg.get("MaxRecords"),
            "output_attributes": []
        }
        
        # Source entities
        for source in agg.findall(".//Source"):
            agg_data["sources"].append(source.get("Entity"))
        
        # Joins
        for join in agg.findall(".//Join"):
            agg_data["joins"].append({
                "entity": join.get("Entity"),
                "type": join.get("Type"),
                "condition": join.get("Condition")
            })
        
        # Filters
        for filter in agg.findall(".//Filter"):
            agg_data["filters"].append(filter.get("Condition"))
        
        # Sorts
        for sort in agg.findall(".//Sort"):
            agg_data["sorts"].append({
                "attribute": sort.get("Attribute"),
                "direction": sort.get("Direction")
            })
        
        # Output/Calculated attributes
        for output in agg.findall(".//OutputAttribute"):
            agg_data["output_attributes"].append({
                "name": output.get("Name"),
                "expression": output.get("Expression")
            })
        
        aggregates.append(agg_data)
    
    return aggregates
```

---

### Step 12: Extract Screen Definitions

**Action:**
- Extract all screen definitions
- Document screen type (Reactive, Traditional)
- Extract screen-level data (aggregates, variables)
- Note entry point screens

**Extract From OML:**
```xml
<Screen Name="CustomerList" Title="Customers" IsDefault="true">
  <InputParameter Name="SearchTerm" Type="Text" />
  <LocalVariable Name="Customers" Type="Customer List" />
  <DataAction Name="GetCustomers">
    <Aggregate>...</Aggregate>
  </DataAction>
</Screen>
```

**Script:**
```python
def extract_screens(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    screens = []
    for screen in root.findall(".//Screen") + root.findall(".//WebScreen"):
        screen_data = {
            "name": screen.get("Name"),
            "title": screen.get("Title"),
            "type": screen.tag,
            "is_default": screen.get("IsDefault") == "true",
            "inputs": [],
            "variables": [],
            "data_actions": [],
            "client_actions": []
        }
        
        # Input parameters
        for param in screen.findall(".//InputParameter"):
            screen_data["inputs"].append({
                "name": param.get("Name"),
                "type": param.get("Type"),
                "is_mandatory": param.get("IsMandatory") == "true"
            })
        
        # Local variables
        for var in screen.findall(".//LocalVariable"):
            screen_data["variables"].append({
                "name": var.get("Name"),
                "type": var.get("Type")
            })
        
        # Data actions
        for da in screen.findall(".//DataAction"):
            screen_data["data_actions"].append(da.get("Name"))
        
        screens.append(screen_data)
    
    return screens
```

---

### Step 13: Extract Screen Widgets and Bindings

**Action:**
- Extract UI widget hierarchy
- Document widget types (Input, Button, Table, List, etc.)
- Extract data bindings
- Extract style classes

**Extract From OML:**
```xml
<Screen Name="CustomerList">
  <Content>
    <Container Style="MainContainer">
      <Input Variable="SearchTerm" Label="Search" />
      <Button Action="Search" Label="Search" Style="btn-primary" />
      <Table Source="Customers">
        <Column Attribute="Name" Header="Customer Name" />
        <Column Attribute="Email" Header="Email" />
        <Column>
          <Button Action="Edit" Label="Edit" />
        </Column>
      </Table>
    </Container>
  </Content>
</Screen>
```

**Script:**
```python
def extract_widgets(oml_path, screen_name):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    widgets = []
    screen = root.find(f".//*[@Name='{screen_name}']")
    
    if screen is None:
        return widgets
    
    widget_types = [
        "Container", "Input", "TextArea", "Button", "Link",
        "Table", "List", "If", "Label", "Expression",
        "Dropdown", "Checkbox", "RadioButton", "DatePicker",
        "Upload", "Image", "Popup", "Tabs", "Tab"
    ]
    
    def extract_widget_tree(element, parent=None):
        widget_list = []
        
        for wtype in widget_types:
            for widget in element.findall(f".//{wtype}"):
                widget_data = {
                    "type": wtype,
                    "name": widget.get("Name"),
                    "parent": parent,
                    "properties": dict(widget.attrib),
                    "children": []
                }
                
                # Extract bindings
                if widget.get("Variable"):
                    widget_data["binding"] = widget.get("Variable")
                if widget.get("Source"):
                    widget_data["source"] = widget.get("Source")
                if widget.get("Action"):
                    widget_data["action"] = widget.get("Action")
                
                widget_list.append(widget_data)
        
        return widget_list
    
    return extract_widget_tree(screen)
```

---

### Step 14: Extract Screen Actions and Events

**Action:**
- Extract button click actions
- Extract on-change handlers
- Extract on-initialize logic
- Map events to actions

**Extract From OML:**
```xml
<Screen Name="CustomerEdit">
  <OnInitialize>
    <Action Name="LoadCustomer" />
  </OnInitialize>
  
  <Button Name="SaveButton" Action="SaveCustomer" />
  
  <Input Variable="Customer.Name" OnChange="ValidateName" />
  
  <ScreenAction Name="SaveCustomer">
    <Flow>
      <ServerAction Name="UpdateCustomer" />
      <Navigate Screen="CustomerList" />
    </Flow>
  </ScreenAction>
</Screen>
```

**Script:**
```python
def extract_screen_events(oml_path, screen_name):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    screen = root.find(f".//*[@Name='{screen_name}']")
    if screen is None:
        return {}
    
    events = {
        "on_initialize": [],
        "on_destroy": [],
        "button_actions": [],
        "input_events": [],
        "screen_actions": []
    }
    
    # On Initialize
    for init in screen.findall(".//OnInitialize"):
        for action in init.findall(".//Action"):
            events["on_initialize"].append(action.get("Name"))
    
    # Button actions
    for btn in screen.findall(".//Button"):
        if btn.get("Action"):
            events["button_actions"].append({
                "button": btn.get("Name"),
                "action": btn.get("Action")
            })
    
    # Input events
    for inp in screen.findall(".//Input"):
        if inp.get("OnChange"):
            events["input_events"].append({
                "input": inp.get("Name"),
                "event": "OnChange",
                "action": inp.get("OnChange")
            })
    
    # Screen actions (local actions)
    for sa in screen.findall(".//ScreenAction"):
        events["screen_actions"].append({
            "name": sa.get("Name"),
            "flow": [node.tag for node in sa.findall(".//*")]
        })
    
    return events
```

---

### Step 15: Extract Web Blocks (Reusable Components)

**Action:**
- Extract web block definitions
- Document inputs/outputs
- Extract internal widgets
- Note placeholders

**Extract From OML:**
```xml
<WebBlock Name="CustomerCard">
  <InputParameter Name="Customer" Type="Customer" />
  <OutputParameter Name="OnEdit" Type="Action" />
  
  <Placeholder Name="Actions" />
  
  <Content>
    <Container Style="card">
      <Label Value="Customer.Name" />
      <Placeholder Name="Actions" />
    </Container>
  </Content>
</WebBlock>
```

**Script:**
```python
def extract_web_blocks(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    blocks = []
    for block in root.findall(".//WebBlock") + root.findall(".//Block"):
        block_data = {
            "name": block.get("Name"),
            "inputs": [],
            "outputs": [],
            "placeholders": [],
            "widgets": []
        }
        
        for param in block.findall(".//InputParameter"):
            block_data["inputs"].append({
                "name": param.get("Name"),
                "type": param.get("Type")
            })
        
        for param in block.findall(".//OutputParameter"):
            block_data["outputs"].append({
                "name": param.get("Name"),
                "type": param.get("Type")
            })
        
        for ph in block.findall(".//Placeholder"):
            block_data["placeholders"].append(ph.get("Name"))
        
        blocks.append(block_data)
    
    return blocks
```

---

### Step 16: Extract REST API Consumes

**Action:**
- Extract external REST API definitions
- Document base URLs
- Extract all methods with request/response formats
- Note authentication methods

**Extract From OML:**
```xml
<RESTConsume Name="PaymentGateway" BaseURL="https://api.payment.com/v1">
  <Authentication Type="Basic" Username="..." Password="..." />
  
  <Method Name="CreatePayment" HTTPMethod="POST" URLPath="/payments">
    <RequestFormat Type="JSON" />
    <Input Name="Amount" Type="Decimal" />
    <Input Name="Currency" Type="Text" />
    <Output Name="PaymentId" Type="Text" />
    <Output Name="Status" Type="Text" />
  </Method>
  
  <Method Name="GetPayment" HTTPMethod="GET" URLPath="/payments/{PaymentId}">
    <Input Name="PaymentId" Type="Text" SendIn="URL" />
    <Output Name="Status" Type="Text" />
  </Method>
</RESTConsume>
```

**Script:**
```python
def extract_rest_consumes(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    rest_apis = []
    for rest in root.findall(".//RESTConsume"):
        api_data = {
            "name": rest.get("Name"),
            "base_url": rest.get("BaseURL"),
            "authentication": None,
            "methods": []
        }
        
        # Authentication
        auth = rest.find(".//Authentication")
        if auth is not None:
            api_data["authentication"] = {
                "type": auth.get("Type"),
                "details": dict(auth.attrib)
            }
        
        # Methods
        for method in rest.findall(".//Method"):
            method_data = {
                "name": method.get("Name"),
                "http_method": method.get("HTTPMethod"),
                "url_path": method.get("URLPath"),
                "request_format": method.get("RequestFormat"),
                "response_format": method.get("ResponseFormat"),
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
```

---

### Step 17: Extract REST API Exposes

**Action:**
- Extract exposed REST APIs
- Document endpoints and methods
- Extract request/response structures
- Note authentication requirements

**Extract From OML:**
```xml
<RESTExpose Name="CustomerAPI" BasePath="/api/customers">
  <Method Name="GetCustomers" HTTPMethod="GET" URLPath="/">
    <Output Name="Customers" Type="Customer List" />
  </Method>
  
  <Method Name="CreateCustomer" HTTPMethod="POST" URLPath="/">
    <Input Name="Customer" Type="CustomerDTO" />
    <Output Name="CustomerId" Type="Integer" />
  </Method>
</RESTExpose>
```

**Script:**
```python
def extract_rest_exposes(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
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
                    "source": inp.get("Source")  # URL, Header, Body
                })
            
            for out in method.findall(".//Output"):
                method_data["outputs"].append({
                    "name": out.get("Name"),
                    "type": out.get("Type")
                })
            
            api_data["methods"].append(method_data)
        
        exposed_apis.append(api_data)
    
    return exposed_apis
```

---

### Step 18: Extract SOAP Web Services

**Action:**
- Extract SOAP service definitions (if any)
- Document WSDL references
- Extract methods and parameters

**Script:**
```python
def extract_soap_services(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    soap_services = []
    for soap in root.findall(".//SOAPConsume") + root.findall(".//WebService"):
        service_data = {
            "name": soap.get("Name"),
            "wsdl_url": soap.get("WSDL"),
            "methods": []
        }
        
        for method in soap.findall(".//Method"):
            service_data["methods"].append({
                "name": method.get("Name"),
                "inputs": [p.get("Name") for p in method.findall(".//Input")],
                "outputs": [p.get("Name") for p in method.findall(".//Output")]
            })
        
        soap_services.append(service_data)
    
    return soap_services
```

---

### Step 19: Extract Timers (Scheduled Jobs)

**Action:**
- Extract timer definitions
- Document schedules (cron expressions)
- Identify the action to execute
- Note timeout settings

**Extract From OML:**
```xml
<Timer Name="DailyOrderCleanup" Schedule="0 2 * * *" Timeout="600">
  <Action Name="CleanupOldOrders" />
</Timer>

<Timer Name="ProcessPendingPayments" Schedule="*/15 * * * *" Timeout="300">
  <Action Name="ProcessPayments" />
</Timer>
```

**Script:**
```python
def extract_timers(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    timers = []
    for timer in root.findall(".//Timer"):
        timers.append({
            "name": timer.get("Name"),
            "schedule": timer.get("Schedule"),
            "timeout": timer.get("Timeout"),
            "action": timer.find(".//Action").get("Name") if timer.find(".//Action") else None,
            "is_active": timer.get("IsActive", "true") == "true"
        })
    
    return timers
```

---

### Step 20: Extract BPT Processes (Workflows)

**Action:**
- Extract business process definitions
- Document process flow
- Identify human activities, automatic activities
- Extract wait conditions and decisions

**Extract From OML:**
```xml
<Process Name="OrderApproval">
  <ProcessInput Name="OrderId" Type="Integer" />
  
  <Start />
  
  <AutomaticActivity Name="ValidateOrder">
    <Action Name="ValidateOrderData" />
  </AutomaticActivity>
  
  <Decision Name="NeedsApproval">
    <Condition>Order.Amount > 1000</Condition>
  </Decision>
  
  <HumanActivity Name="ManagerApproval" Role="Manager">
    <Timeout>48h</Timeout>
  </HumanActivity>
  
  <Wait Name="PaymentReceived">
    <Condition>Order.PaymentStatus = 'Paid'</Condition>
  </Wait>
  
  <End />
</Process>
```

**Script:**
```python
def extract_processes(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
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
        
        # Extract activities in order
        activity_types = [
            "Start", "End", "AutomaticActivity", "HumanActivity",
            "Decision", "Wait", "ConditionalStart"
        ]
        
        for act_type in activity_types:
            for act in proc.findall(f".//{act_type}"):
                activity = {
                    "type": act_type,
                    "name": act.get("Name"),
                    "properties": dict(act.attrib)
                }
                
                if act_type == "HumanActivity":
                    activity["role"] = act.get("Role")
                    timeout = act.find(".//Timeout")
                    if timeout is not None:
                        activity["timeout"] = timeout.text
                
                if act_type == "Decision":
                    cond = act.find(".//Condition")
                    if cond is not None:
                        activity["condition"] = cond.text
                
                proc_data["activities"].append(activity)
        
        processes.append(proc_data)
    
    return processes
```

---

### Step 21: Extract Roles and Permissions

**Action:**
- Extract role definitions
- Document screen/action access rules
- Identify role hierarchy

**Extract From OML:**
```xml
<Role Name="Administrator" />
<Role Name="Manager" />
<Role Name="User" />

<Screen Name="AdminDashboard">
  <Access Role="Administrator" />
</Screen>

<Action Name="DeleteCustomer">
  <Access Role="Administrator" />
</Action>
```

**Script:**
```python
def extract_roles_and_permissions(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    roles = []
    for role in root.findall(".//Role"):
        roles.append({
            "name": role.get("Name"),
            "is_persistent": role.get("IsPersistent") == "true"
        })
    
    permissions = []
    
    # Screen access
    for screen in root.findall(".//Screen") + root.findall(".//WebScreen"):
        for access in screen.findall(".//Access"):
            permissions.append({
                "resource_type": "Screen",
                "resource": screen.get("Name"),
                "role": access.get("Role")
            })
    
    # Action access
    for action in root.findall(".//Action"):
        for access in action.findall(".//Access"):
            permissions.append({
                "resource_type": "Action",
                "resource": action.get("Name"),
                "role": access.get("Role")
            })
    
    return {"roles": roles, "permissions": permissions}
```

---

### Step 22: Extract Site Properties (Configuration)

**Action:**
- Extract site property definitions
- Document default values
- Identify environment-specific settings

**Extract From OML:**
```xml
<SiteProperty Name="MaxUploadSize" Type="Integer" DefaultValue="10485760" />
<SiteProperty Name="SMTPServer" Type="Text" DefaultValue="smtp.company.com" />
<SiteProperty Name="EnableDebugMode" Type="Boolean" DefaultValue="false" />
```

**Script:**
```python
def extract_site_properties(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    properties = []
    for prop in root.findall(".//SiteProperty"):
        properties.append({
            "name": prop.get("Name"),
            "type": prop.get("Type"),
            "default_value": prop.get("DefaultValue"),
            "is_public": prop.get("IsPublic") == "true"
        })
    
    return properties
```

---

### Step 23: Extract Resources (Images, CSS, JS)

**Action:**
- List all embedded resources
- Extract image references
- Document CSS classes used
- List JavaScript inclusions

**Script:**
```python
def extract_resources(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    resources = {
        "images": [],
        "stylesheets": [],
        "scripts": [],
        "themes": []
    }
    
    for img in root.findall(".//Image") + root.findall(".//Resource[@Type='Image']"):
        resources["images"].append({
            "name": img.get("Name"),
            "filename": img.get("Filename")
        })
    
    for css in root.findall(".//Stylesheet") + root.findall(".//CSS"):
        resources["stylesheets"].append({
            "name": css.get("Name"),
            "content": css.text if css.text else None
        })
    
    for js in root.findall(".//JavaScript") + root.findall(".//Script"):
        resources["scripts"].append({
            "name": js.get("Name"),
            "content": js.text if js.text else None
        })
    
    return resources
```

---

### Step 24: Extract Extensions (Custom C#/Java)

**Action:**
- Identify extension references
- Document extension actions used
- Flag for manual migration (if custom code)

**Extract From OML:**
```xml
<Extension Name="CryptoExtension">
  <Action Name="EncryptText" />
  <Action Name="DecryptText" />
</Extension>
```

**Script:**
```python
def extract_extensions(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
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
```

---

### Step 25: Map Cross-Module References

**Action:**
- Identify public elements used across modules
- Document producer-consumer relationships
- Create reference map for migration order

**Script:**
```python
def map_cross_references(oml_files):
    all_modules = {}
    references = []
    
    for oml_path in oml_files:
        tree = ET.parse(oml_path)
        root = tree.getroot()
        module_name = root.get("Name")
        
        all_modules[module_name] = {
            "public_entities": [],
            "public_actions": [],
            "public_structures": []
        }
        
        # Find public elements
        for entity in root.findall(".//Entity[@IsPublic='true']"):
            all_modules[module_name]["public_entities"].append(entity.get("Name"))
        
        for action in root.findall(".//Action[@IsPublic='true']"):
            all_modules[module_name]["public_actions"].append(action.get("Name"))
        
        # Find references to other modules
        for ref in root.findall(".//Reference"):
            references.append({
                "consumer": module_name,
                "producer": ref.get("Name"),
                "element": ref.get("Element")
            })
    
    return {"modules": all_modules, "references": references}
```

---

### Step 26: Document Business Rules and Logic

**Action:**
- Review extracted actions and identify business rules
- Document validation logic
- Document calculation formulas
- Create business rules catalog

**Output Template:**
| Rule ID | Name | Location | Description | Conditions | Actions |
|---------|------|----------|-------------|------------|---------|
| BR001 | Order Approval Required | CreateOrder | Orders over $1000 need approval | Amount > 1000 | Set NeedsApproval = true |

---

### Step 27: Validate Completeness

**Action:**
- Compare extracted counts with OutSystems reports
- Verify all elements are captured
- Document any gaps or unsupported features

**Checklist:**
```
[ ] Entity count matches
[ ] Screen count matches
[ ] Server action count matches
[ ] Client action count matches
[ ] Integration count matches
[ ] Timer count matches
[ ] Role count matches
[ ] All foreign keys documented
[ ] All indexes documented
[ ] Business rules cataloged
```

---

## Master Extraction Script

```python
# master_extractor.py
import xml.etree.ElementTree as ET
import json
import os
import sys

class OMLExtractor:
    def __init__(self, oml_path):
        self.oml_path = oml_path
        self.tree = ET.parse(oml_path)
        self.root = self.tree.getroot()
    
    def extract_all(self):
        return {
            "module_name": self.root.get("Name"),
            "entities": self.extract_entities(),
            "static_entities": self.extract_static_entities(),
            "relationships": self.extract_relationships(),
            "indexes": self.extract_indexes(),
            "structures": self.extract_structures(),
            "server_actions": self.extract_server_actions(),
            "client_actions": self.extract_client_actions(),
            "aggregates": self.extract_aggregates(),
            "screens": self.extract_screens(),
            "web_blocks": self.extract_web_blocks(),
            "rest_consumes": self.extract_rest_consumes(),
            "rest_exposes": self.extract_rest_exposes(),
            "timers": self.extract_timers(),
            "processes": self.extract_processes(),
            "roles": self.extract_roles(),
            "site_properties": self.extract_site_properties(),
            "resources": self.extract_resources(),
            "extensions": self.extract_extensions(),
            "dependencies": self.extract_dependencies()
        }
    
    # Include all extract methods from above...
    
    def save_to_json(self, output_path):
        data = self.extract_all()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        return data

if __name__ == "__main__":
    oml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "extracted_module.json"
    
    extractor = OMLExtractor(oml_file)
    data = extractor.save_to_json(output_file)
    
    # Print summary
    print(f"Module: {data['module_name']}")
    print(f"Entities: {len(data['entities'])}")
    print(f"Screens: {len(data['screens'])}")
    print(f"Server Actions: {len(data['server_actions'])}")
    print(f"REST APIs: {len(data['rest_consumes']) + len(data['rest_exposes'])}")
    print(f"Timers: {len(data['timers'])}")
    print(f"\nOutput saved to: {output_file}")
```

---

## Iterative Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION 1: Structure                        │
│  Steps 1-3: Export, Extract, Parse Dependencies                  │
│  Output: Module inventory, dependency graph                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION 2: Data Model                       │
│  Steps 4-8: Entities, Static Entities, Relationships, Indexes   │
│  Output: Complete data model documentation                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION 3: Business Logic                   │
│  Steps 9-11: Server Actions, Client Actions, Aggregates         │
│  Output: Service layer specification                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION 4: User Interface                   │
│  Steps 12-15: Screens, Widgets, Events, Web Blocks              │
│  Output: UI component specification                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION 5: Integrations                     │
│  Steps 16-18: REST Consumes, REST Exposes, SOAP                 │
│  Output: Integration specification                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION 6: Background & Security            │
│  Steps 19-22: Timers, Processes, Roles, Site Properties         │
│  Output: Infrastructure specification                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ITERATION 7: Finalization                     │
│  Steps 23-27: Resources, Extensions, Cross-refs, Validation     │
│  Output: Complete migration specification                        │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document Version: 1.0*  
*Created: 2026-07-23*
