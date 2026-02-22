# AI 배차 최적화 - GPS 좌표 추출 방식 상세 설명

## ✅ 개선 완료: 실시간 차량 GPS 위치 사용

### 🎉 변경 사항

**Before (기존):**
- ❌ 차량의 **차고지(garage)** GPS만 사용
- ❌ 운행중인 차량의 실제 위치 미반영

**After (개선):**
- ✅ 차량의 **실시간 GPS 위치** 우선 사용
- ✅ 3단계 Fallback 메커니즘
- ✅ GPS 출처 로깅 추가

---

## 📍 GPS 좌표 추출 우선순위

### **Depot (차량 출발지) GPS 추출 로직**

```python
# backend/app/services/cvrptw_service.py

# 1순위: 실시간 GPS 위치 ⭐ NEW!
latest_location = db.query(VehicleLocation).filter(
    VehicleLocation.vehicle_id == vehicle.id
).order_by(VehicleLocation.recorded_at.desc()).first()

if latest_location:
    depot_lat = latest_location.latitude
    depot_lon = latest_location.longitude
    logger.info(f"📍 차량 {vehicle.code} 실시간 GPS 사용")
    
# 2순위: 차고지 좌표
elif vehicle.garage_latitude and vehicle.garage_longitude:
    depot_lat = vehicle.garage_latitude
    depot_lon = vehicle.garage_longitude
    logger.info(f"🏠 차량 {vehicle.code} 차고지 GPS 사용")
    
# 3순위: 기본 좌표 (서울)
else:
    depot_lat = 37.5665  # 서울시청
    depot_lon = 126.9780
    logger.warning(f"⚠️  차량 {vehicle.code} GPS 없음, 기본 좌표 사용")
```

---

## 🗺️ 전체 GPS 좌표 추출 구조

### 1️⃣ **차량 출발지 (Depot)**

| 우선순위 | 데이터 소스 | 테이블 | 필드 | 조건 |
|---------|-----------|--------|------|------|
| **1순위** | 실시간 GPS | `vehicle_locations` | `latitude`, `longitude` | 최근 기록 존재 시 ⭐ |
| **2순위** | 차고지 | `vehicles` | `garage_latitude`, `garage_longitude` | 차고지 등록 시 |
| **3순위** | 기본 좌표 | Hard-coded | `37.5665, 126.9780` | GPS 없음 |

**시나리오별 동작:**

```python
# 시나리오 A: 운행중인 차량 (최적)
vehicle_location = {
    "latitude": 37.5012,  # 실시간 GPS ✅
    "longitude": 127.0395,
    "recorded_at": "2026-02-19 14:30:00"
}
→ 📍 실시간 GPS 사용

# 시나리오 B: 차고지 대기 차량
vehicle.garage_latitude = 37.4567
vehicle.garage_longitude = 126.9876
→ 🏠 차고지 GPS 사용

# 시나리오 C: GPS 미등록 차량
vehicle.garage_latitude = None
→ ⚠️ 기본 좌표(서울시청) 사용
```

---

### 2️⃣ **상차지 GPS**

| 우선순위 | 데이터 소스 | 테이블 | 필드 | 조건 |
|---------|-----------|--------|------|------|
| **1순위** | 거래처 GPS | `clients` | `latitude`, `longitude` | 거래처 선택 시 |
| **2순위** | 주문 GPS | `orders` | `pickup_latitude`, `pickup_longitude` | 주소 직접 입력 시 |
| **3순위** | Depot GPS | (상기) | - | GPS 없음 (Fallback) |

**코드:**
```python
# 거래처로 입력된 경우
if order.pickup_client:
    latitude = pickup_client.latitude or depot_lat
    longitude = pickup_client.longitude or depot_lon

# 주소로 직접 입력된 경우
else:
    latitude = order.pickup_latitude or depot_lat
    longitude = order.pickup_longitude or depot_lon
```

---

### 3️⃣ **하차지 GPS**

| 우선순위 | 데이터 소스 | 테이블 | 필드 | 조건 |
|---------|-----------|--------|------|------|
| **1순위** | 거래처 GPS | `clients` | `latitude`, `longitude` | 거래처 선택 시 |
| **2순위** | 주문 GPS | `orders` | `delivery_latitude`, `delivery_longitude` | 주소 직접 입력 시 |
| **3순위** | Depot GPS | (상기) | - | GPS 없음 (Fallback) |

**코드:**
```python
# 거래처로 입력된 경우
if order.delivery_client:
    latitude = delivery_client.latitude or depot_lat
    longitude = delivery_client.longitude or depot_lon

# 주소로 직접 입력된 경우
else:
    latitude = order.delivery_latitude or depot_lat
    longitude = order.delivery_longitude or depot_lon
```

---

## 📊 실시간 GPS 데이터 (VehicleLocation)

### 테이블 구조
```sql
CREATE TABLE vehicle_locations (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL,      -- 차량 ID
    dispatch_id INTEGER,               -- 배차 ID
    
    -- GPS 정보
    latitude FLOAT NOT NULL,           -- 위도 ⭐
    longitude FLOAT NOT NULL,          -- 경도 ⭐
    accuracy FLOAT,                    -- GPS 정확도 (미터)
    altitude FLOAT,                    -- 고도 (미터)
    speed FLOAT,                       -- 속도 (km/h)
    heading FLOAT,                     -- 방향 (0-360도)
    
    -- 온도 정보
    temperature_celsius FLOAT,         -- 화물칸 온도
    humidity_percent FLOAT,            -- 습도 (%)
    
    -- 메타데이터
    recorded_at TIMESTAMP NOT NULL,    -- 기록 시각 ⭐
    is_ignition_on BOOLEAN,            -- 시동 상태
    battery_voltage FLOAT,             -- 배터리 전압
    fuel_level_percent FLOAT,          -- 연료 잔량
    odometer_km FLOAT,                 -- 주행거리
    
    -- UVIS 연동
    uvis_device_id VARCHAR(100),       -- UVIS 단말기 ID
    uvis_timestamp TIMESTAMP,          -- UVIS 타임스탬프
    
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    FOREIGN KEY (dispatch_id) REFERENCES dispatches(id)
);
```

### 데이터 수집 경로

```
1. UVIS 단말기 (차량에 설치)
   ↓
2. UVIS API Server
   ↓
3. Backend Webhook/Polling
   ↓
4. VehicleLocation Table 저장
   ↓
5. 배차 최적화 시 최신 GPS 조회 ⭐
```

---

## 🔍 최적화 프로세스 (업데이트)

```
1️⃣ 주문 수집
   - order_ids로 주문 조회
   ↓
2️⃣ 차량 수집
   - 사용 가능한 차량 조회
   - 온도대별 호환 차량 필터링
   ↓
3️⃣ GPS 좌표 추출 ⭐ 업데이트
   ┌─────────────────────────────────┐
   │ Depot (차량 출발지)               │
   │ 1. 실시간 GPS (VehicleLocation)  │ ← NEW!
   │ 2. 차고지 GPS (vehicles)         │
   │ 3. 기본 좌표 (Fallback)          │
   └─────────────────────────────────┘
   ┌─────────────────────────────────┐
   │ 상차지                            │
   │ 1. 거래처 GPS (clients)          │
   │ 2. 주문 GPS (orders)             │
   │ 3. Depot GPS (Fallback)          │
   └─────────────────────────────────┘
   ┌─────────────────────────────────┐
   │ 하차지                            │
   │ 1. 거래처 GPS (clients)          │
   │ 2. 주문 GPS (orders)             │
   │ 3. Depot GPS (Fallback)          │
   └─────────────────────────────────┘
   ↓
4️⃣ 거리 행렬 생성
   - [Haversine] or [Naver API]
   ↓
5️⃣ CVRPTW 알고리즘 실행
   - Google OR-Tools
   ↓
6️⃣ 최적 배차 계획 생성
```

---

## 🧪 테스트 방법

### 1. 실시간 GPS 데이터 확인
```sql
-- 차량별 최신 GPS 위치 조회
SELECT 
    v.code,
    v.plate_number,
    vl.latitude,
    vl.longitude,
    vl.recorded_at,
    vl.speed,
    v.garage_latitude,
    v.garage_longitude
FROM vehicles v
LEFT JOIN vehicle_locations vl ON vl.vehicle_id = v.id
WHERE vl.id = (
    SELECT id FROM vehicle_locations 
    WHERE vehicle_id = v.id 
    ORDER BY recorded_at DESC 
    LIMIT 1
)
ORDER BY v.code;
```

### 2. 배차 최적화 실행 후 로그 확인
```bash
# 백엔드 로그에서 GPS 출처 확인
docker logs uvis-backend --tail 100 | grep -E "(실시간 GPS|차고지 GPS|기본 좌표)"
```

**예상 로그:**
```
📍 차량 V001 실시간 GPS 사용: (37.501234, 127.039456)  ← 운행중
🏠 차량 V002 차고지 GPS 사용: (37.456789, 126.987654)  ← 대기중
⚠️  차량 V003 GPS 없음, 기본 좌표 사용                ← 미등록
```

### 3. API 테스트
```bash
curl -X POST 'http://localhost:8000/api/v1/dispatches/optimize-cvrptw' \
  -H 'Content-Type: application/json' \
  -d '{
    "order_ids": [27, 28, 30],
    "vehicle_ids": [],
    "dispatch_date": "2026-02-19"
  }' | jq .
```

---

## 📊 시나리오별 GPS 사용

### 시나리오 A: 운행중인 차량 ✅ 최적
```python
vehicle_id = 1
latest_gps = VehicleLocation.query.filter_by(vehicle_id=1).order_by(recorded_at.desc()).first()

# 결과
latitude = 37.5012     # 현재 위치 (강남역 인근)
longitude = 127.0395
recorded_at = "2026-02-19 14:30:00"

→ 📍 실시간 GPS 사용 (현재 위치에서 출발)
```

### 시나리오 B: 차고지 대기 차량 ✅ 양호
```python
vehicle_id = 2
latest_gps = None  # GPS 기록 없음 (차고지 대기)

# 차고지 좌표 사용
garage_latitude = 37.4567
garage_longitude = 126.9876

→ 🏠 차고지 GPS 사용 (차고지에서 출발)
```

### 시나리오 C: GPS 미등록 차량 ⚠️ Fallback
```python
vehicle_id = 3
latest_gps = None
garage_latitude = None
garage_longitude = None

# 기본 좌표 (서울시청)
default_lat = 37.5665
default_lon = 126.9780

→ ⚠️ 기본 좌표 사용 (정확도 낮음)
```

---

## 🎯 개선 효과

| 항목 | Before | After |
|-----|--------|-------|
| **차량 위치** | 차고지 고정 | 실시간 GPS ⭐ |
| **정확도** | 차고지 기준 | 현재 위치 기준 ✅ |
| **운행중 차량** | 부정확 | 정확 ✅ |
| **경로 최적화** | 차고지 → 상차지 | 현위치 → 상차지 ✅ |
| **거리 계산** | 부정확 | 정확 ✅ |

---

## 📝 Git 커밋

```bash
1223371 - feat: Use real-time vehicle GPS location for dispatch optimization
```

**변경 파일:**
- `backend/app/services/cvrptw_service.py`
  - Import `VehicleLocation` model
  - Query latest GPS location
  - Add 3-tier fallback logic
  - Add GPS source logging

**GitHub**: https://github.com/rpaakdi1-spec/3-/commit/1223371

---

## 🔍 결론

### ✅ GPS 좌표 추출 방식 (최종)

1. **차량 출발지 (Depot)**
   - 1순위: 실시간 GPS (`vehicle_locations`) ⭐ **NEW!**
   - 2순위: 차고지 GPS (`vehicles.garage_*`)
   - 3순위: 기본 좌표 (서울시청)

2. **상차지**
   - 1순위: 거래처 GPS (`clients`)
   - 2순위: 주문 GPS (`orders.pickup_*`)
   - 3순위: Depot GPS (Fallback)

3. **하차지**
   - 1순위: 거래처 GPS (`clients`)
   - 2순위: 주문 GPS (`orders.delivery_*`)
   - 3순위: Depot GPS (Fallback)

### 🎉 핵심 개선사항

- ✅ **운행중인 차량의 실제 위치**를 배차 최적화에 반영
- ✅ 3단계 Fallback으로 GPS 누락 상황 대응
- ✅ GPS 출처 로깅으로 디버깅 용이
- ✅ 더 정확한 경로 계산 및 배차 계획

---

**작성일**: 2026-02-19  
**버전**: 2.0 (실시간 GPS 추가)  
**작성자**: AI Assistant
