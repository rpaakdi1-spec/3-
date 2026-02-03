#!/bin/bash

echo "================================================================================"
echo "주문 시간 필드 API 테스트"
echo "================================================================================"

# 주문 ID (수정 필요: 실제 주문 ID로 변경)
ORDER_ID=3

echo ""
echo "1️⃣ 기존 주문 데이터 확인"
echo "--------------------------------------------------------------------------------"
curl -s http://localhost:8000/api/v1/orders/${ORDER_ID} | jq '{
  id,
  order_number,
  order_date,
  pickup_start_time,
  pickup_end_time,
  delivery_start_time,
  delivery_end_time
}'

echo ""
echo ""
echo "2️⃣ 시간 필드 업데이트 (pickup_start_time: 10:30, pickup_end_time: 19:00)"
echo "--------------------------------------------------------------------------------"
curl -X PUT http://localhost:8000/api/v1/orders/${ORDER_ID} \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_start_time": "10:30",
    "pickup_end_time": "19:00"
  }' | jq '{
  id,
  order_number,
  pickup_start_time,
  pickup_end_time
}'

echo ""
echo ""
echo "3️⃣ 업데이트 후 데이터 재확인"
echo "--------------------------------------------------------------------------------"
curl -s http://localhost:8000/api/v1/orders/${ORDER_ID} | jq '{
  id,
  order_number,
  pickup_start_time,
  pickup_end_time,
  delivery_start_time,
  delivery_end_time
}'

echo ""
echo ""
echo "================================================================================"
echo "✅ 테스트 완료!"
echo ""
echo "예상 결과:"
echo "  - 2번에서 pickup_start_time: 10:30, pickup_end_time: 19:00 표시"
echo "  - 3번에서 동일한 시간 표시"
echo ""
echo "실패 시:"
echo "  - 로그 확인: docker logs uvis-backend --tail 100 | grep -E '🕐|✅|ERROR'"
echo "================================================================================"
