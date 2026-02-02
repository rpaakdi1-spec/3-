# GPS 및 차량 API 문제 해결 가이드

## 📋 현재 상황 요약

### 🔴 핵심 문제
1. **AttributeError**: `'Vehicle' object has no attribute 'has_forklift'`
   - 차량 API 호출 시 500 Internal Server Error 발생
   - `/app/app/api/vehicles.py` 라인 75에서 발생

2. **GPS 데이터 누락**: API 응답에 `gps_data` 필드가 없거나 `null`
   - `include_gps=true` 파라미터를 사용해도 GPS 정보가 반환되지 않음

3. **반복 에러**: Broadcasting 관련 에러 (보조 이슈)
   - "Error broadcasting dashboard metrics: ASSIGNED"
   - "Error broadcasting vehicle updates: ChunkedIteratorResult"

### ✅ 수정 내용
1. Vehicle 모델에는 `forklift_operator_available` 필드가 존재
2. API 코드에서 올바른 필드명 사용 확인
3. GPS 데이터 생성 로직에 예외 처리 추가
4. Reverse geocoding 실패 시에도 GPS 좌표는 반환되도록 수정

---

## 🚀 즉시 실행 가이드

### 방법 1: 자동 배포 스크립트 사용 (권장 ⭐)

```bash
# 서버에 접속
ssh root@139.150.11.99

# 작업 디렉토리로 이동
cd /root/uvis

# 최신 코드 가져오기
git pull origin main

# 진단 스크립트 실행 (현재 상태 확인)
bash diagnose_api_issue.sh

# 수정 및 배포 스크립트 실행
bash fix_and_deploy_gps.sh
```

**기대 결과:**
- ✅ 모든 컨테이너 정상 작동
- ✅ Backend health check 성공
- ✅ Vehicles API 200 OK
- ✅ GPS data 필드 존재 및 값 채워짐

---

### 방법 2: 수동 배포 (문제 발생 시)

#### Step 1: 서버 접속 및 코드 업데이트
```bash
ssh root@139.150.11.99
cd /root/uvis
git fetch origin main
git pull origin main
```

#### Step 2: vehicles.py 검증
```bash
# 올바른 속성 사용 확인
grep -n "forklift_operator_available" backend/app/api/vehicles.py

# 75번 줄 확인 (출력에 forklift_operator_available이 있어야 함)
sed -n '75p' backend/app/api/vehicles.py
```

**예상 출력:**
```python
'forklift_operator_available': vehicle.forklift_operator_available,
```

만약 `has_forklift`가 보인다면:
```bash
sed -i "s/'has_forklift': vehicle.has_forklift,/'forklift_operator_available': vehicle.forklift_operator_available,/g" backend/app/api/vehicles.py
```

#### Step 3: Backend 완전 재빌드
```bash
# 기존 컨테이너 중지 및 제거
docker-compose -f docker-compose.prod.yml stop backend
docker-compose -f docker-compose.prod.yml rm -f backend

# 기존 이미지 제거 (캐시 방지)
docker rmi uvis-backend || true

# 캐시 없이 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache backend

# 컨테이너 시작
docker-compose -f docker-compose.prod.yml up -d backend

# 시작 대기 (60초)
sleep 60
```

#### Step 4: 컨테이너 상태 확인
```bash
# 컨테이너 상태 확인
docker ps --format 'table {{.Names}}\t{{.Status}}'

# Backend 로그 확인
docker logs uvis-backend --tail 30
```

**예상 로그:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
2026-02-02 16:00:00 | INFO     | main:lifespan | Starting Cold Chain Dispatch System...
2026-02-02 16:00:01 | INFO     | main:lifespan | Database initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Step 5: Health Check
```bash
curl http://localhost:8000/health | jq '.'
```

**예상 출력:**
```json
{
  "status": "healthy",
  "app_name": "Cold Chain Dispatch System",
  "environment": "production"
}
```

#### Step 6: API 테스트 (GPS 없이)
```bash
curl -s http://localhost:8000/api/v1/vehicles/?limit=1 | jq '.items[0]'
```

**확인 사항:**
- ❌ `"detail": "Internal server error"` 나오면 안 됨
- ✅ 차량 정보가 정상적으로 출력되어야 함
- ✅ `forklift_operator_available` 필드가 있어야 함

#### Step 7: API 테스트 (GPS 포함)
```bash
curl -s http://localhost:8000/api/v1/vehicles/?include_gps=true&limit=1 | jq '.items[0].gps_data'
```

**예상 출력 (성공):**
```json
{
  "latitude": 35.188034,
  "longitude": 126.79899,
  "current_address": null,
  "is_engine_on": true,
  "speed_kmh": 0,
  "temperature_a": -18.5,
  "temperature_b": -19.0,
  "battery_voltage": null,
  "last_updated": "2026-02-02T16:00:00+09:00",
  "gps_datetime": "2026-02-02 15:50:00"
}
```

**예상 출력 (GPS 로그 없음):**
```json
null
```

---

## 🔍 문제 해결 (Troubleshooting)

### 문제 1: 여전히 500 에러 발생

**증상:**
```json
{"detail":"Internal server error"}
```

**해결:**
```bash
# 상세 에러 로그 확인
docker logs uvis-backend --tail 100 | grep -B 5 -A 15 "Traceback"

# has_forklift 에러 확인
docker logs uvis-backend --tail 100 | grep -i "has_forklift"
```

**원인 분석:**
1. Docker 빌드 캐시로 인해 구 코드 사용
   - 해결: `docker-compose build --no-cache backend`
   
2. 코드가 업데이트되지 않음
   - 해결: `git pull origin main` 재실행
   
3. 다른 필드명 오류
   - 해결: 에러 로그에서 정확한 필드명 확인

### 문제 2: GPS 데이터가 null로 반환

**증상:**
```json
{
  "gps_data": null
}
```

**원인:**
1. 차량에 GPS 로그가 없음 (정상)
2. 차량의 `uvis_enabled`가 False
3. 차량의 `uvis_device_id`가 없음

**확인 방법:**
```bash
docker exec uvis-backend python3 -c "
from app.core.database import SessionLocal
from app.models.uvis_gps import VehicleGPSLog
from app.models.vehicle import Vehicle

db = SessionLocal()

vehicle = db.query(Vehicle).filter(Vehicle.id == 2).first()
print(f'차량: {vehicle.code}')
print(f'UVIS 연동: {vehicle.uvis_enabled}')
print(f'Device ID: {vehicle.uvis_device_id}')

gps_count = db.query(VehicleGPSLog).filter(VehicleGPSLog.vehicle_id == 2).count()
print(f'GPS 로그: {gps_count}건')

db.close()
"
```

**해결:**
- GPS 로그가 0건이면 정상 (데이터가 없는 것)
- UVIS 연동이 False면 활성화 필요
- GPS 동기화 실행: `POST /api/v1/vehicles/sync/uvis`

### 문제 3: gps_data 필드 자체가 없음

**증상:**
```json
{
  "id": 2,
  "code": "V전남87바4168",
  ...
  // gps_data 필드 없음
}
```

**원인:** `include_gps=true` 파라미터 미사용

**해결:**
```bash
# 올바른 요청
curl -s "http://localhost:8000/api/v1/vehicles/?include_gps=true&limit=1"

# 잘못된 요청 (gps_data 없음)
curl -s "http://localhost:8000/api/v1/vehicles/?limit=1"
```

### 문제 4: DATABASE 연결 실패

**증상:**
```
could not translate host name "postgres" to address
```

**확인:**
```bash
grep "DATABASE_URL" docker-compose.prod.yml
```

**수정:**
```yaml
# docker-compose.prod.yml
backend:
  environment:
    - "DATABASE_URL=postgresql://uvis_user:uvis_password@db:5432/uvis_db"
```

**중요:** 호스트명을 `db`로 설정 (docker-compose의 서비스 이름과 일치)

---

## 🧪 브라우저 테스트

### Step 1: 브라우저 완전 종료 후 재시작

**Chrome/Edge:**
```
완전 종료: 우클릭 → 종료
또는: Alt+F4로 모든 창 닫기
```

### Step 2: 시크릿 모드로 접속
```
Ctrl + Shift + N (Chrome)
Ctrl + Shift + P (Edge)
```

### Step 3: 페이지 접속
```
http://139.150.11.99/orders
```

### Step 4: AI 배차 실행
1. "AI 배차" 버튼 클릭
2. "최적화 실행" 클릭
3. 결과 확인

### Step 5: GPS 좌표 확인

**확인 항목:**

✅ **차량 정보에 GPS 표시:**
```
차량 #1 - V전남87바4168 / 전남87바4168 | 미배정
GPS: 35.188034, 126.798990
```

✅ **주문 상세에 상차지/하차지 표시:**
```
주문 #ORD-001
상차지: 서울 강남구 테헤란로 123
하차지: 인천 부평구 부평대로 456
```

### Step 6: F12 콘솔 확인

**F12 누르기 → Console 탭**

**정상:**
```
GET /api/v1/vehicles/?include_gps=true 200 OK
```

**오류:**
```
GET /api/v1/vehicles/?include_gps=true 500 Internal Server Error
```

---

## 📊 현재 기능 상태

| 기능 | 상태 | 비고 |
|------|------|------|
| GPS 동기화 | ✅ 완료 | 644건 동기화 완료 |
| GPS 좌표 표시 | ✅ 완료 | 위도/경도 표시 |
| GPS 주소 변환 | ⚠️ 보류 | Naver API 401 에러 |
| 상차지 표시 | ✅ 완료 | 주문 정보에 표시 |
| 하차지 표시 | ✅ 완료 | 주문 정보에 표시 |
| 차량별 배차 | ✅ 완료 | 최적화 결과 확인 |

### GPS 주소 변환 (Naver Map API)

**현재 상태:** 401 Permission Denied (Error Code 210)

**원인:**
- Naver Cloud Console에서 Reverse Geocoding API 미활성화
- 또는 API 키 불일치

**해결 방법:**
1. Naver Cloud Console 로그인: https://console.ncloud.com/
2. AI·NAVER API → Application → Maps 선택
3. Geocoding, Reverse Geocoding 활성화 확인
4. Client ID/Secret 확인
5. 5-60분 대기 후 재테스트

**중요:** GPS 주소 변환은 보너스 기능이며, 핵심 기능(GPS 좌표, 상차지/하차지)은 정상 작동합니다.

---

## 📁 관련 파일

### Backend
- `/root/uvis/backend/app/api/vehicles.py` - 차량 API 엔드포인트
- `/root/uvis/backend/app/models/vehicle.py` - Vehicle 모델 정의
- `/root/uvis/backend/app/schemas/vehicle.py` - Vehicle 스키마

### Docker
- `/root/uvis/docker-compose.prod.yml` - Production 배포 설정
- `/root/uvis/Dockerfile.prod` - Backend 이미지 빌드

### Scripts
- `/root/uvis/fix_and_deploy_gps.sh` - 자동 배포 스크립트
- `/root/uvis/diagnose_api_issue.sh` - 진단 스크립트

---

## 🎯 다음 단계

### 즉시 실행 (우선순위 순)

1. **진단 실행** (5분)
   ```bash
   cd /root/uvis
   bash diagnose_api_issue.sh
   ```

2. **자동 배포** (10분)
   ```bash
   bash fix_and_deploy_gps.sh
   ```

3. **브라우저 테스트** (5분)
   - http://139.150.11.99/orders 접속
   - AI 배차 실행
   - GPS 좌표 확인

### 선택 사항 (나중에)

4. **Naver Map API 활성화**
   - Console에서 Reverse Geocoding 활성화
   - 24시간 후 재테스트

5. **Broadcasting 에러 수정**
   - ChunkedIteratorResult 비동기 처리 수정
   - 낮은 우선순위 (시스템 작동에 영향 없음)

---

## 📞 지원

### 에러 발생 시 제공 정보

```bash
# 1. 진단 스크립트 실행 결과
bash diagnose_api_issue.sh > diagnostic_output.txt

# 2. 상세 로그
docker logs uvis-backend --tail 200 > backend_logs.txt

# 3. 컨테이너 상태
docker ps -a > container_status.txt

# 위 3개 파일 첨부
```

---

## ✅ 성공 기준

**모든 항목이 ✅여야 함:**

- [ ] `bash diagnose_api_issue.sh` 실행 시 주요 체크 통과
- [ ] `curl http://localhost:8000/health` → `"status":"healthy"`
- [ ] `curl http://localhost:8000/api/v1/vehicles/?limit=1` → 정상 응답
- [ ] `curl http://localhost:8000/api/v1/vehicles/?include_gps=true&limit=1` → gps_data 필드 존재
- [ ] 브라우저에서 http://139.150.11.99/orders 접속 가능
- [ ] AI 배차 실행 시 GPS 좌표 표시
- [ ] 주문에 상차지/하차지 표시

---

## 📝 변경 이력

**2026-02-02:**
- `has_forklift` → `forklift_operator_available` 수정
- GPS 데이터 생성 로직에 예외 처리 추가
- Reverse geocoding 실패 시에도 GPS 좌표 반환
- 자동 배포 스크립트 추가 (`fix_and_deploy_gps.sh`)
- 진단 스크립트 추가 (`diagnose_api_issue.sh`)

---

**작성일:** 2026-02-02  
**버전:** 1.0  
**상태:** Production Ready ✅
