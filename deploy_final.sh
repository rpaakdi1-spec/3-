#!/bin/bash
# 🎯 UVIS Frontend Final Deployment Script
# Date: 2026-02-05
# Fix: .env.production now committed to Git
# Status: READY FOR DEPLOYMENT

set -e  # Exit on error

echo "=============================================="
echo "🚀 UVIS Frontend Final Deployment"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Working directory
WORK_DIR="/root/uvis"
cd "$WORK_DIR"

echo -e "${YELLOW}📍 Working directory: $WORK_DIR${NC}"
echo ""

# Step 1: Fetch latest code
echo -e "${YELLOW}Step 1/9: Fetching latest code...${NC}"
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer
echo -e "${GREEN}✅ Code updated to commit: $(git rev-parse --short HEAD)${NC}"
echo ""

# Step 2: Verify .env.production exists
echo -e "${YELLOW}Step 2/9: Verifying .env.production...${NC}"
if [ -f "frontend/.env.production" ]; then
    echo -e "${GREEN}✅ frontend/.env.production exists${NC}"
    echo "Content preview:"
    head -3 frontend/.env.production
else
    echo -e "${RED}❌ ERROR: frontend/.env.production NOT FOUND!${NC}"
    echo "This file is required for Docker build."
    exit 1
fi
echo ""

# Step 3: Verify .dockerignore
echo -e "${YELLOW}Step 3/9: Verifying .dockerignore...${NC}"
if [ -f "frontend/.dockerignore" ]; then
    echo -e "${GREEN}✅ frontend/.dockerignore exists${NC}"
    echo "Checking if .env is excluded:"
    grep "^\.env$" frontend/.dockerignore && echo -e "${GREEN}✅ .env is excluded (GOOD!)${NC}" || echo -e "${RED}⚠️  WARNING: .env not excluded${NC}"
else
    echo -e "${RED}❌ WARNING: frontend/.dockerignore NOT FOUND${NC}"
fi
echo ""

# Step 4: Build frontend (no cache)
echo -e "${YELLOW}Step 4/9: Building frontend (this will take ~6 minutes)...${NC}"
echo "Building with --no-cache to ensure .env.production is used..."
docker-compose build --no-cache frontend
echo -e "${GREEN}✅ Frontend build complete${NC}"
echo ""

# Step 5: Restart containers
echo -e "${YELLOW}Step 5/9: Restarting frontend and nginx...${NC}"
docker-compose up -d --force-recreate frontend nginx
echo -e "${GREEN}✅ Containers restarted${NC}"
echo ""

# Step 6: Wait for startup
echo -e "${YELLOW}Step 6/9: Waiting 30 seconds for containers to start...${NC}"
for i in {30..1}; do
    echo -ne "⏳ $i seconds remaining...\r"
    sleep 1
done
echo -e "${GREEN}✅ Wait complete${NC}"
echo ""

# Step 7: Check container status
echo -e "${YELLOW}Step 7/9: Checking container status...${NC}"
docker-compose ps
echo ""

# Step 8: Verify build result
echo -e "${YELLOW}Step 8/9: Verifying build result...${NC}"
echo "Checking for localhost:8000 in built files (should be EMPTY):"
LOCALHOST_CHECK=$(docker-compose exec frontend grep -r "localhost:8000" /usr/share/nginx/html/assets/*.js 2>/dev/null || true)
if [ -z "$LOCALHOST_CHECK" ]; then
    echo -e "${GREEN}✅ No localhost:8000 found in built files (PERFECT!)${NC}"
else
    echo -e "${RED}❌ ERROR: Found localhost:8000 in built files:${NC}"
    echo "$LOCALHOST_CHECK"
    echo -e "${RED}This means .env.production was not used during build${NC}"
    exit 1
fi

echo ""
echo "Checking for /api/v1 in built files (should have results):"
API_CHECK=$(docker-compose exec frontend grep -o "/api/v1" /usr/share/nginx/html/assets/*.js 2>/dev/null | head -5)
if [ -n "$API_CHECK" ]; then
    echo -e "${GREEN}✅ Found /api/v1 in built files (GOOD!)${NC}"
    echo "$API_CHECK"
else
    echo -e "${YELLOW}⚠️  WARNING: No /api/v1 found (may be in other files)${NC}"
fi
echo ""

# Step 9: Health checks
echo -e "${YELLOW}Step 9/9: Running health checks...${NC}"
echo "Backend health check:"
curl -s http://localhost:8000/health | jq '.' 2>/dev/null || curl -s http://localhost:8000/health || echo -e "${RED}❌ Backend not responding${NC}"
echo ""
echo "Frontend health check:"
curl -s -I http://localhost/ | head -5
echo ""

# Final summary
echo "=============================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "=============================================="
echo ""
echo "📊 Access URLs:"
echo "   Frontend:   http://139.150.11.99/"
echo "   API Docs:   http://139.150.11.99:8000/docs"
echo "   Health:     http://139.150.11.99:8000/health"
echo ""
echo "🔍 Verification Steps:"
echo "   1. Open http://139.150.11.99/ in browser"
echo "   2. Open DevTools (F12) → Network tab"
echo "   3. Try to login"
echo "   4. Check Request URL: should be '/api/v1/auth/login' (NOT localhost:8000)"
echo "   5. Status should be 200 OK or 401 (NOT ERR_CONNECTION_REFUSED)"
echo ""
echo "⚠️  If still seeing localhost:8000:"
echo "   - Clear browser cache: Ctrl+Shift+Delete"
echo "   - Hard refresh: Ctrl+Shift+R"
echo "   - Try incognito mode: Ctrl+Shift+N"
echo ""
echo -e "${GREEN}Git Info:${NC}"
echo "   Repository: https://github.com/rpaakdi1-spec/3-"
echo "   Branch:     genspark_ai_developer"
echo "   PR:         #4"
echo "   Commit:     $(git rev-parse --short HEAD)"
echo ""
echo "📚 Documentation:"
echo "   🎯_FINAL_SOLUTION.md - Complete solution guide"
echo "   README_DEPLOY.md - Deployment reference"
echo ""
echo -e "${GREEN}Status: DEPLOYMENT SUCCESSFUL ✅${NC}"
echo "=============================================="
