#!/bin/bash

# ==============================================================================
# UI 최적화 빠른 테스트 스크립트
# ==============================================================================

echo "🔍 UI Optimization Quick Test"
echo "=============================="
echo ""

# 1. Frontend accessibility test
echo "1. Testing frontend accessibility..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "   ✅ Frontend accessible (HTTP $HTTP_STATUS)"
else
    echo "   ❌ Frontend not accessible (HTTP $HTTP_STATUS)"
fi
echo ""

# 2. Check dist size
echo "2. Checking build size..."
if [ -d "/root/uvis/frontend/dist" ]; then
    DIST_SIZE=$(du -sh /root/uvis/frontend/dist 2>/dev/null | cut -f1)
    echo "   📦 Dist size: $DIST_SIZE"
    
    # List main bundles
    if [ -d "/root/uvis/frontend/dist/assets/js" ]; then
        echo ""
        echo "   JavaScript bundles:"
        ls -lh /root/uvis/frontend/dist/assets/js/*.js 2>/dev/null | awk '{print "      " $9 " - " $5}' | head -10
    fi
else
    echo "   ⚠️  Dist directory not found"
fi
echo ""

# 3. Container status
echo "3. Checking container status..."
if docker ps | grep -q uvis-frontend; then
    echo "   ✅ Frontend container running"
    docker ps | grep uvis-frontend | awk '{print "      " $1 " - " $2 " - " $NF}'
else
    echo "   ❌ Frontend container not running"
fi
echo ""

# 4. Performance test with curl
echo "4. Performance test..."
echo "   Testing page load time..."
LOAD_TIME=$(curl -o /dev/null -s -w "%{time_total}" http://localhost:80)
echo "   ⏱️  Load time: ${LOAD_TIME}s"
echo ""

# 5. Check for optimization files
echo "5. Checking optimization files..."
cd /root/uvis
if [ -f "frontend/vite.config.ts" ]; then
    if grep -q "manualChunks" frontend/vite.config.ts; then
        echo "   ✅ Vite optimization config applied"
    else
        echo "   ⚠️  Vite config exists but optimization not detected"
    fi
else
    echo "   ❌ Vite config not found"
fi

if [ -f "frontend/src/components/Dashboard.tsx" ]; then
    if grep -q "memo" frontend/src/components/Dashboard.tsx; then
        echo "   ✅ Dashboard optimization applied (React.memo detected)"
    else
        echo "   ⚠️  Dashboard exists but memo not detected"
    fi
else
    echo "   ❌ Dashboard component not found"
fi
echo ""

# Summary
echo "=============================="
echo "📊 Test Summary"
echo "=============================="
echo ""

if [ "$HTTP_STATUS" = "200" ] && docker ps | grep -q uvis-frontend; then
    echo "✅ All basic tests passed!"
    echo ""
    echo "🌐 Access your optimized frontend at:"
    echo "   http://139.150.11.99/"
    echo ""
    echo "🔍 Run Lighthouse test:"
    echo "   1. Open http://139.150.11.99/ in Chrome"
    echo "   2. Press F12 → Lighthouse tab"
    echo "   3. Click 'Generate report'"
else
    echo "⚠️  Some tests failed. Please check the logs above."
fi
echo ""
