#!/bin/bash
# Financial Dashboard Complete Fix Script
# This script rebuilds the frontend and prepares deployment instructions

set -e

echo "============================================"
echo "Financial Dashboard Complete Fix"
echo "============================================"
echo ""

cd /home/user/webapp/frontend

# 1. Clean previous build
echo "1. Cleaning previous build..."
rm -rf dist node_modules/.vite
echo "✅ Clean complete"
echo ""

# 2. Verify Recharts is installed
echo "2. Verifying dependencies..."
if ! grep -q '"recharts"' package.json; then
    echo "❌ Recharts not found! Installing..."
    npm install recharts@^2.10.0
else
    echo "✅ Recharts is installed"
fi
echo ""

# 3. Build frontend
echo "3. Building frontend..."
npm run build
echo "✅ Build complete"
echo ""

# 4. Verify build output
echo "4. Verifying build output..."
if [ -f "dist/index.html" ]; then
    echo "✅ index.html exists"
else
    echo "❌ index.html NOT found"
    exit 1
fi

if find dist/assets -name "FinancialDashboardPage-*.js" | grep -q .; then
    echo "✅ FinancialDashboardPage JS bundle exists"
    find dist/assets -name "FinancialDashboardPage-*.js"
else
    echo "❌ FinancialDashboardPage JS bundle NOT found"
    exit 1
fi

echo ""
echo "============================================"
echo "✅ Frontend Build Complete!"
echo "============================================"
echo ""
echo "📦 Build artifacts are ready in: frontend/dist"
echo ""
echo "============================================"
echo "🚀 DEPLOYMENT INSTRUCTIONS FOR SERVER"
echo "============================================"
echo ""
echo "Run the following commands on your SERVER (/root/uvis):"
echo ""
echo "# 1. Navigate to project directory"
echo "cd /root/uvis"
echo ""
echo "# 2. Copy this built frontend to the server (if not already there)"
echo "# (Skip this if you're running on the server already)"
echo ""
echo "# 3. Rebuild frontend on server"
echo "cd /root/uvis/frontend"
echo "npm run build"
echo ""
echo "# 4. Copy built files to Docker container"
echo "cd /root/uvis"
echo "docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/"
echo ""
echo "# 5. Restart frontend container"
echo "docker-compose restart frontend"
echo ""
echo "# 6. Wait for container to start (15 seconds)"
echo "sleep 15"
echo ""
echo "# 7. Verify container is running"
echo "docker-compose ps | grep frontend"
echo ""
echo "============================================"
echo "🌐 TESTING THE DASHBOARD"
echo "============================================"
echo ""
echo "1. Open browser and navigate to: http://139.150.11.99"
echo "2. Login with: admin / admin123"
echo "3. Navigate to: 청구/정산 → 재무 대시보드"
echo "4. Perform HARD REFRESH:"
echo "   - Windows/Linux: Ctrl + Shift + R"
echo "   - macOS: Cmd + Shift + R"
echo "5. Open DevTools (F12) → Console tab"
echo "6. Check for any errors"
echo ""
echo "Expected UI elements:"
echo "  ✓ 4 Summary cards (총 매출, 수금액, 미수금, 미지급 정산)"
echo "  ✓ Date range selector"
echo "  ✓ Download buttons (Excel, PDF)"
echo "  ✓ Monthly trend line chart (월별 매출 추이)"
echo "  ✓ Monthly profit bar chart (월별 순이익)"
echo "  ✓ Top 10 clients table (주요 거래처 TOP 10)"
echo "  ✓ Quick action buttons at bottom"
echo ""
echo "============================================"
echo "🔍 TROUBLESHOOTING"
echo "============================================"
echo ""
echo "If UI elements still don't appear:"
echo ""
echo "1. Check browser console for errors"
echo "2. Check Network tab for failed API calls"
echo "3. Verify API is returning data:"
echo "   curl -X POST http://localhost:8000/api/v1/auth/login \\"
echo "     -H 'Content-Type: application/x-www-form-urlencoded' \\"
echo "     -d 'username=admin&password=admin123'"
echo ""
echo "4. Test financial dashboard API:"
echo "   TOKEN='<your_token_from_login>'"
echo "   curl -X GET \"http://localhost:8000/api/v1/billing/enhanced/dashboard/financial?start_date=2026-01-01&end_date=2026-02-12\" \\"
echo "     -H \"Authorization: Bearer \$TOKEN\""
echo ""
echo "5. Check if Recharts is loaded in browser DevTools:"
echo "   - Open DevTools → Sources tab"
echo "   - Search for 'recharts' in the file tree"
echo ""
echo "============================================"
