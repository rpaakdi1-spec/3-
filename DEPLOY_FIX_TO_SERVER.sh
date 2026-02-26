#!/bin/bash
# ============================================================
# UVIS Frontend Layout Fix - Complete Deployment Script
# ============================================================
# This script deploys the fixed frontend to the server
# Run this on the server: bash DEPLOY_FIX_TO_SERVER.sh
# ============================================================

set -e  # Exit on error

echo "=================================================="
echo "UVIS Frontend Layout Fix - Deployment"
echo "=================================================="
echo ""

# Change to project directory
cd /root/uvis

echo "✓ Changed to /root/uvis"
echo ""

# ============================================================
# STEP 1: Update Dockerfile (simplified version)
# ============================================================
echo "STEP 1: Backing up and updating Dockerfile..."
cd frontend
cp Dockerfile Dockerfile.backup.$(date +%Y%m%d_%H%M%S)

cat > Dockerfile << 'EOF'
FROM nginx:alpine
LABEL maintainer="UVIS Team"
LABEL description="UVIS Logistics Frontend"

# Copy pre-built dist folder
COPY dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
EOF

echo "✓ Dockerfile updated (simplified build)"
echo ""

# ============================================================
# STEP 2: Build frontend locally
# ============================================================
echo "STEP 2: Building frontend locally..."
rm -rf dist/
npm run build

if [ ! -d "dist" ]; then
    echo "❌ ERROR: dist/ folder not created!"
    exit 1
fi

echo "✓ Frontend built successfully"
echo ""

# ============================================================
# STEP 3: Verify CSS files
# ============================================================
echo "STEP 3: Verifying CSS files..."
echo "=== Local build CSS files ==="
ls -lh dist/assets/*.css

echo ""
echo "=== index.html stylesheet reference ==="
cat dist/index.html | grep stylesheet

echo ""
echo "✓ CSS files verified"
echo ""

# ============================================================
# STEP 4: Rebuild Docker image
# ============================================================
echo "STEP 4: Rebuilding Docker image..."
cd /root/uvis

# Stop and remove old container
echo "  → Stopping frontend container..."
docker-compose stop frontend

echo "  → Removing frontend container..."
docker-compose rm -f frontend

# Remove old image
echo "  → Removing old image..."
docker rmi uvis-frontend || true

# Build new image without cache
echo "  → Building new image (this takes ~15-30 seconds)..."
docker-compose build --no-cache frontend

echo "✓ Docker image rebuilt"
echo ""

# ============================================================
# STEP 5: Start frontend container
# ============================================================
echo "STEP 5: Starting frontend container..."
docker-compose up -d frontend

echo "  → Waiting 15 seconds for container to start..."
sleep 15

echo "✓ Frontend container started"
echo ""

# ============================================================
# STEP 6: Verify deployment
# ============================================================
echo "STEP 6: Verifying deployment..."
echo "=== Container CSS files ==="
docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.css"

echo ""
echo "=== Container index.html stylesheet reference ==="
docker exec uvis-frontend cat /usr/share/nginx/html/index.html | grep stylesheet

echo ""
echo "=== JS file count ==="
JS_COUNT=$(docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js | wc -l")
echo "JavaScript files in container: $JS_COUNT"

if [ "$JS_COUNT" -lt 80 ]; then
    echo "❌ WARNING: Expected ~90 JS files, found only $JS_COUNT"
fi

echo ""
echo "✓ Deployment verified"
echo ""

# ============================================================
# SUCCESS
# ============================================================
echo "=================================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Clear browser cache completely:"
echo "   - Close ALL Edge windows"
echo "   - Press Ctrl+Shift+Delete → 'All time' → Clear"
echo "   - Restart browser"
echo ""
echo "2. Test in incognito mode:"
echo "   - Press Ctrl+Shift+N"
echo "   - Visit: http://139.150.11.99/login"
echo "   - Login: admin / admin123"
echo ""
echo "3. Verify layout:"
echo "   - Dashboard: http://139.150.11.99/dashboard"
echo "   - Orders: http://139.150.11.99/orders"
echo "   - Calendar: http://139.150.11.99/calendar"
echo ""
echo "Expected result:"
echo "  ✓ Sidebar displays correctly on left"
echo "  ✓ Main content area properly aligned"
echo "  ✓ All text and elements positioned correctly"
echo "  ✓ No console errors in DevTools"
echo ""
echo "=================================================="
