output "alb_dns_name" {
  value = aws_lb.api.dns_name
}

output "api_base_url" {
  value = "https://${aws_lb.api.dns_name}"
}

output "api_domain_url" {
  value = var.create_route53_record ? "https://${var.api_domain_name}" : null
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.backend.name
}

output "postgres_endpoint" {
  value = aws_db_instance.postgres.address
}

output "redis_primary_endpoint" {
  value = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "secrets" {
  value = {
    upstox_api_key      = aws_secretsmanager_secret.upstox_api_key.name
    upstox_access_token = aws_secretsmanager_secret.upstox_access_token.name
    database_url        = aws_secretsmanager_secret.database_url.name
    redis_url           = aws_secretsmanager_secret.redis_url.name
  }
}
