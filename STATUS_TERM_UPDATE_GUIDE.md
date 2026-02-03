# 상태 용어 통일 업데이트 가이드

## 📋 개요

주문관리, AI배차최적화, 배차관리 항목의 상태 용어를 통일했습니다.

---

## 🔄 변경 내역

### 1. OrderStatus (주문 관리)
```python
# 변경 전
IN_TRANSIT = "운송중"

# 변경 후
IN_TRANSIT = "배송중"
```

### 2. DispatchStatus (배차 관리)
```python
# 변경 전
COMPLETED = "완료"

# 변경 후
COMPLETED = "배차완료"
```

---

## 🎯 통일된 용어 체계

### 주문 상태 흐름
```
배차대기 → 배차완료 → 배송중 → 배송완료 → 취소
```

### 배차 상태 흐름
```
임시저장 → 확정 → 진행중 → 배차완료 → 취소
```

---

## 🚀 배포 절차

### 1. 코드 업데이트
```bash
cd /root/uvis
git fetch origin main
git reset --hard origin/main
```

### 2. 데이터베이스 ENUM 업데이트
```bash
# OrderStatus ENUM에 '배송중' 추가
docker exec uvis-db psql -U uvis_user -d uvis_db -c "ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS '배송중';"

# DispatchStatus ENUM에 '배차완료' 추가
docker exec uvis-db psql -U uvis_user -d uvis_db -c "ALTER TYPE dispatchstatus ADD VALUE IF NOT EXISTS '배차완료';"
```

### 3. ENUM 확인
```bash
# OrderStatus 확인
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT unnest(enum_range(NULL::orderstatus));"

# DispatchStatus 확인
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT unnest(enum_range(NULL::dispatchstatus));"
```

### 4. 기존 데이터 마이그레이션 (필요시)

**주문 데이터:**
```bash
docker exec uvis-backend python -c "
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # '운송중' → '배송중'으로 변경
    result = db.execute(
        text('UPDATE orders SET status = :new_status WHERE status = :old_status'),
        {'new_status': '배송중', 'old_status': '운송중'}
    )
    db.commit()
    print(f'✅ 주문 상태 업데이트: {result.rowcount}건')
finally:
    db.close()
"
```

**배차 데이터:**
```bash
docker exec uvis-backend python -c "
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # '완료' → '배차완료'로 변경
    result = db.execute(
        text('UPDATE dispatches SET status = :new_status WHERE status = :old_status'),
        {'new_status': '배차완료', 'old_status': '완료'}
    )
    db.commit()
    print(f'✅ 배차 상태 업데이트: {result.rowcount}건')
finally:
    db.close()
"
```

### 5. 백엔드 재시작
```bash
docker-compose -f docker-compose.prod.yml restart backend
sleep 30
```

### 6. 프론트엔드 재빌드 (필요시)
```bash
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml rm -f frontend
docker rmi uvis-frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

---

## ✅ 검증

### API 테스트
```bash
# 주문 상태 확인
curl -s http://localhost:8000/api/v1/orders/ | jq '.items[] | {id, order_number, status}'

# 배차 상태 확인
curl -s http://localhost:8000/api/v1/dispatches/ | jq '.items[] | {id, dispatch_number, status}'

# 상태별 집계
curl -s http://localhost:8000/api/v1/orders/ | jq '[.items[].status] | group_by(.) | map({status: .[0], count: length})'
curl -s http://localhost:8000/api/v1/dispatches/ | jq '[.items[].status] | group_by(.) | map({status: .[0], count: length})'
```

---

## 📊 예상 결과

### 주문 상태 예시
```json
[
  {"status": "배차대기", "count": 5},
  {"status": "배차완료", "count": 3},
  {"status": "배송중", "count": 2},
  {"status": "배송완료", "count": 10},
  {"status": "취소", "count": 1}
]
```

### 배차 상태 예시
```json
[
  {"status": "임시저장", "count": 8},
  {"status": "확정", "count": 2},
  {"status": "진행중", "count": 1},
  {"status": "배차완료", "count": 3},
  {"status": "취소", "count": 1}
]
```

---

## 🔧 트러블슈팅

### 1. ENUM 값 추가 실패
```bash
# 이미 값이 존재하는 경우 무시됨 (정상)
# IF NOT EXISTS를 사용하므로 여러 번 실행해도 안전
```

### 2. 데이터 마이그레이션 실패
```bash
# 기존 데이터 확인
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT status, COUNT(*) FROM orders GROUP BY status;"
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT status, COUNT(*) FROM dispatches GROUP BY status;"
```

### 3. 백엔드 에러
```bash
# 로그 확인
docker logs uvis-backend --tail 100 | grep -A 5 "LookupError"

# ENUM 매핑 오류가 있으면 백엔드 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📝 참고사항

1. **ENUM 순서**: PostgreSQL ENUM에 새 값을 추가하면 기존 값 뒤에 추가됩니다.
2. **기존 데이터**: 기존 데이터는 자동으로 변경되지 않으므로 마이그레이션 스크립트 필요
3. **프론트엔드**: 상태 표시 로직은 자동으로 새 값을 인식합니다.
4. **API 호환성**: Enum 값이 변경되어도 API 스키마는 동일하게 동작합니다.

---

## 🎉 완료 체크리스트

- [ ] 코드 업데이트 (`git pull`)
- [ ] OrderStatus ENUM 추가 ('배송중')
- [ ] DispatchStatus ENUM 추가 ('배차완료')
- [ ] 기존 주문 데이터 마이그레이션
- [ ] 기존 배차 데이터 마이그레이션
- [ ] 백엔드 재시작
- [ ] API 테스트
- [ ] 브라우저 테스트 (http://139.150.11.99/orders)
- [ ] 상태 집계 확인

---

## 📅 업데이트 일자

- **작성일**: 2026-02-03
- **커밋**: 2571b20
- **작업자**: AI Assistant
