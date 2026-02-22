#!/bin/bash
# Frontend Bundle Verification Script
# Verifies that browser loads the correct JavaScript bundles

set -e
cd /root/uvis

echo "╔════════════════════════════════════════════════════════╗"
echo "║     Frontend Bundle Verification                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

echo "=== 1. Check built frontend assets ==="
echo "Looking for FinancialDashboardPage and billing-enhanced bundles:"
ls -lh frontend/dist/assets/ | grep -E "FinancialDashboard|billing-enhanced" | tail -10
echo ""

echo "=== 2. Check index.html references ==="
echo "Main bundle in index.html:"
grep -o 'index-[^"'\'']*\.js' frontend/dist/index.html | head -3
echo ""
echo "FinancialDashboard bundle in index.html:"
grep -o 'FinancialDashboardPage-[^"'\'']*\.js' frontend/dist/index.html | head -1 || echo "(Dynamic import - not in index.html)"
echo ""
echo "billing-enhanced bundle in index.html:"
grep -o 'billing-enhanced-[^"'\'']*\.js' frontend/dist/index.html | head -1 || echo "(Dynamic import - not in index.html)"
echo ""

echo "=== 3. Check Docker container assets ==="
echo "Assets inside frontend container:"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/ | grep -E "FinancialDashboard|billing-enhanced" | tail -10
echo ""

echo "=== 4. Check nginx configuration ==="
docker exec uvis-frontend cat /etc/nginx/conf.d/default.conf | grep -E "location|try_files|root" | head -20
echo ""

echo "=== 5. Test HTTP access to assets ==="
echo "Testing main index.html:"
curl -s -I http://localhost:80/ | head -5
echo ""

MAIN_BUNDLE=$(grep -o 'index-[^"'\'']*\.js' frontend/dist/index.html | head -1)
if [ -n "$MAIN_BUNDLE" ]; then
    echo "Testing main bundle: /assets/$MAIN_BUNDLE"
    curl -s -I "http://localhost:80/assets/$MAIN_BUNDLE" | head -5
    echo ""
fi

echo "=== 6. Check browser cache headers ==="
echo "Cache-Control and ETag headers:"
curl -s -I http://localhost:80/assets/index.css 2>/dev/null | grep -E "Cache-Control|ETag|Last-Modified" || echo "No cache headers found"
echo ""

echo "=== 7. Expected vs Actual ==="
echo ""
echo "📦 Expected bundles (from latest build):"
ls -1 frontend/dist/assets/ | grep -E "FinancialDashboard|billing-enhanced" | tail -5
echo ""

echo "🚀 Served bundles (from Docker container):"
docker exec uvis-frontend ls -1 /usr/share/nginx/html/assets/ | grep -E "FinancialDashboard|billing-enhanced" | tail -5
echo ""

echo "╔════════════════════════════════════════════════════════╗"
echo "║              Verification Complete                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🔍 To check what browser is loading:"
echo "   1. Open: http://139.150.11.99 in incognito mode"
echo "   2. Press F12 to open DevTools"
echo "   3. Go to Network tab"
echo "   4. Navigate to 청구/정산 → 재무 대시보드"
echo "   5. Filter by 'JS' and look for:"
echo "      - index-*.js"
echo "      - FinancialDashboardPage-*.js"
echo "      - billing-enhanced-*.js"
echo ""
echo "✅ Expected files:"
echo "   - index-*.js (main bundle)"
echo "   - FinancialDashboardPage-PZYafZdB.js (from latest build)"
echo "   - billing-enhanced-Tpm2rv1m.js (from latest build)"
echo ""
echo "⚠️  If browser loads different files:"
echo "   1. Clear browser cache completely"
echo "   2. Use a different browser"
echo "   3. Use incognito/private mode"
echo "   4. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
echo ""
