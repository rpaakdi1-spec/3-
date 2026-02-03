#!/bin/bash

echo "================================================================================"
echo "🔍 배차 확정 후 주문 상태 동기화 문제 진단"
echo "================================================================================"

echo ""
echo "1️⃣ 최근 배차 및 주문 상태 확인"
echo "--------------------------------------------------------------------------------"

echo "최근 배차 목록:"
curl -s http://localhost:8000/api/v1/dispatches/ | jq '.items[] | {
  id,
  dispatch_number,
  status,
  total_orders,
  dispatch_date
}' | head -20

echo ""
echo "2️⃣ 특정 배차의 상세 정보 및 연결된 주문 확인"
echo "--------------------------------------------------------------------------------"

# Get the first dispatch ID
DISPATCH_ID=$(curl -s http://localhost:8000/api/v1/dispatches/ | jq -r '.items[0].id')

if [ -z "$DISPATCH_ID" ] || [ "$DISPATCH_ID" == "null" ]; then
    echo "⚠️  배차가 없습니다"
else
    echo "배차 ID: $DISPATCH_ID"
    echo ""
    
    # Get dispatch details
    echo "배차 상세 정보:"
    DISPATCH_DETAIL=$(curl -s http://localhost:8000/api/v1/dispatches/$DISPATCH_ID)
    echo "$DISPATCH_DETAIL" | jq '{
      dispatch_number,
      status,
      dispatch_date,
      total_orders,
      route_count: (.routes | length)
    }'
    
    echo ""
    echo "배차 경로에 포함된 주문 ID들:"
    echo "$DISPATCH_DETAIL" | jq '.routes[] | select(.order_id != null) | {
      sequence,
      route_type,
      order_id
    }'
    
    # Extract order IDs
    ORDER_IDS=$(echo "$DISPATCH_DETAIL" | jq -r '.routes[] | select(.order_id != null) | .order_id')
    
    if [ ! -z "$ORDER_IDS" ]; then
        echo ""
        echo "3️⃣ 해당 주문들의 현재 상태 확인"
        echo "--------------------------------------------------------------------------------"
        
        for ORDER_ID in $ORDER_IDS; do
            echo "주문 ID: $ORDER_ID"
            curl -s http://localhost:8000/api/v1/orders/$ORDER_ID | jq '{
              order_number,
              status,
              order_date,
              pallet_count
            }'
            echo ""
        done
    else
        echo ""
        echo "⚠️  배차 경로에 주문이 연결되어 있지 않습니다!"
    fi
fi

echo ""
echo "4️⃣ DB에서 직접 확인 (서버에서 실행)"
echo "--------------------------------------------------------------------------------"
echo "다음 SQL을 실행하여 확인하세요:"
echo ""
echo "-- 배차와 연결된 주문 상태 확인"
cat << 'SQL'
SELECT 
    d.id as dispatch_id,
    d.dispatch_number,
    d.status as dispatch_status,
    dr.order_id,
    o.order_number,
    o.status as order_status,
    dr.route_type
FROM dispatches d
JOIN dispatch_routes dr ON d.id = dr.dispatch_id
LEFT JOIN orders o ON dr.order_id = o.id
WHERE d.dispatch_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY d.dispatch_date DESC, dr.sequence;
SQL

echo ""
echo "5️⃣ 배차 확정 프로세스 테스트"
echo "--------------------------------------------------------------------------------"

if [ ! -z "$DISPATCH_ID" ]; then
    DISPATCH_STATUS=$(echo "$DISPATCH_DETAIL" | jq -r '.status')
    
    if [ "$DISPATCH_STATUS" == "DRAFT" ]; then
        echo "DRAFT 상태 배차 발견 - 확정 테스트 진행 가능"
        echo ""
        echo "테스트 명령어:"
        echo "curl -X POST http://localhost:8000/api/v1/dispatches/confirm \\"
        echo "  -H 'Content-Type: application/json' \\"
        echo "  -d '{\"dispatch_ids\": [$DISPATCH_ID]}'"
    elif [ "$DISPATCH_STATUS" == "CONFIRMED" ]; then
        echo "이미 CONFIRMED 상태입니다"
        echo "주문 상태가 ASSIGNED(배차완료)가 아니라면 버그입니다!"
    else
        echo "배차 상태: $DISPATCH_STATUS"
    fi
fi

echo ""
echo "================================================================================"
echo "진단 완료!"
echo ""
echo "예상 동작:"
echo "  1. 배차 생성 시 → 주문 상태: PENDING(배차대기)"
echo "  2. 배차 확정 시 → 주문 상태: ASSIGNED(배차완료)"
echo "  3. 배송 시작 시 → 주문 상태: IN_TRANSIT(배송중)"
echo "  4. 배송 완료 시 → 주문 상태: DELIVERED(배송완료)"
echo ""
echo "문제 발견 시:"
echo "  - 배차 경로에 order_id가 null인 경우: 경로 생성 로직 문제"
echo "  - 주문 상태가 PENDING인 경우: 상태 업데이트 로직 문제"
echo "  - DB 트랜잭션 롤백 가능성"
echo "================================================================================"
