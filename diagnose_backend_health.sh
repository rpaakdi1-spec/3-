#!/bin/bash

# UVIS Backend Health Diagnosis Script
# Purpose: Diagnose why backend container is unhealthy
# Location: /root/uvis/

echo "========================================="
echo "🔍 UVIS Backend Health Diagnosis"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "⚠️ Warning: docker-compose.prod.yml not found"
    echo "📁 Please run this script from /root/uvis/"
    echo ""
fi

echo "📊 1. Container Status"
echo "-------------------------------------"
docker ps --filter "name=uvis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -n 10
echo ""

echo "🏥 2. Backend Health Check Details"
echo "-------------------------------------"
HEALTH_STATUS=$(docker inspect uvis-backend --format='{{.State.Health.Status}}' 2>/dev/null || echo "N/A")
echo "Health Status: $HEALTH_STATUS"

if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "⚠️ Backend is NOT healthy!"
    echo ""
    echo "Last 3 Health Check Results:"
    docker inspect uvis-backend --format='{{range .State.Health.Log}}{{.Start}}: {{.ExitCode}} - {{.Output}}{{end}}' 2>/dev/null | tail -n 3
fi
echo ""

echo "📋 3. Backend Logs (Last 50 lines)"
echo "-------------------------------------"
docker logs uvis-backend --tail 50 2>&1
echo ""

echo "🗄️ 4. Database Connection Test"
echo "-------------------------------------"
docker exec uvis-backend python -c "
try:
    from sqlalchemy import create_engine, text
    from backend.app.core.config import settings
    print('🔗 Attempting database connection...')
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection: SUCCESS')
        print('✅ Query test: PASSED')
except Exception as e:
    print(f'❌ Database connection: FAILED')
    print(f'Error: {str(e)}')
" 2>&1
echo ""

echo "🌐 5. Backend API Health Endpoint Test"
echo "-------------------------------------"
# Try internal health check
docker exec uvis-backend curl -s http://localhost:8000/health 2>/dev/null || echo "❌ Health endpoint not responding"
echo ""

echo "🔍 6. Process Check Inside Container"
echo "-------------------------------------"
docker exec uvis-backend ps aux 2>/dev/null | grep -E "(python|uvicorn)" || echo "⚠️ No Python/Uvicorn process found"
echo ""

echo "📦 7. Backend Container Resource Usage"
echo "-------------------------------------"
docker stats uvis-backend --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""

echo "🔧 8. Recent Error Patterns"
echo "-------------------------------------"
echo "Database errors:"
docker logs uvis-backend 2>&1 | grep -i "database\|connection\|sqlalchemy" | tail -n 5
echo ""
echo "Python errors:"
docker logs uvis-backend 2>&1 | grep -i "error\|exception\|traceback" | tail -n 5
echo ""

echo "========================================="
echo "📝 Diagnosis Summary"
echo "========================================="
echo ""

# Provide diagnosis summary
if docker inspect uvis-backend --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
    echo "✅ Backend container is HEALTHY"
    echo "   No action needed."
elif docker inspect uvis-backend --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "unhealthy"; then
    echo "❌ Backend container is UNHEALTHY"
    echo ""
    echo "🔧 Recommended actions:"
    echo "   1. Check database connection (Section 4 above)"
    echo "   2. Review error logs (Sections 3 & 8)"
    echo "   3. Restart backend:"
    echo "      docker-compose -f docker-compose.prod.yml restart backend"
    echo "   4. If restart fails, rebuild:"
    echo "      ./complete_cleanup_and_redeploy.sh"
else
    echo "⚠️ Unable to determine backend health status"
    echo "   Container might not exist or health check not configured"
fi

echo ""
echo "========================================="
echo "📊 Next Steps"
echo "========================================="
echo ""
echo "If backend is unhealthy:"
echo "  1. Save this output: ./diagnose_backend_health.sh > diagnosis.log"
echo "  2. Try restart: docker-compose -f docker-compose.prod.yml restart backend"
echo "  3. Wait 30 seconds: sleep 30"
echo "  4. Check again: ./quick_status.sh"
echo ""
echo "If restart doesn't help:"
echo "  Run: ./complete_cleanup_and_redeploy.sh"
echo ""
