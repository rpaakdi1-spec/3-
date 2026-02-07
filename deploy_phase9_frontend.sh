#!/bin/bash

# Phase 9 - Production Frontend Deployment Script
# Purpose: Deploy Phase 9 frontend changes to production /root/uvis
# Author: Claude AI
# Date: 2026-02-07

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   Phase 9 - Frontend Production Deployment                    ║"
echo "║   Advanced Reporting System - PDF/Excel Download UI           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Git Update
echo -e "${BLUE}📥 Step 1/6: Git Update${NC}"
echo "Fetching latest changes from phase8-verification branch..."
cd /root/uvis
git fetch origin phase8-verification
echo ""

echo "Pulling changes..."
git pull origin phase8-verification
echo -e "${GREEN}✅ Git update complete${NC}"
echo ""

# Step 2: Check changes
echo -e "${BLUE}📋 Step 2/6: Verify Changes${NC}"
echo "Modified files:"
git diff --name-status HEAD~5 HEAD | grep frontend || echo "No frontend changes in last 5 commits"
echo ""

# Step 3: Frontend dependencies
echo -e "${BLUE}📦 Step 3/6: Install Frontend Dependencies${NC}"
cd frontend
echo "Running npm install..."
npm install
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 4: Build frontend
echo -e "${BLUE}🔨 Step 4/6: Build Frontend${NC}"
echo "Running npm run build..."
npm run build
echo -e "${GREEN}✅ Frontend build complete${NC}"
echo ""

# Step 5: Docker rebuild
echo -e "${BLUE}🐳 Step 5/6: Docker Rebuild Frontend${NC}"
cd /root/uvis
echo "Building frontend Docker image..."
docker-compose build frontend
echo -e "${GREEN}✅ Docker image built${NC}"
echo ""

# Step 6: Restart frontend
echo -e "${BLUE}🚀 Step 6/6: Restart Frontend Container${NC}"
echo "Starting frontend container..."
docker-compose up -d frontend
sleep 10
echo ""

# Verification
echo -e "${BLUE}🔍 Verification${NC}"
echo ""

echo "Container Status:"
docker ps --filter "name=uvis-frontend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "Frontend Health Check:"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80)
if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Frontend is responding: HTTP $HTTP_STATUS${NC}"
else
    echo -e "${RED}❌ Frontend health check failed: HTTP $HTTP_STATUS${NC}"
fi
echo ""

echo "Frontend Logs (last 10 lines):"
docker logs uvis-frontend --tail 10
echo ""

# Summary
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    Deployment Summary                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✅ Phase 9 Frontend Deployment Complete!${NC}"
echo ""
echo "🌐 Frontend URL: http://139.150.11.99/"
echo ""
echo "📝 Next Steps:"
echo "  1. Login: admin / admin123"
echo "  2. Navigate: 청구/정산 → 재무 대시보드"
echo "  3. Click: 보고서 다운로드 button (top-right)"
echo "  4. Select: Excel or PDF format"
echo "  5. Download and verify files"
echo ""
echo "📊 Phase 9 Features:"
echo "  • ReportDownloadModal component"
echo "  • PDF/Excel format selection"
echo "  • Date range display"
echo "  • Loading state animation"
echo "  • Automatic file download"
echo ""
echo "🧪 Testing:"
echo "  • Frontend UI: http://139.150.11.99/"
echo "  • Backend API: http://139.150.11.99:8000/docs#/Reports"
echo ""
echo -e "${YELLOW}⚠️  Remember to test both frontend and Swagger UI!${NC}"
echo ""
