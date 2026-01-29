#!/bin/bash
# Automated Backup Script for Cold Chain Delivery System
# Backs up PostgreSQL database and Redis data

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

# Database credentials from environment
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-coldchain_user}"
POSTGRES_DB="${POSTGRES_DB:-coldchain_prod}"

# Create backup directories
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/redis"
mkdir -p "$BACKUP_DIR/uploads"
mkdir -p "$BACKUP_DIR/logs"

echo "=========================================="
echo "Cold Chain Backup - $TIMESTAMP"
echo "=========================================="

# ==================== PostgreSQL Backup ====================
echo "Backing up PostgreSQL database..."
PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -F c \
    -f "$BACKUP_DIR/database/postgres_${TIMESTAMP}.dump"

# Compress the dump
gzip "$BACKUP_DIR/database/postgres_${TIMESTAMP}.dump"
echo "✓ PostgreSQL backup completed: postgres_${TIMESTAMP}.dump.gz"

# ==================== Redis Backup ====================
echo "Backing up Redis data..."
docker exec coldchain-redis-prod redis-cli --raw SAVE
docker cp coldchain-redis-prod:/data/dump.rdb "$BACKUP_DIR/redis/redis_${TIMESTAMP}.rdb"
gzip "$BACKUP_DIR/redis/redis_${TIMESTAMP}.rdb"
echo "✓ Redis backup completed: redis_${TIMESTAMP}.rdb.gz"

# ==================== Upload Files Backup ====================
echo "Backing up upload files..."
if [ -d "/app/data/uploads" ]; then
    tar -czf "$BACKUP_DIR/uploads/uploads_${TIMESTAMP}.tar.gz" -C /app/data uploads
    echo "✓ Upload files backup completed: uploads_${TIMESTAMP}.tar.gz"
else
    echo "⚠ Upload directory not found, skipping"
fi

# ==================== Application Logs Backup ====================
echo "Backing up application logs..."
if [ -d "/app/logs" ]; then
    tar -czf "$BACKUP_DIR/logs/logs_${DATE}.tar.gz" -C /app logs
    echo "✓ Logs backup completed: logs_${DATE}.tar.gz"
else
    echo "⚠ Logs directory not found, skipping"
fi

# ==================== Backup Summary ====================
echo ""
echo "Backup Summary:"
echo "----------------------------------------"
du -sh "$BACKUP_DIR/database/postgres_${TIMESTAMP}.dump.gz"
du -sh "$BACKUP_DIR/redis/redis_${TIMESTAMP}.rdb.gz"
[ -f "$BACKUP_DIR/uploads/uploads_${TIMESTAMP}.tar.gz" ] && du -sh "$BACKUP_DIR/uploads/uploads_${TIMESTAMP}.tar.gz"
[ -f "$BACKUP_DIR/logs/logs_${DATE}.tar.gz" ] && du -sh "$BACKUP_DIR/logs/logs_${DATE}.tar.gz"

# ==================== Cleanup Old Backups ====================
echo ""
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR/database" -name "*.gz" -mtime +"$RETENTION_DAYS" -delete
find "$BACKUP_DIR/redis" -name "*.gz" -mtime +"$RETENTION_DAYS" -delete
find "$BACKUP_DIR/uploads" -name "*.tar.gz" -mtime +"$RETENTION_DAYS" -delete
find "$BACKUP_DIR/logs" -name "*.tar.gz" -mtime +"$RETENTION_DAYS" -delete
echo "✓ Cleanup completed"

# ==================== Upload to S3 (Optional) ====================
if [ -n "$BACKUP_S3_BUCKET" ] && command -v aws &> /dev/null; then
    echo ""
    echo "Uploading backups to S3..."
    aws s3 sync "$BACKUP_DIR" "s3://$BACKUP_S3_BUCKET/coldchain-backups/" \
        --exclude "*" \
        --include "database/postgres_${TIMESTAMP}.dump.gz" \
        --include "redis/redis_${TIMESTAMP}.rdb.gz" \
        --storage-class STANDARD_IA
    echo "✓ S3 upload completed"
fi

# ==================== Backup Verification ====================
echo ""
echo "Verifying backups..."
if [ -f "$BACKUP_DIR/database/postgres_${TIMESTAMP}.dump.gz" ]; then
    SIZE=$(stat -f%z "$BACKUP_DIR/database/postgres_${TIMESTAMP}.dump.gz" 2>/dev/null || stat -c%s "$BACKUP_DIR/database/postgres_${TIMESTAMP}.dump.gz")
    if [ "$SIZE" -gt 1024 ]; then
        echo "✓ Database backup verified (size: $SIZE bytes)"
    else
        echo "✗ Database backup too small, may be corrupted"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Backup completed successfully!"
echo "Timestamp: $TIMESTAMP"
echo "=========================================="
