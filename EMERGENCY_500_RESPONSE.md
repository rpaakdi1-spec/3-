# 🚨 500 오류 긴급 대응 가이드

## 현재 상황

**오류**: `GET http://139.150.11.99/api/v1/orders/ 500 (Internal Server Error)`  
**증상**: 주문 목록이 로드되지 않음  
**원인**: 서버에 최신 코드 미배포 또는 데이터베이스 시간 필드 이슈

---

## 🔥 즉시 실행 (1분 소요)

### 방법 1: 자동 긴급 복구 (권장)

```bash
# PuTTY로 서버 접속 (139.150.11.99)
cd /root/uvis
git pull origin genspark_ai_developer
./emergency_hotfix_500.sh
```

이 스크립트가 자동으로:
1. ✅ 최신 코드 가져오기
2. ✅ 데이터베이스 시간 필드 정리
3. ✅ 백엔드 재시작
4. ✅ API 테스트

---

### 방법 2: 수동 단계별 실행

#### 1단계: 백엔드 로그 확인 (필수!)
```bash
docker logs uvis-backend-1 --tail 50
```

**다음 중 하나의 오류를 찾으세요:**

##### A. AttributeError (가장 가능성 높음)
```
AttributeError: 'str' object has no attribute 'strftime'
```
→ **해결책**: DB 핫픽스 스크립트 실행 (아래 2단계)

##### B. ValidationError
```
pydantic.ValidationError: ... temperature_zone
```
→ **해결책**: 프론트엔드 캐시 삭제 필요

##### C. ImportError / ModuleNotFoundError
```
ModuleNotFoundError: No module named 'app.services...'
```
→ **해결책**: 백엔드 재빌드 필요

#### 2단계: 데이터베이스 핫픽스 실행
```bash
cd /root/uvis
docker exec uvis-backend-1 python3 /app/hotfix_500_error.py
```

**예상 출력:**
```
==================================================
Order Time Fields Hotfix
==================================================

✓ Fixed order 1 (ORD-001)
✓ Fixed order 2 (ORD-002)

✅ Successfully fixed 2 orders
==================================================
```

#### 3단계: 백엔드 재시작
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

#### 4단계: 헬스 체크
```bash
# 백엔드 상태 확인
docker ps | grep backend

# 최근 로그 확인
docker logs uvis-backend-1 --tail 20

# API 테스트
curl -X GET "http://139.150.11.99/api/v1/orders/?limit=1" \
     -H "accept: application/json"
```

**예상 응답 (성공):**
```json
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "order_number": "ORD-001",
      "pickup_start_time": "09:00",
      ...
    }
  ]
}
```

---

## 🔍 문제 진단 체크리스트

### 체크포인트 1: 코드 버전
```bash
cd /root/uvis
git branch
git log --oneline -3
```

**예상 출력:**
```
* genspark_ai_developer
* 16cf8b6 fix: 500 오류 긴급 핫픽스
* ada204e docs: 주문 시스템 오류 완전 해결
* 24c6eec fix(backend): Pydantic serializer 충돌 제거
```

✅ 최신 커밋이 `16cf8b6` 이상이어야 함

### 체크포인트 2: 백엔드 컨테이너
```bash
docker ps | grep backend
```

**예상 출력:**
```
uvis-backend-1   Up 5 minutes   0.0.0.0:8000->8000/tcp
```

✅ 상태가 `Up`이어야 함

### 체크포인트 3: 데이터베이스 연결
```bash
docker exec uvis-backend-1 python3 -c "
from app.core.database import SessionLocal
from app.models.order import Order

db = SessionLocal()
count = db.query(Order).count()
print(f'✓ Database OK. Total orders: {count}')
db.close()
"
```

✅ 오류 없이 주문 수가 출력되어야 함

### 체크포인트 4: 시간 필드 타입
```bash
docker exec uvis-backend-1 python3 -c "
from app.core.database import SessionLocal
from app.models.order import Order
from datetime import time

db = SessionLocal()
orders = db.query(Order).limit(3).all()

for order in orders:
    print(f'Order {order.id}:')
    print(f'  pickup_start_time: type={type(order.pickup_start_time).__name__}, value={order.pickup_start_time}')
    if order.pickup_start_time:
        is_time = isinstance(order.pickup_start_time, time)
        is_str = isinstance(order.pickup_start_time, str)
        print(f'  is_time={is_time}, is_str={is_str}')

db.close()
"
```

**예상 출력 (정상):**
```
Order 1:
  pickup_start_time: type=time, value=09:00:00
  is_time=True, is_str=False
```

❌ **문제 (is_str=True인 경우):**
```
Order 1:
  pickup_start_time: type=str, value=09:00
  is_time=False, is_str=True  ← 이 경우 핫픽스 필요!
```

---

## 🛠️ 문제별 해결 방법

### Case A: 시간 필드가 문자열로 저장됨
**증상**: `is_str=True` 또는 `AttributeError: 'str' has no attribute 'strftime'`

**해결:**
```bash
docker exec uvis-backend-1 python3 /app/hotfix_500_error.py
docker-compose -f docker-compose.prod.yml restart backend
```

### Case B: 최신 코드 미배포
**증상**: 커밋이 `16cf8b6`보다 오래됨

**해결:**
```bash
cd /root/uvis
git checkout genspark_ai_developer
git pull origin genspark_ai_developer
docker-compose -f docker-compose.prod.yml restart backend
```

### Case C: 프론트엔드 캐시 문제
**증상**: 백엔드는 정상이지만 브라우저에서 오류

**해결:**
1. 브라우저에서 `Ctrl+Shift+R` (캐시 삭제 새로고침)
2. 개발자 도구 > Application > Clear Storage > Clear site data
3. 프론트엔드 재시작:
   ```bash
   docker-compose -f docker-compose.prod.yml restart frontend
   ```

### Case D: 데이터베이스 연결 끊김
**증상**: `sqlalchemy.exc.OperationalError`

**해결:**
```bash
# 전체 스택 재시작
docker-compose -f docker-compose.prod.yml restart

# 또는 DB만 재시작
docker-compose -f docker-compose.prod.yml restart postgres
```

---

## 📊 핫픽스 스크립트 상세

### hotfix_500_error.py 동작 방식

```python
# 모든 주문을 순회하며:
for order in orders:
    # 시간 필드가 문자열이면:
    if isinstance(order.pickup_start_time, str):
        # time 객체로 변환
        hour, minute = map(int, order.pickup_start_time.split(':'))
        order.pickup_start_time = time(hour, minute)
    
    # 변환 실패 시 None으로 설정
    except:
        order.pickup_start_time = None

# DB에 커밋
db.commit()
```

**안전성:**
- ✅ 읽기 전용 DB 접근 (조회만 수행)
- ✅ 변환 실패 시 롤백
- ✅ 원본 데이터 백업 권장 (선택사항)

---

## 🧪 수동 API 테스트

### 테스트 1: 주문 목록 조회
```bash
curl -X GET "http://139.150.11.99/api/v1/orders/" \
     -H "accept: application/json" \
     -w "\nStatus: %{http_code}\n" \
     | jq '.'
```

**성공 (200):**
```json
{
  "total": 10,
  "items": [...]
}
```

**실패 (500):**
```json
{
  "detail": "Internal server error"
}
```

### 테스트 2: 단일 주문 조회
```bash
curl -X GET "http://139.150.11.99/api/v1/orders/1" \
     -H "accept: application/json"
```

### 테스트 3: 새 주문 생성
```bash
curl -X POST "http://139.150.11.99/api/v1/orders/" \
     -H "Content-Type: application/json" \
     -d '{
       "order_number": "TEST-500-FIX",
       "order_date": "2026-01-31",
       "temperature_zone": "냉동",
       "pallet_count": 5,
       "pickup_client_id": 1,
       "delivery_client_id": 2,
       "pickup_start_time": "09:00",
       "delivery_start_time": "14:00"
     }'
```

---

## 📞 에스컬레이션 (여전히 500 오류 발생 시)

### 필수 정보 공유

```bash
# 1. 백엔드 로그 (최근 100줄)
docker logs uvis-backend-1 --tail 100 > backend_logs.txt

# 2. 현재 코드 버전
cd /root/uvis
git log --oneline -5 > git_version.txt

# 3. 컨테이너 상태
docker ps > docker_status.txt

# 4. API 테스트 결과
curl -X GET "http://139.150.11.99/api/v1/orders/?limit=1" \
     -H "accept: application/json" \
     -v > api_test.txt 2>&1

# 5. 데이터베이스 샘플
docker exec uvis-backend-1 python3 -c "
from app.core.database import SessionLocal
from app.models.order import Order

db = SessionLocal()
order = db.query(Order).first()
if order:
    print(f'Sample Order {order.id}:')
    print(f'  order_number: {order.order_number}')
    print(f'  temperature_zone: {order.temperature_zone} (type: {type(order.temperature_zone).__name__})')
    print(f'  pickup_start_time: {order.pickup_start_time} (type: {type(order.pickup_start_time).__name__})')
db.close()
" > db_sample.txt
```

위 파일들을 공유해주세요.

---

## ✅ 성공 확인

### 브라우저에서:
1. `http://139.150.11.99/orders` 접속
2. ✅ 주문 목록 로드됨 (500 오류 없음)
3. ✅ 시간 필드가 `HH:MM` 형식으로 표시
4. ✅ 개발자 도구 Console에 오류 없음

### API에서:
```bash
curl -X GET "http://139.150.11.99/api/v1/orders/?limit=1" -H "accept: application/json"
```
→ HTTP 200 OK 응답

---

## 🎯 다음 단계

1. ⏳ 긴급 핫픽스 실행: `./emergency_hotfix_500.sh`
2. ⏳ 백엔드 로그 확인 및 공유
3. ⏳ 브라우저 테스트 결과 공유
4. ✅ 모든 테스트 통과 시: 문제 해결 완료!

---

**커밋**: `16cf8b6`  
**우선순위**: P0 (최우선)  
**예상 해결 시간**: 1-5분

**즉시 실행하세요**: `cd /root/uvis && git pull origin genspark_ai_developer && ./emergency_hotfix_500.sh`
