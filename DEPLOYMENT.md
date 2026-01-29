# 🚀 Production Deployment Guide

## Overview

This comprehensive guide covers the complete deployment process for the UVIS GPS Fleet Management System to production on AWS.

## Prerequisites

### Required Accounts and Access

- [ ] AWS Account with admin access
- [ ] GitHub account with repository access
- [ ] Domain name (example.com)
- [ ] Docker Hub account (or AWS ECR)
- [ ] Slack workspace for notifications (optional)

### Required Tools

```bash
# Install required tools
brew install terraform
brew install awscli
brew install kubectl
brew install docker
brew install jq

# Verify installations
terraform version
aws --version
kubectl version
docker --version
jq --version
```

### AWS CLI Configuration

```bash
# Configure AWS CLI
aws configure

# Verify access
aws sts get-caller-identity

# Set region
export AWS_DEFAULT_REGION=ap-northeast-2
```

## Phase 1: Infrastructure Deployment

### Step 1: Prepare Terraform Configuration

```bash
cd infrastructure/terraform

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit configuration
vim terraform.tfvars
```

Required variables in `terraform.tfvars`:

```hcl
# Project Configuration
project_name = "uvis-gps"
environment  = "prod"

# AWS Region
aws_region = "ap-northeast-2"

# VPC Configuration
vpc_cidr             = "10.0.0.0/16"
availability_zones   = ["ap-northeast-2a", "ap-northeast-2b", "ap-northeast-2c"]
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

# RDS Configuration
db_instance_class    = "db.t3.medium"
db_allocated_storage = 100
db_name              = "uvis_gps"
db_username          = "postgres"
# db_password will be generated and stored in Secrets Manager

# Redis Configuration
redis_node_type     = "cache.t3.medium"
redis_num_nodes     = 2

# ECS Configuration
backend_cpu         = 1024
backend_memory      = 2048
backend_desired_count = 2

frontend_cpu        = 512
frontend_memory     = 1024
frontend_desired_count = 2

# Domain Configuration
domain_name         = "example.com"
certificate_arn     = "" # Will be created

# Monitoring
enable_monitoring   = true
log_retention_days  = 30

# Backup Configuration
backup_retention_days = 7
enable_backup_replication = true
backup_replication_region = "us-west-2"

# Auto Scaling
enable_auto_scaling = true
min_capacity        = 2
max_capacity        = 10

# Tags
tags = {
  Project     = "UVIS GPS"
  Environment = "Production"
  ManagedBy   = "Terraform"
  Owner       = "DevOps Team"
}
```

### Step 2: Initialize Terraform

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -out=tfplan

# Review the plan carefully
```

### Step 3: Deploy Infrastructure

```bash
# Apply infrastructure
terraform apply tfplan

# This will take 15-20 minutes
# Infrastructure components created:
# - VPC with 3 AZs
# - Public and private subnets
# - NAT Gateways
# - Application Load Balancer
# - ECS Cluster
# - RDS PostgreSQL instance
# - ElastiCache Redis cluster
# - S3 buckets
# - CloudWatch alarms
# - IAM roles and policies
```

### Step 4: Verify Infrastructure

```bash
# Get infrastructure outputs
terraform output

# Verify VPC
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=uvis-gps-prod-vpc"

# Verify RDS
aws rds describe-db-instances --db-instance-identifier uvis-gps-prod-db

# Verify ECS Cluster
aws ecs describe-clusters --clusters uvis-gps-prod

# Verify ALB
aws elbv2 describe-load-balancers --names uvis-gps-prod-alb
```

## Phase 2: SSL/TLS Configuration

### Step 1: Request SSL Certificate

```bash
# Request certificate via AWS ACM
aws acm request-certificate \
    --domain-name example.com \
    --subject-alternative-names "*.example.com" \
    --validation-method DNS \
    --region ap-northeast-2

# Get certificate ARN
CERT_ARN=$(aws acm list-certificates --region ap-northeast-2 --query 'CertificateSummaryList[0].CertificateArn' --output text)
echo $CERT_ARN
```

### Step 2: Validate Certificate

```bash
# Get validation records
aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region ap-northeast-2

# Add CNAME records to your DNS provider
# Wait for validation (usually 5-30 minutes)

# Check validation status
aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region ap-northeast-2 \
    --query 'Certificate.Status' \
    --output text
```

### Step 3: Update ALB with Certificate

```bash
# Update terraform.tfvars with certificate ARN
echo "certificate_arn = \"$CERT_ARN\"" >> terraform.tfvars

# Re-apply terraform
terraform apply -auto-approve

# Verify HTTPS listener
aws elbv2 describe-listeners --load-balancer-arn $(terraform output -raw alb_arn)
```

## Phase 3: Database Setup

### Step 1: Get Database Credentials

```bash
# Get RDS endpoint
DB_HOST=$(terraform output -raw rds_endpoint)

# Get database password from Secrets Manager
DB_PASSWORD=$(aws secretsmanager get-secret-value \
    --secret-id uvis-gps/prod/db-password \
    --query SecretString \
    --output text)

echo "DB Host: $DB_HOST"
echo "DB Password: $DB_PASSWORD"
```

### Step 2: Initialize Database Schema

```bash
# Connect to database
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U postgres -d uvis_gps

# Or run Alembic migrations
cd backend
export DATABASE_URL="postgresql://postgres:$DB_PASSWORD@$DB_HOST:5432/uvis_gps"
alembic upgrade head
```

### Step 3: Seed Initial Data

```bash
# Run seed script
python scripts/seed_data.py

# Verify data
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U postgres -d uvis_gps -c "SELECT COUNT(*) FROM users;"
```

## Phase 4: Application Deployment

### Step 1: Build and Push Docker Images

```bash
# Get ECR login
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url)

# Build backend image
cd backend
docker build -t uvis-gps-backend:latest .

# Tag and push
docker tag uvis-gps-backend:latest $(terraform output -raw ecr_backend_url):latest
docker push $(terraform output -raw ecr_backend_url):latest

# Build frontend image
cd ../frontend
docker build -t uvis-gps-frontend:latest .

# Tag and push
docker tag uvis-gps-frontend:latest $(terraform output -raw ecr_frontend_url):latest
docker push $(terraform output -raw ecr_frontend_url):latest
```

### Step 2: Update Environment Variables

```bash
# Create secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name uvis-gps/prod/backend-env \
    --secret-string file://backend/.env.prod

# Update ECS task definition with secrets
terraform apply -auto-approve
```

### Step 3: Deploy Application

**Option A: Using GitHub Actions (Recommended)**

```bash
# Push to main branch
git push origin main

# GitHub Actions will automatically:
# 1. Build Docker images
# 2. Push to ECR
# 3. Update ECS services
# 4. Run health checks
# 5. Send notifications
```

**Option B: Using Deploy Script**

```bash
# Set environment variables
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=ap-northeast-2

# Run deploy script
./infrastructure/scripts/deploy.sh

# Select option:
# 1) Deploy Backend
# 2) Deploy Frontend
# 3) Deploy Both
```

### Step 4: Verify Deployment

```bash
# Check ECS services
aws ecs describe-services \
    --cluster uvis-gps-prod \
    --services uvis-gps-prod-backend uvis-gps-prod-frontend

# Check running tasks
aws ecs list-tasks --cluster uvis-gps-prod --desired-status RUNNING

# Get ALB DNS name
ALB_DNS=$(terraform output -raw alb_dns_name)
echo "ALB DNS: $ALB_DNS"

# Test backend health
curl http://$ALB_DNS/health

# Test API
curl http://$ALB_DNS/api/v1/health
```

## Phase 5: DNS Configuration

### Step 1: Update DNS Records

```bash
# Get ALB DNS name
ALB_DNS=$(terraform output -raw alb_dns_name)

# Create Route53 hosted zone (if not exists)
aws route53 create-hosted-zone --name example.com --caller-reference $(date +%s)

# Get hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones-by-name --dns-name example.com --query 'HostedZones[0].Id' --output text | cut -d'/' -f3)

# Create A record for domain
cat > dns-record.json <<EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "example.com",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "$(terraform output -raw alb_zone_id)",
        "DNSName": "$ALB_DNS",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $ZONE_ID \
    --change-batch file://dns-record.json

# Create A record for www subdomain
cat > dns-record-www.json <<EOF
{
  "Changes": [{
    "Action": "UPSERT",
    "ResourceRecordSet": {
      "Name": "www.example.com",
      "Type": "A",
      "AliasTarget": {
        "HostedZoneId": "$(terraform output -raw alb_zone_id)",
        "DNSName": "$ALB_DNS",
        "EvaluateTargetHealth": true
      }
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
    --hosted-zone-id $ZONE_ID \
    --change-batch file://dns-record-www.json
```

### Step 2: Verify DNS Resolution

```bash
# Wait for DNS propagation (5-30 minutes)
watch -n 10 "dig example.com +short"

# Test HTTPS access
curl -I https://example.com
```

## Phase 6: Monitoring Setup

### Step 1: Deploy Monitoring Stack

```bash
# Set environment variables
export ELASTIC_PASSWORD=$(openssl rand -base64 32)

# Create .env file
cat > infrastructure/logging/.env <<EOF
ELASTIC_PASSWORD=$ELASTIC_PASSWORD
EOF

# Deploy ELK Stack
cd infrastructure/logging
docker-compose -f docker-compose.logging.yml up -d

# Deploy Prometheus + Grafana
cd ../monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

### Step 2: Configure Dashboards

```bash
# Access Kibana
echo "Kibana: http://localhost:5601"
echo "Username: elastic"
echo "Password: $ELASTIC_PASSWORD"

# Access Grafana
echo "Grafana: http://localhost:3001"
echo "Username: admin"
echo "Password: admin"

# Import pre-configured dashboards
# 1. Log in to Grafana
# 2. Go to Dashboards > Import
# 3. Import dashboard JSON files from infrastructure/monitoring/grafana/dashboards/
```

### Step 3: Configure Alerts

```bash
# Update Alertmanager configuration
vim infrastructure/monitoring/alertmanager/alertmanager.yml

# Add your Slack webhook or email
# Restart Alertmanager
docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml restart alertmanager
```

## Phase 7: Backup Configuration

### Step 1: Configure Automated Backups

```bash
# Create backup configuration
cat > /etc/cron.d/uvis-gps-backup <<EOF
# Daily backup at 2:00 AM
0 2 * * * root /home/user/webapp/infrastructure/scripts/backup.sh daily >> /var/log/backup-daily.log 2>&1

# Weekly backup at 3:00 AM every Sunday
0 3 * * 0 root /home/user/webapp/infrastructure/scripts/backup.sh weekly >> /var/log/backup-weekly.log 2>&1

# Monthly backup at 4:00 AM on 1st of month
0 4 1 * * root /home/user/webapp/infrastructure/scripts/backup.sh monthly >> /var/log/backup-monthly.log 2>&1
EOF

# Set backup environment variables
cat > /etc/environment <<EOF
DB_HOST=$DB_HOST
DB_PORT=5432
DB_NAME=uvis_gps
DB_USER=postgres
DB_PASSWORD=$DB_PASSWORD
BACKUP_DIR=/backups/database
S3_BUCKET=uvis-gps-backups-prod
RETENTION_DAYS=30
EOF
```

### Step 2: Test Backup

```bash
# Run manual backup
./infrastructure/scripts/backup.sh manual

# Verify backup in S3
aws s3 ls s3://uvis-gps-backups-prod/database/ --recursive

# Test restore (to test database)
export DB_NAME=uvis_gps_test
./infrastructure/scripts/restore.sh /backups/database/latest-backup.sql.gz
```

## Phase 8: Security Hardening

### Step 1: Enable Security Features

```bash
# Enable GuardDuty
aws guardduty create-detector --enable

# Enable AWS Config
aws configservice put-configuration-recorder --configuration-recorder file://config-recorder.json
aws configservice put-delivery-channel --delivery-channel file://delivery-channel.json
aws configservice start-configuration-recorder --configuration-recorder-name default

# Enable VPC Flow Logs (already done in Terraform)
```

### Step 2: Configure WAF

```bash
# Create WAF WebACL
aws wafv2 create-web-acl \
    --name uvis-gps-waf \
    --scope REGIONAL \
    --default-action Allow={} \
    --rules file://waf-rules.json \
    --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=uvis-gps-waf

# Associate with ALB
aws wafv2 associate-web-acl \
    --web-acl-arn $(aws wafv2 list-web-acls --scope REGIONAL --query 'WebACLs[0].ARN' --output text) \
    --resource-arn $(terraform output -raw alb_arn)
```

### Step 3: Scan for Vulnerabilities

```bash
# Scan Docker images
trivy image $(terraform output -raw ecr_backend_url):latest
trivy image $(terraform output -raw ecr_frontend_url):latest

# Check dependencies
cd backend && safety check --file requirements.txt
cd ../frontend && npm audit
```

## Deployment Verification Checklist

### Infrastructure ✅

- [ ] VPC created with 3 AZs
- [ ] Public and private subnets configured
- [ ] NAT Gateways operational
- [ ] Internet Gateway attached
- [ ] Route tables configured
- [ ] Security groups with least privilege
- [ ] ECS Cluster running
- [ ] Application Load Balancer configured
- [ ] Target groups healthy
- [ ] RDS instance running and accessible
- [ ] Redis cluster running
- [ ] S3 buckets created with encryption
- [ ] ECR repositories created
- [ ] CloudWatch alarms configured
- [ ] IAM roles and policies created

### SSL/TLS ✅

- [ ] SSL certificate issued and validated
- [ ] HTTPS listener configured on ALB
- [ ] HTTP redirects to HTTPS
- [ ] Security headers configured
- [ ] Strong SSL ciphers configured

### Application ✅

- [ ] Backend container running
- [ ] Frontend container running
- [ ] Database migrations applied
- [ ] Initial data seeded
- [ ] Health checks passing
- [ ] API endpoints accessible
- [ ] WebSocket connections working
- [ ] Frontend loads correctly
- [ ] User authentication working
- [ ] API rate limiting configured

### DNS ✅

- [ ] Domain points to ALB
- [ ] www subdomain configured
- [ ] DNS resolution working
- [ ] SSL certificate matches domain

### Monitoring ✅

- [ ] Elasticsearch running
- [ ] Logstash processing logs
- [ ] Kibana accessible
- [ ] Filebeat shipping logs
- [ ] Metricbeat collecting metrics
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards configured
- [ ] Alertmanager configured
- [ ] CloudWatch alarms active
- [ ] Log aggregation working

### Backup ✅

- [ ] Automated backups configured
- [ ] Manual backup tested
- [ ] Backup uploaded to S3
- [ ] Backup integrity verified
- [ ] Restore procedure tested
- [ ] Backup retention policy set
- [ ] Cross-region replication enabled (if configured)

### Security ✅

- [ ] Database passwords changed
- [ ] Secrets stored in Secrets Manager
- [ ] Security groups follow least privilege
- [ ] VPC Flow Logs enabled
- [ ] GuardDuty enabled
- [ ] WAF configured (optional)
- [ ] Container images scanned
- [ ] Dependencies checked for vulnerabilities
- [ ] Firewall rules configured
- [ ] Fail2ban configured (if applicable)

### Performance ✅

- [ ] Auto-scaling configured
- [ ] CloudFront CDN configured (optional)
- [ ] Database connection pooling enabled
- [ ] Redis caching working
- [ ] Static assets cached
- [ ] Gzip compression enabled

## Post-Deployment Tasks

### Day 1

1. **Monitor Application**
   ```bash
   # Check CloudWatch metrics
   aws cloudwatch get-metric-statistics \
       --namespace AWS/ECS \
       --metric-name CPUUtilization \
       --dimensions Name=ServiceName,Value=uvis-gps-prod-backend \
       --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
       --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
       --period 300 \
       --statistics Average
   ```

2. **Review Logs**
   ```bash
   # Backend logs
   aws logs tail /ecs/uvis-gps-prod-backend --follow
   
   # Frontend logs
   aws logs tail /ecs/uvis-gps-prod-frontend --follow
   ```

3. **Test Key Flows**
   - User registration
   - User login
   - Create dispatch
   - Vehicle tracking
   - Temperature monitoring
   - Alerts

### Week 1

1. **Performance Optimization**
   - Review slow queries
   - Optimize database indices
   - Adjust auto-scaling thresholds
   - Fine-tune cache settings

2. **Security Review**
   - Review security group rules
   - Check GuardDuty findings
   - Review CloudTrail logs
   - Analyze VPC Flow Logs

3. **Backup Verification**
   - Verify daily backups
   - Test restore procedure
   - Check backup retention

### Month 1

1. **Cost Optimization**
   - Review AWS Cost Explorer
   - Identify unused resources
   - Right-size instances
   - Enable Reserved Instances / Savings Plans

2. **Disaster Recovery Drill**
   - Test full restore
   - Verify RTO/RPO
   - Update DR documentation

3. **User Feedback**
   - Collect user feedback
   - Address issues
   - Plan improvements

## Rollback Procedures

### Rollback Application

```bash
# List previous task definitions
aws ecs list-task-definitions --family-prefix uvis-gps-prod-backend

# Update service with previous task definition
aws ecs update-service \
    --cluster uvis-gps-prod \
    --service uvis-gps-prod-backend \
    --task-definition uvis-gps-prod-backend:PREVIOUS_VERSION

# Or use rollback script
./infrastructure/scripts/rollback.sh backend
```

### Rollback Database

```bash
# List available backups
aws s3 ls s3://uvis-gps-backups-prod/database/ --recursive

# Restore from backup
./infrastructure/scripts/restore.sh database/2026-01-28/backup.sql.gz --from-s3
```

### Rollback Infrastructure

```bash
# Revert to previous Terraform state
cd infrastructure/terraform
terraform state list
terraform state pull > current-state.json

# Apply previous configuration
git checkout <previous-commit>
terraform apply -auto-approve

# Or restore from Terraform Cloud/Backend
```

## Troubleshooting

### Issue: ECS Tasks Not Starting

**Symptoms**: Tasks start and immediately stop

**Debugging**:
```bash
# Check task logs
aws logs tail /ecs/uvis-gps-prod-backend --follow

# Check task stopped reason
aws ecs describe-tasks \
    --cluster uvis-gps-prod \
    --tasks <task-id> \
    --query 'tasks[0].stoppedReason'
```

**Common Causes**:
- Missing environment variables
- Database connection failed
- Port conflicts
- Insufficient memory/CPU

### Issue: ALB Health Checks Failing

**Symptoms**: Targets marked as unhealthy

**Debugging**:
```bash
# Check target health
aws elbv2 describe-target-health \
    --target-group-arn $(terraform output -raw backend_target_group_arn)

# Check health endpoint
curl http://<task-private-ip>:8000/health
```

**Common Causes**:
- Application not listening on correct port
- Health check path incorrect
- Security group blocking health checks
- Application startup time too long

### Issue: Database Connection Errors

**Symptoms**: Application cannot connect to database

**Debugging**:
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier uvis-gps-prod-db

# Test connection
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U postgres -d uvis_gps -c '\l'

# Check security group
aws ec2 describe-security-groups --group-ids <rds-security-group-id>
```

**Common Causes**:
- Security group not allowing connection
- Incorrect credentials
- Database not initialized
- Network configuration issues

## Support and Contacts

### Internal Team
- **DevOps Lead**: devops@example.com
- **Backend Lead**: backend@example.com
- **Frontend Lead**: frontend@example.com
- **Security Lead**: security@example.com

### External Support
- **AWS Support**: AWS Console
- **GitHub Support**: support@github.com
- **Domain Registrar**: support@domain-registrar.com

## Additional Resources

- [Infrastructure Documentation](terraform/README.md)
- [CI/CD Documentation](CI-CD.md)
- [Monitoring Documentation](monitoring/MONITORING.md)
- [Logging Documentation](logging/LOGGING.md)
- [Backup Documentation](BACKUP_DR.md)
- [Security Documentation](SECURITY.md)
- [API Documentation](http://example.com/docs)

---

**Last Updated**: 2026-01-28  
**Version**: 1.0.0  
**Author**: GenSpark AI Developer
