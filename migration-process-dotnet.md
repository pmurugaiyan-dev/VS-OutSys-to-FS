# OutSystems to .NET Migration Process

## Comprehensive Step-by-Step Guide

---

## Table of Contents

1. [Phase 1: Discovery & Assessment](#phase-1-discovery--assessment)
2. [Phase 2: Architecture Design](#phase-2-architecture-design)
3. [Phase 3: Infrastructure Setup](#phase-3-infrastructure-setup)
4. [Phase 4: Data Layer Migration](#phase-4-data-layer-migration)
5. [Phase 5: Business Logic Migration](#phase-5-business-logic-migration)
6. [Phase 6: User Interface Migration](#phase-6-user-interface-migration)
7. [Phase 7: Integration Migration](#phase-7-integration-migration)
8. [Phase 8: Security Implementation](#phase-8-security-implementation)
9. [Phase 9: Cross-Cutting Concerns](#phase-9-cross-cutting-concerns)
10. [Phase 10: Testing & Validation](#phase-10-testing--validation)
11. [Phase 11: Deployment & Go-Live](#phase-11-deployment--go-live)
12. [Phase 12: Post-Migration Support](#phase-12-post-migration-support)

---

## Phase 1: Discovery & Assessment

### 1.1 Application Inventory

| Step | Action | Deliverable |
|------|--------|-------------|
| 1.1.1 | Export all OAP/OML files from OutSystems | Application pack files |
| 1.1.2 | Document all modules and dependencies | Module dependency diagram |
| 1.1.3 | List all applications in scope | Application inventory spreadsheet |
| 1.1.4 | Identify module types (Reactive, Traditional, Service) | Module classification list |

### 1.2 Technical Analysis

| Step | Action | Deliverable |
|------|--------|-------------|
| 1.2.1 | Parse OML files to extract metadata | Parsed JSON/XML data |
| 1.2.2 | Count entities, screens, actions per module | Complexity metrics |
| 1.2.3 | Identify external integrations (REST, SOAP, DB) | Integration inventory |
| 1.2.4 | List all extensions (C#, Java) | Extension catalog |
| 1.2.5 | Document Site Properties and configurations | Configuration inventory |
| 1.2.6 | Identify BPT processes and timers | Process workflow list |

### 1.3 Complexity Assessment

```
Complexity Score Calculation:
- Entities: count × 1 point
- Screens: count × 2 points
- Server Actions: count × 1.5 points
- Client Actions: count × 1 point
- Integrations: count × 3 points
- BPT Processes: count × 5 points
- Extensions: count × 4 points

Low: < 100 points
Medium: 100-500 points
High: 500-1000 points
Very High: > 1000 points
```

### 1.4 Current State Documentation

| Item | Details to Capture |
|------|-------------------|
| **User Base** | Number of users, roles, concurrent users |
| **Traffic Patterns** | Peak load, request/sec, data volume |
| **SLAs** | Response time, uptime, availability requirements |
| **Compliance** | GDPR, HIPAA, PCI-DSS, SOC2 requirements |
| **Data Sensitivity** | PII, PHI, financial data locations |

---

## Phase 2: Architecture Design

### 2.1 Target Architecture Selection

| Pattern | When to Use | .NET Implementation |
|---------|-------------|---------------------|
| **Monolith** | Small apps, tight coupling | Single ASP.NET Core Web API + Blazor |
| **Modular Monolith** | Medium apps, logical separation | ASP.NET Core with feature folders |
| **Microservices** | Large apps, independent scaling | Multiple ASP.NET Core services |
| **Hybrid** | Gradual migration, mixed workloads | Combination approach |

### 2.2 Technology Stack Definition

| Layer | Technology | Version |
|-------|------------|---------|
| **Runtime** | .NET | 8.0 LTS (or latest) |
| **Web Framework** | ASP.NET Core | 8.0 |
| **Frontend (Option A)** | Blazor Server/WebAssembly | 8.0 |
| **Frontend (Option B)** | React + TypeScript | 18.x |
| **ORM** | Entity Framework Core | 8.0 |
| **Database** | SQL Server / PostgreSQL | 2022 / 16 |
| **Caching** | Redis | 7.x |
| **Message Queue** | RabbitMQ / Azure Service Bus | 3.x / Latest |
| **Search** | Elasticsearch (if needed) | 8.x |

### 2.3 Project Structure Design

```
Solution/
├── src/
│   ├── Company.App.Domain/           # Entities, Value Objects, Domain Events
│   ├── Company.App.Application/      # Use Cases, DTOs, Interfaces
│   ├── Company.App.Infrastructure/   # EF Core, External Services, Repositories
│   ├── Company.App.API/              # ASP.NET Core Web API
│   ├── Company.App.Web/              # Blazor / React Frontend
│   └── Company.App.Shared/           # Shared utilities, constants
├── tests/
│   ├── Company.App.UnitTests/
│   ├── Company.App.IntegrationTests/
│   └── Company.App.E2ETests/
├── docs/
├── scripts/
└── docker/
```

### 2.4 API Design

| OutSystems Pattern | .NET API Pattern |
|-------------------|------------------|
| Screen Aggregates | GET endpoints with query params |
| Server Actions (read) | GET endpoints |
| Server Actions (write) | POST/PUT/DELETE endpoints |
| Service Actions | Dedicated API controllers |
| BPT Process triggers | Event-driven endpoints / Message handlers |

---

## Phase 3: Infrastructure Setup

### 3.1 Development Environment

| Step | Action | Tools |
|------|--------|-------|
| 3.1.1 | Set up source control | Git, Azure DevOps / GitHub |
| 3.1.2 | Create solution structure | dotnet CLI, Visual Studio |
| 3.1.3 | Configure CI/CD pipelines | GitHub Actions / Azure Pipelines |
| 3.1.4 | Set up development database | SQL Server Developer / Docker |
| 3.1.5 | Configure local secrets management | dotnet user-secrets |

### 3.2 Cloud Infrastructure (Azure Example)

| Component | Azure Service | Purpose |
|-----------|---------------|---------|
| **Compute** | App Service / AKS | Host application |
| **Database** | Azure SQL / PostgreSQL Flexible | Data storage |
| **Cache** | Azure Cache for Redis | Session, caching |
| **Storage** | Blob Storage | Files, documents |
| **Queue** | Service Bus | Async messaging |
| **Identity** | Azure AD B2C | Authentication |
| **Monitoring** | Application Insights | APM, logging |
| **Key Vault** | Azure Key Vault | Secrets management |

### 3.3 Environment Configuration

| Environment | Purpose | Configuration |
|-------------|---------|---------------|
| **Development** | Local development | appsettings.Development.json |
| **QA** | Testing | appsettings.QA.json |
| **Staging** | Pre-production | appsettings.Staging.json |
| **Production** | Live | appsettings.Production.json + Key Vault |

---

## Phase 4: Data Layer Migration

### 4.1 Entity Migration

| OutSystems | .NET (EF Core) | Notes |
|------------|----------------|-------|
| Entity | C# class with [Table] | One class per entity |
| Attribute | Property with [Column] | Match data types |
| Identifier | [Key] property | Auto-increment or GUID |
| Reference (FK) | Navigation property | Configure relationships |
| Index | [Index] or Fluent API | Replicate all indexes |
| Unique constraint | [Index(IsUnique=true)] | Add validation |
| Delete Rule | .OnDelete() | Cascade, Restrict, SetNull |

#### 4.1.1 Data Type Mapping

| OutSystems Type | C# Type | SQL Server Type |
|-----------------|---------|-----------------|
| Integer | int | int |
| Long Integer | long | bigint |
| Decimal | decimal | decimal(18,8) |
| Boolean | bool | bit |
| Text | string | nvarchar(max) |
| Text (length) | string with [MaxLength] | nvarchar(n) |
| Date | DateOnly | date |
| Time | TimeOnly | time |
| Date Time | DateTime | datetime2 |
| Binary Data | byte[] | varbinary(max) |
| Email | string | nvarchar(255) |
| Phone Number | string | nvarchar(50) |
| Currency | decimal | decimal(18,4) |

#### 4.1.2 Entity Example

**OutSystems Entity:**
```
Entity: Customer
- Id (Auto Number)
- Name (Text, 100)
- Email (Email)
- CreatedDate (Date Time)
- IsActive (Boolean)
- TotalOrders (Integer)
```

**.NET Entity:**
```csharp
[Table("Customer")]
public class Customer
{
    [Key]
    [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }
    
    [Required]
    [MaxLength(100)]
    public string Name { get; set; }
    
    [Required]
    [MaxLength(255)]
    [EmailAddress]
    public string Email { get; set; }
    
    public DateTime CreatedDate { get; set; }
    
    public bool IsActive { get; set; }
    
    public int TotalOrders { get; set; }
    
    // Navigation properties
    public virtual ICollection<Order> Orders { get; set; }
}
```

### 4.2 Static Entity Migration

| OutSystems | .NET Option 1 | .NET Option 2 |
|------------|---------------|---------------|
| Static Entity | Enum | Lookup Table |

**Example - Status Static Entity:**
```csharp
// Option 1: Enum
public enum OrderStatus
{
    [Description("Pending")]
    Pending = 1,
    
    [Description("Processing")]
    Processing = 2,
    
    [Description("Shipped")]
    Shipped = 3,
    
    [Description("Delivered")]
    Delivered = 4,
    
    [Description("Cancelled")]
    Cancelled = 5
}

// Option 2: Lookup Table with seeding
public class OrderStatus
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public bool IsActive { get; set; }
}
```

### 4.3 Aggregate/Query Migration

| OutSystems Aggregate | EF Core LINQ |
|---------------------|--------------|
| Source entity | DbSet<Entity> |
| Filter | .Where() |
| Sort | .OrderBy() / .OrderByDescending() |
| Join | .Include() / .Join() |
| Group By | .GroupBy() |
| Max Records | .Take() |
| Calculated Attribute | .Select() with projection |
| Count | .Count() / .CountAsync() |
| Sum/Avg/Min/Max | .Sum() / .Average() / .Min() / .Max() |

**Example:**
```csharp
// OutSystems Aggregate equivalent
var activeCustomersWithOrders = await _context.Customers
    .Where(c => c.IsActive)
    .Include(c => c.Orders.Where(o => o.Status == OrderStatus.Delivered))
    .OrderByDescending(c => c.CreatedDate)
    .Select(c => new CustomerDto
    {
        Id = c.Id,
        Name = c.Name,
        Email = c.Email,
        OrderCount = c.Orders.Count,
        TotalSpent = c.Orders.Sum(o => o.TotalAmount)
    })
    .Take(100)
    .ToListAsync();
```

### 4.4 Database Migration Strategy

| Approach | When to Use | Steps |
|----------|-------------|-------|
| **Big Bang** | Small DB, downtime OK | Export → Transform → Import |
| **Incremental** | Large DB, minimal downtime | Sync tool, cutover window |
| **Parallel Run** | Zero downtime required | Dual-write, gradual switch |

#### 4.4.1 Data Migration Steps

1. **Schema Migration**
   - Generate EF Core migrations from entities
   - Review and adjust migrations
   - Apply to target database

2. **Data Export from OutSystems**
   - Use OutSystems APIs or direct DB access
   - Export to CSV/JSON intermediate format
   - Include audit trail data

3. **Data Transformation**
   - Map old IDs to new IDs (if changing)
   - Convert data types
   - Handle null values
   - Validate referential integrity

4. **Data Import to .NET DB**
   - Bulk insert using EF Core or SqlBulkCopy
   - Validate row counts
   - Verify foreign key relationships

5. **Data Validation**
   - Compare record counts
   - Spot-check sample records
   - Validate calculated fields

---

## Phase 5: Business Logic Migration

### 5.1 Server Action Migration

| OutSystems Element | .NET Implementation |
|-------------------|---------------------|
| Server Action | Service class method |
| Input Parameter | Method parameter |
| Output Parameter | Return type (DTO or tuple) |
| Local Variable | Local variable |
| Assign | Variable assignment |
| If | if-else statement |
| Switch | switch expression |
| For Each | foreach / LINQ |
| Aggregate | Repository/DbContext call |
| Create/Update/Delete | EF Core operations |
| Exception Handler | try-catch block |
| Raise Exception | throw new Exception() |

#### 5.1.1 Service Layer Structure

```csharp
// Interface
public interface IOrderService
{
    Task<OrderDto> GetOrderByIdAsync(int orderId);
    Task<IEnumerable<OrderDto>> GetCustomerOrdersAsync(int customerId);
    Task<OrderDto> CreateOrderAsync(CreateOrderRequest request);
    Task<OrderDto> UpdateOrderStatusAsync(int orderId, OrderStatus status);
    Task CancelOrderAsync(int orderId, string reason);
}

// Implementation
public class OrderService : IOrderService
{
    private readonly IOrderRepository _orderRepository;
    private readonly ICustomerRepository _customerRepository;
    private readonly INotificationService _notificationService;
    private readonly ILogger<OrderService> _logger;
    private readonly IAuditService _auditService;

    public OrderService(
        IOrderRepository orderRepository,
        ICustomerRepository customerRepository,
        INotificationService notificationService,
        ILogger<OrderService> logger,
        IAuditService auditService)
    {
        _orderRepository = orderRepository;
        _customerRepository = customerRepository;
        _notificationService = notificationService;
        _logger = logger;
        _auditService = auditService;
    }

    public async Task<OrderDto> CreateOrderAsync(CreateOrderRequest request)
    {
        _logger.LogInformation("Creating order for customer {CustomerId}", request.CustomerId);
        
        try
        {
            // Validate customer exists
            var customer = await _customerRepository.GetByIdAsync(request.CustomerId);
            if (customer == null)
                throw new NotFoundException($"Customer {request.CustomerId} not found");

            // Create order
            var order = new Order
            {
                CustomerId = request.CustomerId,
                Items = request.Items.Select(i => new OrderItem
                {
                    ProductId = i.ProductId,
                    Quantity = i.Quantity,
                    UnitPrice = i.UnitPrice
                }).ToList(),
                Status = OrderStatus.Pending,
                CreatedDate = DateTime.UtcNow
            };

            order.TotalAmount = order.Items.Sum(i => i.Quantity * i.UnitPrice);

            await _orderRepository.AddAsync(order);
            await _orderRepository.SaveChangesAsync();

            // Audit
            await _auditService.LogAsync("Order", order.Id, "Created", request.CustomerId);

            // Notification
            await _notificationService.SendOrderConfirmationAsync(order);

            _logger.LogInformation("Order {OrderId} created successfully", order.Id);
            
            return order.ToDto();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating order for customer {CustomerId}", request.CustomerId);
            throw;
        }
    }
}
```

### 5.2 Timer/Scheduled Job Migration

| OutSystems Timer | .NET Options |
|-----------------|--------------|
| Timer (scheduled) | Hangfire / Quartz.NET |
| Timer (wake) | IHostedService |
| BPT Wait | Hangfire continuation |

**Example - Hangfire Job:**
```csharp
// Job definition
public class OrderCleanupJob
{
    private readonly IOrderService _orderService;
    private readonly ILogger<OrderCleanupJob> _logger;

    public OrderCleanupJob(IOrderService orderService, ILogger<OrderCleanupJob> logger)
    {
        _orderService = orderService;
        _logger = logger;
    }

    public async Task ExecuteAsync()
    {
        _logger.LogInformation("Starting order cleanup job");
        
        var cancelledCount = await _orderService.CleanupAbandonedOrdersAsync(TimeSpan.FromDays(30));
        
        _logger.LogInformation("Order cleanup completed. Cancelled {Count} orders", cancelledCount);
    }
}

// Registration in Program.cs
builder.Services.AddHangfire(config => 
    config.UseSqlServerStorage(connectionString));

// Schedule (in startup)
RecurringJob.AddOrUpdate<OrderCleanupJob>(
    "order-cleanup",
    job => job.ExecuteAsync(),
    Cron.Daily(2, 0)); // Run at 2 AM daily
```

### 5.3 BPT Process Migration

| OutSystems BPT | .NET Workflow Options |
|---------------|----------------------|
| Process | Elsa Workflows / Azure Durable Functions |
| Human Activity | Task queue with approval UI |
| Automatic Activity | Background job step |
| Wait | Durable timer / Delay |
| Decision | Conditional branching |
| Conditional Start | Event trigger |

**Example - Elsa Workflow:**
```csharp
public class OrderApprovalWorkflow : IWorkflow
{
    public void Build(IWorkflowBuilder builder)
    {
        builder
            .StartWith<ReceiveOrder>()
            .Then<ValidateOrder>()
            .Then<Fork>(fork => fork
                .When("RequiresApproval")
                    .Then<RequestApproval>()
                    .Then<WaitForApproval>()
                    .Then<Join>()
                .When("AutoApprove")
                    .Then<Join>()
            )
            .Then<ProcessPayment>()
            .Then<FulfillOrder>()
            .Then<SendConfirmation>();
    }
}
```

### 5.4 Exception Handling Strategy

```csharp
// Custom exception types
public class NotFoundException : Exception { }
public class ValidationException : Exception { }
public class BusinessRuleException : Exception { }

// Global exception handler middleware
public class GlobalExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (NotFoundException ex)
        {
            _logger.LogWarning(ex, "Resource not found");
            context.Response.StatusCode = 404;
            await context.Response.WriteAsJsonAsync(new { error = ex.Message });
        }
        catch (ValidationException ex)
        {
            _logger.LogWarning(ex, "Validation error");
            context.Response.StatusCode = 400;
            await context.Response.WriteAsJsonAsync(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception");
            context.Response.StatusCode = 500;
            await context.Response.WriteAsJsonAsync(new { error = "An error occurred" });
        }
    }
}
```

---

## Phase 6: User Interface Migration

### 6.1 Screen Migration Strategy

| OutSystems Screen Type | .NET Frontend Option |
|-----------------------|---------------------|
| Reactive Web | Blazor WebAssembly / React |
| Traditional Web | Blazor Server / Razor Pages |
| Mobile (PWA) | Blazor PWA / React Native |

### 6.2 Widget to Component Mapping

| OutSystems Widget | Blazor Component | React Component |
|------------------|------------------|-----------------|
| Input | `<InputText>` | `<input>` |
| Text Area | `<InputTextArea>` | `<textarea>` |
| Checkbox | `<InputCheckbox>` | `<input type="checkbox">` |
| Radio Button | `<InputRadioGroup>` | `<input type="radio">` |
| Dropdown | `<InputSelect>` | `<select>` |
| Button | `<button @onclick>` | `<button onClick>` |
| Link | `<NavLink>` | `<Link>` (React Router) |
| Container | `<div>` | `<div>` |
| If | `@if` | `{condition && }` |
| List Records | `@foreach` | `.map()` |
| Table Records | `<table>` with `@foreach` | Data grid component |
| Popup/Modal | Modal component | Modal component |
| Tabs | Tab component | Tab component |

### 6.3 Screen Example Migration

**OutSystems Screen → Blazor Component:**
```razor
@page "/customers"
@inject ICustomerService CustomerService
@inject NavigationManager Navigation

<PageTitle>Customers</PageTitle>

<h1>Customer List</h1>

@if (_loading)
{
    <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
    </div>
}
else if (_customers == null || !_customers.Any())
{
    <p>No customers found.</p>
}
else
{
    <div class="mb-3">
        <input type="text" class="form-control" placeholder="Search..."
               @bind="_searchTerm" @bind:event="oninput" @onkeyup="FilterCustomers" />
    </div>

    <table class="table table-striped">
        <thead>
            <tr>
                <th @onclick="() => SortBy(nameof(CustomerDto.Name))">Name</th>
                <th @onclick="() => SortBy(nameof(CustomerDto.Email))">Email</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            @foreach (var customer in _filteredCustomers)
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
                        <button class="btn btn-sm btn-primary" 
                                @onclick="() => EditCustomer(customer.Id)">Edit</button>
                        <button class="btn btn-sm btn-danger" 
                                @onclick="() => DeleteCustomer(customer.Id)">Delete</button>
                    </td>
                </tr>
            }
        </tbody>
    </table>
}

@code {
    private List<CustomerDto> _customers;
    private List<CustomerDto> _filteredCustomers;
    private string _searchTerm = "";
    private bool _loading = true;

    protected override async Task OnInitializedAsync()
    {
        _customers = await CustomerService.GetAllAsync();
        _filteredCustomers = _customers;
        _loading = false;
    }

    private void FilterCustomers()
    {
        _filteredCustomers = string.IsNullOrWhiteSpace(_searchTerm)
            ? _customers
            : _customers.Where(c => 
                c.Name.Contains(_searchTerm, StringComparison.OrdinalIgnoreCase) ||
                c.Email.Contains(_searchTerm, StringComparison.OrdinalIgnoreCase))
              .ToList();
    }

    private void EditCustomer(int id) => Navigation.NavigateTo($"/customers/{id}/edit");
    
    private async Task DeleteCustomer(int id)
    {
        if (await JSRuntime.InvokeAsync<bool>("confirm", "Delete this customer?"))
        {
            await CustomerService.DeleteAsync(id);
            _customers = await CustomerService.GetAllAsync();
            FilterCustomers();
        }
    }
}
```

### 6.4 Client Action Migration

| OutSystems Client Action | .NET/JS Equivalent |
|-------------------------|-------------------|
| Client Action | Blazor method / JS function |
| Ajax Refresh | StateHasChanged() / React setState |
| Run Server Action | HTTP call to API |
| Client Variable | Component state |
| Session Variable | Browser sessionStorage |
| JavaScript node | JS Interop |

---

## Phase 7: Integration Migration

### 7.1 REST API Consumption

**OutSystems REST Consume → .NET HttpClient:**
```csharp
// Service registration
builder.Services.AddHttpClient<IExternalApiService, ExternalApiService>(client =>
{
    client.BaseAddress = new Uri(configuration["ExternalApi:BaseUrl"]);
    client.DefaultRequestHeaders.Add("X-API-Key", configuration["ExternalApi:ApiKey"]);
    client.Timeout = TimeSpan.FromSeconds(30);
})
.AddPolicyHandler(GetRetryPolicy())
.AddPolicyHandler(GetCircuitBreakerPolicy());

// Polly policies for resilience
static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .WaitAndRetryAsync(3, retryAttempt => 
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
}

// Service implementation
public class ExternalApiService : IExternalApiService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ExternalApiService> _logger;

    public async Task<ProductDto> GetProductAsync(string productId)
    {
        _logger.LogInformation("Fetching product {ProductId} from external API", productId);
        
        var response = await _httpClient.GetAsync($"/api/products/{productId}");
        response.EnsureSuccessStatusCode();
        
        return await response.Content.ReadFromJsonAsync<ProductDto>();
    }
}
```

### 7.2 REST API Exposure

**OutSystems Service Action → .NET API Controller:**
```csharp
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class OrdersController : ControllerBase
{
    private readonly IOrderService _orderService;
    private readonly ILogger<OrdersController> _logger;

    public OrdersController(IOrderService orderService, ILogger<OrdersController> logger)
    {
        _orderService = orderService;
        _logger = logger;
    }

    /// <summary>
    /// Get order by ID
    /// </summary>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(OrderDto), 200)]
    [ProducesResponseType(404)]
    public async Task<ActionResult<OrderDto>> GetOrder(int id)
    {
        var order = await _orderService.GetOrderByIdAsync(id);
        if (order == null)
            return NotFound();
        return Ok(order);
    }

    /// <summary>
    /// Create new order
    /// </summary>
    [HttpPost]
    [ProducesResponseType(typeof(OrderDto), 201)]
    [ProducesResponseType(400)]
    public async Task<ActionResult<OrderDto>> CreateOrder([FromBody] CreateOrderRequest request)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var order = await _orderService.CreateOrderAsync(request);
        return CreatedAtAction(nameof(GetOrder), new { id = order.Id }, order);
    }
}
```

### 7.3 SOAP Web Service Migration

```csharp
// Using CoreWCF for SOAP services
builder.Services.AddServiceModelServices();
builder.Services.AddServiceModelMetadata();

// Or convert to REST and use adapter pattern
public class LegacySoapAdapter
{
    private readonly LegacySoapClient _soapClient;

    public async Task<CustomerInfo> GetCustomerAsync(string customerId)
    {
        // Call legacy SOAP service
        var soapResponse = await _soapClient.GetCustomerInfoAsync(customerId);
        
        // Map to modern DTO
        return new CustomerInfo
        {
            Id = soapResponse.CustomerID,
            Name = soapResponse.CustomerName,
            // ... mapping
        };
    }
}
```

### 7.4 Database Integration

```csharp
// Multiple database contexts
public class ExternalDbContext : DbContext
{
    public ExternalDbContext(DbContextOptions<ExternalDbContext> options) 
        : base(options) { }

    public DbSet<ExternalProduct> Products { get; set; }
}

// Registration
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddDbContext<ExternalDbContext>(options =>
    options.UseSqlServer(configuration.GetConnectionString("ExternalConnection")));
```

### 7.5 Message Queue Integration

```csharp
// Azure Service Bus example
public class OrderEventPublisher : IOrderEventPublisher
{
    private readonly ServiceBusSender _sender;

    public async Task PublishOrderCreatedAsync(OrderCreatedEvent @event)
    {
        var message = new ServiceBusMessage(JsonSerializer.Serialize(@event))
        {
            ContentType = "application/json",
            Subject = "OrderCreated",
            CorrelationId = @event.OrderId.ToString()
        };

        await _sender.SendMessageAsync(message);
    }
}

// Consumer
public class OrderEventConsumer : BackgroundService
{
    private readonly ServiceBusProcessor _processor;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _processor.ProcessMessageAsync += ProcessMessageAsync;
        _processor.ProcessErrorAsync += ProcessErrorAsync;
        
        await _processor.StartProcessingAsync(stoppingToken);
    }

    private async Task ProcessMessageAsync(ProcessMessageEventArgs args)
    {
        var @event = JsonSerializer.Deserialize<OrderCreatedEvent>(args.Message.Body);
        // Process event
        await args.CompleteMessageAsync(args.Message);
    }
}
```

---

## Phase 8: Security Implementation

### 8.1 Authentication Migration

| OutSystems | .NET Implementation |
|------------|---------------------|
| Built-in Users | ASP.NET Core Identity |
| External IdP (SAML) | SAML2 middleware |
| External IdP (OIDC) | Microsoft.Identity.Web |
| API Keys | Custom authentication handler |

**ASP.NET Core Identity Setup:**
```csharp
// Program.cs
builder.Services.AddIdentity<ApplicationUser, IdentityRole>(options =>
{
    options.Password.RequiredLength = 8;
    options.Password.RequireDigit = true;
    options.Password.RequireUppercase = true;
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
})
.AddEntityFrameworkStores<ApplicationDbContext>()
.AddDefaultTokenProviders();

// JWT for API authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = configuration["Jwt:Issuer"],
            ValidAudience = configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(configuration["Jwt:Key"]))
        };
    });
```

### 8.2 Authorization Migration

| OutSystems | .NET Implementation |
|------------|---------------------|
| Role | ASP.NET Core Role |
| Check Role | [Authorize(Roles = "...")] |
| Grant/Revoke | RoleManager |
| Screen access | Authorize attribute on page/controller |

```csharp
// Role-based authorization
[Authorize(Roles = "Admin,Manager")]
public class AdminController : ControllerBase { }

// Policy-based authorization
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("CanManageOrders", policy =>
        policy.RequireRole("Admin", "OrderManager")
              .RequireClaim("Department", "Sales", "Operations"));
    
    options.AddPolicy("CanViewReports", policy =>
        policy.RequireAssertion(context =>
            context.User.IsInRole("Admin") ||
            context.User.HasClaim("Permission", "ViewReports")));
});

// Apply policy
[Authorize(Policy = "CanManageOrders")]
public async Task<IActionResult> UpdateOrder(int id) { }
```

### 8.3 Session Management

```csharp
// Session configuration
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
});

// Distributed session with Redis
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = configuration["Redis:ConnectionString"];
    options.InstanceName = "AppSession_";
});
```

---

## Phase 9: Cross-Cutting Concerns

### 9.1 Logging Implementation

| OutSystems | .NET Implementation |
|------------|---------------------|
| Log Message | ILogger<T> |
| Log Level | LogLevel enum |
| Log to database | Serilog sink |

**Structured Logging with Serilog:**
```csharp
// Program.cs
builder.Host.UseSerilog((context, services, configuration) => configuration
    .ReadFrom.Configuration(context.Configuration)
    .ReadFrom.Services(services)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithEnvironmentName()
    .WriteTo.Console()
    .WriteTo.File("logs/log-.txt", rollingInterval: RollingInterval.Day)
    .WriteTo.Seq(context.Configuration["Seq:ServerUrl"])
    .WriteTo.ApplicationInsights(TelemetryConverter.Traces));

// appsettings.json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "System": "Warning"
      }
    }
  }
}

// Usage in service
public class OrderService
{
    private readonly ILogger<OrderService> _logger;

    public async Task<OrderDto> CreateOrderAsync(CreateOrderRequest request)
    {
        using (_logger.BeginScope(new Dictionary<string, object>
        {
            ["CustomerId"] = request.CustomerId,
            ["OrderItems"] = request.Items.Count
        }))
        {
            _logger.LogInformation("Creating new order");
            // ...
            _logger.LogInformation("Order {OrderId} created with total {Total}", 
                order.Id, order.TotalAmount);
        }
    }
}
```

### 9.2 Audit Trail Implementation

```csharp
// Audit entity
public class AuditLog
{
    public long Id { get; set; }
    public string EntityType { get; set; }
    public string EntityId { get; set; }
    public string Action { get; set; }  // Create, Update, Delete
    public string OldValues { get; set; }  // JSON
    public string NewValues { get; set; }  // JSON
    public string UserId { get; set; }
    public string UserName { get; set; }
    public DateTime Timestamp { get; set; }
    public string IpAddress { get; set; }
}

// Audit service
public interface IAuditService
{
    Task LogAsync(string entityType, object entityId, string action, 
                  object oldValues = null, object newValues = null);
}

public class AuditService : IAuditService
{
    private readonly ApplicationDbContext _context;
    private readonly IHttpContextAccessor _httpContextAccessor;

    public async Task LogAsync(string entityType, object entityId, string action,
                               object oldValues = null, object newValues = null)
    {
        var user = _httpContextAccessor.HttpContext?.User;
        
        var audit = new AuditLog
        {
            EntityType = entityType,
            EntityId = entityId?.ToString(),
            Action = action,
            OldValues = oldValues != null ? JsonSerializer.Serialize(oldValues) : null,
            NewValues = newValues != null ? JsonSerializer.Serialize(newValues) : null,
            UserId = user?.FindFirstValue(ClaimTypes.NameIdentifier),
            UserName = user?.Identity?.Name,
            Timestamp = DateTime.UtcNow,
            IpAddress = _httpContextAccessor.HttpContext?.Connection?.RemoteIpAddress?.ToString()
        };

        _context.AuditLogs.Add(audit);
        await _context.SaveChangesAsync();
    }
}

// Auto-audit with EF Core interceptor
public class AuditSaveChangesInterceptor : SaveChangesInterceptor
{
    public override async ValueTask<InterceptionResult<int>> SavingChangesAsync(
        DbContextEventData eventData, 
        InterceptionResult<int> result,
        CancellationToken cancellationToken = default)
    {
        var context = eventData.Context;
        if (context == null) return result;

        var entries = context.ChangeTracker.Entries()
            .Where(e => e.State is EntityState.Added or EntityState.Modified or EntityState.Deleted)
            .ToList();

        foreach (var entry in entries)
        {
            // Create audit records
        }

        return result;
    }
}
```

### 9.3 Notification System

```csharp
// Notification interfaces
public interface INotificationService
{
    Task SendEmailAsync(EmailNotification notification);
    Task SendSmsAsync(SmsNotification notification);
    Task SendPushAsync(PushNotification notification);
    Task SendInAppAsync(InAppNotification notification);
}

// Email implementation
public class EmailNotificationService : IEmailNotificationService
{
    private readonly IEmailSender _emailSender;
    private readonly ITemplateEngine _templateEngine;
    private readonly ILogger<EmailNotificationService> _logger;

    public async Task SendOrderConfirmationAsync(Order order, Customer customer)
    {
        var template = await _templateEngine.RenderAsync("OrderConfirmation", new
        {
            CustomerName = customer.Name,
            OrderId = order.Id,
            OrderDate = order.CreatedDate,
            Items = order.Items,
            TotalAmount = order.TotalAmount
        });

        await _emailSender.SendAsync(new EmailMessage
        {
            To = customer.Email,
            Subject = $"Order Confirmation - #{order.Id}",
            HtmlBody = template,
            Priority = EmailPriority.Normal
        });

        _logger.LogInformation("Order confirmation email sent for order {OrderId}", order.Id);
    }
}

// Notification preferences
public class NotificationPreferences
{
    public int UserId { get; set; }
    public bool EmailEnabled { get; set; }
    public bool SmsEnabled { get; set; }
    public bool PushEnabled { get; set; }
    public bool InAppEnabled { get; set; }
    public List<string> SubscribedTopics { get; set; }
}
```

### 9.4 Caching Strategy

```csharp
// Distributed cache
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = configuration["Redis:ConnectionString"];
});

// Cache service
public class CacheService : ICacheService
{
    private readonly IDistributedCache _cache;
    private readonly ILogger<CacheService> _logger;

    public async Task<T> GetOrSetAsync<T>(
        string key, 
        Func<Task<T>> factory, 
        TimeSpan? expiration = null)
    {
        var cached = await _cache.GetStringAsync(key);
        if (cached != null)
        {
            _logger.LogDebug("Cache hit for key {Key}", key);
            return JsonSerializer.Deserialize<T>(cached);
        }

        _logger.LogDebug("Cache miss for key {Key}", key);
        var value = await factory();
        
        var options = new DistributedCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = expiration ?? TimeSpan.FromMinutes(10)
        };

        await _cache.SetStringAsync(key, JsonSerializer.Serialize(value), options);
        return value;
    }

    public async Task InvalidateAsync(string key)
    {
        await _cache.RemoveAsync(key);
        _logger.LogDebug("Cache invalidated for key {Key}", key);
    }
}

// Usage
public async Task<CustomerDto> GetCustomerAsync(int id)
{
    return await _cacheService.GetOrSetAsync(
        $"customer:{id}",
        () => _customerRepository.GetByIdAsync(id),
        TimeSpan.FromMinutes(15));
}
```

### 9.5 Health Checks & Monitoring

```csharp
// Health checks registration
builder.Services.AddHealthChecks()
    .AddSqlServer(configuration.GetConnectionString("DefaultConnection"), name: "database")
    .AddRedis(configuration["Redis:ConnectionString"], name: "redis")
    .AddUrlGroup(new Uri(configuration["ExternalApi:HealthUrl"]), name: "external-api")
    .AddCheck<CustomHealthCheck>("custom");

// Custom health check
public class CustomHealthCheck : IHealthCheck
{
    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, 
        CancellationToken cancellationToken = default)
    {
        // Check critical dependencies
        var isHealthy = await CheckDependenciesAsync();
        
        return isHealthy 
            ? HealthCheckResult.Healthy("All systems operational")
            : HealthCheckResult.Unhealthy("One or more dependencies failed");
    }
}

// Endpoint mapping
app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false // Just checks if app is running
});
```

### 9.6 SLA Monitoring

```csharp
// Response time tracking middleware
public class ResponseTimeMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ResponseTimeMiddleware> _logger;

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        
        context.Response.OnStarting(() =>
        {
            stopwatch.Stop();
            var responseTime = stopwatch.ElapsedMilliseconds;
            
            context.Response.Headers["X-Response-Time"] = $"{responseTime}ms";
            
            // Log slow requests (SLA breach)
            if (responseTime > 2000) // 2 second SLA
            {
                _logger.LogWarning(
                    "SLA breach: {Method} {Path} took {ResponseTime}ms",
                    context.Request.Method,
                    context.Request.Path,
                    responseTime);
            }
            
            return Task.CompletedTask;
        });

        await _next(context);
    }
}

// SLA metrics with Application Insights
public class SlaMetricsService
{
    private readonly TelemetryClient _telemetryClient;

    public void TrackRequest(string operation, TimeSpan duration, bool success)
    {
        _telemetryClient.TrackMetric($"SLA.{operation}.Duration", duration.TotalMilliseconds);
        _telemetryClient.TrackMetric($"SLA.{operation}.Success", success ? 1 : 0);
    }

    public void TrackAvailability(string component, bool available)
    {
        _telemetryClient.TrackAvailability(
            component,
            DateTimeOffset.UtcNow,
            TimeSpan.FromSeconds(1),
            "HealthCheck",
            available);
    }
}
```

---

## Phase 10: Testing & Validation

### 10.1 Unit Testing

```csharp
public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _orderRepoMock;
    private readonly Mock<ICustomerRepository> _customerRepoMock;
    private readonly Mock<INotificationService> _notificationMock;
    private readonly OrderService _sut;

    public OrderServiceTests()
    {
        _orderRepoMock = new Mock<IOrderRepository>();
        _customerRepoMock = new Mock<ICustomerRepository>();
        _notificationMock = new Mock<INotificationService>();
        
        _sut = new OrderService(
            _orderRepoMock.Object,
            _customerRepoMock.Object,
            _notificationMock.Object,
            Mock.Of<ILogger<OrderService>>(),
            Mock.Of<IAuditService>());
    }

    [Fact]
    public async Task CreateOrderAsync_ValidRequest_ReturnsOrder()
    {
        // Arrange
        var customer = new Customer { Id = 1, Name = "Test" };
        _customerRepoMock.Setup(x => x.GetByIdAsync(1)).ReturnsAsync(customer);
        
        var request = new CreateOrderRequest
        {
            CustomerId = 1,
            Items = new List<OrderItemRequest>
            {
                new() { ProductId = 1, Quantity = 2, UnitPrice = 10.00m }
            }
        };

        // Act
        var result = await _sut.CreateOrderAsync(request);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(20.00m, result.TotalAmount);
        _notificationMock.Verify(x => x.SendOrderConfirmationAsync(It.IsAny<Order>()), Times.Once);
    }

    [Fact]
    public async Task CreateOrderAsync_CustomerNotFound_ThrowsNotFoundException()
    {
        // Arrange
        _customerRepoMock.Setup(x => x.GetByIdAsync(It.IsAny<int>())).ReturnsAsync((Customer)null);

        // Act & Assert
        await Assert.ThrowsAsync<NotFoundException>(
            () => _sut.CreateOrderAsync(new CreateOrderRequest { CustomerId = 999 }));
    }
}
```

### 10.2 Integration Testing

```csharp
public class OrdersApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    private readonly WebApplicationFactory<Program> _factory;

    public OrdersApiTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace with test database
                services.RemoveAll<DbContextOptions<ApplicationDbContext>>();
                services.AddDbContext<ApplicationDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));
            });
        });
        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task GetOrder_ExistingOrder_ReturnsOk()
    {
        // Arrange - seed test data
        using var scope = _factory.Services.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        context.Orders.Add(new Order { Id = 1, CustomerId = 1, TotalAmount = 100 });
        await context.SaveChangesAsync();

        // Act
        var response = await _client.GetAsync("/api/orders/1");

        // Assert
        response.EnsureSuccessStatusCode();
        var order = await response.Content.ReadFromJsonAsync<OrderDto>();
        Assert.Equal(1, order.Id);
    }
}
```

### 10.3 Data Validation Checklist

| Validation | Query/Check |
|------------|-------------|
| Record counts match | Compare COUNT(*) between source and target |
| Sum of amounts match | Compare SUM(amount) for financial data |
| Foreign keys valid | Check for orphan records |
| No data truncation | Verify long text fields |
| Date/time precision | Check milliseconds if needed |
| NULL handling | Verify NULL vs empty string |
| Character encoding | Check special characters, emojis |

### 10.4 Functional Equivalence Testing

```csharp
// Compare OutSystems vs .NET output
public class FunctionalEquivalenceTests
{
    [Theory]
    [MemberData(nameof(GetTestCases))]
    public async Task BusinessLogic_SameInput_SameOutput(TestCase testCase)
    {
        // Get result from OutSystems (via API)
        var osResult = await _outsystemsClient.ExecuteAsync(testCase.Input);
        
        // Get result from .NET
        var dotnetResult = await _dotnetService.ExecuteAsync(testCase.Input);
        
        // Compare
        Assert.Equivalent(osResult, dotnetResult);
    }
}
```

---

## Phase 11: Deployment & Go-Live

### 11.1 Deployment Checklist

| Category | Item | Status |
|----------|------|--------|
| **Infrastructure** | Production environment provisioned | ☐ |
| | SSL certificates configured | ☐ |
| | DNS entries updated | ☐ |
| | Load balancer configured | ☐ |
| | CDN configured (if applicable) | ☐ |
| **Database** | Production database created | ☐ |
| | Migrations applied | ☐ |
| | Data migrated and validated | ☐ |
| | Backup configured | ☐ |
| **Security** | Secrets in Key Vault | ☐ |
| | Firewall rules configured | ☐ |
| | WAF enabled | ☐ |
| | Penetration testing completed | ☐ |
| **Monitoring** | Application Insights configured | ☐ |
| | Alerts configured | ☐ |
| | Dashboard created | ☐ |
| | Log aggregation enabled | ☐ |
| **Testing** | UAT signed off | ☐ |
| | Performance testing completed | ☐ |
| | Load testing completed | ☐ |
| **Documentation** | Runbook created | ☐ |
| | API documentation published | ☐ |
| | User training completed | ☐ |

### 11.2 Cutover Plan

| Step | Action | Duration | Rollback |
|------|--------|----------|----------|
| 1 | Announce maintenance window | - | - |
| 2 | Disable OutSystems app | 5 min | Re-enable |
| 3 | Final data sync | 30 min | Restore backup |
| 4 | Update DNS/load balancer | 5 min | Revert DNS |
| 5 | Smoke test new app | 15 min | Rollback deploy |
| 6 | Enable monitoring alerts | 5 min | - |
| 7 | Announce go-live | - | - |

### 11.3 Rollback Plan

```
IF critical issues detected within 24 hours:
  1. Switch DNS/load balancer back to OutSystems
  2. Disable .NET application
  3. Assess and fix issues
  4. Plan new cutover window

IF issues detected after 24 hours:
  1. Implement hotfix in .NET
  2. Deploy emergency patch
  3. Monitor closely
```

---

## Phase 12: Post-Migration Support

### 12.1 Hypercare Period (Weeks 1-4)

| Week | Focus | Activities |
|------|-------|------------|
| 1 | Stabilization | 24/7 monitoring, immediate bug fixes |
| 2 | Optimization | Performance tuning, user feedback |
| 3 | Enhancement | Minor improvements, documentation |
| 4 | Handover | Knowledge transfer, support transition |

### 12.2 Monitoring Dashboard Metrics

| Metric | SLA Target | Alert Threshold |
|--------|------------|-----------------|
| Uptime | 99.9% | < 99.5% |
| Response time (P95) | < 500ms | > 1000ms |
| Error rate | < 0.1% | > 1% |
| CPU utilization | < 70% | > 85% |
| Memory utilization | < 80% | > 90% |
| Database connections | < 80% pool | > 90% pool |

### 12.3 Decommission OutSystems

| Step | Action | Timeline |
|------|--------|----------|
| 1 | Parallel run period | 2-4 weeks |
| 2 | Redirect all traffic to .NET | After validation |
| 3 | Disable OutSystems app | After 1 week stable |
| 4 | Archive OutSystems data | After 30 days |
| 5 | Terminate OutSystems license | End of contract |

---

## Appendix A: Migration Effort Estimates

| Component | Simple | Medium | Complex |
|-----------|--------|--------|---------|
| Entity | 0.5 hrs | 1 hr | 2 hrs |
| Screen | 2 hrs | 4 hrs | 8 hrs |
| Server Action | 1 hr | 2 hrs | 4 hrs |
| Client Action | 0.5 hrs | 1 hr | 2 hrs |
| REST Integration | 2 hrs | 4 hrs | 8 hrs |
| Timer/Job | 1 hr | 2 hrs | 4 hrs |
| BPT Process | 4 hrs | 8 hrs | 16 hrs |

## Appendix B: Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data loss during migration | Low | Critical | Multiple backups, validation scripts |
| Performance degradation | Medium | High | Load testing, optimization sprints |
| Security vulnerabilities | Low | Critical | Security audit, pen testing |
| Extended downtime | Low | High | Parallel run, quick rollback plan |
| User adoption issues | Medium | Medium | Training, change management |
| Integration failures | Medium | High | Thorough integration testing |

---

*Document Version: 1.0*  
*Created: 2026-07-22*  
*Last Updated: 2026-07-22*
