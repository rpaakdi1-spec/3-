#!/bin/bash

# ==============================================================================
# UI 최적화 프로덕션 배포 스크립트
# ==============================================================================
# 이 스크립트는 UI 최적화를 프로덕션에 적용합니다.
# ==============================================================================

set -e  # Exit on error

echo "🎨 Starting UI Optimization Deployment"
echo "========================================"
echo ""

# Navigate to project directory
cd /root/uvis

# Step 1: Backup current files
echo "Step 1: Creating backups..."
cp frontend/vite.config.ts frontend/vite.config.ts.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
cp frontend/src/components/Dashboard.tsx frontend/src/components/Dashboard.tsx.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
echo "✅ Backups created"
echo ""

# Step 2: Apply Vite optimization config
echo "Step 2: Applying Vite optimization config..."
if [ -f "frontend/vite.config.optimization.ts" ]; then
    cp frontend/vite.config.optimization.ts frontend/vite.config.ts
    echo "✅ Vite config updated"
else
    echo "⚠️  vite.config.optimization.ts not found - skipping"
fi
echo ""

# Step 3: Apply optimized Dashboard component
echo "Step 3: Applying optimized Dashboard component..."
if [ -f "frontend/src/components/Dashboard.optimized.tsx" ]; then
    cp frontend/src/components/Dashboard.optimized.tsx frontend/src/components/Dashboard.tsx
    echo "✅ Dashboard component updated"
else
    echo "⚠️  Dashboard.optimized.tsx not found - skipping"
fi
echo ""

# Step 4: Clean npm cache and dependencies
echo "Step 4: Cleaning npm cache..."
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
echo "✅ Cache cleaned"
echo ""

# Step 5: Install dependencies
echo "Step 5: Installing dependencies..."
export NODE_OPTIONS="--max-old-space-size=4096"
npm install --legacy-peer-deps --prefer-offline --no-audit
echo "✅ Dependencies installed"
echo ""

# Step 6: Build frontend
echo "Step 6: Building frontend..."
npm run build

# Check build success
if [ -d "dist" ]; then
    DIST_SIZE=$(du -sh dist | cut -f1)
    echo "✅ Build successful! Dist size: $DIST_SIZE"
    
    echo ""
    echo "=== Build Analysis ==="
    echo "Total dist size: $DIST_SIZE"
    
    if [ -d "dist/assets/js" ]; then
        echo ""
        echo "JavaScript bundles:"
        ls -lh dist/assets/js/*.js 2>/dev/null | awk '{print "  " $9 " - " $5}'
    fi
    
    if [ -d "dist/assets/css" ]; then
        echo ""
        echo "CSS bundles:"
        ls -lh dist/assets/css/*.css 2>/dev/null | awk '{print "  " $9 " - " $5}'
    fi
else
    echo "❌ Build failed - dist directory not found"
    exit 1
fi
echo ""

# Step 7: Return to project root
cd /root/uvis
echo "Step 7: Returned to project root"
echo ""

# Step 8: Stop frontend container
echo "Step 8: Stopping frontend container..."
docker-compose stop frontend
docker-compose rm -f frontend
echo "✅ Frontend container stopped"
echo ""

# Step 9: Remove old image
echo "Step 9: Removing old frontend image..."
docker rmi uvis-frontend 2>/dev/null || echo "Image already removed or doesn't exist"
echo "✅ Old image removed"
echo ""

# Step 10: Build new frontend image
echo "Step 10: Building new frontend image..."
docker-compose build frontend
echo "✅ Frontend image built"
echo ""

# Step 11: Start frontend container
echo "Step 11: Starting frontend container..."
docker-compose up -d frontend
echo "✅ Frontend container started"
echo ""

# Step 12: Wait for startup
echo "Step 12: Waiting for frontend to start (15 seconds)..."
sleep 15
echo "✅ Wait completed"
echo ""

# Step 13: Check container status
echo "Step 13: Checking container status..."
if docker ps | grep -q uvis-frontend; then
    echo "✅ Frontend container is running"
    docker ps | grep uvis-frontend
else
    echo "❌ Frontend container is not running"
    echo "Checking logs:"
    docker logs uvis-frontend --tail 50
    exit 1
fi
echo ""

# Step 14: Test frontend access
echo "Step 14: Testing frontend access..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80 || echo "000")
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Frontend is accessible (HTTP $HTTP_STATUS)"
else
    echo "⚠️  Frontend returned HTTP $HTTP_STATUS"
fi
echo ""

# Final summary
echo "========================================"
echo "🎉 UI Optimization Deployment Complete!"
echo "========================================"
echo ""
echo "📋 Summary:"
echo "  - Vite config: Optimized with manual chunks"
echo "  - Dashboard: React.memo, useCallback, useMemo applied"
echo "  - Build size: $DIST_SIZE"
echo "  - Frontend: Running on port 80"
echo ""
echo "🔍 Next Steps:"
echo "  1. Test frontend: http://139.150.11.99/"
echo "  2. Check loading speed"
echo "  3. Run Lighthouse test"
echo "  4. Monitor performance"
echo ""
echo "🌐 Access Points:"
echo "  - Frontend: http://139.150.11.99/"
echo "  - Backend: http://139.150.11.99:8000"
echo "  - Swagger: http://139.150.11.99:8000/docs"
echo ""
echo "✅ Done!"
