#!/bin/bash

# Complete Cleanup and Redeploy Script
# Run this on: 139.150.11.99 at /root/uvis
# This script ensures all ORD- patterns and max_weight_kg are removed

echo "=========================================="
echo "  UVIS Complete Cleanup & Redeploy"
echo "=========================================="
echo ""

cd /root/uvis

# Phase 1: Verify current state
echo "=== Phase 1: Current State Check ==="
echo ""
echo "Checking for ORD- patterns in frontend:"
FRONTEND_ORD=$(grep -rn "ORD-" frontend/src --include="*.tsx" --include="*.ts" | grep -v node_modules | grep -v backup | wc -l)
echo "Found: $FRONTEND_ORD references"

echo ""
echo "Checking for max_weight_kg in frontend:"
FRONTEND_WEIGHT=$(grep -rn "max_weight_kg" frontend/src --include="*.tsx" --include="*.ts" | wc -l)
echo "Found: $FRONTEND_WEIGHT references"

echo ""
echo "Checking for max_weight_kg in backend:"
BACKEND_WEIGHT=$(grep -rn "max_weight_kg" backend/app --include="*.py" | wc -l)
echo "Found: $BACKEND_WEIGHT references"

echo ""
if [ $FRONTEND_ORD -eq 0 ] && [ $FRONTEND_WEIGHT -eq 0 ] && [ $BACKEND_WEIGHT -eq 0 ]; then
    echo "✅ Code is clean! Proceeding with rebuild..."
else
    echo "⚠️  Found remaining references. Please check manually."
    exit 1
fi

# Phase 2: Git commit (if needed)
echo ""
echo "=== Phase 2: Git Commit ==="
git add .
if git commit -m "fix: Final cleanup - remove all ORD- and max_weight_kg references"; then
    echo "✅ Committed new changes"
else
    echo "ℹ️  No changes to commit"
fi

# Phase 3: Stop and remove old containers
echo ""
echo "=== Phase 3: Stop and Remove Old Containers ==="
docker-compose -f docker-compose.prod.yml stop frontend backend
docker-compose -f docker-compose.prod.yml rm -f frontend backend
echo "✅ Old containers removed"

# Phase 4: Rebuild with no cache
echo ""
echo "=== Phase 4: Rebuild (No Cache) ==="
docker-compose -f docker-compose.prod.yml build --no-cache frontend backend
echo "✅ Rebuild complete"

# Phase 5: Start services
echo ""
echo "=== Phase 5: Start Services ==="
docker-compose -f docker-compose.prod.yml up -d
echo "✅ Services started"

# Phase 6: Wait and check health
echo ""
echo "=== Phase 6: Health Check ==="
echo "Waiting 30 seconds for services to stabilize..."
sleep 30

echo ""
echo "Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep uvis

echo ""
echo "Frontend Health:"
docker inspect uvis-frontend --format='{{.State.Health.Status}}' 2>/dev/null || echo "N/A"

echo ""
echo "Backend Health:"
docker inspect uvis-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "N/A"

# Phase 7: Check logs
echo ""
echo "=== Phase 7: Recent Logs ==="
echo ""
echo "Frontend logs (last 10 lines):"
docker logs uvis-frontend --tail 10 2>&1 | grep -v "GET /assets"

echo ""
echo "Backend logs (last 10 lines):"
docker logs uvis-backend --tail 10

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "🎉 Next Steps:"
echo ""
echo "1. ⚠️  CRITICAL: Clear browser cache"
echo "   - Chrome/Edge: Ctrl + Shift + Delete"
echo "   - Select: Cached images and files, Cookies and site data"
echo "   - Time range: All time"
echo "   - Click: Clear data"
echo ""
echo "2. 🔄 Hard Reload"
echo "   - Windows: Ctrl + F5"
echo "   - Mac: Cmd + Shift + R"
echo ""
echo "3. 🕵️  OR use Incognito/Private mode"
echo "   - Chrome: Ctrl + Shift + N"
echo "   - Edge: Ctrl + Shift + P"
echo ""
echo "4. ✅ Test URLs:"
echo "   - Orders: http://139.150.11.99/orders"
echo "   - Vehicles: http://139.150.11.99/vehicles"
echo "   - Clients: http://139.150.11.99/clients"
echo "   - AI Cost: http://139.150.11.99/ai-cost"
echo ""
echo "5. 🔍 What to check:"
echo "   - Order modal: NO 'ORD-20260130-001' field"
echo "   - Order modal: NO '주문 코드' field"
echo "   - Order modal: NO '주문번호' field"
echo "   - Vehicle form: NO '최대 적재중량(kg)' field"
echo "   - Only: 주문일자, 온도대, 픽업 거래처, 배송 거래처, etc."
echo ""
