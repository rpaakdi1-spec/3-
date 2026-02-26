#!/bin/bash
echo "=== 1. Check if Tailwind directives are in src/index.css ==="
head -10 /root/uvis/frontend/src/index.css

echo ""
echo "=== 2. Check tailwind.config.js ==="
cat /root/uvis/frontend/tailwind.config.js

echo ""
echo "=== 3. Check postcss.config.js ==="
cat /root/uvis/frontend/postcss.config.js

echo ""
echo "=== 4. Check vite.config.ts ==="
cat /root/uvis/frontend/vite.config.ts

echo ""
echo "=== 5. Check if Tailwind CSS is actually bundled ==="
echo "First 100 lines of built CSS:"
head -100 /root/uvis/frontend/dist/assets/index-BjMybcaV.css

echo ""
echo "=== 6. Check for specific Tailwind classes in built CSS ==="
echo "Looking for 'bg-gradient', 'from-blue', 'to-blue':"
grep -o "bg-gradient-to-b\|from-blue-400\|to-blue-600" /root/uvis/frontend/dist/assets/index-BjMybcaV.css | head -5

echo ""
echo "=== 7. Check LoginPage source for className usage ==="
grep -n "className" /root/uvis/frontend/src/pages/LoginPage.tsx | head -10
