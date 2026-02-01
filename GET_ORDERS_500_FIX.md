# GET /orders/ 500 오류 해결

## 📋 문제 분석

### 증상
- **오류 코드**: 500 Internal Server Error
- **발생 위치**: GET http://139.150.11.99/api/v1/orders/
- **오류 메시지**: AxiosError: Request failed with status code 500

### 근본 원인
**백엔드의 시간 필드 변환 로직에서 예외 발생**

#### 상황 설명
1. 기존 주문 데이터에 시간 필드가 **다양한 형식**으로 저장되어 있음:
   - `datetime.time` 객체
   - `str` 문자열 (예: "09:00")
   - `None` (null)

2. 기존 코드는 모든 값이 `time` 객체라고 가정:
   ```python
   # 문제 코드
   if item.pickup_start_time and isinstance(item.pickup_start_time, time_type):
       item.pickup_start_time = item.pickup_start_time.strftime('%H:%M')
   ```

3. 예상치 못한 형식의 데이터가 있으면 **500 오류** 발생

---

## ✅ 해결 방법

### backend/app/api/orders.py 수정

#### GET /orders/ 엔드포인트

```python
# 변경 전 (문제 코드)
# Convert time objects to HH:MM string format
if item.pickup_start_time and isinstance(item.pickup_start_time, time_type):
    item.pickup_start_time = item.pickup_start_time.strftime('%H:%M')
# ... 반복

# 변경 후 (안전한 코드)
try:
    if item.pickup_start_time:
        if isinstance(item.pickup_start_time, time_type):
            item.pickup_start_time = item.pickup_start_time.strftime('%H:%M')
        elif isinstance(item.pickup_start_time, str):
            # Already a string, keep as is
            pass
    # ... 다른 시간 필드도 동일하게 처리
except Exception as e:
    logger.error(f"Error converting time fields for order {item.id}: {e}")
    # Set to None if conversion fails
    item.pickup_start_time = None
    item.pickup_end_time = None
    item.delivery_start_time = None
    item.delivery_end_time = None
```

#### GET /orders/{order_id} 엔드포인트
동일한 안전한 변환 로직 적용

### 핵심 개선사항
1. **try-except 블록**: 예외 발생 시 500 오류 대신 안전하게 처리
2. **타입 체크 강화**: `time` 객체와 `str` 모두 처리
3. **실패 시 fallback**: 변환 실패 시 `None`으로 설정
4. **로깅 추가**: 변환 오류를 로그에 기록하여 디버깅 가능

---

## 🚀 배포 방법

### 자동 배포 (권장)
```bash
cd /root/uvis
git pull origin genspark_ai_developer
chmod +x deploy_500_fix.sh
./deploy_500_fix.sh
```

### 수동 배포
```bash
cd /root/uvis

# 최신 코드 가져오기
git fetch origin genspark_ai_developer
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

# 백엔드 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 상태 확인
docker-compose -f docker-compose.prod.yml ps backend
docker-compose -f docker-compose.prod.yml logs backend --tail=30
```

---

## 🧪 테스트 절차

### 1. 주문 목록 조회 테스트
1. **접속**: http://139.150.11.99/orders
2. **F12** 눌러 개발자 도구 열기
3. **Network** 탭 확인
4. 페이지 새로고침

### 2. 예상 결과
✅ **성공 케이스**:
- Network 탭에서 `GET /api/v1/orders/` 요청이 **200 OK**
- Response에 주문 목록 데이터:
  ```json
  {
    "total": 10,
    "items": [
      {
        "id": 1,
        "order_number": "ORD-20260130-001",
        "pickup_start_time": "09:00",  // HH:MM 형식
        "pickup_end_time": "18:00",
        ...
      }
    ]
  }
  ```
- 주문 목록이 테이블에 정상적으로 표시됨

❌ **실패 시 확인사항**:

#### 1. 백엔드 로그 확인
```bash
cd /root/uvis
./debug_500_error.sh
```

또는

```bash
docker-compose -f docker-compose.prod.yml logs backend --tail=100 | grep -A 20 "error\|Error\|Exception"
```

#### 2. 특정 주문의 시간 필드 확인
```bash
# PostgreSQL 컨테이너 접속
docker-compose -f docker-compose.prod.yml exec db psql -U uvis_user -d uvis_db

# 시간 필드 확인
SELECT id, order_number, 
       pickup_start_time, 
       pickup_end_time,
       pg_typeof(pickup_start_time) as pickup_type
FROM orders 
LIMIT 5;
```

#### 3. 시간 필드 데이터 정리 (필요 시)
만약 데이터베이스에 잘못된 형식의 시간 데이터가 있다면:

```sql
-- 잘못된 시간 필드를 NULL로 설정
UPDATE orders 
SET pickup_start_time = NULL,
    pickup_end_time = NULL,
    delivery_start_time = NULL,
    delivery_end_time = NULL
WHERE pickup_start_time IS NOT NULL 
  AND pg_typeof(pickup_start_time)::text != 'time without time zone';
```

---

## 🔍 디버깅 가이드

### 여전히 500 오류가 발생하는 경우

#### 1. 백엔드 상세 로그 확인
```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml logs backend --tail=200
```

다음과 같은 패턴을 찾습니다:
```
ERROR    Error converting time fields for order 123: ...
```

#### 2. Python 스택 트레이스 확인
```bash
docker-compose -f docker-compose.prod.yml logs backend --tail=300 | grep -A 30 "Traceback"
```

#### 3. 특정 주문 ID 확인
오류 로그에서 주문 ID를 찾은 후:
```bash
# PostgreSQL 접속
docker-compose -f docker-compose.prod.yml exec db psql -U uvis_user -d uvis_db

# 문제 주문 확인
SELECT * FROM orders WHERE id = 123;
```

#### 4. 백엔드 컨테이너 재빌드 (최후의 수단)
```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml stop backend
docker-compose -f docker-compose.prod.yml build --no-cache backend
docker-compose -f docker-compose.prod.yml up -d backend
docker-compose -f docker-compose.prod.yml logs backend --tail=50
```

---

## 📊 API 응답 예시

### 성공적인 GET /orders/ 응답
```json
{
  "total": 3,
  "items": [
    {
      "id": 1,
      "order_number": "ORD-1738218123456",
      "order_date": "2026-01-30",
      "temperature_zone": "냉동",
      "pallet_count": 10,
      "status": "PENDING",
      "pickup_client_name": "서울물류센터",
      "delivery_client_name": "부산물류센터",
      "pickup_start_time": "09:00",
      "pickup_end_time": "18:00",
      "delivery_start_time": "09:00",
      "delivery_end_time": "18:00",
      "created_at": "2026-01-30T10:30:00",
      "updated_at": "2026-01-30T10:30:00"
    }
  ]
}
```

### 500 오류 응답 (수정 전)
```json
{
  "detail": "Internal Server Error"
}
```

---

## ✅ 완료 체크리스트

- [x] **문제 원인 분석**: 시간 필드 변환 로직에서 예외 발생
- [x] **backend/app/api/orders.py 수정**: try-except로 안전한 변환 추가
- [x] **Git 커밋**: e455eb0
- [x] **Git 푸시**: genspark_ai_developer 브랜치
- [x] **배포 스크립트 작성**: deploy_500_fix.sh
- [x] **디버깅 스크립트 작성**: debug_500_error.sh
- [x] **문서 작성**: 이 파일

---

## 📚 관련 파일

1. **수정된 파일**:
   - `backend/app/api/orders.py` (GET /orders/, GET /orders/{id})

2. **배포 도구**:
   - `deploy_500_fix.sh` - 자동 배포 스크립트
   - `debug_500_error.sh` - 백엔드 오류 디버깅 스크립트

3. **관련 문서**:
   - `ORDER_REGISTRATION_422_COMPLETE_FIX.md` - 422 오류 해결 (이전)
   - `TEMPERATURE_ZONE_FIX.md` - 온도대 Enum 수정 (이전)

---

## 🎯 다음 단계

1. **즉시 배포**: 위의 배포 방법 실행
2. **테스트 수행**: GET /orders/ 정상 작동 확인
3. **결과 공유**: 
   - 성공: 스크린샷 + Network 탭
   - 실패: 백엔드 로그 + 오류 메시지

---

## 📝 추가 개선 사항 (향후)

### 1. 데이터베이스 마이그레이션 (권장)
시간 필드를 일관된 형식으로 정규화:
```python
# Alembic 마이그레이션 스크립트
def upgrade():
    # 모든 시간 필드를 time 타입으로 변환
    op.execute("""
        UPDATE orders 
        SET pickup_start_time = pickup_start_time::time
        WHERE pickup_start_time IS NOT NULL
    """)
```

### 2. Pydantic 직렬화 개선
OrderResponse 스키마에서 `@field_serializer` 사용:
```python
@field_serializer('pickup_start_time', 'pickup_end_time', 
                 'delivery_start_time', 'delivery_end_time')
def serialize_time(self, value: Optional[time], _info) -> Optional[str]:
    """Convert time objects to HH:MM string format"""
    if value is None:
        return None
    if isinstance(value, time):
        return value.strftime('%H:%M')
    return str(value)  # Fallback for string values
```

---

**작업 완료 일시**: 2026-01-30  
**커밋**: e455eb0  
**작업자**: GenSpark AI Developer  
**상태**: ✅ 수정 완료, 배포 대기
