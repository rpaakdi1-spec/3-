#!/bin/bash
# UVIS Frontend Fix Deployment Script
# Apply on server: /root/uvis

set -e

echo "========================================"
echo "UVIS 실시간 통계 표시 수정 배포"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: 현재 상태 확인${NC}"
echo "-------------------"
docker ps --filter name=uvis-frontend --format "table {{.Names}}\t{{.Status}}"
echo ""

echo -e "${YELLOW}Step 2: 최신 코드 가져오기${NC}"
echo "-------------------"
cd /root/uvis
git fetch origin main
git log --oneline -3 origin/main

echo ""
read -p "위 커밋들을 적용하시겠습니까? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "배포 취소됨"
    exit 1
fi

git pull origin main
echo -e "${GREEN}✓ 코드 업데이트 완료${NC}"
echo ""

echo -e "${YELLOW}Step 3: 프론트엔드 재빌드${NC}"
echo "-------------------"
echo "Frontend 컨테이너를 중지하고 재빌드합니다..."
docker-compose down frontend
docker-compose up -d --build frontend
echo -e "${GREEN}✓ Frontend 재빌드 완료${NC}"
echo ""

echo -e "${YELLOW}Step 4: 서비스 시작 대기 (30초)${NC}"
echo "-------------------"
for i in {30..1}; do
    echo -ne "\r대기 중... $i초 남음  "
    sleep 1
done
echo -e "\n${GREEN}✓ 대기 완료${NC}"
echo ""

echo -e "${YELLOW}Step 5: 서비스 상태 확인${NC}"
echo "-------------------"
docker ps --filter name=uvis-frontend --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo -e "${YELLOW}Step 6: API 응답 검증${NC}"
echo "-------------------"
echo "Testing: /api/v1/vehicles/analytics/fleet (last 7 days)"
curl -s "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=$(date -d '7 days ago' +%Y-%m-%d)&end_date=$(date +%Y-%m-%d)" \
  | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'✓ Total: {d[\"total_vehicles\"]}, Active: {d[\"active_vehicles\"]}, Distance: {d[\"total_distance_km\"]} km, Stats: {len(d[\"vehicle_stats\"])} vehicles')"
echo ""

echo -e "${YELLOW}Step 7: Frontend 접속 테스트${NC}"
echo "-------------------"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://139.150.11.99/)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Frontend 정상 응답 (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Frontend 응답 이상 (HTTP $HTTP_CODE)${NC}"
fi
echo ""

echo "========================================"
echo -e "${GREEN}배포 완료!${NC}"
echo "========================================"
echo ""
echo "📋 다음 단계:"
echo "1. 브라우저에서 http://139.150.11.99/ 접속"
echo "2. Ctrl+Shift+R (강력 새로고침)"
echo "3. UVIS 실시간 통계 섹션 확인:"
echo "   - 운행 중 차량: 46대 / 46대 (이전: 0대)"
echo "   - 총 주행 거리: 183.0 km"
echo "   - 평균 속도: 26.8 km/h"
echo "   - 최고 속도: 105.0 km/h"
echo ""
echo "🐛 문제가 지속되면:"
echo "   - F12 > Console 탭에서 에러 확인"
echo "   - F12 > Network 탭에서 'fleet' 요청 확인"
echo "   - bash /root/uvis/debug_uvis_frontend.sh 실행"
echo ""
