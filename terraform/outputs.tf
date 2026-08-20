output "alb_dns_name" {
  description = "Load balancer endpoint for the API tier"
  value       = aws_lb.afriground.dns_name
}

output "api_endpoint" {
  description = "Public API base URL"
  value       = var.acm_certificate_arn != "" ? "https://${aws_lb.afriground.dns_name}" : "http://${aws_lb.afriground.dns_name}"
}

output "rds_endpoint" {
  description = "PostgreSQL endpoint"
  value       = aws_db_instance.afriground_db.endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.afriground_redis.cache_nodes[0].address
}

output "ecr_api_url" {
  description = "API image repository"
  value       = aws_ecr_repository.api.repository_url
}

output "ecr_worker_url" {
  description = "Worker image repository"
  value       = aws_ecr_repository.worker.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.afriground.name
}