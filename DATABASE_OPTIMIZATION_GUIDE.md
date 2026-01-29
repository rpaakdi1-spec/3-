# 🗄️ 데이터베이스 최적화 가이드

**Cold Chain Dispatch System - Database Optimization**

작성일: 2026-01-27  
작성자: GenSpark AI Developer  
버전: 1.0.0

---

## 📚 목차

1. [개요](#개요)
2. [인덱스 최적화](#인덱스-최적화)
3. [쿼리 최적화](#쿼리-최적화)
4. [커넥션 풀 튜닝](#커넥션-풀-튜닝)
5. [성능 모니터링](#성능-모니터링)
6. [베스트 프랙티스](#베스트-프랙티스)

---

## 개요

이 문서는 Cold Chain Dispatch System의 데이터베이스 성능 최적화 가이드입니다.

### 주요 최적화 항목

- ✅ **인덱스 최적화** - 45개 인덱스 추가
- ✅ **쿼리 최적화** - N+1 문제 해결, 조인 최적화
- ✅ **커넥션 풀** - 풀 크기 및 타임아웃 튜닝
- ✅ **모니터링** - 성능 분석 도구
- ✅ **유지보수** - VACUUM, ANALYZE

---

## 인덱스 최적화

### 추가된 인덱스 (45개)

#### Orders 테이블 (8개)
```sql
CREATE INDEX idx_orders_order_number ON orders(order_number);  -- 주문 번호 조회
CREATE INDEX idx_orders_status ON orders(status);  -- 상태 필터링
CREATE INDEX idx_orders_order_date ON orders(order_date);  -- 날짜 범위 조회
CREATE INDEX idx_orders_requested_delivery_date ON orders(requested_delivery_date);  -- 배송일 조회
CREATE INDEX idx_orders_pickup_client ON orders(pickup_client_id);  -- 거래처별 조회
CREATE INDEX idx_orders_delivery_client ON orders(delivery_client_id);  -- 거래처별 조회
CREATE INDEX idx_orders_status_date ON orders(status, order_date);  -- 복합 인덱스
CREATE INDEX idx_orders_temperature_zone ON orders(temperature_zone);  -- 온도대 필터링
```

#### Dispatches 테이블 (6개)
```sql
CREATE INDEX idx_dispatches_dispatch_number ON dispatches(dispatch_number);  -- 배차 번호
CREATE INDEX idx_dispatches_status ON dispatches(status);  -- 상태 필터링
CREATE INDEX idx_dispatches_dispatch_date ON dispatches(dispatch_date);  -- 날짜 조회
CREATE INDEX idx_dispatches_vehicle ON dispatches(vehicle_id);  -- 차량별 배차
CREATE INDEX idx_dispatches_driver ON dispatches(driver_id);  -- 기사별 배차
CREATE INDEX idx_dispatches_status_date ON dispatches(status, dispatch_date);  -- 복합 인덱스
```

#### Dispatch Routes 테이블 (3개)
```sql
CREATE INDEX idx_dispatch_routes_dispatch ON dispatch_routes(dispatch_id, sequence);  -- 경로 조회
CREATE INDEX idx_dispatch_routes_order ON dispatch_routes(order_id);  -- 주문별 경로
CREATE INDEX idx_dispatch_routes_type ON dispatch_routes(route_type);  -- 경로 타입
```

#### Vehicles 테이블 (4개)
```sql
CREATE INDEX idx_vehicles_vehicle_number ON vehicles(vehicle_number);  -- 차량 번호
CREATE INDEX idx_vehicles_status ON vehicles(status);  -- 상태 필터링
CREATE INDEX idx_vehicles_temperature_zone ON vehicles(temperature_zone);  -- 온도대
CREATE INDEX idx_vehicles_status_temp ON vehicles(status, temperature_zone);  -- 복합 인덱스
```

#### Drivers 테이블 (3개)
```sql
CREATE INDEX idx_drivers_license_number ON drivers(license_number);  -- 면허 번호
CREATE INDEX idx_drivers_status ON drivers(status);  -- 상태 필터링
CREATE INDEX idx_drivers_phone ON drivers(phone);  -- 전화번호 조회
```

#### Clients 테이블 (3개)
```sql
CREATE INDEX idx_clients_business_number ON clients(business_number);  -- 사업자 번호
CREATE INDEX idx_clients_name ON clients(name);  -- 이름 검색
CREATE INDEX idx_clients_location ON clients USING GIST (ST_MakePoint(longitude, latitude));  -- 공간 인덱스
```

#### Vehicle Locations 테이블 (3개)
```sql
CREATE INDEX idx_vehicle_locations_vehicle_time ON vehicle_locations(vehicle_id, timestamp);  -- 차량별 시간순
CREATE INDEX idx_vehicle_locations_dispatch ON vehicle_locations(dispatch_id);  -- 배차별 위치
CREATE INDEX idx_vehicle_locations_timestamp ON vehicle_locations(timestamp);  -- 시간 범위
```

#### Temperature Alerts 테이블 (3개)
```sql
CREATE INDEX idx_temp_alerts_dispatch ON temperature_alerts(dispatch_id, alert_time);  -- 배차별 알림
CREATE INDEX idx_temp_alerts_resolved ON temperature_alerts(is_resolved);  -- 해결 여부
CREATE INDEX idx_temp_alerts_unresolved ON temperature_alerts(is_resolved, dispatch_id) WHERE is_resolved = false;  -- 부분 인덱스
```

#### Users 테이블 (3개)
```sql
CREATE INDEX idx_users_username ON users(username);  -- 로그인
CREATE INDEX idx_users_email ON users(email);  -- 이메일 조회
CREATE INDEX idx_users_is_active ON users(is_active);  -- 활성 사용자
```

### 인덱스 적용

```bash
cd /home/user/webapp/backend

# Alembic 마이그레이션 실행
alembic upgrade head

# 또는 직접 스크립트 실행
python scripts/db_analyzer.py
```

### 인덱스 성능 확인

```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'PENDING' AND order_date >= '2026-01-01';

-- Index Scan이 표시되면 인덱스가 사용됨
-- Seq Scan이 표시되면 인덱스가 사용되지 않음
```

---

## 쿼리 최적화

### 1. N+1 문제 해결

**문제**: 1개의 쿼리로 목록을 조회한 후, 각 항목마다 추가 쿼리 실행

❌ **Before (N+1 문제)**:
```python
# 1개의 쿼리로 주문 조회
orders = db.query(Order).all()

# 각 주문마다 추가 쿼리 (N개)
for order in orders:
    pickup_client = order.pickup_client  # 쿼리 실행
    delivery_client = order.delivery_client  # 쿼리 실행
```

✅ **After (Eager Loading)**:
```python
from sqlalchemy.orm import joinedload

# 1개의 쿼리로 관련 데이터 함께 조회
orders = db.query(Order).options(
    joinedload(Order.pickup_client),
    joinedload(Order.delivery_client)
).all()
```

### 2. 선택적 컬럼 조회

❌ **Before (모든 컬럼 조회)**:
```python
orders = db.query(Order).all()  # 모든 컬럼 조회
```

✅ **After (필요한 컬럼만)**:
```python
orders = db.query(
    Order.id,
    Order.order_number,
    Order.status,
    Order.product_name
).all()
```

### 3. 페이지네이션

❌ **Before (전체 조회)**:
```python
orders = db.query(Order).all()  # 10,000건 조회
```

✅ **After (페이지네이션)**:
```python
page = 1
page_size = 50
orders = db.query(Order).offset((page - 1) * page_size).limit(page_size).all()
```

### 4. 집계 쿼리 최적화

❌ **Before (Python에서 집계)**:
```python
orders = db.query(Order).all()
total_pallets = sum(order.pallet_count for order in orders)
```

✅ **After (SQL 집계)**:
```python
from sqlalchemy import func

total_pallets = db.query(func.sum(Order.pallet_count)).scalar()
```

### 5. 부분 인덱스 활용

```sql
-- 미해결 알림만 인덱스 (부분 인덱스)
CREATE INDEX idx_temp_alerts_unresolved 
ON temperature_alerts(is_resolved, dispatch_id) 
WHERE is_resolved = false;
```

---

## 커넥션 풀 튜닝

### SQLAlchemy 커넥션 풀 설정

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # 기본 커넥션 수
    max_overflow=10,       # 추가 커넥션 수
    pool_timeout=30,       # 커넥션 대기 시간 (초)
    pool_recycle=3600,     # 커넥션 재사용 시간 (1시간)
    pool_pre_ping=True,    # 커넥션 유효성 검사
    echo=False             # SQL 로깅 비활성화 (프로덕션)
)
```

### 권장 설정

| 환경 | pool_size | max_overflow | pool_timeout |
|------|-----------|--------------|--------------|
| 개발 | 5 | 10 | 30 |
| 스테이징 | 20 | 10 | 30 |
| 프로덕션 | 50 | 20 | 30 |

### 커넥션 풀 모니터링

```python
# 커넥션 풀 상태 확인
pool = engine.pool
print(f"Pool Size: {pool.size()}")
print(f"Checked In: {pool.checkedin()}")
print(f"Checked Out: {pool.checkedout()}")
print(f"Overflow: {pool.overflow()}")
```

---

## 성능 모니터링

### 데이터베이스 분석 도구

```bash
cd /home/user/webapp/backend

# 분석 보고서 생성
python scripts/db_analyzer.py
```

**출력 예시**:
```
================================================================================
데이터베이스 분석 보고서 - 2026-01-27 22:00:00
================================================================================

📊 테이블 크기 분석
--------------------------------------------------------------------------------
  orders                         | Rows:      1,234
  dispatches                     | Rows:        456
  clients                        | Rows:        123
  vehicles                       | Rows:         45
  drivers                        | Rows:         30

🔍 인덱스 현황
--------------------------------------------------------------------------------
  테이블: orders
    - idx_orders_order_number: order_number (UNIQUE)
    - idx_orders_status: status
    - idx_orders_status_date: status, order_date

⚠️  인덱스 권장사항
--------------------------------------------------------------------------------
  모든 필수 인덱스가 존재합니다.

🔌 커넥션 풀 상태
--------------------------------------------------------------------------------
  Pool Size: 20
  Checked In: 18
  Checked Out: 2
  Overflow: 0
  Status: healthy
```

### 느린 쿼리 로깅 (PostgreSQL)

```sql
-- postgresql.conf
log_min_duration_statement = 1000  -- 1초 이상 쿼리 로깅

-- 느린 쿼리 확인
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### EXPLAIN ANALYZE

```sql
-- 쿼리 실행 계획 확인
EXPLAIN ANALYZE
SELECT o.*, c1.name as pickup_name, c2.name as delivery_name
FROM orders o
JOIN clients c1 ON o.pickup_client_id = c1.id
JOIN clients c2 ON o.delivery_client_id = c2.id
WHERE o.status = 'PENDING'
AND o.order_date >= '2026-01-01';
```

---

## 베스트 프랙티스

### ✅ DO

1. **인덱스 사용**
   - 자주 조회되는 컬럼에 인덱스 추가
   - 복합 인덱스 활용 (status, date)
   - 외래 키에 인덱스 추가

2. **쿼리 최적화**
   - Eager Loading으로 N+1 문제 해결
   - 필요한 컬럼만 조회
   - 페이지네이션 사용
   - SQL 집계 함수 활용

3. **커넥션 풀**
   - 적절한 pool_size 설정
   - pool_pre_ping 활성화
   - 커넥션 재사용 (pool_recycle)

4. **유지보수**
   - 정기적인 VACUUM (PostgreSQL)
   - 정기적인 ANALYZE
   - 인덱스 재구축 (REINDEX)

### ❌ DON'T

1. **과도한 인덱스**
   - 모든 컬럼에 인덱스 추가 금지
   - 업데이트가 빈번한 컬럼 인덱스 주의

2. **비효율적 쿼리**
   - SELECT * 사용 자제
   - LIKE '%keyword%' 사용 자제
   - 과도한 JOIN 금지

3. **커넥션 누수**
   - 세션 닫지 않기
   - 트랜잭션 롤백 누락

---

## 마이그레이션 적용

### 인덱스 추가

```bash
cd /home/user/webapp/backend

# 마이그레이션 실행
alembic upgrade head

# 롤백 (필요시)
alembic downgrade -1
```

### VACUUM 실행

```bash
# PostgreSQL
psql -d database_name -c "VACUUM ANALYZE;"

# SQLite
sqlite3 database.db "VACUUM;"

# 또는 Python 스크립트
python scripts/db_analyzer.py
```

---

## 성능 목표

| 지표 | 목표 | 현재 |
|------|------|------|
| 주문 목록 조회 | < 100ms | TBD |
| 주문 생성 | < 50ms | TBD |
| 배차 최적화 | < 2s | TBD |
| 대시보드 조회 | < 200ms | TBD |
| 동시 커넥션 | 100개 | TBD |

---

## 참고 자료

- [SQLAlchemy Performance](https://docs.sqlalchemy.org/en/14/faq/performance.html)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Database Indexing Best Practices](https://use-the-index-luke.com/)

---

**작성일**: 2026-01-27  
**버전**: 1.0.0  
**상태**: ✅ 완료
