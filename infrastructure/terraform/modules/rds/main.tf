# RDS PostgreSQL Module for Cold Chain Dispatch

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "database_subnets" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}

variable "db_name" {
  type = string
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "instance_class" {
  type    = string
  default = "db.t3.medium"
}

variable "allocated_storage" {
  type    = number
  default = 100
}

variable "tags" {
  type = map(string)
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.database_subnets
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  })
}

# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-pg15"
  family = "postgres15"
  
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }
  
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"  # Log queries taking > 1 second
  }
  
  parameter {
    name  = "log_connections"
    value = "1"
  }
  
  parameter {
    name  = "log_disconnections"
    value = "1"
  }
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-pg15"
  })
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-db"
  
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = var.instance_class
  allocated_storage    = var.allocated_storage
  max_allocated_storage = var.allocated_storage * 2
  storage_type         = "gp3"
  storage_encrypted    = true
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = var.security_group_ids
  parameter_group_name   = aws_db_parameter_group.main.name
  
  # Backup
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "mon:04:00-mon:05:00"
  
  # High Availability (for production)
  multi_az               = var.environment == "prod" ? true : false
  
  # Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = 60
  monitoring_role_arn            = aws_iam_role.rds_monitoring.arn
  
  # Performance Insights
  performance_insights_enabled    = true
  performance_insights_retention_period = 7
  
  # Deletion protection (for production)
  deletion_protection = var.environment == "prod" ? true : false
  skip_final_snapshot = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${var.project_name}-${var.environment}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null
  
  # Auto minor version upgrade
  auto_minor_version_upgrade = true
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-db"
  })
}

# IAM Role for Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.project_name}-${var.environment}-rds-monitoring-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(var.tags, {
    Name = "${var.project_name}-${var.environment}-rds-monitoring-role"
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Outputs
output "instance_id" {
  value = aws_db_instance.main.id
}

output "endpoint" {
  value = aws_db_instance.main.endpoint
}

output "address" {
  value = aws_db_instance.main.address
}

output "port" {
  value = aws_db_instance.main.port
}

output "connection_string" {
  value     = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}"
  sensitive = true
}
