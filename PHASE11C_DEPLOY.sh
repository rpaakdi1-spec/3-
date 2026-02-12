#!/bin/bash

# Phase 11-C Server Deployment Script
# Date: 2026-02-10
# Purpose: Deploy Rule Simulation Engine to production server

set -e  # Exit on error

echo "========================================="
echo "Phase 11-C: Rule Simulation Deployment"
echo "========================================="
echo ""

# Step 1: Navigate to project directory
echo "Step 1: Navigate to project directory..."
cd /root/uvis
pwd
echo "✅ Current directory: $(pwd)"
echo ""

# Step 2: Clean working directory
echo "Step 2: Clean working directory..."
git status
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Working directory is not clean. Stashing changes..."
    git stash
else
    echo "✅ Working directory is clean"
fi
echo ""

# Step 3: Pull latest code
echo "Step 3: Pull latest code from GitHub..."
git pull origin main
echo "✅ Code updated to latest version"
echo ""

# Step 4: Check latest commits
echo "Step 4: Verify Phase 11-C commits..."
git log --oneline -5
echo ""

# Step 5: Backend - Database Migration
echo "Step 5: Backend - Run database migrations..."
cd backend
source venv/bin/activate

echo "Running Alembic migrations..."
alembic upgrade head
echo "✅ Database migrations completed"
echo ""

cd /root/uvis
echo ""

# Step 6: Frontend - Install dependencies
echo "Step 6: Frontend - Check for new dependencies..."
cd frontend

# Check if package.json was updated
if git diff HEAD~3 HEAD --name-only | grep -q "package.json"; then
    echo "⚠️  package.json was updated. Installing new dependencies..."
    npm install --legacy-peer-deps
else
    echo "✅ No new dependencies detected"
fi
echo ""

# Step 7: Frontend - Build
echo "Step 7: Frontend - Build production bundle..."
npm run build
echo "✅ Frontend build completed"
echo ""

cd /root/uvis
echo ""

# Step 8: Verify build output
echo "Step 8: Verify build output..."
if [ -f "frontend/dist/index.html" ]; then
    echo "✅ Build successful - index.html found"
    ls -lh frontend/dist/index.html
else
    echo "❌ Build failed - index.html not found"
    exit 1
fi
echo ""

# Step 9: Stop containers
echo "Step 9: Stop backend, frontend, and nginx containers..."
docker-compose stop backend frontend nginx
echo "✅ Containers stopped"
echo ""

# Step 10: Remove old containers
echo "Step 10: Remove old containers..."
docker-compose rm -f backend frontend nginx
echo "✅ Old containers removed"
echo ""

# Step 11: Build new images
echo "Step 11: Build new Docker images (no cache)..."
echo "⚠️  This may take 3-5 minutes..."
docker-compose build --no-cache backend frontend
echo "✅ New images built"
echo ""

# Step 12: Start containers
echo "Step 12: Start containers..."
docker-compose up -d backend frontend nginx
echo "✅ Containers started"
echo ""

# Step 13: Wait for containers to be healthy
echo "Step 13: Wait for containers to be healthy (30 seconds)..."
sleep 30
echo "✅ Wait completed"
echo ""

# Step 14: Check container status
echo "Step 14: Check container status..."
docker-compose ps
echo ""

# Step 15: Test API endpoints
echo "Step 15: Test API endpoints..."

# Test backend health
echo "Testing backend health..."
curl -I http://localhost:8000/api/v1/health 2>/dev/null | head -n 1 || echo "⚠️  Backend health check failed"

# Test frontend
echo "Testing frontend..."
curl -I http://localhost/ 2>/dev/null | head -n 1 || echo "⚠️  Frontend check failed"

# Test simulations API
echo "Testing simulations templates API..."
TEMPLATES_RESPONSE=$(curl -s http://localhost:8000/api/v1/simulations/templates 2>/dev/null)
if [ -n "$TEMPLATES_RESPONSE" ]; then
    echo "✅ Simulations API is working"
    echo "Templates count: $(echo $TEMPLATES_RESPONSE | grep -o '"id"' | wc -l)"
else
    echo "⚠️  Simulations API check failed"
fi
echo ""

# Step 16: Show recent logs
echo "Step 16: Show recent backend logs..."
docker-compose logs --tail=20 backend
echo ""

echo "========================================="
echo "Phase 11-C Deployment Complete!"
echo "========================================="
echo ""
echo "📋 Next Steps:"
echo "1. Open browser: http://139.150.11.99/"
echo "2. Clear cache: Ctrl+Shift+Delete"
echo "3. Check sidebar: '규칙 시뮬레이션' menu"
echo "4. Navigate to: /simulations"
echo "5. Test simulation: Use template gallery"
echo ""
echo "📊 API Endpoints:"
echo "- GET  /api/v1/simulations/templates - List templates"
echo "- POST /api/v1/simulations - Run simulation"
echo "- GET  /api/v1/simulations - List simulations"
echo "- POST /api/v1/simulations/compare - Compare results"
echo ""
echo "🎉 Phase 11-C is now live!"
echo ""
