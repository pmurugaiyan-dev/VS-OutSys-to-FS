"""
.NET Project Generator
Generates .NET project structure from parsed OutSystems manifest.
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime


class DotNetGenerator:
    """Generates .NET project structure from parsed OutSystems data."""
    
    def __init__(self, namespace: str, output_dir: str):
        self.namespace = namespace
        self.output_dir = output_dir
        
    def generate_all(self, parsed_dir: str):
        """Generate complete .NET project structure."""
        # Load parsed data
        entities = self._load_json(os.path.join(parsed_dir, "entities.json"))
        web_blocks = self._load_json(os.path.join(parsed_dir, "web_blocks.json"))
        summary = self._load_json(os.path.join(parsed_dir, "manifest_summary.json"))
        
        # Create folder structure
        self._create_folders()
        
        # Generate files
        generated = {}
        generated["csproj"] = self._generate_csproj()
        generated["Program.cs"] = self._generate_program_cs(entities)
        generated["appsettings.json"] = self._generate_appsettings()
        generated["Dockerfile"] = self._generate_dockerfile()
        generated["docker-compose.yml"] = self._generate_docker_compose()
        
        # Generate entities
        for entity in entities:
            if entity.get("kind") in ["Entity", "HiddenEntity"]:
                path = self._generate_entity(entity)
                generated[f"Entity_{entity['name']}"] = path
        
        # Generate DbContext
        generated["AppDbContext.cs"] = self._generate_db_context(entities)
        
        # Generate repository interfaces and implementations
        generated["IRepository.cs"] = self._generate_repository_interface()
        generated["Repository.cs"] = self._generate_repository_base()
        
        # Generate services skeleton
        for entity in entities:
            if entity.get("kind") == "Entity":
                path = self._generate_service(entity)
                generated[f"Service_{entity['name']}"] = path
        
        # Generate LLM prompts for detailed implementation
        self._generate_llm_prompts(entities, web_blocks, summary)
        
        # Generate migration report
        self._generate_report(entities, web_blocks, summary, generated)
        
        return generated
    
    def _load_json(self, path: str) -> Any:
        """Load JSON file."""
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return []
    
    def _create_folders(self):
        """Create .NET project folder structure."""
        folders = [
            "Models/Entities",
            "Models/DTOs",
            "Models/Enums",
            "Data",
            "Data/Configurations",
            "Data/Repositories",
            "Services",
            "Services/Interfaces",
            "Controllers",
            "Pages",
            "Components",
            "Shared",
            "wwwroot",
            "wwwroot/css",
            "wwwroot/js",
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(self.output_dir, folder), exist_ok=True)
    
    def _generate_csproj(self) -> str:
        """Generate .csproj file."""
        content = f"""<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RootNamespace>{self.namespace}</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.0.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
    </PackageReference>
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
    <PackageReference Include="AutoMapper.Extensions.Microsoft.DependencyInjection" Version="12.0.1" />
    <PackageReference Include="FluentValidation.AspNetCore" Version="11.3.0" />
    <PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
  </ItemGroup>

</Project>
"""
        path = os.path.join(self.output_dir, f"{self.namespace}.csproj")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def _generate_program_cs(self, entities: List[Dict]) -> str:
        """Generate Program.cs."""
        entity_names = [e['name'] for e in entities if e.get('kind') == 'Entity']
        
        content = f"""using Microsoft.EntityFrameworkCore;
using {self.namespace}.Data;
using {self.namespace}.Services;
using {self.namespace}.Services.Interfaces;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .CreateLogger();

builder.Host.UseSerilog();

// Database
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// AutoMapper
builder.Services.AddAutoMapper(typeof(Program));

// Services - TODO: Register your services here
// Example: builder.Services.AddScoped<ICustomerService, CustomerService>();

// Controllers
builder.Services.AddControllers();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{{
    app.UseSwagger();
    app.UseSwaggerUI();
}}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

// Apply migrations on startup (development only)
using (var scope = app.Services.CreateScope())
{{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}}

app.Run();
"""
        path = os.path.join(self.output_dir, "Program.cs")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def _generate_appsettings(self) -> str:
        """Generate appsettings.json."""
        content = {
            "Logging": {
                "LogLevel": {
                    "Default": "Information",
                    "Microsoft.AspNetCore": "Warning"
                }
            },
            "AllowedHosts": "*",
            "ConnectionStrings": {
                "DefaultConnection": f"Server=localhost;Database={self.namespace};Trusted_Connection=True;TrustServerCertificate=True"
            },
            "Serilog": {
                "MinimumLevel": {
                    "Default": "Information"
                }
            }
        }
        
        path = os.path.join(self.output_dir, "appsettings.json")
        with open(path, 'w') as f:
            json.dump(content, f, indent=2)
        return path
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile."""
        content = f"""FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["{self.namespace}.csproj", "./"]
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "{self.namespace}.dll"]
"""
        path = os.path.join(self.output_dir, "Dockerfile")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml."""
        content = f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__DefaultConnection=Server=db;Database={self.namespace};User=sa;Password=YourStrong!Passw0rd;TrustServerCertificate=True
    depends_on:
      - db

  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=YourStrong!Passw0rd
    ports:
      - "1433:1433"
    volumes:
      - sqldata:/var/opt/mssql

volumes:
  sqldata:
"""
        path = os.path.join(self.output_dir, "docker-compose.yml")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def _generate_entity(self, entity: Dict) -> str:
        """Generate entity class (skeleton - needs LLM for attributes)."""
        name = entity['name']
        
        content = f"""using System.ComponentModel.DataAnnotations;

namespace {self.namespace}.Models.Entities;

/// <summary>
/// Entity migrated from OutSystems: {name}
/// UID: {entity.get('uid', 'N/A')}
/// TODO: Add attributes based on OML definition
/// </summary>
public class {name}
{{
    [Key]
    public int Id {{ get; set; }}
    
    // TODO: Add entity attributes here
    // This skeleton was generated from Manifest.xml
    // Use LLM agent with OML details to complete the entity
}}
"""
        path = os.path.join(self.output_dir, "Models", "Entities", f"{name}.cs")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def _generate_db_context(self, entities: List[Dict]) -> str:
        """Generate AppDbContext."""
        entity_names = [e['name'] for e in entities if e.get('kind') in ['Entity', 'HiddenEntity']]
        
        dbsets = "\n    ".join([
            f"public DbSet<{name}> {name}s {{ get; set; }}"
            for name in entity_names
        ])
        
        usings = "\n".join([
            f"using {self.namespace}.Models.Entities;"
        ])
        
        content = f"""using Microsoft.EntityFrameworkCore;
{usings}

namespace {self.namespace}.Data;

public class AppDbContext : DbContext
{{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {{
    }}
    
    {dbsets}
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {{
        base.OnModelCreating(modelBuilder);
        
        // TODO: Add entity configurations
        // modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }}
}}
"""
        path = os.path.join(self.output_dir, "Data", "AppDbContext.cs")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def _generate_repository_interface(self) -> str:
        """Generate generic repository interface."""
        content = f"""namespace {self.namespace}.Data.Repositories;

public interface IRepository<T> where T : class
{{
    Task<T?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IEnumerable<T>> GetAllAsync(CancellationToken ct = default);
    Task<T> AddAsync(T entity, CancellationToken ct = default);
    Task UpdateAsync(T entity, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
    IQueryable<T> Query();
}}
"""
        path = os.path.join(self.output_dir, "Data", "Repositories", "IRepository.cs")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def _generate_repository_base(self) -> str:
        """Generate base repository implementation."""
        content = f"""using Microsoft.EntityFrameworkCore;

namespace {self.namespace}.Data.Repositories;

public class Repository<T> : IRepository<T> where T : class
{{
    protected readonly AppDbContext _context;
    protected readonly DbSet<T> _dbSet;
    
    public Repository(AppDbContext context)
    {{
        _context = context;
        _dbSet = context.Set<T>();
    }}
    
    public virtual async Task<T?> GetByIdAsync(int id, CancellationToken ct = default)
    {{
        return await _dbSet.FindAsync(new object[] {{ id }}, ct);
    }}
    
    public virtual async Task<IEnumerable<T>> GetAllAsync(CancellationToken ct = default)
    {{
        return await _dbSet.ToListAsync(ct);
    }}
    
    public virtual async Task<T> AddAsync(T entity, CancellationToken ct = default)
    {{
        await _dbSet.AddAsync(entity, ct);
        await _context.SaveChangesAsync(ct);
        return entity;
    }}
    
    public virtual async Task UpdateAsync(T entity, CancellationToken ct = default)
    {{
        _dbSet.Update(entity);
        await _context.SaveChangesAsync(ct);
    }}
    
    public virtual async Task DeleteAsync(int id, CancellationToken ct = default)
    {{
        var entity = await GetByIdAsync(id, ct);
        if (entity != null)
        {{
            _dbSet.Remove(entity);
            await _context.SaveChangesAsync(ct);
        }}
    }}
    
    public virtual IQueryable<T> Query()
    {{
        return _dbSet.AsQueryable();
    }}
}}
"""
        path = os.path.join(self.output_dir, "Data", "Repositories", "Repository.cs")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def _generate_service(self, entity: Dict) -> str:
        """Generate service interface and implementation skeleton."""
        name = entity['name']
        
        # Interface
        interface_content = f"""namespace {self.namespace}.Services.Interfaces;

public interface I{name}Service
{{
    Task<{name}?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IEnumerable<{name}>> GetAllAsync(CancellationToken ct = default);
    Task<{name}> CreateAsync({name} entity, CancellationToken ct = default);
    Task UpdateAsync({name} entity, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
    
    // TODO: Add migrated server actions here
}}
"""
        interface_path = os.path.join(self.output_dir, "Services", "Interfaces", f"I{name}Service.cs")
        with open(interface_path, 'w') as f:
            f.write(interface_content)
        
        # Implementation
        impl_content = f"""using {self.namespace}.Data.Repositories;
using {self.namespace}.Models.Entities;
using {self.namespace}.Services.Interfaces;

namespace {self.namespace}.Services;

public class {name}Service : I{name}Service
{{
    private readonly IRepository<{name}> _repository;
    private readonly ILogger<{name}Service> _logger;
    
    public {name}Service(IRepository<{name}> repository, ILogger<{name}Service> logger)
    {{
        _repository = repository;
        _logger = logger;
    }}
    
    public async Task<{name}?> GetByIdAsync(int id, CancellationToken ct = default)
    {{
        return await _repository.GetByIdAsync(id, ct);
    }}
    
    public async Task<IEnumerable<{name}>> GetAllAsync(CancellationToken ct = default)
    {{
        return await _repository.GetAllAsync(ct);
    }}
    
    public async Task<{name}> CreateAsync({name} entity, CancellationToken ct = default)
    {{
        return await _repository.AddAsync(entity, ct);
    }}
    
    public async Task UpdateAsync({name} entity, CancellationToken ct = default)
    {{
        await _repository.UpdateAsync(entity, ct);
    }}
    
    public async Task DeleteAsync(int id, CancellationToken ct = default)
    {{
        await _repository.DeleteAsync(id, ct);
    }}
    
    // TODO: Implement migrated server actions
}}
"""
        impl_path = os.path.join(self.output_dir, "Services", f"{name}Service.cs")
        with open(impl_path, 'w') as f:
            f.write(impl_content)
        
        return impl_path
    
    def _generate_llm_prompts(self, entities: List[Dict], web_blocks: List[Dict], summary: Dict):
        """Generate prompts for LLM to complete the implementation."""
        prompts_dir = os.path.join(self.output_dir, ".work", "llm_prompts")
        os.makedirs(prompts_dir, exist_ok=True)
        
        # Entity completion prompt
        entity_prompt = f"""Complete the entity definitions for the following OutSystems entities.

Target Namespace: {self.namespace}.Models.Entities

## Entities to Complete:
{json.dumps([e for e in entities if e.get('kind') in ['Entity', 'HiddenEntity']], indent=2)}

## Requirements:
1. Add appropriate attributes (properties) based on common patterns for entity names
2. Add data annotations ([Required], [MaxLength], etc.)
3. Add navigation properties for relationships
4. Use C# 8.0+ features (nullable reference types)

For each entity, generate a complete C# class with:
- All likely attributes based on the entity name
- Proper data annotations
- XML documentation comments
"""
        with open(os.path.join(prompts_dir, "entity_completion.txt"), 'w') as f:
            f.write(entity_prompt)
        
        # Service completion prompt
        service_prompt = f"""Generate service methods for the following OutSystems entities.

Target Namespace: {self.namespace}.Services

## Summary:
- Total Entities: {summary.get('total_entities', 0)}
- Total Actions: {summary.get('total_actions', 0)}
- Total WebBlocks: {summary.get('total_web_blocks', 0)}

## Requirements:
1. Implement CRUD operations
2. Add business logic methods based on entity purpose
3. Include validation
4. Add logging
5. Handle exceptions appropriately
"""
        with open(os.path.join(prompts_dir, "service_completion.txt"), 'w') as f:
            f.write(service_prompt)
    
    def _generate_report(self, entities: List[Dict], web_blocks: List[Dict], summary: Dict, generated: Dict):
        """Generate migration report."""
        report = f"""# Migration Report - {self.namespace}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Source Application
- Server Version: {summary.get('server_version', 'N/A')}
- Creation Date: {summary.get('creation_date', 'N/A')}

## Components Identified

| Component | Count |
|-----------|-------|
| Entities | {len([e for e in entities if e.get('kind') == 'Entity'])} |
| Hidden Entities | {len([e for e in entities if e.get('kind') == 'HiddenEntity'])} |
| Web Blocks | {len(web_blocks)} |
| Actions | {summary.get('total_actions', 0)} |

## Entities

| Name | Kind | UID |
|------|------|-----|
"""
        for entity in entities:
            report += f"| {entity.get('name', 'N/A')} | {entity.get('kind', 'N/A')} | {entity.get('uid', 'N/A')[:8]}... |\n"
        
        report += f"""

## Generated Files

| Category | Count |
|----------|-------|
| Project Files | 5 |
| Entity Models | {len([e for e in entities if e.get('kind') in ['Entity', 'HiddenEntity']])} |
| Services | {len([e for e in entities if e.get('kind') == 'Entity'])} |
| Repository | 2 |

## Next Steps

1. **Complete Entity Definitions**: Use LLM prompts in `.work/llm_prompts/` to add attributes
2. **Add Relationships**: Define foreign keys and navigation properties
3. **Implement Services**: Add business logic to service classes
4. **Create Controllers**: Generate API controllers for each entity
5. **Add UI Components**: Generate Blazor pages/components
6. **Testing**: Create unit and integration tests

## Notes

- Entity skeletons were generated from Manifest.xml metadata
- Full entity attributes require parsing the binary OML file (needs OutSystems DLLs)
- Use the OML Utilities tool to extract full XML from OML files for complete migration

## Files Location

Output Directory: `{self.output_dir}`
"""
        
        reports_dir = os.path.join(self.output_dir, ".work", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        path = os.path.join(reports_dir, "migration-report.md")
        with open(path, 'w') as f:
            f.write(report)
        
        return path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate .NET project from parsed manifest")
    parser.add_argument("parsed_dir", help="Directory with parsed manifest JSON files")
    parser.add_argument("-o", "--output", default="./output", help="Output directory")
    parser.add_argument("-n", "--namespace", default="MyApp", help="Target namespace")
    args = parser.parse_args()
    
    generator = DotNetGenerator(args.namespace, args.output)
    generated = generator.generate_all(args.parsed_dir)
    
    print(f"\nGenerated {len(generated)} files/components:")
    for name, path in list(generated.items())[:10]:
        print(f"  - {name}")
    if len(generated) > 10:
        print(f"  ... and {len(generated) - 10} more")
    
    print(f"\nOutput directory: {args.output}")
    print(f"See .work/reports/migration-report.md for details")


if __name__ == "__main__":
    main()
