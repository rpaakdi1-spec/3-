# OrderModal 수정사항 배포 가이드

## 📋 문제 분석

### 발생한 문제
- 캘린더에서 날짜 선택 → 주문관리 → 신규등록 시 **오류 발생**
- **원인**: OrderModal 컴포넌트가 백엔드 API와 **완전히 다른 필드**를 사용

### 필드 불일치 사항

#### ❌ 기존 OrderModal (잘못된 필드)
```typescript
{
  client_id: '',           // ❌ 백엔드: pickup_client_id, delivery_client_id
  origin: '',              // ❌ 백엔드: pickup_address
  destination: '',         // ❌ 백엔드: delivery_address
  cargo_type: '',          // ❌ 백엔드: temperature_zone
  pickup_time: '',         // ❌ 백엔드: pickup_start_time, pickup_end_time
  delivery_deadline: '',   // ❌ 백엔드: requested_delivery_date
  temperature_min: '',     // ❌ 백엔드에 없음
  temperature_max: '',     // ❌ 백엔드에 없음
  special_requirements: '' // ❌ 백엔드: notes
}
```

#### ✅ 수정된 OrderModal (올바른 필드)
```typescript
{
  order_number: '',              // ✅ 주문번호 (필수)
  order_date: '',                // ✅ 주문일자 (필수)
  temperature_zone: '',          // ✅ 온도대: FROZEN, REFRIGERATED, AMBIENT
  pickup_client_id: '',          // ✅ 상차 거래처 ID (거래처 선택 모드)
  delivery_client_id: '',        // ✅ 하차 거래처 ID (거래처 선택 모드)
  pickup_address: '',            // ✅ 상차 주소 (주소 직접 입력 모드)
  pickup_address_detail: '',     // ✅ 상차 상세주소
  delivery_address: '',          // ✅ 하차 주소 (주소 직접 입력 모드)
  delivery_address_detail: '',   // ✅ 하차 상세주소
  pallet_count: '',              // ✅ 팔레트 수량 (필수)
  weight_kg: '',                 // ✅ 중량
  pickup_start_time: '',         // ✅ 상차 시작시간 (HH:MM)
  pickup_end_time: '',           // ✅ 상차 종료시간
  delivery_start_time: '',       // ✅ 하차 시작시간
  delivery_end_time: '',         // ✅ 하차 종료시간
  requested_delivery_date: '',   // ✅ 희망 배송일
  priority: 5,                   // ✅ 우선순위 (1-10)
  notes: ''                      // ✅ 특이사항
}
```

## 🔧 수정 내용

### 1. 필드 구조 완전 재구성
- 백엔드 API 스키마(`/backend/app/schemas/order.py`)에 맞춰 모든 필드 재작성
- 필수 필드: `order_number`, `order_date`, `temperature_zone`, `pallet_count`
- 선택적 필드: `weight_kg`, `requested_delivery_date`, `priority`, `notes`

### 2. 거래처/주소 입력 방식 분리
**탭 방식으로 2가지 입력 모드 제공:**

#### 모드 1: 거래처 선택 (기본)
- 상차/하차 거래처를 드롭다운에서 선택
- `pickup_client_id`, `delivery_client_id` 사용

#### 모드 2: 주소 직접 입력
- 주소를 직접 입력하면 네이버 지오코딩 자동 수행
- `pickup_address`, `delivery_address` 사용

### 3. UI 개선사항
- **기본 정보**: 주문번호, 주문일자, 희망배송일, 온도대, 팔레트, 중량, 우선순위
- **상차/하차 정보**: 탭으로 거래처 선택 vs 주소 직접 입력 전환
- **시간 정보**: 상차/하차 시작/종료 시간 (각 4개 입력 필드)
- **특이사항**: notes 필드로 통합

### 4. 자동 입력 기능
- 주문번호: `ORD-{timestamp}` 자동 생성
- 주문일자/희망배송일: 오늘 날짜 자동 입력
- 상차/하차 시간: 09:00 ~ 18:00 기본값
- 우선순위: 5 (보통) 기본값

## 🚀 배포 절차

### PuTTY에서 실행할 명령어

```bash
# 1. 최신 코드 가져오기
cd /root/uvis
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

# 2. 프론트엔드 리빌드 (캐시 삭제 포함)
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend

# 3. 상태 확인
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs frontend --tail=50

# 4. 완료!
echo "✅ 배포 완료! 브라우저에서 테스트하세요."
```

### 배포 후 테스트 순서

#### 1단계: 브라우저 캐시 삭제
- **Chrome**: Ctrl+Shift+Delete → "전체 기간" → "캐시된 이미지 및 파일" 체크 → 삭제
- **또는 시크릿 모드**: Ctrl+Shift+N

#### 2단계: 캘린더에서 주문 등록 테스트
1. http://139.150.11.99/calendar 접속
2. 다음 날짜 클릭 (빈 날짜)
3. "주문 등록 페이지로 이동" 버튼 클릭
4. 주문관리 페이지로 이동 확인

#### 3단계: 주문 등록 폼 테스트
1. "신규 등록" 버튼 클릭
2. **기본 정보 입력:**
   - 주문번호: 자동 생성된 값 확인 (예: ORD-1738216789123)
   - 주문일자: 오늘 날짜 확인
   - 희망 배송일: 선택
   - 온도대: FROZEN, REFRIGERATED, AMBIENT 중 선택
   - 팔레트 수량: 10 입력
   - 중량(kg): 1000 입력 (선택)
   - 우선순위: 보통(5) 확인

3. **상차/하차 정보 입력 (모드 1: 거래처 선택):**
   - "거래처 선택" 탭 클릭 (기본값)
   - 상차 거래처: 드롭다운에서 선택
   - 하차 거래처: 드롭다운에서 선택

4. **또는 (모드 2: 주소 직접 입력):**
   - "주소 직접 입력" 탭 클릭
   - 상차 주소: "서울시 강남구 테헤란로 427" 입력
   - 상차 상세주소: "1층" 입력
   - 하차 주소: "부산시 해운대구 센텀중앙로 48" 입력
   - 하차 상세주소: "2층 창고" 입력

5. **시간 정보:**
   - 상차 시작: 09:00 (기본값 확인)
   - 상차 종료: 18:00
   - 하차 시작: 09:00
   - 하차 종료: 18:00

6. **특이사항:**
   - "온도 유지 필수, 조심히 취급해주세요" 입력

7. **등록 버튼 클릭**

#### 4단계: 성공 확인
- ✅ "주문이 등록되었습니다" 토스트 메시지
- ✅ 주문 목록에 새 주문 추가
- ✅ 주문 상세 정보 확인

#### 5단계: 오류 발생 시
- **브라우저 콘솔 열기**: F12 → Console 탭
- **네트워크 탭 확인**: F12 → Network 탭 → POST /api/v1/orders/ 요청 확인
- **오류 메시지 공유**: 빨간색 오류 메시지 캡처

## 📊 예상 API 요청 예시

### POST /api/v1/orders/ (거래처 선택 모드)
```json
{
  "order_number": "ORD-1738216789123",
  "order_date": "2026-01-30",
  "temperature_zone": "FROZEN",
  "pickup_client_id": 1,
  "delivery_client_id": 2,
  "pallet_count": 10,
  "weight_kg": 1000.0,
  "pickup_start_time": "09:00",
  "pickup_end_time": "18:00",
  "delivery_start_time": "09:00",
  "delivery_end_time": "18:00",
  "requested_delivery_date": "2026-01-31",
  "priority": 5,
  "notes": "온도 유지 필수"
}
```

### POST /api/v1/orders/ (주소 직접 입력 모드)
```json
{
  "order_number": "ORD-1738216789124",
  "order_date": "2026-01-30",
  "temperature_zone": "REFRIGERATED",
  "pickup_address": "서울시 강남구 테헤란로 427",
  "pickup_address_detail": "1층",
  "delivery_address": "부산시 해운대구 센텀중앙로 48",
  "delivery_address_detail": "2층 창고",
  "pallet_count": 20,
  "weight_kg": 2000.0,
  "pickup_start_time": "10:00",
  "pickup_end_time": "12:00",
  "delivery_start_time": "14:00",
  "delivery_end_time": "16:00",
  "requested_delivery_date": "2026-01-31",
  "priority": 3,
  "notes": "조심히 취급해주세요"
}
```

## ✅ 커밋 및 PR 정보

### Git Commit
- **Branch**: genspark_ai_developer
- **Commit Hash**: 772e1b8
- **Commit Message**: 
  ```
  fix(frontend): OrderModal 필드를 백엔드 API 스키마와 일치하도록 수정
  
  - 기존 client_id, origin, destination 등 잘못된 필드를 order_number, pickup_client_id, delivery_client_id 등으로 변경
  - 거래처 선택 모드와 주소 직접 입력 모드를 탭으로 구분
  - 온도대(temperature_zone), 팔레트 수량(pallet_count), 중량(weight_kg) 필드 추가
  - 상차/하차 시간(pickup_start_time, delivery_start_time) 필드 추가
  - 희망 배송일(requested_delivery_date), 우선순위(priority), 특이사항(notes) 필드 추가
  - 캘린더에서 주문 등록 시 발생하던 필드 불일치 오류 해결
  ```

### Pull Request
- **URL**: https://github.com/rpaakdi1-spec/3-/pull/3
- **Status**: Updated (2026-01-30)
- **From**: genspark_ai_developer → main

## 🔍 문제 해결 체크리스트

### 오류가 계속 발생하면 확인할 사항:

#### 1. 백엔드 API 확인
```bash
# 주문 생성 API 테스트
curl -X POST http://139.150.11.99:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "TEST-001",
    "order_date": "2026-01-30",
    "temperature_zone": "FROZEN",
    "pickup_client_id": 1,
    "delivery_client_id": 2,
    "pallet_count": 10,
    "priority": 5
  }'
```

#### 2. 프론트엔드 빌드 확인
```bash
# 빌드 로그 확인
docker-compose -f docker-compose.prod.yml logs frontend --tail=200

# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

#### 3. 거래처 데이터 확인
```bash
# 거래처 목록 확인
curl http://139.150.11.99:8000/api/v1/clients/
```

#### 4. 네이버 지오코딩 확인
```bash
# 지오코딩 API 테스트
curl -X POST http://139.150.11.99:8000/api/v1/naver-map/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울시 강남구 테헤란로 427"}'
```

## 📝 참고 사항

### 백엔드 스키마 파일
- `/backend/app/schemas/order.py`: OrderCreate, OrderUpdate 스키마 정의
- `/backend/app/api/orders.py`: 주문 생성/수정 API 엔드포인트

### 프론트엔드 파일
- `/frontend/src/components/orders/OrderModal.tsx`: 주문 등록/수정 모달 (✅ 수정 완료)
- `/frontend/src/pages/OrdersPage.tsx`: 주문 관리 페이지
- `/frontend/src/pages/OrderCalendarPage.tsx`: 캘린더 페이지

### API 문서
- http://139.150.11.99:8000/docs
- POST /api/v1/orders/ - 주문 생성
- GET /api/v1/orders/ - 주문 목록 조회
- PUT /api/v1/orders/{order_id} - 주문 수정

## 🎯 다음 단계

1. **즉시 실행**: 위의 PuTTY 명령어를 복사하여 실행
2. **브라우저 테스트**: 캐시 삭제 후 주문 등록 테스트
3. **결과 공유**: 
   - ✅ 성공: "등록 완료!" 스크린샷
   - ❌ 오류: 콘솔 오류 메시지 + 네트워크 탭 캡처

---

**작성일**: 2026-01-30  
**작성자**: GenSpark AI Developer  
**상태**: ✅ 코드 수정 완료, 배포 대기 중
