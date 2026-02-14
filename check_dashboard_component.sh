#!/bin/bash

echo "======================================"
echo "FinancialDashboardPage 컴포넌트 진단"
echo "======================================"
echo ""

DASHBOARD_FILE="frontend/src/pages/FinancialDashboardPage.tsx"

if [ ! -f "$DASHBOARD_FILE" ]; then
    echo "❌ $DASHBOARD_FILE 파일이 없습니다!"
    exit 1
fi

echo "=== 1. Import 문 확인 ==="
echo "Recharts 관련 import:"
grep -n "from 'recharts'" "$DASHBOARD_FILE" || echo "⚠️  Recharts import가 없습니다"
echo ""

echo "API import:"
grep -n "BillingEnhancedAPI\|billing-enhanced" "$DASHBOARD_FILE" || echo "⚠️  API import가 없습니다"
echo ""

echo "=== 2. State 확인 ==="
grep -n "useState\|data\|loading" "$DASHBOARD_FILE" | head -10
echo ""

echo "=== 3. API 호출 확인 ==="
grep -n "getFinancialDashboard\|fetchData" "$DASHBOARD_FILE" | head -5
echo ""

echo "=== 4. 차트 렌더링 확인 ==="
echo "LineChart 사용:"
grep -n "LineChart\|<LineChart" "$DASHBOARD_FILE" || echo "⚠️  LineChart가 없습니다"
echo ""

echo "BarChart 사용:"
grep -n "BarChart\|<BarChart" "$DASHBOARD_FILE" || echo "⚠️  BarChart가 없습니다"
echo ""

echo "=== 5. 요약 카드 렌더링 확인 ==="
grep -n "summary\|총 매출\|수금액\|미수금" "$DASHBOARD_FILE" | head -10
echo ""

echo "=== 6. 조건부 렌더링 확인 ==="
echo "Loading 상태:"
grep -n "loading &&\|if (loading)" "$DASHBOARD_FILE" || echo "⚠️  Loading 상태 처리가 없습니다"
echo ""

echo "데이터 확인:"
grep -n "data &&\|data\?" "$DASHBOARD_FILE" | head -5
echo ""

echo "=== 7. 전체 파일 라인 수 ==="
wc -l "$DASHBOARD_FILE"
echo ""

echo "======================================"
echo "진단 완료"
echo "======================================"
echo ""
echo "🔍 다음 단계:"
echo "1. 브라우저 F12 → Console에서 오류 확인"
echo "2. 브라우저 F12 → Network에서 API 응답 확인"
echo "3. 브라우저 F12 → Elements에서 DOM 구조 확인"
echo ""
echo "필요시 아래 명령으로 전체 파일 확인:"
echo "cat $DASHBOARD_FILE"
