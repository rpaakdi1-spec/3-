#!/bin/bash
################################################################################
# Container Asset Diagnostic Tool
# Purpose: Identify why assets are missing from container
################################################################################

echo "=========================================="
echo "🔍 CONTAINER ASSET DIAGNOSTIC"
echo "=========================================="
echo ""

cd /root/uvis

echo "1️⃣  LOCAL BUILD STATUS"
echo "──────────────────────────────────────────"
if [ -f "frontend/dist/index.html" ]; then
    echo "✅ frontend/dist/index.html exists"
    echo ""
    echo "   Referenced files:"
    grep -E 'src=|href=' frontend/dist/index.html | sed 's/^/   /'
    echo ""
    
    JS_FILE=$(grep -oP 'src="/assets/\K[^"]+' frontend/dist/index.html || echo "NOT_FOUND")
    CSS_FILE=$(grep -oP 'href="/assets/\K[^"]+' frontend/dist/index.html || echo "NOT_FOUND")
    
    echo "   Expected JS:  /assets/$JS_FILE"
    echo "   Expected CSS: /assets/$CSS_FILE"
    echo ""
    
    if [ -f "frontend/dist/assets/$JS_FILE" ]; then
        echo "   ✅ Local JS file exists: $(ls -lh frontend/dist/assets/$JS_FILE | awk '{print $5}')"
    else
        echo "   ❌ Local JS file MISSING: frontend/dist/assets/$JS_FILE"
    fi
    
    if [ -f "frontend/dist/assets/$CSS_FILE" ]; then
        echo "   ✅ Local CSS file exists: $(ls -lh frontend/dist/assets/$CSS_FILE | awk '{print $5}')"
    else
        echo "   ❌ Local CSS file MISSING: frontend/dist/assets/$CSS_FILE"
    fi
    
    echo ""
    echo "   Total assets in frontend/dist/assets/:"
    echo "   - JS files:  $(ls frontend/dist/assets/*.js 2>/dev/null | wc -l)"
    echo "   - CSS files: $(ls frontend/dist/assets/*.css 2>/dev/null | wc -l)"
else
    echo "❌ frontend/dist/index.html NOT FOUND"
    echo "   Run: cd frontend && npm run build"
fi

echo ""
echo "2️⃣  CONTAINER STATUS"
echo "──────────────────────────────────────────"
if docker ps | grep -q uvis-frontend; then
    echo "✅ Container uvis-frontend is running"
    
    echo ""
    echo "   Container index.html content:"
    docker exec uvis-frontend cat /usr/share/nginx/html/index.html 2>/dev/null | grep -E 'src=|href=' | sed 's/^/   /'
    
    echo ""
    CONT_JS=$(docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l")
    CONT_CSS=$(docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.css 2>/dev/null | wc -l")
    
    echo "   Assets in container:"
    echo "   - JS files:  $CONT_JS"
    echo "   - CSS files: $CONT_CSS"
    
    if [ "$CONT_JS" -eq 0 ]; then
        echo ""
        echo "   ❌ CRITICAL: NO JavaScript files in container!"
    else
        echo ""
        echo "   Sample JS files (first 5):"
        docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.js 2>/dev/null | head -5" | sed 's/^/   /'
    fi
    
    if [ "$CONT_CSS" -eq 0 ]; then
        echo ""
        echo "   ❌ WARNING: NO CSS files in container!"
    else
        echo ""
        echo "   CSS files:"
        docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/assets/*.css 2>/dev/null" | sed 's/^/   /'
    fi
else
    echo "❌ Container uvis-frontend is NOT running"
    echo "   Start it: docker-compose up -d frontend"
fi

echo ""
echo "3️⃣  DOCKERFILE & DOCKERIGNORE CHECK"
echo "──────────────────────────────────────────"
if [ -f "frontend/Dockerfile" ]; then
    echo "Dockerfile COPY instructions:"
    grep "^COPY" frontend/Dockerfile | sed 's/^/   /'
else
    echo "❌ frontend/Dockerfile not found"
fi

echo ""
if [ -f "frontend/.dockerignore" ]; then
    echo ".dockerignore content:"
    cat frontend/.dockerignore | sed 's/^/   /'
    echo ""
    
    if grep -q "^dist$" frontend/.dockerignore; then
        echo "   ⚠️  WARNING: 'dist' is in .dockerignore!"
        echo "   This will BLOCK dist/ from being copied to Docker"
    fi
    
    if grep -q "^build$" frontend/.dockerignore; then
        echo "   ⚠️  WARNING: 'build' is in .dockerignore!"
    fi
else
    echo "   (no .dockerignore file)"
fi

echo ""
echo "4️⃣  DIAGNOSIS SUMMARY"
echo "──────────────────────────────────────────"

HAS_LOCAL_DIST="NO"
HAS_CONTAINER_JS="NO"
DOCKERIGNORE_BLOCKS="NO"

[ -f "frontend/dist/index.html" ] && HAS_LOCAL_DIST="YES"
[ "$CONT_JS" -gt 0 ] 2>/dev/null && HAS_CONTAINER_JS="YES"
grep -q "^dist$" frontend/.dockerignore 2>/dev/null && DOCKERIGNORE_BLOCKS="YES"

echo "Local build exists:        $HAS_LOCAL_DIST"
echo "Container has JS files:    $HAS_CONTAINER_JS"
echo ".dockerignore blocks dist: $DOCKERIGNORE_BLOCKS"

echo ""
if [ "$HAS_LOCAL_DIST" = "YES" ] && [ "$HAS_CONTAINER_JS" = "NO" ]; then
    if [ "$DOCKERIGNORE_BLOCKS" = "YES" ]; then
        echo "🎯 ROOT CAUSE: .dockerignore is blocking dist/ folder"
        echo ""
        echo "   FIX:"
        echo "   1. Remove 'dist' from frontend/.dockerignore"
        echo "   2. Rebuild: docker-compose build --no-cache frontend"
        echo "   3. Restart: docker-compose up -d frontend"
    else
        echo "🎯 ROOT CAUSE: Docker COPY instruction may be wrong"
        echo ""
        echo "   FIX:"
        echo "   1. Check frontend/Dockerfile COPY instruction"
        echo "   2. Should have: COPY dist/ /usr/share/nginx/html/"
        echo "   3. Rebuild: docker-compose build --no-cache frontend"
    fi
elif [ "$HAS_LOCAL_DIST" = "NO" ]; then
    echo "🎯 ROOT CAUSE: Local build missing"
    echo ""
    echo "   FIX:"
    echo "   cd /root/uvis/frontend && npm run build"
elif [ "$HAS_CONTAINER_JS" = "YES" ]; then
    echo "✅ Assets are present in container!"
    echo ""
    echo "   If browser still shows broken layout:"
    echo "   1. Clear browser cache completely"
    echo "   2. Close ALL browser windows"
    echo "   3. Restart browser"
    echo "   4. Test in incognito mode"
fi

echo ""
echo "=========================================="
echo "🔧 QUICK FIXES"
echo "=========================================="
echo ""
echo "Option A: Remove .dockerignore blocker & rebuild"
echo "   sed -i '/^dist$/d' frontend/.dockerignore"
echo "   docker-compose build --no-cache frontend"
echo "   docker-compose up -d frontend"
echo ""
echo "Option B: Manual copy (quick workaround)"
echo "   docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/"
echo "   docker exec uvis-frontend nginx -s reload"
echo ""
echo "Option C: Run emergency fix script"
echo "   bash EMERGENCY_FIX.sh"
echo ""
