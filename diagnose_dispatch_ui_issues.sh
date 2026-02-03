#!/bin/bash

echo "=========================================="
echo "배차 UI 전체 문제 진단"
echo "=========================================="
echo ""

# 1. 백엔드 상태 확인
echo "1️⃣ 백엔드 API 상태"
echo "------------------------------------------"
curl -s http://localhost:8000/health | jq . || echo "❌ 백엔드 연결 실패"
echo ""

# 2. 배차 데이터 확인
echo "2️⃣ 배차 데이터 현황"
echo "------------------------------------------"
echo "📊 전체 배차 통계:"
psql -U postgres -d uvis -t -c "
SELECT 
    status,
    COUNT(*) as count
FROM dispatches 
GROUP BY status
ORDER BY status;
" || echo "❌ DB 연결 실패"
echo ""

echo "📋 최근 배차 목록 (상위 5건):"
psql -U postgres -d uvis -t -c "
SELECT 
    id,
    dispatch_number,
    status,
    vehicle_id,
    dispatch_date,
    created_at
FROM dispatches 
ORDER BY created_at DESC 
LIMIT 5;
" || echo "❌ DB 연결 실패"
echo ""

# 3. 임시저장 배차와 관련 주문 확인
echo "3️⃣ 임시저장(DRAFT) 배차 상세"
echo "------------------------------------------"
psql -U postgres -d uvis -t -c "
SELECT 
    d.id,
    d.dispatch_number,
    d.vehicle_id,
    COUNT(dr.id) as route_count,
    COUNT(DISTINCT dr.order_id) as order_count
FROM dispatches d
LEFT JOIN dispatch_routes dr ON d.id = dr.dispatch_id
WHERE d.status = 'DRAFT'
GROUP BY d.id, d.dispatch_number, d.vehicle_id;
" || echo "❌ DB 연결 실패"
echo ""

# 4. 주문 상태 확인
echo "4️⃣ 주문 상태 현황"
echo "------------------------------------------"
psql -U postgres -d uvis -t -c "
SELECT 
    status,
    COUNT(*) as count
FROM orders
GROUP BY status
ORDER BY status;
" || echo "❌ DB 연결 실패"
echo ""

# 5. API 엔드포인트 테스트
echo "5️⃣ API 엔드포인트 테스트"
echo "------------------------------------------"

echo "✅ GET /api/v1/dispatches (전체 배차 목록):"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/dispatches)
if [ "$RESPONSE" -eq 200 ]; then
    echo "   ✅ 200 OK"
    TOTAL=$(curl -s http://localhost:8000/api/v1/dispatches | jq -r '.total // .items | length')
    echo "   📊 총 배차 수: $TOTAL"
else
    echo "   ❌ $RESPONSE"
fi
echo ""

echo "✅ GET /api/v1/dispatches?status=DRAFT (임시저장 필터):"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/v1/dispatches?status=DRAFT")
if [ "$RESPONSE" -eq 200 ]; then
    echo "   ✅ 200 OK"
    DRAFT_COUNT=$(curl -s "http://localhost:8000/api/v1/dispatches?status=DRAFT" | jq -r '.total // .items | length')
    echo "   📊 임시저장 배차: $DRAFT_COUNT"
else
    echo "   ❌ $RESPONSE"
fi
echo ""

echo "✅ POST /api/v1/dispatches/confirm (확정 API):"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    http://localhost:8000/api/v1/dispatches/confirm \
    -H "Content-Type: application/json" \
    -d '{"dispatch_ids": [999999]}')
if [ "$RESPONSE" -eq 200 ] || [ "$RESPONSE" -eq 422 ]; then
    echo "   ✅ 엔드포인트 존재 ($RESPONSE)"
else
    echo "   ❌ $RESPONSE"
fi
echo ""

# 6. 프런트엔드 빌드 확인
echo "6️⃣ 프런트엔드 상태 확인"
echo "------------------------------------------"
if docker ps | grep -q "uvis-frontend"; then
    echo "✅ 프런트엔드 컨테이너 실행 중"
    echo ""
    echo "📋 최근 로그 (마지막 10줄):"
    docker logs uvis-frontend --tail 10 2>&1 | grep -E "(Compiled|ready|error|warning)" || echo "   (빌드 로그 없음)"
else
    echo "❌ 프런트엔드 컨테이너 미실행"
fi
echo ""

# 7. 프런트엔드 파일 확인
echo "7️⃣ 프런트엔드 코드 점검"
echo "------------------------------------------"

echo "✅ DispatchesPage 확정 버튼 존재 여부:"
if grep -q "handleConfirmSelected" frontend/src/pages/DispatchesPage.tsx; then
    echo "   ✅ handleConfirmSelected 함수 존재"
else
    echo "   ❌ handleConfirmSelected 함수 없음"
fi

if grep -q "선택 배차 확정" frontend/src/pages/DispatchesPage.tsx; then
    echo "   ✅ 확정 버튼 UI 존재"
else
    echo "   ❌ 확정 버튼 UI 없음"
fi
echo ""

echo "✅ OptimizationPage 확정 후 리다이렉트:"
if grep -q "window.location.href = '/dispatches'" frontend/src/pages/OptimizationPage.tsx; then
    echo "   ✅ 리다이렉트 코드 존재"
else
    echo "   ❌ 리다이렉트 코드 없음"
fi
echo ""

echo "✅ API Client confirmDispatches 메서드:"
if grep -q "confirmDispatches" frontend/src/api/client.ts; then
    echo "   ✅ confirmDispatches 메서드 존재"
else
    echo "   ❌ confirmDispatches 메서드 없음"
fi
echo ""

# 8. Git 상태
echo "8️⃣ Git 상태"
echo "------------------------------------------"
echo "현재 커밋: $(git log -1 --oneline)"
echo "브랜치: $(git branch --show-current)"
echo ""

# 9. 진단 요약
echo "=========================================="
echo "🔍 진단 요약"
echo "=========================================="
echo ""

# DRAFT 배차 수 확인
DRAFT_COUNT=$(psql -U postgres -d uvis -t -c "SELECT COUNT(*) FROM dispatches WHERE status = 'DRAFT';" 2>/dev/null | xargs)

if [ -n "$DRAFT_COUNT" ] && [ "$DRAFT_COUNT" -gt 0 ]; then
    echo "✅ 임시저장 배차: ${DRAFT_COUNT}건"
else
    echo "⚠️  임시저장 배차 없음 (새로 생성 필요)"
fi

# API 상태
if [ "$RESPONSE" -eq 200 ]; then
    echo "✅ 백엔드 API: 정상"
else
    echo "❌ 백엔드 API: 문제 있음"
fi

# 프런트엔드 상태
if docker ps | grep -q "uvis-frontend"; then
    echo "✅ 프런트엔드: 실행 중"
else
    echo "❌ 프런트엔드: 미실행"
fi

echo ""
echo "=========================================="
echo "💡 다음 단계"
echo "=========================================="
echo ""

if [ -n "$DRAFT_COUNT" ] && [ "$DRAFT_COUNT" -gt 0 ]; then
    echo "1️⃣ 브라우저에서 http://139.150.11.99/dispatches 접속"
    echo "2️⃣ Ctrl+Shift+R로 강제 새로고침"
    echo "3️⃣ 임시저장 배차 선택 (체크박스)"
    echo "4️⃣ '선택 배차 확정' 녹색 버튼 클릭"
    echo ""
    echo "🔍 버튼이 보이지 않으면:"
    echo "   docker-compose -f docker-compose.prod.yml restart frontend"
    echo "   sleep 120"
    echo "   브라우저 캐시 삭제 (Ctrl+Shift+Delete)"
else
    echo "⚠️  임시저장 배차가 없습니다."
    echo ""
    echo "1️⃣ 먼저 주문 생성: http://139.150.11.99/orders"
    echo "2️⃣ AI 배차 최적화 실행"
    echo "3️⃣ 배차 확정 클릭"
    echo "4️⃣ 배차 관리 페이지에서 확인"
fi

echo ""
echo "=========================================="
