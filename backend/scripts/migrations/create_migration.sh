#!/bin/bash
# Create a new database migration

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <migration_message>"
    echo "Example: $0 'add user phone field'"
    exit 1
fi

MESSAGE="$1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔧 Creating new migration: $MESSAGE"
echo "Timestamp: $TIMESTAMP"
echo ""

# Generate migration
docker exec uvis-backend alembic revision --autogenerate -m "$MESSAGE"

echo ""
echo "✅ Migration created!"
echo ""
echo "📋 Next steps:"
echo "  1. Review the generated migration file in alembic/versions/"
echo "  2. Test the migration: ./scripts/migrations/test_migration.sh"
echo "  3. Apply the migration: ./scripts/migrations/apply_migration.sh"
