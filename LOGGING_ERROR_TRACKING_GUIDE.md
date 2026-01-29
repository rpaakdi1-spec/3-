# 📝 로깅 및 에러 트래킹 가이드

**Cold Chain Dispatch System - Logging & Error Tracking**

작성일: 2026-01-27  
작성자: GenSpark AI Developer  
버전: 1.0.0

---

## 📚 목차

1. [개요](#개요)
2. [구조화된 로깅](#구조화된-로깅)
3. [Sentry 에러 트래킹](#sentry-에러-트래킹)
4. [로그 레벨](#로그-레벨)
5. [로그 형식](#로그-형식)
6. [사용 방법](#사용-방법)
7. [베스트 프랙티스](#베스트-프랙티스)

---

## 개요

### 로깅의 중요성

- ✅ **디버깅**: 문제 원인 파악
- ✅ **모니터링**: 시스템 상태 추적
- ✅ **감사**: 보안 및 규정 준수
- ✅ **분석**: 사용 패턴 분석
- ✅ **알림**: 실시간 에러 통지

### 구현된 기능

- ✅ **구조화된 로깅** (JSON 포맷)
- ✅ **Sentry 에러 트래킹**
- ✅ **로그 레벨 관리**
- ✅ **로그 파일 로테이션**
- ✅ **컨텍스트 추가**
- ✅ **성능 메트릭 로깅**

---

## 구조화된 로깅

### 로그 파일 구조

```
logs/
├── app.log          # 일반 텍스트 로그
├── app.json         # JSON 구조화 로그
└── error.log        # 에러 전용 로그
```

### 로그 로테이션

| 파일 | 크기 제한 | 보관 기간 | 압축 |
|------|-----------|-----------|------|
| `app.log` | 500 MB | 30일 | zip |
| `app.json` | 500 MB | 30일 | zip |
| `error.log` | 100 MB | 60일 | zip |

### JSON 로그 형식

```json
{
  "timestamp": "2026-01-27T23:45:00.123456",
  "service": "cold-chain-dispatch",
  "level": "INFO",
  "message": "Order created successfully",
  "context": {
    "order_id": 123,
    "user_id": 45,
    "ip_address": "192.168.1.100"
  },
  "environment": "production"
}
```

---

## Sentry 에러 트래킹

### 설정 방법

#### 1. Sentry 프로젝트 생성

1. https://sentry.io 접속
2. 새 프로젝트 생성 (FastAPI)
3. DSN 복사

#### 2. 환경 변수 설정

`.env` 파일:
```bash
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

#### 3. 자동 초기화

애플리케이션 시작 시 자동으로 Sentry가 초기화됩니다.

### Sentry 기능

#### 에러 캡처
- 자동으로 모든 예외 캡처
- 스택 트레이스 포함
- 컨텍스트 정보 추가

#### 성능 추적
- API 엔드포인트 성능
- 데이터베이스 쿼리 시간
- Redis 캐시 성능

#### 통합
- FastAPI 통합
- SQLAlchemy 통합
- Redis 통합
- Logging 통합

---

## 로그 레벨

### 레벨 정의

| 레벨 | 용도 | 예시 |
|------|------|------|
| **DEBUG** | 상세 디버깅 정보 | 변수 값, 함수 호출 |
| **INFO** | 일반 정보 | 요청 처리, 성공 메시지 |
| **WARNING** | 경고 메시지 | 재시도, 비정상 상태 |
| **ERROR** | 에러 발생 | 예외, 실패 |
| **CRITICAL** | 심각한 에러 | 시스템 다운, 데이터 손실 |

### 환경별 레벨

| 환경 | 콘솔 | 파일 |
|------|------|------|
| **개발** | DEBUG | INFO |
| **스테이징** | INFO | INFO |
| **프로덕션** | INFO | INFO |

---

## 로그 형식

### 콘솔 출력 (개발 환경)

```
2026-01-27 23:45:00 | INFO     | app.api.orders:create_order:45 | Order created successfully
```

**컬러 코딩**:
- 🟢 DEBUG: 회색
- 🔵 INFO: 파란색
- 🟡 WARNING: 노란색
- 🔴 ERROR: 빨간색
- 🔥 CRITICAL: 보라색

### 파일 출력 (프로덕션)

```
2026-01-27 23:45:00 | INFO | app.api.orders:create_order:45 | Order created successfully
```

### JSON 출력

```json
{
  "timestamp": "2026-01-27T23:45:00.123456",
  "level": "INFO",
  "message": "Order created successfully",
  "context": {...}
}
```

---

## 사용 방법

### 기본 로깅

```python
from app.services.logging_service import get_logger

logger = get_logger()

# 디버그
logger.debug("Debugging information")

# 정보
logger.info("User logged in")

# 경고
logger.warning("Cache miss, falling back to database")

# 에러
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exception=e)

# 심각한 에러
logger.critical("Database connection lost", exception=e)
```

### 컨텍스트 추가

```python
# 추가 정보와 함께 로깅
logger.info(
    "Order created",
    order_id=123,
    user_id=45,
    total_amount=15000
)
```

### API 요청 로깅

```python
from fastapi import Request
import time

@app.post("/orders")
async def create_order(request: Request):
    start_time = time.time()
    
    # ... 처리 로직 ...
    
    # 요청 로깅
    duration = time.time() - start_time
    logger.log_api_request(
        method=request.method,
        path=request.url.path,
        status_code=200,
        duration=duration,
        user_id=current_user.id,
        ip_address=request.client.host
    )
```

### 데이터베이스 쿼리 로깅

```python
import time

start_time = time.time()
orders = db.query(Order).all()
duration = time.time() - start_time

logger.log_database_query(
    query_type="SELECT",
    table="orders",
    duration=duration,
    rows_affected=len(orders)
)
```

### 비즈니스 이벤트 로깅

```python
logger.log_business_event(
    event_type="order_created",
    entity_type="order",
    entity_id=order.id,
    action="create",
    user_id=current_user.id,
    details={
        "product_name": order.product_name,
        "pallet_count": order.pallet_count
    }
)
```

### 보안 이벤트 로깅

```python
logger.log_security_event(
    event_type="failed_login",
    severity="medium",
    ip_address=request.client.host,
    details={
        "username": username,
        "attempts": 3
    }
)
```

### 성능 메트릭 로깅

```python
logger.log_performance_metric(
    metric_name="api_response_time",
    value=45.2,
    unit="ms",
    tags={
        "endpoint": "/orders",
        "method": "GET"
    }
)
```

---

## Sentry 사용법

### 예외 캡처

```python
from app.services.sentry_service import get_sentry

sentry = get_sentry()

try:
    risky_operation()
except Exception as e:
    sentry.capture_exception(
        e,
        context={"order_id": 123},
        tags={"operation": "dispatch"}
    )
    raise
```

### 메시지 캡처

```python
sentry.capture_message(
    "Important event occurred",
    level="warning",
    context={"event_type": "dispatch_completed"},
    tags={"priority": "high"}
)
```

### 사용자 컨텍스트 설정

```python
sentry.set_user(
    user_id=current_user.id,
    email=current_user.email,
    username=current_user.username,
    ip_address=request.client.host
)
```

### Breadcrumb 추가

```python
# API 요청
sentry.add_breadcrumb(
    category="http",
    message="GET /orders",
    level="info",
    data={"status_code": 200}
)

# 데이터베이스 쿼리
sentry.add_breadcrumb(
    category="db",
    message="SELECT orders",
    level="info",
    data={"rows": 42}
)

# 캐시 조회
sentry.add_breadcrumb(
    category="cache",
    message="Cache hit",
    level="info",
    data={"key": "orders:list"}
)
```

### 트랜잭션 추적 (성능)

```python
transaction = sentry.start_transaction(
    name="/api/v1/orders",
    op="http.server"
)

with transaction:
    # ... 작업 수행 ...
    with transaction.start_child(op="db.query") as span:
        span.set_tag("table", "orders")
        orders = db.query(Order).all()
    
    with transaction.start_child(op="cache.get") as span:
        cached_data = cache.get("orders")
```

---

## 베스트 프랙티스

### ✅ DO

1. **적절한 로그 레벨 사용**
   ```python
   # ✅ 정보성 메시지
   logger.info("User logged in")
   
   # ✅ 에러 발생
   logger.error("Failed to connect to database", exception=e)
   ```

2. **컨텍스트 추가**
   ```python
   # ✅ 추가 정보 제공
   logger.error(
       "Order creation failed",
       order_id=123,
       user_id=45,
       reason="Insufficient inventory"
   )
   ```

3. **예외 정보 포함**
   ```python
   # ✅ 예외 객체 전달
   try:
       process_order()
   except Exception as e:
       logger.error("Processing failed", exception=e)
   ```

4. **구조화된 로깅**
   ```python
   # ✅ JSON 구조
   logger.info(
       "Payment processed",
       payment_id=789,
       amount=15000,
       method="card"
   )
   ```

5. **성능 로깅**
   ```python
   # ✅ 처리 시간 기록
   start = time.time()
   result = expensive_operation()
   duration = time.time() - start
   logger.log_performance_metric("operation_time", duration)
   ```

### ❌ DON'T

1. **민감 정보 로깅 금지**
   ```python
   # ❌ 절대 금지
   logger.info(f"Password: {password}")
   logger.info(f"Credit Card: {card_number}")
   
   # ✅ 마스킹
   logger.info(f"Card: {card_number[-4:]}")
   ```

2. **과도한 로깅**
   ```python
   # ❌ 루프 내 로깅
   for item in items:
       logger.debug(f"Processing {item}")  # 10,000번 호출
   
   # ✅ 요약 로깅
   logger.info(f"Processed {len(items)} items")
   ```

3. **에러 무시**
   ```python
   # ❌ 에러 무시
   try:
       critical_operation()
   except:
       pass
   
   # ✅ 에러 로깅
   try:
       critical_operation()
   except Exception as e:
       logger.error("Critical operation failed", exception=e)
       raise
   ```

4. **부적절한 레벨**
   ```python
   # ❌ 잘못된 레벨
   logger.error("User clicked button")  # INFO 레벨
   logger.info("Database connection lost")  # ERROR 레벨
   ```

---

## 로그 분석

### 로그 검색

```bash
# 에러 로그 검색
grep "ERROR" logs/app.log

# 특정 사용자 로그
grep "user_id=123" logs/app.json

# 시간대별 로그
grep "2026-01-27 23:" logs/app.log

# 특정 IP 로그
grep "192.168.1.100" logs/app.log
```

### 로그 집계

```bash
# 에러 횟수
grep "ERROR" logs/app.log | wc -l

# 가장 빈번한 에러
grep "ERROR" logs/app.log | cut -d'|' -f4 | sort | uniq -c | sort -nr | head -10

# API 응답 시간 평균
grep "duration_ms" logs/app.json | jq '.context.duration_ms' | awk '{sum+=$1; count++} END {print sum/count}'
```

---

## 트러블슈팅

### 문제: 로그 파일이 생성되지 않음

**해결**:
```bash
# 로그 디렉토리 권한 확인
ls -la logs/

# 디렉토리 생성
mkdir -p logs
chmod 755 logs
```

### 문제: Sentry 에러가 전송되지 않음

**해결**:
1. DSN 확인: `.env` 파일
2. 네트워크 확인: 방화벽
3. Sentry 대시보드 확인

### 문제: 로그 파일이 너무 큼

**해결**:
```python
# 로테이션 설정 조정
logger.add(
    "logs/app.log",
    rotation="100 MB",  # 크기 줄이기
    retention="7 days"  # 보관 기간 단축
)
```

---

## 참고 자료

- [Loguru 문서](https://loguru.readthedocs.io/)
- [Sentry 문서](https://docs.sentry.io/)
- [Structured Logging Best Practices](https://stackify.com/what-is-structured-logging-and-why-developers-need-it/)

---

**작성일**: 2026-01-27  
**버전**: 1.0.0  
**상태**: ✅ 완료
