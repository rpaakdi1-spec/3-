#!/bin/bash
# 간단한 배포 체크 스크립트
# 사용법: bash quick_check.sh

echo "════════════════════════════════════════════════════════════════"
echo "  🔍 UVIS ML 배차 시스템 - 빠른 상태 확인"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 컨테이너 상태
echo "1️⃣  컨테이너 상태:"
if docker ps | grep -q "uvis-backend.*Up"; then
    echo -e "   ${GREEN}✓${NC} Backend: 실행 중"
else
    echo -e "   ${RED}✗${NC} Backend: 중지됨"
fi

if docker ps | grep -q "uvis-frontend.*Up"; then
    echo -e "   ${GREEN}✓${NC} Frontend: 실행 중"
else
    echo -e "   ${RED}✗${NC} Frontend: 중지됨"
fi

if docker ps | grep -q "redis.*Up"; then
    echo -e "   ${GREEN}✓${NC} Redis: 실행 중"
else
    echo -e "   ${RED}✗${NC} Redis: 중지됨"
fi
echo ""

# 2. API 헬스
echo "2️⃣  API 헬스 체크:"
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓${NC} Backend API: 정상"
else
    echo -e "   ${RED}✗${NC} Backend API: 응답 없음"
fi

if docker exec -it uvis-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo -e "   ${GREEN}✓${NC} Redis: 연결 정상"
else
    echo -e "   ${RED}✗${NC} Redis: 연결 실패"
fi
echo ""

# 3. ML Dispatch API
echo "3️⃣  ML Dispatch API:"
if curl -sf http://localhost:8000/api/ml-dispatch/ab-test/stats > /dev/null 2>&1; then
    ROLLOUT=$(curl -s http://localhost:8000/api/ml-dispatch/ab-test/stats | grep -o '"rollout_percentage":[0-9]*' | cut -d: -f2)
    echo -e "   ${GREEN}✓${NC} ML Dispatch API: 정상"
    echo "   📊 현재 롤아웃: ${ROLLOUT}%"
else
    echo -e "   ${YELLOW}⚠${NC} ML Dispatch API: 데이터 없음 (정상, 처음 실행 시)"
fi
echo ""

# 4. 최근 에러 체크
echo "4️⃣  최근 에러 (최근 10줄):"
ERRORS=$(docker logs uvis-backend --tail 100 2>&1 | grep -i "error" | tail -10)
if [ -z "$ERRORS" ]; then
    echo -e "   ${GREEN}✓${NC} 최근 에러 없음"
else
    echo -e "   ${YELLOW}⚠${NC} 에러 발견:"
    echo "$ERRORS" | head -3
    echo "   ... (전체 로그: docker logs uvis-backend)"
fi
echo ""

# 5. 리소스 사용량
echo "5️⃣  리소스 사용량:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep uvis
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "  📝 빠른 명령어"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "로그 확인:"
echo "  docker logs uvis-backend --tail 50 -f"
echo ""
echo "파일럿 롤아웃 (10%):"
echo "  ./scripts/gradual_rollout.sh pilot"
echo ""
echo "모니터링 시작:"
echo "  nohup ./scripts/monitor_pilot.sh > logs/monitor_output.log 2>&1 &"
echo ""
echo "실시간 로그:"
echo "  tail -f logs/monitor_output.log"
echo ""
echo "긴급 롤백:"
echo "  ./scripts/gradual_rollout.sh rollback"
echo ""
