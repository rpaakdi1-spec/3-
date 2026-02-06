# Database Migration Guide

## Quick Start

### When adding Phase features:

1. Modify models in backend/app/models/
2. Create migration: `./backend/scripts/migrations/create_migration.sh "description"`
3. Backup: `./backend/scripts/migrations/backup_before_migration.sh`
4. Test: `./backend/scripts/migrations/test_migration.sh`
5. Apply: `./backend/scripts/migrations/apply_migration.sh`
6. Rollback if needed: `./backend/scripts/migrations/rollback_migration.sh`

## Current Status
- Baseline: baseline_20260206
- Database: Alembic-managed
- Backups: /root/uvis/backups/

## Important Files
- Migrations: /root/uvis/backend/alembic/versions/
- Scripts: /root/uvis/backend/scripts/migrations/
- Database config: /root/uvis/backend/app/core/database.py

Created: 2026-02-06
