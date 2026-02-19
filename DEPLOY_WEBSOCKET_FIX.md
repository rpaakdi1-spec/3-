# WebSocket Connection Fix - Deployment Guide

## 📋 Summary

This fix resolves the WebSocket connection stability issues where the dashboard and alerts WebSocket connections were repeatedly disconnecting with "ClientDisconnected" errors.

**Commit:** `895e980` - fix(websocket): Fix dashboard and alerts WebSocket connection stability

## 🎯 Root Cause Analysis

### Frontend Issue
- The `useRealtimeData` hook was calling `setData()` for **every message**, including system messages like `connected` and `keepalive`
- This caused unnecessary React state updates and re-renders
- Component lifecycle effects were triggered, potentially causing WebSocket disconnections

### Backend Issues
1. **Dashboard WebSocket**: Sent an initial "loading" message with `loading: true` flag, which had a different structure than the expected dashboard metrics
2. **Alerts WebSocket**: 
   - Keepalive interval was too long (30 seconds), causing frontend timeout/reconnection
   - Missing `data: null` field in system messages

## 🔧 Changes Made

### Frontend (`frontend/src/hooks/useRealtimeData.ts`)

```typescript
// Before:
setData(message.data || message);  // Called for ALL messages

// After:
if (message.type !== 'connected' && message.type !== 'keepalive') {
  setData(message.data || message);  // Only called for data messages
}
```

**Impact:** System messages no longer trigger state updates, preventing unnecessary re-renders.

### Backend (`backend/app/api/dispatches.py`)

#### 1. Dashboard WebSocket
```python
# Removed the initial "loading" message
# Now sends real dashboard stats immediately upon connection
await websocket.accept()
logger.info("✅ Dashboard WebSocket connected, will send real data immediately")

# Stats sent every 5 seconds with real data:
{
  "total_orders": 0,
  "pending_orders": 0,
  "active_dispatches": 0,
  "completed_today": 0,
  "available_vehicles": 46,
  "active_vehicles": 0,
  "revenue_today": 0.0,
  "revenue_month": 0.0,
  "timestamp": "2026-02-15T...",
  "loading": false
}
```

#### 2. Alerts WebSocket
```python
# Changed keepalive interval from 30s to 5s
await asyncio.sleep(5)  # Send keepalive every 5 seconds

# Added "data: null" field to system messages
initial_message = {
  "type": "connected",
  "message": "Alerts WebSocket connected",
  "data": None,  # ← Added
  "timestamp": datetime.now().isoformat()
}

keepalive = {
  "type": "keepalive",
  "data": None,  # ← Added
  "timestamp": datetime.now().isoformat()
}
```

## 🚀 Deployment Steps

### Step 1: Pull Latest Code
```bash
cd /root/uvis
git pull origin main

# Verify you have the latest commit
git log --oneline -3
# Should show:
# 895e980 fix(websocket): Fix dashboard and alerts WebSocket connection stability
# ef4c2ab debug(websocket): Add verbose logging for dashboard stats collection
# 775dfd1 fix(websocket): Add missing SQLAlchemy and_ import
```

### Step 2: Deploy Backend
```bash
# Copy updated dispatches.py into backend container
docker cp /root/uvis/backend/app/api/dispatches.py uvis-backend:/app/app/api/dispatches.py

# Clear Python cache
docker exec uvis-backend find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
docker exec uvis-backend find /app -name "*.pyc" -delete

# Restart backend container
docker restart uvis-backend

# Wait 30 seconds for startup
sleep 30

# Check backend health
curl http://localhost:8000/api/v1/health
# Should return: {"status":"healthy","service":"uvis-backend"}
```

### Step 3: Deploy Frontend
```bash
cd /root/uvis/frontend

# Build frontend with latest changes
npm run build

# Deploy to frontend container
docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/

# Restart frontend container (to clear any cached connections)
docker restart uvis-frontend

# Wait 10 seconds
sleep 10
```

### Step 4: Verify Deployment

#### Check Container Status
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected output:
```
NAMES               STATUS
uvis-backend        Up X minutes (healthy)
uvis-frontend       Up X minutes (healthy)
```

#### Monitor WebSocket Connections
```bash
# Watch live backend logs
docker logs -f uvis-backend --since 1m | grep -E "WebSocket|dashboard|alerts|Sent"
```

Expected log output:
```
✅ Dashboard WebSocket connected, will send real data immediately
🔄 Starting to collect dashboard stats...
⏳ Executing DB queries in thread pool...
✅ Stats collected successfully: {...}
📊 Sent dashboard stats: pending=0, active=0
```

No "ClientDisconnected" or "Failed to send" warnings should appear.

## 🧪 Testing Instructions

### Browser Test (Critical!)

1. **Close ALL browser tabs** completely
2. **Fully exit the browser** (not just close window)
3. **Reopen browser** in a fresh session
4. **Open a new incognito/private window** (Ctrl+Shift+N / Cmd+Shift+N)
5. **Open DevTools** (F12) → Console tab
6. **Navigate to:** `http://139.150.11.99/realtime`
7. **Force refresh:** Ctrl+Shift+R (or Cmd+Shift+R on Mac)

### Expected Browser Console Output

✅ **Success Pattern:**
```
✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/dashboard
📊 Dashboard WebSocket connected
📊 Dashboard stats updated: {
  total_orders: 0,
  pending_orders: 0,
  active_dispatches: 0,
  completed_today: 0,
  available_vehicles: 46,
  active_vehicles: 0,
  revenue_today: 0,
  revenue_month: 0,
  timestamp: "2026-02-15T...",
  loading: false
}
... (repeats every 5 seconds) ...
```

❌ **Failure Pattern (should NOT see):**
```
❌ WebSocket error: ws://...
🔌 WebSocket disconnected: ws://...
🔄 Reconnecting (1/10)...
```

### Dashboard UI Verification

The dashboard should display:
- ✅ **Available Vehicles**: 46 (updating automatically)
- ✅ **Active Dispatches**: 0 (or current count)
- ✅ **Completed Today**: X (today's completed dispatches)
- ✅ **Pending Orders**: 0 (or current count)

Numbers should **automatically update every 5 seconds** without page refresh.

## 🔍 Troubleshooting

### Issue: Still seeing "ClientDisconnected" in logs

**Cause:** Browser cache not cleared or old tab still open

**Solution:**
```bash
# 1. Completely close browser (not just tabs)
# 2. Clear browser cache manually:
#    - Chrome: Ctrl+Shift+Delete → Clear cached images and files
#    - Firefox: Ctrl+Shift+Delete → Cookies and Cache
# 3. Open new incognito window
# 4. Hard refresh: Ctrl+Shift+R
```

### Issue: Frontend not showing updated stats

**Cause:** Frontend container serving old files

**Solution:**
```bash
# Clear frontend container cache completely
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*

# Redeploy frontend
docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/

# Restart nginx
docker restart uvis-frontend
```

### Issue: Backend health check failing

**Cause:** Container still starting or database connection issue

**Solution:**
```bash
# Check backend logs
docker logs uvis-backend --tail=50

# Check database connection
docker exec uvis-backend python3 -c "
from app.core.database import SessionLocal
db = SessionLocal()
print('✅ Database connected')
db.close()
"
```

## 📊 Expected Metrics After Fix

### Before Fix:
- ❌ WebSocket reconnects every ~5 seconds
- ❌ "ClientDisconnected" warnings in logs
- ❌ Dashboard shows "loading..." indefinitely
- ❌ No automatic stats updates

### After Fix:
- ✅ WebSocket stays connected continuously
- ✅ No "ClientDisconnected" warnings
- ✅ Dashboard displays real-time stats immediately
- ✅ Stats update every 5 seconds automatically
- ✅ Clean logs with only INFO messages

## 📝 Technical Notes

### Why This Fix Works

1. **Frontend:** By skipping `setData()` for system messages, we avoid triggering React's reconciliation algorithm unnecessarily. This prevents component lifecycle methods (useEffect, useMemo, etc.) from re-running on every keepalive message.

2. **Backend:** Sending real data immediately eliminates the "loading" state confusion and ensures the frontend always receives data in the expected format.

3. **Keepalive Interval:** 5 seconds matches the dashboard stats interval, ensuring consistent heartbeat timing and preventing timeout-related disconnections.

### Message Flow After Fix

```
┌─────────┐                    ┌─────────┐
│ Browser │                    │ Backend │
└────┬────┘                    └────┬────┘
     │                              │
     │ ─────  Connect WS  ────────> │
     │                              │
     │ <──  Dashboard Stats (5s) ── │  ✅ Real data immediately
     │ <──  Dashboard Stats (5s) ── │  ✅ Every 5 seconds
     │ <──  Dashboard Stats (5s) ── │  ✅ Continuous updates
     │                              │
     │ ─────  Connect Alerts  ────> │
     │                              │
     │ <──  Connected (data:null) ─ │  ✅ Ignored by frontend
     │ <──  Keepalive (data:null) ─ │  ✅ Ignored by frontend (5s)
     │ <──  Alert (real data)  ───  │  ✅ Processed by frontend
     │                              │
```

## ✅ Success Criteria

Deployment is successful when:

1. ✅ Backend logs show "✅ Dashboard WebSocket connected" and "📊 Sent dashboard stats" every 5 seconds
2. ✅ No "ClientDisconnected" or "Failed to send" warnings in logs
3. ✅ Browser console shows continuous "Dashboard stats updated" messages every 5 seconds
4. ✅ Dashboard UI displays real-time metrics that update automatically
5. ✅ No WebSocket error or reconnection messages in browser console
6. ✅ Container health checks remain green (healthy status)

---

## 📞 Support

If issues persist after following this guide:

1. **Collect logs:**
   ```bash
   docker logs uvis-backend --tail=200 > /tmp/backend_logs.txt
   docker logs uvis-frontend --tail=50 > /tmp/frontend_logs.txt
   ```

2. **Test WebSocket directly:**
   ```bash
   docker exec uvis-backend python3 -c "
   import asyncio, websockets
   async def test():
       async with websockets.connect('ws://localhost:8000/api/v1/dispatches/ws/dashboard') as ws:
           msg = await ws.recv()
           print(f'Received: {msg}')
   asyncio.run(test())
   "
   ```

3. **Provide:**
   - Browser console screenshot
   - Backend logs
   - Direct WebSocket test results

---

**Last Updated:** 2026-02-15  
**Commit:** 895e980  
**Status:** ✅ Ready for Production Deployment
