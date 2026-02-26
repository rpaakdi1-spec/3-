# 🔴 LOGIN 405 ERROR - CRITICAL DEBUGGING GUIDE

**Created**: 2026-02-25  
**Status**: 🚨 BLOCKING LOGIN  
**Priority**: CRITICAL

---

## 📋 Current Situation

### ✅ What's Working:
- ✅ Frontend UI renders correctly with Tailwind v3
- ✅ Nginx configuration file created and deployed
- ✅ Nginx syntax test passed (`nginx -t`)
- ✅ Nginx reloaded successfully
- ✅ `/api` location block confirmed in nginx.conf

### ❌ What's Broken:
- ❌ Login API returns **HTTP 405 Method Not Allowed**
- ❌ Backend container status: **unhealthy**
- ❌ Health check endpoint `/api/v1/health` returns **404 Not Found**
- ❌ Backend logs show repeated errors

---

## 🔍 ROOT CAUSE ANALYSIS

The **405 error** has **TWO possible causes**:

### 🅰️ **CAUSE A: Backend API Path Mismatch**

**Frontend expects**: `/api/auth/login`  
**Backend might use**: `/api/v1/auth/login` or different path

**Evidence**:
```bash
# Health check uses /api/v1/health (from backend logs)
# But frontend calls /api/auth/login (no /v1)
```

### 🅱️ **CAUSE B: Backend Service Not Running Properly**

**Container status**: `unhealthy`  
**Errors in logs**:
- `Error broadcasting dashboard metrics: ASSIGNED`
- `Error broadcasting vehicle updates: object ChunkedIteratorResult can't be used in 'await' expression`
- Health endpoint returns 404

---

## 🛠️ IMMEDIATE FIX STEPS

### **Step 1: Check Backend API Routes**

Run these commands on the server:

```bash
# 1. Find the backend route definitions
cd /root/uvis/backend
grep -r "auth/login" . --include="*.py" | head -20

# 2. Check if routes use /api/v1 prefix
grep -r "api/v1" . --include="*.py" | head -20

# 3. Look for Flask Blueprint registration
grep -r "Blueprint\|register_blueprint" . --include="*.py" | head -20
```

### **Step 2: Verify Backend Container Health**

```bash
# 1. Check backend logs for startup messages
docker logs uvis-backend --tail 100 | grep -i "running\|started\|listening\|port"

# 2. Check what port backend is actually listening on
docker exec uvis-backend netstat -tlnp | grep LISTEN

# 3. Test backend health directly (inside container)
docker exec uvis-backend curl -X GET http://localhost:8000/api/v1/health -v
docker exec uvis-backend curl -X GET http://localhost:8000/api/health -v
```

### **Step 3: Test API Endpoints from Inside Nginx Container**

```bash
# Test if backend is reachable from nginx container
docker exec uvis-frontend curl -X POST http://backend:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' -v

# Try with /v1 prefix
docker exec uvis-frontend curl -X POST http://backend:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' -v
```

---

## 🔧 LIKELY FIXES

### **FIX 1: Update Nginx to Add /v1 Prefix**

If backend uses `/api/v1/auth/login`, update nginx.conf:

```bash
cd /root/uvis/frontend
cat > nginx.conf << 'EOF'
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    keepalive_timeout  65;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/javascript application/json;
    gzip_disable "MSIE [1-6]\.";

    server {
        listen 80;
        server_name _;

        root /usr/share/nginx/html;
        index index.html;

        # API Proxy - WITH /v1 prefix
        location /api/ {
            proxy_pass http://backend:8000/api/v1/;  # ⬅️ ADD /v1 HERE
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # SPA fallback
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

# Deploy updated config
docker cp nginx.conf uvis-frontend:/etc/nginx/nginx.conf
docker exec uvis-frontend nginx -t
docker exec uvis-frontend nginx -s reload

# Test again
curl -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' -v
```

### **FIX 2: Restart Backend Container**

If backend is unhealthy, restart it:

```bash
# 1. Restart backend
docker restart uvis-backend

# 2. Wait 10 seconds for startup
sleep 10

# 3. Check logs
docker logs uvis-backend --tail 50

# 4. Test health
curl -X GET http://139.150.11.99/api/health -v
curl -X GET http://139.150.11.99/api/v1/health -v

# 5. Test login
curl -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' -v
```

### **FIX 3: Check Backend Code for Route Definitions**

Look for the actual route path in backend code:

```bash
cd /root/uvis/backend

# Find auth route file
find . -name "*auth*" -type f | head -10

# Show auth routes
cat routes/auth.py 2>/dev/null || cat api/auth.py 2>/dev/null || echo "Auth file not found"

# Find main app file
cat app.py 2>/dev/null || cat main.py 2>/dev/null || cat server.py 2>/dev/null || echo "Main file not found"
```

---

## 📊 DIAGNOSTIC CHECKLIST

Run ALL these commands and provide results:

```bash
# === BACKEND ROUTE CHECK ===
cd /root/uvis/backend
grep -r "auth/login" . --include="*.py" | head -10
grep -r "api/v1" . --include="*.py" | head -10

# === BACKEND HEALTH CHECK ===
docker logs uvis-backend --tail 50 | grep -E "Running|Started|Listening|Port|Error"
docker exec uvis-backend netstat -tlnp 2>/dev/null | grep LISTEN || echo "netstat not available"
docker exec uvis-backend curl -X GET http://localhost:8000/api/v1/health -v 2>&1
docker exec uvis-backend curl -X GET http://localhost:8000/api/health -v 2>&1

# === NGINX → BACKEND TEST ===
docker exec uvis-frontend curl -X POST http://backend:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' -v 2>&1

docker exec uvis-frontend curl -X POST http://backend:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' -v 2>&1

# === EXTERNAL API TEST ===
curl -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' -v 2>&1
```

---

## 🎯 EXPECTED OUTCOME

After applying fixes, you should see:

```bash
# ✅ SUCCESS RESPONSE
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJ0eXAiOiJKV1QiLC...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

---

## 📝 SUMMARY

| Check | Status | Command |
|-------|--------|---------|
| Backend routes | ❓ | `grep -r "auth/login" backend/` |
| Backend health | ❌ unhealthy | `docker logs uvis-backend` |
| Nginx config | ✅ deployed | `cat /etc/nginx/nginx.conf` |
| API path | ❓ /api vs /api/v1 | Test both paths |
| External API test | ❌ 405 | `curl http://139.150.11.99/api/auth/login` |

---

## 🚀 NEXT STEPS

1. ✅ Run all diagnostic commands above
2. ✅ Share the complete output
3. ✅ Identify the correct backend API path
4. ✅ Apply the appropriate fix (FIX 1, 2, or 3)
5. ✅ Test login and confirm 200 OK response

---

## 📚 RELATED DOCUMENTS

- `TAILWIND_V3_DOWNGRADE_RECORD.md` - Tailwind v3 downgrade process
- `LOGIN_405_ERROR_FIX.md` - Initial 405 error troubleshooting
- `CACHE_CLEAR_ULTIMATE.md` - Browser cache clearing guide
- `DIAGNOSIS_SUMMARY.md` - Overall project diagnosis

---

**⏰ Created**: 2026-02-25  
**👤 For**: Server admin troubleshooting login 405 error  
**🎯 Goal**: Restore login functionality and resolve 405 Method Not Allowed
