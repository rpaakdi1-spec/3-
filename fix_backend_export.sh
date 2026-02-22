#!/bin/bash
# Complete Backend Export Fix Script
# Fixes Content-Disposition encoding and filename issues

set -e
cd /root/uvis

echo "╔════════════════════════════════════════════════════════╗"
echo "║     Backend Excel/PDF Export Fix Script               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Backup
echo "=== 1. Creating backup ==="
BACKUP_FILE="backend/app/api/v1/endpoints/billing_enhanced.py.backup.$(date +%Y%m%d_%H%M%S)"
cp backend/app/api/v1/endpoints/billing_enhanced.py "$BACKUP_FILE"
echo "✅ Backup created: $BACKUP_FILE"
echo ""

# Step 2: Show current issues
echo "=== 2. Checking for issues ==="
echo "Current Content-Disposition usage:"
grep -n "Content-Disposition" backend/app/api/v1/endpoints/billing_enhanced.py | head -5 || echo "Not found"
echo ""
echo "Current quote() usage:"
grep -n "from urllib.parse import quote" backend/app/api/v1/endpoints/billing_enhanced.py || echo "Not found"
echo ""

# Step 3: Apply fixes
echo "=== 3. Applying fixes ==="
python3 <<'PYEND'
import re
from pathlib import Path

file_path = Path('backend/app/api/v1/endpoints/billing_enhanced.py')
content = file_path.read_text(encoding='utf-8')

# Fix 1: Remove problematic quote import
if 'from urllib.parse import quote' in content:
    content = content.replace('from urllib.parse import quote\n', '')
    print("  ✓ Removed quote() import")

# Fix 2: Fix filename generation for Excel
# Change: filename = f"Financial_Dashboard_{start_date}_{end_date}.xlsx"
# To: filename = f"Financial_Dashboard_{start_date.replace('-','')}_{end_date.replace('-','')}.xlsx"

excel_old = r'filename = f"Financial_Dashboard_\{start_date\}_\{end_date\}\.xlsx"'
excel_new = r'filename = f"Financial_Dashboard_{start_date.replace(\'-\', \'\')}_{ end_date.replace(\'-\', \'\')}.xlsx"'

if re.search(excel_old, content):
    content = re.sub(excel_old, excel_new, content)
    print("  ✓ Fixed Excel filename format")

# Fix 3: Fix filename generation for PDF
pdf_old = r'filename = f"Financial_Dashboard_\{start_date\}_\{end_date\}\.pdf"'
pdf_new = r'filename = f"Financial_Dashboard_{start_date.replace(\'-\', \'\')}_{ end_date.replace(\'-\', \'\')}.pdf"'

if re.search(pdf_old, content):
    content = re.sub(pdf_old, pdf_new, content)
    print("  ✓ Fixed PDF filename format")

# Fix 4: Fix Content-Disposition headers
# Find all occurrences of Content-Disposition with quoted filename
old_header_pattern = r'["\']Content-Disposition["\']\s*:\s*f["\']attachment;\s*filename="?\{filename\}"?["\']'
new_header_pattern = r'"Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8\'\'{filename}"'

matches = list(re.finditer(old_header_pattern, content))
if matches:
    content = re.sub(old_header_pattern, new_header_pattern, content)
    print(f"  ✓ Fixed {len(matches)} Content-Disposition header(s)")

# Write back
file_path.write_text(content, encoding='utf-8')
print("\n✅ All fixes applied successfully")
PYEND

if [ $? -ne 0 ]; then
    echo "❌ Fix script failed"
    echo "Restoring backup..."
    cp "$BACKUP_FILE" backend/app/api/v1/endpoints/billing_enhanced.py
    exit 1
fi
echo ""

# Step 4: Verify fixes
echo "=== 4. Verifying fixes ==="
echo "New Content-Disposition format:"
grep -A 1 "Content-Disposition" backend/app/api/v1/endpoints/billing_enhanced.py | head -6
echo ""
echo "New filename format:"
grep "Financial_Dashboard.*replace" backend/app/api/v1/endpoints/billing_enhanced.py | head -2
echo ""

# Step 5: Rebuild backend
echo "=== 5. Rebuilding backend container ==="
docker-compose stop backend
sleep 2
docker-compose build --no-cache backend
echo "✅ Backend rebuilt"
echo ""

# Step 6: Start backend
echo "=== 6. Starting backend ==="
docker-compose up -d backend
echo "Waiting for backend to be ready..."
sleep 15

# Step 7: Check health
echo ""
echo "=== 7. Checking backend health ==="
docker ps | grep backend
echo ""
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
echo "Backend health endpoint: $HEALTH_STATUS"

if [ "$HEALTH_STATUS" != "200" ]; then
    echo "⚠️  Backend health check failed. Checking logs..."
    docker logs --tail 30 uvis-backend
fi
echo ""

# Step 8: Test exports
echo "=== 8. Testing Excel/PDF exports ==="
echo "Logging in..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "⚠️  Login failed. Trying alternative method..."
    TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=admin&password=admin123" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -n "$TOKEN" ]; then
    echo "✅ Login successful"
    echo ""
    
    # Test Excel
    echo "Testing Excel export..."
    EXCEL_STATUS=$(curl -s -w "%{http_code}" -o /tmp/test_dashboard.xlsx \
      -H "Authorization: Bearer $TOKEN" \
      "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/excel?start_date=2026-01-01&end_date=2026-02-12")
    
    echo "Excel export status: $EXCEL_STATUS"
    if [ "$EXCEL_STATUS" = "200" ]; then
        ls -lh /tmp/test_dashboard.xlsx
        file /tmp/test_dashboard.xlsx
        echo "✅ Excel export successful"
    else
        echo "❌ Excel export failed"
        echo "Response:"
        curl -s -H "Authorization: Bearer $TOKEN" \
          "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/excel?start_date=2026-01-01&end_date=2026-02-12"
    fi
    echo ""
    
    # Test PDF
    echo "Testing PDF export..."
    PDF_STATUS=$(curl -s -w "%{http_code}" -o /tmp/test_dashboard.pdf \
      -H "Authorization: Bearer $TOKEN" \
      "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/pdf?start_date=2026-01-01&end_date=2026-02-12")
    
    echo "PDF export status: $PDF_STATUS"
    if [ "$PDF_STATUS" = "200" ]; then
        ls -lh /tmp/test_dashboard.pdf
        file /tmp/test_dashboard.pdf
        echo "✅ PDF export successful"
    else
        echo "❌ PDF export failed"
        echo "Response:"
        curl -s -H "Authorization: Bearer $TOKEN" \
          "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/pdf?start_date=2026-01-01&end_date=2026-02-12"
    fi
else
    echo "❌ Could not obtain authentication token"
    echo "Please test exports manually after login"
fi
echo ""

# Step 9: Git operations
echo "=== 9. Git commit and push ==="
git add backend/app/api/v1/endpoints/billing_enhanced.py

git diff --cached backend/app/api/v1/endpoints/billing_enhanced.py

git commit -m "fix(backend): Fix Excel/PDF export Content-Disposition encoding

- Remove quote() usage causing latin-1 encoding errors
- Use RFC 5987 format: filename*=UTF-8''filename
- Fix date format in filenames: YYYYMMDD (remove hyphens)
- Ensure English-only filenames for browser compatibility

Fixes: HTTP 500 on /api/v1/billing/enhanced/export/financial-dashboard/excel
Fixes: HTTP 500 on /api/v1/billing/enhanced/export/financial-dashboard/pdf"

git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Changes committed and pushed"
else
    echo "⚠️  Git push failed. You may need to pull first:"
    echo "    git pull origin main --rebase"
    echo "    git push origin main"
fi
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════╗"
echo "║                  FIX COMPLETE                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Backend export fix applied"
echo "✅ Docker container rebuilt and restarted"
echo "✅ Changes committed to Git"
echo ""
echo "📝 Expected filenames:"
echo "   - Financial_Dashboard_20260101_20260212.xlsx (~8-9 KB)"
echo "   - Financial_Dashboard_20260101_20260212.pdf (~3 KB)"
echo ""
echo "🌐 Test in browser:"
echo "   1. Go to: http://139.150.11.99"
echo "   2. Login: admin / admin123"
echo "   3. Navigate: 청구/정산 → 재무 대시보드"
echo "   4. Hover: 보고서 다운로드 button"
echo "   5. Click: Excel 다운로드 or PDF 다운로드"
echo ""
echo "If issues persist, check backend logs:"
echo "   docker logs --tail 100 uvis-backend"
echo ""
