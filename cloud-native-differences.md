# Cloud-Native .NET on AWS: Key Differences & Changes

## Overview

This document highlights the differences between a traditional .NET application deployment and an AWS Cloud-Native approach for the OutSystems migration.

---

## Traditional .NET vs Cloud-Native .NET Comparison

### Architecture Philosophy

| Aspect | Traditional .NET | Cloud-Native .NET (AWS) |
|--------|-----------------|------------------------|
| **Deployment Model** | VMs or bare metal servers | Containers (ECS/EKS) or Serverless (Lambda) |
| **Scaling** | Vertical (bigger servers) | Horizontal (more instances) |
| **State Management** | In-process session, local files | Externalized (Redis, S3, DynamoDB) |
| **Configuration** | Web.config, appsettings.json on disk | Environment variables, Secrets Manager, Parameter Store |
| **Infrastructure** | Manual provisioning, scripts | Infrastructure as Code (Terraform/CDK) |
| **Deployment** | Manual or basic CI/CD | Automated CI/CD with blue-green/canary |
| **Availability** | Single server or basic failover | Multi-AZ, auto-healing, self-recovering |
| **Monitoring** | Local logs, basic APM | Distributed tracing, centralized logging, metrics |

### Infrastructure Comparison

| Component | Traditional | Cloud-Native (AWS) |
|-----------|-------------|-------------------|
| **Compute** | IIS on Windows Server VM | ECS Fargate (serverless containers) |
| **Load Balancing** | Hardware LB or Windows NLB | Application Load Balancer (ALB) |
| **Database** | SQL Server on VM | RDS PostgreSQL/SQL Server (managed) |
| **Caching** | In-memory or local Redis | ElastiCache Redis (managed cluster) |
| **File Storage** | Local disk or NAS | S3 (object storage) |
| **Message Queue** | MSMQ or RabbitMQ on VM | SQS (managed) |
| **Secrets** | Config files, encrypted sections | AWS Secrets Manager |
| **SSL Certificates** | Manual renewal, IIS binding | ACM (auto-renewal) |
| **DNS** | On-prem DNS or registrar | Route 53 (managed) |
| **CDN** | None or third-party | CloudFront |
| **Firewall** | Hardware/Windows Firewall | Security Groups + WAF |

---

## Key AWS Services Mapping

### Core Services

| Purpose | AWS Service | Replaces |
|---------|-------------|----------|
| **Container Orchestration** | ECS Fargate | IIS/Windows Services |
| **Container Registry** | ECR | - |
| **Relational Database** | RDS | SQL Server on VM |
| **In-Memory Cache** | ElastiCache | Local Redis/Memcached |
| **Object Storage** | S3 | File system/NAS |
| **Message Queue** | SQS | MSMQ/RabbitMQ |
| **Pub/Sub** | SNS | - |
| **Workflow/BPM** | Step Functions | Windows Workflow Foundation |
| **Scheduled Jobs** | EventBridge + ECS/Lambda | Windows Task Scheduler |
| **Authentication** | Cognito | ASP.NET Identity on SQL |
| **API Management** | API Gateway | - |

### Operations & Security

| Purpose | AWS Service | Replaces |
|---------|-------------|----------|
| **Logging** | CloudWatch Logs | File-based logs, Event Viewer |
| **Metrics** | CloudWatch Metrics | Performance counters |
| **Tracing** | X-Ray | - |
| **Secrets** | Secrets Manager | Config files |
| **Configuration** | Parameter Store | appsettings.json |
| **SSL/TLS** | ACM | Manual certificates |
| **WAF** | AWS WAF | Hardware/software WAF |
| **DNS** | Route 53 | On-prem DNS |
| **CDN** | CloudFront | - |

---

## New Sections Added for Cloud-Native

### 1. Twelve-Factor App Compliance

Cloud-native apps follow the [12-Factor methodology](https://12factor.net/):

| Factor | Traditional Approach | Cloud-Native Implementation |
|--------|---------------------|----------------------------|
| **1. Codebase** | Multiple codebases, manual sync | Single repo, branch-based deploys |
| **2. Dependencies** | GAC, local DLLs | NuGet packages, Docker images |
| **3. Config** | Web.config, hardcoded | Environment vars, Secrets Manager |
| **4. Backing Services** | Tight coupling | Attached resources via connection strings |
| **5. Build, Release, Run** | Mixed stages | Strict separation in CI/CD |
| **6. Processes** | Stateful, sticky sessions | Stateless, external state store |
| **7. Port Binding** | IIS hosting | Self-contained Kestrel |
| **8. Concurrency** | Single process, threads | Multiple container instances |
| **9. Disposability** | Long startup, graceful shutdown rare | Fast startup, graceful SIGTERM handling |
| **10. Dev/Prod Parity** | Different configs, databases | Docker + LocalStack parity |
| **11. Logs** | File-based | Stdout to CloudWatch |
| **12. Admin Processes** | Remote desktop, manual scripts | ECS Run Task, Lambda |

### 2. Container-First Design

**Traditional:**
```
Windows Server → IIS → ASP.NET Application Pool → .NET App
```

**Cloud-Native:**
```
ECS Cluster → Fargate Task → Docker Container → Kestrel → .NET App
```

**Dockerfile Example:**
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/Company.App.API/Company.App.API.csproj", "Company.App.API/"]
RUN dotnet restore "Company.App.API/Company.App.API.csproj"
COPY src/ .
RUN dotnet build "Company.App.API/Company.App.API.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "Company.App.API/Company.App.API.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Company.App.API.dll"]
```

### 3. Infrastructure as Code (IaC)

**Traditional:** Manual server setup, documentation, runbooks

**Cloud-Native:** Everything defined in Terraform/CDK

```
infrastructure/
├── terraform/
│   ├── modules/
│   │   ├── vpc/           # Network infrastructure
│   │   ├── ecs/           # Container orchestration
│   │   ├── rds/           # Database
│   │   ├── elasticache/   # Caching
│   │   ├── cognito/       # Authentication
│   │   └── monitoring/    # Observability
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── prod/
```

### 4. Auto-Scaling

**Traditional:**
- Manual capacity planning
- Vertical scaling (bigger servers)
- Over-provisioning for peak loads

**Cloud-Native:**
- Automatic horizontal scaling based on metrics
- Scale to zero possible (Lambda)
- Pay for actual usage

```hcl
# Auto-scaling policy
resource "aws_appautoscaling_policy" "cpu" {
  policy_type = "TargetTrackingScaling"
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

### 5. Blue-Green Deployments

**Traditional:**
- Stop old version, start new version
- Downtime during deployment
- Rollback = redeploy old version

**Cloud-Native:**
- Two identical environments (blue/green)
- Instant traffic switch
- Instant rollback

```
Before Deployment:
[Users] → [ALB] → [Blue (v1.0)] ← Active
                  [Green (idle)]

During Deployment:
[Users] → [ALB] → [Blue (v1.0)]
                  [Green (v1.1)] ← Deployed, tested

After Switch:
[Users] → [ALB] → [Blue (v1.0)] ← Standby
                  [Green (v1.1)] ← Active
```

### 6. Distributed Tracing

**Traditional:**
- Log files on each server
- Manual correlation
- Limited visibility

**Cloud-Native (X-Ray):**
- Automatic trace propagation
- Service map visualization
- End-to-end request tracking

```csharp
// X-Ray integration
app.UseXRay("AppAPI");

// Automatic tracing of:
// - Incoming HTTP requests
// - Outgoing HTTP calls
// - Database queries
// - AWS SDK calls
```

### 7. Centralized Secrets Management

**Traditional:**
```xml
<!-- Web.config with encrypted sections -->
<connectionStrings configProtectionProvider="RsaProtectedConfigurationProvider">
  <EncryptedData>...</EncryptedData>
</connectionStrings>
```

**Cloud-Native:**
```csharp
// Secrets from AWS Secrets Manager
builder.Configuration.AddSecretsManager(region: "us-east-1");

// Task definition references
"secrets": [
  {
    "name": "ConnectionStrings__Default",
    "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:app/db-conn"
  }
]
```

### 8. Multi-AZ High Availability

**Traditional:**
- Single data center
- Manual failover procedures
- Extended downtime during failures

**Cloud-Native:**
- Automatic multi-AZ deployment
- Self-healing infrastructure
- Sub-minute failover

```
Region: us-east-1
├── AZ-a
│   ├── ECS Tasks (2)
│   ├── RDS Primary
│   └── ElastiCache Primary
├── AZ-b
│   ├── ECS Tasks (2)
│   ├── RDS Standby (sync replication)
│   └── ElastiCache Replica
└── AZ-c
    ├── ECS Tasks (2)
    └── ElastiCache Replica
```

### 9. Local Development Parity

**Traditional:**
- SQL Server Express locally
- Different config for dev
- "Works on my machine" issues

**Cloud-Native (Docker + LocalStack):**
```yaml
# docker-compose.yml
services:
  localstack:
    image: localstack/localstack:latest
    environment:
      - SERVICES=sqs,sns,s3,secretsmanager
    ports:
      - "4566:4566"

  postgres:
    image: postgres:16
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    environment:
      - AWS_SERVICE_URL=http://localstack:4566
    depends_on:
      - localstack
      - postgres
      - redis
```

### 10. Cost Optimization Features

**Traditional:**
- Fixed infrastructure costs
- Pay for idle capacity
- Difficult to right-size

**Cloud-Native:**

| Strategy | Savings |
|----------|---------|
| Fargate Spot for non-critical | 50-70% |
| RDS Reserved Instances | 30-50% |
| ElastiCache Reserved Nodes | 30-50% |
| S3 Intelligent Tiering | 20-40% |
| Auto-scaling (scale down) | Variable |

---

## Code-Level Differences

### Configuration

**Traditional:**
```csharp
// appsettings.json on disk
var connectionString = Configuration.GetConnectionString("Default");
```

**Cloud-Native:**
```csharp
// Environment variables + Secrets Manager
builder.Configuration
    .AddEnvironmentVariables()
    .AddSecretsManager(region: "us-east-1");

// Accessed the same way, but source is different
var connectionString = Configuration.GetConnectionString("Default");
```

### Session State

**Traditional:**
```csharp
// In-process session
services.AddSession();
// or SQL Server session
services.AddDistributedSqlServerCache();
```

**Cloud-Native:**
```csharp
// ElastiCache Redis
services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = Configuration["Redis:ConnectionString"];
});

services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
});
```

### File Storage

**Traditional:**
```csharp
// Local file system
var path = Path.Combine(_webHostEnvironment.WebRootPath, "uploads", fileName);
await using var stream = new FileStream(path, FileMode.Create);
await file.CopyToAsync(stream);
```

**Cloud-Native:**
```csharp
// S3
public async Task<string> UploadAsync(IFormFile file)
{
    var key = $"uploads/{Guid.NewGuid()}/{file.FileName}";
    
    await _s3Client.PutObjectAsync(new PutObjectRequest
    {
        BucketName = _bucketName,
        Key = key,
        InputStream = file.OpenReadStream(),
        ContentType = file.ContentType
    });
    
    return key;
}
```

### Background Jobs

**Traditional:**
```csharp
// Windows Service or Hangfire on same server
services.AddHangfire(config => config.UseSqlServerStorage(connectionString));
BackgroundJob.Schedule(() => CleanupOldOrders(), TimeSpan.FromDays(1));
```

**Cloud-Native:**
```csharp
// Option 1: EventBridge + ECS Task (for heavy jobs)
// Scheduled via Terraform, runs as separate container

// Option 2: Lambda (for lightweight jobs)
public class CleanupFunction
{
    public async Task Handler(ScheduledEvent evt, ILambdaContext context)
    {
        await _orderService.CleanupOldOrdersAsync();
    }
}

// Option 3: SQS + Worker Service (for queue-based)
public class OrderProcessor : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var messages = await _sqsClient.ReceiveMessageAsync(...);
            foreach (var msg in messages.Messages)
            {
                await ProcessAsync(msg);
                await _sqsClient.DeleteMessageAsync(...);
            }
        }
    }
}
```

### Logging

**Traditional:**
```csharp
// File-based logging
services.AddLogging(builder =>
{
    builder.AddFile("logs/app-{Date}.log");
});
```

**Cloud-Native:**
```csharp
// Stdout → CloudWatch Logs
services.AddLogging(builder =>
{
    builder.AddConsole();  // Stdout captured by CloudWatch
    builder.AddAWSProvider(Configuration.GetAWSLoggingConfigSection());
});

// Structured logging with correlation
using (LogContext.PushProperty("CorrelationId", correlationId))
{
    _logger.LogInformation("Processing order {OrderId}", orderId);
}
```

### Health Checks

**Traditional:**
```csharp
// Basic endpoint
app.MapGet("/health", () => "OK");
```

**Cloud-Native:**
```csharp
// Comprehensive health checks for ALB/ECS
services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "database", tags: new[] { "ready" })
    .AddRedis(redisConnection, name: "redis", tags: new[] { "ready" })
    .AddUrlGroup(new Uri(externalApiUrl), name: "external-api", tags: new[] { "ready" });

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false  // Just checks if app is running
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});
```

---

## Operational Differences

### Deployment

| Aspect | Traditional | Cloud-Native |
|--------|-------------|--------------|
| **Method** | xcopy, Web Deploy, manual | CI/CD pipeline |
| **Downtime** | Minutes to hours | Zero (blue-green) |
| **Rollback** | Manual redeploy | Instant switch |
| **Approval** | Email/ticket | GitHub PR approval |
| **Audit** | Manual logs | Automated trail |

### Monitoring

| Aspect | Traditional | Cloud-Native |
|--------|-------------|--------------|
| **Logs** | RDP to server, Event Viewer | CloudWatch Logs Insights |
| **Metrics** | Performance counters | CloudWatch Metrics + Dashboards |
| **Alerting** | Email from monitoring tool | CloudWatch Alarms → SNS → PagerDuty |
| **Tracing** | Manual log correlation | X-Ray service map |
| **Cost** | Estimated | AWS Cost Explorer, detailed |

### Disaster Recovery

| Aspect | Traditional | Cloud-Native |
|--------|-------------|--------------|
| **Backup** | Nightly scripts, tape | Automated RDS snapshots, S3 versioning |
| **Recovery** | Hours to days | Minutes to hours |
| **DR Site** | Cold/warm standby | Pilot light, multi-region |
| **Failover** | Manual | Automatic (Route 53 health checks) |
| **Testing** | Annual DR tests | Regular chaos engineering |

---

## Migration Effort Delta

### Additional Tasks for Cloud-Native

| Task | Effort | Priority |
|------|--------|----------|
| Containerize application | 2-3 days | High |
| Set up Terraform modules | 3-5 days | High |
| Configure CI/CD pipelines | 2-3 days | High |
| Implement health checks | 1 day | High |
| Externalize session to Redis | 1-2 days | High |
| Migrate file storage to S3 | 1-2 days | Medium |
| Set up CloudWatch dashboards | 1-2 days | Medium |
| Configure auto-scaling | 1 day | Medium |
| Implement X-Ray tracing | 1 day | Medium |
| Set up LocalStack for dev | 1 day | Medium |
| Configure WAF rules | 1 day | Medium |
| Set up Cognito (if using) | 2-3 days | Conditional |
| Blue-green deployment setup | 1-2 days | Low (can do later) |

### Total Additional Effort: 15-25 days

---

## Summary: Why Cloud-Native?

| Benefit | Impact |
|---------|--------|
| **Scalability** | Handle 10x traffic without re-architecture |
| **Reliability** | 99.9%+ uptime with multi-AZ |
| **Cost Efficiency** | Pay for what you use, not peak capacity |
| **Developer Productivity** | Fast deployments, easy rollbacks |
| **Security** | Managed services, automatic patching |
| **Operational Excellence** | Less ops burden, more automation |
| **Future-Proof** | Easy to adopt new services, patterns |

---

*Document Version: 1.0*  
*Created: 2026-07-22*
