# Telemetry API 및 Redis 인증 수정 가이드

## 📋 문제 요약

### 발견된 문제들

1. **Telemetry API 500 에러**
   - 원인: `VehicleLocation` 모델에 `timestamp` 컬럼이 없음
   - 증상: `AttributeError: type object 'VehicleLocation' has no attribute 'timestamp'`
   - 영향: `/api/v1/telemetry/vehicles/status` 엔드포인트 동작 불가

2. **Redis 인증 실패**
   - 원인: 잘못된 비밀번호 사용 (`redispass` 대신 실제 비밀번호 사용 필요)
   - 증상: `WRONGPASS invalid username-password pair` 또는 `AUTH failed`
   - 영향: AB Test API 및 캐시 기능 동작 불가

3. **Clients API 누락 컬럼**
   - 원인: `clients` 테이블에 여러 필수 컬럼 누락
   - 증상: `UndefinedColumn: column clients.xxx does not exist`
   - 영향: 고객 관리 API 동작 불가

## ✅ 적용된 수정 사항

### 1. VehicleLocation 모델 업데이트

**파일**: `backend/app/models/vehicle_location.py`

```python
# 메타데이터
recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
timestamp = Column(DateTime, nullable=True, default=datetime.utcnow, index=True)  # 타임스탬프 (호환성)
is_ignition_on = Column(Boolean, default=True)  # 시동 상태
```

**변경 사항**:
- `timestamp` 컬럼 추가 (기존 `recorded_at`과 동일한 값으로 사용)
- `vehicle_telemetry_service.py`에서 사용하는 `timestamp` 속성 지원

### 2. PostgreSQL 테이블 스키마 업데이트

**실행된 SQL**:
```sql
-- vehicle_locations 테이블에 timestamp 컬럼 추가
ALTER TABLE vehicle_locations 
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 기존 데이터에 recorded_at 값 복사
UPDATE vehicle_locations 
SET timestamp = recorded_at 
WHERE timestamp IS NULL;

-- clients 테이블에 누락된 컬럼들 추가
ALTER TABLE clients ADD COLUMN IF NOT EXISTS address_detail VARCHAR(500);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS geocoded BOOLEAN DEFAULT false;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS geocode_error TEXT;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS pickup_start_time TIME;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS pickup_end_time TIME;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS delivery_start_time TIME;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS delivery_end_time TIME;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS forklift_operator_available BOOLEAN DEFAULT false;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS loading_time_minutes INTEGER DEFAULT 15;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS contact_person VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS notes TEXT;
```

### 3. Redis 비밀번호 설정 확인

**환경 변수** (`.env` 파일):
```env
REDIS_PASSWORD=pXrvuewL2gXRrc6NDpaAvDNWg
REDIS_URL=redis://:pXrvuewL2gXRrc6NDpaAvDNWg@redis:6379/0
```

**Docker Compose** (`docker-compose.yml`):
```yaml
redis:
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redispass}
  
backend:
  environment:
    REDIS_URL: redis://:${REDIS_PASSWORD:-redispass}@redis:6379/0
```

## 🚀 배포 방법

### 자동 배포 스크립트 사용

서버에서 다음 명령어를 실행:

```bash
cd /root/uvis

# 최신 코드 다운로드
git pull origin main

# 수정 스크립트 실행
bash FIX_TELEMETRY_AND_REDIS.sh
```

스크립트가 자동으로:
1. ✅ 최신 코드를 가져옴
2. ✅ Redis 비밀번호 확인
3. ✅ Redis 연결 테스트
4. ✅ 백엔드 재빌드 (업데이트된 모델 반영)
5. ✅ 백엔드 재시작
6. ✅ 헬스 체크
7. ✅ API 엔드포인트 테스트

### 수동 배포 (단계별)

#### 1단계: 코드 업데이트
```bash
cd /root/uvis
git pull origin main
```

#### 2단계: Redis 비밀번호 확인
```bash
grep "REDIS_PASSWORD=" .env
docker-compose exec redis redis-cli -a "pXrvuewL2gXRrc6NDpaAvDNWg" ping
```

#### 3단계: 백엔드 재빌드
```bash
docker-compose stop backend
docker-compose rm -f backend
docker-compose build --no-cache backend
docker-compose up -d backend
```

#### 4단계: 대기 및 확인
```bash
sleep 30
docker-compose ps backend
curl -s http://localhost:8000/api/v1/health | jq .
```

#### 5단계: API 테스트
```bash
# JWT 토큰 발급
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" | jq -r '.access_token')

# Telemetry API 테스트
curl -s -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/telemetry/vehicles/status | jq .

# AB Test API 테스트
curl -s -H "Authorization: Bearer ${TOKEN}" \
    http://localhost:8000/api/v1/ab-test/stats | jq .
```

## 🧪 테스트 체크리스트

배포 후 다음 항목들을 확인:

### ✅ 기본 헬스 체크
- [ ] Backend 컨테이너가 정상 실행 중 (`docker-compose ps backend`)
- [ ] 헬스 엔드포인트 응답 (`/api/v1/health` → 200 OK)
- [ ] Redis 연결 성공 (`redis-cli -a [password] ping` → PONG)

### ✅ API 엔드포인트
- [ ] Clients API: `GET /api/v1/clients/` → 200 OK (빈 배열 가능)
- [ ] Telemetry API: `GET /api/v1/telemetry/vehicles/status` → 200 OK (토큰 필요)
- [ ] AB Test API: `GET /api/v1/ab-test/stats` → 200 OK (토큰 필요)
- [ ] ML Predictions API: `GET /api/v1/ml/predictions` → 400 (모델 미학습) 또는 200

### ✅ 에러 로그 확인
```bash
# 최근 에러 로그 확인
docker-compose logs backend --tail 50 | grep -i "error\|exception"

# Telemetry 관련 로그
docker-compose logs backend --tail 50 | grep -i "telemetry"

# Redis 관련 로그
docker-compose logs backend --tail 50 | grep -i "redis"
```

**예상 결과**:
- ❌ `AttributeError: type object 'VehicleLocation' has no attribute 'timestamp'` → 더 이상 발생하지 않음
- ❌ `WRONGPASS invalid username-password pair` → 더 이상 발생하지 않음
- ❌ `UndefinedColumn: column clients.xxx does not exist` → 더 이상 발생하지 않음

## 🔧 문제 해결

### Telemetry API가 여전히 500 에러를 반환하는 경우

1. **모델이 제대로 업데이트되었는지 확인**:
```bash
cd /root/uvis
grep -n "timestamp" backend/app/models/vehicle_location.py
```
출력에 `timestamp = Column(...)` 라인이 있어야 함

2. **백엔드가 재빌드되었는지 확인**:
```bash
docker-compose images backend
```
이미지 생성 시간이 최근이어야 함

3. **백엔드 로그 확인**:
```bash
docker-compose logs backend --tail 100 | grep -A 10 "Traceback"
```

### Redis 인증이 여전히 실패하는 경우

1. **환경 변수 확인**:
```bash
docker-compose exec backend env | grep REDIS
```

2. **Redis 컨테이너 내부에서 테스트**:
```bash
docker-compose exec redis redis-cli
AUTH pXrvuewL2gXRrc6NDpaAvDNWg
ping
```

3. **Redis 재시작**:
```bash
docker-compose restart redis
sleep 10
docker-compose restart backend
```

### Clients API가 여전히 500 에러를 반환하는 경우

1. **테이블 스키마 확인**:
```bash
docker-compose exec -T db psql -U uvis_user -d uvis_db -c "\d clients"
```

2. **누락된 컬럼 확인**:
```bash
docker-compose logs backend --tail 50 | grep "UndefinedColumn"
```

3. **필요시 컬럼 추가**:
```bash
# 에러 메시지에서 누락된 컬럼 이름 확인 후
docker-compose exec -T db psql -U uvis_user -d uvis_db -c "
ALTER TABLE clients ADD COLUMN IF NOT EXISTS [column_name] [data_type];
"
```

## 📊 영향 받는 기능

### 수정 완료된 기능
- ✅ **실시간 차량 모니터링**: Telemetry API가 정상 동작
- ✅ **AB 테스트 통계**: Redis 인증 문제 해결로 정상 동작
- ✅ **고객 관리**: 누락된 컬럼 추가로 정상 동작
- ✅ **온도 알림**: 위치 데이터 조회 가능

### 추가 작업 필요
- ⚠️ **ML 예측 모델**: 모델 학습 필요 (`/api/v1/ml/train` 호출)
- ⚠️ **WebSocket 실시간 통신**: WebSocket 엔드포인트 구현 필요

## 📝 커밋 히스토리

```
f7b23b6 - feat: Add telemetry and Redis authentication fix script
eac74cd - fix: Add timestamp column to VehicleLocation model for telemetry service compatibility
195bd27 - fix: Add sidebar to Dispatch Monitoring page by wrapping with LayoutWrapper
```

## 🎯 다음 단계

1. **프론트엔드 사이드바 테스트**
   - 실시간 배차 모니터링 페이지에서 사이드바 표시 확인
   - 새로운 그룹화된 네비게이션 구조 확인

2. **ML 모델 학습**
   - `/api/v1/ml/train` 엔드포인트 호출하여 모델 학습
   - 학습 완료 후 예측 API 테스트

3. **WebSocket 구현**
   - 실시간 텔레메트리 WebSocket 엔드포인트 구현
   - 프론트엔드 WebSocket 연결 테스트

4. **모니터링 설정**
   - Prometheus, Grafana를 통한 시스템 모니터링
   - 에러 알림 설정

## 📞 지원

문제가 지속되는 경우:
1. 위의 "문제 해결" 섹션 참조
2. 백엔드 로그 전체 확인: `docker-compose logs backend --tail 200`
3. 데이터베이스 상태 확인: `docker-compose exec -T db psql -U uvis_user -d uvis_db`

---

**작성일**: 2026-02-27  
**버전**: 1.0  
**적용 대상**: UVIS 콜드체인 배차 시스템
