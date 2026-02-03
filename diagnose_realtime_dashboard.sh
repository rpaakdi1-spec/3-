#!/bin/bash
set -e

echo "🔍 실시간 모니터링 대시보드 GPS 데이터 진단"
echo "============================================="
echo ""

# 1. Backend Health Check
echo "1️⃣  Backend Health Check..."
HEALTH=$(curl -s http://localhost:8000/health || echo "FAILED")
if [[ "$HEALTH" == *"healthy"* ]] || [[ "$HEALTH" == *"ok"* ]]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi
echo ""

# 2. 차량 목록 확인
echo "2️⃣  차량 목록 확인..."
TOTAL_VEHICLES=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM vehicles WHERE is_active = true;" 2>/dev/null | tr -d ' ')
echo "   활성 차량: ${TOTAL_VEHICLES}대"

if [ "$TOTAL_VEHICLES" -gt 0 ]; then
    echo "   차량 목록 (최대 5대):"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT id, code, plate_number, uvis_device_id FROM vehicles WHERE is_active = true LIMIT 5;"
fi
echo ""

# 3. GPS 로그 확인
echo "3️⃣  GPS 로그 확인..."
TOTAL_GPS=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM vehicle_gps_logs;" 2>/dev/null | tr -d ' ')
echo "   전체 GPS 로그: ${TOTAL_GPS}건"

if [ "$TOTAL_GPS" -gt 0 ]; then
    echo "   최근 GPS 로그 (최대 5건):"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT vehicle_id, latitude, longitude, speed_kmh, is_engine_on, bi_date, bi_time, created_at 
       FROM vehicle_gps_logs 
       ORDER BY created_at DESC LIMIT 5;"
else
    echo "   ⚠️  GPS 로그가 없습니다!"
fi
echo ""

# 4. 온도 로그 확인
echo "4️⃣  온도 로그 확인..."
TOTAL_TEMP=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM vehicle_temperature_logs;" 2>/dev/null | tr -d ' ')
echo "   전체 온도 로그: ${TOTAL_TEMP}건"

if [ "$TOTAL_TEMP" -gt 0 ]; then
    echo "   최근 온도 로그 (최대 5건):"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT vehicle_id, temperature_a, temperature_b, tpl_date, tpl_time, created_at 
       FROM vehicle_temperature_logs 
       ORDER BY created_at DESC LIMIT 5;"
else
    echo "   ⚠️  온도 로그가 없습니다!"
fi
echo ""

# 5. 차량별 최신 GPS 데이터
echo "5️⃣  차량별 최신 GPS 데이터..."
if [ "$TOTAL_GPS" -gt 0 ]; then
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT DISTINCT ON (v.id)
         v.id, v.plate_number,
         g.latitude, g.longitude, g.speed_kmh, g.is_engine_on,
         g.bi_date || ' ' || g.bi_time as gps_time,
         g.created_at
       FROM vehicles v
       LEFT JOIN vehicle_gps_logs g ON v.id = g.vehicle_id
       WHERE v.is_active = true
       ORDER BY v.id, g.created_at DESC
       LIMIT 10;"
else
    echo "   GPS 데이터 없음"
fi
echo ""

# 6. API 엔드포인트 테스트
echo "6️⃣  실시간 차량 상태 API 테스트..."
echo "   GET /api/v1/uvis-gps/realtime/vehicles"

API_RESPONSE=$(curl -s http://localhost:8000/api/v1/uvis-gps/realtime/vehicles 2>&1)
API_STATUS=$?

if [ $API_STATUS -eq 0 ]; then
    echo "   ✅ API 호출 성공"
    
    # Parse JSON response
    VEHICLE_COUNT=$(echo "$API_RESPONSE" | jq -r '.total // 0' 2>/dev/null || echo "0")
    echo "   응답 차량 수: ${VEHICLE_COUNT}대"
    
    if [ "$VEHICLE_COUNT" -gt 0 ]; then
        echo ""
        echo "   첫 번째 차량 데이터:"
        echo "$API_RESPONSE" | jq -r '.items[0] // empty' 2>/dev/null | head -20
    else
        echo "   ⚠️  응답에 차량 데이터가 없습니다"
        echo ""
        echo "   전체 응답:"
        echo "$API_RESPONSE" | head -20
    fi
else
    echo "   ❌ API 호출 실패"
    echo "   에러: $API_RESPONSE"
fi
echo ""

# 7. UVIS Device ID 매칭 확인
echo "7️⃣  UVIS Device ID 매칭 확인..."
VEHICLES_WITH_DEVICE=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
  "SELECT COUNT(*) FROM vehicles WHERE is_active = true AND uvis_device_id IS NOT NULL AND uvis_device_id != '';" 2>/dev/null | tr -d ' ')
echo "   Device ID가 설정된 차량: ${VEHICLES_WITH_DEVICE}/${TOTAL_VEHICLES}대"

if [ "$VEHICLES_WITH_DEVICE" -lt "$TOTAL_VEHICLES" ]; then
    echo "   ⚠️  일부 차량에 Device ID가 없습니다:"
    docker exec uvis-db psql -U uvis_user -d uvis_db -c \
      "SELECT id, code, plate_number, uvis_device_id 
       FROM vehicles 
       WHERE is_active = true AND (uvis_device_id IS NULL OR uvis_device_id = '') 
       LIMIT 5;"
fi
echo ""

# 8. GPS 동기화 상태 확인
echo "8️⃣  GPS 동기화 상태..."
if [ "$TOTAL_GPS" -gt 0 ]; then
    LATEST_GPS_TIME=$(docker exec uvis-db psql -U uvis_user -d uvis_db -t -c \
      "SELECT MAX(created_at) FROM vehicle_gps_logs;" 2>/dev/null | tr -d ' ')
    echo "   최근 GPS 수신 시각: $LATEST_GPS_TIME (UTC)"
    
    # Calculate time difference
    CURRENT_TIME=$(date -u +%s)
    LATEST_GPS_EPOCH=$(date -d "$LATEST_GPS_TIME" +%s 2>/dev/null || echo "0")
    
    if [ "$LATEST_GPS_EPOCH" != "0" ]; then
        TIME_DIFF=$((CURRENT_TIME - LATEST_GPS_EPOCH))
        TIME_DIFF_MIN=$((TIME_DIFF / 60))
        
        echo "   경과 시간: ${TIME_DIFF_MIN}분 전"
        
        if [ "$TIME_DIFF_MIN" -gt 60 ]; then
            echo "   ⚠️  GPS 데이터가 1시간 이상 업데이트되지 않았습니다!"
            echo "      → GPS 동기화를 실행하세요: 대시보드에서 'GPS 동기화' 버튼 클릭"
        fi
    fi
else
    echo "   ⚠️  GPS 데이터가 전혀 없습니다!"
    echo "      → GPS 동기화를 실행하세요: 대시보드에서 'GPS 동기화' 버튼 클릭"
fi
echo ""

# 9. 문제 진단 요약
echo "🔧 문제 진단 요약"
echo "================="

ISSUES=0

if [ "$TOTAL_VEHICLES" -eq 0 ]; then
    echo "   ❌ 차량이 등록되지 않았습니다"
    echo "      → 차량 관리에서 차량을 먼저 등록하세요"
    ISSUES=$((ISSUES + 1))
fi

if [ "$VEHICLES_WITH_DEVICE" -lt "$TOTAL_VEHICLES" ]; then
    echo "   ⚠️  일부 차량에 UVIS Device ID가 없습니다"
    echo "      → 차량 관리에서 Device ID를 입력하세요"
    ISSUES=$((ISSUES + 1))
fi

if [ "$TOTAL_GPS" -eq 0 ]; then
    echo "   ❌ GPS 데이터가 없습니다"
    echo "      → 대시보드에서 'GPS 동기화' 버튼을 클릭하세요"
    echo "      → 또는 Backend에서 수동 동기화: curl -X POST http://localhost:8000/api/v1/uvis-gps/sync/gps"
    ISSUES=$((ISSUES + 1))
fi

if [ "$ISSUES" -eq 0 ]; then
    echo "   ✅ 데이터베이스에는 문제가 없습니다"
    echo "   ℹ️  Frontend에서 데이터가 표시되지 않는 경우:"
    echo "      1. 브라우저 캐시 삭제 (Ctrl+Shift+Delete)"
    echo "      2. 강제 새로고침 (Ctrl+Shift+R)"
    echo "      3. Frontend 재빌드: docker-compose -f docker-compose.prod.yml restart frontend"
fi

echo ""
echo "📊 데이터 요약"
echo "============="
echo "   차량: ${TOTAL_VEHICLES}대"
echo "   GPS 로그: ${TOTAL_GPS}건"
echo "   온도 로그: ${TOTAL_TEMP}건"
echo "   API 응답 차량: ${VEHICLE_COUNT}대"
echo ""
echo "✅ 진단 완료!"
