# AfriGround production infrastructure (Phase 4.3)
#
# VPC + RDS PostgreSQL + ElastiCache Redis + S3 datasets, plus the
# orchestration API and Celery worker on ECS Fargate behind an ALB.
# Web frontend deploys on Vercel (out of band) and calls the API tier.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "afriground-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "af-south-1" # Cape Town region for African data residency
    dynamodb_table = "afriground-terraform-lock"
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  tags = {
    Project     = "afriground"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  api_image    = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/afriground-api:${var.image_tag}"
  worker_image = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/afriground-worker:${var.image_tag}"
  redis_url    = "redis://${aws_elasticache_cluster.afriground_redis.cache_nodes[0].address}:6379/0"
}

# ── VPC ──────────────────────────────────────────────────────────────────────

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "afriground-prod-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["af-south-1a", "af-south-1b", "af-south-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  database_subnets = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  create_database_subnet_group = true
  enable_nat_gateway           = true
  enable_vpn_gateway           = false
}

# ── Security groups ──────────────────────────────────────────────────────────

resource "aws_security_group" "alb_sg" {
  name        = "afriground-alb-sg"
  description = "Allow inbound web traffic to the load balancer"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_security_group" "app_sg" {
  name        = "afriground-app-sg"
  description = "API + worker task security group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "API from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_security_group" "db_sg" {
  name        = "afriground-db-sg"
  description = "Allow inbound traffic from app tier"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "PostgreSQL from App Tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id]
  }
}

resource "aws_security_group" "redis_sg" {
  name        = "afriground-redis-sg"
  description = "Allow inbound Redis from app tier"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Redis from App Tier"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id]
  }
}

# ── Database ─────────────────────────────────────────────────────────────────

resource "aws_db_instance" "afriground_db" {
  identifier           = "afriground-prod-db"
  allocated_storage    = 100
  storage_type         = "gp3"
  engine               = "postgres"
  engine_version       = "16.3"
  instance_class       = "db.r6g.large" # Graviton for better price/performance
  db_name              = "afriground"
  username             = "afriground_admin"
  password             = var.db_password
  parameter_group_name = "default.postgres16"

  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = module.vpc.database_subnet_group_name

  multi_az             = true
  publicly_accessible  = false
  skip_final_snapshot  = false
  deletion_protection  = true

  tags = local.tags
}

# ── Redis ────────────────────────────────────────────────────────────────────

resource "aws_elasticache_cluster" "afriground_redis" {
  cluster_id           = "afriground-prod-redis"
  engine               = "redis"
  node_type            = "cache.t4g.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.1"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet.name
  security_group_ids   = [aws_security_group.redis_sg.id]

  tags = local.tags
}

resource "aws_elasticache_subnet_group" "redis_subnet" {
  name       = "afriground-redis-subnet"
  subnet_ids = module.vpc.private_subnets
}

# ── Dataset storage ──────────────────────────────────────────────────────────

resource "aws_s3_bucket" "datasets" {
  bucket = "afriground-prod-datasets-af-south"

  tags = local.tags
}

resource "aws_s3_bucket_versioning" "datasets_versioning" {
  bucket = aws_s3_bucket.datasets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "datasets" {
  bucket                  = aws_s3_bucket.datasets.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ── Container registry ───────────────────────────────────────────────────────

resource "aws_ecr_repository" "api" {
  name                 = "afriground-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = false

  tags = local.tags
}

resource "aws_ecr_repository" "worker" {
  name                 = "afriground-worker"
  image_tag_mutability = "MUTABLE"
  force_delete         = false

  tags = local.tags
}

resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name
  policy     = <<-EOT
    {
      "rules": [
        {
          "rulePriority": 1,
          "description": "Keep last 10 tagged images",
          "selection": { "tagStatus": "tagged", "tagPrefixList": [], "countType": "imageCountMoreThan", "countNumber": 10 },
          "action": { "type": "expire" }
        },
        {
          "rulePriority": 2,
          "description": "Expire untagged images after 7 days",
          "selection": { "tagStatus": "untagged", "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 7 },
          "action": { "type": "expire" }
        }
      ]
    }
  EOT
}

resource "aws_ecr_lifecycle_policy" "worker" {
  repository = aws_ecr_repository.worker.name
  policy     = aws_ecr_lifecycle_policy.api.policy
}

# ── Secrets (SSM Parameter Store, referenced by ECS task definitions) ────────

resource "aws_ssm_parameter" "database_url" {
  name  = "/afriground/${var.environment}/database_url"
  type  = "SecureString"
  value = "postgresql+asyncpg://afriground_admin:${var.db_password}@${aws_db_instance.afriground_db.endpoint}/afriground"
  tags  = local.tags
}

resource "aws_ssm_parameter" "secret_key" {
  name  = "/afriground/${var.environment}/secret_key"
  type  = "SecureString"
  value = var.secret_key
  tags  = local.tags
}

resource "aws_ssm_parameter" "supabase_service_role_key" {
  name  = "/afriground/${var.environment}/supabase_service_role_key"
  type  = "SecureString"
  value = var.supabase_service_role_key
  tags  = local.tags
}

resource "aws_ssm_parameter" "supabase_jwt_secret" {
  name  = "/afriground/${var.environment}/supabase_jwt_secret"
  type  = "SecureString"
  value = var.supabase_jwt_secret
  tags  = local.tags
}

resource "aws_ssm_parameter" "agent_mtls_cert" {
  count = var.agent_mtls_enabled ? 1 : 0
  name  = "/afriground/${var.environment}/agent_mtls_cert"
  type  = "SecureString"
  value = var.agent_mtls_cert
  tags  = local.tags
}

resource "aws_ssm_parameter" "agent_mtls_key" {
  count = var.agent_mtls_enabled ? 1 : 0
  name  = "/afriground/${var.environment}/agent_mtls_key"
  type  = "SecureString"
  value = var.agent_mtls_key
  tags  = local.tags
}

resource "aws_ssm_parameter" "agent_mtls_ca" {
  count = var.agent_mtls_enabled ? 1 : 0
  name  = "/afriground/${var.environment}/agent_mtls_ca"
  type  = "SecureString"
  value = var.agent_mtls_ca
  tags  = local.tags
}

# ── ECS roles ────────────────────────────────────────────────────────────────

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "afriground-ecs-execution-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  tags               = local.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "ssm_read" {
  name = "afriground-ssm-read-${var.environment}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ssm:GetParameters"]
        Resource = ["arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/afriground/${var.environment}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["kms:Decrypt"]
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm_read" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = aws_iam_policy.ssm_read.arn
}

resource "aws_iam_role" "ecs_task" {
  name               = "afriground-ecs-task-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
  tags               = local.tags
}

resource "aws_iam_policy" "datasets_rw" {
  name = "afriground-datasets-rw-${var.environment}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = "${aws_s3_bucket.datasets.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.datasets.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "datasets_rw" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.datasets_rw.arn
}

# ── ECS cluster ──────────────────────────────────────────────────────────────

resource "aws_ecs_cluster" "afriground" {
  name = "afriground-prod"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = local.tags
}

# ── Task definitions ─────────────────────────────────────────────────────────

resource "aws_ecs_task_definition" "api" {
  family                   = "afriground-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  container_definitions    = jsonencode([{
    name             = "api"
    image            = local.api_image
    essential        = true
    portMappings     = [{ containerPort = 8000, protocol = "tcp" }]
    environment      = [
      { name = "REDIS_URL", value = local.redis_url },
      { name = "CELERY_BROKER_URL", value = local.redis_url },
      { name = "SUPABASE_URL", value = var.supabase_url },
      { name = "API_CORS_ORIGINS", value = var.api_cors_origins },
      { name = "AFRIGROUND_ORCHESTRATION_SIMULATE", value = var.orchestration_simulate },
      { name = "AGENT_MTLS_ENABLED", value = var.agent_mtls_enabled },
    ]
    secrets          = concat([
      { name = "DATABASE_URL", valueFrom = aws_ssm_parameter.database_url.arn },
      { name = "SECRET_KEY", valueFrom = aws_ssm_parameter.secret_key.arn },
      { name = "SUPABASE_SERVICE_ROLE_KEY", valueFrom = aws_ssm_parameter.supabase_service_role_key.arn },
      { name = "SUPABASE_JWT_SECRET", valueFrom = aws_ssm_parameter.supabase_jwt_secret.arn },
    ], var.agent_mtls_enabled ? [
      { name = "AGENT_MTLS_CERT", valueFrom = aws_ssm_parameter.agent_mtls_cert[0].arn },
      { name = "AGENT_MTLS_KEY", valueFrom = aws_ssm_parameter.agent_mtls_key[0].arn },
      { name = "AGENT_MTLS_CA", valueFrom = aws_ssm_parameter.agent_mtls_ca[0].arn },
    ] : [])
    logConfiguration = {
      logDriver = "awslogs"
      options   = {
        "awslogs-group"         = "/ecs/afriground-api"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "api"
      }
    }
    healthCheck = {
      command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz', timeout=4)\" || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 15
    }
  }])
  tags = local.tags
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "afriground-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  container_definitions    = jsonencode([{
    name        = "worker"
    image       = local.worker_image
    essential   = true
    environment = [
      { name = "REDIS_URL", value = local.redis_url },
      { name = "CELERY_BROKER_URL", value = local.redis_url },
      { name = "SUPABASE_URL", value = var.supabase_url },
      { name = "AFRIGROUND_ORCHESTRATION_SIMULATE", value = var.orchestration_simulate },
    ]
    secrets     = [
      { name = "AFRIGROUND_WORKER_URL", valueFrom = aws_ssm_parameter.database_url.arn },
      { name = "DATABASE_URL", valueFrom = aws_ssm_parameter.database_url.arn },
      { name = "SECRET_KEY", valueFrom = aws_ssm_parameter.secret_key.arn },
      { name = "SUPABASE_SERVICE_ROLE_KEY", valueFrom = aws_ssm_parameter.supabase_service_role_key.arn },
      { name = "SUPABASE_JWT_SECRET", valueFrom = aws_ssm_parameter.supabase_jwt_secret.arn },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options   = {
        "awslogs-group"         = "/ecs/afriground-worker"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "worker"
      }
    }
  }])
  tags = local.tags
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/afriground-api"
  retention_in_days = 30
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/afriground-worker"
  retention_in_days = 30
  tags              = local.tags
}

# ── Services ─────────────────────────────────────────────────────────────────

resource "aws_ecs_service" "api" {
  name            = "afriground-api"
  cluster         = aws_ecs_cluster.afriground.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.app_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  tags = local.tags
}

resource "aws_ecs_service" "worker" {
  name            = "afriground-worker"
  cluster         = aws_ecs_cluster.afriground.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.app_sg.id]
    assign_public_ip = false
  }

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  tags = local.tags
}

# ── Load balancer ────────────────────────────────────────────────────────────

resource "aws_lb" "afriground" {
  name               = "afriground-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = module.vpc.public_subnets

  tags = local.tags
}

resource "aws_lb_target_group" "api" {
  name        = "afriground-api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    path                = "/healthz"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = local.tags
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.afriground.arn
  port              = 80
  protocol          = "HTTP"

  dynamic "default_action" {
    for_each = var.acm_certificate_arn == "" ? [1] : []
    content {
      type             = "forward"
      target_group_arn = aws_lb_target_group.api.arn
    }
  }

  dynamic "default_action" {
    for_each = var.acm_certificate_arn != "" ? [1] : []
    content {
      type = "redirect"
      redirect {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  }
}

resource "aws_lb_listener" "https" {
  count             = var.acm_certificate_arn != "" ? 1 : 0
  load_balancer_arn = aws_lb.afriground.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}