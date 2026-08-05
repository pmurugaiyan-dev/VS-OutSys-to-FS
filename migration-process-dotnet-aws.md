# OutSystems to .NET Migration Process (AWS Cloud-Native)

## Comprehensive Step-by-Step Guide for AWS Deployment

---

## Table of Contents

1. [Phase 1: Discovery & Assessment](#phase-1-discovery--assessment)
2. [Phase 2: Cloud-Native Architecture Design](#phase-2-cloud-native-architecture-design)
3. [Phase 3: AWS Infrastructure Setup](#phase-3-aws-infrastructure-setup)
4. [Phase 4: Data Layer Migration](#phase-4-data-layer-migration)
5. [Phase 5: Business Logic Migration](#phase-5-business-logic-migration)
6. [Phase 6: User Interface Migration](#phase-6-user-interface-migration)
7. [Phase 7: Integration Migration](#phase-7-integration-migration)
8. [Phase 8: Security Implementation](#phase-8-security-implementation)
9. [Phase 9: Cross-Cutting Concerns](#phase-9-cross-cutting-concerns)
10. [Phase 10: Testing & Validation](#phase-10-testing--validation)
11. [Phase 11: AWS Deployment & Go-Live](#phase-11-aws-deployment--go-live)
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

### 1.3 Cloud-Native Readiness Assessment

| Factor | Assessment Questions | Impact on Design |
|--------|---------------------|------------------|
| **Scalability** | Peak users? Traffic patterns? | Auto-scaling config |
| **Statelessness** | Session dependencies? | Redis/DynamoDB for state |
| **Data Volume** | DB size? Growth rate? | RDS sizing, read replicas |
| **Integrations** | Sync vs async? Latency needs? | API Gateway, SQS/SNS |
| **Compliance** | HIPAA, PCI, SOC2? | AWS compliance services |
| **Region** | User locations? Data residency? | Multi-region strategy |

### 1.4 Complexity Assessment

```
Complexity Score Calculation:
- Entities: count × 1 point
- Screens: count × 2 points
- Server Actions: count × 1.5 points
- Client Actions: count × 1 point
- Integrations: count × 3 points
- BPT Processes: count × 5 points
- Extensions: count × 4 points

Low: < 100 points → Single ECS Service
Medium: 100-500 points → Multiple ECS Services
High: 500-1000 points → EKS Microservices
Very High: > 1000 points → EKS + Serverless Hybrid
```

---

## Phase 2: Cloud-Native Architecture Design

### 2.1 AWS Cloud-Native Architecture Patterns

| Pattern | When to Use | AWS Services |
|---------|-------------|--------------|
| **Containerized Monolith** | Small-medium apps, team learning containers | ECS Fargate, single service |
| **Microservices on ECS** | Medium apps, independent scaling | ECS Fargate, multiple services |
| **Microservices on EKS** | Large apps, K8s expertise, multi-cloud | EKS, Helm charts |
| **Serverless-First** | Event-driven, variable load | Lambda, API Gateway, Step Functions |
| **Hybrid** | Mixed workloads | ECS + Lambda for specific functions |

### 2.2 Recommended AWS Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS Cloud                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         VPC (Multi-AZ)                               │   │
│  │                                                                      │   │
│  │   ┌──────────┐    ┌──────────────────────────────────────────────┐  │   │
│  │   │ Route 53 │───▶│            Application Load Balancer          │  │   │
│  │   └──────────┘    └──────────────────────────────────────────────┘  │   │
│  │                                    │                                 │   │
│  │         ┌──────────────────────────┼──────────────────────────┐     │   │
│  │         ▼                          ▼                          ▼     │   │
│  │   ┌───────────┐            ┌───────────┐             ┌───────────┐  │   │
│  │   │   ECS     │            │   ECS     │             │   ECS     │  │   │
│  │   │ Service A │            │ Service B │             │ Service C │  │   │
│  │   │ (API)     │            │ (Workers) │             │ (Frontend)│  │   │
│  │   └─────┬─────┘            └─────┬─────┘             └───────────┘  │   │
│  │         │                        │                                   │   │
│  │         ▼                        ▼                                   │   │
│  │   ┌───────────┐            ┌───────────┐                            │   │
│  │   │ RDS       │            │ ElastiCache│                           │   │
│  │   │ PostgreSQL│            │ Redis      │                           │   │
│  │   │ (Multi-AZ)│            │ (Cluster)  │                           │   │
│  │   └───────────┘            └───────────┘                            │   │
│  │                                                                      │   │
│  │   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │   │
│  │   │    SQS    │  │    SNS    │  │    S3     │  │ Secrets   │       │   │
│  │   │  Queues   │  │  Topics   │  │  Buckets  │  │ Manager   │       │   │
│  │   └───────────┘  └───────────┘  └───────────┘  └───────────┘       │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│   │CloudWatch │  │  X-Ray    │  │  Cognito  │  │    WAF    │              │
│   │Logs/Metrics│ │ Tracing   │  │   Auth    │  │ Firewall  │              │
│   └───────────┘  └───────────┘  └───────────┘  └───────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Technology Stack Definition (AWS Cloud-Native)

| Layer | Technology | AWS Service |
|-------|------------|-------------|
| **Runtime** | .NET 8.0 LTS | - |
| **Web Framework** | ASP.NET Core 8.0 | - |
| **Frontend** | Blazor WebAssembly / React | CloudFront + S3 |
| **Container Runtime** | Docker | ECS Fargate / EKS |
| **Container Registry** | Docker images | ECR |
| **Database** | PostgreSQL / SQL Server | RDS (Multi-AZ) |
| **Caching** | Redis | ElastiCache |
| **Message Queue** | SQS / SNS | Managed |
| **File Storage** | S3 | Managed |
| **Secrets** | AWS Secrets Manager | Managed |
| **Authentication** | Amazon Cognito | Managed |
| **API Gateway** | Amazon API Gateway | Managed |
| **CDN** | CloudFront | Managed |
| **DNS** | Route 53 | Managed |
| **Monitoring** | CloudWatch + X-Ray | Managed |
| **IaC** | Terraform / CDK | - |

### 2.4 Project Structure (Cloud-Native)

```
Solution/
├── src/
│   ├── Company.App.Domain/              # Entities, Value Objects
│   ├── Company.App.Application/         # Use Cases, DTOs, Interfaces
│   ├── Company.App.Infrastructure/      # EF Core, AWS SDKs, Repositories
│   │   ├── Persistence/
│   │   ├── AWS/
│   │   │   ├── S3/
│   │   │   ├── SQS/
│   │   │   ├── SNS/
│   │   │   ├── SecretsManager/
│   │   │   └── Cognito/
│   │   └── External/
│   ├── Company.App.API/                 # ASP.NET Core Web API
│   ├── Company.App.Web/                 # Blazor / React Frontend
│   ├── Company.App.Workers/             # Background job processors
│   └── Company.App.Lambda/              # Serverless functions (optional)
├── tests/
│   ├── Company.App.UnitTests/
│   ├── Company.App.IntegrationTests/
│   └── Company.App.E2ETests/
├── infrastructure/
│   ├── terraform/                       # Or CDK
│   │   ├── modules/
│   │   │   ├── vpc/
│   │   │   ├── ecs/
│   │   │   ├── rds/
│   │   │   ├── elasticache/
│   │   │   └── monitoring/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── prod/
│   │   └── main.tf
│   └── docker/
│       ├── Dockerfile.api
│       ├── Dockerfile.web
│       └── Dockerfile.workers
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd-dev.yml
│       ├── cd-staging.yml
│       └── cd-prod.yml
└── docs/
```

### 2.5 Twelve-Factor App Compliance

| Factor | Implementation |
|--------|---------------|
| **1. Codebase** | Single repo, multiple deploys via branches |
| **2. Dependencies** | NuGet packages, Docker base images |
| **3. Config** | Environment variables, Secrets Manager, Parameter Store |
| **4. Backing Services** | RDS, ElastiCache, SQS as attached resources |
| **5. Build, Release, Run** | CI/CD pipeline separates stages |
| **6. Processes** | Stateless containers, state in Redis/RDS |
| **7. Port Binding** | Self-contained via Kestrel |
| **8. Concurrency** | Horizontal scaling via ECS tasks |
| **9. Disposability** | Fast startup/shutdown, graceful termination |
| **10. Dev/Prod Parity** | Docker + LocalStack for local dev |
| **11. Logs** | Stdout → CloudWatch Logs |
| **12. Admin Processes** | ECS Run Task for one-off jobs |

---

## Phase 3: AWS Infrastructure Setup

### 3.1 AWS Account Structure

| Account | Purpose | Environment |
|---------|---------|-------------|
| **Management** | AWS Organizations, billing | - |
| **Shared Services** | ECR, shared networking, CI/CD | All |
| **Development** | Dev workloads | Dev |
| **Staging** | Pre-prod testing | Staging |
| **Production** | Live workloads | Prod |

### 3.2 VPC Design

```hcl
# Terraform VPC Module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "app-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]

  enable_nat_gateway     = true
  single_nat_gateway     = false  # One per AZ for HA
  enable_dns_hostnames   = true
  enable_dns_support     = true

  # VPC Flow Logs
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true

  tags = {
    Environment = var.environment
    Project     = "outsystems-migration"
  }
}
```

### 3.3 ECS Fargate Cluster Setup

```hcl
# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "app-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs_exec.name
      }
    }
  }
}

# ECS Service
resource "aws_ecs_service" "api" {
  name            = "api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8080
  }

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
}

# Task Definition
resource "aws_ecs_task_definition" "api" {
  family                   = "api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
      
      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "ASPNETCORE_ENVIRONMENT", value = var.environment },
        { name = "AWS_REGION", value = var.aws_region }
      ]

      secrets = [
        { name = "ConnectionStrings__Default", valueFrom = "${aws_secretsmanager_secret.db_connection.arn}" },
        { name = "Jwt__Key", valueFrom = "${aws_secretsmanager_secret.jwt_key.arn}" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.api.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "api"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}
```

### 3.4 RDS PostgreSQL Setup

```hcl
# RDS PostgreSQL
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "app-db"

  engine               = "postgres"
  engine_version       = "16.1"
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = var.db_instance_class

  allocated_storage     = 100
  max_allocated_storage = 500
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  db_name  = "appdb"
  username = "appuser"
  port     = 5432

  # Credentials from Secrets Manager
  manage_master_user_password = true

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  vpc_security_group_ids = [aws_security_group.rds.id]

  maintenance_window      = "Sun:03:00-Sun:04:00"
  backup_window           = "02:00-03:00"
  backup_retention_period = 30
  deletion_protection     = true

  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  create_monitoring_role                = true
  monitoring_interval                   = 60

  parameters = [
    {
      name  = "log_statement"
      value = "all"
    },
    {
      name  = "log_min_duration_statement"
      value = "1000"  # Log queries > 1 second
    }
  ]

  tags = {
    Environment = var.environment
  }
}
```

### 3.5 ElastiCache Redis Setup

```hcl
# ElastiCache Redis Cluster
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "app-redis"
  description                = "Redis cluster for session and caching"
  
  engine                     = "redis"
  engine_version             = "7.1"
  node_type                  = var.redis_node_type
  num_cache_clusters         = 2
  port                       = 6379
  
  parameter_group_name       = aws_elasticache_parameter_group.redis.name
  subnet_group_name          = aws_elasticache_subnet_group.redis.name
  security_group_ids         = [aws_security_group.redis.id]
  
  automatic_failover_enabled = true
  multi_az_enabled           = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_auth.result
  
  snapshot_retention_limit   = 7
  snapshot_window            = "03:00-05:00"
  maintenance_window         = "sun:05:00-sun:06:00"

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
  }

  tags = {
    Environment = var.environment
  }
}
```

### 3.6 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/cd-prod.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: app-api
  ECS_SERVICE: api-service
  ECS_CLUSTER: app-cluster
  CONTAINER_NAME: api

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.build-image.outputs.image }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2
      
      - name: Build, tag, and push image
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -f docker/Dockerfile.api .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Download task definition
        run: |
          aws ecs describe-task-definition --task-definition api \
            --query taskDefinition > task-definition.json
      
      - name: Update task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ needs.build-and-push.outputs.image }}
      
      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true
```

### 3.7 Local Development with LocalStack

```yaml
# docker-compose.yml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=sqs,sns,s3,secretsmanager,dynamodb
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
    volumes:
      - localstack_data:/tmp/localstack

  postgres:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_SERVICE_URL=http://localstack:4566
      - ConnectionStrings__Default=Host=postgres;Database=appdb;Username=appuser;Password=devpassword
      - Redis__ConnectionString=redis:6379
    depends_on:
      - localstack
      - postgres
      - redis

volumes:
  localstack_data:
  postgres_data:
```

---

## Phase 4: Data Layer Migration

### 4.1 Entity Migration (Same as base document)

Refer to base `migration-process-dotnet.md` for entity mapping details.

### 4.2 AWS-Specific Data Configurations

```csharp
// Program.cs - AWS configuration
builder.Services.AddDbContext<ApplicationDbContext>((serviceProvider, options) =>
{
    var configuration = serviceProvider.GetRequiredService<IConfiguration>();
    var connectionString = configuration.GetConnectionString("Default");
    
    options.UseNpgsql(connectionString, npgsqlOptions =>
    {
        npgsqlOptions.EnableRetryOnFailure(
            maxRetryCount: 5,
            maxRetryDelay: TimeSpan.FromSeconds(30),
            errorCodesToAdd: null);
        npgsqlOptions.CommandTimeout(30);
    });
});

// Health check for RDS
builder.Services.AddHealthChecks()
    .AddNpgSql(
        connectionString: builder.Configuration.GetConnectionString("Default"),
        name: "rds-postgres",
        tags: new[] { "db", "ready" });
```

### 4.3 Database Migration Strategy for RDS

| Step | Action | AWS Tools |
|------|--------|-----------|
| 1 | Create RDS snapshot of source (if applicable) | RDS Snapshots |
| 2 | Set up DMS replication instance | AWS DMS |
| 3 | Configure source and target endpoints | DMS Endpoints |
| 4 | Create migration task | DMS Task |
| 5 | Run full load migration | DMS Full Load |
| 6 | Enable CDC for ongoing sync | DMS CDC |
| 7 | Validate data | DMS Validation |
| 8 | Cutover | Stop DMS, switch apps |

```hcl
# AWS DMS for data migration
resource "aws_dms_replication_instance" "migration" {
  replication_instance_id     = "app-migration"
  replication_instance_class  = "dms.r5.large"
  allocated_storage           = 100
  vpc_security_group_ids      = [aws_security_group.dms.id]
  replication_subnet_group_id = aws_dms_replication_subnet_group.main.id
  multi_az                    = true
  publicly_accessible         = false
}

resource "aws_dms_endpoint" "source" {
  endpoint_id   = "outsystems-source"
  endpoint_type = "source"
  engine_name   = "sqlserver"  # OutSystems typically uses SQL Server
  server_name   = var.source_db_host
  port          = 1433
  database_name = var.source_db_name
  username      = var.source_db_user
  password      = var.source_db_password
}

resource "aws_dms_endpoint" "target" {
  endpoint_id   = "rds-target"
  endpoint_type = "target"
  engine_name   = "postgres"
  server_name   = module.rds.db_instance_address
  port          = 5432
  database_name = "appdb"
  username      = "appuser"
  password      = var.db_password
}
```

---

## Phase 5: Business Logic Migration

### 5.1 Server Action Migration (Same patterns as base document)

### 5.2 Timer/Scheduled Job Migration with AWS

| OutSystems Timer | AWS Cloud-Native Option |
|-----------------|------------------------|
| Timer (scheduled) | EventBridge Scheduler + Lambda / ECS Task |
| Timer (wake) | SQS + ECS Worker |
| BPT Wait | Step Functions Wait state |

**EventBridge Scheduled Task:**
```hcl
# EventBridge rule for scheduled tasks
resource "aws_cloudwatch_event_rule" "order_cleanup" {
  name                = "order-cleanup-daily"
  description         = "Trigger order cleanup at 2 AM UTC"
  schedule_expression = "cron(0 2 * * ? *)"
}

resource "aws_cloudwatch_event_target" "order_cleanup" {
  rule      = aws_cloudwatch_event_rule.order_cleanup.name
  target_id = "OrderCleanupTask"
  arn       = aws_ecs_cluster.main.arn
  role_arn  = aws_iam_role.eventbridge_ecs.arn

  ecs_target {
    task_definition_arn = aws_ecs_task_definition.workers.arn
    task_count          = 1
    launch_type         = "FARGATE"

    network_configuration {
      subnets          = module.vpc.private_subnets
      security_groups  = [aws_security_group.ecs_tasks.id]
      assign_public_ip = false
    }
  }

  input = jsonencode({
    containerOverrides = [
      {
        name    = "worker"
        command = ["dotnet", "Company.App.Workers.dll", "--job", "OrderCleanup"]
      }
    ]
  })
}
```

**Lambda for Lightweight Jobs:**
```csharp
// Lambda function handler
public class OrderCleanupFunction
{
    private readonly IOrderService _orderService;

    public OrderCleanupFunction()
    {
        var services = new ServiceCollection();
        ConfigureServices(services);
        var provider = services.BuildServiceProvider();
        _orderService = provider.GetRequiredService<IOrderService>();
    }

    public async Task<string> FunctionHandler(ScheduledEvent input, ILambdaContext context)
    {
        context.Logger.LogInformation($"Starting order cleanup at {DateTime.UtcNow}");
        
        var cancelledCount = await _orderService.CleanupAbandonedOrdersAsync(TimeSpan.FromDays(30));
        
        return $"Cleaned up {cancelledCount} orders";
    }
}
```

### 5.3 BPT Process Migration with Step Functions

```json
{
  "Comment": "Order Approval Workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:ValidateOrder",
      "Next": "CheckApprovalRequired"
    },
    "CheckApprovalRequired": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.requiresApproval",
          "BooleanEquals": true,
          "Next": "RequestApproval"
        }
      ],
      "Default": "ProcessPayment"
    },
    "RequestApproval": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
      "Parameters": {
        "QueueUrl": "${ApprovalQueueUrl}",
        "MessageBody": {
          "orderId.$": "$.orderId",
          "taskToken.$": "$$.Task.Token"
        }
      },
      "TimeoutSeconds": 86400,
      "Next": "CheckApprovalDecision"
    },
    "CheckApprovalDecision": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.approved",
          "BooleanEquals": true,
          "Next": "ProcessPayment"
        }
      ],
      "Default": "OrderRejected"
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:ProcessPayment",
      "Next": "FulfillOrder"
    },
    "FulfillOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:FulfillOrder",
      "Next": "SendConfirmation"
    },
    "SendConfirmation": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:SendConfirmation",
      "End": true
    },
    "OrderRejected": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789:function:NotifyRejection",
      "End": true
    }
  }
}
```

---

## Phase 6: User Interface Migration

### 6.1 Frontend Hosting on AWS

| Option | AWS Services | Best For |
|--------|--------------|----------|
| **Blazor Server** | ECS Fargate | Real-time, server-rendered |
| **Blazor WASM** | S3 + CloudFront | Static SPA, offline capable |
| **React SPA** | S3 + CloudFront | Complex UI, large team |

**CloudFront + S3 for SPA:**
```hcl
# S3 bucket for frontend
resource "aws_s3_bucket" "frontend" {
  bucket = "app-frontend-${var.environment}"
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"  # SPA routing
  }
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"
  aliases             = [var.domain_name]

  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "S3Origin"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3Origin"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  # SPA routing - return index.html for 404s
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.frontend.arn
    ssl_support_method  = "sni-only"
  }
}
```

---

## Phase 7: Integration Migration

### 7.1 REST API with API Gateway

```hcl
# API Gateway
resource "aws_apigatewayv2_api" "main" {
  name          = "app-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = var.cors_origins
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 3600
  }
}

resource "aws_apigatewayv2_integration" "ecs" {
  api_id             = aws_apigatewayv2_api.main.id
  integration_type   = "HTTP_PROXY"
  integration_uri    = aws_lb_listener.api.arn
  integration_method = "ANY"
  connection_type    = "VPC_LINK"
  connection_id      = aws_apigatewayv2_vpc_link.main.id
}

resource "aws_apigatewayv2_route" "api" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "ANY /api/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.ecs.id}"
}
```

### 7.2 Message Queue with SQS/SNS

```csharp
// SQS Producer
public class SqsMessagePublisher : IMessagePublisher
{
    private readonly IAmazonSQS _sqsClient;
    private readonly ILogger<SqsMessagePublisher> _logger;
    private readonly string _queueUrl;

    public SqsMessagePublisher(IAmazonSQS sqsClient, IConfiguration config, ILogger<SqsMessagePublisher> logger)
    {
        _sqsClient = sqsClient;
        _logger = logger;
        _queueUrl = config["AWS:SQS:OrderQueueUrl"];
    }

    public async Task PublishAsync<T>(T message, CancellationToken cancellationToken = default)
    {
        var request = new SendMessageRequest
        {
            QueueUrl = _queueUrl,
            MessageBody = JsonSerializer.Serialize(message),
            MessageAttributes = new Dictionary<string, MessageAttributeValue>
            {
                ["MessageType"] = new MessageAttributeValue
                {
                    DataType = "String",
                    StringValue = typeof(T).Name
                }
            }
        };

        await _sqsClient.SendMessageAsync(request, cancellationToken);
        _logger.LogInformation("Message published to SQS: {MessageType}", typeof(T).Name);
    }
}

// SQS Consumer (Background Service)
public class SqsMessageConsumer : BackgroundService
{
    private readonly IAmazonSQS _sqsClient;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<SqsMessageConsumer> _logger;
    private readonly string _queueUrl;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var request = new ReceiveMessageRequest
            {
                QueueUrl = _queueUrl,
                MaxNumberOfMessages = 10,
                WaitTimeSeconds = 20,  // Long polling
                MessageAttributeNames = new List<string> { "All" }
            };

            var response = await _sqsClient.ReceiveMessageAsync(request, stoppingToken);

            foreach (var message in response.Messages)
            {
                try
                {
                    await ProcessMessageAsync(message, stoppingToken);
                    await _sqsClient.DeleteMessageAsync(_queueUrl, message.ReceiptHandle, stoppingToken);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing message {MessageId}", message.MessageId);
                    // Message will return to queue after visibility timeout
                }
            }
        }
    }

    private async Task ProcessMessageAsync(Message message, CancellationToken cancellationToken)
    {
        using var scope = _serviceProvider.CreateScope();
        var messageType = message.MessageAttributes["MessageType"].StringValue;
        
        // Route to appropriate handler based on message type
        var handler = scope.ServiceProvider.GetRequiredService<IMessageHandler>();
        await handler.HandleAsync(messageType, message.Body, cancellationToken);
    }
}
```

### 7.3 SNS for Fan-Out

```csharp
// SNS Publisher for events
public class SnsEventPublisher : IEventPublisher
{
    private readonly IAmazonSimpleNotificationService _snsClient;
    private readonly string _topicArn;

    public async Task PublishEventAsync<T>(T @event) where T : IDomainEvent
    {
        var message = new PublishRequest
        {
            TopicArn = _topicArn,
            Message = JsonSerializer.Serialize(@event),
            MessageAttributes = new Dictionary<string, MessageAttributeValue>
            {
                ["EventType"] = new MessageAttributeValue
                {
                    DataType = "String",
                    StringValue = typeof(T).Name
                }
            }
        };

        await _snsClient.PublishAsync(message);
    }
}
```

### 7.4 S3 for File Storage

```csharp
// S3 File Service
public class S3FileService : IFileService
{
    private readonly IAmazonS3 _s3Client;
    private readonly string _bucketName;

    public async Task<string> UploadAsync(Stream fileStream, string fileName, string contentType)
    {
        var key = $"{DateTime.UtcNow:yyyy/MM/dd}/{Guid.NewGuid()}/{fileName}";
        
        var request = new PutObjectRequest
        {
            BucketName = _bucketName,
            Key = key,
            InputStream = fileStream,
            ContentType = contentType,
            ServerSideEncryptionMethod = ServerSideEncryptionMethod.AES256
        };

        await _s3Client.PutObjectAsync(request);
        return key;
    }

    public async Task<Stream> DownloadAsync(string key)
    {
        var response = await _s3Client.GetObjectAsync(_bucketName, key);
        return response.ResponseStream;
    }

    public string GetPresignedUrl(string key, TimeSpan expiration)
    {
        var request = new GetPreSignedUrlRequest
        {
            BucketName = _bucketName,
            Key = key,
            Expires = DateTime.UtcNow.Add(expiration)
        };

        return _s3Client.GetPreSignedURL(request);
    }
}
```

---

## Phase 8: Security Implementation

### 8.1 Amazon Cognito Authentication

```csharp
// Program.cs - Cognito configuration
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    var cognitoConfig = builder.Configuration.GetSection("AWS:Cognito");
    var region = cognitoConfig["Region"];
    var userPoolId = cognitoConfig["UserPoolId"];
    var appClientId = cognitoConfig["AppClientId"];

    options.Authority = $"https://cognito-idp.{region}.amazonaws.com/{userPoolId}";
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuerSigningKey = true,
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidAudience = appClientId,
        ValidateLifetime = true
    };
});

// Cognito User Service
public class CognitoUserService : IUserService
{
    private readonly IAmazonCognitoIdentityProvider _cognitoClient;
    private readonly string _userPoolId;

    public async Task<UserDto> CreateUserAsync(CreateUserRequest request)
    {
        var adminCreateRequest = new AdminCreateUserRequest
        {
            UserPoolId = _userPoolId,
            Username = request.Email,
            UserAttributes = new List<AttributeType>
            {
                new AttributeType { Name = "email", Value = request.Email },
                new AttributeType { Name = "email_verified", Value = "true" },
                new AttributeType { Name = "custom:role", Value = request.Role }
            },
            TemporaryPassword = GenerateTemporaryPassword(),
            MessageAction = MessageActionType.SUPPRESS  // Or RESEND to send welcome email
        };

        var response = await _cognitoClient.AdminCreateUserAsync(adminCreateRequest);
        return MapToDto(response.User);
    }

    public async Task AddUserToGroupAsync(string username, string groupName)
    {
        await _cognitoClient.AdminAddUserToGroupAsync(new AdminAddUserToGroupRequest
        {
            UserPoolId = _userPoolId,
            Username = username,
            GroupName = groupName
        });
    }
}
```

### 8.2 Cognito Infrastructure

```hcl
# Cognito User Pool
resource "aws_cognito_user_pool" "main" {
  name = "app-user-pool"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 12
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  mfa_configuration = "OPTIONAL"

  software_token_mfa_configuration {
    enabled = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  schema {
    name                = "role"
    attribute_data_type = "String"
    mutable             = true
    required            = false

    string_attribute_constraints {
      min_length = 1
      max_length = 256
    }
  }
}

resource "aws_cognito_user_pool_client" "app" {
  name         = "app-client"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }

  access_token_validity  = 1
  id_token_validity      = 1
  refresh_token_validity = 30
}

# Cognito Groups (Roles)
resource "aws_cognito_user_group" "admin" {
  name         = "Admin"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Administrator role"
}

resource "aws_cognito_user_group" "user" {
  name         = "User"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Standard user role"
}
```

### 8.3 AWS Secrets Manager

```csharp
// Secrets Manager configuration
public static class SecretsManagerExtensions
{
    public static IConfigurationBuilder AddSecretsManager(
        this IConfigurationBuilder builder,
        string secretId,
        string region)
    {
        var client = new AmazonSecretsManagerClient(RegionEndpoint.GetBySystemName(region));
        
        var request = new GetSecretValueRequest { SecretId = secretId };
        var response = client.GetSecretValueAsync(request).Result;
        
        var secrets = JsonSerializer.Deserialize<Dictionary<string, string>>(response.SecretString);
        
        builder.AddInMemoryCollection(secrets);
        return builder;
    }
}

// Usage in Program.cs
if (!builder.Environment.IsDevelopment())
{
    builder.Configuration.AddSecretsManager(
        secretId: "app/production/secrets",
        region: "us-east-1");
}
```

### 8.4 AWS WAF Configuration

```hcl
# WAF for API protection
resource "aws_wafv2_web_acl" "api" {
  name        = "api-waf"
  description = "WAF rules for API protection"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Rate limiting
  rule {
    name     = "RateLimitRule"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed Rules - Common Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # SQL Injection protection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 3

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "api-waf"
    sampled_requests_enabled   = true
  }
}
```

---

## Phase 9: Cross-Cutting Concerns

### 9.1 CloudWatch Logging

```csharp
// Program.cs - AWS Logging
builder.Logging.ClearProviders();
builder.Logging.AddAWSProvider(builder.Configuration.GetAWSLoggingConfigSection());

// appsettings.json
{
  "AWS": {
    "Logging": {
      "Region": "us-east-1",
      "LogGroup": "/app/api",
      "LogLevel": {
        "Default": "Information",
        "Microsoft": "Warning",
        "System": "Warning"
      }
    }
  }
}

// Structured logging with correlation
public class CorrelationIdMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers["X-Correlation-Id"].FirstOrDefault() 
            ?? Guid.NewGuid().ToString();
        
        context.Items["CorrelationId"] = correlationId;
        context.Response.Headers["X-Correlation-Id"] = correlationId;
        
        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            await _next(context);
        }
    }
}
```

### 9.2 AWS X-Ray Distributed Tracing

```csharp
// Program.cs - X-Ray configuration
builder.Services.AddAWSXRayRecorder();

// X-Ray middleware
app.UseXRay("AppAPI");

// Trace outgoing HTTP calls
builder.Services.AddHttpClient("ExternalApi")
    .AddHttpMessageHandler<TracingHttpMessageHandler>();

// Trace database calls
public class TracedDbContext : ApplicationDbContext
{
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.AddInterceptors(new XRayDbCommandInterceptor());
    }
}

// Custom X-Ray segment for business operations
public async Task<OrderDto> CreateOrderAsync(CreateOrderRequest request)
{
    using var segment = AWSXRayRecorder.Instance.BeginSubsegment("CreateOrder");
    segment.AddAnnotation("CustomerId", request.CustomerId);
    
    try
    {
        // Business logic
        var order = await _orderRepository.CreateAsync(request);
        segment.AddMetadata("OrderId", order.Id);
        return order;
    }
    catch (Exception ex)
    {
        segment.AddException(ex);
        throw;
    }
}
```

### 9.3 CloudWatch Metrics and Alarms

```hcl
# Custom metrics dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "app-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", "api-service", "ClusterName", "app-cluster"],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "ECS Service Metrics"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", module.rds.db_instance_identifier],
            [".", "DatabaseConnections", ".", "."],
            [".", "ReadLatency", ".", "."],
            [".", "WriteLatency", ".", "."]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "RDS Metrics"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.main.arn_suffix],
            [".", "HTTPCode_Target_2XX_Count", ".", "."],
            [".", "HTTPCode_Target_5XX_Count", ".", "."]
          ]
          period = 60
          stat   = "Sum"
          region = var.aws_region
          title  = "ALB Metrics"
        }
      }
    ]
  })
}

# Alarms
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "ecs-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization is too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.api.name
  }
}

resource "aws_cloudwatch_metric_alarm" "error_rate" {
  alarm_name          = "api-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "High 5XX error rate"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
}
```

### 9.4 Audit Trail with DynamoDB

```csharp
// DynamoDB Audit Service
public class DynamoDbAuditService : IAuditService
{
    private readonly IAmazonDynamoDB _dynamoDb;
    private readonly string _tableName;

    public async Task LogAsync(string entityType, object entityId, string action,
                               object oldValues = null, object newValues = null)
    {
        var item = new Dictionary<string, AttributeValue>
        {
            ["PK"] = new AttributeValue { S = $"ENTITY#{entityType}#{entityId}" },
            ["SK"] = new AttributeValue { S = $"AUDIT#{DateTime.UtcNow:O}#{Guid.NewGuid()}" },
            ["EntityType"] = new AttributeValue { S = entityType },
            ["EntityId"] = new AttributeValue { S = entityId?.ToString() },
            ["Action"] = new AttributeValue { S = action },
            ["Timestamp"] = new AttributeValue { S = DateTime.UtcNow.ToString("O") },
            ["TTL"] = new AttributeValue { N = DateTimeOffset.UtcNow.AddYears(7).ToUnixTimeSeconds().ToString() }
        };

        if (oldValues != null)
            item["OldValues"] = new AttributeValue { S = JsonSerializer.Serialize(oldValues) };
        if (newValues != null)
            item["NewValues"] = new AttributeValue { S = JsonSerializer.Serialize(newValues) };

        await _dynamoDb.PutItemAsync(new PutItemRequest
        {
            TableName = _tableName,
            Item = item
        });
    }

    public async Task<IEnumerable<AuditLogDto>> GetAuditHistoryAsync(string entityType, string entityId)
    {
        var response = await _dynamoDb.QueryAsync(new QueryRequest
        {
            TableName = _tableName,
            KeyConditionExpression = "PK = :pk AND begins_with(SK, :sk)",
            ExpressionAttributeValues = new Dictionary<string, AttributeValue>
            {
                [":pk"] = new AttributeValue { S = $"ENTITY#{entityType}#{entityId}" },
                [":sk"] = new AttributeValue { S = "AUDIT#" }
            },
            ScanIndexForward = false,
            Limit = 100
        });

        return response.Items.Select(MapToDto);
    }
}
```

### 9.5 Notifications with SES and SNS

```csharp
// SES Email Service
public class SesEmailService : IEmailService
{
    private readonly IAmazonSimpleEmailService _sesClient;
    private readonly ILogger<SesEmailService> _logger;
    private readonly string _fromAddress;

    public async Task SendEmailAsync(EmailRequest request)
    {
        var sendRequest = new SendEmailRequest
        {
            Source = _fromAddress,
            Destination = new Destination
            {
                ToAddresses = request.ToAddresses.ToList()
            },
            Message = new Message
            {
                Subject = new Content(request.Subject),
                Body = new Body
                {
                    Html = new Content
                    {
                        Charset = "UTF-8",
                        Data = request.HtmlBody
                    },
                    Text = new Content
                    {
                        Charset = "UTF-8",
                        Data = request.TextBody
                    }
                }
            },
            ConfigurationSetName = "app-emails"  // For tracking
        };

        try
        {
            var response = await _sesClient.SendEmailAsync(sendRequest);
            _logger.LogInformation("Email sent. MessageId: {MessageId}", response.MessageId);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send email to {Recipients}", string.Join(", ", request.ToAddresses));
            throw;
        }
    }
}

// SNS for push notifications / SMS
public class SnsNotificationService : IPushNotificationService
{
    private readonly IAmazonSimpleNotificationService _snsClient;

    public async Task SendSmsAsync(string phoneNumber, string message)
    {
        await _snsClient.PublishAsync(new PublishRequest
        {
            PhoneNumber = phoneNumber,
            Message = message,
            MessageAttributes = new Dictionary<string, MessageAttributeValue>
            {
                ["AWS.SNS.SMS.SMSType"] = new MessageAttributeValue
                {
                    DataType = "String",
                    StringValue = "Transactional"
                }
            }
        });
    }
}
```

### 9.6 Auto Scaling Configuration

```hcl
# ECS Auto Scaling
resource "aws_appautoscaling_target" "api" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Scale on CPU
resource "aws_appautoscaling_policy" "api_cpu" {
  name               = "api-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Scale on request count
resource "aws_appautoscaling_policy" "api_requests" {
  name               = "api-requests-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.api.resource_id
  scalable_dimension = aws_appautoscaling_target.api.scalable_dimension
  service_namespace  = aws_appautoscaling_target.api.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.main.arn_suffix}/${aws_lb_target_group.api.arn_suffix}"
    }
    target_value       = 1000
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
```

---

## Phase 10: Testing & Validation

### 10.1 Testing with LocalStack

```csharp
// Integration test with LocalStack
public class OrderServiceIntegrationTests : IClassFixture<LocalStackFixture>
{
    private readonly LocalStackFixture _fixture;

    [Fact]
    public async Task CreateOrder_PublishesToSQS()
    {
        // Arrange
        var sqsClient = _fixture.CreateSqsClient();
        var service = new OrderService(
            _fixture.CreateDbContext(),
            sqsClient,
            _fixture.Logger);

        // Act
        var order = await service.CreateOrderAsync(new CreateOrderRequest { ... });

        // Assert
        var messages = await sqsClient.ReceiveMessageAsync(new ReceiveMessageRequest
        {
            QueueUrl = _fixture.OrderQueueUrl,
            MaxNumberOfMessages = 1
        });
        
        Assert.Single(messages.Messages);
        var orderEvent = JsonSerializer.Deserialize<OrderCreatedEvent>(messages.Messages[0].Body);
        Assert.Equal(order.Id, orderEvent.OrderId);
    }
}

// LocalStack fixture
public class LocalStackFixture : IAsyncLifetime
{
    private readonly TestcontainersContainer _localstack;

    public LocalStackFixture()
    {
        _localstack = new TestcontainersBuilder<TestcontainersContainer>()
            .WithImage("localstack/localstack:latest")
            .WithPortBinding(4566, 4566)
            .WithEnvironment("SERVICES", "sqs,s3,secretsmanager")
            .Build();
    }

    public async Task InitializeAsync()
    {
        await _localstack.StartAsync();
        await SetupAwsResources();
    }

    public IAmazonSQS CreateSqsClient()
    {
        return new AmazonSQSClient(new AmazonSQSConfig
        {
            ServiceURL = "http://localhost:4566",
            UseHttp = true
        });
    }
}
```

### 10.2 Load Testing

```yaml
# k6 load test script
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up more
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    http_req_failed: ['rate<0.01'],    // Error rate under 1%
  },
};

export default function () {
  let response = http.get('https://api.example.com/api/orders');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

---

## Phase 11: AWS Deployment & Go-Live

### 11.1 Deployment Checklist (AWS)

| Category | Item | Status |
|----------|------|--------|
| **AWS Account** | Production account created | ☐ |
| | IAM roles and policies configured | ☐ |
| | AWS Organizations SCP applied | ☐ |
| **Networking** | VPC created with multi-AZ subnets | ☐ |
| | NAT Gateways deployed | ☐ |
| | VPC Flow Logs enabled | ☐ |
| | Route 53 DNS configured | ☐ |
| **Compute** | ECS cluster created | ☐ |
| | Task definitions registered | ☐ |
| | Auto-scaling configured | ☐ |
| | ECR repositories created | ☐ |
| **Database** | RDS Multi-AZ deployed | ☐ |
| | Read replicas configured (if needed) | ☐ |
| | Automated backups enabled | ☐ |
| | Parameter groups tuned | ☐ |
| **Caching** | ElastiCache cluster deployed | ☐ |
| | Redis AUTH enabled | ☐ |
| **Security** | WAF rules configured | ☐ |
| | Secrets Manager populated | ☐ |
| | ACM certificates issued | ☐ |
| | Cognito user pool configured | ☐ |
| | Security groups reviewed | ☐ |
| **Monitoring** | CloudWatch dashboards created | ☐ |
| | CloudWatch alarms configured | ☐ |
| | X-Ray tracing enabled | ☐ |
| | Log groups with retention set | ☐ |
| **CDN** | CloudFront distribution created | ☐ |
| | Origin access configured | ☐ |
| | Cache behaviors set | ☐ |
| **CI/CD** | GitHub Actions / CodePipeline configured | ☐ |
| | OIDC trust with AWS established | ☐ |
| | Deployment approvals configured | ☐ |

### 11.2 Blue-Green Deployment Strategy

```hcl
# Blue-Green with ECS
resource "aws_ecs_service" "api" {
  name            = "api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  deployment_controller {
    type = "CODE_DEPLOY"
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.blue.arn
    container_name   = "api"
    container_port   = 8080
  }
}

# CodeDeploy for Blue-Green
resource "aws_codedeploy_deployment_group" "api" {
  app_name               = aws_codedeploy_app.api.name
  deployment_group_name  = "api-deployment-group"
  deployment_config_name = "CodeDeployDefault.ECSAllAtOnce"
  service_role_arn       = aws_iam_role.codedeploy.arn

  ecs_service {
    cluster_name = aws_ecs_cluster.main.name
    service_name = aws_ecs_service.api.name
  }

  blue_green_deployment_config {
    deployment_ready_option {
      action_on_timeout = "CONTINUE_DEPLOYMENT"
    }

    terminate_blue_instances_on_deployment_success {
      action                           = "TERMINATE"
      termination_wait_time_in_minutes = 5
    }
  }

  load_balancer_info {
    target_group_pair_info {
      prod_traffic_route {
        listener_arns = [aws_lb_listener.https.arn]
      }

      target_group {
        name = aws_lb_target_group.blue.name
      }

      target_group {
        name = aws_lb_target_group.green.name
      }
    }
  }

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM"]
  }

  alarm_configuration {
    alarms  = [aws_cloudwatch_metric_alarm.error_rate.alarm_name]
    enabled = true
  }
}
```

### 11.3 Cutover Runbook

| Step | Action | Owner | Duration |
|------|--------|-------|----------|
| T-24h | Final data sync validation | DBA | 1h |
| T-12h | Pre-cutover smoke tests | QA | 2h |
| T-4h | Notify stakeholders of maintenance | PM | - |
| T-1h | Create RDS snapshot | DBA | 15m |
| T-0 | Stop OutSystems application | DevOps | 5m |
| T+5m | Run final DMS sync | DBA | 30m |
| T+35m | Validate data counts | DBA | 15m |
| T+50m | Update Route 53 to new ALB | DevOps | 5m |
| T+55m | Smoke test production | QA | 15m |
| T+70m | Enable CloudWatch alarms | DevOps | 5m |
| T+75m | Announce go-live | PM | - |

---

## Phase 12: Post-Migration Support

### 12.1 AWS Cost Optimization

| Service | Optimization | Potential Savings |
|---------|-------------|-------------------|
| **ECS Fargate** | Right-size tasks, use Spot for non-critical | 30-70% |
| **RDS** | Reserved instances, right-size | 30-50% |
| **ElastiCache** | Reserved nodes | 30-50% |
| **NAT Gateway** | Use NAT instances for dev | 50-70% |
| **CloudWatch** | Adjust log retention | Variable |
| **S3** | Lifecycle policies, Intelligent Tiering | 30-50% |

### 12.2 AWS Well-Architected Review

| Pillar | Key Checks |
|--------|-----------|
| **Operational Excellence** | Runbooks, incident response, deployments |
| **Security** | IAM least privilege, encryption, WAF |
| **Reliability** | Multi-AZ, backups, disaster recovery |
| **Performance** | Right-sizing, caching, CDN |
| **Cost Optimization** | Reserved capacity, right-sizing |
| **Sustainability** | Resource efficiency, scaling policies |

### 12.3 Disaster Recovery Plan

| Scenario | RTO | RPO | Strategy |
|----------|-----|-----|----------|
| Single AZ failure | 0 | 0 | Multi-AZ automatic failover |
| Region failure | 4h | 1h | Pilot light in DR region |
| Data corruption | 1h | 5m | Point-in-time recovery |
| Complete outage | 4h | 1h | Cross-region restore |

```hcl
# Cross-region backup
resource "aws_backup_plan" "main" {
  name = "app-backup-plan"

  rule {
    rule_name         = "daily-backup"
    target_vault_name = aws_backup_vault.main.name
    schedule          = "cron(0 2 * * ? *)"

    lifecycle {
      delete_after = 30
    }

    copy_action {
      destination_vault_arn = aws_backup_vault.dr_region.arn
      lifecycle {
        delete_after = 7
      }
    }
  }
}
```

---

## Appendix A: AWS Service Mapping (OutSystems → AWS)

| OutSystems Feature | AWS Service |
|-------------------|-------------|
| Application Server | ECS Fargate / EKS |
| Database | RDS (PostgreSQL/SQL Server) |
| Session Store | ElastiCache Redis |
| File Storage | S3 |
| Scheduled Jobs | EventBridge + ECS/Lambda |
| BPT Processes | Step Functions |
| Authentication | Cognito |
| API Gateway | Amazon API Gateway |
| CDN | CloudFront |
| DNS | Route 53 |
| Logging | CloudWatch Logs |
| Monitoring | CloudWatch + X-Ray |
| Secrets | Secrets Manager |
| Message Queue | SQS |
| Pub/Sub | SNS |
| Email | SES |
| Search | OpenSearch (if needed) |

## Appendix B: Terraform Module Structure

```
infrastructure/terraform/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecs/
│   │   ├── cluster.tf
│   │   ├── service.tf
│   │   ├── task-definition.tf
│   │   ├── autoscaling.tf
│   │   └── variables.tf
│   ├── rds/
│   │   ├── main.tf
│   │   ├── parameter-group.tf
│   │   └── variables.tf
│   ├── elasticache/
│   │   ├── main.tf
│   │   └── variables.tf
│   ├── cognito/
│   │   ├── user-pool.tf
│   │   ├── user-pool-client.tf
│   │   └── variables.tf
│   └── monitoring/
│       ├── cloudwatch.tf
│       ├── alarms.tf
│       ├── dashboard.tf
│       └── variables.tf
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── ...
│   └── prod/
│       └── ...
└── backend.tf
```

---

*Document Version: 1.0 (AWS Cloud-Native)*  
*Created: 2026-07-22*  
*Last Updated: 2026-07-22*
