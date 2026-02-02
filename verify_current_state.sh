#!/bin/bash

# Verification Script for UVIS Production Server
# Run this on: 139.150.11.99 at /root/uvis

echo "=========================================="
echo "  UVIS Production State Verification"
echo "=========================================="
echo ""

cd /root/uvis

echo "=== 1. Git Status ==="
git status
echo ""

echo "=== 2. Latest Commits ==="
git log --oneline -5
echo ""

echo "=== 3. Check OrderModal.tsx (should NOT have ORD- pattern) ==="
echo "Lines 248-260:"
sed -n '248,260p' frontend/src/components/orders/OrderModal.tsx
echo ""
grep -n "ORD-\|placeholder.*ORD" frontend/src/components/orders/OrderModal.tsx && echo "❌ FOUND ORD- pattern!" || echo "✅ No ORD- pattern found"
echo ""

echo "=== 4. Check for max_weight_kg references ==="
echo "Frontend:"
grep -rn "max_weight_kg" frontend/src --include="*.tsx" --include="*.ts" | wc -l
echo "Backend:"
grep -rn "max_weight_kg" backend/app --include="*.py" | wc -l
echo ""

echo "=== 5. Container Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== 6. Frontend Container Health ==="
docker inspect uvis-frontend --format='{{.State.Health.Status}}' 2>/dev/null || echo "Health check not configured"
echo ""

echo "=== 7. Backend Container Health ==="
docker inspect uvis-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "Health check not configured"
echo ""

echo "=== 8. Recent Frontend Logs ==="
docker logs uvis-frontend --tail 10 2>&1 | grep -v "GET /assets"
echo ""

echo "=== 9. Recent Backend Logs ==="
docker logs uvis-backend --tail 10
echo ""

echo "=========================================="
echo "  Verification Complete"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo "1. If ORD- pattern is found in OrderModal.tsx → Need to fix"
echo "2. If max_weight_kg count is not 0 → Need to fix"
echo "3. If containers are not healthy → Check logs"
echo "4. If everything is clean → Browser cache issue"
echo ""
echo "🌐 Test in browser (after clearing cache):"
echo "   http://139.150.11.99/orders"
echo ""
