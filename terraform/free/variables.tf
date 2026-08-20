variable "aws_region" {
  description = "AWS Region (free-tier eligible)"
  type        = string
  default     = "ap-northeast-1" # Tokyo
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "FastAPI session/HS256 signing secret"
  type        = string
  sensitive   = true
}

variable "supabase_url" {
  description = "Supabase project URL used by the API"
  type        = string
  default     = "https://placeholder.supabase.co"
}

variable "supabase_service_role_key" {
  description = "Supabase service-role key"
  type        = string
  sensitive   = true
}

variable "supabase_jwt_secret" {
  description = "Supabase JWT secret (HS256 verification + web service identity)"
  type        = string
  sensitive   = true
}

variable "api_cors_origins" {
  description = "Comma-separated CORS origins allowed to call the API"
  type        = string
  default     = "https://afriground.vercel.app,http://localhost:3000"
}

variable "ssh_cidrs" {
  description = "CIDRs allowed to SSH to the EC2 host (0.0.0.0/0 for demo)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "api_cidrs" {
  description = "CIDRs allowed to reach the API on :8000 (0.0.0.0/0 for demo)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ssh_public_key_path" {
  description = "Path to the public key to import as the deploy key pair"
  type        = string
  default     = ".ssh/afriground.pub"
}

variable "datasets_bucket" {
  description = "Globally unique S3 bucket for dataset storage"
  type        = string
}

variable "repo_bucket" {
  description = "Globally unique S3 bucket used to ship the repo to the EC2 host"
  type        = string
}