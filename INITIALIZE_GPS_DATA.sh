#!/bin/bash

###############################################################################
# GPS 데이터 초기화 및 테스트 스크립트
# GPS Data Initialization and Testing Script
#
# 목적: UVIS GPS 장치가 연동되지 않은 경우 테스트용 GPS 데이터 생성
# Purpose: Generate test GPS data when UVIS GPS devices are not connected
#
# 작성: 2026-02-19
###############################################################################

set -e  # 에러 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "============================================"
echo "🚀 GPS 데이터 초기화 스크립트"
echo "============================================"
echo ""

# 1. 현재 GPS 데이터 상태 확인
log_info "1. 현재 GPS 데이터 상태 확인 중..."
CURRENT_COUNT=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM vehicle_locations;" | tr -d '[:space:]')

echo "   현재 GPS 데이터 포인트: $CURRENT_COUNT 개"

if [ "$CURRENT_COUNT" -gt 0 ]; then
    log_warning "이미 GPS 데이터가 존재합니다 ($CURRENT_COUNT 개)"
    read -p "   기존 데이터를 삭제하고 새로 생성하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "작업을 취소했습니다."
        exit 0
    fi
    
    log_info "기존 GPS 데이터 삭제 중..."
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "DELETE FROM vehicle_locations;" > /dev/null
    log_success "기존 데이터 삭제 완료"
fi

# 2. 활성 차량 수 확인
log_info "2. 활성 차량 수 확인 중..."
ACTIVE_VEHICLES=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM vehicles WHERE is_active = true;" | tr -d '[:space:]')

echo "   활성 차량: $ACTIVE_VEHICLES 대"

if [ "$ACTIVE_VEHICLES" -eq 0 ]; then
    log_error "활성 차량이 없습니다. 차량 데이터를 먼저 등록하세요."
    exit 1
fi

# 3. 테스트 GPS 데이터 생성
log_info "3. 테스트 GPS 데이터 생성 중..."
log_info "   - 광주/전남 지역 좌표 (위도: 35.0~35.3, 경도: 126.8~127.2)"
log_info "   - 최근 24시간 내 랜덤 시간"
log_info "   - 차량당 6개 GPS 포인트 생성"

docker exec uvis-db psql -U uvis_user -d uvis_db << 'EOF'
-- 첫 번째 GPS 포인트 (최근 데이터)
INSERT INTO vehicle_locations (
    vehicle_id, latitude, longitude, recorded_at,
    speed_kmh, heading, altitude, accuracy,
    created_at, updated_at
)
SELECT 
    v.id,
    35.0 + (RANDOM() * 0.3)::numeric(10,6) as latitude,
    126.8 + (RANDOM() * 0.4)::numeric(10,6) as longitude,
    NOW() - (RANDOM() * INTERVAL '2 hours') as recorded_at,
    (RANDOM() * 80)::numeric(5,2) as speed_kmh,
    (RANDOM() * 360)::numeric(5,2) as heading,
    (50 + RANDOM() * 150)::numeric(7,2) as altitude,
    (5 + RANDOM() * 15)::numeric(5,2) as accuracy,
    NOW(),
    NOW()
FROM vehicles v
WHERE v.is_active = true;

-- 추가 GPS 포인트 (경로 시뮬레이션)
INSERT INTO vehicle_locations (
    vehicle_id, latitude, longitude, recorded_at,
    speed_kmh, heading, altitude, accuracy,
    created_at, updated_at
)
SELECT 
    v.id,
    35.0 + (RANDOM() * 0.3)::numeric(10,6) as latitude,
    126.8 + (RANDOM() * 0.4)::numeric(10,6) as longitude,
    NOW() - ((2 + i) * INTERVAL '2 hours') as recorded_at,
    (RANDOM() * 70)::numeric(5,2) as speed_kmh,
    (RANDOM() * 360)::numeric(5,2) as heading,
    (50 + RANDOM() * 150)::numeric(7,2) as altitude,
    (5 + RANDOM() * 15)::numeric(5,2) as accuracy,
    NOW(),
    NOW()
FROM vehicles v
CROSS JOIN generate_series(1, 5) as i
WHERE v.is_active = true;

SELECT 
    '✅ GPS 데이터 생성 완료: ' || COUNT(*) || '개 포인트' as result
FROM vehicle_locations;
EOF

log_success "GPS 데이터 생성 완료"

# 4. 생성된 데이터 확인
log_info "4. 생성된 데이터 통계 확인..."
docker exec uvis-db psql -U uvis_user -d uvis_db << 'EOF'
SELECT 
    '총 GPS 포인트' as metric,
    COUNT(*)::text as value
FROM vehicle_locations
UNION ALL
SELECT 
    '활성 차량' as metric,
    COUNT(DISTINCT vehicle_id)::text as value
FROM vehicle_locations
UNION ALL
SELECT 
    '최신 GPS 시간' as metric,
    TO_CHAR(MAX(recorded_at), 'YYYY-MM-DD HH24:MI:SS') as value
FROM vehicle_locations
UNION ALL
SELECT 
    '가장 오래된 GPS 시간' as metric,
    TO_CHAR(MIN(recorded_at), 'YYYY-MM-DD HH24:MI:SS') as value
FROM vehicle_locations
UNION ALL
SELECT 
    '평균 속도' as metric,
    ROUND(AVG(speed_kmh), 2)::text || ' km/h' as value
FROM vehicle_locations
WHERE speed_kmh IS NOT NULL
UNION ALL
SELECT 
    '평균 정확도' as metric,
    ROUND(AVG(accuracy), 2)::text || ' m' as value
FROM vehicle_locations
WHERE accuracy IS NOT NULL;
EOF

# 5. 차량별 GPS 포인트 확인
log_info "5. 차량별 GPS 데이터 확인 (상위 10대)..."
docker exec uvis-db psql -U uvis_user -d uvis_db << 'EOF'
SELECT 
    v.code as vehicle_code,
    COUNT(vl.id) as gps_points,
    TO_CHAR(MAX(vl.recorded_at), 'YYYY-MM-DD HH24:MI') as latest_gps,
    ROUND(AVG(vl.speed_kmh), 2) as avg_speed_kmh
FROM vehicles v
LEFT JOIN vehicle_locations vl ON v.id = vl.vehicle_id
WHERE v.is_active = true
GROUP BY v.id, v.code
ORDER BY gps_points DESC
LIMIT 10;
EOF

# 6. Docker 컨테이너 재시작 (캐시 갱신)
log_info "6. 백엔드 컨테이너 재시작 중..."
docker restart uvis-backend > /dev/null
sleep 10
log_success "백엔드 재시작 완료"

# 7. 헬스체크
log_info "7. 헬스체크..."
HEALTH_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$HEALTH_STATUS" = "healthy" ]; then
    log_success "백엔드 정상 작동 중"
else
    log_error "백엔드 헬스체크 실패"
    exit 1
fi

# 8. API 테스트
log_info "8. GPS 분석 API 테스트 중..."

# 토큰 발급
log_info "   인증 토큰 발급..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    log_error "토큰 발급 실패"
    exit 1
fi
log_success "토큰 발급 완료"

# GPS 최적화 리포트 테스트
log_info "   GPS 최적화 리포트 호출..."
REPORT_RESULT=$(curl -s -X GET "http://localhost:8000/api/v1/analytics/gps-optimization/report" \
  -H "Authorization: Bearer $TOKEN")

GPS_POINTS=$(echo "$REPORT_RESULT" | jq -r '.gps_usage.total_gps_points // 0')
USAGE_RATE=$(echo "$REPORT_RESULT" | jq -r '.gps_usage.usage_rate_percentage // 0')

echo "   📊 GPS 사용률: ${USAGE_RATE}%"
echo "   📍 총 GPS 포인트: ${GPS_POINTS}개"

if [ "$GPS_POINTS" -gt 0 ]; then
    log_success "GPS 데이터 정상 수집 확인"
else
    log_warning "GPS 데이터가 아직 집계되지 않았습니다"
fi

# 차량 위치 예측 테스트
log_info "   차량 위치 예측 API 테스트 (차량 ID 1)..."
PREDICT_RESULT=$(curl -s -X GET "http://localhost:8000/api/v1/analytics/vehicle-location/predict/1?prediction_minutes=30" \
  -H "Authorization: Bearer $TOKEN")

PREDICT_SUCCESS=$(echo "$PREDICT_RESULT" | jq -r '.success // false')

if [ "$PREDICT_SUCCESS" = "true" ]; then
    VEHICLE_CODE=$(echo "$PREDICT_RESULT" | jq -r '.vehicle_code')
    METHOD=$(echo "$PREDICT_RESULT" | jq -r '.predicted_location.method')
    CONFIDENCE=$(echo "$PREDICT_RESULT" | jq -r '.prediction_confidence')
    
    echo "   🚗 차량: $VEHICLE_CODE"
    echo "   🎯 예측 방법: $METHOD"
    echo "   📈 신뢰도: ${CONFIDENCE}%"
    log_success "차량 위치 예측 API 정상 작동"
else
    log_warning "차량 위치 예측 실패 - 데이터가 더 필요할 수 있습니다"
fi

echo ""
echo "============================================"
echo "✅ GPS 데이터 초기화 완료!"
echo "============================================"
echo ""
echo "📋 다음 단계:"
echo "1. 프론트엔드에서 GPS 분석 대시보드 확인"
echo "2. 실시간 차량 위치 지도 확인"
echo "3. UVIS GPS 장치 연동 시 실제 데이터로 교체"
echo ""
echo "🔗 API 엔드포인트:"
echo "- GPS 최적화 리포트: GET /api/v1/analytics/gps-optimization/report"
echo "- GPS 수집 전략: GET /api/v1/analytics/gps-collection/strategy"
echo "- 차량 위치 예측: GET /api/v1/analytics/vehicle-location/predict/{id}"
echo ""
