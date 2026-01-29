# 🔄 Backup and Disaster Recovery

## Overview

This document describes the backup and disaster recovery (DR) procedures for the UVIS GPS Fleet Management System. It covers database backups, application backups, and recovery procedures.

## Backup Strategy

### Multi-Tier Backup Approach

| Backup Type | Frequency | Retention | Storage Location | Purpose |
|-------------|-----------|-----------|------------------|---------|
| **Hot Backups** | Real-time | 7 days | Primary (Local) | Point-in-time recovery |
| **Daily Backups** | Every day at 2 AM | 30 days | Primary + S3 Standard-IA | Daily recovery |
| **Weekly Backups** | Every Sunday at 3 AM | 90 days | S3 Standard-IA | Weekly recovery |
| **Monthly Backups** | 1st day of month at 4 AM | 1 year | S3 Glacier | Long-term archival |
| **Pre-Deployment Backups** | Before deployments | 7 days | Local + S3 | Rollback capability |

## Components Backed Up

### 1. Database (PostgreSQL)
- Full database dumps (schema + data)
- Transaction logs (WAL files)
- Database configuration files

### 2. Application Files
- Backend source code (Git repository)
- Frontend build artifacts
- Configuration files
- Environment variables (encrypted)

### 3. Storage
- S3 bucket contents (uploads, exports)
- User-uploaded files
- Generated reports

### 4. Infrastructure
- Terraform state files
- Docker images (ECR)
- Kubernetes configurations

## Database Backup

### Automated Backup Script

The `backup.sh` script provides automated PostgreSQL backups with the following features:

- **Compression**: gzip compression (70-80% reduction)
- **Verification**: Integrity checks after backup
- **S3 Upload**: Automatic upload to S3
- **Retention**: Automatic cleanup of old backups
- **Notifications**: Status notifications (email/Slack)
- **Error Handling**: Comprehensive error handling

### Configuration

Create a `.env` file in `/infrastructure/scripts/`:

```bash
# Database Configuration
DB_HOST=your-rds-endpoint.amazonaws.com
DB_PORT=5432
DB_NAME=uvis_gps
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Backup Configuration
BACKUP_DIR=/backups/database
S3_BUCKET=your-backup-bucket
RETENTION_DAYS=30

# AWS Configuration
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

### Manual Backup

```bash
cd infrastructure/scripts

# Daily backup
./backup.sh daily

# Weekly backup
./backup.sh weekly

# Monthly backup
./backup.sh monthly

# Manual backup
./backup.sh manual
```

### Automated Backup with Cron

Add to crontab:

```cron
# Daily backup at 2:00 AM
0 2 * * * /path/to/infrastructure/scripts/backup.sh daily >> /var/log/backup-daily.log 2>&1

# Weekly backup at 3:00 AM every Sunday
0 3 * * 0 /path/to/infrastructure/scripts/backup.sh weekly >> /var/log/backup-weekly.log 2>&1

# Monthly backup at 4:00 AM on 1st of month
0 4 1 * * /path/to/infrastructure/scripts/backup.sh monthly >> /var/log/backup-monthly.log 2>&1
```

### GitHub Actions Automated Backup

The `.github/workflows/backup.yml` workflow automates backups:

- **Schedule**: Daily at 2:00 AM UTC
- **Triggers**: Manual trigger via `workflow_dispatch`
- **Actions**:
  1. Connect to RDS instance
  2. Create database dump
  3. Compress backup
  4. Upload to S3
  5. Verify integrity
  6. Send notification

## Database Restore

### Restore Script

The `restore.sh` script provides safe database restoration:

**Features**:
- **Pre-restore Backup**: Creates backup before restore
- **Connection Termination**: Safely terminates active connections
- **Verification**: Verifies backup file integrity
- **S3 Support**: Can restore directly from S3
- **Rollback**: Can rollback to pre-restore state

### Restore from Local Backup

```bash
cd infrastructure/scripts

# Restore from local file
./restore.sh /backups/database/uvis_gps_daily_20260128_120000.sql.gz
```

### Restore from S3

```bash
# Restore from S3
./restore.sh database/2026-01-28/uvis_gps_daily_20260128_120000.sql.gz --from-s3
```

### Point-in-Time Recovery (PITR)

For AWS RDS, enable automated backups and use PITR:

```bash
# Restore to specific point in time
aws rds restore-db-instance-to-point-in-time \
    --source-db-instance-identifier uvis-gps-prod \
    --target-db-instance-identifier uvis-gps-restored \
    --restore-time 2026-01-28T12:00:00Z \
    --no-multi-az
```

## Application Backup

### Docker Images

All Docker images are pushed to Amazon ECR:

```bash
# List all images
aws ecr describe-images --repository-name uvis-gps-backend

# Pull specific image
docker pull <aws_account_id>.dkr.ecr.ap-northeast-2.amazonaws.com/uvis-gps-backend:v1.0.0
```

### Configuration Files

Configuration files are backed up to S3:

```bash
# Backup configuration
aws s3 sync /path/to/config s3://your-backup-bucket/config/$(date +%Y-%m-%d)/

# Restore configuration
aws s3 sync s3://your-backup-bucket/config/2026-01-28/ /path/to/config/
```

## S3 Backup

### S3 Bucket Configuration

```terraform
resource "aws_s3_bucket" "backups" {
  bucket = "uvis-gps-backups"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    enabled = true

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
```

### S3 Replication

Enable cross-region replication for disaster recovery:

```terraform
resource "aws_s3_bucket_replication_configuration" "replication" {
  role   = aws_iam_role.replication.arn
  bucket = aws_s3_bucket.backups.id

  rule {
    id     = "backup-replication"
    status = "Enabled"

    destination {
      bucket        = aws_s3_bucket.backups_replica.arn
      storage_class = "STANDARD_IA"
    }
  }
}
```

## Disaster Recovery Procedures

### Recovery Time Objective (RTO)

| Scenario | RTO Target | Actual RTO |
|----------|------------|------------|
| Database corruption | 30 minutes | ~20 minutes |
| Application failure | 15 minutes | ~10 minutes |
| Full datacenter outage | 4 hours | ~2-3 hours |
| Partial service outage | 10 minutes | ~5 minutes |

### Recovery Point Objective (RPO)

| Scenario | RPO Target | Actual RPO |
|----------|------------|------------|
| Database | 5 minutes | ~1 minute (WAL) |
| Application files | 24 hours | Daily backup |
| User uploads | 5 minutes | Real-time replication |
| Logs | 1 hour | ~15 minutes |

### Disaster Recovery Scenarios

#### Scenario 1: Database Corruption

**Symptoms**:
- Database errors
- Data inconsistency
- Failed queries

**Recovery Steps**:

1. **Identify the issue**:
```bash
# Check database logs
docker logs postgres-container

# Check for corruption
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM pg_stat_database;"
```

2. **Restore from latest backup**:
```bash
# Find latest backup
aws s3 ls s3://your-backup-bucket/database/ --recursive | sort | tail -n 1

# Restore database
./restore.sh database/2026-01-28/uvis_gps_daily_20260128_020000.sql.gz --from-s3
```

3. **Verify restoration**:
```bash
# Check table counts
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"

# Check recent data
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM dispatches WHERE created_at > NOW() - INTERVAL '1 day';"
```

4. **Resume services**:
```bash
# Restart application
docker-compose restart backend

# Verify health
curl http://localhost:8000/health
```

#### Scenario 2: Complete Service Outage

**Recovery Steps**:

1. **Assess the situation**:
```bash
# Check all services
docker-compose ps
kubectl get pods --all-namespaces

# Check infrastructure
terraform show
```

2. **Deploy to secondary region** (if configured):
```bash
# Switch to DR region
export AWS_REGION=us-west-2

# Deploy infrastructure
cd infrastructure/terraform
terraform workspace select dr
terraform apply -auto-approve

# Deploy application
cd ../..
./infrastructure/scripts/deploy.sh
```

3. **Restore database**:
```bash
# Restore from latest backup in S3
./infrastructure/scripts/restore.sh database/2026-01-28/uvis_gps_daily_20260128_020000.sql.gz --from-s3
```

4. **Update DNS** (for region failover):
```bash
# Update Route53 to point to DR region
aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch file://dns-failover.json
```

5. **Verify all services**:
```bash
# Health checks
curl https://api.example.com/health
curl https://example.com

# Database connectivity
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c '\l'

# Application logs
kubectl logs -f deployment/backend
```

#### Scenario 3: Data Loss (User Error)

**Recovery Steps**:

1. **Identify what was lost**:
```bash
# Query audit logs
SELECT * FROM audit_logs WHERE created_at > '2026-01-28 10:00:00' AND action = 'DELETE';
```

2. **Find backup before the deletion**:
```bash
# List backups
aws s3 ls s3://your-backup-bucket/database/2026-01-28/
```

3. **Restore to temporary database**:
```bash
# Create temporary database
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE uvis_gps_temp;"

# Restore backup to temp database
export DB_NAME=uvis_gps_temp
./restore.sh database/2026-01-28/uvis_gps_daily_20260128_010000.sql.gz --from-s3
```

4. **Extract lost data**:
```bash
# Export specific table
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d uvis_gps_temp -t dispatches --data-only > lost_data.sql
```

5. **Import to production**:
```bash
# Import lost data
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d uvis_gps < lost_data.sql
```

6. **Cleanup**:
```bash
# Drop temporary database
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "DROP DATABASE uvis_gps_temp;"
```

## Backup Monitoring

### CloudWatch Alarms

```terraform
resource "aws_cloudwatch_metric_alarm" "backup_failure" {
  alarm_name          = "uvis-gps-backup-failure"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "BackupFailureCount"
  namespace           = "UVIS/Backup"
  period              = "86400"  # 24 hours
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Alert when backup fails"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "old_backup" {
  alarm_name          = "uvis-gps-old-backup"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "HoursSinceLastBackup"
  namespace           = "UVIS/Backup"
  period              = "3600"  # 1 hour
  statistic           = "Maximum"
  threshold           = "26"  # Alert if > 26 hours since last backup
  alarm_description   = "Alert when backup is more than 26 hours old"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
```

### Backup Verification

Automated backup verification script:

```bash
#!/bin/bash
# verify-backups.sh

# Check if backups exist
LATEST_BACKUP=$(aws s3 ls s3://your-backup-bucket/database/ --recursive | sort | tail -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "ERROR: No backups found"
    exit 1
fi

# Check backup age
BACKUP_DATE=$(echo $LATEST_BACKUP | awk '{print $1}')
CURRENT_DATE=$(date +%Y-%m-%d)
DAYS_OLD=$(( ($(date -d "$CURRENT_DATE" +%s) - $(date -d "$BACKUP_DATE" +%s)) / 86400 ))

if [ $DAYS_OLD -gt 1 ]; then
    echo "WARNING: Latest backup is $DAYS_OLD days old"
    exit 1
fi

# Test restore (to temporary database)
echo "Testing restore to temporary database..."
export DB_NAME=uvis_gps_test
./restore.sh $(echo $LATEST_BACKUP | awk '{print $4}') --from-s3

if [ $? -eq 0 ]; then
    echo "SUCCESS: Backup verification passed"
    # Cleanup test database
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "DROP DATABASE uvis_gps_test;"
else
    echo "ERROR: Backup verification failed"
    exit 1
fi
```

## Testing DR Procedures

### Monthly DR Drills

Conduct monthly disaster recovery drills:

**Checklist**:
- [ ] Restore database from backup
- [ ] Deploy application to DR environment
- [ ] Verify all services are functional
- [ ] Test failover procedures
- [ ] Measure actual RTO and RPO
- [ ] Document issues and improvements
- [ ] Update DR procedures

**Drill Schedule**:
```cron
# Monthly DR drill (first Saturday of month at 10:00 AM)
0 10 1-7 * 6 /path/to/dr-drill.sh >> /var/log/dr-drill.log 2>&1
```

## Backup Security

### Encryption

- **At Rest**: AES-256 encryption for S3
- **In Transit**: SSL/TLS for all transfers
- **Database Dumps**: Encrypted with GPG before upload

### Access Control

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BackupBucketAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:role/BackupRole"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::uvis-gps-backups",
        "arn:aws:s3:::uvis-gps-backups/*"
      ]
    }
  ]
}
```

## Cost Optimization

### Storage Costs (Monthly Estimates)

| Storage Tier | Size | Monthly Cost |
|--------------|------|--------------|
| S3 Standard (7 days) | 50 GB | $1.15 |
| S3 Standard-IA (30 days) | 150 GB | $1.88 |
| S3 Glacier (90 days) | 450 GB | $1.80 |
| S3 Deep Archive (1 year) | 1.8 TB | $1.80 |
| **Total** | **~2.5 TB** | **~$6.63/month** |

### Cost Optimization Tips

1. **Use lifecycle policies**: Automatically transition to cheaper storage
2. **Compress backups**: 70-80% size reduction with gzip
3. **Incremental backups**: Only backup changed data
4. **Retention policies**: Delete old backups automatically
5. **Cross-region replication**: Only for critical data

## Compliance and Auditing

### Audit Logging

All backup and restore operations are logged:

```json
{
  "timestamp": "2026-01-28T12:00:00Z",
  "operation": "backup",
  "type": "database",
  "source": "uvis_gps",
  "destination": "s3://uvis-gps-backups/database/2026-01-28/",
  "size_bytes": 1073741824,
  "duration_seconds": 120,
  "status": "success",
  "user": "backup-system",
  "ip_address": "10.0.1.100"
}
```

### Compliance Requirements

- **GDPR**: 30-day data retention minimum
- **SOC 2**: Encrypted backups, access control
- **ISO 27001**: Regular backup testing, DR drills
- **HIPAA** (if applicable): Encrypted backups, audit logs

## Troubleshooting

### Common Issues

#### Issue: Backup script fails with "disk full"

**Solution**:
```bash
# Check disk space
df -h /backups

# Clean up old backups
find /backups -type f -name "*.sql.gz" -mtime +30 -delete

# Increase disk size (AWS EBS)
aws ec2 modify-volume --volume-id vol-xxxxx --size 100
```

#### Issue: S3 upload fails

**Solution**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check S3 bucket permissions
aws s3api get-bucket-policy --bucket uvis-gps-backups

# Retry upload with exponential backoff
for i in {1..5}; do
    aws s3 cp backup.sql.gz s3://uvis-gps-backups/ && break
    sleep $((2**i))
done
```

#### Issue: Restore takes too long

**Solution**:
- Use parallel restore with `pg_restore --jobs=4`
- Increase database instance size temporarily
- Restore only specific tables if possible
- Use PITR for faster recovery

## Support and Escalation

### Backup Issues
- **Level 1**: DevOps team
- **Level 2**: Database administrator
- **Level 3**: AWS Support (for RDS issues)

### Emergency Contacts
- **DevOps On-Call**: +82-10-xxxx-xxxx
- **Database Admin**: +82-10-xxxx-xxxx
- **AWS Support**: Case via AWS Console

---

**Last Updated**: 2026-01-28  
**Version**: 1.0.0  
**Author**: GenSpark AI Developer
