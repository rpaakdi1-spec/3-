#!/bin/bash
# diagnose_backend_health.sh - Diagnose backend health and database schema issues

echo "🔍 Backend & Database Diagnostics"
echo "=================================="
echo ""

# 1. Check backend container status
echo "=== 1. Backend Container Status ==="
docker ps -a | grep uvis-backend
echo ""

# 2. Recent backend logs (last 100 lines)
echo "=== 2. Backend Error Logs (last 100 lines) ==="
docker logs uvis-backend --tail 100 2>&1 | grep -E "ERROR|ProgrammingError|relation.*does not exist" | tail -20
echo ""

# 3. Check database connection
echo "=== 3. Database Connection Test ==="
docker exec uvis-db psql -U postgres -d uvis -c "SELECT version();" 2>&1 | head -3
echo ""

# 4. List all tables in the database
echo "=== 4. Existing Tables in Database ==="
docker exec uvis-db psql -U postgres -d uvis -c "\dt" 2>&1
echo ""

# 5. Check for dispatches and vehicles tables specifically
echo "=== 5. Check for Missing Tables (dispatches, vehicles) ==="
docker exec uvis-db psql -U postgres -d uvis -c "SELECT to_regclass('public.dispatches');" 2>&1
docker exec uvis-db psql -U postgres -d uvis -c "SELECT to_regclass('public.vehicles');" 2>&1
echo ""

# 6. Check Alembic migration history
echo "=== 6. Alembic Migration History ==="
docker exec uvis-db psql -U postgres -d uvis -c "SELECT * FROM alembic_version;" 2>&1
echo ""

# 7. Check backend health endpoint
echo "=== 7. Backend Health Endpoint Test ==="
docker exec uvis-backend curl -s http://localhost:8000/api/v1/health 2>&1 || echo "Health check failed"
echo ""

# 8. Check PostgreSQL stats
echo "=== 8. Database Stats ==="
docker exec uvis-db psql -U postgres -d uvis -c "SELECT count(*) as table_count FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';" 2>&1
echo ""

echo "✅ Diagnostics complete!"
echo ""
echo "📋 Summary of findings will help determine next steps:"
echo "  • If 'dispatches' or 'vehicles' tables are missing → Run missing migrations"
echo "  • If Alembic version is outdated → Upgrade to head"
echo "  • If backend logs show startup errors → Check environment variables"
