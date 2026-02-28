# 🚨 CRITICAL FIX: Email Field 500 Error

## Problem Identified
The signup endpoint was returning **500 Internal Server Error** because:
1. ✅ Frontend removed the email field from the signup form
2. ✅ Backend schema made email optional (`Optional[str]`)
3. ❌ **Database User model still had `email` as `nullable=False`**

This caused a database constraint violation when trying to insert a user with `email=None`.

## Solution Applied
1. **Changed User model**: `nullable=False` → `nullable=True` in `/backend/app/models/user.py`
2. **Created migration**: `20260228_155700_make_email_nullable.py` to alter the database column

## Deployment Steps (Run on server at /root/uvis)

### 1. Pull Latest Code
```bash
cd /root/uvis
git pull origin main
```

**Expected**: Should pull commit `337d792` - "fix: make email field nullable in User model"

### 2. Stop Backend Container
```bash
docker compose down backend
```

### 3. Run Database Migration
```bash
docker compose run --rm backend alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade 20260228_133550 -> 20260228_155700, make email nullable in users table
```

**If you get an error** about constraint not existing, that's OK - it means the constraint name might be different. In that case, manually fix the database:

```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
ALTER TABLE users ALTER COLUMN email DROP NOT NULL;
"
```

### 4. Rebuild and Restart Backend
```bash
docker compose build --no-cache backend
docker compose up -d backend
sleep 20
```

### 5. Verify Backend Health
```bash
curl http://139.150.11.99/api/v1/health
```

**Expected:**
```json
{"status":"healthy","app_name":"Cold Chain Dispatch System","environment":"production"}
```

### 6. Test Signup API
```bash
curl -v -X POST http://139.150.11.99/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser05",
    "password": "test123456",
    "role": "DRIVER",
    "name": "최영수",
    "phone": "010-3333-2222",
    "employee_role": "DRIVER",
    "employment_type": "FULL_TIME",
    "hire_date": "2026-02-28",
    "has_cargo_license": false,
    "can_drive_forklift": false,
    "has_forklift_certificate": false
  }'
```

**Expected:** HTTP 201 Created with user data:
```json
{
  "username": "testuser05",
  "email": null,
  "full_name": "최영수",
  "phone": "010-3333-2222",
  "role": "DRIVER",
  "id": 5,
  "is_active": false,
  "approval_status": "pending"
}
```

### 7. Verify in Database
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, username, email, full_name, phone, is_active, approval_status
FROM users
WHERE username = 'testuser05';
"
```

**Expected:**
```
 id | username   | email | full_name | phone        | is_active | approval_status
----+------------+-------+-----------+--------------+-----------+-----------------
  5 | testuser05 | NULL  | 최영수    | 010-3333-2222| f         | pending
```

### 8. Check Pending Employees Table
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, employee_code, name, phone, email, created_at
FROM pending_employees
WHERE name = '최영수';
"
```

**Expected:**
```
 id |    employee_code     |  name  |     phone     | email |          created_at
----+----------------------+--------+---------------+-------+-------------------------------
  4 | PENDING_20260228_004 | 최영수 | 010-3333-2222 | NULL  | 2026-02-28 15:xx:xx.xxxxxx+00
```

## Troubleshooting

### If Migration Fails
If the Alembic migration fails because constraint name is different:

```bash
# Check existing constraints
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT conname, contype
FROM pg_constraint
WHERE conrelid = 'users'::regclass;
"

# Manually alter the column
docker compose exec db psql -U uvis_user -d uvis_db -c "
ALTER TABLE users ALTER COLUMN email DROP NOT NULL;
"

# Mark migration as applied (optional)
docker compose run --rm backend alembic stamp 20260228_155700
```

### If Still Getting 500 Error
1. **Check backend logs:**
   ```bash
   docker compose logs backend --tail=100 | grep -A 30 "500\|Error\|Traceback"
   ```

2. **Verify database schema:**
   ```bash
   docker compose exec db psql -U uvis_user -d uvis_db -c "\d users"
   ```
   
   The `email` column should show `nullable: yes` or `null: true`

3. **Hard reset (last resort):**
   ```bash
   docker compose down backend
   docker system prune -f
   docker compose build --no-cache backend
   docker compose up -d backend
   ```

## Testing Checklist
- [ ] Backend health check passes
- [ ] Signup with no email returns 201 (not 500)
- [ ] User created in `users` table with `email = NULL`
- [ ] Pending employee created with correct auto-generated employee_code
- [ ] Admin can see pending user in UI (Settings → User Management)
- [ ] Admin can approve pending user
- [ ] Approved user can login successfully

## What Changed
| Component | Before | After |
|-----------|--------|-------|
| User.email model | `nullable=False` | `nullable=True` ✅ |
| Database email column | NOT NULL | NULL allowed ✅ |
| Signup API email handling | ❌ 500 error | ✅ 201 success |

## Next Steps After Deployment
1. ✅ Test signup via browser at http://139.150.11.99/
2. ✅ Complete signup without email field
3. ✅ Login as admin (admin/admin123)
4. ✅ Go to Settings → User Management → Pending Users
5. ✅ Approve testuser05
6. ✅ Login as testuser05

## GitHub Commits
- `337d792` - fix: make email field nullable in User model to support optional email in signup

Repository: https://github.com/rpaakdi1-spec/3-
