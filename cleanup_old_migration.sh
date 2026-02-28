#!/bin/bash

echo "=========================================="
echo "Cleanup Old Migration Files"
echo "=========================================="
echo ""

echo "🔍 Step 1: Finding duplicate pending_emp migrations..."
echo ""

# Find all files with pending_emp in the name
echo "Files to check:"
find backend/alembic/versions/ -name "*pending*" -type f 2>/dev/null

echo ""
echo "=========================================="
echo "Server Instructions:"
echo "=========================================="
echo ""
echo "On the server, run these commands to find and remove old migration:"
echo ""
echo "# 1. Find all pending_emp migration files"
echo "find /root/uvis/backend/alembic/versions/ -name '*pending*' -type f"
echo ""
echo "# 2. Check for the old file with pending_emp_001"
echo "grep -l \"pending_emp_001\" /root/uvis/backend/alembic/versions/*.py"
echo ""
echo "# 3. Remove any OLD files that are NOT the latest one"
echo "# (Check the file date - remove older files with pending_emp_001)"
echo ""
echo "# Example if you find an old file:"
echo "# rm /root/uvis/backend/alembic/versions/OLD_FILE_NAME.py"
echo ""
echo "=========================================="
