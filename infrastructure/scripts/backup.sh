#!/bin/bash

###############################################################################
# UVIS GPS Fleet Management - Database Backup Script
# 
# Description: Automated backup script for PostgreSQL database
# Usage: ./backup.sh [daily|weekly|monthly|manual]
# Environment Variables:
#   - DB_HOST: Database host (default: localhost)
#   - DB_PORT: Database port (default: 5432)
#   - DB_NAME: Database name (required)
#   - DB_USER: Database user (required)
#   - DB_PASSWORD: Database password (required)
#   - BACKUP_DIR: Backup directory (default: /backups/database)
#   - S3_BUCKET: S3 bucket for backup storage (optional)
#   - RETENTION_DAYS: Days to keep backups (default: 30)
###############################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-uvis_gps}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-}"
BACKUP_DIR="${BACKUP_DIR:-/backups/database}"
S3_BUCKET="${S3_BUCKET:-}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
BACKUP_TYPE="${1:-daily}"

# Timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE=$(date +"%Y-%m-%d")

# Backup file names
BACKUP_FILENAME="${DB_NAME}_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"

# Log function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} ${timestamp} - ${message}"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - ${message}"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} ${timestamp} - ${message}"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} ${timestamp} - ${message}"
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    # Check if pg_dump is installed
    if ! command -v pg_dump &> /dev/null; then
        log ERROR "pg_dump is not installed. Please install PostgreSQL client tools."
        exit 1
    fi
    
    # Check if gzip is installed
    if ! command -v gzip &> /dev/null; then
        log ERROR "gzip is not installed. Please install gzip."
        exit 1
    fi
    
    # Check if AWS CLI is installed (if S3 backup is enabled)
    if [ -n "$S3_BUCKET" ] && ! command -v aws &> /dev/null; then
        log WARNING "AWS CLI is not installed. S3 backup will be skipped."
        S3_BUCKET=""
    fi
    
    # Check database connection
    if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' &> /dev/null; then
        log ERROR "Cannot connect to database: $DB_NAME@$DB_HOST:$DB_PORT"
        exit 1
    fi
    
    log SUCCESS "All prerequisites met"
}

# Create backup directory
create_backup_directory() {
    log INFO "Creating backup directory: $BACKUP_DIR"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        log SUCCESS "Backup directory created"
    else
        log INFO "Backup directory already exists"
    fi
}

# Perform database backup
perform_backup() {
    log INFO "Starting database backup: $BACKUP_FILENAME"
    log INFO "Database: $DB_NAME, Host: $DB_HOST, Port: $DB_PORT"
    
    # Get database size
    DB_SIZE=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" | xargs)
    log INFO "Database size: $DB_SIZE"
    
    # Perform backup with progress
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --format=plain \
        --no-owner \
        --no-acl \
        | gzip > "$BACKUP_PATH"
    
    if [ $? -eq 0 ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
        log SUCCESS "Backup completed: $BACKUP_PATH (Size: $BACKUP_SIZE)"
    else
        log ERROR "Backup failed"
        exit 1
    fi
}

# Upload to S3
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log INFO "S3 backup is not configured. Skipping..."
        return
    fi
    
    log INFO "Uploading backup to S3: s3://$S3_BUCKET/database/$DATE/$BACKUP_FILENAME"
    
    aws s3 cp "$BACKUP_PATH" "s3://$S3_BUCKET/database/$DATE/$BACKUP_FILENAME" \
        --storage-class STANDARD_IA \
        --server-side-encryption AES256
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Backup uploaded to S3"
    else
        log ERROR "Failed to upload backup to S3"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log INFO "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Cleanup local backups
    find "$BACKUP_DIR" -name "${DB_NAME}_${BACKUP_TYPE}_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    local deleted_count=$(find "$BACKUP_DIR" -name "${DB_NAME}_${BACKUP_TYPE}_*.sql.gz" -mtime +$RETENTION_DAYS 2>/dev/null | wc -l || echo 0)
    
    if [ $deleted_count -gt 0 ]; then
        log SUCCESS "Deleted $deleted_count old local backups"
    else
        log INFO "No old local backups to delete"
    fi
    
    # Cleanup S3 backups (if configured)
    if [ -n "$S3_BUCKET" ]; then
        log INFO "Cleaning up S3 backups older than $RETENTION_DAYS days..."
        
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d)
        
        aws s3 ls "s3://$S3_BUCKET/database/" --recursive | \
            awk '{print $4}' | \
            while read key; do
                file_date=$(echo "$key" | grep -oP '\d{4}-\d{2}-\d{2}' | head -1)
                if [ -n "$file_date" ] && [ "$file_date" \< "$cutoff_date" ]; then
                    aws s3 rm "s3://$S3_BUCKET/$key"
                    log INFO "Deleted old S3 backup: $key"
                fi
            done
    fi
}

# Verify backup integrity
verify_backup() {
    log INFO "Verifying backup integrity..."
    
    # Check if file exists and is not empty
    if [ ! -s "$BACKUP_PATH" ]; then
        log ERROR "Backup file is empty or does not exist"
        exit 1
    fi
    
    # Test gzip integrity
    if gzip -t "$BACKUP_PATH" &> /dev/null; then
        log SUCCESS "Backup file integrity verified"
    else
        log ERROR "Backup file is corrupted"
        exit 1
    fi
}

# Send notification (placeholder for email/Slack integration)
send_notification() {
    local status=$1
    local message=$2
    
    # TODO: Implement email/Slack notification
    # Example: Send to Slack webhook
    # curl -X POST -H 'Content-type: application/json' \
    #     --data "{\"text\":\"$message\"}" \
    #     "$SLACK_WEBHOOK_URL"
    
    log INFO "Notification: $message"
}

# Main execution
main() {
    log INFO "=== UVIS GPS Database Backup Script ==="
    log INFO "Backup Type: $BACKUP_TYPE"
    log INFO "Timestamp: $TIMESTAMP"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup directory
    create_backup_directory
    
    # Perform backup
    perform_backup
    
    # Verify backup
    verify_backup
    
    # Upload to S3
    upload_to_s3 || log WARNING "S3 upload failed, but local backup is available"
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Send success notification
    send_notification "success" "Database backup completed successfully: $BACKUP_FILENAME"
    
    log SUCCESS "=== Backup process completed ==="
    echo ""
    log INFO "Backup location: $BACKUP_PATH"
    
    if [ -n "$S3_BUCKET" ]; then
        log INFO "S3 location: s3://$S3_BUCKET/database/$DATE/$BACKUP_FILENAME"
    fi
}

# Error handler
error_handler() {
    log ERROR "Backup script failed at line $1"
    send_notification "error" "Database backup failed at line $1"
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR

# Run main function
main

exit 0
