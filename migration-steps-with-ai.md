# OutSystems to .NET Migration: Practical Steps with AI

## Actual Technical Steps to Migrate Using AI Tools

This document outlines the real, hands-on steps to migrate an OutSystems application to .NET using AI assistance.

---

## Prerequisites

- OutSystems application exported as OAP/OML files
- Access to AI tools (ChatGPT/Claude/Copilot or custom AI)
- .NET 8 SDK installed
- Visual Studio / VS Code
- Database access (source OutSystems DB)

---

## Migration Steps Overview

### Step 1: Extract OutSystems Application
- 1.1 Export from OutSystems (Service Studio or LifeTime API)
- 1.2 Extract OML Files from OAP
- 1.3 Parse OML to JSON (for AI processing)

### Step 2: Generate .NET Project Structure with AI
- 2.1 AI Prompt for Project Scaffolding
- 2.2 Execute Generated Commands

### Step 3: Generate Entity Classes with AI
- 3.1 Extract Entity Details from OML
- 3.2 AI Prompt for Entity Generation
- 3.3 AI Output Example
- 3.4 Save and Verify Generated Entities

### Step 4: Generate DbContext and Repositories with AI
- 4.1 AI Prompt for DbContext
- 4.2 AI Prompt for Repository Pattern

### Step 5: Migrate Server Actions to Services with AI
- 5.1 Extract Server Action Logic from OML
- 5.2 AI Prompt for Service Method Generation
- 5.3 AI Output Example

### Step 6: Migrate Aggregates/Queries with AI
- 6.1 Extract Aggregate from OML
- 6.2 AI Prompt for LINQ Query Generation
- 6.3 AI Output Example

### Step 7: Migrate Screens/UI with AI
- 7.1 Extract Screen Structure from OML
- 7.2 AI Prompt for Blazor Component Generation
- 7.3 AI Output Example

### Step 8: Migrate Integrations with AI
- 8.1 Extract REST Integration Details
- 8.2 AI Prompt for HttpClient Service Generation

### Step 9: Migrate Database Data
- 9.1 Generate Data Migration Script with AI
- 9.2 Use EF Core Migrations

### Step 10: Generate API Controllers with AI
- 10.1 AI Prompt for Controller Generation

### Step 11: Test Generated Code
- 11.1 AI Prompt for Unit Tests
- 11.2 Run Tests

### Step 12: Validate Migration
- 12.1 Functional Comparison Checklist
- 12.2 Data Validation Queries

---

## Detailed Steps

---

## Step 1: Extract OutSystems Application

### 1.1 Export from OutSystems

```
Service Studio → Application → Export → Download OAP file
```

Or via LifeTime API:
```bash
curl -X GET "https://{environment}/lifetimeapi/rest/v2/applications/{AppKey}/versions/{VersionKey}/content" \
  -H "Authorization: Bearer {token}" \
  -o application.oap
```

### 1.2 Extract OML Files

```powershell
# OAP is a ZIP file
Rename-Item application.oap application.zip
Expand-Archive application.zip -DestinationPath ./extracted

# Find all OML files
Get-ChildItem -Path ./extracted -Filter "*.oml" -Recurse
```

### 1.3 Parse OML to JSON (for AI processing)

```python
# oml_parser.py
import xml.etree.ElementTree as ET
import json
import sys

def parse_oml(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    result = {
        "module_name": root.get("Name"),
        "entities": [],
        "screens": [],
        "server_actions": [],
        "client_actions": [],
        "integrations": [],
        "site_properties": []
    }
    
    # Extract entities
    for entity in root.findall(".//Entity"):
        entity_data = {
            "name": entity.get("Name"),
            "attributes": []
        }
        for attr in entity.findall(".//Attribute"):
            entity_data["attributes"].append({
                "name": attr.get("Name"),
                "type": attr.get("Type"),
                "is_mandatory": attr.get("IsMandatory", "false"),
                "length": attr.get("Length")
            })
        result["entities"].append(entity_data)
    
    # Extract screens
    for screen in root.findall(".//WebScreen") + root.findall(".//Screen"):
        result["screens"].append({
            "name": screen.get("Name"),
            "type": screen.tag
        })
    
    # Extract server actions
    for action in root.findall(".//Action[@IsServerAction='true']") + root.findall(".//ServerAction"):
        result["server_actions"].append({
            "name": action.get("Name"),
            "parameters": [p.get("Name") for p in action.findall(".//Parameter")]
        })
    
    # Extract REST integrations
    for rest in root.findall(".//RESTConsume") + root.findall(".//RESTExpose"):
        result["integrations"].append({
            "name": rest.get("Name"),
            "type": rest.tag,
            "url": rest.get("URL")
        })
    
    return result

if __name__ == "__main__":
    oml_file = sys.argv[1]
    parsed = parse_oml(oml_file)
    print(json.dumps(parsed, indent=2))
```

Run:
```powershell
python oml_parser.py ./extracted/Module.oml > module_structure.json
```

---

## Step 2: Generate .NET Project Structure with AI

### 2.1 AI Prompt for Project Scaffolding

```
I'm migrating an OutSystems application to .NET 8. Here's the application structure:

[Paste module_structure.json content]

Generate the .NET solution structure using Clean Architecture with:
1. Domain layer (entities)
2. Application layer (services, DTOs)
3. Infrastructure layer (EF Core, repositories)
4. API layer (ASP.NET Core Web API)
5. Web layer (Blazor or React)

Provide the dotnet CLI commands to create this structure.
```

### 2.2 Execute Generated Commands

```powershell
# Create solution
dotnet new sln -n MyApp

# Create projects
dotnet new classlib -n MyApp.Domain -o src/MyApp.Domain
dotnet new classlib -n MyApp.Application -o src/MyApp.Application
dotnet new classlib -n MyApp.Infrastructure -o src/MyApp.Infrastructure
dotnet new webapi -n MyApp.API -o src/MyApp.API
dotnet new blazorserver -n MyApp.Web -o src/MyApp.Web

# Add to solution
dotnet sln add src/MyApp.Domain
dotnet sln add src/MyApp.Application
dotnet sln add src/MyApp.Infrastructure
dotnet sln add src/MyApp.API
dotnet sln add src/MyApp.Web

# Add project references
dotnet add src/MyApp.Application reference src/MyApp.Domain
dotnet add src/MyApp.Infrastructure reference src/MyApp.Application
dotnet add src/MyApp.API reference src/MyApp.Infrastructure
dotnet add src/MyApp.Web reference src/MyApp.Application
```

---

## Step 3: Generate Entity Classes with AI

### 3.1 Extract Entity Details from OML

```python
# extract_entities.py
import xml.etree.ElementTree as ET
import json

def extract_entities_detail(oml_path):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    entities = []
    for entity in root.findall(".//Entity"):
        entity_data = {
            "name": entity.get("Name"),
            "description": entity.get("Description", ""),
            "attributes": [],
            "indexes": [],
            "foreign_keys": []
        }
        
        for attr in entity.findall(".//Attribute"):
            attr_data = {
                "name": attr.get("Name"),
                "type": attr.get("Type"),
                "is_mandatory": attr.get("IsMandatory") == "true",
                "is_auto_number": attr.get("IsAutoNumber") == "true",
                "length": attr.get("Length"),
                "decimals": attr.get("Decimals"),
                "default_value": attr.get("DefaultValue")
            }
            
            # Check for foreign key
            ref = attr.find(".//ReferenceAttribute")
            if ref is not None:
                attr_data["foreign_key"] = {
                    "entity": ref.get("Entity"),
                    "delete_rule": ref.get("DeleteRule")
                }
                entity_data["foreign_keys"].append(attr_data)
            
            entity_data["attributes"].append(attr_data)
        
        # Extract indexes
        for idx in entity.findall(".//Index"):
            entity_data["indexes"].append({
                "name": idx.get("Name"),
                "is_unique": idx.get("IsUnique") == "true",
                "attributes": [a.get("Attribute") for a in idx.findall(".//IndexAttribute")]
            })
        
        entities.append(entity_data)
    
    return entities

entities = extract_entities_detail("./extracted/Module.oml")
print(json.dumps(entities, indent=2))
```

### 3.2 AI Prompt for Entity Generation

```
Convert these OutSystems entities to C# EF Core entity classes:

[Paste entities JSON]

Requirements:
1. Use data annotations for validation
2. Include proper navigation properties for foreign keys
3. Add [Table] attribute with original table name
4. Map OutSystems types to C# types:
   - Integer → int
   - Long Integer → long
   - Decimal → decimal
   - Text → string with [MaxLength]
   - Date → DateOnly
   - Date Time → DateTime
   - Boolean → bool
   - Binary Data → byte[]
5. Include XML documentation comments
```

### 3.3 AI Output Example

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
    /// <summary>
    /// Unique identifier for the customer.
    /// </summary>
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    /// <summary>
    /// Customer's full name.
    /// </summary>
    [Required]
    [MaxLength(100)]
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Customer's email address.
    /// </summary>
    [Required]
    [MaxLength(255)]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;

    /// <summary>
    /// Date when the customer was created.
    /// </summary>
    public DateTime CreatedDate { get; set; }

    /// <summary>
    /// Whether the customer account is active.
    /// </summary>
    public bool IsActive { get; set; }

    // Navigation properties
    public virtual ICollection<Order> Orders { get; set; } = new List<Order>();
}
```

### 3.4 Save and Verify Generated Entities

```powershell
# Save AI output to file
# Then verify it compiles
dotnet build src/MyApp.Domain
```

---

## Step 4: Generate DbContext and Repositories with AI

### 4.1 AI Prompt for DbContext

```
Generate an EF Core DbContext for these entities:

[List entity names]

Include:
1. DbSet for each entity
2. OnModelCreating with Fluent API configurations
3. Index configurations
4. Relationship configurations
5. Soft delete query filter (if IsDeleted property exists)
```

### 4.2 AI Prompt for Repository Pattern

```
Generate a generic repository interface and implementation for EF Core:

Requirements:
1. IRepository<T> interface with CRUD operations
2. Async methods
3. Include/ThenInclude support for eager loading
4. Specification pattern for complex queries
5. Unit of Work pattern
```

---

## Step 5: Migrate Server Actions to Services with AI

### 5.1 Extract Server Action Logic from OML

```python
# extract_actions.py
import xml.etree.ElementTree as ET
import json

def extract_action_flow(oml_path, action_name):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    for action in root.findall(f".//Action[@Name='{action_name}']"):
        flow = {
            "name": action.get("Name"),
            "description": action.get("Description"),
            "inputs": [],
            "outputs": [],
            "variables": [],
            "flow_nodes": []
        }
        
        # Input parameters
        for param in action.findall(".//InputParameter"):
            flow["inputs"].append({
                "name": param.get("Name"),
                "type": param.get("Type"),
                "is_mandatory": param.get("IsMandatory")
            })
        
        # Output parameters
        for param in action.findall(".//OutputParameter"):
            flow["outputs"].append({
                "name": param.get("Name"),
                "type": param.get("Type")
            })
        
        # Local variables
        for var in action.findall(".//Variable"):
            flow["variables"].append({
                "name": var.get("Name"),
                "type": var.get("Type")
            })
        
        # Flow nodes (simplified)
        for node in action.findall(".//*[@NodeType]"):
            flow["flow_nodes"].append({
                "type": node.tag,
                "name": node.get("Name"),
                "properties": dict(node.attrib)
            })
        
        return flow
    
    return None

# Example usage
flow = extract_action_flow("./extracted/Module.oml", "CreateOrder")
print(json.dumps(flow, indent=2))
```

### 5.2 AI Prompt for Service Method Generation

```
Convert this OutSystems Server Action to a C# service method:

Action Name: CreateOrder
Inputs:
- CustomerId (Integer, mandatory)
- Items (List of OrderItem)

Flow:
1. Aggregate: Get Customer by CustomerId
2. If: Customer not found → Raise Exception "Customer not found"
3. Create Record: Order with CustomerId, CreatedDate = Now()
4. For Each: Items
   4.1 Create Record: OrderItem with OrderId, ProductId, Quantity
5. Aggregate: Calculate order total
6. Update Record: Order.TotalAmount = calculated total
7. Output: Created Order

Generate:
1. Service interface method
2. Service implementation
3. Request/Response DTOs
4. Include logging
5. Include validation
6. Use repository pattern
```

### 5.3 AI Output Example

```csharp
// IOrderService.cs
public interface IOrderService
{
    Task<CreateOrderResponse> CreateOrderAsync(CreateOrderRequest request, CancellationToken cancellationToken = default);
}

// CreateOrderRequest.cs
public record CreateOrderRequest(
    int CustomerId,
    List<OrderItemRequest> Items
);

public record OrderItemRequest(
    int ProductId,
    int Quantity,
    decimal UnitPrice
);

// CreateOrderResponse.cs
public record CreateOrderResponse(
    int OrderId,
    decimal TotalAmount,
    DateTime CreatedDate
);

// OrderService.cs
public class OrderService : IOrderService
{
    private readonly IRepository<Customer> _customerRepository;
    private readonly IRepository<Order> _orderRepository;
    private readonly IUnitOfWork _unitOfWork;
    private readonly ILogger<OrderService> _logger;

    public OrderService(
        IRepository<Customer> customerRepository,
        IRepository<Order> orderRepository,
        IUnitOfWork unitOfWork,
        ILogger<OrderService> logger)
    {
        _customerRepository = customerRepository;
        _orderRepository = orderRepository;
        _unitOfWork = unitOfWork;
        _logger = logger;
    }

    public async Task<CreateOrderResponse> CreateOrderAsync(
        CreateOrderRequest request, 
        CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Creating order for customer {CustomerId}", request.CustomerId);

        // Step 1: Get Customer
        var customer = await _customerRepository.GetByIdAsync(request.CustomerId, cancellationToken);
        
        // Step 2: Validate customer exists
        if (customer is null)
        {
            _logger.LogWarning("Customer {CustomerId} not found", request.CustomerId);
            throw new NotFoundException($"Customer {request.CustomerId} not found");
        }

        // Step 3: Create Order
        var order = new Order
        {
            CustomerId = request.CustomerId,
            CreatedDate = DateTime.UtcNow,
            Status = OrderStatus.Pending
        };

        // Step 4: Add Order Items
        foreach (var item in request.Items)
        {
            order.Items.Add(new OrderItem
            {
                ProductId = item.ProductId,
                Quantity = item.Quantity,
                UnitPrice = item.UnitPrice
            });
        }

        // Step 5 & 6: Calculate and set total
        order.TotalAmount = order.Items.Sum(i => i.Quantity * i.UnitPrice);

        await _orderRepository.AddAsync(order, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        _logger.LogInformation("Order {OrderId} created successfully", order.Id);

        // Step 7: Return response
        return new CreateOrderResponse(
            order.Id,
            order.TotalAmount,
            order.CreatedDate
        );
    }
}
```

---

## Step 6: Migrate Aggregates/Queries with AI

### 6.1 Extract Aggregate from OML

```python
# extract_aggregates.py
def extract_aggregate(oml_path, aggregate_name):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    for agg in root.findall(f".//Aggregate[@Name='{aggregate_name}']"):
        aggregate = {
            "name": agg.get("Name"),
            "source": None,
            "joins": [],
            "filters": [],
            "sorts": [],
            "max_records": agg.get("MaxRecords"),
            "output_attributes": []
        }
        
        # Source entity
        source = agg.find(".//Source")
        if source:
            aggregate["source"] = source.get("Entity")
        
        # Joins
        for join in agg.findall(".//Join"):
            aggregate["joins"].append({
                "entity": join.get("Entity"),
                "type": join.get("JoinType"),
                "condition": join.get("Condition")
            })
        
        # Filters
        for filter in agg.findall(".//Filter"):
            aggregate["filters"].append(filter.get("Condition"))
        
        # Sort
        for sort in agg.findall(".//Sort"):
            aggregate["sorts"].append({
                "attribute": sort.get("Attribute"),
                "direction": sort.get("Direction")
            })
        
        return aggregate
```

### 6.2 AI Prompt for LINQ Query Generation

```
Convert this OutSystems Aggregate to EF Core LINQ:

Aggregate: GetActiveCustomerOrders
Source: Customer
Joins:
- Order (Inner Join on Customer.Id = Order.CustomerId)
- OrderItem (Left Join on Order.Id = OrderItem.OrderId)
Filters:
- Customer.IsActive = true
- Order.CreatedDate >= StartDate (input parameter)
Sorts:
- Order.CreatedDate DESC
Max Records: 100
Output:
- Customer.Name
- Order.Id
- Order.TotalAmount
- Count of OrderItems

Generate:
1. LINQ query using EF Core
2. DTO for the result
3. Repository method
```

### 6.3 AI Output Example

```csharp
// DTO
public record CustomerOrderSummaryDto(
    string CustomerName,
    int OrderId,
    decimal TotalAmount,
    int ItemCount
);

// Repository method
public async Task<List<CustomerOrderSummaryDto>> GetActiveCustomerOrdersAsync(
    DateTime startDate,
    CancellationToken cancellationToken = default)
{
    return await _context.Customers
        .Where(c => c.IsActive)
        .Join(
            _context.Orders.Where(o => o.CreatedDate >= startDate),
            customer => customer.Id,
            order => order.CustomerId,
            (customer, order) => new { customer, order }
        )
        .GroupJoin(
            _context.OrderItems,
            co => co.order.Id,
            item => item.OrderId,
            (co, items) => new CustomerOrderSummaryDto(
                co.customer.Name,
                co.order.Id,
                co.order.TotalAmount,
                items.Count()
            )
        )
        .OrderByDescending(x => x.OrderId)
        .Take(100)
        .ToListAsync(cancellationToken);
}
```

---

## Step 7: Migrate Screens/UI with AI

### 7.1 Extract Screen Structure from OML

```python
# extract_screens.py
def extract_screen(oml_path, screen_name):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    for screen in root.findall(f".//*[@Name='{screen_name}']"):
        if screen.tag in ['WebScreen', 'Screen']:
            screen_data = {
                "name": screen.get("Name"),
                "title": screen.get("Title"),
                "widgets": [],
                "data_actions": [],
                "client_actions": []
            }
            
            # Extract widgets
            for widget in screen.findall(".//*"):
                if widget.tag in ['Input', 'Button', 'Table', 'List', 'Container', 'If', 'Link', 'Label']:
                    screen_data["widgets"].append({
                        "type": widget.tag,
                        "name": widget.get("Name"),
                        "properties": dict(widget.attrib)
                    })
            
            return screen_data
    return None
```

### 7.2 AI Prompt for Blazor Component Generation

```
Convert this OutSystems Screen to a Blazor component:

Screen: CustomerList
Data: 
- Aggregate: GetCustomers (returns list of Customer entities)
- Filter input: SearchTerm (text)

Widgets:
1. Input (SearchTerm binding)
2. Button (triggers filter)
3. Table:
   - Column: Name
   - Column: Email
   - Column: Status (conditional: Active/Inactive badge)
   - Column: Actions (Edit, Delete buttons)
4. Pagination

Generate:
1. Blazor component (.razor file)
2. Code-behind if needed
3. Use Bootstrap 5 for styling
4. Include loading state
5. Include error handling
```

### 7.3 AI Output Example

```razor
@page "/customers"
@inject ICustomerService CustomerService
@inject NavigationManager Navigation

<PageTitle>Customers</PageTitle>

<div class="container mt-4">
    <h1>Customers</h1>
    
    <div class="row mb-3">
        <div class="col-md-4">
            <div class="input-group">
                <input type="text" class="form-control" placeholder="Search customers..."
                       @bind="searchTerm" @bind:event="oninput" />
                <button class="btn btn-primary" @onclick="SearchAsync">
                    <i class="bi bi-search"></i> Search
                </button>
            </div>
        </div>
    </div>

    @if (isLoading)
    {
        <div class="d-flex justify-content-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    }
    else if (errorMessage is not null)
    {
        <div class="alert alert-danger">@errorMessage</div>
    }
    else
    {
        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                @foreach (var customer in customers)
                {
                    <tr>
                        <td>@customer.Name</td>
                        <td>@customer.Email</td>
                        <td>
                            @if (customer.IsActive)
                            {
                                <span class="badge bg-success">Active</span>
                            }
                            else
                            {
                                <span class="badge bg-secondary">Inactive</span>
                            }
                        </td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" 
                                    @onclick="() => Edit(customer.Id)">
                                Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger" 
                                    @onclick="() => Delete(customer.Id)">
                                Delete
                            </button>
                        </td>
                    </tr>
                }
            </tbody>
        </table>
        
        <Pagination CurrentPage="currentPage" 
                    TotalPages="totalPages" 
                    OnPageChanged="LoadPageAsync" />
    }
</div>

@code {
    private List<CustomerDto> customers = new();
    private string searchTerm = "";
    private bool isLoading = true;
    private string? errorMessage;
    private int currentPage = 1;
    private int totalPages = 1;

    protected override async Task OnInitializedAsync()
    {
        await LoadCustomersAsync();
    }

    private async Task LoadCustomersAsync()
    {
        isLoading = true;
        errorMessage = null;
        
        try
        {
            var result = await CustomerService.GetCustomersAsync(searchTerm, currentPage);
            customers = result.Items;
            totalPages = result.TotalPages;
        }
        catch (Exception ex)
        {
            errorMessage = "Failed to load customers. Please try again.";
        }
        finally
        {
            isLoading = false;
        }
    }

    private async Task SearchAsync()
    {
        currentPage = 1;
        await LoadCustomersAsync();
    }

    private async Task LoadPageAsync(int page)
    {
        currentPage = page;
        await LoadCustomersAsync();
    }

    private void Edit(int id) => Navigation.NavigateTo($"/customers/{id}/edit");

    private async Task Delete(int id)
    {
        // Show confirmation, then delete
        await CustomerService.DeleteAsync(id);
        await LoadCustomersAsync();
    }
}
```

---

## Step 8: Migrate Integrations with AI

### 8.1 Extract REST Integration Details

```python
# extract_integrations.py
def extract_rest_consume(oml_path, integration_name):
    tree = ET.parse(oml_path)
    root = tree.getroot()
    
    for rest in root.findall(f".//RESTConsume[@Name='{integration_name}']"):
        integration = {
            "name": rest.get("Name"),
            "base_url": rest.get("BaseURL"),
            "methods": []
        }
        
        for method in rest.findall(".//Method"):
            integration["methods"].append({
                "name": method.get("Name"),
                "http_method": method.get("HTTPMethod"),
                "url_path": method.get("URLPath"),
                "request_format": method.get("RequestFormat"),
                "response_format": method.get("ResponseFormat"),
                "inputs": [{"name": p.get("Name"), "type": p.get("Type")} 
                          for p in method.findall(".//Input")],
                "outputs": [{"name": p.get("Name"), "type": p.get("Type")} 
                           for p in method.findall(".//Output")]
            })
        
        return integration
```

### 8.2 AI Prompt for HttpClient Service Generation

```
Convert this OutSystems REST Consume to a C# HttpClient service:

Integration: PaymentGateway
Base URL: https://api.payments.com/v1
Authentication: API Key in header (X-API-Key)

Methods:
1. CreatePayment
   - POST /payments
   - Input: amount (decimal), currency (string), orderId (int)
   - Output: paymentId (string), status (string)

2. GetPaymentStatus
   - GET /payments/{paymentId}
   - Input: paymentId (string)
   - Output: status (string), processedAt (datetime)

Generate:
1. Interface
2. Implementation using HttpClient
3. Request/Response DTOs
4. Polly retry policy
5. Error handling
```

---

## Step 9: Migrate Database Data

### 9.1 Generate Data Migration Script with AI

```
Generate a data migration script from OutSystems SQL Server to PostgreSQL:

Source tables (OutSystems):
- OSUSR_ABC_CUSTOMER
- OSUSR_ABC_ORDER
- OSUSR_ABC_ORDERITEM

Target tables (.NET):
- Customer
- Order  
- OrderItem

Mappings:
- OSUSR_ABC_CUSTOMER.ID → Customer.Id
- OSUSR_ABC_CUSTOMER.NAME → Customer.Name
- OSUSR_ABC_CUSTOMER.EMAIL → Customer.Email
- OSUSR_ABC_CUSTOMER.ISACTIVE → Customer.IsActive (1/0 → true/false)

Generate:
1. SQL script for data export from source
2. SQL script for data import to target
3. Data validation queries
```

### 9.2 Use EF Core Migrations

```powershell
# Generate migration
dotnet ef migrations add InitialCreate -p src/MyApp.Infrastructure -s src/MyApp.API

# Apply migration
dotnet ef database update -p src/MyApp.Infrastructure -s src/MyApp.API
```

---

## Step 10: Generate API Controllers with AI

### 10.1 AI Prompt for Controller Generation

```
Generate ASP.NET Core API controllers for these services:

Services:
1. ICustomerService
   - GetAllAsync(filter, page, pageSize)
   - GetByIdAsync(id)
   - CreateAsync(request)
   - UpdateAsync(id, request)
   - DeleteAsync(id)

2. IOrderService
   - GetCustomerOrdersAsync(customerId)
   - GetByIdAsync(id)
   - CreateOrderAsync(request)
   - UpdateStatusAsync(id, status)

Include:
1. Proper HTTP methods and routes
2. Response types
3. Swagger/OpenAPI attributes
4. Model validation
5. Error handling with ProblemDetails
```

---

## Step 11: Test Generated Code

### 11.1 AI Prompt for Unit Tests

```
Generate xUnit tests for OrderService.CreateOrderAsync:

Test cases:
1. Valid request → creates order successfully
2. Invalid CustomerId → throws NotFoundException
3. Empty items list → throws ValidationException
4. Calculates total correctly

Use:
- Moq for mocking
- FluentAssertions for assertions
```

### 11.2 Run Tests

```powershell
dotnet test --collect:"XPlat Code Coverage"
```

---

## Step 12: Validate Migration

### 12.1 Functional Comparison Checklist

```markdown
| OutSystems Feature | .NET Implementation | Test Status |
|-------------------|---------------------|-------------|
| Customer CRUD | CustomerService | [ ] Pass |
| Order Creation | OrderService | [ ] Pass |
| Order List Screen | CustomerOrders.razor | [ ] Pass |
| Payment Integration | PaymentGatewayService | [ ] Pass |
| Email Notifications | EmailService | [ ] Pass |
```

### 12.2 Data Validation Queries

```sql
-- Compare record counts
SELECT 'Customers' as entity, 
       (SELECT COUNT(*) FROM OSUSR_ABC_CUSTOMER) as source,
       (SELECT COUNT(*) FROM Customer) as target;

SELECT 'Orders' as entity,
       (SELECT COUNT(*) FROM OSUSR_ABC_ORDER) as source,
       (SELECT COUNT(*) FROM "Order") as target;

-- Compare totals
SELECT 'Order Total' as metric,
       (SELECT SUM(TOTALAMOUNT) FROM OSUSR_ABC_ORDER) as source,
       (SELECT SUM(TotalAmount) FROM "Order") as target;
```

---

## AI Tools Usage Summary

| Step | AI Task | Recommended Tool |
|------|---------|------------------|
| Entity Generation | Convert OML entities to C# | ChatGPT/Claude |
| Service Generation | Convert Server Actions to methods | ChatGPT/Claude |
| Query Conversion | Aggregates to LINQ | GitHub Copilot |
| UI Generation | Screens to Blazor/React | ChatGPT/Claude |
| Test Generation | Generate unit tests | GitHub Copilot |
| Code Completion | Fill in boilerplate | GitHub Copilot |
| Documentation | Generate XML docs | GitHub Copilot |

---

## Automation Script Example

```python
# migrate.py - Orchestrate migration with AI
import os
import json
from openai import OpenAI

client = OpenAI()

def migrate_entity(entity_json):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a .NET developer. Convert OutSystems entities to C# EF Core entities."},
            {"role": "user", "content": f"Convert this entity to C#:\n{json.dumps(entity_json)}"}
        ]
    )
    return response.choices[0].message.content

def migrate_action(action_json):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a .NET developer. Convert OutSystems Server Actions to C# service methods."},
            {"role": "user", "content": f"Convert this action to C#:\n{json.dumps(action_json)}"}
        ]
    )
    return response.choices[0].message.content

# Process all entities
with open('entities.json') as f:
    entities = json.load(f)

for entity in entities:
    code = migrate_entity(entity)
    with open(f"src/MyApp.Domain/Entities/{entity['name']}.cs", 'w') as f:
        f.write(code)
    print(f"Generated {entity['name']}.cs")
```

---

## Quick Reference: AI Prompts

### Entity Prompt Template
```
Convert this OutSystems entity to C# EF Core:
- Name: [EntityName]
- Attributes: [List attributes with types]
- Primary Key: [Identifier]
- Foreign Keys: [List FKs]
- Indexes: [List indexes]

Output: C# class with data annotations, navigation properties, XML documentation.
```

### Service Prompt Template
```
Convert this OutSystems Server Action to C# service:
- Name: [ActionName]
- Inputs: [List parameters]
- Outputs: [List outputs]
- Logic Flow: [Describe steps]

Output: Interface, implementation, DTOs, with logging and error handling.
```

### Screen Prompt Template
```
Convert this OutSystems Screen to Blazor:
- Name: [ScreenName]
- Data: [Aggregates/actions used]
- Widgets: [List widgets with bindings]
- Events: [List button clicks, etc.]

Output: Razor component with code-behind, Bootstrap styling.
```

---

*Document Version: 1.0*  
*Created: 2026-07-22*
