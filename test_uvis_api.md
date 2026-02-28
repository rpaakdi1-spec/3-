# UVIS 실시간 통계 문제 분석 (2026-02-28)

## 문제 상황
- 대시보드 "UVIS 실시간 통계" 섹션에서 모든 값이 0으로 표시됨
- 운행 중 차량: 0대 / 46대
- 총 주행 거리: 0.0 km
- 평균 속도: 0.0 km/h
- 최고 속도: 0.0 km/h
- UVIS 알림: 최근 24시간 이내 알림 없음

## 원인 분석

### 1. 프론트엔드 (UvisFleetStats.tsx)
- **API 호출**: `/api/v1/vehicles/analytics/fleet?start_date=${today}&end_date=${today}`
- **자동 새로고침**: 30초마다 갱신
- **정상 동작**: 코드 로직은 문제 없음

### 2. 백엔드 (vehicles.py + vehicle_analytics_service.py)
- **엔드포인트**: `GET /api/v1/vehicles/analytics/fleet`
- **서비스 메서드**: `VehicleAnalyticsService.get_fleet_statistics()`
- **동작 방식**:
  1. `uvis_device_id`가 있는 활성 차량 조회
  2. 각 차량의 GPS 로그에서 주행 거리/속도 계산
  3. 최근 1시간 이내 GPS 데이터가 있으면 활성 차량으로 판단

### 3. 데이터 확인 필요
다음 3가지를 확인해야 합니다:

#### A. 차량에 UVIS 디바이스 ID가 연동되어 있는가?
```sql
-- 확인 쿼리
SELECT 
    id,
    plate_number,
    uvis_device_id,
    is_active
FROM vehicles 
WHERE uvis_device_id IS NOT NULL 
AND is_active = true;
```

**예상 문제**: 차량 46대가 있지만, `uvis_device_id`가 `NULL`인 경우

#### B. GPS 로그 데이터가 있는가?
```sql
-- 확인 쿼리
SELECT 
    COUNT(*) as total_logs,
    COUNT(DISTINCT tid_id) as unique_devices,
    MAX(created_at) as latest_log,
    MIN(created_at) as oldest_log
FROM vehicle_gps_logs;
```

**예상 문제**: `vehicle_gps_logs` 테이블에 데이터가 없음

#### C. GPS 로그와 차량이 연동되어 있는가?
```sql
-- 확인 쿼리
SELECT 
    v.plate_number,
    v.uvis_device_id,
    COUNT(gps.id) as gps_log_count,
    MAX(gps.created_at) as latest_gps
FROM vehicles v
LEFT JOIN vehicle_gps_logs gps ON v.uvis_device_id = gps.tid_id
WHERE v.is_active = true
GROUP BY v.id, v.plate_number, v.uvis_device_id
ORDER BY gps_log_count DESC;
```

**예상 문제**: `uvis_device_id`와 `tid_id`가 매칭되지 않음

---

## 해결 방안

### 시나리오 1: 차량에 UVIS 디바이스 ID가 없는 경우

**원인**: 차량 등록 시 `uvis_device_id`를 입력하지 않음

**해결**:
1. 차량 관리 페이지에서 각 차량에 UVIS 디바이스 ID 입력
2. 또는 일괄 업데이트 SQL:
```sql
-- 예시: 차량 번호 기반 디바이스 ID 매핑 (실제 매핑 규칙에 따라 수정)
UPDATE vehicles 
SET uvis_device_id = CONCAT('DEVICE_', id)
WHERE uvis_device_id IS NULL;
```

### 시나리오 2: GPS 로그 데이터가 없는 경우

**원인**: UVIS GPS 디바이스에서 데이터 수집이 안 됨

**해결**:
1. **UVIS GPS 디바이스 확인**: 디바이스가 켜져 있고 통신 중인지 확인
2. **GPS 수집 서비스 확인**: 백엔드 GPS 수집 서비스 동작 확인
3. **IoT 서버 연결 확인**: UVIS IoT 서버와 API 연결 상태 확인

**임시 테스트 데이터 생성** (개발/테스트용):
```python
# backend/scripts/generate_test_gps_data.py
from datetime import datetime, timedelta
from app.models.uvis_gps import VehicleGPSLog
from app.database import SessionLocal

db = SessionLocal()

# 차량 46대에 대해 최근 24시간 GPS 로그 생성
for vehicle_id in range(1, 47):
    device_id = f"DEVICE_{vehicle_id}"
    
    # 최근 24시간 동안 10분마다 GPS 로그 생성
    for i in range(144):  # 24시간 * 6 (10분마다)
        timestamp = datetime.utcnow() - timedelta(minutes=i*10)
        
        log = VehicleGPSLog(
            tid_id=device_id,
            latitude=37.5 + (vehicle_id * 0.01),  # 서울 근처
            longitude=127.0 + (vehicle_id * 0.01),
            speed_kmh=30 + (vehicle_id % 50),  # 30-80 km/h
            is_engine_on=i < 72,  # 최근 12시간만 엔진 on
            created_at=timestamp
        )
        db.add(log)
    
    db.commit()
    print(f"✅ {device_id} GPS 로그 생성 완료")

db.close()
```

### 시나리오 3: GPS 로그는 있지만 차량과 매칭이 안 되는 경우

**원인**: `vehicles.uvis_device_id`와 `vehicle_gps_logs.tid_id` 불일치

**해결**:
```sql
-- 실제 GPS 로그의 디바이스 ID 확인
SELECT DISTINCT tid_id 
FROM vehicle_gps_logs 
ORDER BY tid_id;

-- 차량의 디바이스 ID 확인
SELECT id, plate_number, uvis_device_id 
FROM vehicles 
WHERE uvis_device_id IS NOT NULL;

-- 불일치하면 차량의 uvis_device_id 업데이트
UPDATE vehicles 
SET uvis_device_id = '실제_GPS_로그의_tid_id'
WHERE id = 차량_id;
```

---

## 즉시 확인 가능한 방법

### 서버에서 API 직접 테스트
```bash
# 1. Fleet 통계 API 호출
curl http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-28&end_date=2026-02-28

# 2. 최근 알림 API 호출
curl http://localhost:8000/api/v1/vehicles/alerts/recent?limit=10

# 3. 차량 목록 API 호출 (UVIS 연동 확인)
curl http://localhost:8000/api/v1/vehicles/
```

### 데이터베이스 직접 확인
```bash
# PostgreSQL 접속
docker exec -it uvis-db psql -U coldchain_user -d coldchain_dispatch

# 쿼리 실행
SELECT COUNT(*) FROM vehicles WHERE uvis_device_id IS NOT NULL;
SELECT COUNT(*) FROM vehicle_gps_logs;
SELECT COUNT(*) FROM vehicle_temperature_logs;
```

---

## 권장 조치 순서

1. **즉시 확인** (5분)
   ```bash
   # 서버에서 실행
   curl http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-28&end_date=2026-02-28 | jq
   ```
   → 응답이 0인 이유 파악

2. **데이터 확인** (10분)
   ```bash
   docker exec -it uvis-db psql -U coldchain_user -d coldchain_dispatch -c "
   SELECT 
       (SELECT COUNT(*) FROM vehicles WHERE uvis_device_id IS NOT NULL) as vehicles_with_uvis,
       (SELECT COUNT(*) FROM vehicle_gps_logs) as gps_logs,
       (SELECT MAX(created_at) FROM vehicle_gps_logs) as latest_gps_log;
   "
   ```

3. **문제 해결**:
   - GPS 로그 없음 → UVIS 디바이스 확인 또는 테스트 데이터 생성
   - 차량에 UVIS ID 없음 → 차량 정보 업데이트
   - 매칭 문제 → 디바이스 ID 재매핑

---

## 예상 결과

### 정상 동작 시
```json
{
  "period": {
    "start_date": "2026-02-28",
    "end_date": "2026-02-28"
  },
  "total_vehicles": 46,
  "active_vehicles": 12,
  "total_distance_km": 1234.56,
  "avg_distance_per_vehicle_km": 26.84,
  "vehicle_stats": [
    {
      "vehicle_id": 1,
      "vehicle_plate": "12가3456",
      "total_distance_km": 45.2,
      "max_speed_kmh": 85.0,
      "avg_speed_kmh": 42.5,
      "engine_on_ratio": 75.0,
      "data_points": 144
    },
    // ...
  ]
}
```

### 현재 (문제 발생 시)
```json
{
  "period": {
    "start_date": "2026-02-28",
    "end_date": "2026-02-28"
  },
  "total_vehicles": 0,  // ← UVIS 연동 차량 없음
  "active_vehicles": 0,
  "total_distance_km": 0.0,
  "avg_distance_per_vehicle_km": 0.0,
  "vehicle_stats": []    // ← GPS 데이터 없음
}
```

---

## 요약

**문제**: GPS 데이터가 없거나 차량과 매칭이 안 됨  
**원인**: UVIS 디바이스 미연동 또는 GPS 로그 수집 안 됨  
**해결**: 데이터베이스 확인 → GPS 로그 또는 디바이스 ID 설정  
**다음**: 서버에서 위 쿼리 실행 후 결과 공유
