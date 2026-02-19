# 배차 최적화 엔드포인트 수정 배포 가이드

## 문제 상황
- POST `/api/v1/dispatches/optimize` 엔드포인트 호출 시 500 에러 발생
- 에러: `TypeError: DispatchOptimizationService.optimize_dispatch() got an unexpected keyword argument 'vehicle_ids'`
- 원인: 서버의 `dispatches.py` 파일이 이전 버전으로, `AdvancedDispatchOptimizationService`를 제대로 사용하지 않음

## 해결 방법

### 방법 1: 전체 파일 교체 (권장)

```bash
# 1. 로컬에서 서버로 파일 복사
cd /home/user/webapp
scp backend/app/api/dispatches.py root@139.150.11.99:/root/uvis/backend/app/api/

# 2. 서버에서 Docker 재시작
ssh root@139.150.11.99 "cd /root/uvis && docker restart uvis-backend"

# 3. 10초 대기 후 컨테이너 확인
ssh root@139.150.11.99 "docker ps | grep uvis-backend"
```

### 방법 2: 서버에서 직접 수정

서버에 SSH 접속 후:

```bash
cd /root/uvis/backend/app/api

# 백업
cp dispatches.py dispatches.py.$(date +%Y%m%d_%H%M%S).backup

# 파일 확인
head -60 dispatches.py
```

**수정할 라인 29-56:**

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
    optimizer = AdvancedDispatchOptimizationService(db)
    
    result = await optimizer.optimize_dispatch_cvrptw(
        order_ids=request.order_ids,
        vehicle_ids=request.vehicle_ids,
        dispatch_date=request.dispatch_date,
        time_limit_seconds=15,  # 빠른 실행 (15초)
        use_time_windows=False,  # 시간 제약 비활성화
        use_real_routing=False   # Haversine 거리 사용
    )
    
    return OptimizationResponse(**result)
```

### 배포 후 확인

```bash
# 1. 컨테이너 재시작
cd /root/uvis
docker restart uvis-backend
sleep 10

# 2. 로그 확인 (에러가 없어야 함)
docker logs uvis-backend --tail 30

# 3. API 테스트
curl -X POST "http://localhost:8000/api/v1/dispatches/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "order_ids": [1, 2],
    "vehicle_ids": [],
    "dispatch_date": "2026-02-19"
  }' | jq .

# 4. 성공 응답 예시:
# {
#   "success": true,
#   "message": "배차 최적화 완료",
#   "total_orders": 2,
#   "assigned_orders": X,
#   "unassigned_orders": Y,
#   "total_distance": Z,
#   "execution_time": W
# }
```

## 추가 문제 해결

### 문제 1: Import 누락
만약 여전히 에러가 발생하면 import 확인:

```bash
grep -n "AdvancedDispatchOptimizationService" /root/uvis/backend/app/api/dispatches.py
```

**22-23번 라인에 다음이 있어야 함:**
```python
from app.services.dispatch_optimization_service import DispatchOptimizationService
from app.services.cvrptw_service import AdvancedDispatchOptimizationService
```

### 문제 2: 이중 import
중복된 import가 있으면 제거:

```bash
# 중복 확인
grep -n "from app.services.cvrptw_service import" /root/uvis/backend/app/api/dispatches.py

# 중복이 있다면 하나만 남기고 삭제
vi /root/uvis/backend/app/api/dispatches.py
```

### 문제 3: Geocoding 401 에러
현재 Naver API 역지오코딩에서 401 에러가 발생하고 있습니다. 임시 해결책:

```python
# naver_map_service.py에서 에러 발생 시 기본값 반환하도록 수정
except Exception as e:
    logger.warning(f"Geocoding failed: {str(e)}, using default address")
    return "주소 정보 없음"
```

## 테스트 시나리오

### 1. 주문 관리 테스트
```bash
curl http://localhost:8000/api/v1/orders | jq '.data | length'
# 예상: 주문 목록 반환
```

### 2. 배차 대기 주문 조회
```bash
curl "http://localhost:8000/api/v1/orders?status=배차대기" | jq '.data | length'
# 예상: 배차 대기 중인 주문 수 반환
```

### 3. AI 배차 최적화
```bash
curl -X POST "http://localhost:8000/api/v1/dispatches/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "order_ids": [1, 2, 3],
    "vehicle_ids": [],
    "dispatch_date": "2026-02-19"
  }' | jq .
# 예상: success=true, 배차 계획 반환
```

### 4. 고급 CVRPTW 최적화
```bash
curl -X POST "http://localhost:8000/api/v1/dispatches/optimize-cvrptw?time_limit=30&use_time_windows=true" \
  -H "Content-Type: application/json" \
  -d '{
    "order_ids": [1, 2, 3],
    "vehicle_ids": [],
    "dispatch_date": "2026-02-19"
  }' | jq .
# 예상: success=true, 더 최적화된 배차 계획
```

### 5. 배차 내역 조회
```bash
curl http://localhost:8000/api/v1/dispatches | jq '.data | length'
# 예상: 배차 기록 수 반환
```

### 6. 대시보드 통계
```bash
curl http://localhost:8000/api/v1/dispatches/dashboard | jq .
# 예상: 실시간 통계 반환
```

## 성공 기준

✅ **모든 테스트가 통과해야 함:**
1. 주문 목록 조회 성공
2. 배차 대기 주문 조회 성공 (12~15건)
3. 기본 배차 최적화 성공 (200 응답, success=true)
4. 고급 CVRPTW 최적화 성공
5. 배차 내역 조회 성공 (437건)
6. 대시보드 통계 조회 성공

## 현재 상태

- ✅ 로컬 코드: 정상 (`AdvancedDispatchOptimizationService` 사용)
- ❌ 서버 코드: 구버전 (`DispatchOptimizationService` 사용 또는 잘못된 함수 호출)
- 🔄 필요 작업: 서버 코드 업데이트 + 재배포

## 문의사항

배포 중 문제가 발생하면:
1. 에러 로그 전체를 공유해주세요: `docker logs uvis-backend --tail 50`
2. 파일 내용 확인: `head -60 /root/uvis/backend/app/api/dispatches.py`
3. Import 확인: `grep -n "import" /root/uvis/backend/app/api/dispatches.py | head -25`
