variable "project_name" {
  type    = string
  default = "nexusquant"
}

variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "backend_image" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "backend_security_group_id" {
  type = string
}

variable "upstox_api_key_secret_arn" {
  type = string
}

variable "upstox_access_token_secret_arn" {
  type = string
}

variable "database_url_secret_arn" {
  type = string
}

variable "redis_url_secret_arn" {
  type = string
}
