# Backend Issues Fix Guide

## 🔍 Issues Identified

### 1. Vehicle API 307 Redirect
**Problem**: `/api/v1/vehicles` redirects to `/api/v1/vehicles/` (307)  
**Impact**: Frontend might not follow redirect properly

### 2. WebSocket AsyncIterator Error
**Problem**: `Error broadcasting vehicle updates: object ChunkedIteratorResult can't be used in 'await' expression`  
**Impact**: WebSocket broadcasting fails, dashboard doesn't update in real-time

### 3. WebSocket 403 Authentication
**Problem**: Token is sent but backend doesn't validate it properly  
**Impact**: WebSocket connection rejected, falls back to polling

---

## 🛠️ Fix Commands (Execute on Server)

### STEP 1: Diagnose Backend Issues

```bash
# 1.1. Check vehicle API route definition
docker exec uvis-backend cat /app/app/api/vehicles.py | grep -A 10 "@router.get"

# 1.2. Find the async error location
docker exec uvis-backend grep -rn "broadcast.*vehicle" /app/app --include="*.py"

# 1.3. Check WebSocket authentication
docker exec uvis-backend cat /app/app/api/v1/websocket.py | grep -B 5 -A 20 "async def websocket_endpoint"

# 1.4. Test vehicle API with trailing slash
TOKEN=$(curl -s -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

curl -X GET "http://139.150.11.99/api/v1/vehicles/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## 🔧 FIXES

### FIX 1: Vehicle API Redirect (Nginx Level)

The 307 redirect happens because FastAPI's routing is strict about trailing slashes. Fix in Nginx:

```bash
cd /root/uvis/frontend

# Backup
cp nginx.conf nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# Add rewrite rule for vehicles endpoint (before location /api/v1/)
cat > nginx_vehicles_fix.conf << 'EOF'
        # Fix vehicle API redirect - add trailing slash
        rewrite ^/api/v1/vehicles$ /api/v1/vehicles/ permanent;
        
        location /api/v1/ws/ {
            proxy_pass http://backend:8000/api/v1/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Authorization $http_authorization;
            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
        }

        location /api/v1/ {
            proxy_pass http://backend:8000/api/v1/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Authorization $http_authorization;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
EOF

# Show the section to insert
echo "Insert the above block in your nginx.conf inside the server block"
echo "Then apply:"
echo "docker cp nginx.conf uvis-frontend:/etc/nginx/nginx.conf"
echo "docker exec uvis-frontend nginx -t && docker exec uvis-frontend nginx -s reload"
```

---

### FIX 2: WebSocket AsyncIterator Error

The error `ChunkedIteratorResult can't be used in 'await' expression` occurs when trying to await a non-awaitable object.

**Locate the error:**
```bash
docker exec uvis-backend grep -rn "ChunkedIteratorResult\|broadcast.*vehicle" /app/app --include="*.py" -A 5
```

**Common pattern causing this:**
```python
# WRONG - ChunkedIteratorResult is not awaitable
result = await session.execute(select(...))
await result  # ❌ ERROR

# CORRECT - Use result methods
result = await session.execute(select(...))
vehicles = result.scalars().all()  # ✅ OK
```

**Fix approach:**
```bash
# Find the file with the error
docker exec uvis-backend grep -rn "Error broadcasting vehicle" /app/app --include="*.py" -B 10 -A 5

# The issue is likely in a background task or WebSocket handler
# Look for patterns like:
#   result = await db.execute(query)
#   await result  # THIS IS WRONG
#
# Should be:
#   result = await db.execute(query)
#   items = result.scalars().all()
```

---

### FIX 3: WebSocket Token Authentication

**Current problem:** Backend doesn't validate the token sent in query params.

**Check current implementation:**
```bash
docker exec uvis-backend cat /app/app/api/v1/websocket.py | grep -A 30 "async def websocket_endpoint"
```

**Expected fix pattern:**
```python
from fastapi import WebSocket, Depends, HTTPException, status
from app.core.security import verify_token

@router.websocket("/dashboard")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None)
):
    # Validate token
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        # Verify JWT token
        payload = verify_token(token)
        user = payload.get("sub")
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Accept connection
    await websocket.accept()
    
    # ... rest of code
```

---

## 🧪 Testing After Fixes

```bash
# 1. Get fresh token
TOKEN=$(curl -s -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 2. Test vehicle API (should be 200 OK, not 307)
curl -X GET "http://139.150.11.99/api/v1/vehicles" \
  -H "Authorization: Bearer $TOKEN" -v

# 3. Test dashboard stats
curl -X GET "http://139.150.11.99/api/v1/dispatches/stats/summary" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 4. Check backend logs (should have no ChunkedIteratorResult errors)
docker logs uvis-backend --tail 50 | grep -E "Error|Exception"

# 5. Browser test:
#    - Open http://139.150.11.99
#    - Login with admin/admin123
#    - Check Console (F12) - should see "WebSocket connected: dashboard"
#    - Network tab - WebSocket should show "101 Switching Protocols"
```

---

## 📝 Quick Fix Priority

1. **HIGH**: Fix Nginx vehicle redirect (1 minute)
2. **HIGH**: Fix async ChunkedIteratorResult error (requires code change in backend)
3. **MEDIUM**: Implement WebSocket token validation (requires code change in backend)

**For items 2 & 3**, you need to:
1. Locate the exact files/lines causing errors
2. Edit the Python code in the backend container or mount
3. Restart the backend container: `docker restart uvis-backend`

---

## 🎯 Workaround: Disable WebSocket (Already Applied)

If WebSocket fixes take too long, the dashboard already falls back to polling every 5 seconds, which is functional but not real-time.

**Current status:**
- ✅ Login works
- ✅ Dashboard displays
- ✅ Stats API works (returns zeros if no data)
- ⚠️ Vehicle API returns 307 redirect
- ❌ WebSocket connection fails (403)
- ❌ Backend has async errors

**Next Steps:**
1. Execute the diagnostic commands above
2. Share the output
3. Apply fixes based on findings
4. Test and verify

---

## 📚 Reference

- FastAPI WebSocket docs: https://fastapi.tiangolo.com/advanced/websockets/
- SQLAlchemy async patterns: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Nginx WebSocket proxy: https://nginx.org/en/docs/http/websocket.html
