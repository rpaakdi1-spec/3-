# 🚨 Docker 코드 동기화 문제 해결 가이드

## 문제 상황

**증상**: 
- Git에서 코드를 업데이트하고 `docker-compose restart backend`를 실행했지만
- 여전히 이전 코드가 실행되고 있음
- ResponseValidationError가 계속 발생

**원인**:
1. **Python 바이트코드 캐시**: `.pyc` 파일이 오래된 상태로 남아있음
2. **Docker 볼륨 마운트 이슈**: 코드 변경이 컨테이너에 제대로 반영되지 않음
3. **FastAPI 자동 리로드 실패**: 개발 모드가 아니면 코드 변경을 감지하지 못함

---

## 해결 방법 (3단계)

### 🥉 방법 1: 간단한 재시작 (먼저 시도)

```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main
docker-compose -f docker-compose.prod.yml restart backend
sleep 30
```

**성공 확률**: 30%  
**소요 시간**: 1분

---

### 🥈 방법 2: Python 캐시 제거 후 재시작 (권장)

```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main

# Python 캐시 제거
docker exec uvis-backend find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
docker exec uvis-backend find /app -type f -name "*.pyc" -delete 2>/dev/null || true

# 완전 재시작 (stop → start)
docker-compose -f docker-compose.prod.yml stop backend
sleep 5
docker-compose -f docker-compose.prod.yml start backend
sleep 30

# 헬스 체크
curl -s http://localhost:8000/health
```

**성공 확률**: 70%  
**소요 시간**: 2분

**자동 스크립트**:
```bash
cd /root/uvis
./force_backend_reload.sh
```

---

### 🥇 방법 3: 완전 재빌드 (가장 확실)

Docker 이미지를 완전히 재빌드합니다.

```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main

# 백엔드 중지
docker-compose -f docker-compose.prod.yml stop backend

# 컨테이너 및 이미지 제거
docker-compose -f docker-compose.prod.yml rm -f backend
docker rmi uvis-backend:latest

# 캐시 없이 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache backend

# 재시작
docker-compose -f docker-compose.prod.yml up -d backend
sleep 45

# 헬스 체크
curl -s http://localhost:8000/health
```

**성공 확률**: 99%  
**소요 시간**: 5-10분

**자동 스크립트**:
```bash
cd /root/uvis
./rebuild_backend_image.sh
```

---

## 테스트 및 검증

### 1. 종합 테스트 실행
```bash
cd /root/uvis
./test_order_update_comprehensive.sh
```

### 2. 예상 결과
```
✅ SUCCESS: 시간 업데이트가 정상적으로 작동합니다!
```

### 3. 로그 확인
```bash
docker logs uvis-backend --tail 100 | grep -E '🕐|✅|Updated order'
```

**정상 로그**:
```
INFO - 🕐 Updating pickup_start_time: 10:30:00 (type: <class 'datetime.time'>)
INFO - 🕐 Updating pickup_end_time: 19:00:00 (type: <class 'datetime.time'>)
INFO - ✅ After commit pickup_start_time: 10:30:00
INFO - ✅ After commit pickup_end_time: 19:00:00
INFO - Updated order: ORD-1769829329699
```

### 4. DB 직접 확인
```bash
docker exec uvis-db psql -U uvis_user -d uvis_db -c "
SELECT id, order_number, pickup_start_time, pickup_end_time 
FROM orders 
WHERE id = 3;
"
```

**정상 출력**:
```
 id | order_number        | pickup_start_time | pickup_end_time
----+---------------------+-------------------+-----------------
  3 | ORD-1769829329699   | 10:30:00          | 19:00:00
```

---

## 현재 상황 분석

### 테스트 결과에서 발견된 문제

```
Step 2: GET /api/v1/orders/3
HTTP Status: 500
ResponseValidationError: pickup_client, delivery_client should be dict
```

**이것이 의미하는 것**:
- ❌ 서버에서 실행 중인 코드가 **아직 업데이트되지 않음**
- ❌ 여전히 `OrderWithClientsResponse`를 사용 중
- ❌ SQLAlchemy 객체를 직접 반환하고 있음

**올바른 코드 (이미 Git에 푸시됨)**:
```python
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    
    # ✅ Dict로 변환
    order_dict = {
        'id': order.id,
        'order_number': order.order_number,
        'pickup_start_time': order.pickup_start_time,
        # ...
        'pickup_client_name': order.pickup_client.name if order.pickup_client else None,
    }
    return order_dict  # ✅ dict 반환
```

---

## 추천 해결 순서

### 현재 상황에 가장 적합한 방법

```bash
# 1. 코드 업데이트
cd /root/uvis
git fetch origin main
git reset --hard origin/main

# 2. 방법 2 시도 (캐시 제거 + 재시작)
./force_backend_reload.sh

# 3. 테스트
./test_order_update_comprehensive.sh

# 4. 만약 여전히 실패하면 방법 3 시도 (완전 재빌드)
./rebuild_backend_image.sh

# 5. 재테스트
./test_order_update_comprehensive.sh
```

---

## 문제가 계속되면

### A. 코드가 실제로 컨테이너 안에 있는지 확인

```bash
# 컨테이너 안의 파일 확인
docker exec uvis-backend cat /app/app/api/orders.py | grep "response_model=OrderResponse"
```

**예상 출력**:
```python
@router.get("/{order_id}", response_model=OrderResponse)
```

만약 `OrderWithClientsResponse`가 보인다면 → 코드가 컨테이너에 반영되지 않은 것

### B. 볼륨 마운트 확인

```bash
docker inspect uvis-backend | grep -A 10 "Mounts"
```

호스트의 `/root/uvis/backend` → 컨테이너의 `/app` 마운트 확인

### C. 컨테이너 재생성

```bash
docker-compose -f docker-compose.prod.yml down backend
docker-compose -f docker-compose.prod.yml up -d backend
```

---

## 성공 체크리스트

완료 시 다음을 모두 확인:

- [ ] `git reset --hard origin/main` → HEAD at c50d805
- [ ] `force_backend_reload.sh` 또는 `rebuild_backend_image.sh` 실행 완료
- [ ] Backend health check 200 OK
- [ ] `test_order_update_comprehensive.sh` 실행 → ✅ SUCCESS
- [ ] GET /api/v1/orders/3 → HTTP 200 (500 아님)
- [ ] PUT /api/v1/orders/3 → 시간 10:30, 19:00 반영
- [ ] 백엔드 로그에 🕐, ✅ 이모지 표시
- [ ] DB에 시간 정상 저장 확인
- [ ] ResponseValidationError 미발생

---

## Git 커밋 상태

**최신 커밋**:
```
c50d805 - fix: Add scripts to force backend code reload and rebuild (최신)
9c66c56 - fix: Add rebuild and hotfix scripts
64bd52c - docs: Add complete resolution summary
0453953 - fix: Convert all order endpoints to dict responses (핵심 수정)
```

**저장소**: https://github.com/rpaakdi1-spec/3-  
**브랜치**: main

---

## 연락처

문제가 계속되면 다음 정보를 공유:

1. **실행한 명령어**:
   ```bash
   cd /root/uvis
   ./force_backend_reload.sh
   ./test_order_update_comprehensive.sh
   ```

2. **테스트 결과**: 전체 출력

3. **백엔드 로그**:
   ```bash
   docker logs uvis-backend --tail 200 > backend_logs.txt
   ```

4. **코드 확인**:
   ```bash
   docker exec uvis-backend cat /app/app/api/orders.py | head -120 > orders_api.txt
   ```

---

**지금 실행할 명령어**:

```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main
./force_backend_reload.sh
./test_order_update_comprehensive.sh
```

이 가이드대로 진행하면 문제가 해결될 것입니다! 🚀
