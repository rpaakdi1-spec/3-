#!/bin/bash

echo "======================================"
echo "재무 대시보드 차트 진단 스크립트"
echo "======================================"
echo ""

echo "=== 1. API 응답 확인 ==="
echo "브라우저 콘솔에서 토큰을 확인하세요:"
echo "localStorage.getItem('access_token')"
echo ""

# Use the token from earlier in conversation
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJBRE1JTiIsImV4cCI6MTc3MDkxMDE5MX0.oCkeT-Yc3daW0n2TAhaCw7NJGmpoDUZlhBLggdeKDfI"

echo "API 호출 테스트 중..."
RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/billing/enhanced/dashboard/financial?start_date=2026-01-01&end_date=2026-02-12" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo ""

# Check if response has data
if echo "$RESPONSE" | grep -q "summary"; then
    echo "✅ API 응답에 데이터 있음"
    
    # Extract summary values
    echo ""
    echo "=== 요약 데이터 ==="
    echo "$RESPONSE" | jq '.summary' 2>/dev/null
    
    echo ""
    echo "=== 월별 추이 데이터 (처음 3개) ==="
    echo "$RESPONSE" | jq '.monthly_trends[:3]' 2>/dev/null
    
    echo ""
    echo "=== 상위 고객 데이터 (처음 3개) ==="
    echo "$RESPONSE" | jq '.top_clients[:3]' 2>/dev/null
else
    echo "❌ API 응답에 데이터 없음 또는 오류"
fi

echo ""
echo "=== 2. 백엔드 로그 확인 ==="
docker logs --tail 50 uvis-backend 2>&1 | grep -E "financial|dashboard|ERROR|Exception" | tail -20

echo ""
echo "=== 3. 프론트엔드 파일 확인 ==="
echo "FinancialDashboardPage 파일 존재 여부:"
ls -lh frontend/src/pages/FinancialDashboardPage.tsx 2>&1

echo ""
echo "=== 4. Recharts 패키지 확인 ==="
cd frontend 2>/dev/null && grep -E '"recharts"' package.json || echo "❌ recharts not found in package.json"

echo ""
echo "=== 5. 빌드 파일 확인 ==="
echo "최신 빌드 파일:"
ls -lht frontend/dist/assets/FinancialDashboard* 2>/dev/null | head -5

echo ""
echo "=== 6. 컨테이너 내 파일 확인 ==="
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/FinancialDashboard* 2>&1 | head -5

echo ""
echo "=== 7. 브라우저 콘솔 로그 확인 필요 ==="
echo "브라우저에서 F12 → Console 탭을 열고 다음을 확인하세요:"
echo "  - API 호출 성공 여부"
echo "  - JavaScript 오류 메시지"
echo "  - 데이터 로드 확인"
echo ""
echo "브라우저에서 F12 → Network 탭을 열고 다음을 확인하세요:"
echo "  - /api/v1/billing/enhanced/dashboard/financial 호출 상태"
echo "  - 응답 데이터 내용"
echo ""

echo "======================================"
echo "진단 완료"
echo "======================================"
