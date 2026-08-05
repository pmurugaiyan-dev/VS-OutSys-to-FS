# OutSystems to FullStack Component Mapping

## Data Layer

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **Entity** | JPA Entity / Spring Data | Entity Framework Core Model |
| **Entity Attribute** | @Column annotation | Property with [Column] attribute |
| **Entity Identifier** | @Id with @GeneratedValue | [Key] with identity |
| **Foreign Key / Reference** | @ManyToOne, @OneToMany | Navigation properties |
| **Index** | @Index annotation | [Index] attribute / Fluent API |
| **Static Entity** | Enum or lookup table | Enum or lookup table |
| **Entity Action (CRUD)** | Spring Data Repository | EF Core DbSet methods |
| **Aggregate (Query)** | JPQL / Criteria API / QueryDSL | LINQ queries |
| **Advanced Query (SQL)** | Native SQL with @Query | Raw SQL / FromSqlRaw |

## Business Logic

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **Server Action** | @Service method | Service class method |
| **Client Action** | Frontend JS/TS function | Frontend JS/TS function |
| **Service Action (exposed)** | @RestController endpoint | [ApiController] endpoint |
| **Timer (Scheduled)** | @Scheduled / Quartz | Hangfire / IHostedService |
| **Process (BPM)** | Camunda / Flowable | Elsa Workflows / Azure Durable Functions |
| **Exception Handler** | @ExceptionHandler / try-catch | Middleware / try-catch |
| **Input Parameter** | Method parameter | Method parameter |
| **Output Parameter** | Return type / DTO | Return type / DTO |
| **Local Variable** | Local variable | Local variable |
| **Assign** | Variable assignment | Variable assignment |
| **If / Switch** | if-else / switch | if-else / switch |
| **For Each** | for / forEach / Stream | foreach / LINQ |
| **Aggregate in Action** | Repository call | DbContext query |

## User Interface

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **Screen (Reactive)** | React / Angular component | React / Blazor component |
| **Screen (Traditional)** | Thymeleaf / JSP | Razor Pages / MVC View |
| **Block (Reusable)** | React/Angular component | React/Blazor component |
| **Web Block** | Partial view / component | Partial view / component |
| **Input Widget** | `<input>` / form control | `<input>` / form control |
| **Button** | `<button>` with onClick | `<button>` with onClick |
| **Table Records** | Data grid component | Data grid component |
| **List Records** | map() / ngFor | map() / @foreach |
| **If Widget** | Conditional rendering | Conditional rendering |
| **Container** | `<div>` | `<div>` |
| **Expression** | Template interpolation | Template interpolation |
| **Link** | `<a>` / Router Link | `<a>` / NavLink |
| **Image** | `<img>` | `<img>` |
| **Popup / Modal** | Modal component | Modal component |
| **CSS / Theme** | CSS / SCSS / Tailwind | CSS / SCSS / Tailwind |

## Integration

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **REST API (Consume)** | RestTemplate / WebClient / Feign | HttpClient / RestSharp |
| **REST API (Expose)** | @RestController | [ApiController] |
| **SOAP Web Service** | JAX-WS / Spring WS | WCF / CoreWCF |
| **Database Connection** | DataSource / HikariCP | SqlConnection / DbContext |
| **External Database** | Multiple DataSources | Multiple DbContexts |
| **SAP Integration** | SAP JCo | SAP .NET Connector |
| **Extension (C#/.NET)** | N/A (rewrite in Java) | Direct reuse possible |
| **Extension (Java)** | Direct reuse possible | N/A (rewrite in C#) |

## Security

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **User** | Spring Security UserDetails | ASP.NET Identity User |
| **Role** | @RolesAllowed / GrantedAuthority | [Authorize(Roles)] / Role claims |
| **Login** | Spring Security authentication | ASP.NET Identity SignIn |
| **Logout** | SecurityContextHolder.clear() | SignOutAsync() |
| **Session** | HttpSession / Redis | ISession / Redis |
| **Check Role** | hasRole() / @PreAuthorize | User.IsInRole() / [Authorize] |
| **CSRF Protection** | Spring Security CSRF | Antiforgery tokens |
| **Encryption** | javax.crypto / Bouncy Castle | System.Security.Cryptography |

## Site Properties & Configuration

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **Site Property** | application.properties / @Value | appsettings.json / IConfiguration |
| **Session Variable** | HttpSession attribute | Session / TempData |
| **Client Variable** | localStorage / sessionStorage | localStorage / sessionStorage |
| **Application Variable** | Static / singleton | Static / singleton |

## Resources & Assets

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **Image Resource** | static/images folder | wwwroot/images folder |
| **JavaScript** | static/js folder | wwwroot/js folder |
| **CSS** | static/css folder | wwwroot/css folder |
| **Script (inline)** | React useEffect / Angular | Blazor JS interop / script tag |

## Error Handling & Logging

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **Exception** | Java Exception class | C# Exception class |
| **Raise Exception** | throw new Exception() | throw new Exception() |
| **OnException Handler** | @ExceptionHandler / @ControllerAdvice | Exception middleware |
| **Log Message** | SLF4J / Log4j | Serilog / NLog / ILogger |

## Deployment & Infrastructure

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **Module** | Microservice / JAR | Microservice / DLL |
| **Application** | Multiple microservices | Multiple microservices |
| **Environment** | Docker + K8s / AWS / Azure | Docker + K8s / Azure / AWS |
| **Database** | PostgreSQL / MySQL | SQL Server / PostgreSQL |
| **File Storage** | S3 / MinIO | Azure Blob / S3 |
| **Cache** | Redis / Hazelcast | Redis / MemoryCache |

## Testing

| OutSystems Component | Java Stack | .NET Stack |
|---------------------|------------|------------|
| **BDD Framework** | Cucumber / JBehave | SpecFlow / xBehave |
| **Unit Testing** | JUnit / Mockito | xUnit / NUnit / Moq |
| **API Testing** | RestAssured / MockMvc | WebApplicationFactory |
| **UI Testing** | Selenium / Playwright | Selenium / Playwright |

---

## Migration Complexity Guide

| Complexity | OutSystems Features | Migration Effort |
|------------|---------------------|------------------|
| **Low** | Simple CRUD, basic screens, standard widgets | Automated (80%+) |
| **Medium** | Custom queries, integrations, business logic | Semi-automated (50-70%) |
| **High** | BPT processes, complex UI, custom extensions | Manual with AI assist (30-50%) |
| **Very High** | Heavy customization, platform-specific features | Significant rewrite needed |

---

*Created: 2026-07-20*
