# 온도대(Temperature Zone) 422 오류 해결

## 📋 문제 분석

### 증상
- **오류 코드**: 422 Unprocessable Entity
- **발생 위치**: POST http://139.150.11.99/api/v1/orders/
- **오류 메시지**: AxiosError: Request failed with status code 422

### 근본 원인 발견 🔥
**프론트엔드와 백엔드의 온도대 Enum 값 불일치!**

#### 백엔드 (backend/app/models/order.py)
```python
class TemperatureZone(str, Enum):
    """온도대 구분"""
    FROZEN = "냉동"       # -18°C ~ -25°C
    REFRIGERATED = "냉장"  # 0°C ~ 6°C
    AMBIENT = "상온"      # 온도 제어 없음
```

#### 프론트엔드 (기존 - 잘못됨)
```typescript
<option value="FROZEN">냉동 (-30°C ~ -18°C)</option>
<option value="REFRIGERATED">냉장 (0°C ~ 6°C)</option>
<option value="AMBIENT">상온</option>
```

**문제**: 프론트엔드가 `"FROZEN"`, `"REFRIGERATED"`, `"AMBIENT"` 같은 영문 값을 보냈지만,  
백엔드는 `"냉동"`, `"냉장"`, `"상온"` 같은 한글 값을 기대했습니다!

---

## ✅ 해결 방법

### 1. OrderModal.tsx 수정
**파일**: `frontend/src/components/orders/OrderModal.tsx`

```typescript
// 변경 전 (잘못됨)
<option value="FROZEN">냉동 (-30°C ~ -18°C)</option>
<option value="REFRIGERATED">냉장 (0°C ~ 6°C)</option>
<option value="AMBIENT">상온</option>

// 변경 후 (올바름)
<option value="냉동">냉동 (-30°C ~ -18°C)</option>
<option value="냉장">냉장 (0°C ~ 6°C)</option>
<option value="상온">상온</option>
```

### 2. OrdersPage.tsx 수정
**파일**: `frontend/src/pages/OrdersPage.tsx`

```typescript
// 변경 전 (복잡한 변환 로직)
{order.temperature_zone === 'FROZEN' ? '냉동' : 
 order.temperature_zone === 'REFRIGERATED' ? '냉장' : 
 order.temperature_zone === 'AMBIENT' ? '상온' : 
 order.cargo_type === 'FROZEN' ? '냉동' : 
 order.cargo_type === 'REFRIGERATED' ? '냉장' : '혼합'}

// 변경 후 (단순화 - 한글 값 그대로 표시)
{order.temperature_zone || order.cargo_type || '-'}
```

### 3. types/index.ts 수정
**파일**: `frontend/src/types/index.ts`

```typescript
// 변경 전
temperature_zone: 'FROZEN' | 'REFRIGERATED' | 'AMBIENT';

// 변경 후
temperature_zone: '냉동' | '냉장' | '상온';  // Backend uses Korean values
```

---

## 🚀 배포 방법

### 자동 배포 (권장)
```bash
cd /root/uvis
git pull origin genspark_ai_developer
chmod +x deploy_temperature_zone_fix.sh
./deploy_temperature_zone_fix.sh
```

### 수동 배포
```bash
cd /root/uvis

# 1. 최신 코드 가져오기
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

# 2. 프론트엔드 재빌드 (캐시 제거)
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend

# 3. 상태 확인
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs frontend --tail=50
```

---

## 🧪 테스트 절차

### 1. 브라우저 캐시 완전 삭제
- Chrome: `Ctrl + Shift + Delete`
- 전체 기간, 캐시 + 인터넷 기록 제거

### 2. 주문 등록 테스트
1. **접속**: http://139.150.11.99/orders
2. **신규 등록** 버튼 클릭
3. **폼 입력**:
   - 주문번호: 자동 생성됨 (예: `ORD-1738217890123`)
   - 주문일자: 오늘 날짜 자동 선택
   - **온도대**: **냉동**, **냉장**, **상온** 중 선택 (한글로 표시됨)
   - 팔레트 수량: `10`
   - 중량: `1000`
   - 거래처 선택 또는 주소 입력
   - 특이사항: `온도 유지 필수`
4. **등록** 버튼 클릭

### 3. 예상 결과
✅ **성공 케이스**:
- 녹색 토스트 메시지: "주문이 등록되었습니다"
- 모달이 자동으로 닫힘
- 주문 목록에 새 주문이 추가됨
- 온도대 열에 **냉동**, **냉장**, 또는 **상온**이 한글로 표시됨

❌ **실패 시 확인사항**:
1. **브라우저 콘솔** (F12 → Console):
   ```
   🚀 Submitting order: { temperature_zone: "냉동", ... }
   ```
   - `temperature_zone` 값이 **한글**인지 확인

2. **Network 탭**:
   - POST `/api/v1/orders/` 요청의 Request Payload 확인
   - Response가 201 Created인지 확인

3. **백엔드 로그**:
   ```bash
   cd /root/uvis
   docker-compose -f docker-compose.prod.yml logs backend --tail=100 | grep -A 20 "POST.*orders"
   ```

---

## 📊 API 예시

### 성공적인 요청 예시
```json
{
  "order_number": "ORD-1738217890123",
  "order_date": "2026-01-30",
  "temperature_zone": "냉동",
  "pallet_count": 10,
  "weight_kg": 1000,
  "pickup_client_id": 1,
  "delivery_client_id": 2,
  "pickup_start_time": "09:00",
  "pickup_end_time": "18:00",
  "delivery_start_time": "09:00",
  "delivery_end_time": "18:00",
  "requested_delivery_date": "2026-01-30",
  "priority": 5,
  "notes": "온도 유지 필수"
}
```

### 성공 응답 (201 Created)
```json
{
  "id": 123,
  "order_number": "ORD-1738217890123",
  "order_date": "2026-01-30",
  "temperature_zone": "냉동",
  "status": "PENDING",
  "pickup_client_name": "서울물류센터",
  "delivery_client_name": "부산물류센터",
  "pallet_count": 10,
  "created_at": "2026-01-30T10:30:00",
  "updated_at": "2026-01-30T10:30:00"
}
```

---

## 🔍 디버깅 가이드

### 여전히 422 오류가 발생하는 경우

#### 1. 브라우저 콘솔 확인
```javascript
// 예상 출력:
🚀 Submitting order: {
  order_number: "ORD-1738217890123",
  order_date: "2026-01-30",
  temperature_zone: "냉동",  // ← 한글 값인지 확인!
  ...
}
```

#### 2. 백엔드 상세 로그 확인
```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml logs backend --tail=200 | grep -A 30 "validation error"
```

#### 3. Pydantic Validation Error 분석
422 오류가 계속되면 백엔드 응답에서 다음 정보 확인:
```json
{
  "detail": [
    {
      "loc": ["body", "temperature_zone"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

이 경우 프론트엔드가 여전히 잘못된 값을 보내고 있다는 의미입니다.

---

## ✅ 완료 체크리스트

- [x] **문제 원인 분석**: 프론트엔드와 백엔드의 Enum 값 불일치
- [x] **OrderModal.tsx 수정**: 온도대 옵션을 한글로 변경
- [x] **OrdersPage.tsx 수정**: 온도대 표시 로직 단순화
- [x] **types/index.ts 수정**: TypeScript 타입 정의 업데이트
- [x] **Git 커밋**: b246d20
- [x] **Git 푸시**: genspark_ai_developer 브랜치
- [x] **배포 스크립트 작성**: deploy_temperature_zone_fix.sh
- [x] **문서 작성**: 이 파일

---

## 📚 관련 파일

1. **수정된 파일**:
   - `frontend/src/components/orders/OrderModal.tsx`
   - `frontend/src/pages/OrdersPage.tsx`
   - `frontend/src/types/index.ts`

2. **참조 파일**:
   - `backend/app/models/order.py` (TemperatureZone Enum 정의)
   - `backend/app/schemas/order.py` (Pydantic 스키마)

3. **배포 도구**:
   - `deploy_temperature_zone_fix.sh`

---

## 🎯 다음 단계

1. **즉시 배포**: 위의 배포 방법 중 하나 실행
2. **테스트 수행**: 주문 등록 플로우 완전 테스트
3. **결과 공유**: 성공 여부 및 스크린샷 공유
4. **추가 이슈**: 다른 문제 발견 시 즉시 보고

---

**작업 완료 일시**: 2026-01-30  
**커밋**: b246d20  
**작업자**: GenSpark AI Developer  
**상태**: ✅ 수정 완료, 배포 대기
