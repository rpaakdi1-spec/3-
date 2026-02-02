#!/bin/bash

# Quick Status Check
# 빠른 상태 확인 스크립트

echo "🔍 UVIS Quick Status Check"
echo "=========================="
echo ""

cd /root/uvis

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: Not in /root/uvis directory"
    exit 1
fi

# 1. Container status
echo "📦 Containers:"
docker ps --format "{{.Names}}: {{.Status}}" | grep uvis

echo ""

# 2. Check for ORD- in frontend
ORD_COUNT=$(grep -rn "ORD-" frontend/src --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v node_modules | grep -v backup | wc -l)
if [ "$ORD_COUNT" -eq 0 ]; then
    echo "✅ ORD- pattern: CLEAN (0 references)"
else
    echo "❌ ORD- pattern: FOUND ($ORD_COUNT references)"
fi

# 3. Check for max_weight_kg
WEIGHT_FRONTEND=$(grep -rn "max_weight_kg" frontend/src --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)
WEIGHT_BACKEND=$(grep -rn "max_weight_kg" backend/app --include="*.py" 2>/dev/null | wc -l)

if [ "$WEIGHT_FRONTEND" -eq 0 ] && [ "$WEIGHT_BACKEND" -eq 0 ]; then
    echo "✅ max_weight_kg: CLEAN (0 references)"
else
    echo "❌ max_weight_kg: FOUND (Frontend: $WEIGHT_FRONTEND, Backend: $WEIGHT_BACKEND)"
fi

echo ""
echo "=========================="
echo ""

# Summary
if [ "$ORD_COUNT" -eq 0 ] && [ "$WEIGHT_FRONTEND" -eq 0 ] && [ "$WEIGHT_BACKEND" -eq 0 ]; then
    echo "🎉 ALL CLEAN! Code is ready."
    echo ""
    echo "Next: Clear browser cache and test!"
    echo "URL: http://139.150.11.99/orders"
else
    echo "⚠️  Issues found. Run: ./complete_cleanup_and_redeploy.sh"
fi

echo ""
