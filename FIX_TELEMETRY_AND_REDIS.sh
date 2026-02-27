#!/bin/bash
# ===================================================================
# Telemetry API 및 Redis 인증 수정 스크립트
# ===================================================================

set -e  # 에러 발생 시 중단

echo "====================================================================="
echo "Telemetry API 및 Redis 인증 수정 시작"
echo "====================================================================="
echo ""

# 현재 디렉토리로 이동
cd /root/uvis

# 1. 최신 코드 가져오기
echo "=== 1. 최신 코드 Pull ==="
git pull origin main
echo "✅ 코드 업데이트 완료"
echo ""

# 2. Redis 비밀번호 확인
echo "=== 2. Redis 비밀번호 확인 ==="
REDIS_PASSWORD=$(grep "REDIS_PASSWORD=" .env | cut -d'=' -f2)
echo "Redis 비밀번호: ${REDIS_PASSWORD}"
echo ""

# 3. Redis 연결 테스트
echo "=== 3. Redis 연결 테스트 ==="
docker-compose exec redis redis-cli -a "${REDIS_PASSWORD}" ping
if [ $? -eq 0 ]; then
    echo "✅ Redis 연결 성공"
else
    echo "❌ Redis 연결 실패 - 비밀번호를 확인해주세요"
    exit 1
fi
echo ""

# 4. 백엔드 재빌드 (모델 업데이트 반영)
echo "=== 4. 백엔드 컨테이너 재빌드 ==="
docker-compose stop backend
docker-compose rm -f backend
docker-compose build --no-cache backend
echo "✅ 백엔드 이미지 재빌드 완료"
echo ""

# 5. 백엔드 시작
echo "=== 5. 백엔드 컨테이너 시작 ==="
docker-compose up -d backend
echo "⏳ 백엔드 시작 대기 중 (30초)..."
sleep 30
echo ""

# 6. 백엔드 상태 확인
echo "=== 6. 백엔드 상태 확인 ==="
docker-compose ps backend
echo ""

# 7. 헬스 체크
echo "=== 7. 헬스 체크 ==="
curl -s http://localhost:8000/api/v1/health | jq .
echo ""

# 8. JWT 토큰 발급
echo "=== 8. JWT 토큰 발급 ==="
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ 토큰 발급 실패"
    exit 1
fi
echo "✅ 토큰 발급 성공 (길이: ${#TOKEN})"
echo "토큰: ${TOKEN:0:50}..."
echo ""

# 9. API 엔드포인트 테스트
echo "=== 9. API 엔드포인트 테스트 ==="

# Clients API
echo "📌 Clients API:"
curl -s -w "\n  HTTP Status: %{http_code}\n" \
    http://localhost:8000/api/v1/clients/ | head -10
echo ""

# Telemetry API
echo "📌 Telemetry API:"
curl -s -w "\n  HTTP Status: %{http_code}\n" \
    -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/telemetry/vehicles/status | head -10
echo ""

# AB Test API
echo "📌 AB Test API:"
curl -s -w "\n  HTTP Status: %{http_code}\n" \
    -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/ab-test/stats | head -10
echo ""

# ML Predictions API
echo "📌 ML Predictions API:"
curl -s -w "\n  HTTP Status: %{http_code}\n" \
    -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/ml/predictions | head -10
echo ""

# 10. 최근 백엔드 로그 확인
echo "=== 10. 최근 백엔드 로그 ==="
docker-compose logs backend --tail 30
echo ""

echo "====================================================================="
echo "✅ Telemetry API 및 Redis 인증 수정 완료!"
echo "====================================================================="
echo ""
echo "🔍 추가 확인사항:"
echo "1. 모든 API가 200 또는 401 (인증 필요)를 반환해야 합니다"
echo "2. 500 에러가 있다면 위의 로그를 확인해주세요"
echo "3. Redis 연결 에러가 있다면 REDIS_PASSWORD를 다시 확인해주세요"
echo ""
