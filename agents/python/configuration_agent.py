"""
Configuration Agent - Pure Python Implementation
Execution: Python (No LLM Required)

Purpose: Generate .NET project configuration files from templates.
Generates appsettings.json, Dockerfile, docker-compose.yml, and project files.
"""

import json
import os
from typing import Dict, List, Optional, Any
from string import Template
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.types import ParsedModule, AnalysisResult


class ConfigurationAgent:
    """
    Pure Python agent - No LLM required.
    Generates configuration files using templates.
    """
    
    def __init__(self, target_namespace: str = "MyApp"):
        self.namespace = target_namespace
        self.templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    
    def generate_all(
        self,
        modules: Dict[str, ParsedModule],
        analysis: AnalysisResult,
        output_dir: str,
        config: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Generate all configuration files."""
        config = config or {}
        os.makedirs(output_dir, exist_ok=True)
        
        generated = {}
        
        generated["appsettings.json"] = self._generate_appsettings(modules, output_dir, config)
        generated["appsettings.Development.json"] = self._generate_appsettings_dev(output_dir, config)
        generated["Dockerfile"] = self._generate_dockerfile(output_dir, config)
        generated["docker-compose.yml"] = self._generate_docker_compose(output_dir, config)
        generated[f"{self.namespace}.csproj"] = self._generate_csproj(modules, output_dir, config)
        generated["Program.cs"] = self._generate_program_cs(modules, output_dir)
        generated["Directory.Build.props"] = self._generate_directory_build_props(output_dir)
        
        return generated
    
    def _generate_appsettings(
        self,
        modules: Dict[str, ParsedModule],
        output_dir: str,
        config: Dict
    ) -> str:
        """Generate appsettings.json."""
        site_properties = {}
        for module in modules.values():
            for prop in module.site_properties:
                key = f"{module.module_name}:{prop['name']}"
                site_properties[key] = prop.get("default_value", "")
        
        external_apis = {}
        for module in modules.values():
            for rest in module.rest_consumes:
                api_name = rest.get("name", "UnknownAPI")
                external_apis[api_name] = {
                    "BaseUrl": rest.get("base_url", "https://api.example.com"),
                    "Timeout": 30
                }
        
        settings = {
            "Logging": {
                "LogLevel": {
                    "Default": "Information",
                    "Microsoft.AspNetCore": "Warning",
                    "Microsoft.EntityFrameworkCore": "Warning"
                }
            },
            "AllowedHosts": "*",
            "ConnectionStrings": {
                "DefaultConnection": config.get(
                    "connection_string",
                    "Server=localhost;Database=MyApp;Trusted_Connection=True;TrustServerCertificate=True"
                )
            },
            "Jwt": {
                "Issuer": config.get("jwt_issuer", "MyApp"),
                "Audience": config.get("jwt_audience", "MyApp.Users"),
                "ExpirationMinutes": 60,
                "Secret": "YOUR-SECRET-KEY-REPLACE-IN-PRODUCTION-MIN-32-CHARS"
            },
            "SiteProperties": site_properties,
            "ExternalApis": external_apis,
            "FeatureFlags": {
                "EnableSwagger": True,
                "EnableHealthChecks": True
            }
        }
        
        output_path = os.path.join(output_dir, "appsettings.json")
        with open(output_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        return output_path
    
    def _generate_appsettings_dev(self, output_dir: str, config: Dict) -> str:
        """Generate appsettings.Development.json."""
        settings = {
            "Logging": {
                "LogLevel": {
                    "Default": "Debug",
                    "Microsoft.AspNetCore": "Information",
                    "Microsoft.EntityFrameworkCore": "Information"
                }
            },
            "ConnectionStrings": {
                "DefaultConnection": "Server=localhost;Database=MyApp_Dev;Trusted_Connection=True;TrustServerCertificate=True"
            },
            "Jwt": {
                "Secret": "DEV-ONLY-SECRET-KEY-DO-NOT-USE-IN-PRODUCTION"
            }
        }
        
        output_path = os.path.join(output_dir, "appsettings.Development.json")
        with open(output_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        return output_path
    
    def _generate_dockerfile(self, output_dir: str, config: Dict) -> str:
        """Generate Dockerfile."""
        dotnet_version = config.get("dotnet_version", "8.0")
        
        dockerfile = f"""# Build stage
FROM mcr.microsoft.com/dotnet/sdk:{dotnet_version} AS build
WORKDIR /src

# Copy project file and restore
COPY ["*.csproj", "./"]
RUN dotnet restore

# Copy all files and build
COPY . .
RUN dotnet publish -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:{dotnet_version} AS runtime
WORKDIR /app

# Install health check dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy published app
COPY --from=build /app/publish .

# Configure environment
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Run as non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080
ENTRYPOINT ["dotnet", "{self.namespace}.dll"]
"""
        
        output_path = os.path.join(output_dir, "Dockerfile")
        with open(output_path, 'w') as f:
            f.write(dockerfile)
        
        return output_path
    
    def _generate_docker_compose(self, output_dir: str, config: Dict) -> str:
        """Generate docker-compose.yml."""
        compose = f"""version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__DefaultConnection=Server=db;Database={self.namespace};User=sa;Password=YourStrong!Passw0rd;TrustServerCertificate=True
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=YourStrong!Passw0rd
      - MSSQL_PID=Developer
    ports:
      - "1433:1433"
    volumes:
      - sqldata:/var/opt/mssql
    healthcheck:
      test: /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "YourStrong!Passw0rd" -C -Q "SELECT 1" || exit 1
      interval: 10s
      timeout: 3s
      retries: 10
      start_period: 10s
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  sqldata:
  redisdata:

networks:
  app-network:
    driver: bridge
"""
        
        output_path = os.path.join(output_dir, "docker-compose.yml")
        with open(output_path, 'w') as f:
            f.write(compose)
        
        return output_path
    
    def _generate_csproj(
        self,
        modules: Dict[str, ParsedModule],
        output_dir: str,
        config: Dict
    ) -> str:
        """Generate .csproj file."""
        dotnet_version = config.get("dotnet_version", "8.0")
        
        has_timers = any(m.timers for m in modules.values())
        has_rest = any(m.rest_consumes or m.rest_exposes for m in modules.values())
        
        packages = [
            ("Microsoft.EntityFrameworkCore.SqlServer", "8.0.0"),
            ("Microsoft.EntityFrameworkCore.Tools", "8.0.0"),
            ("Microsoft.AspNetCore.Authentication.JwtBearer", "8.0.0"),
            ("Swashbuckle.AspNetCore", "6.5.0"),
            ("Serilog.AspNetCore", "8.0.0"),
            ("FluentValidation.AspNetCore", "11.3.0"),
            ("AutoMapper.Extensions.Microsoft.DependencyInjection", "12.0.1"),
            ("AspNetCore.HealthChecks.SqlServer", "8.0.0"),
        ]
        
        if has_timers:
            packages.append(("Hangfire.AspNetCore", "1.8.6"))
            packages.append(("Hangfire.SqlServer", "1.8.6"))
        
        if has_rest:
            packages.append(("Refit.HttpClientFactory", "7.0.0"))
            packages.append(("Polly", "8.2.0"))
        
        package_refs = "\n    ".join([
            f'<PackageReference Include="{name}" Version="{version}" />'
            for name, version in packages
        ])
        
        csproj = f"""<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net{dotnet_version}</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RootNamespace>{self.namespace}</RootNamespace>
    <AssemblyName>{self.namespace}</AssemblyName>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>

  <ItemGroup>
    {package_refs}
  </ItemGroup>

  <ItemGroup>
    <InternalsVisibleTo Include="{self.namespace}.Tests" />
  </ItemGroup>

</Project>
"""
        
        output_path = os.path.join(output_dir, f"{self.namespace}.csproj")
        with open(output_path, 'w') as f:
            f.write(csproj)
        
        return output_path
    
    def _generate_program_cs(
        self,
        modules: Dict[str, ParsedModule],
        output_dir: str
    ) -> str:
        """Generate Program.cs."""
        has_timers = any(m.timers for m in modules.values())
        
        hangfire_config = ""
        if has_timers:
            hangfire_config = """
// Hangfire for background jobs
builder.Services.AddHangfire(config => config
    .SetDataCompatibilityLevel(CompatibilityLevel.Version_180)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings()
    .UseSqlServerStorage(builder.Configuration.GetConnectionString("DefaultConnection")));
builder.Services.AddHangfireServer();
"""

        hangfire_middleware = ""
        if has_timers:
            hangfire_middleware = """
// Hangfire dashboard
app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new[] { new HangfireAuthorizationFilter() }
});
"""

        program_cs = f"""using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using Serilog;
using FluentValidation;
using {self.namespace}.Data;
using {self.namespace}.Services;
{"using Hangfire;" if has_timers else ""}

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

// Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {{
        options.TokenValidationParameters = new TokenValidationParameters
        {{
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Secret"]!))
        }};
    }});

builder.Services.AddAuthorization();

// AutoMapper
builder.Services.AddAutoMapper(typeof(Program));

// FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// Services
builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();
// TODO: Register generated services

// HttpClient for external APIs
builder.Services.AddHttpClient();

// Controllers
builder.Services.AddControllers();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{{
    c.SwaggerDoc("v1", new() {{ Title = "{self.namespace} API", Version = "v1" }});
}});

// Health checks
builder.Services.AddHealthChecks()
    .AddSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")!);
{hangfire_config}
var app = builder.Build();

// Middleware pipeline
if (app.Environment.IsDevelopment())
{{
    app.UseSwagger();
    app.UseSwaggerUI();
}}

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
{hangfire_middleware}
app.MapControllers();
app.MapHealthChecks("/health");

// Apply migrations
using (var scope = app.Services.CreateScope())
{{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}}

app.Run();
"""
        
        output_path = os.path.join(output_dir, "Program.cs")
        with open(output_path, 'w') as f:
            f.write(program_cs)
        
        return output_path
    
    def _generate_directory_build_props(self, output_dir: str) -> str:
        """Generate Directory.Build.props for solution-wide settings."""
        props = """<Project>
  <PropertyGroup>
    <LangVersion>latest</LangVersion>
    <EnableNETAnalyzers>true</EnableNETAnalyzers>
    <AnalysisLevel>latest</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  </PropertyGroup>
</Project>
"""
        
        output_path = os.path.join(output_dir, "Directory.Build.props")
        with open(output_path, 'w') as f:
            f.write(props)
        
        return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate .NET configuration files")
    parser.add_argument("input_dir", help="Directory with parsed JSON files")
    parser.add_argument("-o", "--output", default="./output", help="Output directory")
    parser.add_argument("-n", "--namespace", default="MyApp", help="Target namespace")
    args = parser.parse_args()
    
    from models.types import ParsedModule
    
    modules = {}
    for filename in os.listdir(args.input_dir):
        if filename.endswith(".json") and not filename.startswith("_"):
            filepath = os.path.join(args.input_dir, filename)
            with open(filepath) as f:
                data = json.load(f)
                module = ParsedModule(**data)
                modules[module.module_name] = module
    
    agent = ConfigurationAgent(target_namespace=args.namespace)
    generated = agent.generate_all(modules, None, args.output)
    
    print(f"Generated {len(generated)} configuration files:")
    for name, path in generated.items():
        print(f"  - {name}: {path}")
