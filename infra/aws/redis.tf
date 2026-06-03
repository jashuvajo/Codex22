resource "random_password" "redis_auth" {
  length  = 48
  special = false
}

resource "aws_elasticache_subnet_group" "redis" {
  name       = "${local.name_prefix}-redis-subnets"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-subnets"
  })
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = substr(replace("${local.name_prefix}-redis", "_", "-"), 0, 40)
  description                = "Redis for NexusQuant telemetry and queues"
  node_type                  = var.redis_node_type
  engine                     = "redis"
  engine_version             = var.redis_engine_version
  port                       = 6379
  parameter_group_name       = "default.redis7"
  subnet_group_name          = aws_elasticache_subnet_group.redis.name
  security_group_ids         = [aws_security_group.redis.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_auth.result
  num_node_groups            = 1
  replicas_per_node_group    = var.redis_replicas_per_node_group
  automatic_failover_enabled = var.redis_replicas_per_node_group > 0
  multi_az_enabled           = var.redis_replicas_per_node_group > 0
  apply_immediately          = var.apply_immediately

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis"
  })
}
