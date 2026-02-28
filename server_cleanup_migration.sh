#!/bin/bash
# Run this script ON THE SERVER to clean up duplicate migrations

echo "=========================================="
echo "Server-Side Migration Cleanup"
echo "=========================================="
echo ""

cd /root/uvis

echo "🔍 Step 1: Finding all pending_emp migration files..."
echo ""
find backend/alembic/versions/ -name "*pending*" -type f -ls

echo ""
echo "🔍 Step 2: Checking which files contain pending_emp_001..."
echo ""
grep -l "pending_emp_001" backend/alembic/versions/*.py 2>/dev/null || echo "No files found with pending_emp_001"

echo ""
echo "🔍 Step 3: Checking which files contain pending_emp_20260228_140810..."
echo ""
grep -l "pending_emp_20260228_140810" backend/alembic/versions/*.py 2>/dev/null || echo "No files found with pending_emp_20260228_140810"

echo ""
echo "=========================================="
echo "Action Required:"
echo "=========================================="
echo ""
echo "If you see TWO different files with pending_emp, you need to:"
echo "1. Keep the file: 20260228_133550_add_pending_employees.py (with pending_emp_20260228_140810)"
echo "2. Remove any OTHER file that has pending_emp_001"
echo ""
echo "To remove old files, run:"
echo "  find backend/alembic/versions/ -name '*pending*' ! -name '20260228_133550_add_pending_employees.py' -delete"
echo ""
echo "Or manually:"
echo "  rm backend/alembic/versions/[OLD_FILE_NAME].py"
echo ""
