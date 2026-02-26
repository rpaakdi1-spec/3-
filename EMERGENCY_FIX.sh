#!/bin/bash
################################################################################
# UVIS Emergency Layout Fix - Complete Container Rebuild
# Date: 2026-02-25
# Purpose: Fix missing JavaScript/CSS files in Docker container
################################################################################

set -e

echo "=========================================="
echo "🚨 EMERGENCY FIX - Container Rebuild"
echo "=========================================="

# Step 1: Verify we're on the server
if [ ! -d "/root/uvis" ]; then
    echo "❌ Error: /root/uvis directory not found!"
    echo "   This script must run on the server at /root/uvis"
    exit 1
fi

cd /root/uvis

# Step 2: Check current OrdersPage.tsx (if not already fixed)
echo ""
echo "Step 1/6: Checking OrdersPage.tsx..."
if grep -q "      )}" frontend/src/pages/OrdersPage.tsx && ! grep -q "    </>" frontend/src/pages/OrdersPage.tsx; then
    echo "  ⚠️  OrdersPage.tsx needs fixing..."
    python3 - <<'PYEOF'
file_path = 'frontend/src/pages/OrdersPage.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
old_pattern = """        </div>
      )}
  );
};"""
new_pattern = """        </div>
      )}
    </>
  );
};"""
if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✅ OrdersPage.tsx fixed!")
else:
    print("  ℹ️  Already fixed or different pattern")
PYEOF
else
    echo "  ✅ OrdersPage.tsx looks OK"
fi

# Step 3: Fix .dockerignore
echo ""
echo "Step 2/6: Fixing .dockerignore..."
sed -i '/^# Build output/d' frontend/.dockerignore
sed -i '/^dist$/d' frontend/.dockerignore
sed -i '/^build$/d' frontend/.dockerignore
echo "  ✅ .dockerignore updated (dist/build removed)"

# Step 4: Clean build
echo ""
echo "Step 3/6: Building frontend (clean)..."
cd frontend
rm -rf dist/ node_modules/.vite 2>/dev/null || true
echo "  🔨 Running npm run build..."
npm run build

# Verify build output
if [ ! -f "dist/index.html" ]; then
    echo "  ❌ Build failed: dist/index.html not found"
    exit 1
fi

JS_FILE=$(grep -oP 'src="/assets/\K[^"]+' dist/index.html)
CSS_FILE=$(grep -oP 'href="/assets/\K[^"]+' dist/index.html)

echo "  ✅ Build complete!"
echo "     JS:  $JS_FILE"
echo "     CSS: $CSS_FILE"

cd ..

# Step 5: Docker rebuild
echo ""
echo "Step 4/6: Rebuilding Docker container..."
docker-compose stop frontend
docker-compose rm -f frontend
docker rmi uvis-frontend 2>/dev/null || true

echo "  🐳 Building Docker image (this may take 2-3 minutes)..."
docker-compose build --no-cache frontend

# Step 6: Start container
echo ""
echo "Step 5/6: Starting container..."
docker-compose up -d frontend

echo "  ⏳ Waiting for container to be ready..."
sleep 20

# Step 7: Verify deployment
echo ""
echo "Step 6/6: Verifying deployment..."

# Check if container is running
if ! docker ps | grep -q uvis-frontend; then
    echo "  ❌ Container is not running!"
    echo "     Check logs: docker logs uvis-frontend"
    exit 1
fi

echo "  ✅ Container is running"

# Check index.html
echo ""
echo "  📄 Container index.html references:"
docker exec uvis-frontend cat /usr/share/nginx/html/index.html | grep -E 'src=|href=' | sed 's/^/     /'

# Check if JS file exists
echo ""
echo "  📦 Checking assets in container..."
CONTAINER_JS=$(docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l")
CONTAINER_CSS=$(docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.css 2>/dev/null | wc -l")

echo "     JavaScript files: $CONTAINER_JS"
echo "     CSS files: $CONTAINER_CSS"

if [ "$CONTAINER_JS" -eq 0 ]; then
    echo ""
    echo "  ❌ CRITICAL: No JavaScript files found in container!"
    echo "     This means the Docker build did NOT copy dist/ folder"
    echo ""
    echo "  🔧 MANUAL FIX REQUIRED:"
    echo "     1. Check Dockerfile COPY instruction"
    echo "     2. Verify .dockerignore doesn't block dist/"
    echo "     3. Manual copy: docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/"
    exit 1
fi

if [ "$CONTAINER_CSS" -eq 0 ]; then
    echo ""
    echo "  ⚠️  WARNING: No CSS files found in container!"
    echo "     Layout may not render correctly"
fi

echo ""
echo "  ✅ Showing first 5 JS files:"
docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.js | head -5" | sed 's/^/     /'

echo ""
echo "  ✅ Showing CSS files:"
docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.css" | sed 's/^/     /'

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🌐 Now test in browser:"
echo "   1. Open Chrome Incognito mode (Ctrl+Shift+N)"
echo "   2. Visit: http://139.150.11.99/login"
echo "   3. Login: admin / admin123"
echo "   4. Verify layout renders correctly"
echo ""
echo "   If still broken:"
echo "   - Clear cache completely (Ctrl+Shift+Delete → All time)"
echo "   - Close ALL Chrome windows"
echo "   - Restart Chrome"
echo "   - Try again in incognito mode"
echo ""
echo "📋 Git commit (after successful test):"
echo "   cd /root/uvis"
echo "   git add frontend/src/pages/OrdersPage.tsx frontend/.dockerignore"
echo '   git commit -m "fix: OrdersPage JSX fragment and Docker build"'
echo "   git push origin main"
echo ""
