# 🚀 Quick Start - Fix 500 Error

## TL;DR
The signup 500 error was caused by the `email` field in the database being `NOT NULL` while the code was trying to insert `NULL` values.

## One-Command Fix 🎯

Run this on the server at `/root/uvis`:

```bash
cd /root/uvis && bash deploy_fix_500.sh
```

This automated script will:
1. ✅ Pull latest code
2. ✅ Run database migration (make email nullable)
3. ✅ Rebuild backend
4. ✅ Test health endpoint
5. ✅ Test signup API
6. ✅ Verify database

**Expected output**: `🎉 Deployment completed successfully!`

## Manual Steps (if script fails)

```bash
cd /root/uvis

# 1. Update code
git pull origin main

# 2. Fix database
docker compose exec db psql -U uvis_user -d uvis_db -c "
ALTER TABLE users ALTER COLUMN email DROP NOT NULL;
"

# 3. Rebuild
docker compose build --no-cache backend
docker compose up -d backend
sleep 20

# 4. Test
curl -X POST http://139.150.11.99/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test123",
    "password": "test123456",
    "role": "DRIVER",
    "name": "테스트",
    "phone": "010-1234-5678",
    "employee_role": "DRIVER",
    "employment_type": "FULL_TIME",
    "hire_date": "2026-02-28",
    "has_cargo_license": false,
    "can_drive_forklift": false,
    "has_forklift_certificate": false
  }'
```

**Expected**: HTTP 201 Created

## Test in Browser

1. Go to: http://139.150.11.99/
2. Click "Sign Up"
3. Fill form (no email field shown)
4. Submit
5. Should redirect to login (not show error)

## Verify Admin Approval

1. Login as admin: `admin` / `admin123`
2. Go to Settings → User Management → Pending Users
3. Should see your new signup
4. Click Approve
5. Enter employee code (e.g., D001)
6. Success message should appear

## GitHub
Repository: https://github.com/rpaakdi1-spec/3-  
Latest commit: `a7f6f7c`

## Full Documentation
- `FINAL_500_ERROR_SOLUTION.md` - Complete analysis
- `CRITICAL_FIX_EMAIL_NULLABLE.md` - Detailed steps
- `deploy_fix_500.sh` - Automated deployment script
