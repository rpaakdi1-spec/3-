#!/bin/bash

# Fix duplicate revision ID by generating a unique one

echo "=========================================="
echo "Fix Duplicate Revision ID"
echo "=========================================="
echo ""

# Generate a unique revision ID
NEW_REVISION="pending_emp_$(date +%Y%m%d_%H%M%S)"

echo "📝 Old revision ID: pending_emp_001"
echo "📝 New revision ID: $NEW_REVISION"
echo ""

# Update the migration file
sed -i "s/revision = 'pending_emp_001'/revision = '$NEW_REVISION'/" backend/alembic/versions/20260228_133550_add_pending_employees.py

echo "✅ Updated migration file"
echo ""

# Show the change
grep "^revision" backend/alembic/versions/20260228_133550_add_pending_employees.py

echo ""
echo "=========================================="
echo "Next steps:"
echo "1. Commit and push the change"
echo "2. Pull on server"
echo "3. Run migration again"
echo "=========================================="
