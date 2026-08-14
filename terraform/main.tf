terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "afriground-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "af-south-1" # Cape Town region for African data residency
  }
}

provider "aws" {
  region = var.aws_region
}

# ── Variables ───────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS Region for deployment"
  type        = string
  default     = "af-south-1" # Prioritize African data sovereignty
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

# ── Infrastructure ──────────────────────────────────────────────────────────

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "afriground-prod-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["af-south-1a", "af-south-1b", "af-south-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true
}

# Relational Database (RDS PostgreSQL + PostGIS)
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
}

# Security Group for DB
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

# Redis for Caching / Background tasks
resource "aws_elasticache_cluster" "afriground_redis" {
  cluster_id           = "afriground-prod-redis"
  engine               = "redis"
  node_type            = "cache.t4g.medium"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.1"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet.name
}

resource "aws_elasticache_subnet_group" "redis_subnet" {
  name       = "afriground-redis-subnet"
  subnet_ids = module.vpc.private_subnets
}

# Security Group for App
resource "aws_security_group" "app_sg" {
  name        = "afriground-app-sg"
  description = "Allow inbound web traffic"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
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
}

# Main S3 Bucket for Earth Observation Dataset Storage
resource "aws_s3_bucket" "datasets" {
  bucket = "afriground-prod-datasets-af-south"
}

resource "aws_s3_bucket_versioning" "datasets_versioning" {
  bucket = aws_s3_bucket.datasets.id
  versioning_configuration {
    status = "Enabled"
  }
}
