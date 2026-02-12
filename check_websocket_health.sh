#!/bin/bash

# ==============================================================================
# WebSocket Health Check Script
# ==============================================================================
# This script verifies that WebSocket errors have been resolved
# ==============================================================================

echo "🔍 WebSocket Health Check"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project directory
cd /root/uvis

# Test 1: Check container status
echo "Test 1: Backend Container Status"
if docker ps | grep -q uvis-backend; then
    echo -e "${GREEN}✅ Backend container is running${NC}"
else
    echo -e "${RED}❌ Backend container is not running${NC}"
    exit 1
fi
echo ""

# Test 2: Check for WebSocket errors in recent logs
echo "Test 2: Recent WebSocket Errors (last 5 minutes)"
ERROR_COUNT=$(docker logs uvis-backend --since 5m 2>&1 | grep -c "Error broadcasting")
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ No WebSocket errors found${NC}"
else
    echo -e "${RED}❌ Found $ERROR_COUNT WebSocket errors${NC}"
    echo "Recent errors:"
    docker logs uvis-backend --since 5m 2>&1 | grep -i "error broadcasting" | tail -5
fi
echo ""

# Test 3: Check health endpoint
echo "Test 3: Backend Health Check"
HEALTH_STATUS=$(curl -s http://localhost:8000/health | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
if [ "$HEALTH_STATUS" == "healthy" ]; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi
echo ""

# Test 4: Check database connections
echo "Test 4: Database Connectivity"
DB_LOGS=$(docker logs uvis-backend --since 1m 2>&1 | grep -i "database\|connection" | tail -3)
if [ -n "$DB_LOGS" ]; then
    echo "Recent database logs:"
    echo "$DB_LOGS"
else
    echo -e "${GREEN}✅ No database connection issues${NC}"
fi
echo ""

# Test 5: Check Redis connectivity
echo "Test 5: Redis Connectivity"
if docker ps | grep -q uvis-redis; then
    echo -e "${GREEN}✅ Redis container is running${NC}"
else
    echo -e "${YELLOW}⚠️  Redis container not found${NC}"
fi
echo ""

# Test 6: Real-time metrics service
echo "Test 6: Real-time Metrics Service"
METRICS_LOGS=$(docker logs uvis-backend --since 1m 2>&1 | grep -i "metrics broadcast")
if echo "$METRICS_LOGS" | grep -q "started"; then
    echo -e "${GREEN}✅ Metrics broadcast service is active${NC}"
else
    echo -e "${YELLOW}⚠️  Metrics broadcast service status unknown${NC}"
fi
echo ""

# Summary
echo "=========================="
echo "📊 Health Check Summary"
echo "=========================="
echo ""

if [ "$ERROR_COUNT" -eq 0 ] && [ "$HEALTH_STATUS" == "healthy" ]; then
    echo -e "${GREEN}🎉 All checks passed! WebSocket errors are resolved.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Monitor logs for 24 hours: docker logs -f uvis-backend"
    echo "2. Test frontend: http://139.150.11.99/"
    echo "3. Verify real-time dashboard updates"
    exit 0
else
    echo -e "${RED}⚠️  Some issues detected. Please review the logs above.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check full logs: docker logs uvis-backend | tail -100"
    echo "2. Restart backend: docker-compose restart backend"
    echo "3. Check configuration: cat backend/app/core/config.py"
    exit 1
fi
