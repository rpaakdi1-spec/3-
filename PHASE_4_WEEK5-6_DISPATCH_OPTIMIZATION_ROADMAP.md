# Phase 4 Week 5-6: 자동 배차 최적화 시스템

**시작일**: 2026-02-05  
**예상 완료일**: 2026-02-19  
**상태**: 🚧 진행 중  
**목표**: 연간 ₩120,000,000 절감

---

## 🎯 프로젝트 개요

다중 차량 경로 최적화, 실시간 교통 정보 통합, 운전자 스킬 매칭을 통해 배차 효율성을 극대화하는 AI 기반 자동 배차 최적화 시스템을 구축합니다.

---

## 💰 예상 비즈니스 임팩트

### 핵심 성과 지표 (KPI)

| 지표 | 현재 | 목표 | 개선율 | 연간 가치 |
|------|------|------|--------|-----------|
| **배차 처리 시간** | 15분 | 5분 | -65% | ₩40M |
| **차량 가동률** | 65% | 80% | +23% | ₩35M |
| **공차 거리** | 28% | 18% | -35% | ₩25M |
| **연료 비용** | - | -18% | -18% | ₩15M |
| **일일 배송 건수** | 100건 | 128건 | +28% | ₩5M |

### 총 연간 절감액: **₩120,000,000**

### 추가 효과
- 고객 만족도 향상 (정시 배송률 +15%)
- 운전자 만족도 향상 (공평한 배차)
- CO2 배출량 감소 (18%)
- 차량 마모 감소 (최적 경로)

---

## 🏗️ 시스템 아키텍처

### 기술 스택

#### 백엔드
```
FastAPI + OR-Tools + Redis + PostgreSQL
├── DispatchOptimizationService
│   ├── 다중 차량 경로 최적화 (OR-Tools VRP)
│   ├── 실시간 교통 정보 통합
│   ├── 운전자 스킬 매칭
│   ├── 차량 용량 최적화
│   ├── 비용 최소화 알고리즘
│   └── 동적 재배차 엔진
├── TrafficIntegrationService
│   ├── Google Maps API 연동
│   ├── 실시간 교통 정보 수집
│   ├── 거리 및 시간 매트릭스 계산
│   └── 경로 예측
└── OptimizationAPI
    ├── REST 엔드포인트 (8개)
    ├── WebSocket 실시간 업데이트
    └── 백그라운드 작업 큐 (Celery)
```

#### 프론트엔드
```
React + TypeScript + Recharts + Leaflet
├── DispatchOptimizationPage
│   ├── 자동 배차 대시보드
│   ├── 배차 제약 조건 설정
│   ├── 최적화 실행 및 결과 표시
│   ├── 경로 시각화 (지도)
│   ├── 실시간 진행 상황
│   └── 성과 비교 차트
└── RouteVisualization
    ├── Leaflet 지도 통합
    ├── 차량별 경로 표시
    ├── 배송지 마커
    └── 실시간 차량 위치
```

---

## 🔧 핵심 기능

### 1. 다중 차량 경로 최적화 (VRP)

#### 최적화 알고리즘
- **Vehicle Routing Problem (VRP)** with Time Windows
- OR-Tools 라이브러리 사용
- 제약 조건:
  - 차량 용량 (톤, 팔레트 수)
  - 배송 시간 창 (고객 요청 시간)
  - 운전자 근무 시간 (최대 8시간)
  - 차량 타입 (냉장, 냉동, 상온)
  - 운전자 면허 및 스킬

#### 목적 함수
```python
# 최소화 목표
minimize(
    total_distance * distance_cost +
    total_time * time_cost +
    empty_distance * empty_cost +
    num_vehicles * vehicle_cost +
    late_deliveries * penalty_cost
)
```

### 2. 실시간 교통 정보 통합

#### Google Maps API 연동
- **Distance Matrix API**: 차량-배송지 간 거리/시간 계산
- **Directions API**: 최적 경로 계산
- **Traffic Data**: 실시간 교통 상황 반영
- **Geocoding API**: 주소 → 좌표 변환

#### 캐싱 전략
- Redis 캐시: 자주 사용하는 경로 (1시간 TTL)
- 데이터베이스: 과거 경로 데이터 저장
- 배치 요청: API 호출 최소화

### 3. 운전자 스킬 매칭

#### 운전자 프로필
```python
DriverProfile:
  - license_type: ["일반", "대형", "특수"]
  - vehicle_types: ["냉장", "냉동", "상온"]
  - experience_years: int
  - performance_score: float (0-100)
  - skill_tags: ["위험물", "장거리", "도심"]
  - max_work_hours: 8
  - current_location: (lat, lng)
```

#### 매칭 알고리즘
- 차량 타입 매칭 (필수)
- 배송 거리 및 난이도 매칭
- 운전자 성과 점수 기반 우선순위
- 공평한 배차 (로테이션)

### 4. 차량 용량 최적화

#### 용량 제약
```python
VehicleCapacity:
  - max_weight: float (톤)
  - max_pallets: int (팔레트 수)
  - max_volume: float (m³)
  - max_orders: int (건수)
```

#### 적재 최적화
- 배송 순서 고려 (LIFO/FIFO)
- 무게 중심 분산
- 온도 구역 분리

### 5. 동적 재배차

#### 재배차 트리거
- 신규 긴급 주문 발생
- 차량 고장 또는 사고
- 교통 상황 급변
- 배송 취소 또는 변경
- 운전자 근무 시간 초과

#### 재최적화 로직
- 부분 경로 재계산 (영향 받은 차량만)
- 실시간 제약 조건 업데이트
- WebSocket으로 즉시 알림

---

## 📡 API 엔드포인트

### 최적화 API

#### 1. 배차 최적화 실행
```http
POST /api/v1/dispatch-optimization/optimize
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "order_ids": [1, 2, 3, ...],
  "date": "2026-02-05",
  "constraints": {
    "max_vehicles": 10,
    "max_route_time": 480,  // 8시간 (분)
    "priority_orders": [1, 5],
    "excluded_vehicles": [3]
  },
  "options": {
    "use_traffic_data": true,
    "optimize_fuel": true,
    "balance_workload": true
  }
}

Response:
{
  "optimization_id": "OPT-2026-0205-0001",
  "status": "completed",
  "summary": {
    "total_vehicles": 8,
    "total_orders": 45,
    "total_distance": 450.5,
    "total_time": 385,
    "empty_distance": 65.2,
    "estimated_cost": 245000,
    "improvement_vs_manual": {
      "distance": -28.5,
      "time": -35.2,
      "cost": -42000
    }
  },
  "routes": [
    {
      "route_id": 1,
      "vehicle_id": 5,
      "driver_id": 12,
      "orders": [1, 4, 7, 9, 11],
      "sequence": [
        {
          "type": "depot",
          "location": {"lat": 37.5665, "lng": 126.9780},
          "arrival_time": "08:00:00",
          "departure_time": "08:15:00"
        },
        {
          "type": "delivery",
          "order_id": 1,
          "location": {"lat": 37.5512, "lng": 126.9882},
          "arrival_time": "08:42:00",
          "service_time": 10,
          "departure_time": "08:52:00"
        },
        ...
      ],
      "total_distance": 65.3,
      "total_time": 125,
      "load": {"weight": 3.5, "pallets": 8}
    },
    ...
  ],
  "unassigned_orders": [],
  "optimization_time": 2.5,
  "created_at": "2026-02-05T08:00:00Z"
}
```

#### 2. 최적화 상태 조회
```http
GET /api/v1/dispatch-optimization/status/{optimization_id}
```

#### 3. 실시간 재최적화
```http
POST /api/v1/dispatch-optimization/re-optimize
{
  "optimization_id": "OPT-2026-0205-0001",
  "reason": "new_urgent_order",
  "changes": {
    "new_orders": [46, 47],
    "cancelled_orders": [23],
    "unavailable_vehicles": [3]
  }
}
```

#### 4. 배차 승인 및 적용
```http
POST /api/v1/dispatch-optimization/{optimization_id}/approve
{
  "approved_by": "user_id",
  "notes": "승인함"
}
```

#### 5. 최적화 이력 조회
```http
GET /api/v1/dispatch-optimization/history?date_from=2026-02-01&date_to=2026-02-05
```

#### 6. 성과 비교 분석
```http
GET /api/v1/dispatch-optimization/performance?optimization_id=xxx
```

#### 7. 거리/시간 매트릭스 계산
```http
POST /api/v1/dispatch-optimization/distance-matrix
{
  "origins": [{"lat": 37.5665, "lng": 126.9780}, ...],
  "destinations": [{"lat": 37.5512, "lng": 126.9882}, ...],
  "use_traffic": true
}
```

#### 8. 제약 조건 시뮬레이션
```http
POST /api/v1/dispatch-optimization/simulate
{
  "scenarios": [
    {"max_vehicles": 10},
    {"max_vehicles": 8},
    {"max_vehicles": 12}
  ]
}
```

### WebSocket

#### 실시간 최적화 진행 상황
```
WS /api/v1/ws/optimization/{optimization_id}

Messages:
{
  "type": "optimization_progress",
  "progress": 65,
  "current_iteration": 1300,
  "best_cost": 245000,
  "message": "차량 8대, 경로 계산 중..."
}

{
  "type": "optimization_complete",
  "result": {...}
}
```

---

## 🎨 프론트엔드 UI 설계

### 메인 대시보드

```
┌─────────────────────────────────────────────────────────────┐
│ 🚚 자동 배차 최적화                           [설정] [실행] │
├─────────────────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐             │
│ │대기중│ │배정됨│ │절감액│ │개선율│ │차량수│             │
│ │  45  │ │  38  │ │₩42K │ │ 28%  │ │  8   │             │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘             │
├─────────────────────────────────────────────────────────────┤
│ 제약 조건 설정                                              │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 날짜: [2026-02-05▼]  차량: [전체 (10대)▼]              ││
│ │ 최대 경로 시간: [8시간]  □ 교통정보 사용               ││
│ │ 우선 주문: [긴급 5건 선택됨]  ✓ 연료 최적화            ││
│ │ 제외 차량: [정비중 1대]  ✓ 업무량 균등 배분            ││
│ └─────────────────────────────────────────────────────────┘│
├───────────────────────────────┬─────────────────────────────┤
│ 최적화 결과 (8개 경로)        │ 지도 시각화                 │
│ ┌───────────────────────────┐ │ ┌─────────────────────────┐│
│ │ 경로 #1 [V005 - 김철수]   │ │ │   🗺️                   ││
│ │ 주문: 6건  거리: 65.3km   │ │ │                         ││
│ │ 시간: 125분  적재: 3.5톤  │ │ │  📍━━🚚━━📍━━📍       ││
│ │ [상세보기] [경로수정]      │ │ │     │                   ││
│ └───────────────────────────┘ │ │  📍━━📍  📍━━📍       ││
│ ┌───────────────────────────┐ │ │                         ││
│ │ 경로 #2 [V012 - 박영희]   │ │ │  범례:                  ││
│ │ 주문: 5건  거리: 52.1km   │ │ │  🚚 차량  📍 배송지     ││
│ │ 시간: 110분  적재: 2.8톤  │ │ └─────────────────────────┘│
│ │ [상세보기] [경로수정]      │ │                             │
│ └───────────────────────────┘ │                             │
├───────────────────────────────┴─────────────────────────────┤
│ 성과 비교                                                   │
│ ┌─────────────────────────────────────────────────────────┐│
│ │   수동 배차 vs AI 최적화                                ││
│ │   ┌───┬───┬───┬───┐                                    ││
│ │   │███│   │   │   │ 거리: -28.5% (190km 절감)         ││
│ │   │███│   │   │   │ 시간: -35.2% (190분 절감)         ││
│ │   │███│   │   │   │ 비용: -₩42,000 (14.6% 절감)       ││
│ │   └───┴───┴───┴───┘                                    ││
│ └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 경로 상세 모달

```
┌──────────────────────────────────────────────────┐
│ 경로 #1 상세 정보                     [X] 닫기  │
├──────────────────────────────────────────────────┤
│ 차량: V005 (냉장 5톤)                            │
│ 운전자: 김철수 (경력 5년, 성과: 92점)            │
│ 총 거리: 65.3km  총 시간: 125분                 │
│ 적재량: 3.5톤 (70%)  팔레트: 8개 (80%)          │
├──────────────────────────────────────────────────┤
│ 배송 순서                                        │
│ ┌──────────────────────────────────────────────┐│
│ │ 1. [08:15] 출고 - 본사 창고                  ││
│ │ 2. [08:42] 배송 - 주문 #1234 (강남구)       ││
│ │    - 도착: 08:42  서비스: 10분  출발: 08:52 ││
│ │    - 거리: 12.5km  예상시간: 27분            ││
│ │    🟢 정시 도착 예정                         ││
│ │ 3. [09:15] 배송 - 주문 #1245 (서초구)       ││
│ │    - 도착: 09:15  서비스: 10분  출발: 09:25 ││
│ │    - 거리: 8.3km  예상시간: 23분             ││
│ │    🟢 정시 도착 예정                         ││
│ │ ...                                           ││
│ └──────────────────────────────────────────────┘│
├──────────────────────────────────────────────────┤
│ [경로 수정] [운전자 변경] [주문 재배치] [승인]  │
└──────────────────────────────────────────────────┘
```

---

## 📋 개발 단계

### Week 5 (백엔드 개발)

#### Day 1-2: 핵심 서비스 개발
- ✅ DispatchOptimizationService 구현
  - OR-Tools VRP 알고리즘 통합
  - 제약 조건 설정 및 검증
  - 최적화 실행 엔진
- ✅ TrafficIntegrationService 구현
  - Google Maps API 연동
  - 거리/시간 매트릭스 계산
  - Redis 캐싱

#### Day 3-4: REST API 개발
- ✅ 8개 엔드포인트 구현
- ✅ WebSocket 실시간 업데이트
- ✅ 백그라운드 작업 큐 (Celery)
- ✅ API 문서화 (Swagger)

#### Day 5: 테스트 및 최적화
- ✅ 유닛 테스트
- ✅ 통합 테스트
- ✅ 성능 최적화
- ✅ 에러 처리

### Week 6 (프론트엔드 개발)

#### Day 6-7: 메인 대시보드
- ✅ DispatchOptimizationPage 구현
- ✅ 제약 조건 설정 UI
- ✅ 최적화 실행 및 결과 표시
- ✅ 성과 비교 차트

#### Day 8-9: 지도 시각화
- ✅ Leaflet 지도 통합
- ✅ 차량 경로 표시
- ✅ 배송지 마커
- ✅ 실시간 업데이트

#### Day 10: 통합 및 문서화
- ✅ 전체 시스템 통합 테스트
- ✅ 사용자 매뉴얼 작성
- ✅ API 문서화
- ✅ 배포 준비

---

## 🧪 테스트 시나리오

### 시나리오 1: 기본 배차 최적화
```
Given: 45개 주문, 10대 차량
When: 최적화 실행
Then:
  - 8대 차량으로 모든 주문 배차
  - 총 거리 < 500km
  - 총 시간 < 400분
  - 수동 배차 대비 28% 개선
```

### 시나리오 2: 긴급 주문 재배차
```
Given: 기존 최적화 결과 실행 중
When: 긴급 주문 2건 추가
Then:
  - 5분 이내 재최적화 완료
  - 기존 경로 최소 변경 (2개 경로만)
  - 긴급 주문 우선 배치
  - WebSocket 실시간 알림
```

### 시나리오 3: 교통 상황 반영
```
Given: 실시간 교통 정보 활성화
When: 주요 도로 교통 체증
Then:
  - 대체 경로 자동 계산
  - 배송 시간 자동 조정
  - 고객에게 지연 알림
```

---

## 📊 성공 지표

### 시스템 성능
- ✅ 최적화 완료 시간: < 5분 (45개 주문)
- ✅ API 응답 시간: < 200ms
- ✅ 동시 최적화 처리: 5개 이상
- ✅ 재최적화 시간: < 2분

### 비즈니스 성과
- ✅ 배차 처리 시간: -65% (15분 → 5분)
- ✅ 차량 가동률: +23% (65% → 80%)
- ✅ 공차 거리: -35% (28% → 18%)
- ✅ 연료 비용: -18%
- ✅ 일일 배송: +28% (100건 → 128건)

### 사용자 만족도
- ✅ 운전자 만족도: > 4.5/5.0
- ✅ 고객 정시 배송률: > 95%
- ✅ 시스템 사용률: > 90%

---

## 🔧 기술 의존성

### Python 패키지
```txt
ortools>=9.7.2996          # 최적화 알고리즘
googlemaps>=4.10.0         # Google Maps API
celery>=5.3.4              # 백그라운드 작업
redis>=5.0.1               # 캐싱
geopy>=2.4.0               # 지리 정보 처리
```

### npm 패키지
```json
{
  "react-leaflet": "^4.2.1",
  "leaflet": "^1.9.4",
  "recharts": "^2.10.0",
  "date-fns": "^3.0.0"
}
```

### 외부 서비스
- Google Maps Distance Matrix API
- Google Maps Directions API
- Google Maps Geocoding API

---

## 💡 향후 개선 사항

### Phase 2 (추후)
- 머신러닝 기반 배송 시간 예측
- 과거 데이터 기반 교통 패턴 학습
- 운전자 선호도 학습
- 동적 가격 책정 (Dynamic Pricing)

### Phase 3 (추후)
- 드론 배송 통합
- 자율주행 차량 지원
- 블록체인 기반 배송 추적
- IoT 센서 데이터 통합

---

## 📞 문의 및 지원

- **GitHub**: https://github.com/rpaakdi1-spec/3-.git
- **문서**: `/docs/dispatch-optimization`
- **API 문서**: `http://localhost:8000/docs#/Dispatch-Optimization`

---

**상태**: 🚧 개발 진행 중  
**다음 단계**: 백엔드 DispatchOptimizationService 구현

---

*문서 생성일: 2026-02-05*  
*최종 업데이트: 2026-02-05*
