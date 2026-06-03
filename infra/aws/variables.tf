variable "project_name" {
  type    = string
  default = "nexusquant"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "az_count" {
  type    = number
  default = 2
}

variable "vpc_cidr" {
  type    = string
  default = "10.42.0.0/16"
}

variable "backend_image" {
  type = string
}

variable "fargate_cpu" {
  type    = number
  default = 1024
}

variable "fargate_memory" {
  type    = number
  default = 2048
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "autoscaling_min_capacity" {
  type    = number
  default = 1
}

variable "autoscaling_max_capacity" {
  type    = number
  default = 4
}

variable "cpu_target_tracking" {
  type    = number
  default = 65
}

variable "memory_target_tracking" {
  type    = number
  default = 70
}

variable "trading_mode" {
  type    = string
  default = "simulator"
}

variable "require_live_upstox_connection" {
  type    = bool
  default = true
}

variable "upstox_base_url" {
  type    = string
  default = "https://api.upstox.com/v2"
}

variable "upstox_market_authorize_endpoint" {
  type    = string
  default = "/v3/feed/market-data-feed/authorize"
}

variable "ws_heartbeat_interval" {
  type    = number
  default = 15
}

variable "redis_channel" {
  type    = string
  default = "market_ticks"
}

variable "log_level" {
  type    = string
  default = "INFO"
}

variable "acm_certificate_arn" {
  type = string
}

variable "ssl_policy" {
  type    = string
  default = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}

variable "alb_idle_timeout" {
  type    = number
  default = 300
}

variable "create_route53_record" {
  type    = bool
  default = false
}

variable "route53_zone_id" {
  type    = string
  default = ""
}

variable "api_domain_name" {
  type    = string
  default = ""
}

variable "postgres_db_name" {
  type    = string
  default = "nexusquant"
}

variable "postgres_username" {
  type    = string
  default = "nexusquant"
}

variable "postgres_instance_class" {
  type    = string
  default = "db.t4g.small"
}

variable "postgres_engine_version" {
  type    = string
  default = "16.4"
}

variable "postgres_allocated_storage" {
  type    = number
  default = 20
}

variable "postgres_max_allocated_storage" {
  type    = number
  default = 100
}

variable "postgres_backup_retention_days" {
  type    = number
  default = 7
}

variable "postgres_deletion_protection" {
  type    = bool
  default = true
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "redis_engine_version" {
  type    = string
  default = "7.1"
}

variable "redis_replicas_per_node_group" {
  type    = number
  default = 1
}

variable "upstox_api_key" {
  type      = string
  default   = ""
  sensitive = true
}

variable "upstox_access_token" {
  type      = string
  default   = ""
  sensitive = true
}

variable "log_retention_days" {
  type    = number
  default = 30
}

variable "cpu_alarm_threshold" {
  type    = number
  default = 75
}

variable "memory_alarm_threshold" {
  type    = number
  default = 80
}

variable "apply_immediately" {
  type    = bool
  default = true
}
