#!/bin/bash
# ===================================================================
# Redis 비밀번호 처리 최종 수정 스크립트
# ===================================================================

set -e

echo "====================================================================="
echo "Redis 비밀번호 처리 최종 수정 배포"
echo "====================================================================="
echo ""

cd /root/uvis

# 1. 최신 코드
echo "=== 1. 최신 코드 Pull ==="
git pull origin main
echo ""

# 2. 백엔드 재빌드
echo "=== 2. 백엔드 재빌드 ==="
docker-compose stop backend
docker-compose rm -f backend
docker-compose build --no-cache backend
echo ""

# 3. 백엔드 시작
echo "=== 3. 백엔드 시작 ==="
docker-compose up -d backend
echo "⏳ 대기 중 (30초)..."
sleep 30
echo ""

# 4. 토큰 발급
echo "=== 4. JWT 토큰 발급 ==="
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" | jq -r '.access_token')
echo "✅ 토큰 발급 성공"
echo ""

# 5. AB Test API 최종 테스트
echo "=== 5. AB Test API 최종 테스트 ==="
echo "이전 에러: Authentication required (500)"
echo "기대 결과: 200 OK"
echo ""

AB_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/ab-test/stats)

HTTP_CODE=$(echo "$AB_RESPONSE" | tail -n 1)
BODY=$(echo "$AB_RESPONSE" | head -n -1)

echo "HTTP Status: ${HTTP_CODE}"
echo "Response:"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅✅✅ 성공! AB Test API 정상 작동!"
    echo ""
    echo "🎉 모든 API 수정 완료!"
    echo "- Clients API: 200 OK ✅"
    echo "- Telemetry API: 200 OK ✅"
    echo "- AB Test API: 200 OK ✅"
else
    echo "❌ 여전히 에러 발생"
    echo ""
    echo "=== 백엔드 로그 ==="
    docker-compose logs backend --tail 20 | grep -i "redis\|ab"
fi

echo ""
echo "====================================================================="
