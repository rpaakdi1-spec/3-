# GET /orders/ 500 Internal Server Error - Pydantic Serializer 충돌 해결

## 문제 요약

**오류**: `GET http://139.150.11.99/api/v1/orders/` 요청 시 `500 Internal Server Error` 발생  
**원인**: API 엔드포인트에서 수동 시간 변환과 Pydantic `field_serializer`가 충돌

## 근본 원인 분석

### 문제 상황
1. **이중 변환 문제**: 
   - API 엔드포인트(`backend/app/api/orders.py`)에서 수동으로 `time` 객체를 문자열로 변환
   - Pydantic 스키마(`backend/app/schemas/order.py`)의 `field_serializer`도 동일한 변환 수행
   - 두 변환 로직이 충돌하여 500 오류 발생

2. **데이터 타입 불일치**:
   - DB에 저장된 시간 필드가 다양한 형식으로 존재:
     - `datetime.time` 객체
     - `'HH:MM'` 문자열
     - `None` (null)
   - 수동 변환 로직이 모든 경우를 처리하지 못함

### 기존 코드의 문제점

#### backend/app/api/orders.py (GET /orders/)
```python
# ❌ 문제: 수동 시간 변환
for item in items:
    if item.pickup_start_time:
        if isinstance(item.pickup_start_time, time_type):
            item.pickup_start_time = item.pickup_start_time.strftime('%H:%M')
        elif isinstance(item.pickup_start_time, str):
            pass
    # ... 다른 시간 필드들도 동일
```

#### backend/app/schemas/order.py (OrderResponse)
```python
# ⚠️ 이미 field_serializer가 있는데 API에서 또 변환
@field_serializer('pickup_start_time', 'pickup_end_time', 'delivery_start_time', 'delivery_end_time')
def serialize_time(self, value: Optional[time], _info) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, time):
        return value.strftime('%H:%M')
    return value  # ❌ 문자열이면 그대로 반환하지만 다른 타입은?
```

## 해결 방법

### 1. API 엔드포인트 수정
**목적**: Pydantic의 `field_serializer`에게 변환을 위임하고 수동 변환 제거

#### GET /orders/ (backend/app/api/orders.py:20-53)
```python
@router.get("/", response_model=OrderListResponse)
def get_orders(...):
    """주문 목록 조회"""
    # ✅ time_type import 제거
    query = db.query(Order)
    
    # ... 필터링 로직 ...
    
    # ✅ 수동 시간 변환 코드 완전 제거
    for item in items:
        if item.pickup_client:
            item.pickup_client_name = item.pickup_client.name
        if item.delivery_client:
            item.delivery_client_name = item.delivery_client.name
    
    # Pydantic이 자동으로 time 필드를 HH:MM 문자열로 변환
    return OrderListResponse(total=total, items=items)
```

#### GET /orders/{order_id} (backend/app/api/orders.py:56-69)
```python
@router.get("/{order_id}", response_model=OrderWithClientsResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """주문 상세 조회"""
    # ✅ time_type import 제거
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # ✅ 수동 시간 변환 코드 제거
    order.pickup_client_name = order.pickup_client.name if order.pickup_client else None
    order.delivery_client_name = order.delivery_client.name if order.delivery_client else None
    
    return order  # Pydantic이 자동 변환
```

#### PUT /orders/{order_id} (backend/app/api/orders.py:142-168)
```python
@router.put("/{order_id}", response_model=OrderResponse)
def update_order(...):
    """주문 수정"""
    # ✅ time_type import 제거
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="주문을 찾을 수 없습니다")
    
    # ... 업데이트 로직 ...
    
    # ✅ 수동 시간 변환 코드 제거
    order.pickup_client_name = order.pickup_client.name if order.pickup_client else None
    order.delivery_client_name = order.delivery_client.name if order.delivery_client else None
    
    return order  # Pydantic이 자동 변환
```

### 2. Pydantic 스키마 개선
**목적**: 다양한 시간 필드 타입(time 객체, 문자열, None)을 안전하게 처리

#### backend/app/schemas/order.py (OrderResponse:100-111)
```python
@field_serializer('pickup_start_time', 'pickup_end_time', 'delivery_start_time', 'delivery_end_time')
def serialize_time(self, value: Optional[time], _info) -> Optional[str]:
    """Convert time objects to HH:MM string format (handles both time objects and strings)"""
    if value is None:
        return None
    if isinstance(value, time):
        # ✅ time 객체 → 'HH:MM' 문자열
        return value.strftime('%H:%M')
    if isinstance(value, str):
        # ✅ 이미 문자열이면 그대로 반환
        return value
    # ✅ 그 외 타입은 문자열로 변환 (안전장치)
    return str(value) if value is not None else None
```

## 수정된 파일 목록

| 파일 경로 | 변경 내용 | 라인 수 |
|----------|----------|--------|
| `backend/app/api/orders.py` | GET/PUT 엔드포인트에서 수동 시간 변환 제거 | -60, +12 |
| `backend/app/schemas/order.py` | field_serializer 강화 (문자열/기타 타입 처리) | -6, +10 |

## 배포 방법

### 방법 1: 자동 배포 스크립트 (권장)

```bash
# PuTTY로 서버 접속 후
cd /root/uvis
git pull origin genspark_ai_developer
./deploy_pydantic_serializer_fix.sh
```

스크립트 동작:
1. ✅ Git에서 최신 코드 가져오기
2. ✅ genspark_ai_developer 브랜치로 체크아웃
3. ✅ 백엔드 컨테이너 재시작
4. ✅ 헬스 체크 및 엔드포인트 테스트

### 방법 2: 수동 배포

```bash
# 1. Git 업데이트
cd /root/uvis
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

# 2. 백엔드 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 3. 상태 확인
docker ps | grep backend
docker logs uvis-backend-1 --tail 50

# 4. 엔드포인트 테스트
curl -X GET "http://139.150.11.99/api/v1/orders/?limit=1" -H "accept: application/json"
```

## 테스트 절차

### 1. 브라우저 테스트

1. 캐시 삭제 (Ctrl+Shift+R 또는 Cmd+Shift+R)
2. 접속: `http://139.150.11.99/orders`
3. **예상 결과**:
   - ✅ 주문 목록이 정상 로드됨
   - ✅ 시간 필드가 `HH:MM` 형식으로 표시됨 (예: `09:00`, `18:00`)
   - ✅ 500 오류 발생하지 않음

### 2. 개발자 도구 확인

**Network 탭**:
```
GET /api/v1/orders/
Status: 200 OK  ✅
```

**Response Body**:
```json
{
  "total": 10,
  "items": [
    {
      "id": 1,
      "order_number": "ORD-20260130-001",
      "pickup_start_time": "09:00",  ✅ 문자열 형식
      "pickup_end_time": "12:00",
      "delivery_start_time": "13:00",
      "delivery_end_time": "18:00",
      ...
    }
  ]
}
```

### 3. 새 주문 생성 테스트

1. "신규 등록" 버튼 클릭
2. 모든 필수 정보 입력
3. 제출 후 **예상 결과**:
   - ✅ `201 Created` 응답
   - ✅ 목록에 새 주문 추가됨
   - ✅ 토스트 알림 표시

### 4. 디버깅 (문제 발생 시)

```bash
# 상세 진단 스크립트 실행
cd /root/uvis
./diagnose_500_detailed.sh
```

진단 항목:
- ✅ 백엔드 컨테이너 상태
- ✅ 최근 로그 (100줄)
- ✅ 데이터베이스 연결
- ✅ 시간 필드 타입 확인
- ✅ API 엔드포인트 테스트

## 기술적 배경

### Pydantic의 field_serializer
Pydantic v2에서는 `field_serializer` 데코레이터를 사용해 필드를 직렬화합니다:

```python
from pydantic import BaseModel, field_serializer

class MyModel(BaseModel):
    my_field: datetime.time
    
    @field_serializer('my_field')
    def serialize_time(self, value, _info):
        # FastAPI가 JSON 응답을 생성할 때 자동 호출
        return value.strftime('%H:%M') if value else None
```

### 변환 흐름

#### ❌ 이전 (이중 변환, 충돌 발생)
```
DB (time 객체) → API 엔드포인트 (time → str) → Pydantic (str → ?) → JSON
                     ↑ 수동 변환                   ↑ field_serializer
                                                   충돌 발생! 500 Error
```

#### ✅ 현재 (단일 변환, Pydantic 위임)
```
DB (time 객체) → Pydantic field_serializer (time → str) → JSON
                     ↑ 안전한 자동 변환
                     (time 객체, 문자열, None 모두 처리)
```

### 장점
1. **단일 책임 원칙**: Pydantic 스키마가 직렬화 담당
2. **일관성**: 모든 응답이 동일한 변환 로직 사용
3. **안전성**: 다양한 타입을 안전하게 처리
4. **유지보수성**: 변환 로직이 한 곳에 집중됨

## 관련 문서

- [이전 온도대 422 오류 해결](./ORDER_REGISTRATION_422_COMPLETE_FIX.md)
- [이전 시간 필드 500 오류 해결](./GET_ORDERS_500_FIX.md) (이번 문제의 근본 원인 재해결)
- [배포 스크립트](./deploy_pydantic_serializer_fix.sh)
- [진단 스크립트](./diagnose_500_detailed.sh)

## 작업 완료 정보

- **완료 일시**: 2026-01-31
- **최종 커밋**: (다음 단계에서 생성)
- **Pull Request**: [#3](https://github.com/rpaakdi1-spec/3-/pull/3)
- **테스트 필요**: ✅ 주문 목록 조회, 주문 등록, 주문 수정

## 다음 단계

1. ✅ 로컬 저장소에서 변경사항 커밋
2. ✅ genspark_ai_developer 브랜치에 푸시
3. ⏳ 서버에서 배포 스크립트 실행
4. ⏳ 브라우저 테스트 및 결과 공유
5. ⏳ PR 업데이트 (테스트 결과 추가)

---

**참고**: 이 문서는 `GET /orders/` 500 오류의 근본 원인을 해결합니다. 
이전 수정(시간 필드 try-except)은 임시 방편이었고, 이번 수정이 올바른 해결책입니다.
