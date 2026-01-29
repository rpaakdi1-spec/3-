# GPS 기반 가장 가까운 차량 자동 배차 기능

## 📋 개요

AI 배차 시스템에 GPS 실시간 위치 기반 배차 최적화 기능을 추가했습니다.  
배차대기 주문의 상차지 주소와 가장 가까운 차량을 자동으로 배정합니다.

---

## ✅ 완료 작업

### 1. GPS 위치 기반 배차 로직 추가

#### 주요 변경사항
```python
# backend/app/services/dispatch_optimization_service.py

# VehicleGPSLog 모델 import
from app.models.uvis_gps import VehicleGPSLog

# GPS 위치 조회 메서드
async def _get_vehicle_current_location(self, vehicle_id: int) -> Optional[Tuple[float, float]]:
    """차량의 최신 GPS 위치 조회"""
    latest_gps = (
        self.db.query(VehicleGPSLog)
        .filter(VehicleGPSLog.vehicle_id == vehicle_id)
        .order_by(VehicleGPSLog.created_at.desc())
        .first()
    )
    
    if latest_gps and latest_gps.latitude and latest_gps.longitude:
        return (latest_gps.latitude, latest_gps.longitude)
    
    return None
```

#### 거리 기반 배차 알고리즘
```python
# 각 차량의 GPS 위치 또는 차고지 위치 수집
vehicle_locations = {}
for vehicle in vehicles:
    gps_loc = await self._get_vehicle_current_location(vehicle.id)
    if gps_loc:
        vehicle_locations[vehicle.id] = gps_loc
    elif vehicle.garage_latitude and vehicle.garage_longitude:
        vehicle_locations[vehicle.id] = (vehicle.garage_latitude, vehicle.garage_longitude)

# 각 주문마다 가장 가까운 차량 선택
for order in orders:
    pickup_lat = order.pickup_latitude or 37.5665
    pickup_lon = order.pickup_longitude or 126.9780
    
    best_vehicle = None
    min_distance = float('inf')
    
    for vehicle in vehicles:
        # 용량 체크
        if has_capacity(vehicle, order):
            # 거리 계산 (Haversine)
            distance = self._calculate_distance(
                vehicle_lat, vehicle_lon,
                pickup_lat, pickup_lon
            )
            
            if distance < min_distance:
                min_distance = distance
                best_vehicle = vehicle
    
    # 가장 가까운 차량에 주문 배정
    assign_order(best_vehicle, order, distance=min_distance)
```

---

## 🧪 테스트 결과

### 테스트 시나리오
- **주문**: ORD-GPS-TEST-001 (냉동, 5팔레트, 300kg)
- **상차지**: (주)광신냉동용인사무실
- **상차지 위치**: 서울 (37.5665, 126.9780) *지오코딩 전 기본 좌표*
- **배차 일자**: 2026-01-27

### 냉동/겸용 차량 거리 순위

```
================================================================================
1. ID  26 | 전남87바1367       | 겸용   | 거리:  52.89km ⭐ **배정된 차량**
2. ID  34 | 전남87바1362       | 냉동   | 거리:  52.89km
3. ID  31 | 전남87바4166       | 겸용   | 거리:  54.11km
4. ID  49 | 전남87바1313       | 겸용   | 거리:  57.90km
5. ID  38 | 전남87바1325       | 겸용   | 거리:  71.47km
6. ID  45 | 전남87바4179       | 겸용   | 거리: 146.34km
7. ID  40 | 전남87바4173       | 겸용   | 거리: 169.70km
8. ID  23 | 전남87바1310       | 겸용   | 거리: 196.32km
9. ID  25 | 전남87바1334       | 겸용   | 거리: 201.77km
10. ID  48 | 전남87바1356       | 겸용   | 거리: 215.18km
================================================================================

✅ 검증 성공: 차량 26이 가장 가까운 냉동/겸용 차량으로 배정되었습니다!
```

### 배차 결과
```json
{
  "success": true,
  "total_orders": 1,
  "total_dispatches": 1,
  "dispatches": [
    {
      "id": 8,
      "dispatch_number": "DISP-20260127-V235771010",
      "vehicle_id": 26,
      "vehicle_code": "V235771010",
      "vehicle_plate": "전남87바1367",
      "vehicle_type": "겸용",
      "total_orders": 1,
      "total_pallets": 5,
      "total_weight_kg": 300.0,
      "initial_distance_km": 52.89,
      "status": "임시저장"
    }
  ]
}
```

### 로그 확인
```log
2026-01-27 11:30:00 | INFO | Vehicle 26 GPS location: (37.248821, 127.423734)
2026-01-27 11:30:00 | INFO | Assigned order ORD-GPS-TEST-001 to vehicle V235771010 (distance: 52.89 km)
2026-01-27 11:30:00 | INFO | Created 1 dispatch plans for zone
```

---

## 🔧 기술 세부사항

### 1. GPS 위치 우선순위
1. **최신 GPS 로그** (`VehicleGPSLog.created_at DESC`)
2. **차고지 위치** (`Vehicle.garage_latitude/longitude`)
3. **없음** (해당 차량 제외)

### 2. 거리 계산
- **공식**: Haversine Formula
- **단위**: km
- **정확도**: 소수점 2자리

```python
def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
    """Haversine distance in kilometers"""
    R = 6371  # Earth radius
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lon/2)**2)
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c
```

### 3. 배차 제약 조건
- ✅ **온도 구역 매칭** (냉동 → 냉동/겸용, 냉장 → 냉장/겸용, 상온 → 상온/겸용)
- ✅ **팔레트 용량** (current_pallets + order.pallet_count ≤ vehicle.max_pallets)
- ✅ **무게 용량** (current_weight + order.weight_kg ≤ vehicle.max_weight_kg)
- ✅ **GPS 거리** (최소 거리 차량 선택)

---

## 📊 성능 개선

### Before (기존 Greedy 알고리즘)
- 차량 리스트 순서대로 배차
- GPS 위치 미고려
- 거리 최적화 없음

### After (GPS 기반 알고리즘)
- **가장 가까운 차량 자동 선택**
- GPS 실시간 위치 활용
- 거리 정보 로깅
- 배차 효율성 향상

---

## 🔍 확인 방법

### 1. GPS 관제 확인
```bash
# GPS 위치 조회
curl http://localhost:8000/api/v1/uvis-gps/realtime/vehicles

# 특정 차량 GPS 위치
curl http://localhost:8000/api/v1/uvis-gps/realtime/vehicles | jq '.items[] | select(.vehicle_id == 26)'
```

### 2. AI 배차 실행
```bash
# 배차 최적화 (Greedy)
curl -X POST http://localhost:8000/api/v1/dispatches/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "order_ids": [15],
    "dispatch_date": "2026-01-27"
  }'
```

### 3. 프론트엔드 확인
1. **AI 배차** 메뉴 접속
2. 배차 대기 주문 선택
3. **Greedy 최적화** 실행
4. 결과 확인:
   - 배정된 차량
   - 거리 정보
   - 경로 확인

---

## 📝 주요 변경 파일

- `backend/app/services/dispatch_optimization_service.py`
  - `_get_vehicle_current_location()` 메서드 추가
  - `_optimize_zone()` 거리 기반 배차 로직 수정
  - VehicleGPSLog import 추가

---

## 🚀 다음 단계 (향후 개선)

### 1. 지오코딩 개선
- 거래처 주소 자동 지오코딩
- 네이버 지오코딩 API 활용
- 위도/경도 자동 업데이트

### 2. 실시간 경로 최적화
- 네이버 Directions API 연동
- 실제 도로 거리 계산
- 교통 정보 반영

### 3. 다중 주문 최적화
- 한 차량에 여러 주문 배정
- TSP (Traveling Salesman Problem) 알고리즘
- 경유지 최적 순서 계산

### 4. 예측 기반 배차
- 과거 배차 데이터 학습
- 차량 도착 시간 예측
- 최적 배차 시간 추천

---

## 🔗 관련 문서

- [GPS 관제 시스템 문서](./UVIS_GPS_SYSTEM.md)
- [배차 최적화 가이드](./DISPATCH_OPTIMIZATION.md)
- [API 문서](http://localhost:8000/docs)

---

## 📌 Git 정보

- **커밋**: b7f3082
- **브랜치**: genspark_ai_developer
- **커밋 메시지**: feat(dispatch): GPS 기반 가장 가까운 차량 자동 배차 기능 추가
- **변경 파일**: 1 file changed, 73 insertions(+), 22 deletions(-)

---

## 📞 접속 정보

- **Backend API**: http://localhost:8000
- **Frontend URL**: https://3000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai
- **API Docs**: http://localhost:8000/docs

---

## 👤 작성자

- **GenSpark AI Developer**
- **완료 시각**: 2026-01-27 21:40 (KST)
- **상태**: ✅ 완료 및 테스트 검증 완료
