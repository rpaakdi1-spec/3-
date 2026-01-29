# ElastiCache Redis Module for Cold Chain Dispatch

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "cache_subnets" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}

variable "node_type" {
  type    = string
  default = "cache.t3.medium"
}

variable "num_cache_nodes" {
  type    = number
  default = 2
}

variable "tags" {
  type = map(string)
}

# Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-redis-subnet-group"
  subnet_ids = var.cache_subnets
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-redis-subnet-group"
  })
}

# Parameter Group
resource "aws_elasticache_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-redis7"
  family = "redis7"
  
  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }
  
  parameter {
    name  = "timeout"
    value = "300"
  }
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-redis7"
  })
}

# Replication Group (for high availability)
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  replication_group_description = "Redis cluster for ${var.project_name} ${var.environment}"
  
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = var.node_type
  num_cache_clusters   = var.num_cache_nodes
  port                 = 6379
  
  parameter_group_name = aws_elasticache_parameter_group.main.name
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = var.security_group_ids
  
  # Automatic failover (for production)
  automatic_failover_enabled = var.num_cache_nodes > 1
  multi_az_enabled          = var.environment == "prod" && var.num_cache_nodes > 1
  
  # Backup
  snapshot_retention_limit = var.environment == "prod" ? 7 : 1
  snapshot_window         = "03:00-05:00"
  maintenance_window      = "mon:05:00-mon:07:00"
  
  # Encryption
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token_enabled        = false  # Set to true and provide auth_token for production
  
  # Auto minor version upgrade
  auto_minor_version_upgrade = true
  
  # Logging
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_slow_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "slow-log"
  }
  
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_engine_log.name
    destination_type = "cloudwatch-logs"
    log_format       = "json"
    log_type         = "engine-log"
  }
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-redis"
  })
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "redis_slow_log" {
  name              = "/aws/elasticache/${var.project_name}-${var.environment}/redis/slow-log"
  retention_in_days = 7
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-redis-slow-log"
  })
}

resource "aws_cloudwatch_log_group" "redis_engine_log" {
  name              = "/aws/elasticache/${var.project_name}-${var.environment}/redis/engine-log"
  retention_in_days = 7
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-redis-engine-log"
  })
}

# Outputs
output "cluster_id" {
  value = aws_elasticache_replication_group.main.id
}

output "primary_endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "reader_endpoint" {
  value = aws_elasticache_replication_group.main.reader_endpoint_address
}

output "endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "port" {
  value = aws_elasticache_replication_group.main.port
}

output "connection_string" {
  value     = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:${aws_elasticache_replication_group.main.port}"
  sensitive = true
}
