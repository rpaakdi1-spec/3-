#!/bin/bash

# ==============================================================================
# Production Fix: WebSocket Errors Resolution
# ==============================================================================
# This script fixes the WebSocket broadcasting errors:
# 1. "Error broadcasting dashboard metrics: ASSIGNED"
# 2. "Error broadcasting vehicle updates: ChunkedIteratorResult can't be used in await"
#
# Root cause: Mixing synchronous SQLAlchemy with async/await
# Solution: Remove await from synchronous database operations
# ==============================================================================

set -e  # Exit on error

echo "🚀 Starting WebSocket Error Fix for Production"
echo "================================================"
echo ""

# Navigate to project directory
cd /root/uvis

# Step 1: Stop backend container
echo "Step 1: Stopping backend container..."
docker-compose stop backend
docker-compose rm -f backend
echo "✅ Backend container stopped and removed"
echo ""

# Step 2: Backup current file
echo "Step 2: Creating backup..."
cp backend/app/services/realtime_metrics_service.py backend/app/services/realtime_metrics_service.py.backup_websocket
echo "✅ Backup created: backend/app/services/realtime_metrics_service.py.backup_websocket"
echo ""

# Step 3: Apply fixes
echo "Step 3: Applying WebSocket fixes..."

# Fix 1: Change AsyncSession import to Session
sed -i 's/from sqlalchemy.ext.asyncio import AsyncSession/from sqlalchemy.orm import Session/' backend/app/services/realtime_metrics_service.py

# Fix 2: Remove async from _collect_dashboard_metrics method
sed -i 's/async def _collect_dashboard_metrics(self, db: AsyncSession)/def _collect_dashboard_metrics(self, db: Session)/' backend/app/services/realtime_metrics_service.py

# Fix 3: Remove await from db.scalar calls (4 occurrences)
sed -i 's/active_dispatches = await db\.scalar/active_dispatches = db.scalar/' backend/app/services/realtime_metrics_service.py
sed -i 's/completed_today = await db\.scalar/completed_today = db.scalar/' backend/app/services/realtime_metrics_service.py
sed -i 's/pending_orders = await db\.scalar/pending_orders = db.scalar/' backend/app/services/realtime_metrics_service.py
sed -i 's/vehicles_in_transit = await db\.scalar/vehicles_in_transit = db.scalar/' backend/app/services/realtime_metrics_service.py

# Fix 4: Remove await from metrics call
sed -i 's/metrics = await self\._collect_dashboard_metrics/metrics = self._collect_dashboard_metrics/' backend/app/services/realtime_metrics_service.py

# Fix 5: Remove await from db.execute
sed -i 's/result = await db\.execute/result = db.execute/' backend/app/services/realtime_metrics_service.py

echo "✅ WebSocket fixes applied"
echo ""

# Step 4: Verify changes
echo "Step 4: Verifying changes..."
echo "--- Checking for remaining 'await db.' calls (should be none) ---"
if grep -n "await.*db\." backend/app/services/realtime_metrics_service.py; then
    echo "⚠️  WARNING: Found remaining 'await db.' calls - review needed!"
else
    echo "✅ No 'await db.' calls found - all fixed!"
fi

echo ""
echo "--- Checking Session import ---"
grep -n "from sqlalchemy.orm import Session" backend/app/services/realtime_metrics_service.py
echo ""

echo "--- Checking method signature ---"
grep -n "def _collect_dashboard_metrics" backend/app/services/realtime_metrics_service.py
echo ""

# Step 5: Remove cached Docker image
echo "Step 5: Removing cached Docker image..."
docker rmi uvis-backend 2>/dev/null || echo "Image already removed or doesn't exist"
echo "✅ Cached image removed"
echo ""

# Step 6: Rebuild backend with no cache
echo "Step 6: Rebuilding backend (no cache)..."
docker-compose build --no-cache backend
echo "✅ Backend rebuilt"
echo ""

# Step 7: Start backend
echo "Step 7: Starting backend container..."
docker-compose up -d backend
echo "✅ Backend container started"
echo ""

# Step 8: Wait for backend to start
echo "Step 8: Waiting for backend to initialize (30 seconds)..."
sleep 30
echo "✅ Wait completed"
echo ""

# Step 9: Check container status
echo "Step 9: Checking container status..."
docker ps | grep uvis-backend
echo ""

# Step 10: Check recent logs for errors
echo "Step 10: Checking recent backend logs..."
echo "--- Last 30 seconds of logs ---"
docker logs uvis-backend --since 30s 2>&1 | tail -50
echo ""

# Step 11: Check for specific error messages
echo "Step 11: Checking for WebSocket errors..."
echo "--- Searching for 'Error broadcasting' messages ---"
if docker logs uvis-backend 2>&1 | grep -i "error broadcasting" | tail -10; then
    echo ""
    echo "⚠️  WARNING: WebSocket errors still present - review logs above"
else
    echo "✅ No 'Error broadcasting' messages found!"
fi
echo ""

# Step 12: Verify health
echo "Step 12: Verifying backend health..."
sleep 5
curl -s http://localhost:8000/health | python3 -m json.tool || echo "⚠️  Health check failed"
echo ""

# Final summary
echo ""
echo "================================================"
echo "🎉 WebSocket Fix Deployment Complete!"
echo "================================================"
echo ""
echo "📋 Summary:"
echo "  - Backend container: Rebuilt and restarted"
echo "  - WebSocket fixes: Applied"
echo "  - Backup created: backend/app/services/realtime_metrics_service.py.backup_websocket"
echo ""
echo "🔍 Next Steps:"
echo "  1. Monitor logs: docker logs -f uvis-backend"
echo "  2. Check for errors: docker logs uvis-backend 2>&1 | grep -i 'error broadcasting'"
echo "  3. Test frontend: http://139.150.11.99/"
echo "  4. Verify real-time updates in dashboard"
echo ""
echo "✅ Done!"
