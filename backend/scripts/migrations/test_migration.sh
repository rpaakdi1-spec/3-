#!/bin/bash
# Test migration on a copy of the database

set -e

echo "🧪 Testing migration (dry-run)..."
echo ""
echo "📊 Current migration status:"
docker exec uvis-backend alembic current
echo ""
echo "📋 Pending migrations:"
docker exec uvis-backend alembic upgrade head --sql | head -50
echo ""
echo "⚠️  This is a dry-run. No changes were made to the database."
echo ""
echo "To apply migrations, run: ./scripts/migrations/apply_migration.sh"
