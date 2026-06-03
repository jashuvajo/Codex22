resource "random_password" "postgres_master" {
  length  = 24
  special = true
}

resource "aws_db_subnet_group" "postgres" {
  name       = "${local.name_prefix}-postgres-subnets"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-postgres-subnets"
  })
}

resource "aws_db_instance" "postgres" {
  identifier                      = "${local.name_prefix}-postgres"
  engine                          = "postgres"
  engine_version                  = var.postgres_engine_version
  instance_class                  = var.postgres_instance_class
  allocated_storage               = var.postgres_allocated_storage
  max_allocated_storage           = var.postgres_max_allocated_storage
  db_name                         = var.postgres_db_name
  username                        = var.postgres_username
  password                        = random_password.postgres_master.result
  db_subnet_group_name            = aws_db_subnet_group.postgres.name
  vpc_security_group_ids          = [aws_security_group.rds.id]
  backup_retention_period         = var.postgres_backup_retention_days
  deletion_protection             = var.postgres_deletion_protection
  performance_insights_enabled    = true
  publicly_accessible             = false
  storage_encrypted               = true
  auto_minor_version_upgrade      = true
  apply_immediately               = var.apply_immediately
  skip_final_snapshot             = false
  final_snapshot_identifier       = "${local.name_prefix}-postgres-final"
  delete_automated_backups        = false
  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-postgres"
  })
}
