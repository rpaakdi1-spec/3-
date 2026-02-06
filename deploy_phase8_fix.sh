#!/bin/bash

##############################################################################
# Phase 8 Production Deployment Script
# Date: 2026-02-06
# Purpose: Deploy Phase 8 API path fix to production
##############################################################################

set -e  # Exit on error

echo "=================================================="
echo "Phase 8: Production Deployment"
echo "Deploying API Path Fix (Commit: 21e524f)"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_DIR="/root/uvis"
BRANCH="genspark_ai_developer"
FRONTEND_DIR="$REPO_DIR/frontend"

echo -e "${YELLOW}Step 1: Pre-deployment checks${NC}"
echo "-------------------------------------------"

# Check if we're in the right directory
if [ ! -d "$REPO_DIR" ]; then
    echo -e "${RED}❌ Error: Repository directory not found: $REPO_DIR${NC}"
    exit 1
fi

cd "$REPO_DIR"
echo -e "${GREEN}✓${NC} Repository directory found"

# Check git branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo -e "${YELLOW}⚠ Warning: Current branch is $CURRENT_BRANCH, switching to $BRANCH${NC}"
    git checkout "$BRANCH"
fi
echo -e "${GREEN}✓${NC} On correct branch: $BRANCH"

echo ""
echo -e "${YELLOW}Step 2: Fetch latest changes${NC}"
echo "-------------------------------------------"
git fetch origin "$BRANCH"
echo -e "${GREEN}✓${NC} Fetched latest changes"

# Show current commit
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "Current commit: $CURRENT_COMMIT"

# Show remote commit
REMOTE_COMMIT=$(git rev-parse --short "origin/$BRANCH")
echo "Remote commit: $REMOTE_COMMIT"

if [ "$CURRENT_COMMIT" == "$REMOTE_COMMIT" ]; then
    echo -e "${YELLOW}⚠ No new commits to pull${NC}"
else
    echo ""
    echo -e "${YELLOW}Step 3: Pull latest changes${NC}"
    echo "-------------------------------------------"
    git pull origin "$BRANCH"
    echo -e "${GREEN}✓${NC} Pulled latest changes"
fi

echo ""
echo -e "${YELLOW}Step 4: Install frontend dependencies${NC}"
echo "-------------------------------------------"
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing node modules..."
    npm install
else
    echo "node_modules exists, skipping install"
fi
echo -e "${GREEN}✓${NC} Dependencies ready"

echo ""
echo -e "${YELLOW}Step 5: Build frontend${NC}"
echo "-------------------------------------------"
echo "Building production frontend..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo -e "${RED}❌ Error: Build failed - dist directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Frontend build successful"

echo ""
echo -e "${YELLOW}Step 6: Rebuild Docker containers${NC}"
echo "-------------------------------------------"
cd "$REPO_DIR"

echo "Building frontend Docker image (no cache)..."
docker-compose build --no-cache frontend
echo -e "${GREEN}✓${NC} Frontend Docker image built"

echo ""
echo -e "${YELLOW}Step 7: Restart services${NC}"
echo "-------------------------------------------"

echo "Restarting frontend container..."
docker-compose up -d frontend
echo -e "${GREEN}✓${NC} Frontend container restarted"

echo "Restarting backend container..."
docker-compose restart backend
echo -e "${GREEN}✓${NC} Backend container restarted"

# Wait a moment for services to start
echo "Waiting for services to start..."
sleep 5

echo ""
echo -e "${YELLOW}Step 8: Health checks${NC}"
echo "-------------------------------------------"

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://139.150.11.99/ || echo "000")
if [ "$FRONTEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend health check: $FRONTEND_STATUS OK"
else
    echo -e "${RED}❌${NC} Frontend health check failed: $FRONTEND_STATUS"
fi

# Check backend
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://139.150.11.99:8000/health || echo "000")
if [ "$BACKEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓${NC} Backend health check: $BACKEND_STATUS OK"
else
    echo -e "${RED}❌${NC} Backend health check failed: $BACKEND_STATUS"
fi

echo ""
echo -e "${YELLOW}Step 9: Container status${NC}"
echo "-------------------------------------------"
docker-compose ps

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo "1. Clear browser cache (Ctrl+Shift+R)"
echo "2. Test Phase 8 pages:"
echo "   - http://139.150.11.99/billing/financial-dashboard"
echo "   - http://139.150.11.99/billing/charge-preview"
echo "   - http://139.150.11.99/billing/auto-schedule"
echo "   - http://139.150.11.99/billing/settlement-approval"
echo "   - http://139.150.11.99/billing/payment-reminder"
echo "   - http://139.150.11.99/billing/export-task"
echo ""
echo "3. Check browser console (F12) for API errors"
echo "4. Verify API calls go to /api/v1/... (not /api/v1/api/v1/...)"
echo ""
echo "📊 Useful Commands:"
echo "  - View frontend logs: docker logs uvis-frontend --tail 100"
echo "  - View backend logs: docker logs uvis-backend --tail 100"
echo "  - Follow backend logs: docker logs uvis-backend -f"
echo ""
echo "🔗 Documentation:"
echo "  - PHASE_8_API_PATH_FIX.md"
echo "  - PHASE_8_PRODUCTION_DEPLOYMENT.md"
echo ""

# Final commit info
echo "📝 Deployed Commit:"
git log --oneline -1
echo ""
