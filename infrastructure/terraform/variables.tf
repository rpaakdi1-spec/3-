# General Configuration
variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "coldchain"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-northeast-2" # Seoul
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

# RDS Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS autoscaling in GB"
  type        = number
  default     = 500
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "coldchain_db"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "coldchain_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "db_backup_retention_period" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = true
}

# ElastiCache Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes in the cluster"
  type        = number
  default     = 2
}

variable "redis_parameter_group_family" {
  description = "Redis parameter group family"
  type        = string
  default     = "redis7"
}

variable "redis_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

# ECS Configuration
variable "ecs_backend_cpu" {
  description = "CPU units for backend ECS task"
  type        = number
  default     = 1024 # 1 vCPU
}

variable "ecs_backend_memory" {
  description = "Memory for backend ECS task in MB"
  type        = number
  default     = 2048 # 2 GB
}

variable "ecs_frontend_cpu" {
  description = "CPU units for frontend ECS task"
  type        = number
  default     = 512 # 0.5 vCPU
}

variable "ecs_frontend_memory" {
  description = "Memory for frontend ECS task in MB"
  type        = number
  default     = 1024 # 1 GB
}

variable "ecs_backend_desired_count" {
  description = "Desired number of backend ECS tasks"
  type        = number
  default     = 2
}

variable "ecs_frontend_desired_count" {
  description = "Desired number of frontend ECS tasks"
  type        = number
  default     = 2
}

variable "ecs_backend_min_capacity" {
  description = "Minimum number of backend ECS tasks for autoscaling"
  type        = number
  default     = 2
}

variable "ecs_backend_max_capacity" {
  description = "Maximum number of backend ECS tasks for autoscaling"
  type        = number
  default     = 10
}

variable "ecs_frontend_min_capacity" {
  description = "Minimum number of frontend ECS tasks for autoscaling"
  type        = number
  default     = 2
}

variable "ecs_frontend_max_capacity" {
  description = "Maximum number of frontend ECS tasks for autoscaling"
  type        = number
  default     = 6
}

# S3 Configuration
variable "s3_bucket_names" {
  description = "S3 bucket names"
  type = object({
    uploads = string
    backups = string
    logs    = string
  })
  default = {
    uploads = "coldchain-uploads"
    backups = "coldchain-backups"
    logs    = "coldchain-logs"
  }
}

# CloudWatch Configuration
variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# Domain Configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = ""
}

# Monitoring Configuration
variable "enable_detailed_monitoring" {
  description = "Enable detailed CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  default     = ""
}

# Backup Configuration
variable "enable_automated_backups" {
  description = "Enable automated RDS backups"
  type        = bool
  default     = true
}

variable "backup_window" {
  description = "Preferred backup window for RDS"
  type        = string
  default     = "03:00-04:00" # UTC
}

variable "maintenance_window" {
  description = "Preferred maintenance window for RDS"
  type        = string
  default     = "mon:04:00-mon:05:00" # UTC
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
