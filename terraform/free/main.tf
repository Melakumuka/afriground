# AfriGround free-tier stack (AWS Free Tier, 12 months)
#
# Region: ap-northeast-1 (Tokyo) — free-tier eligible, close to operator.
# Cost target ~$0/mo: t3.micro RDS + t3.micro ElastiCache + t3.micro EC2,
# no NAT gateway, no ALB (API exposed directly on the EC2 public IP).
# Managed Postgres/Redis come from AWS; the EC2 host runs ONLY the api +
# worker containers via docker compose (override in docker-compose.aws.yml).

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket         = "afriground-terraform-state-free"
    key            = "terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "afriground-terraform-lock-free"
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

locals {
  tags = {
    Project     = "afriground"
    Environment = "free"
    ManagedBy   = "terraform"
  }
  db_url_secret = "/afriground/free/database_url"
  param_prefix  = "/afriground/free"
}

# ── VPC (2 AZs, public + private, no NAT) ────────────────────────────────────

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "afriground-free-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-northeast-1a", "ap-northeast-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  create_database_subnet_group = true
  database_subnets             = ["10.0.11.0/24", "10.0.12.0/24"]

  enable_nat_gateway = false
  enable_vpn_gateway = false
}

# ── Security groups ──────────────────────────────────────────────────────────

resource "aws_security_group" "ssh_sg" {
  name        = "afriground-free-ssh"
  description = "SSH to the EC2 host"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "SSH (demo: open to the internet; tighten via var.ssh_cidrs)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_cidrs
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = local.tags
}

resource "aws_security_group" "api_sg" {
  name        = "afriground-free-api"
  description = "API ingress"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "FastAPI (demo: open; tighten to Vercel IPs in prod)"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.api_cidrs
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
  name        = "afriground-free-db"
  description = "PostgreSQL from the EC2 host"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "PostgreSQL from EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.api_sg.id]
  }
}

resource "aws_security_group" "redis_sg" {
  name        = "afriground-free-redis"
  description = "Redis from the EC2 host"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Redis from EC2"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.api_sg.id]
  }
}

# ── RDS PostgreSQL (t3.micro, free tier) ─────────────────────────────────────

resource "aws_db_instance" "afriground_db" {
  identifier     = "afriground-free-db"
  allocated_storage = 20
  storage_type      = "gp2"
  engine            = "postgres"
  engine_version    = "16.14"
  instance_class    = "db.t3.micro" # free-tier eligible
  db_name           = "afriground"
  username          = "afriground_admin"
  password          = var.db_password
  parameter_group_name = "default.postgres16"

  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = module.vpc.database_subnet_group_name

  multi_az            = false
  publicly_accessible = false
  skip_final_snapshot = false
  deletion_protection = false

  tags = local.tags
}

# ── ElastiCache Redis (t3.micro, free tier) ─────────────────────────────────

resource "aws_elasticache_cluster" "afriground_redis" {
  cluster_id           = "afriground-free-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro" # free-tier eligible
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.1"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet.name
  security_group_ids   = [aws_security_group.redis_sg.id]

  tags = local.tags
}

resource "aws_elasticache_subnet_group" "redis_subnet" {
  name       = "afriground-free-redis-subnet"
  subnet_ids = module.vpc.private_subnets
}

# ── S3: datasets + repo shipping ─────────────────────────────────────────────

resource "aws_s3_bucket" "datasets" {
  bucket = var.datasets_bucket
  tags   = local.tags
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

resource "aws_s3_bucket" "repo" {
  bucket = var.repo_bucket
  tags   = local.tags
}

resource "aws_s3_bucket_public_access_block" "repo" {
  bucket                  = aws_s3_bucket.repo.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ── SSH key + IAM for the EC2 host ───────────────────────────────────────────

resource "aws_key_pair" "deploy" {
  key_name   = "afriground-free"
  public_key = file(var.ssh_public_key_path)
}

data "aws_iam_policy_document" "ec2_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2" {
  name               = "afriground-free-ec2"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume.json
  tags               = local.tags
}

resource "aws_iam_policy" "ec2" {
  name = "afriground-free-ec2-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["ssm:GetParameters"]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/afriground/free/*"
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.repo.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = [aws_s3_bucket.datasets.arn, "${aws_s3_bucket.datasets.arn}/*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2" {
  role       = aws_iam_role.ec2.name
  policy_arn = aws_iam_policy.ec2.arn
}

resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2" {
  name = "afriground-free-ec2"
  role = aws_iam_role.ec2.name
}

# ── Secrets (SSM) ────────────────────────────────────────────────────────────

resource "aws_ssm_parameter" "database_url" {
  name  = local.db_url_secret
  type  = "SecureString"
  value = "postgresql+asyncpg://afriground_admin:${var.db_password}@${aws_db_instance.afriground_db.endpoint}/afriground"
  tags  = local.tags
}

resource "aws_ssm_parameter" "secret_key" {
  name  = "${local.param_prefix}/secret_key"
  type  = "SecureString"
  value = var.secret_key
  tags  = local.tags
}

resource "aws_ssm_parameter" "supabase_service_role_key" {
  name  = "${local.param_prefix}/supabase_service_role_key"
  type  = "SecureString"
  value = var.supabase_service_role_key
  tags  = local.tags
}

resource "aws_ssm_parameter" "supabase_jwt_secret" {
  name  = "${local.param_prefix}/supabase_jwt_secret"
  type  = "SecureString"
  value = var.supabase_jwt_secret
  tags  = local.tags
}

# ── EC2 host (t3.micro) ──────────────────────────────────────────────────────

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  user_data = templatefile("${path.module}/userdata.sh", {
    region         = var.aws_region
    repo_bucket    = aws_s3_bucket.repo.id
    repo_key       = "afriground.zip"
    db_url_param   = local.db_url_secret
    secret_key_param = "${local.param_prefix}/secret_key"
    supabase_role_param = "${local.param_prefix}/supabase_service_role_key"
    supabase_jwt_param  = "${local.param_prefix}/supabase_jwt_secret"
    supabase_url    = var.supabase_url
    api_cors        = var.api_cors_origins
    redis_host      = aws_elasticache_cluster.afriground_redis.cache_nodes[0].address
  })
}

resource "aws_instance" "host" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t3.micro" # free-tier eligible
  key_name               = aws_key_pair.deploy.key_name
  subnet_id              = module.vpc.public_subnets[0]
  vpc_security_group_ids = [aws_security_group.api_sg.id, aws_security_group.ssh_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name
  associate_public_ip_address = true
  user_data              = local.user_data

  user_data_replace_on_change = true

  tags = merge(local.tags, { Name = "afriground-free-host" })
}

# ── Outputs ──────────────────────────────────────────────────────────────────

output "ec2_public_ip" {
  value = aws_instance.host.public_ip
}

output "ec2_ssh" {
  value = "ssh -i terraform/free/.ssh/afriground ec2-user@${aws_instance.host.public_ip}"
}

output "api_endpoint" {
  value = "http://${aws_instance.host.public_ip}:8000"
}

output "rds_endpoint" {
  value = aws_db_instance.afriground_db.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.afriground_redis.cache_nodes[0].address
}