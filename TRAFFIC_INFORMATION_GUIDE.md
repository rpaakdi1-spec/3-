# 실시간 교통 정보 연동 시스템

## 📋 개요

네이버와 카카오 교통 API를 연동하여 실시간 교통 상황을 반영한 정확한 배송 시간 예측 및 최적 경로를 제공하는 시스템입니다.

### 주요 기능

1. **실시간 경로 탐색** - 교통 상황 반영한 최적 경로
2. **소요 시간 계산** - 정확한 배송 시간 예측
3. **교통 상황 분석** - 혼잡도 및 통행 정보
4. **최적 경로 순서** - TSP와 교통 정보 결합
5. **예상 도착 시간** - 동적 업데이트
6. **API 비교 기능** - 네이버 vs 카카오

---

## 🎯 시스템 구성

### Backend

**서비스:** `/backend/app/services/traffic_service.py` (19,409자)  
**API:** `/backend/app/api/traffic.py` (10,902자)  
**설정:** `/backend/app/core/config.py` (업데이트)

#### 주요 클래스 및 메서드

```python
class TrafficService:
    # 실시간 경로 탐색
    get_route_with_traffic()
    
    # 내부 메서드
    _get_naver_route()          # 네이버 Directions API
    _get_kakao_route()          # 카카오 길찾기 API
    _get_fallback_route()       # Fallback (Haversine)
    _analyze_naver_traffic()    # 교통 정보 분석
    
    # 최적 경로 순서
    get_optimized_route_order()
    
    # 도착 시간 예측
    estimate_arrival_time()
    
    # 교통 상황 요약
    get_traffic_summary()
```

### Frontend

**서비스:** `/frontend/src/services/trafficService.ts` (4,768자)

---

## 🚀 API 엔드포인트

### 1. 실시간 경로 탐색

**POST** `/api/v1/traffic/route`

**요청:**
```json
{
  "start": {
    "latitude": 37.5665,
    "longitude": 126.9780
  },
  "end": {
    "latitude": 37.3951,
    "longitude": 127.1113
  },
  "waypoints": [
    {
      "latitude": 37.4979,
      "longitude": 127.0276
    }
  ],
  "provider": "naver",
  "option": "trafast"
}
```

**응답:**
```json
{
  "provider": "naver",
  "distance_km": 30.5,
  "duration_minutes": 45,
  "duration_with_traffic_minutes": 58,
  "traffic_info": {
    "overall_level": "서행",
    "smooth_ratio": 45.2,
    "slow_ratio": 38.5,
    "congested_ratio": 16.3,
    "description": "서행 - 다소 막히는 구간이 있습니다"
  },
  "fuel_cost": 4500,
  "toll_cost": 2000,
  "taxi_fare": 28000,
  "path_coordinates": [
    {"latitude": 37.5665, "longitude": 126.9780},
    {"latitude": 37.5555, "longitude": 126.9870},
    ...
  ],
  "option": "trafast",
  "retrieved_at": "2026-01-27T20:30:00"
}
```

### 2. 간단 경로 탐색

**GET** `/api/v1/traffic/route/simple`

**파라미터:**
- `start_lat`: 출발지 위도
- `start_lon`: 출발지 경도
- `end_lat`: 도착지 위도
- `end_lon`: 도착지 경도
- `provider`: 교통 정보 제공자 (naver/kakao)
- `option`: 경로 옵션

**예시:**
```bash
curl "http://localhost:8000/api/v1/traffic/route/simple?start_lat=37.5665&start_lon=126.9780&end_lat=37.3951&end_lon=127.1113&provider=naver&option=trafast"
```

### 3. 예상 도착 시간 계산

**POST** `/api/v1/traffic/arrival-estimate`

**요청:**
```json
{
  "current_location": {
    "latitude": 37.5665,
    "longitude": 126.9780
  },
  "destination": {
    "latitude": 37.3951,
    "longitude": 127.1113
  },
  "departure_time": "2026-01-27T20:30:00"
}
```

**응답:**
```json
{
  "departure_time": "2026-01-27T20:30:00",
  "estimated_arrival_time": "2026-01-27T21:28:00",
  "early_arrival_time": "2026-01-27T21:19:00",
  "late_arrival_time": "2026-01-27T21:37:00",
  "duration_minutes": 58,
  "distance_km": 30.5,
  "traffic_info": {
    "overall_level": "서행",
    "description": "서행 - 다소 막히는 구간이 있습니다"
  },
  "confidence": "medium",
  "updated_at": "2026-01-27T20:30:05"
}
```

### 4. 간단 도착 시간 예측

**GET** `/api/v1/traffic/arrival-estimate/simple`

**파라미터:**
- `current_lat`: 현재 위도
- `current_lon`: 현재 경도
- `dest_lat`: 목적지 위도
- `dest_lon`: 목적지 경도

**예시:**
```bash
curl "http://localhost:8000/api/v1/traffic/arrival-estimate/simple?current_lat=37.5665&current_lon=126.9780&dest_lat=37.3951&dest_lon=127.1113"
```

### 5. API 테스트

**GET** `/api/v1/traffic/traffic/test`

**파라미터:**
- `provider`: 테스트할 제공자 (naver/kakao)

**응답:**
```json
{
  "status": "success",
  "provider": "naver",
  "api_configured": true,
  "response_time_ms": 245.32,
  "test_route": {
    "from": "서울시청",
    "to": "판교역",
    "distance_km": 30.5,
    "duration_minutes": 45
  },
  "message": "API 연결 성공!"
}
```

### 6. 경로 비교

**GET** `/api/v1/traffic/traffic/compare`

**파라미터:**
- `start_lat`, `start_lon`: 출발지
- `end_lat`, `end_lon`: 도착지

**응답:**
```json
{
  "routes": {
    "naver": {
      "distance_km": 30.5,
      "duration_with_traffic_minutes": 58,
      ...
    },
    "kakao": {
      "distance_km": 31.2,
      "duration_with_traffic_minutes": 62,
      ...
    }
  },
  "comparison": {
    "recommendation": "naver",
    "reason": "네이버가 4.0분 더 빠릅니다"
  }
}
```

---

## 🔧 설정

### 환경 변수

`.env` 파일에 다음 설정 추가:

```bash
# 네이버 Map API (필수)
NAVER_MAP_CLIENT_ID=your_naver_client_id
NAVER_MAP_CLIENT_SECRET=your_naver_client_secret

# 카카오 API (선택)
KAKAO_REST_API_KEY=your_kakao_rest_api_key
```

### API 키 발급

#### 네이버 API

1. [네이버 클라우드 플랫폼](https://www.ncloud.com/) 접속
2. 콘솔 로그인
3. **Services** > **AI·NAVER API** > **Maps**
4. **Application 등록**
5. **Directions** API 활성화
6. **인증 정보** 탭에서 Client ID와 Client Secret 복사

#### 카카오 API

1. [카카오 개발자 사이트](https://developers.kakao.com/) 접속
2. 내 애플리케이션 > 애플리케이션 추가
3. **플랫폼** 설정
4. **앱 키** > REST API 키 복사
5. **제품 설정** > **카카오내비** 활성화

---

## 💻 사용 방법

### Backend 사용

```python
from app.services.traffic_service import TrafficService

# 서비스 인스턴스 생성
traffic = TrafficService()

# 1. 실시간 경로 탐색
route = traffic.get_route_with_traffic(
    start_lat=37.5665,
    start_lon=126.9780,
    end_lat=37.3951,
    end_lon=127.1113,
    provider=TrafficProvider.NAVER,
    option=RouteOption.TRAFAST
)

print(f"거리: {route['distance_km']}km")
print(f"소요 시간: {route['duration_with_traffic_minutes']}분")
print(f"교통 상황: {route['traffic_info']['overall_level']}")

# 2. 예상 도착 시간
estimate = traffic.estimate_arrival_time(
    current_lat=37.5665,
    current_lon=126.9780,
    destination_lat=37.3951,
    destination_lon=127.1113
)

print(f"예상 도착: {estimate['estimated_arrival_time']}")
print(f"신뢰 구간: {estimate['early_arrival_time']} ~ {estimate['late_arrival_time']}")

# 3. 최적 경로 순서 (TSP + 교통)
destinations = [
    (37.4979, 127.0276, {"name": "강남역"}),
    (37.5172, 127.0473, {"name": "삼성역"}),
    (37.5048, 127.0495, {"name": "선릉역"})
]

optimized = traffic.get_optimized_route_order(
    start_location=(37.5665, 126.9780),
    destinations=destinations
)

for route in optimized:
    print(f"{route['sequence']}번째: {route['distance_km']}km, {route['duration_minutes']}분")
```

### Frontend 사용

```typescript
import trafficService from './services/trafficService';

// 1. 실시간 경로 조회
const route = await trafficService.getSimpleRoute(
  37.5665, 126.9780,  // 출발지
  37.3951, 127.1113,  // 도착지
  'naver',
  'trafast'
);

console.log(`거리: ${trafficService.formatDistance(route.distance_km)}`);
console.log(`소요 시간: ${trafficService.formatDuration(route.duration_with_traffic_minutes)}`);

// 2. 교통 혼잡도 색상
const color = trafficService.getTrafficColor(route.traffic_info?.overall_level || '보통');

// 3. 예상 도착 시간
const estimate = await trafficService.estimateArrivalTime(
  37.5665, 126.9780,  // 현재 위치
  37.3951, 127.1113   // 목적지
);

console.log(`예상 도착: ${new Date(estimate.estimated_arrival_time).toLocaleString()}`);

// 4. API 테스트
const test = await trafficService.testTrafficAPI('naver');
console.log(test.message);

// 5. 경로 비교
const comparison = await trafficService.compareRoutes(
  37.5665, 126.9780,
  37.3951, 127.1113
);

console.log(comparison.comparison.reason);
```

---

## 📊 교통 정보 분석

### 교통 혼잡도 레벨

| 레벨 | 설명 | 색상 | 판단 기준 |
|------|------|------|----------|
| 원활 | 교통 흐름이 매우 좋음 | 녹색 | 원활 구간 70% 이상 |
| 보통 | 평균적인 교통 상황 | 파랑 | 기본 상태 |
| 서행 | 다소 막히는 구간 존재 | 주황 | 서행 구간 40% 이상 |
| 정체 | 심한 정체 예상 | 빨강 | 정체 구간 30% 이상 |
| 차단 | 통행 불가능 | 회색 | 도로 차단 |

### 네이버 교통 정보 분석

네이버 Directions API는 각 도로 구간별 교통 정보를 제공합니다:

```python
# traffic 값
0: 원활
1: 서행
2 이상: 정체
```

**분석 로직:**
```python
def _analyze_naver_traffic(route):
    for section in route["section"]:
        for road in section["road"]:
            traffic = road.get("traffic", 0)
            distance = road.get("distance", 0)
            
            if traffic == 0:
                smooth_distance += distance
            elif traffic == 1:
                slow_distance += distance
            else:
                congested_distance += distance
    
    # 비율 계산
    smooth_ratio = smooth_distance / total_distance
    slow_ratio = slow_distance / total_distance
    congested_ratio = congested_distance / total_distance
```

---

## 🔄 배송 추적 시스템 통합

배송 추적 시스템의 예상 도착 시간 계산이 자동으로 실시간 교통 정보를 사용하도록 업데이트되었습니다.

### Before (기본 Haversine)

```python
distance = haversine(current_location, destination)
duration = (distance / 40) * 60  # 평균 40km/h
duration_with_traffic = duration * 1.3  # +30% 여유
```

### After (실시간 교통 정보)

```python
from app.services.traffic_service import TrafficService

traffic_service = TrafficService()
estimate = traffic_service.estimate_arrival_time(
    current_lat=current_location.latitude,
    current_lon=current_location.longitude,
    destination_lat=destination.latitude,
    destination_lon=destination.longitude
)

# 실제 교통 상황 반영된 도착 시간
arrival_time = estimate["estimated_arrival_time"]
```

**장점:**
- ✅ 실시간 교통 상황 반영
- ✅ 더 정확한 예상 시간
- ✅ 신뢰 구간 제공
- ✅ Fallback 메커니즘 (API 실패 시 기본 계산)

---

## 🎯 경로 옵션

### 네이버 경로 옵션

| 옵션 | 설명 | 추천 사용처 |
|------|------|------------|
| trafast | 실시간 빠른길 | 긴급 배송 |
| tracomfort | 실시간 편한길 | 일반 배송 |
| traoptimal | 실시간 최적 | 균형 있는 경로 |
| traavoidtoll | 무료 우선 | 비용 절감 |
| traavoidcaronly | 자전 전용도로 회피 | 대형 차량 |

### 사용 예시

```python
# 긴급 배송 - 가장 빠른 길
route_fast = traffic.get_route_with_traffic(
    ...,
    option=RouteOption.TRAFAST
)

# 비용 절감 - 무료 도로 우선
route_free = traffic.get_route_with_traffic(
    ...,
    option=RouteOption.TRAAVOIDTOLL
)
```

---

## 🧪 테스트

### 1. API 연결 테스트

```bash
# 네이버 API 테스트
curl "http://localhost:8000/api/v1/traffic/traffic/test?provider=naver"

# 카카오 API 테스트
curl "http://localhost:8000/api/v1/traffic/traffic/test?provider=kakao"
```

### 2. 샘플 경로 조회

```bash
# 서울시청 → 판교역
curl "http://localhost:8000/api/v1/traffic/route/simple?start_lat=37.5665&start_lon=126.9780&end_lat=37.3951&end_lon=127.1113&provider=naver"
```

### 3. Python 테스트

```python
from app.services.traffic_service import TrafficService

traffic = TrafficService()

# 서울시청 → 판교역
route = traffic.get_route_with_traffic(
    start_lat=37.5665,
    start_lon=126.9780,
    end_lat=37.3951,
    end_lon=127.1113
)

assert route["provider"] in ["naver", "kakao", "fallback"]
assert route["distance_km"] > 0
assert route["duration_with_traffic_minutes"] > 0
```

---

## 🚨 에러 처리

### Fallback 메커니즘

API 호출 실패 시 자동으로 Haversine 기반 기본 계산으로 전환:

```python
try:
    # 실시간 교통 API 시도
    route = traffic.get_route_with_traffic(...)
except Exception as e:
    logger.error(f"Traffic API failed: {e}")
    # Fallback 계산 자동 적용
    route = traffic._get_fallback_route(...)
```

**Fallback 응답:**
```json
{
  "provider": "fallback",
  "distance_km": 39.65,
  "duration_minutes": 59.48,
  "duration_with_traffic_minutes": 77.32,
  "note": "Fallback calculation (Haversine)",
  "traffic_info": {
    "overall_level": "보통",
    "description": "교통 정보 API를 사용할 수 없어 기본 계산을 사용했습니다."
  }
}
```

### 에러 유형

1. **API 키 미설정**
   - 상태: `fallback`
   - 메시지: "API 키가 설정되지 않았거나 연결 실패"

2. **API 호출 실패**
   - 상태: `error`
   - 메시지: API 응답 오류 메시지

3. **타임아웃**
   - 타임아웃: 10초
   - 자동 Fallback 적용

---

## 📈 성능 최적화

### 1. 응답 캐싱 (향후 구현)

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1000)
def get_cached_route(
    start_lat, start_lon,
    end_lat, end_lon,
    timestamp  # 5분 단위로 캐싱
):
    return traffic.get_route_with_traffic(...)
```

### 2. 배치 요청

여러 경로를 한 번에 조회:

```python
routes = []
for dest in destinations:
    route = traffic.get_route_with_traffic(
        start_lat, start_lon,
        dest.latitude, dest.longitude
    )
    routes.append(route)

summary = traffic.get_traffic_summary(routes)
```

### 3. 비동기 처리 (향후)

```python
import asyncio

async def get_multiple_routes(locations):
    tasks = [
        asyncio.create_task(get_route_async(loc))
        for loc in locations
    ]
    return await asyncio.gather(*tasks)
```

---

## 🔜 향후 개선 사항

### 단기 (1-2주)

1. **Redis 캐싱**
   - 경로 정보 5분간 캐싱
   - API 호출 횟수 감소

2. **배치 경로 조회**
   - 한 번에 여러 경로 조회
   - 성능 향상

3. **웹소켓 실시간 업데이트**
   - 교통 상황 변화 시 자동 알림
   - 예상 도착 시간 동적 갱신

### 중기 (1-2개월)

1. **교통 예측 모델**
   - 과거 데이터 기반 ML 모델
   - 요일/시간대별 교통 패턴 학습

2. **대체 경로 제안**
   - 사고/공사 구간 회피
   - 실시간 최적 경로 재계산

3. **교통 통계 대시보드**
   - 구간별 평균 소요 시간
   - 혼잡 시간대 분석

### 장기 (3개월 이상)

1. **TMAP API 연동**
   - SK TMAP 교통 정보
   - 더 정확한 트럭 경로

2. **자체 교통 데이터 수집**
   - 차량 GPS 기반 교통 정보
   - 실제 배송 데이터 활용

---

## 📚 참고 자료

### API 문서

- **네이버 Directions API:** https://api.ncloud-docs.com/docs/ai-naver-mapsdirections-driving
- **카카오 길찾기 API:** https://developers.kakao.com/docs/latest/ko/local/dev-guide#route

### 관련 문서

- **배송 추적 가이드:** `/DELIVERY_TRACKING_GUIDE.md`
- **PostgreSQL 마이그레이션:** `/POSTGRESQL_MIGRATION_GUIDE.md`
- **API 문서:** `http://localhost:8000/docs`

---

## ✅ 완료 체크리스트

- [x] 네이버 Directions API 연동
- [x] 카카오 길찾기 API 연동
- [x] 실시간 경로 탐색 API
- [x] 예상 도착 시간 계산 API
- [x] 교통 정보 분석
- [x] 최적 경로 순서 계산
- [x] Fallback 메커니즘
- [x] API 테스트 엔드포인트
- [x] 경로 비교 기능
- [x] Frontend 서비스
- [x] 배송 추적 시스템 통합
- [x] 문서화

---

## 🎉 결론

실시간 교통 정보 연동 시스템이 성공적으로 완료되었습니다!

**주요 성과:**
- ✅ 네이버/카카오 API 완전 통합
- ✅ 6개 API 엔드포인트 구현
- ✅ 실시간 교통 반영 경로 탐색
- ✅ 정확한 예상 도착 시간
- ✅ TSP와 교통 정보 결합
- ✅ 배송 추적 시스템 통합
- ✅ Fallback 메커니즘
- ✅ 완전한 문서화

**통계:**
- Backend: 30,311자 (2개 파일)
- Frontend: 4,768자 (1개 파일)
- 문서: 본 가이드

**다음 단계:**
- 모니터링 및 알림 시스템

---

**작성일:** 2026-01-27  
**작성자:** GenSpark AI Developer  
**프로젝트:** Cold Chain Dispatch System  
**GitHub:** https://github.com/rpaakdi1-spec/3-  
**Pull Request:** https://github.com/rpaakdi1-spec/3-/pull/1
