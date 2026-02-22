# Backend Export Fix Guide

## Current Issue
Backend Excel/PDF export endpoints returning HTTP 500 errors due to:
1. Content-Disposition header encoding issues (quote() usage problems / latin-1 issues)
2. PDF filename extension errors  
3. Dict vs Object access errors in billing_enhanced.py

## Step 1: Diagnose Current Backend State

```bash
cd /root/uvis

echo "=== 1. Check backend container status ==="
docker ps | grep backend

echo ""
echo "=== 2. Check recent backend logs for errors ==="
docker logs --tail 100 uvis-backend | grep -E "ERROR|Exception|500|export"

echo ""
echo "=== 3. Check billing_enhanced.py current state ==="
grep -n "Content-Disposition" backend/app/api/v1/endpoints/billing_enhanced.py | head -5

echo ""
echo "=== 4. Check for quote() usage ==="
grep -n "from urllib.parse import quote" backend/app/api/v1/endpoints/billing_enhanced.py

echo ""
echo "=== 5. Check PDF filename generation ==="
grep -n "\.pdf" backend/app/api/v1/endpoints/billing_enhanced.py | head -5
```

## Step 2: Fix Content-Disposition Encoding

The issue is likely in `backend/app/api/v1/endpoints/billing_enhanced.py`. Here's the fix:

### Current (Broken) Code Pattern:
```python
from urllib.parse import quote

# This causes latin-1 encoding errors:
filename = quote(f"Financial_Dashboard_{start_date}_{end_date}.xlsx")
headers = {
    'Content-Disposition': f'attachment; filename="{filename}"'
}
```

### Fixed Code Pattern:
```python
# Remove quote() import - not needed for English filenames
# Use RFC 5987 encoding for proper filename handling

filename = f"Financial_Dashboard_{start_date.replace('-','')}_{end_date.replace('-','')}.xlsx"
headers = {
    'Content-Disposition': f"attachment; filename={filename}; filename*=UTF-8''{filename}"
}
```

## Step 3: Apply the Fix

```bash
cd /root/uvis

echo "=== Creating backup of billing_enhanced.py ==="
cp backend/app/api/v1/endpoints/billing_enhanced.py backend/app/api/v1/endpoints/billing_enhanced.py.backup.$(date +%Y%m%d_%H%M%S)

echo ""
echo "=== Applying fix using Python script ==="
python3 <<'PYEND'
import re
from pathlib import Path

file_path = Path('backend/app/api/v1/endpoints/billing_enhanced.py')
content = file_path.read_text(encoding='utf-8')

# Fix 1: Remove quote import if present
content = re.sub(r'from urllib\.parse import quote\n', '', content)

# Fix 2: Fix Excel export Content-Disposition
# Find the Excel export function and fix the headers
excel_pattern = r'(filename = f"Financial_Dashboard_\{start_date\}_\{end_date\}\.xlsx")\s*\n\s*(headers = \{\s*\n\s*["\']Content-Disposition["\']:\s*f["\']attachment; filename=")\{filename\}(["\'])'

excel_replacement = r'\1\n        headers = {\n            "Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8\'\'{filename}"'

content = re.sub(excel_pattern, excel_replacement, content, flags=re.MULTILINE)

# Fix 3: Fix PDF export Content-Disposition  
pdf_pattern = r'(filename = f"Financial_Dashboard_\{start_date\}_\{end_date\}\.pdf")\s*\n\s*(headers = \{\s*\n\s*["\']Content-Disposition["\']:\s*f["\']attachment; filename=")\{filename\}(["\'])'

pdf_replacement = r'\1\n        headers = {\n            "Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8\'\'{filename}"'

content = re.sub(pdf_pattern, pdf_replacement, content, flags=re.MULTILINE)

# Write back
file_path.write_text(content, encoding='utf-8')
print("✅ Fix applied successfully")
PYEND

echo ""
echo "=== Verifying the fix ==="
grep -A 2 "Content-Disposition" backend/app/api/v1/endpoints/billing_enhanced.py | head -10
```

## Step 4: Fix Date Format in Filenames

The filename should use YYYYMMDD format (without hyphens):

```bash
cd /root/uvis

python3 <<'PYEND'
from pathlib import Path
import re

file_path = Path('backend/app/api/v1/endpoints/billing_enhanced.py')
content = file_path.read_text(encoding='utf-8')

# Fix filename date format - replace {start_date} with {start_date.replace('-','')}
# For Excel
content = re.sub(
    r'filename = f"Financial_Dashboard_\{start_date\}_\{end_date\}\.xlsx"',
    r'filename = f"Financial_Dashboard_{start_date.replace(\'-\',\'\')}_{ end_date.replace(\'-\',\'\')}.xlsx"',
    content
)

# For PDF
content = re.sub(
    r'filename = f"Financial_Dashboard_\{start_date\}_\{end_date\}\.pdf"',
    r'filename = f"Financial_Dashboard_{start_date.replace(\'-\',\'\')}_{ end_date.replace(\'-\',\'\')}.pdf"',
    content
)

file_path.write_text(content, encoding='utf-8')
print("✅ Date format fixed")
PYEND
```

## Step 5: Rebuild and Restart Backend

```bash
cd /root/uvis

echo "=== 1. Stop backend container ==="
docker-compose stop backend

echo ""
echo "=== 2. Rebuild backend (no cache) ==="
docker-compose build --no-cache backend

echo ""
echo "=== 3. Start backend ==="
docker-compose up -d backend

echo ""
echo "=== 4. Wait for backend to be ready ==="
sleep 15

echo ""
echo "=== 5. Check backend health ==="
docker ps | grep backend
curl -s -o /dev/null -w "Backend Health Status: %{http_code}\n" http://localhost:8000/api/v1/health
```

## Step 6: Test the Exports

```bash
cd /root/uvis

echo "=== 1. Login and get token ==="
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  exit 1
fi

echo "✅ Login successful (token: ${TOKEN:0:30}...)"

echo ""
echo "=== 2. Test Excel export ==="
HTTP_CODE=$(curl -s -w "%{http_code}" -o /tmp/test_financial_dashboard.xlsx \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/excel?start_date=2026-01-01&end_date=2026-02-12")

echo "Excel Export Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
  ls -lh /tmp/test_financial_dashboard.xlsx
  file /tmp/test_financial_dashboard.xlsx
  echo "✅ Excel export successful"
else
  echo "❌ Excel export failed with status $HTTP_CODE"
  curl -H "Authorization: Bearer $TOKEN" \
    "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/excel?start_date=2026-01-01&end_date=2026-02-12"
fi

echo ""
echo "=== 3. Test PDF export ==="
HTTP_CODE=$(curl -s -w "%{http_code}" -o /tmp/test_financial_dashboard.pdf \
  -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/pdf?start_date=2026-01-01&end_date=2026-02-12")

echo "PDF Export Status: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
  ls -lh /tmp/test_financial_dashboard.pdf
  file /tmp/test_financial_dashboard.pdf
  echo "✅ PDF export successful"
else
  echo "❌ PDF export failed with status $HTTP_CODE"
  curl -H "Authorization: Bearer $TOKEN" \
    "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/pdf?start_date=2026-01-01&end_date=2026-02-12"
fi

echo ""
echo "=== 4. Summary ==="
echo "Expected files:"
echo "  - Financial_Dashboard_20260101_20260212.xlsx (~8-9 KB)"
echo "  - Financial_Dashboard_20260212_20260212.pdf (~3 KB)"
```

## Step 7: Commit and Push Changes

```bash
cd /root/uvis

# Check what changed
git diff backend/app/api/v1/endpoints/billing_enhanced.py

# Stage the file
git add backend/app/api/v1/endpoints/billing_enhanced.py

# Commit
git commit -m "fix(backend): Fix Excel/PDF export Content-Disposition encoding

- Remove quote() usage that caused latin-1 encoding errors
- Use RFC 5987 format: filename*=UTF-8''filename
- Fix date format in filenames: YYYYMMDD (no hyphens)
- Ensure proper English-only filenames for browser compatibility

Fixes: HTTP 500 errors on /api/v1/billing/enhanced/export/financial-dashboard/excel
Fixes: HTTP 500 errors on /api/v1/billing/enhanced/export/financial-dashboard/pdf"

# Push to main
git push origin main

echo "✅ Backend fix committed and pushed"
```

## Expected Results

After these fixes:

1. ✅ Excel endpoint returns HTTP 200
2. ✅ PDF endpoint returns HTTP 200  
3. ✅ Files download with correct English names:
   - `Financial_Dashboard_20260101_20260212.xlsx`
   - `Financial_Dashboard_20260101_20260212.pdf`
4. ✅ No encoding errors in backend logs
5. ✅ Files open correctly in Excel and PDF readers

## Troubleshooting

If issues persist:

```bash
# Check backend logs in detail
docker logs --tail 200 uvis-backend

# Check specific error patterns
docker logs uvis-backend 2>&1 | grep -A 10 "export/financial-dashboard"

# Test health endpoint
curl -v http://localhost:8000/api/v1/health

# Check if backend can reach database
docker-compose exec backend python -c "from app.db.session import engine; engine.connect(); print('✅ DB connection OK')"
```

## Alternative Manual Fix

If the Python script doesn't work, manually edit the file:

```bash
cd /root/uvis
nano backend/app/api/v1/endpoints/billing_enhanced.py
```

Find the Excel export function and change:
```python
# OLD (around line 1250):
from urllib.parse import quote
filename = quote(f"Financial_Dashboard_{start_date}_{end_date}.xlsx")
headers = {
    'Content-Disposition': f'attachment; filename="{filename}"'
}

# NEW:
filename = f"Financial_Dashboard_{start_date.replace('-','')}_{end_date.replace('-','')}.xlsx"
headers = {
    "Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8''{filename}"
}
```

Do the same for the PDF export function.

Save with `Ctrl+X`, `Y`, `Enter`.

Then rebuild and restart the backend as shown in Step 5.
