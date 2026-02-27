#!/bin/bash

# ============================================================================
# Server Performance Check Script
# ============================================================================
# 서버 과부하 원인을 진단합니다
# ============================================================================

set -e

echo "=================================================="
echo "🔍 서버 성능 및 과부하 원인 진단"
echo "=================================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "📊 1. 컨테이너 리소스 사용량"
echo "--------------------"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}"
echo ""

echo "📦 2. 컨테이너 상태"
echo "--------------------"
docker-compose ps
echo ""

echo "🔄 3. Backend 프로세스 확인"
echo "--------------------"
docker-compose exec -T backend ps aux 2>/dev/null || echo "Backend container not accessible"
echo ""

echo "🌐 4. Frontend Nginx 프로세스"
echo "--------------------"
docker-compose exec -T frontend ps aux 2>/dev/null || echo "Frontend container not accessible"
echo ""

echo "📝 5. Backend 최근 로그 (에러 확인)"
echo "--------------------"
docker-compose logs backend --tail 100 | grep -i "error\|exception\|warning\|memory\|timeout" | tail -20
echo ""

echo "📝 6. Frontend 최근 로그"
echo "--------------------"
docker-compose logs frontend --tail 50 | tail -20
echo ""

echo "🔌 7. 활성 연결 수"
echo "--------------------"
echo "Backend (port 8000):"
docker-compose exec -T backend netstat -an 2>/dev/null | grep ":8000" | wc -l || echo "N/A"
echo ""

echo "Frontend (port 80):"
docker-compose exec -T frontend netstat -an 2>/dev/null | grep ":80" | wc -l || echo "N/A"
echo ""

echo "🗄️  8. 데이터베이스 연결 수"
echo "--------------------"
docker-compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active_connections,
    count(*) FILTER (WHERE state = 'idle') as idle_connections
FROM pg_stat_activity 
WHERE datname = 'uvis_db';
" 2>/dev/null || echo "Cannot query database"
echo ""

echo "💾 9. 디스크 사용량"
echo "--------------------"
df -h | grep -E "Filesystem|/dev/vd|overlay"
echo ""

echo "🔍 10. 메모리 사용량"
echo "--------------------"
free -h
echo ""

echo "⚡ 11. CPU Load Average"
echo "--------------------"
uptime
echo ""

echo "🌀 12. 무한 루프/높은 CPU 사용 프로세스 확인"
echo "--------------------"
echo "Backend container top processes:"
docker-compose exec -T backend top -bn1 | head -20 2>/dev/null || echo "Cannot check backend processes"
echo ""

echo "🔄 13. WebSocket 연결 확인"
echo "--------------------"
docker-compose exec -T backend netstat -an 2>/dev/null | grep -i "websocket\|ws" || echo "No WebSocket connections found"
echo ""

echo "🐛 14. Backend Health Check"
echo "--------------------"
curl -s http://localhost:8000/api/v1/health | jq . 2>/dev/null || echo "Health check failed"
echo ""

echo "=================================================="
echo "✅ 진단 완료"
echo "=================================================="
echo ""
echo "💡 일반적인 과부하 원인:"
echo "  1. 무한 루프 (WebSocket reconnection)"
echo "  2. 메모리 누수 (Memory leak)"
echo "  3. 과도한 API 요청"
echo "  4. 대용량 데이터 쿼리"
echo "  5. 컨테이너 리소스 제한 초과"
echo "  6. Frontend 무한 렌더링"
echo ""
