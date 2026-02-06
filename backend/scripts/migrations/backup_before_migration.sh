#!/bin/bash
# Backup database before applying migrations

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="../../backups/pre_migration_$TIMESTAMP"

echo "📦 Creating backup before migration..."
echo "Backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

echo ""
echo "🔄 Backing up database..."
docker exec uvis-db pg_dump -U uvis_user -d uvis_db > "$BACKUP_DIR/full_backup.sql"
docker exec uvis-db pg_dump -U uvis_user -d uvis_db --schema-only > "$BACKUP_DIR/schema.sql"
docker exec uvis-db pg_dump -U uvis_user -d uvis_db --data-only > "$BACKUP_DIR/data.sql"

echo ""
echo "📊 Backup summary:"
ls -lh "$BACKUP_DIR/"

echo ""
echo "✅ Backup completed!"
echo "Location: $BACKUP_DIR"
