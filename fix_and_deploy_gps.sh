#!/bin/bash

#################################################
# GPS & Vehicle API Complete Fix and Deploy Script
# Purpose: Fix has_forklift error and ensure GPS data is properly exposed
#################################################

set -e  # Exit on any error

echo "========================================="
echo "🚀 GPS & Vehicle API Fix Script"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check current directory
echo -e "${BLUE}📂 Step 1: Verifying working directory...${NC}"
WORK_DIR="/root/uvis"
if [ ! -d "$WORK_DIR" ]; then
    echo -e "${RED}❌ Directory $WORK_DIR does not exist!${NC}"
    echo "Current directory: $(pwd)"
    echo "Please run this script on the production server at $WORK_DIR"
    exit 1
fi

cd "$WORK_DIR"
echo -e "${GREEN}✅ Working directory: $WORK_DIR${NC}"
echo ""

# Step 2: Check git status and pull latest changes
echo -e "${BLUE}📥 Step 2: Pulling latest code from repository...${NC}"
git fetch origin main
git pull origin main
echo -e "${GREEN}✅ Latest code pulled${NC}"
echo ""

# Step 3: Verify the vehicles.py has correct attribute
echo -e "${BLUE}🔍 Step 3: Verifying vehicles.py code...${NC}"
if grep -q "forklift_operator_available" backend/app/api/vehicles.py; then
    echo -e "${GREEN}✅ vehicles.py has correct 'forklift_operator_available' attribute${NC}"
else
    echo -e "${RED}❌ vehicles.py still has has_forklift - fixing now...${NC}"
    sed -i "s/'has_forklift': vehicle.has_forklift,/'forklift_operator_available': vehicle.forklift_operator_available,/g" backend/app/api/vehicles.py
    echo -e "${GREEN}✅ Fixed has_forklift → forklift_operator_available${NC}"
fi
echo ""

# Step 4: Check docker-compose.prod.yml for DATABASE_URL
echo -e "${BLUE}🔧 Step 4: Verifying docker-compose.prod.yml...${NC}"
if grep -q "DATABASE_URL" docker-compose.prod.yml; then
    echo -e "${GREEN}✅ DATABASE_URL found in docker-compose.prod.yml${NC}"
else
    echo -e "${YELLOW}⚠️  DATABASE_URL not found in docker-compose.prod.yml${NC}"
    echo "This might cause connection issues"
fi
echo ""

# Step 5: Stop and remove old backend container
echo -e "${BLUE}🛑 Step 5: Stopping old backend container...${NC}"
docker-compose -f docker-compose.prod.yml stop backend || true
docker-compose -f docker-compose.prod.yml rm -f backend || true
echo -e "${GREEN}✅ Old backend container removed${NC}"
echo ""

# Step 6: Remove old backend image to force rebuild
echo -e "${BLUE}🗑️  Step 6: Removing old backend image...${NC}"
docker rmi uvis-backend || true
echo -e "${GREEN}✅ Old backend image removed${NC}"
echo ""

# Step 7: Rebuild and start backend
echo -e "${BLUE}🔨 Step 7: Rebuilding backend with latest code...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache backend
echo -e "${GREEN}✅ Backend rebuilt${NC}"
echo ""

echo -e "${BLUE}🚀 Step 8: Starting backend container...${NC}"
docker-compose -f docker-compose.prod.yml up -d backend
echo -e "${GREEN}✅ Backend container started${NC}"
echo ""

# Step 8: Wait for backend to be healthy
echo -e "${BLUE}⏳ Step 9: Waiting for backend to be healthy (60 seconds)...${NC}"
sleep 60
echo ""

# Step 9: Check container status
echo -e "${BLUE}📊 Step 10: Checking container status...${NC}"
docker ps --format 'table {{.Names}}\t{{.Status}}' --filter "name=uvis-backend"
echo ""

# Step 10: Check backend logs
echo -e "${BLUE}📋 Step 11: Checking backend logs...${NC}"
echo "Last 30 lines:"
docker logs uvis-backend --tail 30
echo ""

# Step 11: Test health endpoint
echo -e "${BLUE}🏥 Step 12: Testing health endpoint...${NC}"
HEALTH_STATUS=$(curl -s http://localhost:8000/health || echo '{"status":"error"}')
echo "$HEALTH_STATUS"

if echo "$HEALTH_STATUS" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo "Check logs above for errors"
fi
echo ""

# Step 12: Test vehicles API without GPS
echo -e "${BLUE}🚗 Step 13: Testing vehicles API (without GPS)...${NC}"
echo "curl http://localhost:8000/api/v1/vehicles/?limit=1"
VEHICLES_RESPONSE=$(curl -s "http://localhost:8000/api/v1/vehicles/?limit=1")
echo "$VEHICLES_RESPONSE" | jq '.' || echo "$VEHICLES_RESPONSE"
echo ""

if echo "$VEHICLES_RESPONSE" | grep -q '"detail":"Internal server error"'; then
    echo -e "${RED}❌ Vehicles API still failing${NC}"
    echo ""
    echo "=== Detailed Error Logs ==="
    docker logs uvis-backend --tail 100 | grep -B 5 -A 15 "Traceback"
    exit 1
else
    echo -e "${GREEN}✅ Vehicles API working (without GPS)${NC}"
fi
echo ""

# Step 13: Test vehicles API with GPS
echo -e "${BLUE}🌍 Step 14: Testing vehicles API with GPS data...${NC}"
echo "curl http://localhost:8000/api/v1/vehicles/?include_gps=true&limit=1"
GPS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/vehicles/?include_gps=true&limit=1")
echo "$GPS_RESPONSE" | jq '.' || echo "$GPS_RESPONSE"
echo ""

if echo "$GPS_RESPONSE" | grep -q '"detail":"Internal server error"'; then
    echo -e "${RED}❌ GPS API failing${NC}"
    echo ""
    echo "=== Detailed Error Logs ==="
    docker logs uvis-backend --tail 100 | grep -B 5 -A 15 "Traceback"
    exit 1
fi

# Check if gps_data field exists
if echo "$GPS_RESPONSE" | grep -q '"gps_data"'; then
    echo -e "${GREEN}✅ GPS data field present in response${NC}"
    
    # Check if gps_data has actual data
    GPS_DATA=$(echo "$GPS_RESPONSE" | jq '.items[0].gps_data')
    if [ "$GPS_DATA" != "null" ]; then
        echo -e "${GREEN}✅✅ GPS data successfully populated!${NC}"
        echo ""
        echo "GPS Data:"
        echo "$GPS_DATA" | jq '.'
    else
        echo -e "${YELLOW}⚠️  GPS data field exists but is null${NC}"
        echo "This might be normal if the vehicle has no GPS logs"
    fi
else
    echo -e "${RED}❌ GPS data field missing from response${NC}"
fi
echo ""

# Step 14: Summary
echo "========================================="
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "========================================="
echo ""
echo "Summary:"
echo "  1. Code updated with latest changes"
echo "  2. Backend container rebuilt and restarted"
echo "  3. API endpoints tested"
echo ""
echo "Next Steps:"
echo "  1. Test in browser: http://139.150.11.99/orders"
echo "  2. Click 'AI 배차' → Run optimization"
echo "  3. Verify GPS coordinates are displayed"
echo "  4. Check 상차지/하차지 information"
echo ""
echo "If GPS coordinates are not showing:"
echo "  1. Check browser console (F12) for errors"
echo "  2. Hard refresh: Ctrl+Shift+R"
echo "  3. Test API directly:"
echo "     curl http://139.150.11.99/api/v1/vehicles/?include_gps=true | jq '.items[0].gps_data'"
echo ""
echo "========================================="
