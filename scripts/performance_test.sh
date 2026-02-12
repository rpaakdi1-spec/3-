#!/bin/bash
# 성능 테스트 스크립트

SERVER_URL="http://139.150.11.99"
API_BASE="/api/v1"

echo "=================================="
echo "🚀 성능 테스트 시작"
echo "=================================="
echo ""

# 로그인하여 토큰 획득
echo "1️⃣ 로그인 테스트..."
LOGIN_START=$(date +%s%N)
TOKEN=$(curl -s -X POST "${SERVER_URL}${API_BASE}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')
LOGIN_END=$(date +%s%N)
LOGIN_TIME=$(( (LOGIN_END - LOGIN_START) / 1000000 ))
echo "   ✅ 로그인 시간: ${LOGIN_TIME}ms"
echo ""

# Billing Enhanced API 테스트
echo "2️⃣ Billing Enhanced API 테스트..."
echo ""

# Financial Dashboard
echo "   📊 Financial Dashboard API"
FINANCIAL_START=$(date +%s%N)
curl -s -w "\n   - HTTP 상태: %{http_code}\n   - 응답 시간: %{time_total}s\n   - 다운로드 속도: %{speed_download} bytes/s\n" \
  -X GET "${SERVER_URL}${API_BASE}/billing/enhanced/dashboard/financial?start_date=2025-11-12&end_date=2026-02-12" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
FINANCIAL_END=$(date +%s%N)
FINANCIAL_TIME=$(( (FINANCIAL_END - FINANCIAL_START) / 1000000 ))
echo "   - 총 처리 시간: ${FINANCIAL_TIME}ms"
echo ""

# Monthly Trends
echo "   📈 Monthly Trends API"
TRENDS_START=$(date +%s%N)
curl -s -w "\n   - HTTP 상태: %{http_code}\n   - 응답 시간: %{time_total}s\n   - 다운로드 속도: %{speed_download} bytes/s\n" \
  -X GET "${SERVER_URL}${API_BASE}/billing/enhanced/dashboard/trends?months=12" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
TRENDS_END=$(date +%s%N)
TRENDS_TIME=$(( (TRENDS_END - TRENDS_START) / 1000000 ))
echo "   - 총 처리 시간: ${TRENDS_TIME}ms"
echo ""

# Top Clients
echo "   🏆 Top Clients API"
CLIENTS_START=$(date +%s%N)
curl -s -w "\n   - HTTP 상태: %{http_code}\n   - 응답 시간: %{time_total}s\n   - 다운로드 속도: %{speed_download} bytes/s\n" \
  -X GET "${SERVER_URL}${API_BASE}/billing/enhanced/dashboard/top-clients?limit=10&start_date=2025-11-12&end_date=2026-02-12" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
CLIENTS_END=$(date +%s%N)
CLIENTS_TIME=$(( (CLIENTS_END - CLIENTS_START) / 1000000 ))
echo "   - 총 처리 시간: ${CLIENTS_TIME}ms"
echo ""

# 동시 요청 테스트
echo "3️⃣ 동시 요청 테스트 (10개 요청)..."
CONCURRENT_START=$(date +%s%N)
for i in {1..10}; do
  curl -s -X GET "${SERVER_URL}${API_BASE}/billing/enhanced/dashboard/financial?start_date=2025-11-12&end_date=2026-02-12" \
    -H "Authorization: Bearer $TOKEN" > /dev/null &
done
wait
CONCURRENT_END=$(date +%s%N)
CONCURRENT_TIME=$(( (CONCURRENT_END - CONCURRENT_START) / 1000000 ))
echo "   ✅ 10개 동시 요청 처리 시간: ${CONCURRENT_TIME}ms"
echo "   ✅ 평균 처리 시간: $(( CONCURRENT_TIME / 10 ))ms"
echo ""

# 총 평균 계산
TOTAL_AVG=$(( (FINANCIAL_TIME + TRENDS_TIME + CLIENTS_TIME) / 3 ))

echo "=================================="
echo "📊 성능 테스트 결과 요약"
echo "=================================="
echo "로그인: ${LOGIN_TIME}ms"
echo "Financial Dashboard: ${FINANCIAL_TIME}ms"
echo "Monthly Trends: ${TRENDS_TIME}ms"
echo "Top Clients: ${CLIENTS_TIME}ms"
echo "동시 요청 (10개): ${CONCURRENT_TIME}ms"
echo ""
echo "평균 API 응답 시간: ${TOTAL_AVG}ms"
echo ""

# 성능 평가
if [ $TOTAL_AVG -lt 100 ]; then
  echo "🎉 평가: 매우 우수 (< 100ms)"
elif [ $TOTAL_AVG -lt 300 ]; then
  echo "✅ 평가: 우수 (< 300ms)"
elif [ $TOTAL_AVG -lt 1000 ]; then
  echo "⚠️  평가: 보통 (< 1s)"
else
  echo "❌ 평가: 개선 필요 (> 1s)"
fi

echo "=================================="
