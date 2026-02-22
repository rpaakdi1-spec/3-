# 📋 COPY THESE FILES TO SERVER

## Transfer Method

You need to copy these 4 files to your production server at `/root/uvis/`:

1. `fix_backend_export.sh`
2. `verify_frontend_bundles.sh`
3. `system_status_check.sh`
4. `BACKEND_EXPORT_FIX.md`

## Method 1: Using SCP (from your local machine)

```bash
# Replace YOUR_SERVER_IP with 139.150.11.99 or hostname
SERVER_IP="139.150.11.99"

scp fix_backend_export.sh root@${SERVER_IP}:/root/uvis/
scp verify_frontend_bundles.sh root@${SERVER_IP}:/root/uvis/
scp system_status_check.sh root@${SERVER_IP}:/root/uvis/
scp BACKEND_EXPORT_FIX.md root@${SERVER_IP}:/root/uvis/
```

## Method 2: Using Git

```bash
# If files are committed to the repository:
ssh root@139.150.11.99
cd /root/uvis
git pull origin main
chmod +x *.sh
```

## Method 3: Manual Copy-Paste via SSH

Connect to server:
```bash
ssh root@139.150.11.99
cd /root/uvis
```

Then create each file using `cat > filename << 'EOF'` and paste content, ending with `EOF`.

---

## After Transfer, Run This:

```bash
cd /root/uvis

# Make scripts executable
chmod +x fix_backend_export.sh
chmod +x verify_frontend_bundles.sh
chmod +x system_status_check.sh

# Run status check first
./system_status_check.sh

# If issues found, run backend fix
./fix_backend_export.sh

# Verify frontend bundles if needed
./verify_frontend_bundles.sh
```

---

## Quick Start Command (Run This First)

```bash
cd /root/uvis && bash system_status_check.sh
```

This will show you:
- What's working ✅
- What needs fixing ❌
- Recommended next steps

---

## Files Summary

### 1. `fix_backend_export.sh` (8.3 KB)
- **Purpose:** Fixes backend Excel/PDF export Content-Disposition encoding issues
- **Runtime:** ~2-3 minutes
- **Actions:** Backup → Fix code → Rebuild Docker → Test → Commit → Push

### 2. `verify_frontend_bundles.sh` (3.4 KB)
- **Purpose:** Verifies correct JavaScript bundles are being served
- **Runtime:** ~10 seconds
- **Actions:** Check built files → Check Docker files → Compare

### 3. `system_status_check.sh` (9.3 KB)
- **Purpose:** Complete system health check
- **Runtime:** ~30 seconds
- **Actions:** Check all containers → Test all endpoints → Report issues

### 4. `BACKEND_EXPORT_FIX.md` (9.4 KB)
- **Purpose:** Detailed documentation of backend fix
- **Format:** Markdown documentation
- **Usage:** Reference manual for troubleshooting

---

## Execution Order

```
1. system_status_check.sh      ← Start here (diagnose)
   ↓
2. fix_backend_export.sh       ← Fix backend issues
   ↓
3. verify_frontend_bundles.sh  ← Verify frontend (if needed)
   ↓
4. system_status_check.sh      ← Final verification
```

---

## What Each Script Will Do

### system_status_check.sh Output:
```
╔══════════════════════════════════════════════════════════════╗
║            UVIS System Status Check                          ║
╚══════════════════════════════════════════════════════════════╝

1. DOCKER CONTAINERS STATUS
   ✅ uvis-frontend: running
   ✅ uvis-backend: running
   ✅ uvis-db: running
   ✅ uvis-redis: running
   ✅ uvis-nginx: running

2. BACKEND API HEALTH
   ✅ Backend /api/v1/health: 200

3. EXPORT ENDPOINTS TEST
   ❌ Excel export endpoint: 500  ← This needs fixing!
   ❌ PDF export endpoint: 500   ← This needs fixing!

SUMMARY
⚠️  FOUND 2 ISSUE(S)
```

### fix_backend_export.sh Output:
```
╔════════════════════════════════════════════════════════════╗
║     Backend Excel/PDF Export Fix Script                   ║
╚════════════════════════════════════════════════════════════╝

=== 1. Creating backup ===
✅ Backup created

=== 2. Applying fixes ===
  ✓ Removed quote() import
  ✓ Fixed Excel filename format
  ✓ Fixed PDF filename format
  ✓ Fixed 2 Content-Disposition header(s)

=== 5. Rebuilding backend container ===
✅ Backend rebuilt

=== 8. Testing Excel/PDF exports ===
✅ Login successful
Excel export status: 200
✅ Excel export successful
PDF export status: 200
✅ PDF export successful

╔════════════════════════════════════════════════════════════╗
║                  FIX COMPLETE                              ║
╚════════════════════════════════════════════════════════════╝
```

---

## Browser Testing After Fix

1. Open **incognito window**: `http://139.150.11.99`
2. Login: `admin` / `admin123`
3. Navigate: **청구/정산** → **재무 대시보드**
4. Hover: **보고서 다운로드** button
5. Click: **Excel 다운로드** → Should download `Financial_Dashboard_20260101_20260212.xlsx`
6. Click: **PDF 다운로드** → Should download `Financial_Dashboard_20260101_20260212.pdf`

### Expected Results:
- ✅ Excel file: ~8-9 KB, opens in Excel/LibreOffice
- ✅ PDF file: ~3 KB, opens in PDF viewer
- ✅ No HTTP errors in browser console
- ✅ No 500 errors in backend logs

---

## If You Need Help

### Check Logs:
```bash
# Backend logs (last 100 lines)
docker logs --tail 100 uvis-backend

# Look for errors
docker logs uvis-backend 2>&1 | grep -E "ERROR|Exception|500"
```

### Restart Everything:
```bash
cd /root/uvis
docker-compose down
sleep 5
docker-compose up -d
sleep 20
docker ps
```

### Verify Git Status:
```bash
cd /root/uvis
git status
git log --oneline -3
```

---

## Success Checklist

After running all scripts, you should have:

- [x] All Docker containers running and healthy
- [x] Backend API responding (HTTP 200 on /api/v1/health)
- [x] Frontend accessible (HTTP 200 on /)
- [x] Login working (returns JWT token)
- [x] Excel export working (HTTP 200, valid .xlsx file)
- [x] PDF export working (HTTP 200, valid .pdf file)
- [x] Backend fixes committed and pushed to Git
- [x] No 500 errors in logs
- [x] Files download with correct English names
- [x] Files open correctly in respective applications

---

## Contact & Support

If issues persist after running these scripts:

1. Run `system_status_check.sh` again and review output
2. Check the `BACKEND_EXPORT_FIX.md` file for detailed manual fixes
3. Review backend logs: `docker logs --tail 200 uvis-backend`
4. Check for specific errors in the logs and search documentation

---

**Files Location After Transfer:**
- `/root/uvis/fix_backend_export.sh`
- `/root/uvis/verify_frontend_bundles.sh`
- `/root/uvis/system_status_check.sh`
- `/root/uvis/BACKEND_EXPORT_FIX.md`

**Production URL:** http://139.150.11.99
**Login:** admin / admin123
**Key Feature:** 청구/정산 → 재무 대시보드 → 보고서 다운로드

---

Last Updated: 2026-02-12
Ready for deployment ✅
