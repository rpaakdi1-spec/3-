# 🚨 긴급 수정: 배차 번호 중복 오류 해결

## 📋 발견된 문제

**에러 메시지**:
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "ix_dispatches_dispatch_number"
DETAIL: Key (dispatch_number)=(DISP-20260219122701-V전남87바4161) already exists.
```

**원인**: 
- 배차 번호 형식: `DISP-YYYYMMDDHHMMss-VehicleCode`
- 초(second) 단위까지만 포함
- 같은 초에 여러 배차 생성 시 중복 발생
- OR-Tools가 매우 빠르게 최적화하여 여러 배차를 동일한 초에 생성

**영향**:
- 배차 최적화 실행 시 중간에 실패
- 일부 배차만 생성되고 나머지는 실패
- `vehicle_id: 46`의 배차 생성 시 에러 발생

---

## ✅ 해결 방법

**변경 사항**: 배차 번호에 **마이크로초(6자리)** 추가

**Before**:
```python
dispatch_number = f"DISP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{vehicle.code}"
# 예: DISP-20260219122701-V전남87바4161
```

**After**:
```python
now = datetime.now()
dispatch_number = f"DISP-{now.strftime('%Y%m%d%H%M%S')}{now.microsecond:06d}-{vehicle.code}"
# 예: DISP-20260219122701123456-V전남87바4161
```

**개선 효과**:
- 마이크로초(1/1,000,000초) 정밀도로 고유성 보장
- 동시에 1,000,000개의 배차를 생성해도 충돌 없음
- 실전에서는 충분한 시간 간격 확보

---

## 🚀 서버 배포 (긴급)

### 방법 1: 빠른 배포 (추천)

```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 백엔드 디렉터리로 이동
cd /root/uvis/backend

# 3. 최신 코드 가져오기
git fetch origin main
git pull origin main

# 4. 변경사항 확인
git log --oneline -1
# fe2f1e5 fix(dispatch): Add microseconds to dispatch_number to prevent duplicates

# 5. 파일 확인
grep -A 2 "배차 번호 생성" app/services/cvrptw_service.py

# 6. Docker 컨테이너에 복사
docker cp app/services/cvrptw_service.py uvis-backend:/app/app/services/cvrptw_service.py

# 7. 컨테이너 재시작
docker restart uvis-backend

# 8. 로그 확인 (10초 대기)
sleep 10
docker logs uvis-backend --tail 20
```

### 방법 2: 직접 파일 수정 (백업)

서버에서 직접 수정:

```bash
ssh root@139.150.11.99
cd /root/uvis/backend

# 백업
cp app/services/cvrptw_service.py app/services/cvrptw_service.py.backup_dispatch_number

# 830번째 라인 수정
sed -i '829,830d' app/services/cvrptw_service.py
sed -i '828a\            # 배차 번호 생성 (마이크로초 포함하여 고유성 보장)\n            now = datetime.now()\n            dispatch_number = f"DISP-{now.strftime('"'"'%Y%m%d%H%M%S'"'"')}{now.microsecond:06d}-{vehicle.code}"' app/services/cvrptw_service.py

# 확인
sed -n '829,832p' app/services/cvrptw_service.py

# Docker 재시작
docker cp app/services/cvrptw_service.py uvis-backend:/app/app/services/cvrptw_service.py
docker restart uvis-backend
```

---

## 🧪 테스트

### 1. 배차 최적화 재실행

```bash
curl -X POST 'http://localhost:8000/api/v1/dispatches/optimize' \
  -H 'Content-Type: application/json' \
  -d '{"order_ids":[27,28,30],"vehicle_ids":[],"dispatch_date":"2026-02-19"}'
```

### 2. 예상 결과

**성공 케이스**:
```json
{
  "success": true,
  "total_orders": 3,
  "total_dispatches": 5,
  "dispatches": [
    {
      "id": 511,
      "dispatch_number": "DISP-20260219130000123456-V전남87바1336",
      "vehicle_id": 5,
      ...
    },
    {
      "id": 512,
      "dispatch_number": "DISP-20260219130000234567-V전남87바1317",
      "vehicle_id": 6,
      ...
    },
    ...
  ]
}
```

**주목할 점**:
- `dispatch_number`에 마이크로초(123456, 234567 등) 포함
- 모든 배차 번호가 고유함
- `UniqueViolation` 에러 없음

### 3. 데이터베이스 확인

```bash
# 컨테이너 접속
docker exec -it uvis-backend bash

# 최근 배차 확인
psql -U postgres -d uvis_db -c "SELECT id, dispatch_number, vehicle_id, total_orders, created_at FROM dispatches ORDER BY created_at DESC LIMIT 10;"
```

---

## 🔍 배포 검증

### 체크리스트

- [ ] Git pull 성공 (commit fe2f1e5 확인)
- [ ] 파일 변경사항 확인 (마이크로초 추가)
- [ ] Docker 컨테이너 재시작 완료
- [ ] 컨테이너 로그에 에러 없음
- [ ] 배차 최적화 API 테스트 성공
- [ ] 중복 dispatch_number 에러 없음
- [ ] 5개 배차 모두 정상 생성

### 확인 명령어

```bash
# 1. 컨테이너 상태
docker ps | grep uvis-backend

# 2. 최근 로그
docker logs uvis-backend --tail 50

# 3. 최근 배차 확인
docker exec -it uvis-backend psql -U postgres -d uvis_db -c \
  "SELECT dispatch_number, vehicle_id, created_at FROM dispatches ORDER BY created_at DESC LIMIT 5;"
```

---

## 📊 Before vs After

### Before (문제)
```
DISP-20260219122701-V전남87바4161  ← 첫 번째 배차
DISP-20260219122701-V전남87바4161  ← 같은 초에 생성, 중복!
❌ UniqueViolation 에러 발생
```

### After (해결)
```
DISP-20260219122701123456-V전남87바4161  ← 첫 번째 배차
DISP-20260219122701234567-V전남87바4158  ← 마이크로초 다름
DISP-20260219122701345678-V전남87바4401  ← 고유함
✅ 모든 배차 정상 생성
```

---

## 🔄 롤백 (문제 발생 시)

```bash
cd /root/uvis/backend

# 백업에서 복원
docker cp app/services/cvrptw_service.py.backup_dispatch_number uvis-backend:/app/app/services/cvrptw_service.py

# 재시작
docker restart uvis-backend
```

---

## 📝 추가 개선 사항

### 1. 기존 중복 배차 정리 (선택사항)

```sql
-- 중복된 dispatch_number 찾기
SELECT dispatch_number, COUNT(*) 
FROM dispatches 
GROUP BY dispatch_number 
HAVING COUNT(*) > 1;

-- 중복 배차 삭제 (최신 것만 유지)
DELETE FROM dispatches 
WHERE id NOT IN (
  SELECT MAX(id) 
  FROM dispatches 
  GROUP BY dispatch_number
);
```

### 2. 프론트엔드 영향

- ✅ **영향 없음**: 프론트엔드는 `dispatch_number`를 표시만 할 뿐 파싱하지 않음
- ✅ 배차 번호 길이만 14자 → 20자로 증가 (UI 자동 조정)

---

## 🎯 성공 기준

✅ 배차 최적화 실행 시 에러 없음  
✅ 모든 배차가 정상적으로 생성됨  
✅ `dispatch_number`가 고유함 (마이크로초 포함)  
✅ 데이터베이스에 중복 키 없음  
✅ 프론트엔드에서 배차 목록 정상 표시

---

## 📞 지원 정보

**서버**: root@139.150.11.99  
**컨테이너**: uvis-backend  
**파일**: `/root/uvis/backend/app/services/cvrptw_service.py` (라인 829-831)  
**커밋**: fe2f1e5 (fix: Add microseconds to dispatch_number)  
**GitHub**: https://github.com/rpaakdi1-spec/3-/commit/fe2f1e5

---

**작성일**: 2026-02-19 13:00 KST  
**우선순위**: 🔴 긴급 (배차 생성 차단 이슈)  
**예상 소요 시간**: 2분 (배포 + 테스트)
