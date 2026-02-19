# 배차 최적화 문제 해결 가이드

## 🔴 현재 문제

**증상:**
```
POST /api/v1/dispatches/optimize
Response: 500 Internal Server Error
Error: TypeError: DispatchOptimizationService.optimize_dispatch() got an unexpected keyword argument 'vehicle_ids'
```

**원인:**
서버의 `dispatches.py` 파일이 구버전이거나 잘못 수정되어 있음

## 📊 상태 점검 체크리스트

### 1. 서버 측 파일 확인

```bash
# 서버 SSH 접속
ssh root@139.150.11.99

# 파일 존재 확인
ls -lh /root/uvis/backend/app/api/dispatches.py

# Import 라인 확인 (22-23번)
sed -n '22,23p' /root/uvis/backend/app/api/dispatches.py
```

**예상 결과:**
```python
from app.services.dispatch_optimization_service import DispatchOptimizationService
from app.services.cvrptw_service import AdvancedDispatchOptimizationService
```

### 2. Optimizer 코드 확인

```bash
# 29-56번 라인 확인
sed -n '29,56p' /root/uvis/backend/app/api/dispatches.py
```

**예상 결과:**
```python
@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_dispatch(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    AI 기반 배차 최적화 (기본 알고리즘)
    
    주어진 주문들에 대해 최적의 배차 계획을 생성합니다.
    - 온도대별 차량 매칭
    - 적재 용량 제약 (팔레트, 중량)
    - 거리 최적화
    
    Note: 내부적으로 CVRPTW 알고리즘을 사용합니다 (빠른 설정).
    """
    # 기본 최적화는 CVRPTW를 사용 (빠른 실행)
    optimizer = AdvancedDispatchOptimizationService(db)  # ✓ 여기!
    
    result = await optimizer.optimize_dispatch_cvrptw(  # ✓ 여기!
        order_ids=request.order_ids,
        vehicle_ids=request.vehicle_ids,
        dispatch_date=request.dispatch_date,  # ✓ 콤마!
        time_limit_seconds=15,  # 빠른 실행 (15초)
        use_time_windows=False,  # 시간 제약 비활성화
        use_real_routing=False   # Haversine 거리 사용
    )
    
    return OptimizationResponse(**result)
```

### 3. Docker 컨테이너 상태

```bash
# 컨테이너 실행 확인
docker ps | grep uvis-backend

# 최근 로그 확인 (에러 검색)
docker logs uvis-backend --tail 50 | grep -i error

# 실시간 로그 (새 터미널에서)
docker logs -f uvis-backend
```

## 🛠️ 해결 방법

### 방법 A: 자동 수정 스크립트 (권장)

**1단계: 스크립트를 서버로 복사**

로컬에서 실행:
```bash
cd /home/user/webapp
scp server_fix_optimization.sh root@139.150.11.99:/root/
```

**2단계: 서버에서 스크립트 실행**

서버에서 실행:
```bash
cd /root
bash server_fix_optimization.sh
```

스크립트는:
- 자동으로 백업 생성
- Import 추가
- 함수 호출 수정
- 파라미터 추가
- Docker 재시작 (선택)
- 결과 확인

### 방법 B: 수동 수정

**1단계: 서버 접속 및 백업**

```bash
ssh root@139.150.11.99
cd /root/uvis/backend/app/api
cp dispatches.py dispatches.py.backup_$(date +%Y%m%d_%H%M%S)
```

**2단계: 파일 수정**

```bash
vi dispatches.py
```

**수정 사항:**

1. **22-23번 라인 (Import 확인/추가)**
```python
from app.services.dispatch_optimization_service import DispatchOptimizationService
from app.services.cvrptw_service import AdvancedDispatchOptimizationService
```

2. **44번 라인 (Optimizer 변경)**
```python
# 변경 전:
optimizer = DispatchOptimizationService(db)

# 변경 후:
optimizer = AdvancedDispatchOptimizationService(db)
```

3. **46-52번 라인 (함수 호출 변경)**
```python
# 변경 전:
result = await optimizer.optimize_dispatch(
    order_ids=request.order_ids,
    vehicle_ids=request.vehicle_ids,
    dispatch_date=request.dispatch_date
)

# 변경 후:
result = await optimizer.optimize_dispatch_cvrptw(
    order_ids=request.order_ids,
    vehicle_ids=request.vehicle_ids,
    dispatch_date=request.dispatch_date,
    time_limit_seconds=15,
    use_time_windows=False,
    use_real_routing=False
)
```

**3단계: 저장 및 종료**
- ESC 키
- `:wq` 입력
- Enter

**4단계: 변경 확인**

```bash
sed -n '29,56p' dispatches.py
```

**5단계: Docker 재시작**

```bash
cd /root/uvis
docker restart uvis-backend
sleep 10
docker ps | grep uvis-backend
```

### 방법 C: 파일 전체 교체

**로컬에서 실행:**

```bash
cd /home/user/webapp
scp backend/app/api/dispatches.py root@139.150.11.99:/root/uvis/backend/app/api/
```

**서버에서 실행:**

```bash
cd /root/uvis
docker restart uvis-backend
sleep 10
docker logs uvis-backend --tail 30
```

## 🧪 배포 후 테스트

### 테스트 1: 컨테이너 상태

```bash
docker ps | grep uvis-backend
```

**예상 결과:**
```
CONTAINER ID   IMAGE              STATUS          PORTS
xxx            uvis-backend       Up 2 minutes    0.0.0.0:8000->8000/tcp
```

### 테스트 2: 로그 확인

```bash
docker logs uvis-backend --tail 30
```

**예상 결과:** 에러 없이 정상 실행 로그

### 테스트 3: API 호출

```bash
curl -X POST "http://localhost:8000/api/v1/dispatches/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "order_ids": [1, 2],
    "vehicle_ids": [],
    "dispatch_date": "2026-02-19"
  }' | jq .
```

**예상 성공 응답:**
```json
{
  "success": true,
  "message": "배차 최적화 완료",
  "total_orders": 2,
  "assigned_orders": 2,
  "unassigned_orders": 0,
  "total_distance": 15.5,
  "execution_time": 2.3
}
```

**예상 실패 응답 (주문 없음):**
```json
{
  "success": false,
  "message": "배차할 주문이 없습니다.",
  "total_orders": 0
}
```

### 테스트 4: 통합 테스트 (로컬)

```bash
cd /home/user/webapp
python3 test_dispatch_flow.py
```

**예상 결과:**
```
테스트 요약:
총 테스트 수: 6
성공: 6
실패: 0
성공률: 100.0%
```

## ❓ 자주 발생하는 문제

### 문제 1: Import 에러

**증상:**
```
ModuleNotFoundError: No module named 'app.services.cvrptw_service'
```

**해결:**
```bash
# 파일 존재 확인
ls -lh /root/uvis/backend/app/services/cvrptw_service.py

# 파일이 없으면 Git에서 Pull
cd /root/uvis
git pull origin main

# Docker 재빌드 (필요시)
docker-compose build backend
docker restart uvis-backend
```

### 문제 2: 함수 시그니처 불일치

**증상:**
```
TypeError: optimize_dispatch_cvrptw() got an unexpected keyword argument 'xxx'
```

**해결:**
```bash
# cvrptw_service.py 확인
grep -A 20 "def optimize_dispatch_cvrptw" /root/uvis/backend/app/services/cvrptw_service.py

# 파라미터 순서 확인:
# order_ids, vehicle_ids=None, dispatch_date, time_limit_seconds, use_time_windows, use_real_routing
```

### 문제 3: 데이터베이스 연결 실패

**증상:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**해결:**
```bash
# PostgreSQL 컨테이너 확인
docker ps | grep postgres

# 재시작
docker restart uvis-postgres
sleep 5
docker restart uvis-backend
```

### 문제 4: Geocoding 401 에러

**증상:**
```
NaverMapService reverse_geocode failed: 401 Permission Denied
```

**해결:**

이 에러는 정상이며 배차 최적화에 영향을 주지 않습니다.
Naver API 키가 역지오코딩을 지원하지 않아 발생하는 것으로, 주소 정보만 누락되고 배차는 정상 작동합니다.

필요시 `.env` 파일에서 API 키를 업데이트:
```bash
vi /root/uvis/.env
# NAVER_CLIENT_ID=xxx
# NAVER_CLIENT_SECRET=xxx
```

### 문제 5: CVRPTW 결과 0건

**증상:**
```json
{
  "success": true,
  "message": "배차 최적화 완료",
  "assigned_orders": 0,
  "unassigned_orders": 10
}
```

**원인:**
- 주문 데이터 불완전 (픽업/배송 주소 없음)
- 차량 GPS 좌표 없음
- 온도대 불일치
- 용량 부족

**해결:**
```bash
# 주문 데이터 확인
curl "http://localhost:8000/api/v1/orders?status=배차대기" | jq '.data[] | {id, pickup_address, delivery_address, temperature_zone}'

# 차량 데이터 확인
curl "http://localhost:8000/api/v1/vehicles" | jq '.data[] | {id, vehicle_number, temperature_zone, gps_latitude, gps_longitude}'
```

## 📝 로그 분석

### 정상 로그 패턴

```
INFO: CVRPTW 배차 최적화 시작...
INFO: 유효한 주문: 10건
INFO: 유효한 차량: 5건
INFO: OR-Tools 최적화 실행 중... (제한시간: 15초)
INFO: 최적화 완료: 10/10 주문 배차, 총 거리: 120.5km, 실행시간: 12.3초
```

### 에러 로그 패턴

```
ERROR: TypeError: DispatchOptimizationService.optimize_dispatch() got an unexpected keyword argument 'vehicle_ids'
  File "/app/app/api/dispatches.py", line 44, in optimize_dispatch
    result = await optimizer.optimize_dispatch(...)
```

이 경우 `optimize_dispatch` → `optimize_dispatch_cvrptw`로 변경 필요

## 🎯 체크포인트

배포 전:
- [ ] 로컬 코드 최신 상태 확인
- [ ] 백업 생성 확인
- [ ] Import 라인 확인

배포 후:
- [ ] Docker 재시작 완료
- [ ] 로그에 에러 없음
- [ ] API 테스트 성공 (200 응답)
- [ ] 통합 테스트 100% 통과

## 📞 지원

문제가 지속되면 다음 정보를 공유해주세요:

1. **에러 로그 전체:**
```bash
docker logs uvis-backend --tail 100 > backend_error.log
cat backend_error.log
```

2. **파일 상태:**
```bash
head -60 /root/uvis/backend/app/api/dispatches.py > dispatches_current.txt
cat dispatches_current.txt
```

3. **Import 라인:**
```bash
grep -n "import" /root/uvis/backend/app/api/dispatches.py | head -25
```

4. **Docker 상태:**
```bash
docker ps -a | grep uvis
docker-compose ps
```
