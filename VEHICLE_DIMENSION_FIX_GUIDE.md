# 차량 적재함 치수 수정 가이드

## 🎯 문제 해결

### 발견된 문제
1. ❌ UI에서 적재함 길이/너비/높이 수정이 안 됨
2. ❌ 모든 차량의 적재함 길이가 9m로 초기화됨

### 해결 방법
1. ✅ VehicleUpdate 스키마에 누락된 필드 추가
2. ✅ 톤수별 적재함 치수 일괄 업데이트 SQL 제공

---

## 🚀 배포 순서

### 1단계: 백엔드 배포

```bash
cd /root/uvis
git pull origin main
docker compose build backend
docker compose up -d backend
sleep 15
docker compose ps
curl http://139.150.11.99/api/v1/health
```

### 2단계: 데이터베이스 업데이트

#### A. SQL 파일 준비
```bash
# 로컬 파일을 서버로 복사 (또는 직접 생성)
cd /root/uvis
cat > update_vehicle_dimensions.sql << 'SQLEOF'
-- 차량 적재함 길이 일괄 업데이트
-- 5톤 = 6.0m, 11톤 = 9m, 18톤 = 12.2m

-- 1. 5톤 차량 업데이트
UPDATE vehicles 
SET length_m = 6.0,
    width_m = 2.3,
    height_m = 2.3,
    updated_at = NOW()
WHERE tonnage >= 4.5 AND tonnage < 7.5 
  AND is_active = true;

-- 2. 11톤 차량 업데이트
UPDATE vehicles 
SET length_m = 9.0,
    width_m = 2.4,
    height_m = 2.5,
    updated_at = NOW()
WHERE tonnage >= 10 AND tonnage < 15
  AND is_active = true;

-- 3. 18톤 차량 업데이트
UPDATE vehicles 
SET length_m = 12.2,
    width_m = 2.5,
    height_m = 2.7,
    updated_at = NOW()
WHERE tonnage >= 15
  AND is_active = true;

-- 4. 2.5톤 차량 업데이트
UPDATE vehicles 
SET length_m = 4.5,
    width_m = 2.0,
    height_m = 2.0,
    updated_at = NOW()
WHERE tonnage >= 2.0 AND tonnage < 4.5
  AND is_active = true;

-- 5. 1톤 차량 업데이트
UPDATE vehicles 
SET length_m = 2.4,
    width_m = 1.6,
    height_m = 1.8,
    updated_at = NOW()
WHERE tonnage < 2.0
  AND is_active = true;
SQLEOF
```

#### B. 업데이트 전 현재 상태 확인
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT tonnage, 
       COUNT(*) as count,
       AVG(length_m) as avg_length_before
FROM vehicles 
WHERE is_active = true
GROUP BY tonnage
ORDER BY tonnage;
"
```

#### C. SQL 실행
```bash
docker compose exec -T db psql -U uvis_user -d uvis_db < update_vehicle_dimensions.sql
```

#### D. 업데이트 결과 확인
```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT tonnage, 
       COUNT(*) as count,
       ROUND(AVG(length_m)::numeric, 1) as avg_length,
       ROUND(AVG(width_m)::numeric, 1) as avg_width,
       ROUND(AVG(height_m)::numeric, 1) as avg_height
FROM vehicles 
WHERE is_active = true
GROUP BY tonnage
ORDER BY tonnage;
"
```

**예상 결과:**
```
 tonnage | count | avg_length | avg_width | avg_height
---------+-------+------------+-----------+------------
     5.0 |    X  |        6.0 |       2.3 |        2.3
    11.0 |    X  |        9.0 |       2.4 |        2.5
    18.0 |    X  |       12.2 |       2.5 |        2.7
```

---

## 📊 차량 톤수별 적재함 치수

| 톤수 | 길이(m) | 너비(m) | 높이(m) | 용도 |
|------|---------|---------|---------|------|
| 1톤  | 2.4     | 1.6     | 1.8     | 소형 배송 |
| 2.5톤 | 4.5    | 2.0     | 2.0     | 중소형 배송 |
| 5톤  | 6.0     | 2.3     | 2.3     | 중형 배송 |
| 11톤 | 9.0     | 2.4     | 2.5     | 대형 배송 |
| 18톤 | 12.2    | 2.5     | 2.7     | 초대형 배송 |

---

## ✅ 테스트 방법

### 1. 브라우저 캐시 클리어
```
방법 1: http://139.150.11.99/clear-cache.html
방법 2: Ctrl+Shift+Delete → 캐시 삭제 → Ctrl+Shift+R
방법 3: 시크릿 모드 (Ctrl+Shift+N)
```

### 2. 차량 관리 페이지 접속
```
URL: http://139.150.11.99/vehicles
로그인: manager1@test.com / test1234
```

### 3. 차량 수정 테스트
1. 아무 차량 선택 → **수정** 버튼 클릭
2. **적재함 길이** 필드에 값 입력 (예: 10.5)
3. **적재함 너비** 필드에 값 입력 (예: 2.4)
4. **적재함 높이** 필드에 값 입력 (예: 2.6)
5. **저장** 버튼 클릭
6. 저장 성공 메시지 확인
7. 차량 목록에서 변경된 값 확인

### 4. 차량 상세 확인
```bash
# 특정 차량의 치수 확인 (예: 차량 ID 17)
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, plate_number, tonnage, length_m, width_m, height_m 
FROM vehicles 
WHERE id = 17;
"
```

---

## 🐛 문제 해결

### 문제 1: SQL 실행 실패
**증상:** `psql: error: connection refused`

**해결:**
```bash
# DB 컨테이너 상태 확인
docker compose ps db

# DB 컨테이너 재시작
docker compose restart db
sleep 10

# 다시 시도
docker compose exec -T db psql -U uvis_user -d uvis_db < update_vehicle_dimensions.sql
```

### 문제 2: 적재함 치수가 여전히 수정 안 됨
**증상:** UI에서 수정해도 저장이 안 됨

**확인사항:**
```bash
# 1. 백엔드 로그 확인
docker compose logs backend --tail=50 | grep -i "vehicle"

# 2. 백엔드가 최신 코드인지 확인
docker compose exec backend python -c "
from app.schemas.vehicle import VehicleUpdate
import inspect
fields = list(VehicleUpdate.model_fields.keys())
print('length_m in fields:', 'length_m' in fields)
print('width_m in fields:', 'width_m' in fields)
print('height_m in fields:', 'height_m' in fields)
print('All fields:', fields)
"
```

**해결:**
```bash
# 백엔드 완전 재빌드
docker compose down backend
docker compose build --no-cache backend
docker compose up -d backend
```

### 문제 3: 일부 차량만 업데이트됨
**증상:** 특정 톤수의 차량만 업데이트되고 나머지는 그대로

**확인:**
```bash
# 각 톤수별 차량 개수 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT tonnage, COUNT(*) 
FROM vehicles 
WHERE is_active = true 
GROUP BY tonnage 
ORDER BY tonnage;
"
```

**원인:** 톤수가 예상 범위를 벗어남 (예: 4.0톤, 7.5톤 등)

**해결:** SQL 스크립트의 범위 조정 또는 개별 업데이트
```sql
-- 예: 7.5톤 차량 개별 업데이트
UPDATE vehicles 
SET length_m = 7.0, width_m = 2.3, height_m = 2.4, updated_at = NOW()
WHERE tonnage = 7.5 AND is_active = true;
```

### 문제 4: 데이터가 다시 초기화됨
**증상:** 업데이트 후 시간이 지나면 다시 9m로 돌아감

**원인:** 외부 시스템(UVIS API)에서 주기적으로 차량 데이터 동기화

**확인:**
```bash
# UVIS 동기화 로그 확인
docker compose logs backend | grep -i "uvis.*sync\|vehicle.*sync" | tail -20
```

**해결:** 
1. UVIS API 동기화 시 적재함 치수 제외
2. 또는 UVIS API에서 정확한 치수 데이터 가져오기
3. 동기화 스크립트 수정 필요

---

## 📝 추가 정보

### VehicleUpdate 스키마 변경 사항
```python
class VehicleUpdate(BaseModel):
    # ... (기존 필드들)
    
    # 새로 추가된 필드들 ✅
    length_m: Optional[float] = Field(None, gt=0, description="적재함 길이(m)")
    width_m: Optional[float] = Field(None, gt=0, description="적재함 너비(m)")
    height_m: Optional[float] = Field(None, gt=0, description="적재함 높이(m)")
    min_temp_celsius: Optional[float] = None
    max_temp_celsius: Optional[float] = None
    fuel_efficiency_km_per_liter: Optional[float] = Field(None, gt=0)
    fuel_cost_per_liter: Optional[float] = Field(None, gt=0)
```

### API 엔드포인트
```
PUT /api/v1/vehicles/{vehicle_id}

Body (JSON):
{
  "length_m": 10.5,
  "width_m": 2.4,
  "height_m": 2.6
}
```

---

## 🔗 커밋 정보

```bash
Commit: 66aa6b6
Message: fix: 차량 적재함 치수 수정 기능 복구
Files Changed:
  - backend/app/schemas/vehicle.py (VehicleUpdate 스키마 수정)
  - update_vehicle_dimensions.sql (일괄 업데이트 SQL)

Push: https://github.com/rpaakdi1-spec/3-.git
Branch: main
```

---

## 📞 지원

문제가 계속되면 백엔드 로그를 첨부하여 문의하세요:
```bash
docker compose logs backend --tail=100 > backend_logs.txt
```
