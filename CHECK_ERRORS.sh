#!/bin/bash

echo "=== 1. Checking OrdersPage.tsx line 613 error ==="
sed -n '610,620p' /root/uvis/frontend/src/pages/OrdersPage.tsx

echo ""
echo "=== 2. Checking Layout component location ==="
find /root/uvis/frontend/src -name "Layout.tsx" -o -name "Layout.jsx"

echo ""
echo "=== 3. Checking App.tsx Layout import ==="
grep -n "import.*Layout" /root/uvis/frontend/src/App.tsx

echo ""
echo "=== 4. Checking if common directory exists ==="
ls -la /root/uvis/frontend/src/components/common/ 2>/dev/null || echo "Directory not found"

