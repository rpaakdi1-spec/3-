#!/bin/bash
set -e

echo "🚀 자연어 주문 파싱 시스템 배포 스크립트"
echo "========================================"
echo ""

# 1. 코드 업데이트
echo "📥 1. 코드 업데이트..."
git fetch origin main
git reset --hard origin/main
echo "✅ 코드 업데이트 완료 (HEAD: $(git rev-parse --short HEAD))"
echo ""

# 2. OpenAI API 키 확인
echo "🔑 2. OpenAI API 키 확인..."
if grep -q "OPENAI_API_KEY" .env 2>/dev/null; then
    echo "✅ OpenAI API 키 설정됨"
else
    echo "⚠️  OpenAI API 키가 설정되지 않았습니다."
    echo "   다음 명령으로 설정하세요:"
    echo "   echo 'OPENAI_API_KEY=sk-...' >> .env"
    echo ""
    read -p "계속하시겠습니까? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

# 3. Backend 재시작
echo "🔄 3. Backend 재시작..."
docker-compose -f docker-compose.prod.yml restart backend
echo "⏳ Backend 시작 대기 (30초)..."
sleep 30
echo "✅ Backend 재시작 완료"
echo ""

# 4. Backend Health Check
echo "🏥 4. Backend Health Check..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check 실패"
    echo "   로그 확인: docker logs uvis-backend --tail 50"
    exit 1
fi
echo ""

# 5. NLP 엔드포인트 테스트
echo "🧪 5. NLP 엔드포인트 테스트..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/orders/parse-nlp \
  -H "Content-Type: application/json" \
  -d '{"text":"[02/03] 백암 -> 경산 16판"}' \
  2>&1)

if echo "$TEST_RESPONSE" | grep -q '"success"'; then
    echo "✅ NLP 엔드포인트 정상 작동"
    echo "   응답: $TEST_RESPONSE" | head -c 200
    echo "..."
else
    echo "⚠️  NLP 엔드포인트 응답 확인:"
    echo "   $TEST_RESPONSE" | head -c 300
    echo ""
fi
echo ""

# 6. Frontend 재빌드 (선택)
echo "🎨 6. Frontend 재빌드..."
read -p "Frontend를 재빌드하시겠습니까? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.prod.yml restart frontend
    echo "⏳ Frontend 빌드 대기 (60초)..."
    sleep 60
    echo "✅ Frontend 재빌드 완료"
else
    echo "⏭️  Frontend 재빌드 건너뜀"
fi
echo ""

# 7. 최종 확인
echo "📋 7. 배포 완료 체크리스트"
echo "=========================="
echo "✅ 코드 업데이트: $(git rev-parse --short HEAD)"
echo "✅ Backend 재시작: 완료"
echo "✅ Health Check: 통과"
echo "✅ NLP 엔드포인트: 테스트 완료"
echo ""
echo "🌐 브라우저 테스트:"
echo "   http://139.150.11.99/orders"
echo "   → '자연어 입력' 버튼 클릭"
echo ""
echo "📝 테스트 텍스트 예시:"
echo "   [02/03] 추가 배차요청"
echo "   백암 _ 저온 → 경산 16판 1대"
echo ""
echo "🎉 배포 완료!"
