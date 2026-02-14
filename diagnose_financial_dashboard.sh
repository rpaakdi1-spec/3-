#!/bin/bash

echo "====================================="
echo "Financial Dashboard Diagnostic Tool"
echo "====================================="
echo ""

# 1. Check if Recharts is installed
echo "1. Checking Recharts installation..."
cd /home/user/webapp/frontend
if grep -q "recharts" package.json; then
    echo "✅ Recharts found in package.json"
    grep "recharts" package.json
else
    echo "❌ Recharts NOT found in package.json"
fi
echo ""

# 2. Check if the page file exists
echo "2. Checking FinancialDashboardPage.tsx..."
if [ -f "/home/user/webapp/frontend/src/pages/FinancialDashboardPage.tsx" ]; then
    echo "✅ FinancialDashboardPage.tsx exists"
    wc -l "/home/user/webapp/frontend/src/pages/FinancialDashboardPage.tsx"
else
    echo "❌ FinancialDashboardPage.tsx NOT found"
fi
echo ""

# 3. Check API file
echo "3. Checking billing-enhanced API..."
if [ -f "/home/user/webapp/frontend/src/api/billing-enhanced.ts" ]; then
    echo "✅ billing-enhanced.ts exists"
    echo "API functions:"
    grep "^export const" /home/user/webapp/frontend/src/api/billing-enhanced.ts | head -15
else
    echo "❌ billing-enhanced.ts NOT found"
fi
echo ""

# 4. Check route configuration
echo "4. Checking route configuration..."
if grep -q "FinancialDashboardPage" /home/user/webapp/frontend/src/App.tsx; then
    echo "✅ FinancialDashboardPage imported in App.tsx"
    grep -A 2 "FinancialDashboardPage" /home/user/webapp/frontend/src/App.tsx | head -5
else
    echo "❌ FinancialDashboardPage NOT imported in App.tsx"
fi
echo ""

# 5. Check build output
echo "5. Checking last build..."
if [ -d "/home/user/webapp/frontend/dist" ]; then
    echo "✅ Build directory exists"
    ls -lh /home/user/webapp/frontend/dist/assets/*.js | tail -5
else
    echo "❌ Build directory NOT found"
fi
echo ""

# 6. Check TypeScript types
echo "6. Checking TypeScript types..."
grep -n "export interface.*FinancialSummary\|MonthlyTrend\|TopClient" /home/user/webapp/frontend/src/api/billing-enhanced.ts
echo ""

# 7. Test import in FinancialDashboardPage
echo "7. Checking imports in FinancialDashboardPage..."
head -40 /home/user/webapp/frontend/src/pages/FinancialDashboardPage.tsx | grep "import"
echo ""

echo "====================================="
echo "Diagnostic Complete!"
echo "====================================="
