resource "aws_secretsmanager_secret" "upstox_api_key" {
  name = "${var.project_name}/${var.environment}/upstox_api_key"
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "upstox_api_key" {
  secret_id     = aws_secretsmanager_secret.upstox_api_key.id
  secret_string = var.upstox_api_key
}

resource "aws_secretsmanager_secret" "upstox_access_token" {
  name = "${var.project_name}/${var.environment}/upstox_access_token"
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "upstox_access_token" {
  secret_id     = aws_secretsmanager_secret.upstox_access_token.id
  secret_string = var.upstox_access_token
}

resource "aws_secretsmanager_secret" "database_url" {
  name = "${var.project_name}/${var.environment}/database_url"
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = aws_secretsmanager_secret.database_url.id
  secret_string = format(
    "postgresql+asyncpg://%s:%s@%s:%s/%s",
    var.postgres_username,
    random_password.postgres_master.result,
    aws_db_instance.postgres.address,
    aws_db_instance.postgres.port,
    var.postgres_db_name,
  )
}

resource "aws_secretsmanager_secret" "redis_url" {
  name = "${var.project_name}/${var.environment}/redis_url"
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "redis_url" {
  secret_id = aws_secretsmanager_secret.redis_url.id
  secret_string = format(
    "rediss://default:%s@%s:%s/0",
    random_password.redis_auth.result,
    aws_elasticache_replication_group.redis.primary_endpoint_address,
    aws_elasticache_replication_group.redis.port,
  )
}
