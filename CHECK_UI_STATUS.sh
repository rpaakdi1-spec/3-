#!/bin/bash

# UVIS UI Status Check Script
echo "🔍 UVIS UI Status Check"
echo "======================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Check container status
echo "1️⃣ Container Status:"
docker-compose ps | grep frontend
echo ""

# 2. Check CSS files in container
echo "2️⃣ CSS Files in Container:"
docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css" 2>/dev/null | while read file; do
    SIZE=$(docker exec uvis-frontend stat -c%s "$file" 2>/dev/null)
    echo "  $file ($SIZE bytes)"
done
echo ""

# 3. Check index.html CSS reference
echo "3️⃣ index.html CSS Reference:"
docker exec uvis-frontend grep -o 'href="/assets/[^"]*\.css"' /usr/share/nginx/html/index.html
echo ""

# 4. Check if CSS file actually exists
echo "4️⃣ Verifying CSS File Exists:"
CSS_FILE=$(docker exec uvis-frontend grep -o '/assets/index-[^"]*\.css' /usr/share/nginx/html/index.html | head -1)
if [ -n "$CSS_FILE" ]; then
    echo "  CSS file referenced: $CSS_FILE"
    if docker exec uvis-frontend test -f "/usr/share/nginx/html$CSS_FILE"; then
        echo -e "  ${GREEN}✅ File exists${NC}"
        docker exec uvis-frontend ls -lh "/usr/share/nginx/html$CSS_FILE"
    else
        echo -e "  ${RED}❌ File NOT found${NC}"
    fi
else
    echo -e "  ${RED}❌ No CSS file reference found${NC}"
fi
echo ""

# 5. Check pages with Layout
echo "5️⃣ Pages Still Using Layout:"
COUNT=$(find /root/uvis/frontend/src/pages -name "*.tsx" ! -name "LoginPage.tsx" -type f -exec grep -l "import.*Layout" {} \; 2>/dev/null | wc -l)
echo "  Found $COUNT pages with Layout imports (excluding LoginPage)"
if [ "$COUNT" -gt 0 ]; then
    find /root/uvis/frontend/src/pages -name "*.tsx" ! -name "LoginPage.tsx" -type f -exec grep -l "import.*Layout" {} \; 2>/dev/null | while read file; do
        echo "    - $(basename $file)"
    done
fi
echo ""

# 6. Check local dist CSS files
echo "6️⃣ Local dist CSS Files:"
if [ -d "/root/uvis/frontend/dist/assets" ]; then
    ls -lh /root/uvis/frontend/dist/assets/*.css 2>/dev/null || echo "  No CSS files found"
else
    echo "  dist/ directory not found"
fi
echo ""

# 7. Summary
echo "📊 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Container running?
if docker-compose ps | grep -q "frontend.*running"; then
    echo -e "  Container: ${GREEN}✅ Running${NC}"
else
    echo -e "  Container: ${RED}❌ Not running${NC}"
fi

# CSS in container?
CSS_COUNT=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css" 2>/dev/null | wc -l)
if [ "$CSS_COUNT" -gt 0 ]; then
    echo -e "  CSS files: ${GREEN}✅ Found $CSS_COUNT${NC}"
else
    echo -e "  CSS files: ${RED}❌ Not found${NC}"
fi

# Layout removed?
LAYOUT_COUNT=$(find /root/uvis/frontend/src/pages -name "*.tsx" ! -name "LoginPage.tsx" -type f -exec grep -l "import.*Layout" {} \; 2>/dev/null | wc -l)
if [ "$LAYOUT_COUNT" -eq 0 ]; then
    echo -e "  Layout cleanup: ${GREEN}✅ Complete${NC}"
else
    echo -e "  Layout cleanup: ${YELLOW}⚠️  $LAYOUT_COUNT pages remaining${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Recommendations
if [ "$CSS_COUNT" -eq 0 ]; then
    echo "🔧 Recommended Action:"
    echo "  Run: ./COMPLETE_UI_FIX.sh"
    echo "  This will rebuild and redeploy the frontend with CSS files"
elif [ "$LAYOUT_COUNT" -gt 0 ]; then
    echo "🔧 Recommended Action:"
    echo "  Run: ./COMPLETE_UI_FIX.sh"
    echo "  This will remove duplicate Layout components"
else
    echo "✅ Everything looks good!"
    echo ""
    echo "Browser troubleshooting:"
    echo "  1. Clear cache: Ctrl+Shift+Delete"
    echo "  2. Hard refresh: Ctrl+Shift+R"
    echo "  3. Try incognito: Ctrl+Shift+N"
    echo "  4. Check DevTools (F12) Network tab for CSS load errors"
fi
echo ""
