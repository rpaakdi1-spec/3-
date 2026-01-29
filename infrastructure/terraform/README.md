# Cold Chain Dispatch System - Infrastructure

This directory contains Terraform configurations for deploying the Cold Chain Dispatch System to AWS.

## 🏗️ Architecture Overview

The infrastructure includes:

- **VPC**: Multi-AZ VPC with public and private subnets
- **ECS Fargate**: Containerized backend and frontend services
- **RDS PostgreSQL**: Multi-AZ database with automated backups
- **ElastiCache Redis**: High-availability caching cluster
- **Application Load Balancer**: HTTPS termination and routing
- **S3 Buckets**: Storage for uploads, backups, and logs
- **ECR**: Container image repositories
- **CloudWatch**: Comprehensive monitoring and logging
- **Auto Scaling**: Dynamic scaling based on CPU, memory, and requests
- **SNS**: Alarm notifications

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0
3. **AWS CLI** configured with credentials
4. **Docker** for building and pushing images

## 🚀 Quick Start

### 1. Configure Variables

```bash
# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**Important**: Update these values:
- `db_password`: Strong database password
- `domain_name`: Your domain (optional)
- `alarm_email`: Email for alerts
- `s3_bucket_names`: Ensure globally unique bucket names

### 2. Initialize Terraform

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan
```

### 3. Deploy Infrastructure

```bash
# Apply the configuration
terraform apply

# Confirm with 'yes'
```

**Note**: Initial deployment takes 15-20 minutes.

### 4. Build and Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin $(terraform output -raw backend_ecr_repository_url | cut -d'/' -f1)

# Build and push backend
cd ../../backend
docker build -t coldchain-backend .
docker tag coldchain-backend:latest $(terraform output -raw backend_ecr_repository_url):latest
docker push $(terraform output -raw backend_ecr_repository_url):latest

# Build and push frontend
cd ../frontend
docker build -t coldchain-frontend .
docker tag coldchain-frontend:latest $(terraform output -raw frontend_ecr_repository_url):latest
docker push $(terraform output -raw frontend_ecr_repository_url):latest
```

### 5. Deploy Services

```bash
# Update ECS services to use new images
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw backend_service_name) \
  --force-new-deployment

aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw frontend_service_name) \
  --force-new-deployment
```

### 6. Access Application

```bash
# Get application URL
terraform output application_url

# Example: https://coldchain-production-alb-123456789.ap-northeast-2.elb.amazonaws.com
```

## 📁 File Structure

```
infrastructure/terraform/
├── main.tf                    # Main configuration, VPC, security groups
├── variables.tf               # Variable definitions
├── outputs.tf                 # Output values
├── database.tf                # RDS PostgreSQL and ElastiCache Redis
├── ecs.tf                     # ECS cluster, services, ALB
├── storage.tf                 # S3 buckets and ECR repositories
├── autoscaling.tf             # Auto scaling and CloudWatch alarms
├── terraform.tfvars.example   # Example variables
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

Key configuration variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `project_name` | `coldchain` | Project name prefix |
| `environment` | `production` | Environment name |
| `aws_region` | `ap-northeast-2` | AWS region (Seoul) |
| `vpc_cidr` | `10.0.0.0/16` | VPC CIDR block |
| `db_instance_class` | `db.t3.medium` | RDS instance type |
| `redis_node_type` | `cache.t3.medium` | Redis node type |
| `ecs_backend_cpu` | `1024` | Backend CPU units (1 vCPU) |
| `ecs_backend_memory` | `2048` | Backend memory (2 GB) |

### Auto Scaling

**Backend Service**:
- Min: 2 tasks
- Max: 10 tasks
- Triggers: CPU > 70%, Memory > 80%, Requests > 1000/target

**Frontend Service**:
- Min: 2 tasks
- Max: 6 tasks
- Triggers: CPU > 70%, Memory > 80%

### CloudWatch Alarms

Alarms are configured for:
- Unhealthy targets (< 1 healthy)
- High 5XX error rate (> 10 in 5 minutes)
- RDS CPU > 80%
- RDS storage < 10 GB
- RDS connections > 80
- Redis CPU > 75%
- Redis memory > 90%

## 🔒 Security Features

- **Encryption at rest**: Enabled for RDS, Redis, S3
- **Encryption in transit**: HTTPS only, Redis TLS
- **Private subnets**: Database and cache in private subnets
- **Security groups**: Least privilege access
- **IAM roles**: Task-specific permissions
- **S3 bucket policies**: Block public access
- **VPC**: Isolated network environment

## 💰 Cost Estimation

**Monthly costs** (approximate, ap-northeast-2):

| Service | Configuration | Monthly Cost (USD) |
|---------|--------------|-------------------|
| ECS Fargate | 4 tasks (1 vCPU, 2GB) | ~$90 |
| RDS (db.t3.medium) | Multi-AZ | ~$150 |
| ElastiCache (cache.t3.medium) | 2 nodes | ~$100 |
| ALB | Standard | ~$25 |
| NAT Gateway | 2 AZs | ~$70 |
| Data transfer | 100 GB | ~$10 |
| CloudWatch | Logs & metrics | ~$15 |
| S3 | 100 GB storage | ~$3 |
| **Total** | | **~$463/month** |

**Cost optimization tips**:
- Use Savings Plans for ECS and RDS
- Enable S3 lifecycle policies
- Use Reserved Instances for predictable workloads
- Review CloudWatch log retention

## 📊 Monitoring

### CloudWatch Dashboards

Access metrics at:
```
https://console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2
```

Key metrics:
- ECS service CPU/Memory utilization
- ALB request count, latency, error rates
- RDS connections, IOPS, latency
- Redis evictions, connections

### Logs

View logs in CloudWatch Log Groups:
- `/ecs/coldchain-production/backend`
- `/ecs/coldchain-production/frontend`
- `/aws/elasticache/redis/coldchain-production`

## 🔄 Updates and Maintenance

### Update Infrastructure

```bash
# Pull latest Terraform changes
git pull

# Review changes
terraform plan

# Apply updates
terraform apply
```

### Update Application

```bash
# Rebuild and push new images
# ... (see step 4 above)

# Force new deployment
aws ecs update-service --cluster ... --service ... --force-new-deployment
```

### Database Migrations

```bash
# Connect to ECS task
aws ecs execute-command \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --task TASK_ID \
  --container backend \
  --interactive \
  --command "/bin/sh"

# Run migrations
alembic upgrade head
```

## 🔐 Secrets Management

Store secrets in AWS Secrets Manager or SSM Parameter Store:

```bash
# Store database password
aws secretsmanager create-secret \
  --name coldchain/production/db-password \
  --secret-string "YOUR_PASSWORD"

# Store API keys
aws ssm put-parameter \
  --name /coldchain/production/api-key \
  --value "YOUR_API_KEY" \
  --type SecureString
```

Update ECS task definitions to reference secrets.

## 🆘 Troubleshooting

### ECS Tasks Not Starting

```bash
# Check service events
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw backend_service_name)

# Check task logs
aws logs tail /ecs/coldchain-production/backend --follow
```

### Database Connection Issues

```bash
# Verify security group rules
aws ec2 describe-security-groups --group-ids $(terraform output -raw rds_security_group_id)

# Test connection from ECS task
aws ecs execute-command --cluster ... --task ... --command "psql -h RDS_ENDPOINT -U USERNAME -d DATABASE"
```

### High Costs

```bash
# Review cost by service
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## 🧹 Cleanup

**Warning**: This will destroy all resources!

```bash
# Delete all resources
terraform destroy

# Confirm with 'yes'
```

**Note**: Some resources (RDS snapshots, S3 buckets with objects) may require manual cleanup.

## 📚 Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## 📧 Support

For issues or questions:
- Open an issue in the repository
- Contact: DevOps Team

---

**Last Updated**: 2026-01-28  
**Version**: 1.0.0
