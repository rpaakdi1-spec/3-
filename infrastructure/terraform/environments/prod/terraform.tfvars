# Production Environment Configuration
# Cold Chain Dispatch System

environment = "prod"
aws_region  = "ap-northeast-2"  # Seoul

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
az_count = 3  # Use 3 AZs for high availability

# RDS Configuration
db_name           = "coldchain_prod"
db_username       = "coldchain_admin"  # Change in actual deployment
db_password       = "CHANGE_ME_IN_PRODUCTION"  # Use AWS Secrets Manager
db_instance_class = "db.r6g.xlarge"  # 4 vCPU, 32 GB RAM
db_allocated_storage = 500  # 500 GB

# ElastiCache Redis Configuration
redis_node_type  = "cache.r6g.large"  # 2 vCPU, 13.07 GB RAM
redis_num_nodes  = 3  # Primary + 2 replicas

# ECS - Backend Configuration
backend_image         = "ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/cold-chain-backend:latest"
backend_cpu           = 2048  # 2 vCPU
backend_memory        = 4096  # 4 GB
backend_desired_count = 4     # 4 tasks for high availability

# ECS - Frontend Configuration
frontend_image         = "ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/cold-chain-frontend:latest"
frontend_cpu           = 1024  # 1 vCPU
frontend_memory        = 2048  # 2 GB
frontend_desired_count = 3     # 3 tasks for high availability

# Domain Configuration (optional)
domain_name     = "dispatch.coldchain.com"
certificate_arn = "arn:aws:acm:ap-northeast-2:ACCOUNT_ID:certificate/CERT_ID"

# Monitoring
alert_email = "ops@coldchain.com"

# Backup
backup_retention_days = 30  # 30 days retention for production
