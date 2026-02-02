# 🚀 Phase 1: 기본 제약조건 구현 가이드

## 📋 개요

Phase 1에서는 스마트 배차 시스템의 4가지 핵심 제약조건을 구현합니다:

1. ✅ **파렛트 타입 구분** (11형/12형)
2. ✅ **온도대별 차량 매칭** (냉동/냉장/상온)
3. ✅ **24시간 기준 하차시간 계산**
4. ✅ **차량 길이별 적재량 계산**

---

## 📁 생성된 파일

### 1. 데이터베이스 마이그레이션
```
backend/migrations/phase1_constraints.sql (133 라인)
```

**주요 변경사항:**
- `clients` 테이블: `pallet_type`, `unload_start_time`, `unload_end_time` 추가
- `vehicles` 테이블: `max_pallets_11type`, `max_pallets_12type`, `supports_*` 플래그 추가
- `orders` 테이블: `calculated_delivery_datetime`, `pallet_type` 추가
- `vehicle_capacity_rules` 테이블 신규 생성

### 2. Python 유틸리티 함수
```
backend/app/utils/phase1_constraints.py (400+ 라인)
```

**제공 함수:**
- `get_vehicle_capacity_by_pallet_type()` - 차량 용량 조회
- `calculate_remaining_capacity()` - 남은 적재 공간 계산
- `is_temperature_compatible()` - 온도대 호환성 체크
- `calculate_delivery_datetime()` - 24시간 기준 하차시간 계산
- `validate_dispatch_constraints()` - 배차 제약조건 검증

---

## 🔧 구현 상세

### 1️⃣ 파렛트 타입 구분 (11형/12형)

#### 데이터베이스 스키마
```sql
-- Clients에 파렛트 타입 추가
ALTER TABLE clients 
ADD COLUMN pallet_type VARCHAR(10) DEFAULT '11형' 
CHECK (pallet_type IN ('11형', '12형'));

-- Vehicles에 파렛트 타입별 용량 추가
ALTER TABLE vehicles
ADD COLUMN max_pallets_11type INTEGER,
ADD COLUMN max_pallets_12type INTEGER;
```

#### 차량 길이별 용량 규칙
| 차량 길이 | 11형 용량 | 12형 용량 |
|-----------|-----------|-----------|
| 9.5m      | 20개      | 17개      |
| 11.0m     | 24개      | 20개      |
| 12.0m     | 26개      | 22개      |
| 14.0m     | 30개      | 26개      |

#### Python 사용 예시
```python
from app.utils.phase1_constraints import get_vehicle_capacity_by_pallet_type

# 9.5m 차량의 12형 팔레트 용량
capacity = get_vehicle_capacity_by_pallet_type(9.5, "12형")
print(capacity)  # 17

# 남은 적재 공간 계산
from app.utils.phase1_constraints import calculate_remaining_capacity

remaining = calculate_remaining_capacity(
    vehicle_length_m=9.5,
    current_load_11=10,  # 현재 11형 10개 적재
    current_load_12=5    # 현재 12형 5개 적재
)
print(remaining)  # {"11형": 10, "12형": 12}
```

---

### 2️⃣ 온도대별 차량 매칭

#### 데이터베이스 스키마
```sql
ALTER TABLE vehicles
ADD COLUMN supports_frozen BOOLEAN DEFAULT false,   -- 냉동 가능
ADD COLUMN supports_chilled BOOLEAN DEFAULT false,  -- 냉장 가능
ADD COLUMN supports_ambient BOOLEAN DEFAULT true;   -- 상온 가능
```

#### 차량 타입별 자동 설정
```sql
UPDATE vehicles
SET 
    supports_frozen = CASE 
        WHEN vehicle_type IN ('냉동', '겸용') THEN true 
        ELSE false 
    END,
    supports_chilled = CASE 
        WHEN vehicle_type IN ('냉장', '겸용') THEN true 
        ELSE false 
    END,
    supports_ambient = CASE 
        WHEN vehicle_type IN ('상온', '겸용') THEN true
        ELSE false
    END;
```

#### Python 사용 예시
```python
from app.utils.phase1_constraints import is_temperature_compatible

vehicle_supports = {
    "supports_frozen": True,
    "supports_chilled": True,
    "supports_ambient": False
}

# 냉동 주문 호환 체크
compatible = is_temperature_compatible(vehicle_supports, "냉동")
print(compatible)  # True

# 상온 주문 호환 체크
compatible = is_temperature_compatible(vehicle_supports, "상온")
print(compatible)  # False
```

---

### 3️⃣ 24시간 기준 하차시간 계산

#### 로직 설명
```
현재 시간: 20:00, 하차시간: 04:00
→ 하차시간(04:00)이 현재시간(20:00)보다 이르므로 다음날로 계산
→ 결과: 다음날 04:00

현재 시간: 10:00, 하차시간: 14:00
→ 하차시간(14:00)이 현재시간(10:00)보다 늦으므로 같은 날
→ 결과: 오늘 14:00

현재 시간: 23:00, 하차시간: 01:00
→ 자정 넘는 특수 케이스 (22:00~06:00 사이)
→ 결과: 다음날 01:00
```

#### Python 사용 예시
```python
from datetime import datetime
from app.utils.phase1_constraints import calculate_delivery_datetime

# 예시 1: 저녁 주문, 새벽 하차
order_time = datetime(2026, 2, 2, 20, 0)
delivery_dt = calculate_delivery_datetime(order_time, "04:00")
print(delivery_dt)  # 2026-02-03 04:00:00 (다음날)

# 예시 2: 오전 주문, 오후 하차
order_time = datetime(2026, 2, 2, 10, 0)
delivery_dt = calculate_delivery_datetime(order_time, "14:00")
print(delivery_dt)  # 2026-02-02 14:00:00 (같은 날)

# 예시 3: 자정 넘는 케이스
order_time = datetime(2026, 2, 2, 23, 0)
delivery_dt = calculate_delivery_datetime(order_time, "01:00")
print(delivery_dt)  # 2026-02-03 01:00:00 (다음날)
```

#### 데이터베이스 저장
```sql
-- Orders 테이블에 자동 계산된 하차 일시 저장
ALTER TABLE orders
ADD COLUMN calculated_delivery_datetime TIMESTAMP;
```

---

### 4️⃣ 차량 길이별 적재량 계산

#### 차량 용량 규칙 테이블
```sql
CREATE TABLE vehicle_capacity_rules (
    id SERIAL PRIMARY KEY,
    vehicle_length_m FLOAT NOT NULL,
    pallet_type VARCHAR(10) NOT NULL,
    max_capacity INTEGER NOT NULL,
    notes TEXT,
    UNIQUE(vehicle_length_m, pallet_type)
);

-- 기본 데이터 삽입
INSERT INTO vehicle_capacity_rules VALUES
(9.5, '11형', 20, '9.5m 차량 11형 팔레트'),
(9.5, '12형', 17, '9.5m 차량 12형 팔레트'),
... 
```

#### Python 사용 예시
```python
from app.utils.phase1_constraints import validate_vehicle_capacity

# 차량 적재 가능 여부 검증
is_valid, message = validate_vehicle_capacity(
    vehicle_length_m=9.5,
    pallet_type="12형",
    requested_pallets=15
)
print(is_valid, message)  # (True, "가능: 15/17 팔레트")

# 적재율 계산
from app.utils.phase1_constraints import calculate_vehicle_utilization

utilization = calculate_vehicle_utilization(
    vehicle_length_m=9.5,
    pallet_type="12형",
    current_load=10
)
print(f"{utilization:.1%}")  # 58.8%
```

---

## 🚀 배포 절차

### 1. 데이터베이스 마이그레이션 실행

```bash
# 서버 접속
ssh root@139.150.11.99
cd /root/uvis

# 마이그레이션 SQL 업로드 (로컬에서)
scp backend/migrations/phase1_constraints.sql root@139.150.11.99:/root/uvis/

# 서버에서 마이그레이션 실행
docker exec -i uvis-db psql -U postgres -d uvis < phase1_constraints.sql

# 결과 확인
docker exec -it uvis-db psql -U postgres -d uvis -c "
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'vehicles' 
      AND column_name LIKE '%pallet%' OR column_name LIKE '%support%';
"
```

### 2. Backend 코드 배포

```bash
# 로컬에서 코드 커밋
cd /home/user/webapp
git add backend/app/utils/phase1_constraints.py
git add backend/migrations/phase1_constraints.sql
git commit -m "feat: Phase 1 - Basic constraints implementation

- Add pallet type distinction (11형/12형)
- Add temperature zone matching
- Add 24-hour delivery time calculation
- Add vehicle capacity rules by length"

git push origin main

# 서버에서 코드 업데이트
cd /root/uvis
git pull origin main

# Backend 재빌드 및 재시작
docker-compose -f docker-compose.prod.yml up -d --build backend

# 상태 확인
docker ps | grep backend
docker logs backend --tail 20
```

### 3. 기능 테스트

```bash
# Python 유틸리티 함수 테스트
docker exec -it uvis-backend python -c "
from app.utils.phase1_constraints import (
    get_vehicle_capacity_by_pallet_type,
    calculate_delivery_datetime
)
from datetime import datetime

# 테스트 1: 파렛트 용량
print('9.5m 12형:', get_vehicle_capacity_by_pallet_type(9.5, '12형'))

# 테스트 2: 하차시간 계산
order_time = datetime(2026, 2, 2, 20, 0)
delivery = calculate_delivery_datetime(order_time, '04:00')
print('하차시간:', delivery)
"
```

---

## 📊 검증 체크리스트

### 데이터베이스
- [ ] `clients.pallet_type` 필드 생성 확인
- [ ] `vehicles.max_pallets_11type` 필드 생성 확인
- [ ] `vehicles.supports_frozen/chilled/ambient` 필드 생성 확인
- [ ] `orders.calculated_delivery_datetime` 필드 생성 확인
- [ ] `vehicle_capacity_rules` 테이블 생성 확인
- [ ] 기본 용량 규칙 데이터 8건 삽입 확인

### 코드
- [ ] `phase1_constraints.py` 파일 생성 확인
- [ ] 모든 유틸리티 함수 import 성공
- [ ] 단위 테스트 통과

### 기능
- [ ] 9.5m 차량 12형 용량 = 17개 확인
- [ ] 냉동 차량이 냉동 주문 매칭 확인
- [ ] 20시 주문 04시 하차 → 다음날 계산 확인
- [ ] 차량 적재율 계산 정상 동작 확인

---

## 🔍 트러블슈팅

### 문제 1: 마이그레이션 실행 오류

**증상:**
```
ERROR: column "pallet_type" already exists
```

**해결:**
```sql
-- 이미 실행된 경우 무시됨 (IF NOT EXISTS 사용)
-- 강제 재실행 필요시:
ALTER TABLE clients DROP COLUMN IF EXISTS pallet_type CASCADE;
-- 그 후 마이그레이션 재실행
```

### 문제 2: Import 오류

**증상:**
```python
ModuleNotFoundError: No module named 'app.utils.phase1_constraints'
```

**해결:**
```bash
# Backend 컨테이너 재빌드
docker-compose -f docker-compose.prod.yml up -d --build backend

# 또는 파일 권한 확인
chmod 644 backend/app/utils/phase1_constraints.py
```

### 문제 3: 차량 용량이 NULL

**증상:**
```
vehicles.max_pallets_11type = NULL
```

**해결:**
```sql
-- 마이그레이션의 6번 섹션 재실행
UPDATE vehicles
SET 
    max_pallets_11type = COALESCE(max_pallets_11type, max_pallets),
    max_pallets_12type = COALESCE(max_pallets_12type, FLOOR(max_pallets * 0.85)::INTEGER)
WHERE max_pallets_11type IS NULL;
```

---

## 📈 다음 단계 (Phase 2)

Phase 1 완료 후:
1. ✅ 실시간 ETA 모니터링
2. ✅ 지연 위험 알림 시스템
3. ✅ WebSocket 대시보드

---

## 📞 문의

Phase 1 구현 중 문제가 발생하면:
1. `PHASE1_IMPLEMENTATION_GUIDE.md` 트러블슈팅 섹션 확인
2. 로그 확인: `docker logs uvis-backend --tail 100`
3. DB 상태 확인: `docker exec -it uvis-db psql -U postgres -d uvis`

---

**✅ Phase 1 구현 완료!** 🎉
