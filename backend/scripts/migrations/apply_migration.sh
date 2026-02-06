#!/bin/bash
# Apply pending migrations to database

set -e

echo "📊 Checking current migration status..."
docker exec uvis-backend alembic current
echo ""

echo "📋 Pending migrations:"
docker exec uvis-backend alembic show head
echo ""

read -p "Apply all pending migrations? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Applying migrations..."
    docker exec uvis-backend alembic upgrade head
    echo ""
    echo "✅ Migrations applied successfully!"
    echo ""
    echo "📊 Current migration status:"
    docker exec uvis-backend alembic current
else
    echo "❌ Migration cancelled"
fi
