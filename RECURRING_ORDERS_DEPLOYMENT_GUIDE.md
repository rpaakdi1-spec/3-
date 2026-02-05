# 🚀 Recurring Orders Deployment & Test Guide

## 서버 배포 가이드

### Step 1: 코드 동기화
```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main
```

### Step 2: 백엔드 재빌드
```bash
# 백엔드 재빌드 (모델 변경사항 반영)
docker-compose -f docker-compose.prod.yml build --no-cache backend

# 백엔드 재시작
docker-compose -f docker-compose.prod.yml up -d backend

# 로그 확인 (스케줄러 시작 메시지 확인)
docker logs uvis-backend --tail 50 | grep -A 5 "scheduler"
```

예상 로그:
```
Starting scheduler service...
✅ Scheduled jobs configured:
  - 정기 주문 자동 생성: 매일 오전 6시
🚀 Starting scheduler...
✅ Scheduler started
```

### Step 3: 프론트엔드 재빌드
```bash
# 프론트엔드 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# 프론트엔드 재시작
docker-compose -f docker-compose.prod.yml up -d frontend

# Nginx 재시작
docker-compose -f docker-compose.prod.yml restart nginx

# 대기
sleep 20

# 컨테이너 상태 확인
docker ps | grep uvis
```

### Step 4: 데이터베이스 마이그레이션 확인
```bash
# 백엔드 컨테이너 접속
docker exec -it uvis-backend bash

# 마이그레이션 생성 (이미 생성되어 있을 수 있음)
alembic revision --autogenerate -m "Add recurring_orders table"

# 마이그레이션 실행
alembic upgrade head

# 테이블 확인
docker exec -it uvis-db psql -U dispatch_user -d dispatch_db -c "\dt recurring_orders"
```

예상 출력:
```
                  List of relations
 Schema |       Name        | Type  |     Owner
--------+-------------------+-------+---------------
 public | recurring_orders  | table | dispatch_user
(1 row)
```

---

## 백엔드 API 테스트

### 테스트 스크립트 실행
```bash
cd /root/uvis

# 테스트 스크립트 실행
./test_recurring_orders.sh
```

### 수동 테스트 (선택사항)

#### 1. 정기 주문 생성
```bash
curl -X POST http://localhost:8000/api/v1/recurring-orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "서울-부산 매주 월수금 배송",
    "frequency": "WEEKLY",
    "start_date": "2026-02-05",
    "end_date": "2026-12-31",
    "weekdays": 42,
    "order_date": "2026-02-05",
    "temperature_zone": "REFRIGERATED",
    "pickup_address": "서울시 강남구 테헤란로 123",
    "delivery_address": "부산시 해운대구 해운대로 456",
    "pallet_count": 20,
    "weight_kg": 500.0,
    "is_active": true
  }' | python3 -m json.tool
```

#### 2. 정기 주문 목록 조회
```bash
curl http://localhost:8000/api/v1/recurring-orders/ | python3 -m json.tool
```

#### 3. 즉시 생성 테스트
```bash
curl -X POST http://localhost:8000/api/v1/recurring-orders/generate | python3 -m json.tool
```

#### 4. 생성된 주문 확인
```bash
curl http://localhost:8000/api/v1/orders/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
orders = data.get('items', [])
rec_orders = [o for o in orders if o['order_number'].startswith('REC-')]
print(f'REC- 주문 {len(rec_orders)}개:')
for o in rec_orders[:5]:
    print(f'  {o[\"order_number\"]} - {o[\"pallet_count\"]}팔레트')
"
```

#### 5. 스케줄러 상태 확인
```bash
curl http://localhost:8000/api/v1/monitoring/scheduler/status | python3 -m json.tool
```

---

## 프론트엔드 테스트

### 브라우저 테스트

1. **정기 주문 페이지 접속**
   ```
   http://139.150.11.99/recurring-orders
   ```

2. **캐시 삭제** (중요!)
   - Chrome: Ctrl+Shift+Del → 전체 기간 → 캐시 삭제
   - 또는 Shift+F5 (강력 새로고침)

3. **테스트 시나리오**

   **시나리오 1: 매일 반복 주문 생성**
   - "정기 주문 생성" 버튼 클릭
   - 이름: "매일 정기 배송"
   - 주기: "매일" 선택
   - 시작일: 오늘
   - 상차/하차 주소 입력
   - 팔레트 수: 10
   - "생성" 버튼 클릭
   - ✅ 목록에 추가되는지 확인

   **시나리오 2: 매주 특정 요일 주문 생성**
   - "정기 주문 생성" 버튼 클릭
   - 이름: "매주 월수금 배송"
   - 주기: "매주" 선택
   - 요일: 월, 수, 금 클릭 (파란색으로 변경)
   - 나머지 정보 입력
   - "생성" 버튼 클릭
   - ✅ 목록에서 "월, 수, 금" 표시 확인

   **시나리오 3: 즉시 생성 테스트**
   - "즉시 생성" 버튼 클릭
   - 확인 대화상자 → "확인"
   - ✅ "X개의 주문이 생성되었습니다" 알림 확인
   - 주문 페이지(/orders)로 이동
   - ✅ "REC-" 시작하는 주문 확인

   **시나리오 4: 활성화/비활성화 토글**
   - 목록에서 "활성" 상태 클릭
   - ✅ "비활성"으로 변경되는지 확인
   - 다시 클릭 → ✅ "활성"으로 복귀

   **시나리오 5: 수정**
   - 연필 아이콘 클릭
   - 이름 수정: "수정된 이름"
   - "수정" 버튼 클릭
   - ✅ 목록에서 변경된 이름 확인

   **시나리오 6: 삭제**
   - 휴지통 아이콘 클릭
   - 확인 대화상자 → "확인"
   - ✅ 목록에서 제거 확인

---

## 예상 문제 및 해결책

### 문제 1: 테이블이 없음
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) relation "recurring_orders" does not exist
```

**해결:**
```bash
docker exec -it uvis-backend alembic upgrade head
```

### 문제 2: 스케줄러가 시작되지 않음
```
NameError: name 'scheduler_service' is not defined
```

**해결:**
- 백엔드 재빌드 필요:
```bash
docker-compose -f docker-compose.prod.yml build --no-cache backend
docker-compose -f docker-compose.prod.yml up -d backend
```

### 문제 3: 프론트엔드에서 404 Not Found
```
GET /recurring-orders 404
```

**해결:**
- 프론트엔드 재빌드 필요:
```bash
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
docker-compose -f docker-compose.prod.yml restart nginx
```

### 문제 4: 주문이 생성되지 않음
**증상:** generate 호출 시 `generated: 0`

**원인:**
- 오늘 이미 생성됨 (last_generated_date가 오늘)
- 요일 불일치 (WEEKLY 주기인데 오늘이 선택된 요일이 아님)
- 비활성 상태 (is_active = False)

**확인:**
```bash
# 미리보기로 오늘 생성 여부 확인
curl http://localhost:8000/api/v1/recurring-orders/preview | python3 -m json.tool
```

---

## 성공 기준

### ✅ 백엔드
- [ ] 테이블 생성 완료
- [ ] 스케줄러 시작 로그 확인
- [ ] 정기 주문 CRUD API 정상 작동
- [ ] 수동 생성(generate) 정상 작동
- [ ] REC- 시작하는 주문 생성 확인
- [ ] 스케줄러 상태 API 정상 응답

### ✅ 프론트엔드
- [ ] /recurring-orders 페이지 접속 가능
- [ ] 정기 주문 생성 폼 정상 작동
- [ ] 요일 선택 UI 정상 작동
- [ ] 목록 표시 정상
- [ ] 활성화/비활성화 토글 정상
- [ ] 수정/삭제 정상
- [ ] "즉시 생성" 버튼 정상 작동

---

## 다음 단계

### C. 주문 템플릿 구현 (예정)
- 자주 쓰는 주문 양식 저장/불러오기
- 템플릿 기반 빠른 주문 생성

### D. 배차 스케줄링 & 긴급 배차 (예정)
- 미래 날짜 배차 예약
- 긴급 주문 우선 처리

---

**작성일:** 2026-02-05  
**Phase:** 3-C (운영 효율화)  
**작성자:** AI Assistant
