#!/bin/bash
# Complete System Status Check
# Checks all aspects of the UVIS system

set -e
cd /root/uvis

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║            UVIS System Status Check                          ║"
echo "║            Date: $(date '+%Y-%m-%d %H:%M:%S')                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Docker Containers
echo "═══════════════════════════════════════════════════════════════"
echo "1. DOCKER CONTAINERS STATUS"
echo "═══════════════════════════════════════════════════════════════"
docker-compose ps
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "uvis|NAMES"
echo ""

# 2. Container Health
echo "═══════════════════════════════════════════════════════════════"
echo "2. CONTAINER HEALTH DETAILS"
echo "═══════════════════════════════════════════════════════════════"
for container in uvis-frontend uvis-backend uvis-redis uvis-db uvis-nginx; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null || echo "no health check")
        STATUS=$(docker inspect --format='{{.State.Status}}' $container 2>/dev/null)
        echo "  $container: status=$STATUS, health=$HEALTH"
    else
        echo "  $container: NOT RUNNING"
    fi
done
echo ""

# 3. Backend Health
echo "═══════════════════════════════════════════════════════════════"
echo "3. BACKEND API HEALTH"
echo "═══════════════════════════════════════════════════════════════"
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health 2>/dev/null || echo "000")
echo "  Backend /api/v1/health: $BACKEND_HEALTH"

if [ "$BACKEND_HEALTH" = "200" ]; then
    echo "  ✅ Backend is healthy"
else
    echo "  ❌ Backend is not responding correctly"
    echo ""
    echo "  Recent backend logs:"
    docker logs --tail 20 uvis-backend 2>&1 | tail -10
fi
echo ""

# 4. Frontend Check
echo "═══════════════════════════════════════════════════════════════"
echo "4. FRONTEND STATUS"
echo "═══════════════════════════════════════════════════════════════"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80/ 2>/dev/null || echo "000")
echo "  Frontend root /: $FRONTEND_STATUS"

if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "  ✅ Frontend is serving"
else
    echo "  ❌ Frontend is not responding"
fi
echo ""

echo "  Built assets:"
ls -lh frontend/dist/assets/ 2>/dev/null | grep -E "FinancialDashboard|billing-enhanced" | tail -5 || echo "  (No assets found)"
echo ""

echo "  Served assets (in container):"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/ 2>/dev/null | grep -E "FinancialDashboard|billing-enhanced" | tail -5 || echo "  (Container not accessible)"
echo ""

# 5. Database Check
echo "═══════════════════════════════════════════════════════════════"
echo "5. DATABASE STATUS"
echo "═══════════════════════════════════════════════════════════════"
DB_STATUS=$(docker exec uvis-db pg_isready -U uvis 2>/dev/null || echo "not ready")
echo "  PostgreSQL: $DB_STATUS"

if [[ "$DB_STATUS" == *"accepting connections"* ]]; then
    echo "  ✅ Database is accepting connections"
    
    # Check table count
    TABLE_COUNT=$(docker exec uvis-db psql -U uvis -d uvis -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | tr -d ' ')
    echo "  Tables in database: $TABLE_COUNT"
else
    echo "  ❌ Database is not ready"
fi
echo ""

# 6. Redis Check
echo "═══════════════════════════════════════════════════════════════"
echo "6. REDIS STATUS"
echo "═══════════════════════════════════════════════════════════════"
REDIS_PING=$(docker exec uvis-redis redis-cli ping 2>/dev/null || echo "FAILED")
echo "  Redis PING: $REDIS_PING"

if [ "$REDIS_PING" = "PONG" ]; then
    echo "  ✅ Redis is responding"
else
    echo "  ❌ Redis is not responding"
fi
echo ""

# 7. Authentication Test
echo "═══════════════════════════════════════════════════════════════"
echo "7. AUTHENTICATION TEST"
echo "═══════════════════════════════════════════════════════════════"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" 2>/dev/null)

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    # Try grep method
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -n "$TOKEN" ]; then
    echo "  ✅ Login successful"
    echo "  Token (first 30 chars): ${TOKEN:0:30}..."
else
    echo "  ❌ Login failed"
    echo "  Response: $LOGIN_RESPONSE"
fi
echo ""

# 8. Export Endpoints Test
if [ -n "$TOKEN" ]; then
    echo "═══════════════════════════════════════════════════════════════"
    echo "8. EXPORT ENDPOINTS TEST"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Test Excel export
    EXCEL_STATUS=$(curl -s -w "%{http_code}" -o /tmp/test_excel_check.xlsx \
      -H "Authorization: Bearer $TOKEN" \
      "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/excel?start_date=2026-01-01&end_date=2026-02-12" 2>/dev/null)
    
    echo "  Excel export endpoint: $EXCEL_STATUS"
    if [ "$EXCEL_STATUS" = "200" ]; then
        FILE_SIZE=$(stat -f%z /tmp/test_excel_check.xlsx 2>/dev/null || stat -c%s /tmp/test_excel_check.xlsx 2>/dev/null || echo "0")
        echo "  ✅ Excel export working (${FILE_SIZE} bytes)"
    else
        echo "  ❌ Excel export failed"
    fi
    
    # Test PDF export
    PDF_STATUS=$(curl -s -w "%{http_code}" -o /tmp/test_pdf_check.pdf \
      -H "Authorization: Bearer $TOKEN" \
      "http://localhost:8000/api/v1/billing/enhanced/export/financial-dashboard/pdf?start_date=2026-01-01&end_date=2026-02-12" 2>/dev/null)
    
    echo "  PDF export endpoint: $PDF_STATUS"
    if [ "$PDF_STATUS" = "200" ]; then
        FILE_SIZE=$(stat -f%z /tmp/test_pdf_check.pdf 2>/dev/null || stat -c%s /tmp/test_pdf_check.pdf 2>/dev/null || echo "0")
        echo "  ✅ PDF export working (${FILE_SIZE} bytes)"
    else
        echo "  ❌ PDF export failed"
    fi
    echo ""
fi

# 9. Git Status
echo "═══════════════════════════════════════════════════════════════"
echo "9. GIT STATUS"
echo "═══════════════════════════════════════════════════════════════"
echo "  Current branch:"
git branch --show-current
echo ""
echo "  Last 3 commits:"
git log --oneline -3
echo ""
echo "  Uncommitted changes:"
git status -s | head -10
if [ -z "$(git status -s)" ]; then
    echo "  ✅ No uncommitted changes"
fi
echo ""

# 10. System Resources
echo "═══════════════════════════════════════════════════════════════"
echo "10. SYSTEM RESOURCES"
echo "═══════════════════════════════════════════════════════════════"
echo "  Disk usage:"
df -h / | tail -1
echo ""
echo "  Memory usage:"
free -h | grep -E "Mem:|Swap:"
echo ""
echo "  Docker disk usage:"
docker system df
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                     SUMMARY                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

ISSUES=0

# Check each component
if ! docker ps | grep -q "uvis-frontend.*Up"; then
    echo "❌ Frontend container is not running"
    ((ISSUES++))
fi

if ! docker ps | grep -q "uvis-backend.*Up"; then
    echo "❌ Backend container is not running"
    ((ISSUES++))
fi

if [ "$BACKEND_HEALTH" != "200" ]; then
    echo "❌ Backend health check failed"
    ((ISSUES++))
fi

if [ "$FRONTEND_STATUS" != "200" ]; then
    echo "❌ Frontend not accessible"
    ((ISSUES++))
fi

if [[ "$DB_STATUS" != *"accepting connections"* ]]; then
    echo "❌ Database not accepting connections"
    ((ISSUES++))
fi

if [ "$REDIS_PING" != "PONG" ]; then
    echo "❌ Redis not responding"
    ((ISSUES++))
fi

if [ -z "$TOKEN" ]; then
    echo "❌ Authentication failed"
    ((ISSUES++))
fi

if [ -n "$TOKEN" ] && [ "$EXCEL_STATUS" != "200" ]; then
    echo "❌ Excel export not working"
    ((ISSUES++))
fi

if [ -n "$TOKEN" ] && [ "$PDF_STATUS" != "200" ]; then
    echo "❌ PDF export not working"
    ((ISSUES++))
fi

if [ $ISSUES -eq 0 ]; then
    echo "✅ ALL SYSTEMS OPERATIONAL"
    echo ""
    echo "🌐 Access the application:"
    echo "   URL: http://139.150.11.99"
    echo "   Login: admin / admin123"
    echo ""
    echo "📊 Financial Dashboard:"
    echo "   Navigate to: 청구/정산 → 재무 대시보드"
    echo "   Hover: 보고서 다운로드 button"
    echo "   Download: Excel 다운로드 or PDF 다운로드"
else
    echo "⚠️  FOUND $ISSUES ISSUE(S)"
    echo ""
    echo "🔧 Troubleshooting steps:"
    echo "   1. Check logs: docker logs --tail 100 uvis-backend"
    echo "   2. Restart services: docker-compose restart"
    echo "   3. Check network: docker network ls"
    echo "   4. Verify environment: cat .env"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Status check complete at $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════════"
