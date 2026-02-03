#!/bin/bash
set -e

echo "🔍 AI 배차 최적화 프로세스 진단"
echo "=================================="
echo ""

# 1. Backend Health Check
echo "1️⃣  Backend Health Check..."
HEALTH=$(curl -s http://localhost:8000/health || echo "FAILED")
if [[ "$HEALTH" == *"healthy"* ]] || [[ "$HEALTH" == *"ok"* ]]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed: $HEALTH"
    exit 1
fi
echo ""

# 2. 배차대기 주문 확인
echo "2️⃣  배차대기 주문 확인..."
PENDING_ORDERS=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM orders WHERE status = 'PENDING';" 2>/dev/null | tr -d ' ')
echo "   배차대기 주문: ${PENDING_ORDERS}건"
if [ "$PENDING_ORDERS" -gt 0 ]; then
    echo "   최근 배차대기 주문 (최대 5건):"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT id, order_number, status, created_at FROM orders WHERE status = 'PENDING' ORDER BY created_at DESC LIMIT 5;"
fi
echo ""

# 3. 임시저장 배차 확인
echo "3️⃣  임시저장 배차 확인 (DRAFT)..."
DRAFT_DISPATCHES=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM dispatches WHERE status = 'DRAFT';" 2>/dev/null | tr -d ' ')
echo "   임시저장 배차: ${DRAFT_DISPATCHES}건"
if [ "$DRAFT_DISPATCHES" -gt 0 ]; then
    echo "   최근 임시저장 배차 (최대 5건):"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT id, dispatch_number, vehicle_id, status, total_orders, created_at FROM dispatches WHERE status = 'DRAFT' ORDER BY created_at DESC LIMIT 5;"
fi
echo ""

# 4. 확정 배차 확인
echo "4️⃣  확정 배차 확인 (CONFIRMED)..."
CONFIRMED_DISPATCHES=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM dispatches WHERE status = 'CONFIRMED';" 2>/dev/null | tr -d ' ')
echo "   확정 배차: ${CONFIRMED_DISPATCHES}건"
if [ "$CONFIRMED_DISPATCHES" -gt 0 ]; then
    echo "   최근 확정 배차 (최대 3건):"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT id, dispatch_number, vehicle_id, status, total_orders, created_at FROM dispatches WHERE status = 'CONFIRMED' ORDER BY created_at DESC LIMIT 3;"
fi
echo ""

# 5. 배차완료 주문 확인
echo "5️⃣  배차완료 주문 확인 (ASSIGNED)..."
ASSIGNED_ORDERS=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM orders WHERE status = 'ASSIGNED';" 2>/dev/null | tr -d ' ')
echo "   배차완료 주문: ${ASSIGNED_ORDERS}건"
if [ "$ASSIGNED_ORDERS" -gt 0 ]; then
    echo "   최근 배차완료 주문 (최대 5건):"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT id, order_number, status, updated_at FROM orders WHERE status = 'ASSIGNED' ORDER BY updated_at DESC LIMIT 5;"
fi
echo ""

# 6. Dispatch Routes 확인
echo "6️⃣  배차 경로 확인..."
if [ "$DRAFT_DISPATCHES" -gt 0 ]; then
    echo "   임시저장 배차의 경로 정보:"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT dr.id, dr.dispatch_id, dr.order_id, dr.route_type, dr.sequence, o.order_number 
       FROM dispatch_routes dr 
       LEFT JOIN orders o ON dr.order_id = o.id 
       WHERE dr.dispatch_id IN (SELECT id FROM dispatches WHERE status = 'DRAFT' ORDER BY created_at DESC LIMIT 1) 
       ORDER BY dr.sequence;"
fi
echo ""

# 7. API 엔드포인트 테스트
echo "7️⃣  API 엔드포인트 테스트..."

# 배차 확정 API 확인
echo "   POST /api/v1/dispatches/confirm 엔드포인트:"
CONFIRM_TEST=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/v1/dispatches/confirm \
  -H "Content-Type: application/json" \
  -d '{"dispatch_ids": []}' || echo "ERROR")
if [ "$CONFIRM_TEST" == "200" ] || [ "$CONFIRM_TEST" == "422" ]; then
    echo "   ✅ Confirm endpoint exists (HTTP $CONFIRM_TEST)"
else
    echo "   ❌ Confirm endpoint issue (HTTP $CONFIRM_TEST)"
fi

# CVRPTW 최적화 API 확인
echo "   POST /api/v1/dispatches/optimize-cvrptw 엔드포인트:"
OPTIMIZE_TEST=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8000/api/v1/dispatches/optimize-cvrptw?time_limit=30&use_time_windows=true&use_real_routing=false" \
  -H "Content-Type: application/json" \
  -d '{"order_ids": []}' || echo "ERROR")
if [ "$OPTIMIZE_TEST" == "200" ] || [ "$OPTIMIZE_TEST" == "422" ] || [ "$OPTIMIZE_TEST" == "400" ]; then
    echo "   ✅ Optimize endpoint exists (HTTP $OPTIMIZE_TEST)"
else
    echo "   ❌ Optimize endpoint issue (HTTP $OPTIMIZE_TEST)"
fi
echo ""

# 8. 로그 확인
echo "8️⃣  최근 Backend 로그 (배차 관련)..."
docker logs uvis-backend --tail 50 2>&1 | grep -E "optimize|confirm|DRAFT|ASSIGNED|dispatch" | tail -10 || echo "   (로그 없음)"
echo ""

# 9. 프로세스 흐름 요약
echo "📊 프로세스 흐름 요약"
echo "===================="
echo "   1) 배차대기 주문: ${PENDING_ORDERS}건"
echo "   2) AI 최적화 실행 → 임시저장 배차 생성: ${DRAFT_DISPATCHES}건"
echo "   3) 배차 확정 → 확정 배차: ${CONFIRMED_DISPATCHES}건"
echo "   4) 주문 상태 변경 → 배차완료: ${ASSIGNED_ORDERS}건"
echo ""

# 10. 문제 진단
echo "🔧 문제 진단"
echo "==========="

ISSUES=0

if [ "$PENDING_ORDERS" -eq 0 ] && [ "$DRAFT_DISPATCHES" -eq 0 ] && [ "$CONFIRMED_DISPATCHES" -eq 0 ]; then
    echo "   ⚠️  주문과 배차가 모두 없습니다."
    echo "      → 테스트용 주문을 먼저 생성하세요."
    ISSUES=$((ISSUES + 1))
fi

if [ "$DRAFT_DISPATCHES" -gt 0 ] && [ "$CONFIRMED_DISPATCHES" -eq 0 ]; then
    echo "   ⚠️  임시저장 배차가 있지만 확정된 배차가 없습니다."
    echo "      → 배차 확정 버튼을 클릭하지 않았거나 확정 API가 작동하지 않을 수 있습니다."
    ISSUES=$((ISSUES + 1))
fi

if [ "$CONFIRMED_DISPATCHES" -gt 0 ] && [ "$ASSIGNED_ORDERS" -eq 0 ]; then
    echo "   ⚠️  확정된 배차가 있지만 배차완료 주문이 없습니다."
    echo "      → 배차 확정 시 주문 상태 업데이트가 실패했을 수 있습니다."
    ISSUES=$((ISSUES + 1))
fi

if [ "$ISSUES" -eq 0 ]; then
    echo "   ✅ 이상 없음! 프로세스가 정상적으로 작동하고 있습니다."
fi

echo ""
echo "🎯 다음 단계"
echo "==========="
echo "1. 배차대기 주문이 없으면: 주문 관리에서 주문 생성"
echo "2. AI 배차 최적화 실행: 주문 선택 → AI 배차 버튼"
echo "3. 최적화 결과 확인: 차량별 배차 결과 표시"
echo "4. 배차 확정: '배차 확정' 버튼 클릭"
echo "5. 배차 관리 확인: /dispatches 페이지에서 확정 배차 확인"
echo "6. 주문 상태 확인: 주문 관리에서 상태가 '배차완료'로 변경되었는지 확인"
echo ""
echo "✅ 진단 완료!"
