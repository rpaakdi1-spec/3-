#!/bin/bash

###############################################################################
# UVIS GPS 데이터를 VehicleLocation으로 변환
# Convert UVIS GPS data to VehicleLocation table
#
# 목적: vehicle_gps_logs 테이블의 UVIS GPS 데이터를 
#       vehicle_locations 테이블로 변환하여 배차 최적화에 사용
#
# 작성: 2026-02-20
###############################################################################

set -e

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================"
echo "🔄 UVIS GPS 데이터 변환 스크립트"
echo "============================================"
echo ""

# 1. UVIS GPS 데이터 확인
echo -e "${BLUE}[INFO]${NC} 1. UVIS GPS 로그 확인 중..."
UVIS_GPS_COUNT=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM vehicle_gps_logs;" | tr -d '[:space:]')

echo "   UVIS GPS 로그: $UVIS_GPS_COUNT 건"

if [ "$UVIS_GPS_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} UVIS GPS 데이터가 없습니다."
    echo "   먼저 UVIS GPS 동기화를 실행하세요:"
    echo "   curl -X POST \"http://localhost:8000/api/v1/uvis-gps/sync/all\""
    exit 0
fi

# 2. 기존 VehicleLocation 데이터 확인
echo -e "${BLUE}[INFO]${NC} 2. 기존 VehicleLocation 데이터 확인..."
EXISTING_COUNT=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM vehicle_locations;" | tr -d '[:space:]')

echo "   기존 VehicleLocation: $EXISTING_COUNT 건"

# 3. UVIS GPS → VehicleLocation 변환
echo -e "${BLUE}[INFO]${NC} 3. UVIS GPS 데이터 변환 중..."
echo "   변환 규칙:"
echo "   - speed_kmh → speed"
echo "   - bi_date + bi_time → recorded_at"
echo "   - 중복 방지 (같은 차량, 같은 시간)"
echo ""

docker exec uvis-db psql -U uvis_user -d uvis_db << 'EOF'
-- UVIS GPS 데이터를 VehicleLocation으로 변환
INSERT INTO vehicle_locations (
    vehicle_id,
    latitude,
    longitude,
    recorded_at,
    speed,
    heading,
    accuracy,
    uvis_device_id,
    uvis_timestamp,
    is_ignition_on,
    created_at,
    updated_at
)
SELECT 
    vgl.vehicle_id,
    vgl.latitude,
    vgl.longitude,
    -- bi_date(YYYYMMDD) + bi_time(HHMMSS) → timestamp
    TO_TIMESTAMP(vgl.bi_date || ' ' || vgl.bi_time, 'YYYYMMDD HH24MISS') as recorded_at,
    vgl.speed_kmh as speed,
    0 as heading,  -- UVIS에서 heading 정보 없음
    10.0 as accuracy,  -- 기본 정확도 10m
    vgl.tid_id as uvis_device_id,
    TO_TIMESTAMP(vgl.bi_date || ' ' || vgl.bi_time, 'YYYYMMDD HH24MISS') as uvis_timestamp,
    vgl.is_engine_on as is_ignition_on,
    NOW(),
    NOW()
FROM vehicle_gps_logs vgl
WHERE vgl.vehicle_id IS NOT NULL
  AND vgl.latitude IS NOT NULL
  AND vgl.longitude IS NOT NULL
  AND vgl.bi_date IS NOT NULL
  AND vgl.bi_time IS NOT NULL
  AND LENGTH(vgl.bi_date) = 8
  AND LENGTH(vgl.bi_time) = 6
  AND NOT EXISTS (
    -- 중복 방지: 같은 차량, 같은 recorded_at
    SELECT 1 FROM vehicle_locations vl
    WHERE vl.vehicle_id = vgl.vehicle_id
    AND vl.recorded_at = TO_TIMESTAMP(vgl.bi_date || ' ' || vgl.bi_time, 'YYYYMMDD HH24MISS')
  )
ORDER BY vgl.created_at DESC;

-- 변환 결과 통계
SELECT 
    '총 변환 완료' as metric,
    COUNT(*)::text as value
FROM vehicle_locations
UNION ALL
SELECT 
    '최근 24시간 데이터' as metric,
    COUNT(*)::text as value
FROM vehicle_locations
WHERE recorded_at >= NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 
    '활성 차량' as metric,
    COUNT(DISTINCT vehicle_id)::text as value
FROM vehicle_locations
WHERE recorded_at >= NOW() - INTERVAL '24 hours';
EOF

echo -e "${GREEN}[SUCCESS]${NC} UVIS GPS 데이터 변환 완료"

# 4. 변환 후 확인
echo ""
echo -e "${BLUE}[INFO]${NC} 4. 변환 결과 확인..."
docker exec uvis-db psql -U uvis_user -d uvis_db << 'EOF'
-- 차량별 GPS 포인트 확인
SELECT 
    v.code as vehicle_code,
    COUNT(vl.id) as gps_points,
    TO_CHAR(MAX(vl.recorded_at), 'YYYY-MM-DD HH24:MI') as latest_gps,
    ROUND(AVG(vl.speed), 2) as avg_speed_kmh
FROM vehicles v
JOIN vehicle_locations vl ON v.id = vl.vehicle_id
WHERE v.is_active = true
  AND vl.recorded_at >= NOW() - INTERVAL '24 hours'
GROUP BY v.id, v.code
ORDER BY gps_points DESC
LIMIT 10;
EOF

# 5. 백엔드 재시작 (캐시 갱신)
echo ""
echo -e "${BLUE}[INFO]${NC} 5. 백엔드 컨테이너 재시작 중..."
docker restart uvis-backend > /dev/null
echo -e "${BLUE}[INFO]${NC}    백엔드 시작 대기 중 (30초)..."
sleep 30
echo -e "${GREEN}[SUCCESS]${NC} 백엔드 재시작 완료"

# 6. API 테스트
echo ""
echo -e "${BLUE}[INFO]${NC} 6. GPS 분석 API 테스트..."

# 토큰 발급
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo -e "${YELLOW}[WARNING]${NC} 토큰 발급 실패, API 테스트 스킵"
else
    echo -e "${GREEN}[SUCCESS]${NC} 토큰 발급 완료"
    
    # GPS 최적화 리포트
    echo ""
    echo -e "${BLUE}[INFO]${NC}    GPS 최적화 리포트 호출..."
    REPORT=$(curl -s -X GET "http://localhost:8000/api/v1/analytics/gps-optimization/report" \
      -H "Authorization: Bearer $TOKEN")
    
    GPS_POINTS=$(echo "$REPORT" | jq -r '.gps_usage.total_gps_points // 0')
    USAGE_RATE=$(echo "$REPORT" | jq -r '.gps_usage.usage_rate_percentage // 0')
    
    echo "   📊 GPS 사용률: ${USAGE_RATE}%"
    echo "   📍 총 GPS 포인트: ${GPS_POINTS}개"
    
    if [ "$GPS_POINTS" -gt 0 ]; then
        echo -e "${GREEN}[SUCCESS]${NC} GPS 데이터 정상 수집 확인"
    fi
fi

echo ""
echo "============================================"
echo "✅ UVIS GPS 데이터 변환 완료!"
echo "============================================"
echo ""
echo "📊 다음 단계:"
echo "1. 프론트엔드 AI 배차 최적화에서 실시간 GPS 활용"
echo "2. GPS 수집 주기 최적화 (차량 상태별)"
echo "3. 차량 위치 예측 API 활용"
echo ""
