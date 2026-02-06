#!/bin/bash
# Rollback last migration

set -e

echo "⚠️  WARNING: This will rollback the last migration!"
echo ""
echo "📊 Current migration status:"
docker exec uvis-backend alembic current
echo ""

read -p "Rollback one migration? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Rolling back..."
    docker exec uvis-backend alembic downgrade -1
    echo ""
    echo "✅ Rollback completed!"
    echo ""
    echo "📊 Current migration status:"
    docker exec uvis-backend alembic current
else
    echo "❌ Rollback cancelled"
fi
