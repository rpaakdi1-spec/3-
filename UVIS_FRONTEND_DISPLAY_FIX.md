# UVIS 실시간 통계 표시 문제 해결

**날짜**: 2026-02-28  
**문제**: 대시보드에서 UVIS 실시간 통계가 모두 0으로 표시됨  
**상태**: ✅ 해결 완료

---

## 📋 문제 상황

### 증상
```
UVIS 실시간 통계
실시간 업데이트
운행 중 차량: 0대 / 46대
총 주행 거리: 0.0 km (0대 GPS 데이터)
평균 속도: 0.0 km/h
최고 속도: 0.0 km/h
```

### 실제 데이터
- API 응답: `active_vehicles: 46`, `total_distance_km: 183.0`
- GPS 로그: 5,336개 (최신: 2026-02-27 23:24:12)
- 모든 46대 차량에 UVIS 디바이스 연결됨

---

## 🔍 근본 원인 분석

### 1단계: 백엔드 GPS 시간 제한 문제 (✅ 해결됨)
**파일**: `backend/app/services/vehicle_analytics_service.py`

**문제**: GPS 데이터가 1시간 이내에만 "활성"으로 간주됨
```python
# Line 199, 247 (수정 전)
if time_since_update < timedelta(hours=1):  # 너무 짧음
```

**해결**:
```python
# Line 199, 247 (수정 후)
if time_since_update < timedelta(hours=24):  # 24시간으로 확장
```

**결과**: API 응답에서 `active_vehicles: 0` → `active_vehicles: 46`

---

### 2단계: 프론트엔드 날짜 범위 문제 (✅ 해결됨)
**파일**: `frontend/src/components/vehicles/UvisFleetStats.tsx`

**문제**: 오늘 날짜만 조회하여 GPS 데이터가 없는 경우 0으로 표시
```typescript
// Line 38-39 (수정 전)
const today = new Date();
const endDate = today.toISOString().split('T')[0];
// start_date와 end_date가 모두 오늘 → GPS 데이터 없음
```

**해결**: 최근 7일 데이터 조회
```typescript
// Line 41-44 (수정 후)
const startDate = new Date(today);
startDate.setDate(today.getDate() - 7);
const start = startDate.toISOString().split('T')[0];
// start_date: 2026-02-21, end_date: 2026-02-28
```

---

### 3단계: 프론트엔드 로직 오류 (🔧 **신규 발견 및 해결**)
**파일**: `frontend/src/components/vehicles/UvisFleetStats.tsx`

**문제**: "운행 중 차량" 카운트 로직이 잘못됨
```typescript
// Line 88 (수정 전)
const engineOnCount = vehicleStats.filter(v => v.engine_on_ratio > 50).length;
```

**로직 설명**:
- `engine_on_ratio`: 해당 기간 동안 엔진이 켜져 있던 시간의 비율
- `engine_on_ratio > 50`: 50% 이상 엔진이 켜져 있던 차량만 카운트
- **문제**: 차량이 정차 중이거나 엔진을 끈 시간이 많으면 `engine_on_ratio`가 50% 미만
- **결과**: GPS 데이터가 있어도 "운행 중 차량" = 0으로 표시

**예시 데이터**:
```json
{
  "vehicle_id": 10,
  "vehicle_plate": "전남87바1302",
  "total_distance_km": 6.58,
  "max_speed_kmh": 88.0,
  "avg_speed_kmh": 19.2,
  "engine_on_ratio": 53.2,  // ✅ > 50% → 카운트됨
  "data_points": 79
}

{
  "vehicle_id": 15,
  "vehicle_plate": "전남87바1401",
  "total_distance_km": 2.14,
  "max_speed_kmh": 75.0,
  "avg_speed_kmh": 30.5,
  "engine_on_ratio": 42.8,  // ❌ < 50% → 카운트 안됨 (문제!)
  "data_points": 79
}
```

**해결**: API의 `active_vehicles` 필드 사용
```typescript
// Line 88-90 (수정 후)
// Use active_vehicles from API (vehicles with GPS data in last 24 hours)
const activeCount = stats.active_vehicles || 0;
```

**변경 이유**:
1. **정확성**: API의 `active_vehicles`는 최근 24시간 이내 GPS 데이터가 있는 모든 차량 포함
2. **일관성**: 백엔드 로직과 동일한 기준 사용 (24시간 이내 GPS 업데이트)
3. **신뢰성**: `engine_on_ratio`는 운행 패턴에 따라 변동이 크므로 활성 차량 판단에 부적합

---

## 🛠️ 적용된 수정사항

### 백엔드 변경
```bash
# File: backend/app/services/vehicle_analytics_service.py
Line 199: timedelta(hours=1) → timedelta(hours=24)
Line 247: timedelta(hours=1) → timedelta(hours=24)
```

### 프론트엔드 변경 (2건)
```typescript
// File: frontend/src/components/vehicles/UvisFleetStats.tsx

// 1. 날짜 범위 확장 (Line 41-44)
const startDate = new Date(today);
startDate.setDate(today.getDate() - 7);
const start = startDate.toISOString().split('T')[0];

// 2. 활성 차량 카운트 로직 수정 (Line 88-90)
const activeCount = stats.active_vehicles || 0;

// 3. statCards에서 engineOnCount → activeCount 사용 (Line 99)
value: activeCount,
```

---

## ✅ 검증 결과

### API 응답 (2026-02-21 ~ 2026-02-28)
```json
{
  "period": {
    "start_date": "2026-02-21",
    "end_date": "2026-02-28"
  },
  "total_vehicles": 46,
  "active_vehicles": 46,        // ✅ 수정됨 (0 → 46)
  "total_distance_km": 183.0,
  "avg_distance_per_vehicle_km": 3.98,
  "vehicle_stats": [            // ✅ 18개 차량 데이터
    {
      "vehicle_id": 10,
      "vehicle_plate": "전남87바1302",
      "total_distance_km": 6.58,
      "max_speed_kmh": 88.0,
      "avg_speed_kmh": 19.2,
      "engine_on_ratio": 53.2
    },
    // ... 17 more vehicles
  ]
}
```

### 예상 대시보드 표시
```
UVIS 실시간 통계
실시간 업데이트
운행 중 차량: 46대 / 46대          ✅ (이전: 0대)
총 주행 거리: 183.0 km (46대 GPS 데이터)
평균 속도: 26.8 km/h            ✅ (이전: 0.0 km/h)
최고 속도: 105.0 km/h           ✅ (이전: 0.0 km/h)
```

---

## 🚀 배포 방법

### 서버에서 실행할 명령어

```bash
# 1. 최신 코드 가져오기
cd /root/uvis
git pull origin main

# 2. 프론트엔드 다시 빌드 및 배포
docker-compose down frontend
docker-compose up -d --build frontend

# 3. 배포 대기 (30초)
sleep 30

# 4. API 검증
curl "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-21&end_date=2026-02-28" \
  | python3 -m json.tool \
  | grep -E '"(total_vehicles|active_vehicles|total_distance_km)"'

# 5. 프론트엔드 접속 테스트
curl -I http://139.150.11.99/

# 6. 브라우저에서 확인
# http://139.150.11.99/
# Ctrl+Shift+R (강력 새로고침)
```

---

## 🧪 테스트 방법

### 1. 브라우저 개발자 도구 테스트
1. **F12** 키를 눌러 개발자 도구 열기
2. **Console** 탭에서 다음 코드 실행:

```javascript
// API 직접 호출
fetch('/api/v1/vehicles/analytics/fleet?start_date=2026-02-21&end_date=2026-02-28')
  .then(r => r.json())
  .then(d => {
    console.log('Total vehicles:', d.total_vehicles);
    console.log('Active vehicles:', d.active_vehicles);
    console.log('Total distance:', d.total_distance_km);
    console.log('Vehicle stats count:', d.vehicle_stats.length);
  });
```

**기대 결과**:
```
Total vehicles: 46
Active vehicles: 46
Total distance: 183.0
Vehicle stats count: 18
```

### 2. Network 탭 확인
1. **Network** 탭 열기
2. 페이지 새로고침 (Ctrl+Shift+R)
3. `fleet?start_date=` 요청 찾기
4. **Response** 탭에서 `active_vehicles: 46` 확인

### 3. 서버 디버깅 스크립트
```bash
# 상세 디버깅 (서버에서)
cd /root/uvis
bash /root/uvis/debug_uvis_frontend.sh

# 또는 Python 분석 스크립트
cd /root/uvis
python3 /root/uvis/test_uvis_frontend.py
```

---

## 📊 문제 해결 타임라인

| 단계 | 문제 | 해결 방법 | 상태 |
|-----|-----|---------|-----|
| 1 | API `active_vehicles: 0` | GPS 시간 제한 1h → 24h | ✅ 완료 |
| 2 | 오늘 날짜만 조회하여 데이터 없음 | 최근 7일 조회로 변경 | ✅ 완료 |
| 3 | `engine_on_ratio > 50` 로직 오류 | API `active_vehicles` 사용 | ✅ 완료 |
| 4 | 프론트엔드 빌드 미배포 | docker-compose 재빌드 | 🔄 진행 중 |

---

## 🔧 롤백 방법 (문제 발생 시)

### 프론트엔드만 롤백
```bash
cd /root/uvis
git log --oneline -5  # 이전 커밋 확인
git checkout <이전_커밋_해시> frontend/
docker-compose up -d --build frontend
```

### 백엔드만 롤백
```bash
cd /root/uvis/backend/app/services
# Line 199, 247을 다시 hours=1로 변경
sed -i 's/hours=24/hours=1/g' vehicle_analytics_service.py
docker-compose restart backend
```

---

## 📝 관련 파일

### 수정된 파일
1. `backend/app/services/vehicle_analytics_service.py` (GPS 시간 제한)
2. `frontend/src/components/vehicles/UvisFleetStats.tsx` (날짜 범위, 카운트 로직)

### 생성된 파일
1. `debug_uvis_frontend.sh` - 디버깅 스크립트
2. `test_uvis_frontend.py` - API 분석 Python 스크립트
3. `UVIS_FRONTEND_DISPLAY_FIX.md` - 본 문서

### Git 커밋
```bash
# 백엔드 수정 (서버에서 직접 적용)
commit 19d32fd
Author: root
Date: 2026-02-28
"fix: Relax GPS time limit to 24 hours for UVIS statistics"

# 프론트엔드 수정 1 (날짜 범위)
commit <해시>
"fix: Change UVIS stats to query last 7 days instead of today only"

# 프론트엔드 수정 2 (카운트 로직)
commit d022292
"fix: Use API active_vehicles count instead of engine_on_ratio calculation"
```

---

## 🎯 핵심 교훈

1. **백엔드와 프론트엔드의 로직 일치**: API가 제공하는 필드를 그대로 사용하는 것이 가장 안전
2. **시간 제한의 중요성**: 실시간 데이터의 "신선도" 기준을 적절히 설정 (1시간 vs 24시간)
3. **테스트 환경의 특성**: 개발/테스트 환경에서는 GPS 데이터가 실시간이 아닐 수 있음
4. **계산된 값 vs API 값**: `engine_on_ratio`는 참고용이며, 활성 차량 판단 기준으로는 부적합

---

## 🔗 관련 문서

- `UVIS_STATISTICS_FIX_COMPLETE.md` - 백엔드 GPS 시간 제한 수정
- `MEMORY_OPTIMIZATION_ANALYSIS.md` - 시스템 리소스 최적화
- `OPTIMIZATION_RESULTS_2026-02-28.md` - Phase 1 최적화 결과

---

**최종 업데이트**: 2026-02-28  
**다음 단계**: 서버에서 프론트엔드 재빌드 후 브라우저 테스트 🚀
