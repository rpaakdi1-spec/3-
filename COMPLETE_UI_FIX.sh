#!/bin/bash

# UVIS UI Complete Fix Script
# This script removes duplicate Layout components and rebuilds the frontend

echo "🚀 UVIS UI Complete Fix Script"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PAGES_DIR="/root/uvis/frontend/src/pages"
BACKUP_DIR="/root/uvis/frontend/src/pages/layout_removal_backup_$(date +%Y%m%d_%H%M%S)"

# Step 1: Create backup
echo "📦 Step 1: Creating backup..."
mkdir -p "$BACKUP_DIR"
cp -v "$PAGES_DIR"/*.tsx "$BACKUP_DIR/" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup created: $BACKUP_DIR${NC}"
else
    echo -e "${RED}❌ Backup failed${NC}"
    exit 1
fi
echo ""

# Step 2: Remove Layout from pages
echo "🔧 Step 2: Removing Layout from pages..."
echo ""

# Pages to fix (all except LoginPage)
PAGES_TO_FIX=(
    "ABTestMonitorPage.tsx"
    "AIChatPage.tsx"
    "AlertSettingsPage.tsx"
    "AnalyticsPage.tsx"
    "ClientsPage.tsx"
    "DashboardPage.tsx"
    "DeliveryTrackingPage.tsx"
    "DispatchMonitoringPage.tsx"
    "DispatchRulesPage.tsx"
    "DriversPage.tsx"
    "FinancialDashboardPage.tsx"
    "MaintenancePage.tsx"
    "MessagesPage.tsx"
    "NoticePage.tsx"
    "NotificationsPage.tsx"
    "OptimizationPage.tsx"
    "OrderCalendarPage.tsx"
    "OrdersPage.tsx"
    "PlacesPage.tsx"
    "RecurringOrdersPage.tsx"
    "ReportsPage.tsx"
    "SettingsPage.tsx"
    "TemperatureAlertsPage.tsx"
    "TemperatureMonitoringPage.tsx"
    "VehiclesPage.tsx"
)

SUCCESS_COUNT=0
FAIL_COUNT=0

for PAGE in "${PAGES_TO_FIX[@]}"; do
    PAGE_PATH="$PAGES_DIR/$PAGE"
    
    if [ ! -f "$PAGE_PATH" ]; then
        echo "⏭️  Skipped: $PAGE (file not found)"
        continue
    fi
    
    echo "Processing: $PAGE"
    
    # Check if Layout import exists
    if ! grep -q "import.*Layout" "$PAGE_PATH"; then
        echo "  ✓ No Layout import found (already clean)"
        ((SUCCESS_COUNT++))
        continue
    fi
    
    # Create temporary file
    TEMP_FILE="/tmp/${PAGE}.tmp"
    cp "$PAGE_PATH" "$TEMP_FILE"
    
    # Remove import line
    sed -i '/import.*Layout.*from.*@\/components\/Layout/d' "$TEMP_FILE"
    
    # Remove <Layout> opening tag and its closing tag
    # This handles both single-line and multi-line Layout tags
    sed -i '/<Layout>/,/<\/Layout>/c\
<>\
<\/>' "$TEMP_FILE"
    
    # Alternative: Simple removal if above doesn't work
    sed -i 's/<Layout>//g' "$TEMP_FILE"
    sed -i 's/<\/Layout>//g' "$TEMP_FILE"
    
    # Clean up empty lines
    sed -i '/^$/N;/^\n$/D' "$TEMP_FILE"
    
    # Copy back
    cp "$TEMP_FILE" "$PAGE_PATH"
    rm "$TEMP_FILE"
    
    # Verify
    if ! grep -q "import.*Layout" "$PAGE_PATH"; then
        echo -e "  ${GREEN}✅ Successfully removed Layout${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "  ${RED}❌ Failed to remove Layout${NC}"
        ((FAIL_COUNT++))
    fi
done

echo ""
echo "Results:"
echo "  ✅ Success: $SUCCESS_COUNT"
echo "  ❌ Failed: $FAIL_COUNT"
echo ""

# Step 3: Verify no Layout imports remain
echo "🔍 Step 3: Verifying Layout removal..."
REMAINING=$(find "$PAGES_DIR" -name "*.tsx" ! -name "LoginPage.tsx" -type f -exec grep -l "import.*Layout" {} \; | wc -l)

if [ "$REMAINING" -eq 0 ]; then
    echo -e "${GREEN}✅ All Layout imports removed (except LoginPage)${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: $REMAINING files still contain Layout imports:${NC}"
    find "$PAGES_DIR" -name "*.tsx" ! -name "LoginPage.tsx" -type f -exec grep -l "import.*Layout" {} \;
fi
echo ""

# Step 4: Build frontend
echo "🔨 Step 4: Building frontend..."
cd /root/uvis/frontend

# Remove old dist
rm -rf dist/

# Build
echo "Running npm run build..."
BUILD_START=$(date +%s)
npm run build
BUILD_EXIT=$?
BUILD_END=$(date +%s)
BUILD_TIME=$((BUILD_END - BUILD_START))

if [ $BUILD_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Build successful (${BUILD_TIME}s)${NC}"
    echo ""
    
    # Verify CSS files
    echo "Verifying CSS files..."
    CSS_COUNT=$(find dist/assets -name "*.css" 2>/dev/null | wc -l)
    if [ "$CSS_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $CSS_COUNT CSS files in dist/assets${NC}"
        ls -lh dist/assets/*.css
    else
        echo -e "${RED}❌ No CSS files found in dist/assets${NC}"
    fi
    echo ""
else
    echo -e "${RED}❌ Build failed${NC}"
    echo ""
    echo "To restore backup:"
    echo "  cp $BACKUP_DIR/*.tsx $PAGES_DIR/"
    exit 1
fi

# Step 5: Rebuild Docker image
echo "🐳 Step 5: Rebuilding Docker image..."
cd /root/uvis

DOCKER_START=$(date +%s)
docker-compose build --no-cache frontend
DOCKER_EXIT=$?
DOCKER_END=$(date +%s)
DOCKER_TIME=$((DOCKER_END - DOCKER_START))

if [ $DOCKER_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built (${DOCKER_TIME}s)${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi
echo ""

# Step 6: Restart container
echo "🔄 Step 6: Restarting container..."
docker-compose up -d frontend
sleep 10

# Check container status
if docker-compose ps | grep -q "frontend.*running"; then
    echo -e "${GREEN}✅ Frontend container running${NC}"
else
    echo -e "${RED}❌ Frontend container not running${NC}"
    docker-compose logs --tail=50 frontend
    exit 1
fi
echo ""

# Step 7: Verify files in container
echo "🔍 Step 7: Verifying files in container..."

# Check if CSS files exist
CSS_IN_CONTAINER=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css" 2>/dev/null | wc -l)
if [ "$CSS_IN_CONTAINER" -gt 0 ]; then
    echo -e "${GREEN}✅ Found $CSS_IN_CONTAINER CSS files in container${NC}"
    docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css" -exec ls -lh {} \;
else
    echo -e "${RED}❌ No CSS files found in container${NC}"
    echo "Attempting to copy CSS files manually..."
    docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/
    docker exec uvis-frontend nginx -s reload
fi
echo ""

# Check index.html
echo "Checking index.html CSS reference..."
CSS_LINK=$(docker exec uvis-frontend grep -o 'href="/assets/index-[^"]*\.css"' /usr/share/nginx/html/index.html | head -1)
if [ -n "$CSS_LINK" ]; then
    echo "Found CSS link: $CSS_LINK"
    CSS_FILE=$(echo "$CSS_LINK" | sed 's/href="//;s/"//')
    if docker exec uvis-frontend test -f "/usr/share/nginx/html$CSS_FILE"; then
        echo -e "${GREEN}✅ CSS file exists in container${NC}"
    else
        echo -e "${RED}❌ CSS file NOT found in container: $CSS_FILE${NC}"
    fi
else
    echo -e "${RED}❌ No CSS link found in index.html${NC}"
fi
echo ""

# Final summary
TOTAL_TIME=$((BUILD_TIME + DOCKER_TIME))
echo "================================"
echo "✅ Deployment Complete!"
echo "================================"
echo ""
echo "Summary:"
echo "  • Layout removal: $SUCCESS_COUNT pages fixed"
echo "  • Build time: ${BUILD_TIME}s"
echo "  • Docker build time: ${DOCKER_TIME}s"
echo "  • Total time: ${TOTAL_TIME}s"
echo "  • Backup location: $BACKUP_DIR"
echo ""
echo "Next Steps:"
echo "  1. Clear browser cache: Ctrl+Shift+Delete → All time → Cookies & Cache"
echo "  2. Restart Chrome completely"
echo "  3. Visit: http://139.150.11.99/login"
echo "  4. Login: admin / admin123"
echo "  5. Check sidebar and navigation"
echo ""
echo "If issues persist:"
echo "  • Force refresh: Ctrl+Shift+R"
echo "  • Try incognito mode: Ctrl+Shift+N"
echo "  • Check browser console (F12) for errors"
echo "  • Run: docker exec uvis-frontend cat /usr/share/nginx/html/index.html | grep css"
echo ""
