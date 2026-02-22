# 주문 상태 자동 업데이트 기능

## 📋 개요

배차 생성 시 포함된 주문의 상태를 자동으로 **"배차대기" → "배차완료"**로 업데이트하는 기능입니다.

## 🎯 문제점

### 이전 동작
```
1. 주문 생성 → status: "배차대기" (PENDING)
2. 배차 최적화 실행 → 배차 생성
3. 주문 상태 그대로 유지 ❌ ← 문제!
```

**결과**: 배차에 포함된 주문도 여전히 "배차대기" 상태로 표시되어 사용자 혼란 발생

### 수정 후 동작
```
1. 주문 생성 → status: "배차대기" (PENDING)
2. 배차 최적화 실행 → 배차 생성
3. 주문 상태 자동 업데이트 ✅ → status: "배차완료" (ASSIGNED)
```

**결과**: 배차된 주문은 "배차완료" 상태로 변경되어 명확한 상태 관리

---

## 🔄 주문 상태 흐름

```
┌─────────────┐
│  주문 생성   │
│ (PENDING)   │ ← 배차대기 (초록색)
└──────┬──────┘
       │
       │ 배차 최적화 실행
       ▼
┌─────────────┐
│  배차 완료   │
│ (ASSIGNED)  │ ← 배차완료 (파란색) ✨ NEW!
└──────┬──────┘
       │
       │ 배송 시작
       ▼
┌─────────────┐
│   배송 중    │
│(IN_TRANSIT) │ ← 배송중 (주황색)
└──────┬──────┘
       │
       │ 배송 완료
       ▼
┌─────────────┐
│  배송 완료   │
│ (DELIVERED) │ ← 배송완료 (회색)
└─────────────┘
```

---

## 💻 기술 구현

### 1. Import 추가

**파일**: `backend/app/services/cvrptw_service.py`

```python
# 변경 전
from app.models.order import Order, TemperatureZone

# 변경 후
from app.models.order import Order, TemperatureZone, OrderStatus
```

### 2. 주문 상태 업데이트 로직 추가

**위치**: `_save_solution_to_db` 메서드 내부, 경로 생성 후

```python
# 경로 생성
route = DispatchRoute(
    dispatch_id=dispatch.id,
    sequence=seq,
    route_type=route_type,
    order_id=location.order_id,
    # ... 기타 필드들
)

self.db.add(route)

# 🆕 주문 상태 업데이트 로직 추가
if location.order_id:
    order = self.db.query(Order).filter(Order.id == location.order_id).first()
    if order and order.status == OrderStatus.PENDING:
        order.status = OrderStatus.ASSIGNED
        logger.info(f"  → 주문 {order.order_number} 상태 변경: 배차대기 → 배차완료")

self.db.commit()
```

### 3. 동작 방식

1. **배차 경로 생성 시**: 각 경로에 포함된 주문 ID 확인
2. **주문 조회**: 해당 ID의 주문 조회
3. **상태 확인**: 현재 상태가 "배차대기"(PENDING)인지 확인
4. **상태 변경**: "배차완료"(ASSIGNED)로 변경
5. **로그 기록**: 상태 변경 내역 로그에 기록

### 4. 안전장치

- ✅ **중복 업데이트 방지**: 이미 "배차완료" 이상의 상태는 변경하지 않음
- ✅ **Null 체크**: order_id가 None인 경우 스킵 (차고지 등)
- ✅ **트랜잭션**: 배차 생성과 주문 상태 업데이트가 하나의 트랜잭션으로 처리
- ✅ **로그 기록**: 모든 상태 변경 내역이 로그에 기록됨

---

## 🚀 배포 방법

### 자동 배포 (권장)

```bash
# SSH 접속
ssh root@139.150.11.99

# 배포 스크립트 다운로드 및 실행
cd /root/uvis/backend
git fetch origin main
git reset --hard origin/main
bash DEPLOY_ORDER_STATUS_UPDATE.sh
```

### 수동 배포

```bash
# 1. 백엔드 디렉토리로 이동
cd /root/uvis/backend

# 2. 최신 코드 가져오기
git fetch origin main
git reset --hard origin/main

# 3. 변경 확인
grep -A 3 "주문 상태 업데이트" app/services/cvrptw_service.py

# 4. 컨테이너에 복사
docker cp app/services/cvrptw_service.py uvis-backend:/app/app/services/cvrptw_service.py

# 5. 캐시 삭제
docker exec uvis-backend find /app -type d -name __pycache__ -exec rm -rf {} +

# 6. 재시작
docker restart uvis-backend

# 7. 확인
sleep 10
docker logs uvis-backend --tail 30
```

---

## 🧪 테스트 방법

### 1. API 테스트

#### Step 1: 주문 상태 확인 (배차 전)
```bash
curl -s 'http://localhost:8000/api/v1/orders/27' | jq '.status'
# 예상 결과: "배차대기"
```

#### Step 2: 배차 최적화 실행
```bash
curl -X POST 'http://localhost:8000/api/v1/dispatches/optimize' \
  -H 'Content-Type: application/json' \
  -d '{
    "order_ids": [27, 28, 30],
    "vehicle_ids": [],
    "dispatch_date": "2026-02-19"
  }' | jq .
```

#### Step 3: 주문 상태 확인 (배차 후)
```bash
curl -s 'http://localhost:8000/api/v1/orders/27' | jq '.status'
# 예상 결과: "배차완료" ✅

curl -s 'http://localhost:8000/api/v1/orders/28' | jq '.status'
# 예상 결과: "배차완료" ✅

curl -s 'http://localhost:8000/api/v1/orders/30' | jq '.status'
# 예상 결과: "배차완료" ✅
```

### 2. 로그 확인

```bash
docker logs uvis-backend --tail 50 | grep '주문.*상태 변경'
```

**예상 로그 출력**:
```
→ 주문 ORD-20260219-001 상태 변경: 배차대기 → 배차완료
→ 주문 ORD-20260219-002 상태 변경: 배차대기 → 배차완료
→ 주문 ORD-20260219-003 상태 변경: 배차대기 → 배차완료
```

### 3. 브라우저 UI 테스트

1. **주문 관리 페이지 열기**
   - http://139.150.11.99/orders

2. **배차 전 상태 확인**
   - 주문 27, 28, 30의 상태 배지: 🟢 "배차대기"

3. **배차 최적화 페이지로 이동**
   - http://139.150.11.99/optimization

4. **배차 실행**
   - 주문 27, 28, 30 선택
   - "배차 최적화" 버튼 클릭

5. **주문 관리 페이지로 돌아가기**
   - 페이지 새로고침 (F5)
   - 주문 27, 28, 30의 상태 배지: 🔵 "배차완료" ✅

---

## 📊 예상 결과

### ✅ 성공 시

#### API 응답
```json
{
  "id": 27,
  "order_number": "ORD-20260219-001",
  "status": "배차완료",
  "order_date": "2026-02-19",
  "temperature_zone": "냉동"
}
```

#### 백엔드 로그
```
INFO: ✓ 배차 저장: DISP-20260219125500123456-V전남87바1336 (3개 정류장)
INFO:   → 주문 ORD-20260219-001 상태 변경: 배차대기 → 배차완료
INFO:   → 주문 ORD-20260219-002 상태 변경: 배차대기 → 배차완료
INFO:   → 주문 ORD-20260219-003 상태 변경: 배차대기 → 배차완료
```

#### UI 표시
- 배지 색상: 🔵 파란색
- 배지 텍스트: "배차완료"

### ❌ 실패 시 확인 사항

1. **주문 상태가 변경되지 않음**
   ```bash
   # 백엔드 로그 확인
   docker logs uvis-backend --tail 100 | grep -i error
   
   # 코드 확인
   docker exec uvis-backend cat /app/app/services/cvrptw_service.py | grep -A 5 "주문 상태 업데이트"
   ```

2. **오류 메시지**
   ```bash
   # 전체 로그 확인
   docker logs uvis-backend --tail 200
   ```

---

## 🔧 트러블슈팅

### 문제 1: 주문 상태가 여전히 "배차대기"

**원인**: 코드 업데이트가 컨테이너에 반영되지 않음

**해결**:
```bash
# 1. 파일 다시 복사
docker cp /root/uvis/backend/app/services/cvrptw_service.py \
  uvis-backend:/app/app/services/cvrptw_service.py

# 2. 캐시 완전 삭제
docker exec uvis-backend rm -rf /app/app/services/__pycache__

# 3. 강제 재시작
docker restart uvis-backend

# 4. 확인
sleep 10
docker logs uvis-backend --tail 30
```

### 문제 2: Import 오류

**증상**: `ImportError: cannot import name 'OrderStatus'`

**원인**: OrderStatus import가 누락됨

**해결**:
```bash
# 소스 파일 확인
grep "from app.models.order import" /root/uvis/backend/app/services/cvrptw_service.py

# 예상 결과:
# from app.models.order import Order, TemperatureZone, OrderStatus
```

### 문제 3: 로그에 상태 변경 없음

**원인**: order_id가 None이거나 이미 ASSIGNED 상태

**확인**:
```bash
# 주문 현재 상태 확인
curl -s 'http://localhost:8000/api/v1/orders/27' | jq '{id, order_number, status}'

# 배차 경로 확인
curl -s 'http://localhost:8000/api/v1/dispatches/598/routes' | jq '.[] | {order_id, location_name}'
```

---

## 📈 향후 개선 사항

### Phase 2: 배차 확정 시 추가 상태 변경
```python
# 배차 확정 시 (confirm_dispatch)
for route in dispatch.routes:
    if route.order_id:
        order = db.query(Order).get(route.order_id)
        if order.status == OrderStatus.ASSIGNED:
            # 상태 변경하지 않음 (그대로 유지)
            pass
```

### Phase 3: 배송 시작 시 상태 변경
```python
# 배송 시작 시 (start_delivery)
for route in dispatch.routes:
    if route.order_id:
        order = db.query(Order).get(route.order_id)
        if order.status == OrderStatus.ASSIGNED:
            order.status = OrderStatus.IN_TRANSIT
```

### Phase 4: 배송 완료 시 상태 변경
```python
# 배송 완료 시 (complete_delivery)
for route in dispatch.routes:
    if route.order_id:
        order = db.query(Order).get(route.order_id)
        if order.status == OrderStatus.IN_TRANSIT:
            order.status = OrderStatus.DELIVERED
```

### Phase 5: 배차 취소 시 복원
```python
# 배차 취소 시 (cancel_dispatch)
for route in dispatch.routes:
    if route.order_id:
        order = db.query(Order).get(route.order_id)
        if order.status == OrderStatus.ASSIGNED:
            order.status = OrderStatus.PENDING  # 원상복구
```

---

## 📝 체크리스트

### 코드 변경
- [x] OrderStatus import 추가
- [x] 주문 상태 업데이트 로직 추가
- [x] 로그 기록 추가
- [x] Git commit & push

### 배포
- [ ] 서버 SSH 접속
- [ ] 최신 코드 가져오기
- [ ] 컨테이너에 파일 복사
- [ ] 컨테이너 재시작
- [ ] 로그 확인

### 테스트
- [ ] API 테스트 (배차 전후 상태 확인)
- [ ] 로그 확인 (상태 변경 메시지)
- [ ] UI 테스트 (배지 색상 및 텍스트)
- [ ] 여러 주문 동시 테스트

---

## 📚 관련 파일

- `backend/app/services/cvrptw_service.py` - 배차 최적화 서비스 (주요 변경)
- `backend/app/models/order.py` - 주문 모델 (OrderStatus enum)
- `DEPLOY_ORDER_STATUS_UPDATE.sh` - 배포 스크립트

---

## 🔗 Git 커밋

| 커밋 | 내용 | 날짜 |
|------|------|------|
| `584ede1` | feat: Update order status to ASSIGNED when dispatch is created | 2026-02-19 |
| `1eb4bb6` | feat: Add deployment script for order status auto-update | 2026-02-19 |

**GitHub**: https://github.com/rpaakdi1-spec/3-/commits/main

---

**최종 업데이트**: 2026-02-19  
**작성자**: AI Assistant  
**문서 버전**: 1.0  
**상태**: ✅ 코드 완료 (서버 배포 대기 중)
