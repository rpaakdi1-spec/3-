# 📋 UVIS Fix - One Page Cheat Sheet

## 🚀 Quick Commands (Run These in Order)

### On Production Server (139.150.11.99):

```bash
# Step 1: Check status
cd /root/uvis && bash system_status_check.sh

# Step 2: Fix backend exports
bash fix_backend_export.sh

# Step 3: Verify fix
bash system_status_check.sh
```

---

## 📁 Files to Copy to Server

Transfer these to `/root/uvis/`:
- `fix_backend_export.sh`
- `verify_frontend_bundles.sh`
- `system_status_check.sh`
- `BACKEND_EXPORT_FIX.md`

---

## ✅ What's Working

- ✅ Frontend UI (dropdown with Excel/PDF options)
- ✅ Docker containers running
- ✅ Git commits up to date
- ✅ Login/authentication

## ⚠️ What Needs Fixing

- ❌ Excel export (HTTP 500)
- ❌ PDF export (HTTP 500)

**Fix:** Run `fix_backend_export.sh`

---

## 🧪 Browser Test

1. Open: `http://139.150.11.99` (incognito)
2. Login: `admin` / `admin123`
3. Go to: **청구/정산** → **재무 대시보드**
4. Hover: **보고서 다운로드**
5. Click: **Excel 다운로드** or **PDF 다운로드**

**Expected:**
- `Financial_Dashboard_20260101_20260212.xlsx` (~8-9 KB)
- `Financial_Dashboard_20260101_20260212.pdf` (~3 KB)

---

## 🔧 Quick Troubleshooting

### Restart Everything:
```bash
cd /root/uvis
docker-compose down && sleep 5 && docker-compose up -d
```

### Check Logs:
```bash
docker logs --tail 100 uvis-backend
```

### Verify Containers:
```bash
docker ps
```

---

## 📊 Success Criteria

After fix:
- [ ] All containers healthy
- [ ] Backend `/api/v1/health` returns 200
- [ ] Excel export returns 200
- [ ] PDF export returns 200
- [ ] Files download and open correctly

---

## 🆘 If Issues Persist

1. Check `BACKEND_EXPORT_FIX.md` for detailed manual fix
2. Review logs: `docker logs uvis-backend`
3. Verify Git status: `git status`
4. Contact support with error details

---

## 📞 Key Info

- **Server:** 139.150.11.99
- **Login:** admin / admin123
- **Project:** /root/uvis
- **Branch:** main
- **Commit:** 5360e2f (frontend stable)

**Estimated Fix Time:** 5 minutes  
**Last Updated:** 2026-02-12
