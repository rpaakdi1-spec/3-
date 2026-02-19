# WebSocket Connection Issue - Solution Summary

## Current Status ✅
Based on the logs provided:
1. ✅ Nginx is running and responding on port 80
2. ✅ WebSocket upgrade request succeeds (HTTP 101)
3. ✅ Backend is accepting WebSocket connections
4. ✅ New frontend build deployed with correct URLs
5. ⚠️  Container marked as "unhealthy" but still functioning
6. ❌ Browser showing ERR_CONNECTION_REFUSED (intermittent)

## Root Causes Identified

### 1. Container Health Check Failing
The container is marked "unhealthy" which may cause Docker to:
- Intermittently stop routing traffic
- Restart the container periodically
- Block port forwarding

### 2. Browser Cache/Connection Issues
Even though the server works, the browser may have:
- Stale WebSocket connections
- Cached DNS/connection info
- Service worker cache

## Immediate Solutions (For Server Admin)

### Step 1: Fix Container Health Check
```bash
# Check current health check config
docker inspect uvis-frontend | grep -A 20 healthcheck

# If health check is failing, either:
# Option A: Fix the health check endpoint
docker exec uvis-frontend curl -f http://localhost/health || echo "Health endpoint not working"

# Option B: Temporarily disable health check
docker-compose -f /root/uvis/docker-compose.yml up -d --no-deps --force-recreate uvis-frontend
```

### Step 2: Verify WebSocket Proxy
```bash
# Ensure nginx config is correct
docker exec uvis-frontend cat /etc/nginx/nginx.conf | grep -A 15 "location.*ws"

# Should show:
# location ~ ^/api/v1/(dispatches/)?ws/ {
#     proxy_pass http://backend:8000;
#     proxy_http_version 1.1;
#     proxy_set_header Upgrade $http_upgrade;
#     proxy_set_header Connection "upgrade";
#     ...
# }
```

### Step 3: Test WebSocket from Server
```bash
# Install wscat if not present
npm install -g wscat

# Test WebSocket connection
wscat -c ws://localhost/api/v1/dispatches/ws/dashboard

# Should connect and receive messages
```

## Browser Testing Steps

### Clear Everything Method (Most Reliable)
1. **Close ALL browser windows** (not just tabs)
2. **Clear browser data**:
   - Chrome: Settings → Privacy → Clear browsing data
   - Select: Cached images and files, Cookies and other site data
   - Time range: All time
3. **Restart computer** (to clear any socket connections)
4. **Open browser in Incognito/Private mode**
5. **Open DevTools FIRST** (F12)
6. **Navigate to**: http://139.150.11.99/realtime
7. **Hard refresh**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Alternative: Use Different Browser
- If Chrome fails, try Firefox or Edge
- This bypasses any browser-specific cache issues

## Expected Results

### Console Output (Every 5 seconds):
```javascript
✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/dashboard
📊 Dashboard WebSocket connected
{
  total_orders: 0,
  pending_orders: 0,
  active_dispatches: 0,
  completed_today: 0,
  available_vehicles: 46,
  active_vehicles: 0,
  revenue_today: 0.0,
  revenue_month: 0.0,
  loading: false
}

✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/alerts
🚨 Alerts WebSocket connected
```

### Network Tab:
- WS connection to `ws://139.150.11.99/api/v1/dispatches/ws/dashboard` - Status: 101
- WS connection to `ws://139.150.11.99/api/v1/dispatches/ws/alerts` - Status: 101

## Debugging Commands (If Still Failing)

### On Server:
```bash
# Check if backend is receiving connections
docker logs -f uvis-backend | grep -E "WebSocket|connection"

# Check nginx error logs
docker exec uvis-frontend cat /var/log/nginx/error.log | tail -50

# Check if ports are open
ss -tlnp | grep -E ":80|:8000"

# Test backend WebSocket directly
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/api/v1/dispatches/ws/dashboard
```

### Network Check:
```bash
# From another machine, test if port 80 is accessible
telnet 139.150.11.99 80

# Check firewall rules
iptables -L -n | grep -E "80|8000"

# Check if any service is blocking
systemctl status firewalld
firewall-cmd --list-all
```

## Long-term Fixes

### 1. Fix Frontend Source Code
The proper fix has already been applied to `/root/uvis/frontend/src/hooks/useRealtimeData.ts`:
- Line 302: Changed from `/api/v1/ws/alerts` to `/api/v1/dispatches/ws/alerts`

### 2. Update Container Health Check
Edit `/root/uvis/docker-compose.yml`:
```yaml
frontend:
  # ... existing config ...
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost/health"]
    interval: 10s
    timeout: 5s
    retries: 3
    start_period: 30s
```

### 3. Add Nginx Health Endpoint
Ensure nginx config has:
```nginx
location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

## Files Modified
1. ✅ `/root/uvis/frontend/src/hooks/useRealtimeData.ts` - WebSocket URL fixed
2. ✅ `/root/uvis/frontend/dist/assets/RealtimeDashboardPage-CMZi45qs.js` - Built with fix
3. ✅ Container `/usr/share/nginx/html/` - Updated with new build
4. ✅ `/root/uvis/nginx/nginx.conf` - WebSocket proxy configured

## Next Steps
1. Server admin: Run health check diagnosis
2. User: Clear browser cache completely and retry
3. If still failing: Check firewall/network between user and server
4. Monitor backend logs while user attempts connection
