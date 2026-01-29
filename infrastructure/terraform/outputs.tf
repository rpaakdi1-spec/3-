# Infrastructure Outputs

# VPC
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

# Load Balancer
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.main.zone_id
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

# ECS
output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = aws_ecs_service.backend.name
}

output "frontend_service_name" {
  description = "Name of the frontend ECS service"
  value       = aws_ecs_service.frontend.name
}

# ECR
output "backend_ecr_repository_url" {
  description = "URL of the backend ECR repository"
  value       = aws_ecr_repository.backend.repository_url
}

output "frontend_ecr_repository_url" {
  description = "URL of the frontend ECR repository"
  value       = aws_ecr_repository.frontend.repository_url
}

# Database
output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "rds_database_name" {
  description = "Name of the RDS database"
  value       = aws_db_instance.main.db_name
}

output "rds_port" {
  description = "Port of the RDS instance"
  value       = aws_db_instance.main.port
}

# Redis
output "redis_primary_endpoint" {
  description = "Primary endpoint of the Redis cluster"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}

output "redis_reader_endpoint" {
  description = "Reader endpoint of the Redis cluster"
  value       = aws_elasticache_replication_group.main.reader_endpoint_address
  sensitive   = true
}

output "redis_port" {
  description = "Port of the Redis cluster"
  value       = 6379
}

# S3
output "uploads_bucket_name" {
  description = "Name of the uploads S3 bucket"
  value       = aws_s3_bucket.uploads.id
}

output "backups_bucket_name" {
  description = "Name of the backups S3 bucket"
  value       = aws_s3_bucket.backups.id
}

output "logs_bucket_name" {
  description = "Name of the logs S3 bucket"
  value       = aws_s3_bucket.logs.id
}

# CloudWatch
output "backend_log_group" {
  description = "CloudWatch log group for backend"
  value       = aws_cloudwatch_log_group.backend.name
}

output "frontend_log_group" {
  description = "CloudWatch log group for frontend"
  value       = aws_cloudwatch_log_group.frontend.name
}

# SNS
output "alarms_topic_arn" {
  description = "ARN of the SNS topic for alarms"
  value       = aws_sns_topic.alarms.arn
}

# Security Groups
output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "ecs_tasks_security_group_id" {
  description = "ID of the ECS tasks security group"
  value       = aws_security_group.ecs_tasks.id
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = aws_security_group.redis.id
}

# IAM
output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

# Application URL
output "application_url" {
  description = "Application URL"
  value       = var.domain_name != "" ? "https://${var.domain_name}" : "https://${aws_lb.main.dns_name}"
}

output "api_url" {
  description = "API URL"
  value       = var.domain_name != "" ? "https://${var.domain_name}/api" : "https://${aws_lb.main.dns_name}/api"
}

# Connection Strings (for reference)
output "database_connection_info" {
  description = "Database connection information"
  value = {
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    database = aws_db_instance.main.db_name
    username = var.db_username
  }
  sensitive = true
}

output "redis_connection_info" {
  description = "Redis connection information"
  value = {
    primary_endpoint = aws_elasticache_replication_group.main.primary_endpoint_address
    reader_endpoint  = aws_elasticache_replication_group.main.reader_endpoint_address
    port             = 6379
  }
  sensitive = true
}
