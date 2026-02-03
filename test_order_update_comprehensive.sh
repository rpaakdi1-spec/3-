#!/bin/bash

echo "================================================================================"
echo "🔍 주문 시간 필드 업데이트 종합 디버깅 테스트"
echo "================================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 주문 ID
ORDER_ID=3

echo ""
echo "${BLUE}📋 Step 1: 전체 주문 목록 조회 (ID 3 확인)${NC}"
echo "--------------------------------------------------------------------------------"
echo "GET /api/v1/orders/"
ORDERS_RESPONSE=$(curl -s http://localhost:8000/api/v1/orders/)
echo "$ORDERS_RESPONSE" | jq '.items[] | select(.id == 3) | {
  id,
  order_number,
  order_date,
  pickup_start_time,
  pickup_end_time,
  delivery_start_time,
  delivery_end_time,
  status
}'

echo ""
echo "${BLUE}📄 Step 2: 특정 주문 상세 조회 (GET /${ORDER_ID})${NC}"
echo "--------------------------------------------------------------------------------"
DETAIL_RESPONSE=$(curl -s http://localhost:8000/api/v1/orders/${ORDER_ID})
echo "HTTP Status: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/orders/${ORDER_ID})"
echo "$DETAIL_RESPONSE" | jq '{
  id,
  order_number,
  order_date,
  pickup_start_time,
  pickup_end_time,
  delivery_start_time,
  delivery_end_time,
  pickup_client_name,
  delivery_client_name,
  status
}'

# Extract current times for comparison
CURRENT_PICKUP_START=$(echo "$DETAIL_RESPONSE" | jq -r '.pickup_start_time')
CURRENT_PICKUP_END=$(echo "$DETAIL_RESPONSE" | jq -r '.pickup_end_time')

echo ""
echo "${YELLOW}📝 Current Times:${NC}"
echo "  pickup_start_time: ${CURRENT_PICKUP_START}"
echo "  pickup_end_time: ${CURRENT_PICKUP_END}"

echo ""
echo "${BLUE}✏️  Step 3: 시간 필드 업데이트 (PUT /${ORDER_ID})${NC}"
echo "--------------------------------------------------------------------------------"
echo "Payload: {pickup_start_time: \"10:30\", pickup_end_time: \"19:00\"}"

UPDATE_RESPONSE=$(curl -s -X PUT http://localhost:8000/api/v1/orders/${ORDER_ID} \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_start_time": "10:30",
    "pickup_end_time": "19:00"
  }')

echo "HTTP Status: $(curl -s -o /dev/null -w '%{http_code}' -X PUT http://localhost:8000/api/v1/orders/${ORDER_ID} \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_start_time": "10:30",
    "pickup_end_time": "19:00"
  }')"

echo "$UPDATE_RESPONSE" | jq '{
  id,
  order_number,
  pickup_start_time,
  pickup_end_time,
  delivery_start_time,
  delivery_end_time
}'

# Extract updated times
UPDATED_PICKUP_START=$(echo "$UPDATE_RESPONSE" | jq -r '.pickup_start_time')
UPDATED_PICKUP_END=$(echo "$UPDATE_RESPONSE" | jq -r '.pickup_end_time')

echo ""
echo "${BLUE}🔄 Step 4: 업데이트 후 재확인 (GET /${ORDER_ID})${NC}"
echo "--------------------------------------------------------------------------------"
sleep 1  # Brief pause to ensure DB has committed
VERIFY_RESPONSE=$(curl -s http://localhost:8000/api/v1/orders/${ORDER_ID})
echo "$VERIFY_RESPONSE" | jq '{
  id,
  order_number,
  pickup_start_time,
  pickup_end_time,
  delivery_start_time,
  delivery_end_time
}'

VERIFY_PICKUP_START=$(echo "$VERIFY_RESPONSE" | jq -r '.pickup_start_time')
VERIFY_PICKUP_END=$(echo "$VERIFY_RESPONSE" | jq -r '.pickup_end_time')

echo ""
echo "${BLUE}🗄️  Step 5: 직접 DB 확인 (PostgreSQL 쿼리)${NC}"
echo "--------------------------------------------------------------------------------"
echo "SQL: SELECT id, order_number, pickup_start_time, pickup_end_time FROM orders WHERE id = ${ORDER_ID};"
# This would need to be run on the server with docker exec

echo ""
echo "================================================================================"
echo "${YELLOW}📊 테스트 결과 요약${NC}"
echo "================================================================================"

echo ""
echo "Before Update:"
echo "  pickup_start_time: ${CURRENT_PICKUP_START}"
echo "  pickup_end_time: ${CURRENT_PICKUP_END}"

echo ""
echo "Update Response:"
echo "  pickup_start_time: ${UPDATED_PICKUP_START}"
echo "  pickup_end_time: ${UPDATED_PICKUP_END}"

echo ""
echo "After Update (Verification):"
echo "  pickup_start_time: ${VERIFY_PICKUP_START}"
echo "  pickup_end_time: ${VERIFY_PICKUP_END}"

echo ""
echo "Expected:"
echo "  pickup_start_time: 10:30"
echo "  pickup_end_time: 19:00"

echo ""
if [[ "$UPDATED_PICKUP_START" == "10:30" && "$UPDATED_PICKUP_END" == "19:00" ]]; then
    if [[ "$VERIFY_PICKUP_START" == "10:30" && "$VERIFY_PICKUP_END" == "19:00" ]]; then
        echo "${GREEN}✅ SUCCESS: 시간 업데이트가 정상적으로 작동합니다!${NC}"
    else
        echo "${RED}❌ PARTIAL: 업데이트 응답은 정상이지만, DB에 저장되지 않았습니다!${NC}"
        echo "${YELLOW}   → DB 트랜잭션 문제 또는 GET 엔드포인트 이슈${NC}"
    fi
else
    echo "${RED}❌ FAILED: 시간 업데이트가 작동하지 않습니다!${NC}"
    echo "${YELLOW}   → Validator 또는 API 엔드포인트 문제${NC}"
fi

echo ""
echo "================================================================================"
echo "${BLUE}🔧 추가 디버깅 명령어${NC}"
echo "================================================================================"
echo ""
echo "1. 백엔드 로그 확인:"
echo "   docker logs uvis-backend --tail 100 | grep -E '🕐|✅|Updated order|ERROR'"
echo ""
echo "2. DB 직접 확인 (서버에서 실행):"
echo "   docker exec uvis-db psql -U uvis_user -d uvis_db -c \"SELECT id, order_number, pickup_start_time, pickup_end_time FROM orders WHERE id = ${ORDER_ID};\""
echo ""
echo "3. 전체 에러 로그:"
echo "   docker logs uvis-backend --tail 200 | grep -A 5 ERROR"
echo ""
echo "================================================================================"
