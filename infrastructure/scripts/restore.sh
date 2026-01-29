#!/bin/bash

###############################################################################
# UVIS GPS Fleet Management - Database Restore Script
# 
# Description: Restore PostgreSQL database from backup
# Usage: ./restore.sh <backup_file> [--from-s3]
# Environment Variables:
#   - DB_HOST: Database host (default: localhost)
#   - DB_PORT: Database port (default: 5432)
#   - DB_NAME: Database name (required)
#   - DB_USER: Database user (required)
#   - DB_PASSWORD: Database password (required)
#   - S3_BUCKET: S3 bucket for backup storage (optional)
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
S3_BUCKET="${S3_BUCKET:-}"

# Parse arguments
BACKUP_FILE="${1:-}"
FROM_S3=false

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <backup_file> [--from-s3]"
    echo ""
    echo "Examples:"
    echo "  $0 /backups/database/uvis_gps_daily_20260128_120000.sql.gz"
    echo "  $0 database/2026-01-28/uvis_gps_daily_20260128_120000.sql.gz --from-s3"
    exit 1
fi

if [ "${2:-}" == "--from-s3" ]; then
    FROM_S3=true
fi

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

# Confirmation prompt
confirm_restore() {
    log WARNING "⚠️  DATABASE RESTORE WARNING ⚠️"
    log WARNING "This will REPLACE the current database: $DB_NAME"
    log WARNING "Host: $DB_HOST, Port: $DB_PORT"
    log WARNING ""
    log WARNING "Backup file: $BACKUP_FILE"
    log WARNING ""
    
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        log INFO "Restore cancelled by user"
        exit 0
    fi
}

# Download from S3
download_from_s3() {
    log INFO "Downloading backup from S3: s3://$S3_BUCKET/$BACKUP_FILE"
    
    local temp_file="/tmp/$(basename $BACKUP_FILE)"
    
    aws s3 cp "s3://$S3_BUCKET/$BACKUP_FILE" "$temp_file"
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Backup downloaded from S3"
        BACKUP_FILE="$temp_file"
    else
        log ERROR "Failed to download backup from S3"
        exit 1
    fi
}

# Verify backup file
verify_backup_file() {
    log INFO "Verifying backup file..."
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log ERROR "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    if [ ! -s "$BACKUP_FILE" ]; then
        log ERROR "Backup file is empty: $BACKUP_FILE"
        exit 1
    fi
    
    # Test gzip integrity
    if gzip -t "$BACKUP_FILE" &> /dev/null; then
        log SUCCESS "Backup file integrity verified"
    else
        log ERROR "Backup file is corrupted: $BACKUP_FILE"
        exit 1
    fi
}

# Create pre-restore backup
create_pre_restore_backup() {
    log INFO "Creating pre-restore backup of current database..."
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local pre_restore_backup="/tmp/${DB_NAME}_pre_restore_${timestamp}.sql.gz"
    
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=plain \
        --no-owner \
        --no-acl \
        | gzip > "$pre_restore_backup"
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Pre-restore backup created: $pre_restore_backup"
        echo "$pre_restore_backup"
    else
        log ERROR "Failed to create pre-restore backup"
        exit 1
    fi
}

# Terminate active connections
terminate_connections() {
    log INFO "Terminating active database connections..."
    
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "postgres" <<EOF
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
  AND pid <> pg_backend_pid();
EOF
    
    log SUCCESS "Active connections terminated"
}

# Drop and recreate database
recreate_database() {
    log INFO "Dropping and recreating database: $DB_NAME"
    
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "postgres" <<EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
EOF
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Database recreated"
    else
        log ERROR "Failed to recreate database"
        exit 1
    fi
}

# Restore database
restore_database() {
    log INFO "Restoring database from backup..."
    log INFO "This may take a while depending on the database size..."
    
    gunzip -c "$BACKUP_FILE" | PGPASSWORD="$DB_PASSWORD" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --single-transaction
    
    if [ $? -eq 0 ]; then
        log SUCCESS "Database restored successfully"
    else
        log ERROR "Database restore failed"
        exit 1
    fi
}

# Verify restore
verify_restore() {
    log INFO "Verifying database restore..."
    
    # Get table count
    local table_count=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
    
    log INFO "Tables restored: $table_count"
    
    # Get database size
    local db_size=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" | xargs)
    
    log INFO "Database size: $db_size"
    
    log SUCCESS "Database verification completed"
}

# Main execution
main() {
    log INFO "=== UVIS GPS Database Restore Script ==="
    log INFO "Timestamp: $(date)"
    echo ""
    
    # Confirm restore
    confirm_restore
    
    # Download from S3 if needed
    if [ "$FROM_S3" = true ]; then
        download_from_s3
    fi
    
    # Verify backup file
    verify_backup_file
    
    # Create pre-restore backup
    PRE_RESTORE_BACKUP=$(create_pre_restore_backup)
    
    # Terminate active connections
    terminate_connections
    
    # Drop and recreate database
    recreate_database
    
    # Restore database
    restore_database
    
    # Verify restore
    verify_restore
    
    log SUCCESS "=== Database restore completed ==="
    echo ""
    log INFO "Restored from: $BACKUP_FILE"
    log INFO "Pre-restore backup: $PRE_RESTORE_BACKUP"
    log INFO ""
    log INFO "To rollback to pre-restore state, run:"
    log INFO "./restore.sh $PRE_RESTORE_BACKUP"
}

# Error handler
error_handler() {
    log ERROR "Restore script failed at line $1"
    
    if [ -n "${PRE_RESTORE_BACKUP:-}" ]; then
        log INFO "You can restore to the pre-restore state by running:"
        log INFO "./restore.sh $PRE_RESTORE_BACKUP"
    fi
    
    exit 1
}

# Set error trap
trap 'error_handler $LINENO' ERR

# Run main function
main

exit 0
