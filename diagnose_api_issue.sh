#!/bin/bash

#################################################
# API Diagnostic Script
# Quick check for common issues
#################################################

echo "========================================="
echo "🔍 API Issue Diagnostic Tool"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

WORK_DIR="/root/uvis"

# Check 1: Directory exists
echo -e "${BLUE}1. Checking directory...${NC}"
if [ -d "$WORK_DIR" ]; then
    echo -e "${GREEN}✅ $WORK_DIR exists${NC}"
    cd "$WORK_DIR"
else
    echo -e "${RED}❌ $WORK_DIR not found${NC}"
    echo "Current directory: $(pwd)"
    exit 1
fi
echo ""

# Check 2: Docker containers status
echo -e "${BLUE}2. Checking Docker containers...${NC}"
docker ps --format 'table {{.Names}}\t{{.Status}}' --filter "name=uvis-"
echo ""

# Check 3: Backend health
echo -e "${BLUE}3. Checking backend health...${NC}"
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null || echo '{"error":"connection failed"}')
echo "$HEALTH" | jq '.' 2>/dev/null || echo "$HEALTH"
echo ""

# Check 4: Check for has_forklift error in logs
echo -e "${BLUE}4. Checking for has_forklift error...${NC}"
HAS_ERROR=$(docker logs uvis-backend --tail 100 2>&1 | grep -c "has_forklift")
if [ "$HAS_ERROR" -gt 0 ]; then
    echo -e "${RED}❌ Found $HAS_ERROR occurrences of 'has_forklift' error${NC}"
    echo "Last error:"
    docker logs uvis-backend --tail 100 2>&1 | grep -B 2 -A 5 "has_forklift" | head -20
else
    echo -e "${GREEN}✅ No has_forklift errors found${NC}"
fi
echo ""

# Check 5: Check vehicles.py code
echo -e "${BLUE}5. Checking vehicles.py for correct attribute...${NC}"
if [ -f "backend/app/api/vehicles.py" ]; then
    if grep -q "forklift_operator_available.*vehicle.forklift_operator_available" backend/app/api/vehicles.py; then
        echo -e "${GREEN}✅ vehicles.py has correct code${NC}"
    else
        echo -e "${RED}❌ vehicles.py might have incorrect code${NC}"
        echo "Checking line 75:"
        sed -n '75p' backend/app/api/vehicles.py
    fi
else
    echo -e "${RED}❌ vehicles.py not found${NC}"
fi
echo ""

# Check 6: Test basic API call
echo -e "${BLUE}6. Testing basic vehicles API...${NC}"
API_RESPONSE=$(curl -s "http://localhost:8000/api/v1/vehicles/?limit=1" 2>&1)
if echo "$API_RESPONSE" | grep -q '"detail":"Internal server error"'; then
    echo -e "${RED}❌ API returning 500 error${NC}"
    echo "Response: $API_RESPONSE"
elif echo "$API_RESPONSE" | grep -q '"total"'; then
    echo -e "${GREEN}✅ API working${NC}"
    echo "Total vehicles: $(echo "$API_RESPONSE" | jq '.total' 2>/dev/null || echo 'unknown')"
else
    echo -e "${YELLOW}⚠️  Unexpected response${NC}"
    echo "$API_RESPONSE"
fi
echo ""

# Check 7: Test GPS API call
echo -e "${BLUE}7. Testing GPS-enabled vehicles API...${NC}"
GPS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/vehicles/?include_gps=true&limit=1" 2>&1)
if echo "$GPS_RESPONSE" | grep -q '"detail":"Internal server error"'; then
    echo -e "${RED}❌ GPS API returning 500 error${NC}"
elif echo "$GPS_RESPONSE" | grep -q '"gps_data"'; then
    echo -e "${GREEN}✅ GPS API working${NC}"
    GPS_DATA=$(echo "$GPS_RESPONSE" | jq '.items[0].gps_data' 2>/dev/null)
    if [ "$GPS_DATA" != "null" ] && [ "$GPS_DATA" != "" ]; then
        echo -e "${GREEN}✅✅ GPS data populated${NC}"
    else
        echo -e "${YELLOW}⚠️  GPS data is null${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Unexpected response${NC}"
fi
echo ""

# Check 8: Check DATABASE_URL configuration
echo -e "${BLUE}8. Checking DATABASE_URL configuration...${NC}"
if grep -q "DATABASE_URL" docker-compose.prod.yml; then
    echo -e "${GREEN}✅ DATABASE_URL found in docker-compose.prod.yml${NC}"
    # Show the DATABASE_URL line (without password)
    grep "DATABASE_URL" docker-compose.prod.yml | sed 's/:.*@/:*****@/g'
else
    echo -e "${RED}❌ DATABASE_URL not found in docker-compose.prod.yml${NC}"
fi
echo ""

# Check 9: Recent backend errors
echo -e "${BLUE}9. Recent backend errors...${NC}"
ERROR_COUNT=$(docker logs uvis-backend --tail 50 2>&1 | grep -c "ERROR\|Error\|Exception")
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $ERROR_COUNT error messages in recent logs${NC}"
    echo "Last 5 errors:"
    docker logs uvis-backend --tail 50 2>&1 | grep "ERROR\|Error\|Exception" | tail -5
else
    echo -e "${GREEN}✅ No recent errors${NC}"
fi
echo ""

# Summary
echo "========================================="
echo -e "${BLUE}Summary${NC}"
echo "========================================="
echo ""
echo "To fix issues, run:"
echo "  bash fix_and_deploy_gps.sh"
echo ""
echo "To view detailed logs:"
echo "  docker logs uvis-backend --tail 100"
echo ""
echo "To test API manually:"
echo "  curl http://localhost:8000/api/v1/vehicles/?include_gps=true | jq '.items[0]'"
echo ""
