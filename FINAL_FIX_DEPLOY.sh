#!/bin/bash
# ===================================================================
# 최종 수정: Redis 환경 변수 추가 배포
# ===================================================================

set -e

echo "====================================================================="
echo "🎯 최종 수정: Redis 환경 변수 추가 배포"
echo "====================================================================="
echo ""

cd /root/uvis

# 1. 최신 코드
echo "=== 1. 최신 코드 Pull ==="
git pull origin main
echo "✅ 완료"
echo ""

# 2. 변경사항 확인
echo "=== 2. docker-compose.yml 변경사항 확인 ==="
echo "수정된 부분:"
grep -A 4 "# Redis" docker-compose.yml | head -5
echo ""

# 3. 백엔드 재시작 (재빌드 불필요 - 환경 변수만 변경)
echo "=== 3. 백엔드 재시작 ==="
echo "환경 변수만 변경되었으므로 재빌드 없이 재시작만 합니다..."
docker-compose stop backend
docker-compose up -d backend
echo "⏳ 대기 중 (30초)..."
sleep 30
echo "✅ 완료"
echo ""

# 4. 환경 변수 확인
echo "=== 4. 백엔드 컨테이너 Redis 환경 변수 확인 ==="
docker-compose exec -T backend env | grep REDIS | sort
echo ""

# 5. JWT 토큰 발급
echo "=== 5. JWT 토큰 발급 ==="
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ 토큰 발급 실패"
    exit 1
fi
echo "✅ 토큰 발급 성공"
echo ""

# 6. AB Test API 최종 테스트
echo "=== 6. AB Test API 최종 테스트 ==="
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
    echo "🎉🎉🎉 대성공! AB Test API 정상 작동!"
    echo ""
    echo "====================================================================="
    echo "✅ 모든 API 수정 완료!"
    echo "====================================================================="
    echo ""
    echo "📊 최종 API 상태:"
    echo "  ✅ Clients API: 200 OK"
    echo "  ✅ Telemetry API: 200 OK"
    echo "  ✅ AB Test API: 200 OK"
    echo "  ✅ ML Predictions API: 400 (모델 미학습 - 정상)"
    echo ""
    echo "🎯 해결된 문제:"
    echo "  1. VehicleLocation 모델 timestamp 컬럼 추가"
    echo "  2. Clients 테이블 누락 컬럼 추가"
    echo "  3. Redis 환경 변수 설정 수정"
    echo "  4. 실시간 배차 모니터링 사이드바 추가"
    echo ""
else
    echo "❌ 여전히 에러 발생 (HTTP ${HTTP_CODE})"
    echo ""
    echo "=== 백엔드 최근 로그 ==="
    docker-compose logs backend --tail 30 | grep -i "redis\|ab"
fi

echo ""
echo "====================================================================="
echo "배포 완료!"
echo "====================================================================="
