# Phase 3-C: 반복 주문 자동 생성 - 완료 보고서 ✅

## 📅 완료 날짜
2026-02-05

---

## 🎯 Phase 3-C 목표
**운영 효율화를 위한 반복 주문 자동 생성 시스템 구현**

---

## ✅ 완료된 작업

### 1️⃣ 데이터베이스 모델 구현
**파일:** `backend/app/models/recurring_order.py`

#### RecurringOrder 모델
```python
class RecurringOrder(Base):
    __tablename__ = "recurring_orders"
    
    # 기본 정보
    id: int (PK)
    name: str (50자)
    
    # 주기 설정
    frequency: RecurringFrequency  # DAILY, WEEKLY, MONTHLY, CUSTOM
    start_date: date
    end_date: Optional[date]
    weekdays: int  # 비트 플래그 (월:1, 화:2, 수:4, ...)
    custom_days: Optional[str]  # JSON 배열 "[1,15,30]"
    
    # 주문 정보 (Order 테이블과 동일한 구조)
    order_date: date
    temperature_zone: TemperatureZone
    pickup_client_id / pickup_address
    delivery_client_id / delivery_address
    pallet_count: int
    weight_kg, volume_cbm
    product_name, product_code
    pickup_start_time, delivery_start_time 등
    
    # 상태
    is_active: bool (기본값: True)
    last_generated_date: Optional[date]
```

#### 주요 메서드
- **`should_generate_today(target_date=None)`**: 오늘 생성 여부 판단
  - 시작일/종료일 확인
  - 이미 생성했는지 확인
  - 주기별 조건 체크:
    - **DAILY**: 매일 생성
    - **WEEKLY**: 요일 비트 플래그 확인
    - **MONTHLY**: custom_days에 포함된 날짜
    - **CUSTOM**: custom_days에 포함된 일자

---

### 2️⃣ Pydantic 스키마
**파일:** `backend/app/schemas/recurring_order.py`

#### 정의된 스키마
- **RecurringOrderBase**: 공통 필드
- **RecurringOrderCreate**: 생성 요청
- **RecurringOrderUpdate**: 수정 요청 (모든 필드 Optional)
- **RecurringOrderResponse**: 응답 (id, created_at, updated_at 포함)
- **RecurringOrderListResponse**: 페이징 응답 (total, items)

#### 검증 로직
- `end_date >= start_date`
- `weekdays`: 1~127 (월~일 비트 플래그)
- `pickup_client_id` 또는 `pickup_address` 필수
- `delivery_client_id` 또는 `delivery_address` 필수

---

### 3️⃣ CRUD API 구현
**파일:** `backend/app/api/recurring_orders.py`

#### REST API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/recurring-orders/` | 목록 조회 (페이징, is_active 필터) |
| GET | `/recurring-orders/{id}` | 단일 조회 |
| POST | `/recurring-orders/` | 생성 |
| PUT | `/recurring-orders/{id}` | 수정 |
| DELETE | `/recurring-orders/{id}` | 삭제 |
| POST | `/recurring-orders/{id}/toggle` | 활성화/비활성화 토글 |
| **POST** | **`/recurring-orders/generate`** | **수동 주문 생성 (테스트용)** |
| **GET** | **`/recurring-orders/preview`** | **생성 미리보기** |

#### 주요 기능
- **페이징**: `skip`, `limit` 파라미터
- **필터링**: `is_active` (True/False/null)
- **검증**: 거래처/주소 필수, 날짜 유효성
- **에러 핸들링**: 404, 400, 500 with 한글 메시지

---

### 4️⃣ 자동 생성 서비스
**파일:** `backend/app/services/recurring_order_generator.py`

#### RecurringOrderGeneratorService

##### 주요 메서드
**1. `generate_orders_for_date(db, target_date=None)`**
- 특정 날짜(기본값: 오늘)에 생성할 정기 주문들을 실제 Order로 생성
- 흐름:
  ```
  1. 활성화된 정기 주문 조회 (is_active=True)
  2. should_generate_today() 호출로 필터링
  3. 각 정기 주문을 Order 객체로 변환
     - order_number: "REC-{timestamp}-{idx}" 형식 자동 생성
     - order_date: target_date
     - 나머지 필드: 정기 주문에서 복사
  4. DB 저장 (commit)
  5. last_generated_date 업데이트
  6. 결과 반환: {
      'generated': 생성된 주문 수,
      'failed': 실패 수,
      'orders': [Order 리스트],
      'errors': [에러 메시지]
    }
  ```

**2. `preview_generation(db, target_date=None)`**
- 실제 생성하지 않고 미리보기만 제공
- 반환 정보:
  - 정기 주문 ID, 이름
  - 생성될 order_number
  - 상차지/하차지 주소
  - 팔레트, 온도대

---

### 5️⃣ 스케줄러 통합
**파일:** `backend/app/services/scheduler_service.py`

#### SchedulerService
- **라이브러리**: APScheduler (AsyncIOScheduler)
- **스케줄 설정**: 
  - **매일 오전 6시** CronTrigger(hour=6, minute=0)
  - Job ID: `generate_recurring_orders`
  - Job Name: "정기 주문 자동 생성"

#### 실행 로직
```python
async def _generate_recurring_orders():
    1. DB 세션 생성
    2. RecurringOrderGeneratorService.generate_orders_for_date(db) 호출
    3. 결과 로깅 (생성/실패 수, 에러 메시지)
    4. DB 세션 종료
```

#### 모니터링 메서드
- `start()`: 스케줄러 시작
- `stop()`: 스케줄러 중지
- `get_jobs()`: 현재 등록된 작업 목록 반환

---

### 6️⃣ FastAPI 통합
**파일:** `backend/main.py`

#### Lifespan 이벤트 통합
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ...
    await scheduler_service.start()  # 스케줄러 시작
    
    yield
    
    # Shutdown
    await scheduler_service.stop()  # 스케줄러 중지
    ...
```

#### 라우터 등록
```python
app.include_router(
    recurring_orders.router,
    prefix=f"{settings.API_PREFIX}/recurring-orders",
    tags=["Recurring Orders"]
)
```

---

### 7️⃣ 모니터링 API 추가
**파일:** `backend/app/api/monitoring.py`

#### 새 엔드포인트
**GET `/api/v1/monitoring/scheduler/status`**
- 스케줄러 상태 확인
- 등록된 작업 목록
- 다음 실행 시간

**응답 예시:**
```json
{
  "status": "running",
  "jobs": [
    {
      "id": "generate_recurring_orders",
      "name": "정기 주문 자동 생성",
      "next_run_time": "2026-02-06T06:00:00",
      "trigger": "cron[hour='6', minute='0']"
    }
  ],
  "total_jobs": 1
}
```

---

## 📊 API 사용 예시

### 1. 정기 주문 생성
```bash
POST /api/v1/recurring-orders/
{
  "name": "서울-부산 매주 월수금 배송",
  "frequency": "WEEKLY",
  "start_date": "2026-02-05",
  "end_date": "2026-12-31",
  "weekdays": 42,  # 월(2) + 수(8) + 금(32) = 42
  
  "order_date": "2026-02-05",
  "temperature_zone": "REFRIGERATED",
  "pickup_client_id": 1,
  "delivery_client_id": 2,
  "pallet_count": 20,
  "weight_kg": 500.0
}
```

### 2. 수동 주문 생성 (테스트)
```bash
POST /api/v1/recurring-orders/generate?target_date=2026-02-05
# 응답:
{
  "generated": 3,
  "failed": 0,
  "orders": [
    {"order_number": "REC-1738750000-1", "id": 101, ...},
    {"order_number": "REC-1738750000-2", "id": 102, ...}
  ],
  "errors": []
}
```

### 3. 미리보기
```bash
GET /api/v1/recurring-orders/preview?target_date=2026-02-06
# 응답:
{
  "target_date": "2026-02-06",
  "recurring_orders_to_generate": [
    {
      "recurring_order_id": 1,
      "name": "서울-부산 매주 월수금 배송",
      "order_number": "REC-1738836400-1",
      "pickup_address": "서울시 강남구",
      "delivery_address": "부산시 해운대구",
      "pallet_count": 20,
      "temperature_zone": "REFRIGERATED"
    }
  ],
  "count": 1
}
```

### 4. 스케줄러 상태 확인
```bash
GET /api/v1/monitoring/scheduler/status
# 응답:
{
  "status": "running",
  "jobs": [
    {
      "id": "generate_recurring_orders",
      "name": "정기 주문 자동 생성",
      "next_run_time": "2026-02-06T06:00:00",
      "trigger": "cron[hour='6', minute='0']"
    }
  ],
  "total_jobs": 1
}
```

---

## 🔍 테스트 시나리오

### 시나리오 1: 매일 자동 생성
1. 정기 주문 생성 (frequency=DAILY)
2. 다음날 오전 6시까지 대기
3. `/api/v1/orders/` 조회로 자동 생성된 주문 확인

### 시나리오 2: 매주 특정 요일
1. 정기 주문 생성 (frequency=WEEKLY, weekdays=42)  # 월수금
2. `/recurring-orders/preview` 호출로 오늘 생성 여부 확인
3. `/recurring-orders/generate` 수동 실행으로 즉시 테스트

### 시나리오 3: 월별 특정 날짜
1. 정기 주문 생성 (frequency=MONTHLY, custom_days="[1,15,30]")
2. 미리보기로 1일/15일/30일만 생성되는지 확인

### 시나리오 4: 비활성화
1. 정기 주문 생성 후 is_active=False로 변경
2. `/recurring-orders/generate` 호출 → 생성 안됨 확인

---

## 🚀 다음 단계 (Frontend UI)

### Task 4: 프론트엔드 UI 구현 (예정)

#### 4-1. 정기 주문 생성 페이지
**기능:**
- 주문 정보 입력 폼
- 주기 설정 (DAILY/WEEKLY/MONTHLY/CUSTOM)
- 요일 선택 (월~일 체크박스, weekdays 비트 계산)
- 날짜 선택기 (custom_days)
- 상차지/하차지 입력 (거래처 선택 or 주소 직접 입력)

**컴포넌트:**
- `RecurringOrderForm.tsx`
- `FrequencySelector.tsx`
- `WeekdayPicker.tsx`
- `CustomDaysPicker.tsx`

---

#### 4-2. 정기 주문 목록 페이지
**기능:**
- 정기 주문 목록 (페이징, 필터링)
- 활성화/비활성화 토글 버튼
- 수정/삭제 버튼
- 다음 생성 예정일 표시

**컴포넌트:**
- `RecurringOrdersPage.tsx`
- `RecurringOrderTable.tsx`
- `RecurringOrderCard.tsx` (모바일)

**API 호출:**
- GET `/api/v1/recurring-orders/` (목록)
- POST `/api/v1/recurring-orders/{id}/toggle` (활성화 토글)
- DELETE `/api/v1/recurring-orders/{id}` (삭제)

---

#### 4-3. 생성 미리보기 모달
**기능:**
- 특정 날짜 선택
- 생성될 주문 목록 표시
- "지금 생성" 버튼 (수동 실행)

**컴포넌트:**
- `RecurringOrderPreviewModal.tsx`

**API 호출:**
- GET `/api/v1/recurring-orders/preview?target_date=...`
- POST `/api/v1/recurring-orders/generate?target_date=...`

---

#### 4-4. 스케줄러 상태 표시
**위치:** 대시보드 또는 관리자 페이지

**기능:**
- 스케줄러 상태 (running/stopped)
- 다음 실행 시간
- 최근 실행 결과 (생성 수, 실패 수)

**API 호출:**
- GET `/api/v1/monitoring/scheduler/status`

---

## 📝 커밋 히스토리

### Commit 1: d281d4f
**feat: Add recurring orders feature (Phase 3-C)**
- 모델, 스키마, API 엔드포인트 초기 구현

### Commit 2: 32fced6
**feat: Implement recurring order auto-generation scheduler (Phase 3-C)**
- RecurringOrderGeneratorService
- SchedulerService (APScheduler)
- main.py 통합
- 모니터링 API 추가
- 수동 실행 엔드포인트

---

## 🎉 결론

### ✅ 완료된 작업
1. ✅ 반복 주문 테이블 설계 및 모델 구현
2. ✅ Pydantic 스키마 검증
3. ✅ CRUD REST API 구현
4. ✅ 자동 생성 서비스 (RecurringOrderGeneratorService)
5. ✅ 스케줄러 통합 (APScheduler, 매일 오전 6시)
6. ✅ FastAPI Lifespan 통합
7. ✅ 모니터링 API
8. ✅ 수동 실행 엔드포인트 (테스트용)
9. ✅ 미리보기 API

### 🚧 남은 작업
- 프론트엔드 UI 구현 (예정)
- E2E 테스트 (백엔드 자동화)

### 📈 기대 효과
- **자동화**: 반복 주문을 수동으로 입력할 필요 없음
- **시간 절약**: 매일/매주/매월 정기 배송 자동 생성
- **실수 방지**: 수작업 입력 오류 제거
- **운영 효율화**: 관리자는 한 번만 설정하면 자동 실행

---

## 🔗 관련 파일

### Backend
- `backend/app/models/recurring_order.py`
- `backend/app/schemas/recurring_order.py`
- `backend/app/api/recurring_orders.py`
- `backend/app/services/recurring_order_generator.py`
- `backend/app/services/scheduler_service.py`
- `backend/main.py`
- `backend/app/api/monitoring.py`

### Frontend (예정)
- `frontend/src/pages/RecurringOrdersPage.tsx`
- `frontend/src/components/recurring-orders/RecurringOrderForm.tsx`
- `frontend/src/components/recurring-orders/FrequencySelector.tsx`
- `frontend/src/components/recurring-orders/WeekdayPicker.tsx`

---

**작성일:** 2026-02-05  
**작성자:** AI Assistant  
**Phase:** 3-C (운영 효율화)  
**상태:** Backend 완료 ✅, Frontend 예정 🚧
