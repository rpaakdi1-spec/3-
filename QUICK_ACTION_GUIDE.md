# 🚀 UVIS Financial Dashboard - Quick Action Guide

## 📋 Current Status (as of 2026-02-12)

### ✅ Completed
- Frontend rolled back to stable dropdown version (commit f36e242)
- Frontend builds successfully
- Docker containers deployed and running
- Git commit (5360e2f) and push completed
- UI shows working dropdown: "보고서 다운로드" → Excel/PDF options

### ⏳ Pending
- Backend export endpoints may have HTTP 500 errors
- Need to verify Excel/PDF download functionality
- Content-Disposition encoding issues to be fixed

---

## 🔧 Fix Scripts Available

### 1. **Backend Export Fix** (Primary Task)
Fixes Content-Disposition encoding and filename issues.

```bash
# On production server (139.150.11.99):
cd /root/uvis
bash fix_backend_export.sh
```

**What it does:**
- Removes problematic `quote()` usage
- Fixes Content-Disposition headers (RFC 5987 format)
- Corrects filename date format (YYYYMMDD)
- Rebuilds and restarts backend
- Tests Excel/PDF exports
- Commits and pushes changes

**Expected result:**
- ✅ Excel endpoint returns HTTP 200
- ✅ PDF endpoint returns HTTP 200
- ✅ Files download with names like `Financial_Dashboard_20260101_20260212.xlsx`

---

### 2. **Frontend Bundle Verification**
Checks if browser is loading the correct JavaScript files.

```bash
cd /root/uvis
bash verify_frontend_bundles.sh
```

**What it does:**
- Lists built frontend assets
- Checks Docker container assets
- Verifies nginx configuration
- Shows expected vs actual bundles

---

### 3. **Complete System Status Check**
Comprehensive health check of all components.

```bash
cd /root/uvis
bash system_status_check.sh
```

**What it does:**
- Checks all Docker containers
- Tests backend API health
- Verifies frontend accessibility
- Tests database and Redis
- Tests authentication
- Tests Excel/PDF export endpoints
- Shows Git status
- Displays system resources
- Provides summary of issues

---

## 🎯 Step-by-Step Resolution

### Step 1: Run System Status Check
```bash
cd /root/uvis
bash system_status_check.sh
```

This will tell you exactly what's working and what needs fixing.

### Step 2: Fix Backend Exports (if needed)
```bash
cd /root/uvis
bash fix_backend_export.sh
```

This addresses the main pending issue - Excel/PDF export functionality.

### Step 3: Verify Frontend Bundles (if UI issues persist)
```bash
cd /root/uvis
bash verify_frontend_bundles.sh
```

### Step 4: Browser Testing

1. **Open in incognito mode:** `http://139.150.11.99`
2. **Login:** admin / admin123
3. **Navigate:** 청구/정산 → 재무 대시보드
4. **Test downloads:**
   - Hover over "보고서 다운로드" button
   - Click "Excel 다운로드" → should download `Financial_Dashboard_YYYYMMDD_YYYYMMDD.xlsx`
   - Click "PDF 다운로드" → should download `Financial_Dashboard_YYYYMMDD_YYYYMMDD.pdf`

---

## 📁 File Locations

### Scripts (on production server at /root/uvis):
- `fix_backend_export.sh` - Main backend fix script
- `verify_frontend_bundles.sh` - Frontend verification
- `system_status_check.sh` - Complete system health check

### Documentation:
- `BACKEND_EXPORT_FIX.md` - Detailed backend fix documentation

### Key Application Files:
- **Backend:** `/root/uvis/backend/app/api/v1/endpoints/billing_enhanced.py`
- **Frontend:** `/root/uvis/frontend/src/pages/FinancialDashboardPage.tsx`
- **Docker:** `/root/uvis/docker-compose.yml`

---

## 🐛 Troubleshooting

### If Backend Exports Still Fail After Fix:

```bash
# Check backend logs
docker logs --tail 100 uvis-backend

# Check for specific errors
docker logs uvis-backend 2>&1 | grep -A 10 "export/financial-dashboard"

# Restart backend
docker-compose restart backend
```

### If Frontend Shows Old Version:

```bash
# Rebuild frontend without cache
docker-compose stop frontend
docker-compose rm -f frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### If Authentication Fails:

```bash
# Check database connection
docker exec uvis-db pg_isready -U uvis

# Check backend logs for auth errors
docker logs --tail 50 uvis-backend | grep -i "auth"
```

### If Containers Are Unhealthy:

```bash
# Check all container status
docker ps -a

# Restart all services
docker-compose down
sleep 5
docker-compose up -d

# Wait for health checks
sleep 20
docker ps
```

---

## 📊 Expected Test Results

### Backend Health Endpoint:
```bash
curl http://localhost:8000/api/v1/health
# Expected: {"status":"healthy"} - HTTP 200
```

### Login:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
# Expected: {"access_token":"...", "token_type":"bearer"} - HTTP 200
```

### Excel Export:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/excel?start_date=2026-01-01&end_date=2026-02-12" \
  -o test.xlsx
# Expected: HTTP 200, file size ~8-9 KB
```

### PDF Export:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/pdf?start_date=2026-01-01&end_date=2026-02-12" \
  -o test.pdf
# Expected: HTTP 200, file size ~3 KB
```

---

## 🔄 Git Workflow

### Current Branch:
```bash
git branch --show-current
# Expected: main
```

### Recent Commits:
```bash
git log --oneline -5
# Should show:
# - 5360e2f revert(ui): Rollback to stable dropdown version
# - (other commits)
```

### After Backend Fix:
The `fix_backend_export.sh` script will automatically:
1. Create a backup of `billing_enhanced.py`
2. Apply fixes
3. Commit changes with descriptive message
4. Push to `origin main`

---

## 📞 Next Actions

1. **Run the system status check** to identify current issues
2. **Execute the backend export fix** if needed
3. **Test in browser** to verify functionality
4. **Report results** back

### Commands to Run (in order):

```bash
cd /root/uvis

# 1. Check overall system status
bash system_status_check.sh

# 2. If export issues found, apply fix
bash fix_backend_export.sh

# 3. Verify frontend bundles if UI issues persist
bash verify_frontend_bundles.sh

# 4. Final status check
bash system_status_check.sh
```

---

## ✅ Success Criteria

All of these should be ✅:

- [ ] All Docker containers running (frontend, backend, db, redis, nginx)
- [ ] Backend health endpoint returns 200
- [ ] Frontend accessible at http://139.150.11.99
- [ ] Login works (admin/admin123)
- [ ] Financial Dashboard page loads
- [ ] "보고서 다운로드" button visible
- [ ] Excel download works (HTTP 200, valid .xlsx file)
- [ ] PDF download works (HTTP 200, valid .pdf file)
- [ ] No 500 errors in backend logs
- [ ] Correct bundle files loaded in browser
- [ ] Changes committed and pushed to Git

---

## 📚 Additional Resources

### Documentation Files:
- `BACKEND_EXPORT_FIX.md` - Detailed backend fix guide
- `PHASE_8_COMPLETE_SUMMARY.md` - Project phase 8 summary
- `TODO.md` - Outstanding tasks

### Logs:
```bash
# Backend logs
docker logs --tail 200 uvis-backend

# Frontend logs
docker logs --tail 50 uvis-frontend

# Nginx logs
docker logs --tail 50 uvis-nginx

# Database logs
docker logs --tail 50 uvis-db
```

### Container Shell Access:
```bash
# Backend shell
docker exec -it uvis-backend bash

# Frontend shell (nginx)
docker exec -it uvis-frontend sh

# Database shell
docker exec -it uvis-db psql -U uvis -d uvis
```

---

## 🎬 Quick Copy-Paste Commands

### On Production Server (139.150.11.99):

```bash
# Complete fix workflow
cd /root/uvis && \
bash system_status_check.sh && \
echo "Review the status above. Press Enter to continue with backend fix..." && \
read && \
bash fix_backend_export.sh && \
echo "Backend fix complete. Testing in browser now..."

# URL to test: http://139.150.11.99
# Login: admin / admin123
# Navigate to: 청구/정산 → 재무 대시보드
# Test: Excel and PDF downloads
```

---

**Last Updated:** 2026-02-12
**Status:** Ready for deployment testing
**Primary Contact:** System Administrator
