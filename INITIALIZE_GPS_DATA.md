# GPS 데이터 초기화 및 수집 가이드

## 📋 현재 상태
- **GPS 데이터**: 0건 (수집되지 않음)
- **차량 수**: 46대
- **UVIS GPS 장치 연동**: 필요

---

## 🔧 해결 방법

### **방법 1: UVIS GPS API를 통한 실시간 데이터 동기화** ⭐

UVIS GPS 장치가 실제 연동되어 있다면, 아래 API를 호출하여 데이터를 수집할 수 있습니다.

#### 1️⃣ **인증키 발급**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# UVIS 인증키 발급
curl -X POST "http://localhost:8000/api/v1/uvis-gps/access-key/issue" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

#### 2️⃣ **GPS + 온도 데이터 동기화**
```bash
# 전체 데이터 동기화
curl -X POST "http://localhost:8000/api/v1/uvis-gps/sync/all?force_new_key=true" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

#### 3️⃣ **GPS 데이터만 동기화**
```bash
curl -X POST "http://localhost:8000/api/v1/uvis-gps/sync/gps" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_new_key": false}' | jq .
```

#### 4️⃣ **수집된 데이터 확인**
```bash
# 데이터베이스 확인
docker exec -it uvis-db psql -U uvis_user -d uvis_db -c \
  "SELECT v.code, vl.latitude, vl.longitude, vl.recorded_at 
   FROM vehicles v 
   LEFT JOIN vehicle_locations vl ON v.id = vl.vehicle_id 
   WHERE vl.recorded_at >= NOW() - INTERVAL '24 hours' 
   ORDER BY vl.recorded_at DESC 
   LIMIT 10;"

# GPS 로그 확인
curl -X GET "http://localhost:8000/api/v1/uvis-gps/gps-logs?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

### **방법 2: 스케줄러를 통한 자동 수집** 🔄

현재 `scheduler_service.py`가 5분마다 온도 데이터를 수집하고 있습니다.  
GPS 데이터도 같은 방식으로 자동 수집하도록 설정할 수 있습니다.

#### 스케줄러 상태 확인
```bash
# 백엔드 로그 확인
docker logs uvis-backend --tail 100 | grep -E "scheduler|GPS|temperature"
```

#### 예상 로그
```
✅ Scheduler job 'recurring_order_generation' scheduled (daily at 06:00)
✅ Scheduler job 'temperature_data_collection' scheduled (every 5 minutes)
🔄 Starting temperature data collection...
✅ Collected 41 temperature records
```

---

### **방법 3: 테스트 GPS 데이터 생성** 🧪

실제 UVIS 장치가 연동되지 않은 경우, 테스트용 GPS 데이터를 직접 생성할 수 있습니다.

#### 테스트 데이터 생성 SQL
```sql
-- 광주/전남 지역의 실제 좌표 범위
-- 위도: 34.8~35.3 (전남), 35.1~35.2 (광주)
-- 경도: 126.7~127.2

-- 차량별 랜덤 GPS 데이터 생성 (최근 24시간)
INSERT INTO vehicle_locations (
    vehicle_id, 
    latitude, 
    longitude, 
    recorded_at,
    speed_kmh,
    heading,
    altitude,
    accuracy,
    created_at,
    updated_at
)
SELECT 
    v.id,
    -- 광주/전남 지역 랜덤 좌표
    35.0 + (RANDOM() * 0.3)::numeric(10,6) as latitude,
    126.8 + (RANDOM() * 0.4)::numeric(10,6) as longitude,
    -- 최근 24시간 내 랜덤 시간
    NOW() - (RANDOM() * INTERVAL '24 hours') as recorded_at,
    -- 랜덤 속도 (0~80 km/h)
    (RANDOM() * 80)::numeric(5,2) as speed_kmh,
    -- 랜덤 방향 (0~360도)
    (RANDOM() * 360)::numeric(5,2) as heading,
    -- 고도 (50~200m)
    (50 + RANDOM() * 150)::numeric(7,2) as altitude,
    -- GPS 정확도 (5~20m)
    (5 + RANDOM() * 15)::numeric(5,2) as accuracy,
    NOW(),
    NOW()
FROM vehicles v
WHERE v.is_active = true
LIMIT 46;

-- 차량별 추가 GPS 포인트 생성 (경로 시뮬레이션)
INSERT INTO vehicle_locations (
    vehicle_id, 
    latitude, 
    longitude, 
    recorded_at,
    speed_kmh,
    heading,
    created_at,
    updated_at
)
SELECT 
    v.id,
    35.0 + (RANDOM() * 0.3)::numeric(10,6),
    126.8 + (RANDOM() * 0.4)::numeric(10,6),
    NOW() - (RANDOM() * INTERVAL '12 hours'),
    (RANDOM() * 70)::numeric(5,2),
    (RANDOM() * 360)::numeric(5,2),
    NOW(),
    NOW()
FROM vehicles v, generate_series(1, 5)  -- 차량당 5개 포인트
WHERE v.is_active = true;
```

#### 데이터베이스에서 직접 생성
```bash
# 서버에서 실행
docker exec -it uvis-db psql -U uvis_user -d uvis_db << 'EOF'
INSERT INTO vehicle_locations (
    vehicle_id, latitude, longitude, recorded_at,
    speed_kmh, heading, altitude, accuracy,
    created_at, updated_at
)
SELECT 
    v.id,
    35.0 + (RANDOM() * 0.3)::numeric(10,6),
    126.8 + (RANDOM() * 0.4)::numeric(10,6),
    NOW() - (RANDOM() * INTERVAL '24 hours'),
    (RANDOM() * 80)::numeric(5,2),
    (RANDOM() * 360)::numeric(5,2),
    (50 + RANDOM() * 150)::numeric(7,2),
    (5 + RANDOM() * 15)::numeric(5,2),
    NOW(),
    NOW()
FROM vehicles v
WHERE v.is_active = true;

-- 추가 포인트 생성
INSERT INTO vehicle_locations (
    vehicle_id, latitude, longitude, recorded_at,
    speed_kmh, heading, created_at, updated_at
)
SELECT 
    v.id,
    35.0 + (RANDOM() * 0.3)::numeric(10,6),
    126.8 + (RANDOM() * 0.4)::numeric(10,6),
    NOW() - (RANDOM() * INTERVAL '12 hours'),
    (RANDOM() * 70)::numeric(5,2),
    (RANDOM() * 360)::numeric(5,2),
    NOW(),
    NOW()
FROM vehicles v, generate_series(1, 5)
WHERE v.is_active = true;

SELECT COUNT(*) as total_gps_points FROM vehicle_locations;
EOF
```

---

## ✅ 데이터 생성 후 확인

### 1️⃣ **데이터베이스 확인**
```bash
docker exec -it uvis-db psql -U uvis_user -d uvis_db -c \
  "SELECT 
     v.code as vehicle_code,
     COUNT(vl.id) as gps_points,
     MAX(vl.recorded_at) as latest_gps,
     AVG(vl.speed_kmh)::numeric(5,2) as avg_speed
   FROM vehicles v
   LEFT JOIN vehicle_locations vl ON v.id = vl.vehicle_id
   WHERE v.is_active = true
   GROUP BY v.id, v.code
   ORDER BY gps_points DESC
   LIMIT 10;"
```

### 2️⃣ **API 재테스트**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# GPS 최적화 리포트
curl -X GET "http://localhost:8000/api/v1/analytics/gps-optimization/report" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 차량 위치 예측 (차량 1, 30분 후)
curl -X GET "http://localhost:8000/api/v1/analytics/vehicle-location/predict/1?prediction_minutes=30" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

### 3️⃣ **예상 결과**
```json
{
  "success": true,
  "vehicle_id": 1,
  "vehicle_code": "V전남87바1310",
  "current_location": {
    "latitude": 35.1234,
    "longitude": 126.9876,
    "recorded_at": "2026-02-19T16:30:00"
  },
  "predicted_location": {
    "latitude": 35.1456,
    "longitude": 127.0012,
    "method": "history_based",
    "confidence": 65.5
  },
  "prediction_minutes": 30
}
```

---

## 🔄 자동 수집 스케줄러 설정

### GPS 자동 수집 주기 설정
`backend/app/services/scheduler_service.py`에 GPS 수집 작업 추가:

```python
# 차량 상태별 GPS 수집
# - 운행중: 3분
# - 대기중: 10분
# - 정비중: 60분

self.scheduler.add_job(
    self._collect_vehicle_gps_data,
    IntervalTrigger(minutes=5),  # 평균 5분 주기
    id="gps_data_collection",
    name="Vehicle GPS Data Collection",
    replace_existing=True
)
```

---

## 📊 GPS 데이터 품질 모니터링

### 실시간 품질 확인
```bash
# 최근 1시간 GPS 데이터 품질
docker exec -it uvis-db psql -U uvis_user -d uvis_db -c \
  "SELECT 
     COUNT(*) as total_points,
     AVG(accuracy) as avg_accuracy_meters,
     MIN(recorded_at) as oldest,
     MAX(recorded_at) as newest,
     COUNT(DISTINCT vehicle_id) as vehicles_reporting
   FROM vehicle_locations
   WHERE recorded_at >= NOW() - INTERVAL '1 hour';"
```

---

## 🎯 다음 단계

1. ✅ **UVIS GPS 장치 연동 확인** → 방법 1 시도
2. ✅ **테스트 데이터 생성** → 방법 3 실행
3. ✅ **API 재테스트** → 모든 엔드포인트 검증
4. ✅ **자동 수집 활성화** → 스케줄러 설정
5. ✅ **프론트엔드 대시보드** → 실시간 GPS 지도 구축

---

## 🔗 관련 문서
- `GPS_ADVANCED_FEATURES_GUIDE.md` - GPS 고급 기능 가이드
- `GPS_REALTIME_LOCATION_IMPROVEMENT.md` - 실시간 GPS 개선
- `DEPLOY_GPS_REALTIME_LOCATION.sh` - 배포 스크립트
