#!/bin/bash

echo "================================================================================"
echo "🚀 백엔드 전체 재빌드 및 배포 스크립트"
echo "================================================================================"
echo ""
echo "문제: 코드 변경이 컨테이너에 반영되지 않음 (캐싱 문제)"
echo "해결: Docker 이미지 재빌드 및 컨테이너 재생성"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "${BLUE}1️⃣ 현재 상태 확인${NC}"
echo "   Git HEAD: $(git rev-parse --short HEAD)"
echo "   Branch: $(git branch --show-current)"
git log -1 --oneline
echo ""

echo "${BLUE}2️⃣ 백엔드 컨테이너 중지${NC}"
docker-compose -f docker-compose.prod.yml stop backend
echo "${GREEN}✓ 백엔드 중지 완료${NC}"
echo ""

echo "${BLUE}3️⃣ 백엔드 이미지 재빌드 (--no-cache 옵션 사용)${NC}"
echo "   ⚠️  이 작업은 5-10분 정도 소요될 수 있습니다..."
docker-compose -f docker-compose.prod.yml build --no-cache backend
echo "${GREEN}✓ 이미지 재빌드 완료${NC}"
echo ""

echo "${BLUE}4️⃣ 백엔드 컨테이너 재시작${NC}"
docker-compose -f docker-compose.prod.yml up -d backend
echo "${GREEN}✓ 컨테이너 시작 완료${NC}"
echo ""

echo "${BLUE}5️⃣ 백엔드 로그 확인 (30초 대기)${NC}"
sleep 30
docker logs uvis-backend --tail 20
echo ""

echo "${BLUE}6️⃣ Health Check${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)
if [ "$HEALTH_STATUS" = "200" ]; then
    echo "${GREEN}✓ Health Check 성공 (HTTP $HEALTH_STATUS)${NC}"
else
    echo "${RED}✗ Health Check 실패 (HTTP $HEALTH_STATUS)${NC}"
    echo "   로그 확인: docker logs uvis-backend --tail 50"
    exit 1
fi
echo ""

echo "${BLUE}7️⃣ API 테스트${NC}"
echo "   GET /api/v1/orders/3"
RESPONSE=$(curl -s http://localhost:8000/api/v1/orders/3)
echo "$RESPONSE" | jq '{id, order_number, pickup_start_time, pickup_end_time, status}'

# Check if response has valid data
ORDER_ID=$(echo "$RESPONSE" | jq -r '.id')
if [ "$ORDER_ID" != "null" ] && [ "$ORDER_ID" != "" ]; then
    echo "${GREEN}✓ API 응답 정상${NC}"
else
    echo "${RED}✗ API 응답 실패 (id가 null)${NC}"
    echo "   전체 응답:"
    echo "$RESPONSE" | jq
    exit 1
fi
echo ""

echo "${BLUE}8️⃣ 시간 업데이트 테스트${NC}"
UPDATE_RESPONSE=$(curl -s -X PUT http://localhost:8000/api/v1/orders/3 \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_start_time": "10:30",
    "pickup_end_time": "19:00"
  }')

echo "   업데이트 응답:"
echo "$UPDATE_RESPONSE" | jq '{id, order_number, pickup_start_time, pickup_end_time}'

UPDATED_TIME=$(echo "$UPDATE_RESPONSE" | jq -r '.pickup_start_time')
if [ "$UPDATED_TIME" = "10:30" ]; then
    echo "${GREEN}✓ 시간 업데이트 성공!${NC}"
else
    echo "${YELLOW}⚠ 시간 업데이트 확인 필요 (예상: 10:30, 실제: $UPDATED_TIME)${NC}"
fi
echo ""

echo "================================================================================"
echo "${GREEN}✅ 배포 완료!${NC}"
echo "================================================================================"
echo ""
echo "다음 단계:"
echo "  1. 브라우저 테스트: http://139.150.11.99/orders"
echo "  2. 주문 수정 테스트"
echo "  3. 종합 테스트: ./test_order_update_comprehensive.sh"
echo ""
echo "문제 발생 시:"
echo "  - 로그 확인: docker logs uvis-backend --tail 100"
echo "  - 컨테이너 상태: docker-compose -f docker-compose.prod.yml ps"
echo "  - 에러 로그: docker logs uvis-backend --tail 200 | grep ERROR"
echo ""
echo "================================================================================"
