# 제거/유지 필드 완전 정리 문서

## 📋 작업 완료 요약

### ✅ 완전히 제거된 필드

#### 1. 주문(Order) 관련
| 필드명 | 영문 | 제거 이유 |
|--------|------|-----------|
| 주문번호 | order_number | 자동 생성 불필요 |
| 주문 코드 | order_code | 중복 식별자 |
| ORD-YYYYMMDD-XXX | ORD- pattern | 생성 로직 제거 |

**제거된 파일:**
- ✅ `frontend/src/components/orders/OrderModal.tsx`
  - Line 250: `placeholder="ORD-20260130-001"` 제거
  - order_number 관련 Input 필드 제거
- ✅ `frontend/src/components/OrderUpload.tsx`
  - Line 165: `generateOrderNumber()` 함수 제거
  - order_code 필드 제거
  - order_number 필드 제거
- ✅ `frontend/src/pages/OrdersPage.tsx`
  - order_number 컬럼 제거
- ✅ `frontend/src/pages/OptimizationPage.tsx`
  - Line 92, 100: order_number 테스트 데이터 제거
- ✅ `frontend/src/types/index.ts`
  - order_number, order_code 타입 제거
- ✅ `backend/app/models/order.py`
  - order_number 컬럼 제거
- ✅ `backend/app/schemas/order.py`
  - order_number 필드 제거
- ✅ `backend/app/api/orders.py`
  - order_number 참조 제거

---

#### 2. 거래처(Client) 관련
| 필드명 | 영문 | 제거 이유 |
|--------|------|-----------|
| 거래처 코드 | client_code | 불필요한 식별자 |

**제거된 파일:**
- ✅ `frontend/src/components/ClientUpload.tsx`
  - client_code 필드 제거
- ✅ `frontend/src/pages/ClientsPage.tsx`
  - client_code 컬럼 제거
- ✅ `frontend/src/pages/ClientDistributionChart.tsx`
  - client_code 참조 제거
- ✅ `backend/app/models/client.py`
  - code 컬럼 제거
- ✅ `backend/app/schemas/client.py`
  - code 필드 제거
- ✅ `backend/app/api/clients.py`
  - client.code 참조 제거
  - 지오코딩 로그: `client.code` → `client.name`

---

#### 3. 차량(Vehicle) 관련
| 필드명 | 영문 | 제거 이유 |
|--------|------|-----------|
| 최대 적재중량(kg) | max_weight_kg | 팔레트 기반으로 통일 |

**제거된 파일:**
- ✅ `frontend/src/components/VehicleUpload.tsx`
  - max_weight_kg 필드 제거
  - Line 165: max_weight_kg 초기값 제거
- ✅ `frontend/src/pages/VehiclesPage.tsx`
  - Line 732-733: max_weight_kg Input 제거
- ✅ `backend/app/models/vehicle.py`
  - max_weight_kg 컬럼 제거
- ✅ `backend/app/schemas/vehicle.py`
  - max_weight_kg 필드 제거
- ✅ `backend/app/api/vehicles.py`
  - Line 59: 'max_weight_kg' 응답 제거
  - Line 300: max_weight_kg=5000.0 제거
- ✅ `backend/app/services/cvrptw_service.py`
  - Line 50, 135, 640: max_weight_kg 로직 제거
- ✅ `backend/app/services/dispatch_optimization_service.py`
  - Line 41, 367: max_weight_kg 검증 제거
- ✅ `backend/app/services/excel_template_service.py`
  - Line 62: '최대중량(kg)' 템플릿 제거
- ✅ `backend/app/services/ai_chat_service.py`
  - Line 730: 'max_weight_kg' 제거

---

### ✅ 유지되는 필드

#### 1. 주문(Order) - 핵심 필드
```typescript
interface Order {
  id: number;                      // 자동 생성 ID
  order_date: string;              // ✅ 주문일자
  temperature_zone: string;        // ✅ 온도대 (냉동/냉장/상온)
  pickup_client_id: number;        // ✅ 픽업 거래처
  delivery_client_id: number;      // ✅ 배송 거래처
  pallet_count: number;            // ✅ 팔레트 수
  pickup_start_time?: string;      // 상차 시작 시간
  pickup_end_time?: string;        // 상차 종료 시간
  delivery_start_time?: string;    // 하차 시작 시간
  delivery_end_time?: string;      // 하차 종료 시간
  item_name?: string;              // 품목명
  notes?: string;                  // 비고
}
```

#### 2. 차량(Vehicle) - 팔레트 기반 용량
```typescript
interface Vehicle {
  id: number;                      // 자동 생성 ID
  vehicle_number: string;          // ✅ 차량번호
  model: string;                   // ✅ 차종
  type: string;                    // ✅ 타입 (냉동/냉장/겸용/상온)
  max_pallet_capacity: number;     // ✅ 최대 팔레트 수 ⭐
  max_volume_cbm: number;          // ✅ 최대 용적(CBM) ⭐
  cargo_length_m: number;          // ✅ 적재함 길이(m) ⭐
  temperature_range?: string;      // 온도 범위
  forklift_skill?: boolean;        // 지게차 운전 가능
  warehouse_address?: string;      // 차고지 주소
  uvis_terminal_id?: string;       // UVIS 단말기 ID
  driver_name?: string;            // 기사명
  driver_phone?: string;           // 기사 연락처
}
```

#### 3. 거래처(Client) - 간소화
```typescript
interface Client {
  id: number;                      // 자동 생성 ID
  name: string;                    // ✅ 거래처명
  phone?: string;                  // 연락처
  address: string;                 // ✅ 주소
  detailed_address?: string;       // 상세주소
  latitude?: number;               // 위도 (자동 지오코딩)
  longitude?: number;              // 경도 (자동 지오코딩)
}
```

---

## 🎯 UI에서 확인해야 할 사항

### 주문 등록 모달
```
✅ 보여야 하는 필드 (순서대로):
1. 주문일자 *
2. 온도대 *
3. 픽업 거래처 *
4. 배송 거래처 *
5. 팔레트 수 *
6. 상차 시작/종료 시간
7. 하차 시작/종료 시간
8. 품목명
9. 비고

❌ 절대 보이면 안 되는 것:
- ORD-20260130-001
- 주문 코드
- 주문번호
- 주문 번호 자동 생성 관련 텍스트
```

### 차량 등록 폼
```
✅ 보여야 하는 필드:
- 차량번호 *
- 차종 *
- 타입 (냉동/냉장/겸용/상온) *
- 최대 팔레트 수 *
- 최대 용적(CBM) *
- 적재함 길이(m) *
- 온도 범위
- 지게차 운전 가능 여부
- 차고지 주소
- UVIS 단말기 ID
- 기사명
- 기사 연락처

❌ 절대 보이면 안 되는 것:
- 최대 적재중량(kg)
- max_weight_kg
```

### 거래처 등록 폼
```
✅ 보여야 하는 필드:
- 거래처명 *
- 연락처
- 주소 *
- 상세주소

❌ 절대 보이면 안 되는 것:
- 거래처 코드
- client_code
```

---

## 🔄 시스템 동작 방식 변경

### 이전 (Before)
```
주문: order_number(ORD-YYYYMMDD-XXX) 자동 생성
거래처: client_code 수동 입력
차량: max_weight_kg 기반 적재 계산
```

### 현재 (After)
```
주문: id(숫자) 자동 생성, order_number 없음
거래처: id(숫자) 자동 생성, code 없음
차량: 팔레트 기반 적재 계산 (max_pallet_capacity, max_volume_cbm, cargo_length_m)
```

---

## 📊 데이터베이스 스키마 변경 (예정)

### 마이그레이션 필요 사항
```sql
-- orders 테이블
ALTER TABLE orders DROP COLUMN IF EXISTS order_number;

-- clients 테이블
ALTER TABLE clients DROP COLUMN IF EXISTS code;
DROP INDEX IF EXISTS ix_clients_code;

-- vehicles 테이블
ALTER TABLE vehicles DROP COLUMN IF EXISTS max_weight_kg;
```

**주의:** 
- 이미 코드는 수정 완료
- DB 마이그레이션은 선택 사항 (기존 데이터가 있다면)
- 새로운 데이터는 제거된 필드를 사용하지 않음

---

## ✅ 검증 완료 체크리스트

### Code Level
- [x] Frontend: order_number 제거 ✅
- [x] Frontend: order_code 제거 ✅
- [x] Frontend: ORD- 패턴 제거 ✅
- [x] Frontend: client_code 제거 ✅
- [x] Frontend: max_weight_kg 제거 ✅
- [x] Backend: order_number 제거 ✅
- [x] Backend: client.code 제거 ✅
- [x] Backend: max_weight_kg 제거 ✅

### File Level
- [x] OrderModal.tsx ✅
- [x] OrderUpload.tsx ✅
- [x] OrdersPage.tsx ✅
- [x] OptimizationPage.tsx ✅
- [x] VehicleUpload.tsx ✅
- [x] VehiclesPage.tsx ✅
- [x] ClientUpload.tsx ✅
- [x] ClientsPage.tsx ✅
- [x] All backend models/schemas/apis ✅

### Deployment Level
- [x] Git commit ✅
- [x] Docker rebuild (no-cache) ✅
- [x] Container restart ✅
- [x] Health check ✅

### Browser Level
- [ ] 브라우저 캐시 삭제 ⚠️ **← 사용자가 해야 함!**
- [ ] 시크릿 모드 테스트 ⚠️ **← 사용자가 해야 함!**
- [ ] UI 확인 ⚠️ **← 사용자가 해야 함!**

---

## 🎉 결론

**모든 코드 수정과 배포는 완료되었습니다!**

남은 것은 **브라우저 캐시 삭제**뿐입니다.

### 지금 바로 할 일:
1. ✅ 브라우저 완전히 닫기
2. ✅ Ctrl + Shift + Delete → 캐시 삭제
3. ✅ 시크릿 모드로 열기 (Ctrl + Shift + N)
4. ✅ http://139.150.11.99/orders 접속
5. ✅ 주문 등록 버튼 클릭
6. ✅ ORD-20260130-001 없는지 확인!

**성공을 기원합니다! 🚀**
