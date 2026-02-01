#!/bin/bash

# OrderModal 422 오류 디버깅 스크립트

echo "=========================================="
echo "  422 오류 디버깅"
echo "=========================================="
echo ""

echo "📝 Backend 로그에서 422 오류 찾기..."
docker-compose -f docker-compose.prod.yml logs backend --tail=200 | grep -A 15 -B 5 "422\|validation\|Unprocessable\|ValidationError" || echo "422 오류 로그 없음"
echo ""

echo "📝 Backend 로그에서 POST /api/v1/orders/ 요청 찾기..."
docker-compose -f docker-compose.prod.yml logs backend --tail=200 | grep -A 10 "POST.*orders" || echo "POST orders 로그 없음"
echo ""

echo "🧪 거래처 목록 확인..."
curl -s http://localhost:8000/api/v1/clients/ | python3 -m json.tool | head -30
echo ""

echo "🧪 주문 생성 API 테스트 (거래처 선택 모드)..."
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "TEST-DEBUG-001",
    "order_date": "2026-01-30",
    "temperature_zone": "FROZEN",
    "pickup_client_id": 1,
    "delivery_client_id": 2,
    "pallet_count": 10,
    "priority": 5
  }' | python3 -m json.tool
echo ""

echo "🧪 주문 생성 API 테스트 (주소 입력 모드)..."
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "TEST-DEBUG-002",
    "order_date": "2026-01-30",
    "temperature_zone": "REFRIGERATED",
    "pickup_address": "서울시 강남구 테헤란로 427",
    "delivery_address": "부산시 해운대구 센텀중앙로 48",
    "pallet_count": 20,
    "priority": 5
  }' | python3 -m json.tool
echo ""

echo "✅ 디버깅 완료!"
