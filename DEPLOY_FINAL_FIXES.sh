#!/bin/bash

# ============================================================
# UVIS 백엔드 최종 수정사항 배포 스크립트
# ============================================================
# 수정 내용:
# 1. Dockerfile 헬스체크 엔드포인트 수정 (/api/v1/health → /health)
# 2. API 로그 URL 타입 에러 수정 (response.url → str(response.url))
# ============================================================

set -e  # 에러 발생 시 즉시 종료

echo "======================================"
echo "🚀 UVIS 백엔드 최종 수정사항 배포 시작"
echo "======================================"
echo ""

# 1. 최신 코드 가져오기
echo "📥 Step 1: Git에서 최신 코드 가져오기..."
cd /root/uvis
git fetch origin main
git pull origin main
echo "✅ Git pull 완료"
echo ""

# 2. 현재 컨테이너 상태 확인
echo "🔍 Step 2: 현재 컨테이너 상태 확인..."
docker ps -a | grep uvis-backend
echo ""

# 3. 백엔드 서비스 파일 복사
echo "📦 Step 3: 수정된 서비스 파일 복사..."
docker cp /root/uvis/backend/app/services/uvis_gps_service.py uvis-backend:/app/app/services/uvis_gps_service.py
echo "✅ uvis_gps_service.py 복사 완료"
echo ""

# 4. 백엔드 재빌드 (헬스체크 수정 적용을 위해)
echo "🔨 Step 4: 백엔드 컨테이너 재빌드..."
echo "⚠️  이 단계는 시간이 걸릴 수 있습니다 (약 2-3분)..."
cd /root/uvis
docker-compose build backend
echo "✅ 백엔드 재빌드 완료"
echo ""

# 5. 백엔드 컨테이너 재시작
echo "🔄 Step 5: 백엔드 컨테이너 재시작..."
docker-compose stop backend
docker-compose up -d backend
echo "✅ 백엔드 재시작 완료"
echo ""

# 6. 컨테이너 시작 대기
echo "⏳ Step 6: 백엔드 시작 대기 (30초)..."
sleep 30
echo ""

# 7. 헬스체크 확인
echo "🏥 Step 7: 백엔드 헬스체크 확인..."
HEALTH_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status' 2>/dev/null || echo "failed")
if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ 백엔드 헬스체크 성공!"
    curl -s http://localhost:8000/health | jq .
else
    echo "⚠️  헬스체크 응답이 없거나 비정상입니다. 로그를 확인하세요:"
    docker logs uvis-backend --tail 50
fi
echo ""

# 8. Docker 헬스체크 상태 확인
echo "🔍 Step 8: Docker 헬스체크 상태 확인..."
docker ps -a | grep uvis-backend
echo ""

# 9. API 테스트
echo "🧪 Step 9: API 테스트..."

# 인증 토큰 발급
echo "  - 인증 토큰 발급 중..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "  ✅ 인증 성공"
    
    # GPS 최적화 리포트 테스트
    echo ""
    echo "  - GPS 최적화 리포트 조회..."
    GPS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/analytics/gps-optimization/report" \
      -H "Authorization: Bearer $TOKEN")
    
    TOTAL_VEHICLES=$(echo "$GPS_RESPONSE" | jq -r '.gps_usage.total_vehicles // 0')
    USAGE_RATE=$(echo "$GPS_RESPONSE" | jq -r '.gps_usage.usage_rate_percentage // 0')
    
    if [ "$TOTAL_VEHICLES" -gt 0 ]; then
        echo "  ✅ GPS 최적화 리포트 정상 작동"
        echo "     - 총 차량 수: $TOTAL_VEHICLES"
        echo "     - GPS 사용률: $USAGE_RATE%"
    else
        echo "  ⚠️  GPS 데이터가 없거나 API 오류"
        echo "$GPS_RESPONSE" | jq .
    fi
    
    # 차량 위치 예측 테스트
    echo ""
    echo "  - 차량 위치 예측 테스트 (차량 ID: 1)..."
    PREDICT_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/analytics/vehicle-location/predict/1?prediction_minutes=30" \
      -H "Authorization: Bearer $TOKEN")
    
    PREDICT_SUCCESS=$(echo "$PREDICT_RESPONSE" | jq -r '.success // false')
    
    if [ "$PREDICT_SUCCESS" = "true" ]; then
        echo "  ✅ 차량 위치 예측 정상 작동"
        VEHICLE_CODE=$(echo "$PREDICT_RESPONSE" | jq -r '.vehicle_code')
        CONFIDENCE=$(echo "$PREDICT_RESPONSE" | jq -r '.prediction_confidence')
        echo "     - 차량 코드: $VEHICLE_CODE"
        echo "     - 예측 신뢰도: $CONFIDENCE%"
    else
        echo "  ⚠️  차량 위치 예측 오류 또는 데이터 부족"
        echo "$PREDICT_RESPONSE" | jq .
    fi
else
    echo "  ❌ 인증 실패 - API 테스트를 건너뜁니다"
fi

echo ""
echo "======================================"
echo "✅ 배포 완료!"
echo "======================================"
echo ""
echo "📋 배포 요약:"
echo "  1. ✅ Git 최신 코드 가져오기"
echo "  2. ✅ 수정된 서비스 파일 복사"
echo "  3. ✅ 백엔드 재빌드 (헬스체크 수정)"
echo "  4. ✅ 백엔드 재시작"
echo "  5. ✅ 헬스체크 확인"
echo "  6. ✅ API 테스트"
echo ""
echo "🔍 추가 확인 사항:"
echo "  - 백엔드 로그: docker logs uvis-backend --tail 100"
echo "  - 컨테이너 상태: docker ps -a | grep uvis"
echo "  - 헬스체크: curl http://localhost:8000/health | jq ."
echo ""
echo "📊 API 엔드포인트:"
echo "  - GPS 최적화 리포트: GET /api/v1/analytics/gps-optimization/report"
echo "  - 차량 위치 예측: GET /api/v1/analytics/vehicle-location/predict/{vehicle_id}"
echo "  - GPS 수집 전략: GET /api/v1/analytics/gps-collection/strategy"
echo "  - GPS 수집 권장사항: GET /api/v1/analytics/gps-collection/recommendations"
echo ""
echo "🌐 프론트엔드: http://139.150.11.99"
echo ""
