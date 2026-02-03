# 🔧 배차 확정 후 주문 상태 동기화 문제 해결

## 📋 문제 요약

**증상**: 배차를 확정했는데도 주문 관리에서 주문 상태가 "배차대기(PENDING)"로 표시됨

**예상 동작**: 배차 확정 시 → 주문 상태가 "배차완료(ASSIGNED)"로 변경되어야 함

---

## 🔍 근본 원인

### 발견된 문제

1. **SQLAlchemy Relationship Lazy Loading**
   ```python
   # 기존 코드 (문제)
   for route in dispatch.routes:
       if route.order:  # relationship이 로드되지 않을 수 있음
           route.order.status = OrderStatus.ASSIGNED
   ```
   - SQLAlchemy의 lazy loading으로 인해 `route.order`가 None일 수 있음
   - `route.order_id`는 있지만 relationship 객체가 로드되지 않음

2. **로깅 부족**
   - 주문 상태 업데이트 성공/실패 로그가 없어서 디버깅 어려움

---

## ✅ 적용된 수정

### 1. Explicit Order Loading 추가

```python
# 수정된 코드 (해결)
for route in dispatch.routes:
    if route.order_id:
        # Relationship이 로드되지 않았으면 명시적으로 fetch
        order = route.order if route.order else db.query(Order).filter(Order.id == route.order_id).first()
        if order:
            logger.info(f"🔄 Updating order {order.order_number} status: {order.status} → ASSIGNED")
            order.status = OrderStatus.ASSIGNED
            updated_orders += 1
        else:
            logger.warning(f"⚠️  Route has order_id={route.order_id} but order not found!")
```

**개선 사항**:
- ✅ `route.order_id` 존재 여부 확인
- ✅ Relationship이 로드되지 않았으면 명시적으로 DB에서 fetch
- ✅ 업데이트된 주문 수 카운트
- ✅ 상세한 로깅 (이모지 포함)

### 2. Order 모델 Import 추가

```python
from app.models.order import Order, OrderStatus  # Order 추가
```

---

## 🚀 배포 및 테스트

### 1단계: 코드 업데이트

```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main
```

**Expected**: HEAD at ed9b590

### 2단계: 백엔드 재시작

```bash
./rebuild_backend_auto.sh
```

또는 빠른 재시작:
```bash
docker-compose -f docker-compose.prod.yml restart backend
sleep 30
```

### 3단계: 진단 스크립트 실행

```bash
./diagnose_dispatch_order_sync.sh
```

**예상 출력**:
```
1️⃣ 최근 배차 및 주문 상태 확인
최근 배차 목록:
{
  "id": 1,
  "dispatch_number": "DISP-20260203-001",
  "status": "DRAFT",
  "total_orders": 3
}

2️⃣ 배차 상세 정보 및 연결된 주문 확인
배차 경로에 포함된 주문 ID들:
{
  "sequence": 2,
  "route_type": "PICKUP",
  "order_id": 5
}
{
  "sequence": 3,
  "route_type": "DELIVERY",
  "order_id": 5
}

3️⃣ 해당 주문들의 현재 상태 확인
주문 ID: 5
{
  "order_number": "ORD-1769829329699",
  "status": "PENDING",  ← 배차 확정 전
  "order_date": "2026-02-06"
}
```

### 4단계: 배차 확정 테스트

```bash
# 배차 ID 1을 확정
curl -X POST http://localhost:8000/api/v1/dispatches/confirm \
  -H 'Content-Type: application/json' \
  -d '{"dispatch_ids": [1]}'
```

**예상 응답**:
```json
{
  "confirmed": 1,
  "failed": 0,
  "confirmed_dispatch_numbers": ["DISP-20260203-001"],
  "errors": []
}
```

### 5단계: 백엔드 로그 확인

```bash
docker logs uvis-backend --tail 100 | grep -E '🔄|✅|Confirmed dispatch'
```

**예상 로그 (수정 후)**:
```
INFO - 🔄 Updating order ORD-1769829329699 status: PENDING → ASSIGNED
INFO - 🔄 Updating order ORD-1769829330123 status: PENDING → ASSIGNED
INFO - 🔄 Updating order ORD-1769829330456 status: PENDING → ASSIGNED
INFO - ✅ Confirmed dispatch DISP-20260203-001: updated 3 orders
INFO - Confirmed 1 dispatches
```

**기존 로그 (수정 전, 로그 없음)**:
```
INFO - Vehicle V전남87바4168 status changed to IN_USE
INFO - Confirmed 1 dispatches
```

### 6단계: 주문 상태 재확인

```bash
curl -s http://localhost:8000/api/v1/orders/5 | jq '{
  order_number,
  status
}'
```

**예상 출력**:
```json
{
  "order_number": "ORD-1769829329699",
  "status": "ASSIGNED"  ← 배차완료로 변경됨!
}
```

---

## 🧪 브라우저에서 테스트

### 절차

1. **배차 관리 페이지 접속**
   - http://139.150.11.99/dispatches
   
2. **배차 생성 또는 선택**
   - "AI 최적화 배차" 버튼으로 새 배차 생성
   - 또는 기존 "임시저장" 상태 배차 선택

3. **배차 확정**
   - 배차 선택 후 **"배차 확정"** 버튼 클릭
   - 확인 메시지: "배차가 확정되었습니다"

4. **주문 관리 페이지 확인**
   - http://139.150.11.99/orders 접속
   - 배차에 포함된 주문들의 상태 확인
   - ✅ 상태가 **"배차완료"**로 표시되어야 함

5. **페이지 새로고침**
   - Ctrl+Shift+R (강제 새로고침)
   - 상태가 유지되는지 확인

---

## 📊 상태 흐름도

### 주문 상태 변화

```
1. 주문 생성
   └─> PENDING (배차대기)

2. 배차 생성 (AI 최적화)
   └─> PENDING (배차대기) [변경 없음]

3. 배차 확정 ✅ ← 이 단계에서 문제 발생
   └─> ASSIGNED (배차완료) [변경되어야 함]

4. 배송 시작
   └─> IN_TRANSIT (배송중)

5. 배송 완료
   └─> DELIVERED (배송완료)
```

### 배차 상태 변화

```
1. AI 최적화 생성
   └─> DRAFT (임시저장)

2. 배차 확정
   └─> CONFIRMED (확정)

3. 배송 시작
   └─> IN_PROGRESS (진행중)

4. 배송 완료
   └─> 배차완료
```

---

## 🔍 추가 진단

### DB에서 직접 확인

```bash
docker exec uvis-db psql -U uvis_user -d uvis_db -c "
SELECT 
    d.id as dispatch_id,
    d.dispatch_number,
    d.status as dispatch_status,
    dr.sequence,
    dr.route_type,
    dr.order_id,
    o.order_number,
    o.status as order_status
FROM dispatches d
JOIN dispatch_routes dr ON d.id = dr.dispatch_id
LEFT JOIN orders o ON dr.order_id = o.id
WHERE d.dispatch_date >= CURRENT_DATE - INTERVAL '7 days'
  AND dr.order_id IS NOT NULL
ORDER BY d.dispatch_date DESC, dr.sequence;
"
```

**예상 결과**:
```
 dispatch_id | dispatch_number      | dispatch_status | sequence | route_type | order_id | order_number        | order_status
-------------+----------------------+-----------------+----------+------------+----------+---------------------+-------------
           1 | DISP-20260203-001    | CONFIRMED       |        2 | PICKUP     |        5 | ORD-1769829329699   | ASSIGNED
           1 | DISP-20260203-001    | CONFIRMED       |        3 | DELIVERY   |        5 | ORD-1769829329699   | ASSIGNED
```

**문제가 있는 경우**:
- `order_status`가 `PENDING`로 표시 → 상태 업데이트 실패
- `order_id`가 NULL → 배차 생성 시 경로에 주문이 연결되지 않음

---

## 🐛 알려진 이슈 및 해결

### 이슈 1: Relationship Lazy Loading

**증상**: `route.order`가 None이지만 `route.order_id`는 값이 있음

**해결**: 명시적으로 `db.query(Order).filter(...).first()` 호출

### 이슈 2: 트랜잭션 롤백

**증상**: 로그에 업데이트 메시지가 있지만 DB에 반영 안 됨

**해결**: `db.commit()` 위치 확인 (모든 변경 후 한 번만 호출)

### 이슈 3: 캐시 문제

**증상**: 브라우저에서 상태가 업데이트되지 않음

**해결**: 
- Backend 재시작
- 브라우저 캐시 삭제 (Ctrl+Shift+Delete)
- 강제 새로고침 (Ctrl+Shift+R)

---

## 📋 체크리스트

배차 확정 후 다음을 확인:

- [ ] **코드 업데이트**: `git reset --hard origin/main` → ed9b590
- [ ] **백엔드 재시작**: `./rebuild_backend_auto.sh` 또는 `docker-compose restart backend`
- [ ] **진단 실행**: `./diagnose_dispatch_order_sync.sh`
- [ ] **배차 확정 테스트**: API 또는 브라우저에서 확정
- [ ] **로그 확인**: `🔄 Updating order` 메시지 확인
- [ ] **주문 상태 확인**: `curl http://localhost:8000/api/v1/orders/{id}` → status: ASSIGNED
- [ ] **브라우저 확인**: 주문 관리 페이지에서 "배차완료" 표시
- [ ] **DB 확인**: PostgreSQL에서 직접 쿼리

---

## 🔗 관련 파일

| 파일 | 설명 | 변경 사항 |
|-----|-----|---------|
| `backend/app/api/dispatches.py` | 배차 API 엔드포인트 | `confirm_dispatches` 함수 개선 |
| `diagnose_dispatch_order_sync.sh` | 진단 스크립트 | 신규 추가 |

---

## 📞 추가 지원

문제가 계속되면 다음 정보 공유:

1. **진단 스크립트 출력 전체**
2. **백엔드 로그**:
   ```bash
   docker logs uvis-backend --tail 200 > logs.txt
   ```
3. **DB 쿼리 결과** (위의 SQL 실행)
4. **브라우저 콘솔 에러** (F12 → Console)

**GitHub**: https://github.com/rpaakdi1-spec/3-  
**최신 커밋**: ed9b590  
**수정 브랜치**: main
