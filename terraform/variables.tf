variable "aws_region" {
  description = "AWS Region for deployment"
  type        = string
  default     = "af-south-1" # Prioritize African data sovereignty
}

variable "environment" {
  description = "Deployment environment (prod, staging)"
  type        = string
  default     = "prod"
}

variable "image_tag" {
  description = "Container image tag to deploy (api + worker)"
  type        = string
  default     = "latest"
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
  default     = "https://www.afriground.space,https://afriground.space"
}

variable "orchestration_simulate" {
  description = "Keep the Phase 2/3 orchestration simulator driving the outbox"
  type        = string
  default     = "1"
}

variable "agent_mtls_enabled" {
  description = "Require mTLS client certificates for the edge agent bridge (Phase 4.0)"
  type        = string
  default     = "0"
}

variable "agent_mtls_cert" {
  description = "PEM server certificate for the mTLS listener (AGENT_MTLS_CERT)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "agent_mtls_key" {
  description = "PEM private key for the mTLS listener (AGENT_MTLS_KEY)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "agent_mtls_ca" {
  description = "PEM CA bundle that signs edge agent client certs (AGENT_MTLS_CA)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "acm_certificate_arn" {
  description = "ACM certificate for the HTTPS listener; leave empty for HTTP-only"
  type        = string
  default     = ""
}