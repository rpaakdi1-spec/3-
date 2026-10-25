# 운전자별 주행거리 계산 기능 배포 가이드

## 📋 개요

차량 테이블의 `driver_name` 필드를 기반으로 운전자별 주행거리를 자동 집계하는 기능입니다.

## 🎯 주요 기능

- ✅ 배차 시스템 없이도 차량 기반으로 운전자 주행거리 계산
- ✅ 같은 운전자가 여러 차량 운행 시 자동 합산
- ✅ 일별/주별/월별 통계 제공
- ✅ 운전자명 검색 지원

## 🚀 빠른 배포 (자동 스크립트)

### 방법 1: 배포 스크립트 사용 (권장)

```bash
cd /root/uvis
git pull origin main
chmod +x deploy_driver_mileage.sh
./deploy_driver_mileage.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
1. 코드 업데이트 (git pull)
2. 데이터베이스 마이그레이션
3. 백엔드 재빌드 및 재시작
4. 서비스 상태 확인
5. 기능 테스트

---

## 📝 수동 배포 (단계별)

### 1단계: 코드 업데이트

```bash
cd /root/uvis
git stash  # 기존 변경사항 임시 저장 (있다면)
git pull origin main
```

### 2단계: 데이터베이스 마이그레이션

**중요**: `driver_daily_mileage` 테이블의 `driver_id` 컬럼을 NULL 허용으로 변경해야 합니다.

```bash
cat backend/migrations/fix_driver_daily_mileage_nullable.sql | \
docker compose exec -T db psql -U uvis_user -d uvis_db
```

**예상 출력:**
```
ALTER TABLE
ALTER TABLE
DO
ALTER TABLE
CREATE INDEX
CREATE INDEX
COMMENT
COMMENT
COMMENT
```

**문제 해결:**
- 이미 적용되었다는 메시지가 나오면 정상입니다 (무시하고 진행).
- 에러가 발생하면 아래 "문제 해결" 섹션 참조.

### 3단계: 백엔드 재빌드

```bash
docker compose build backend
```

### 4단계: 백엔드 재시작

```bash
docker compose up -d backend
sleep 20  # 서비스 시작 대기
```

### 5단계: 서비스 상태 확인

```bash
docker compose ps
```

**예상 출력:**
```
NAME            STATUS    PORTS
uvis-backend    healthy   0.0.0.0:8000->8000/tcp
uvis-db         healthy   5432/tcp
uvis-redis      healthy   6379/tcp
uvis-frontend   healthy   0.0.0.0:80->80/tcp
```

---

## 🧪 기능 테스트

### 테스트 1: 운전자 주행거리 계산

```bash
docker compose exec -T backend python3 <<'EOF'
from datetime import date, timedelta
from app.core.database import get_db
from app.services.driver_mileage_service import DriverMileageService

db = next(get_db())
service = DriverMileageService(db)
yesterday = date.today() - timedelta(days=1)

print(f"🚗 {yesterday} 운전자별 주행거리 계산 시작...\n")
results = service.calculate_driver_mileage_from_vehicle(yesterday)

if results:
    print(f"✅ 총 {len(results)}명 운전자 계산 완료\n")
    print("="*110)
    print(f"{'운전자명':<12} | {'주행(km)':>10} | {'시간(분)':>9} | {'차량수':>7} | {'평균속도':>9} | {'최고속도':>9}")
    print("="*110)
    
    for m in sorted(results, key=lambda x: x.total_distance_km, reverse=True)[:15]:
        driver_name = m.notes.replace("차량기반:", "") if m.notes else "미지정"
        print(f"{driver_name:<12} | {m.total_distance_km:>10.2f} | {m.total_driving_minutes:>9} | "
              f"{m.vehicle_count:>7} | {m.avg_speed_kmh:>9.1f} | {m.max_speed_kmh:>9.1f}")
    
    print("="*110)
else:
    print("⚠️  계산된 운전자 없음")

db.close()
EOF
```

**예상 출력:**
```
🚗 2026-03-02 운전자별 주행거리 계산 시작...

✅ 총 9명 운전자 계산 완료

==============================================================================================================
운전자명        |   주행(km) |  시간(분) |  차량수 |  평균속도 |  최고속도
==============================================================================================================
박운송          |     537.25 |       214 |       2 |      76.3 |      90.0
김운전          |     147.90 |       107 |       1 |      72.0 |      86.0
이기사          |     144.32 |       106 |       1 |      60.5 |      88.0
정배차          |     144.26 |       106 |       1 |      64.4 |      88.0
...
==============================================================================================================
```

### 테스트 2: API 엔드포인트 확인

```bash
# 일별 운전자 주행거리 조회
curl -s "http://localhost/api/v1/driver-mileage/daily?target_date=2026-03-02" | jq '.mileages[0:3]'

# 운전자명으로 검색
curl -s "http://localhost/api/v1/driver-mileage/daily?driver_name=박운송" | jq

# 운전자 주행거리 재계산
curl -X POST "http://localhost/api/v1/driver-mileage/calculate?target_date=2026-03-02"
```

---

## 📊 데이터베이스 직접 확인

```bash
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT 
    notes AS 운전자명,
    date AS 날짜,
    total_distance_km AS 주행거리_km,
    total_driving_minutes AS 주행시간_분,
    vehicle_count AS 차량수,
    vehicle_ids AS 차량ID목록,
    avg_speed_kmh AS 평균속도,
    max_speed_kmh AS 최고속도
FROM driver_daily_mileage
WHERE date = '2026-03-02'
  AND calculation_method = 'vehicle_based'
ORDER BY total_distance_km DESC
LIMIT 10;
"
```

---

## 🔍 API 사용 가이드

### 1. 일별 운전자 주행거리 조회

```bash
GET /api/v1/driver-mileage/daily

# 파라미터
- target_date: 조회 날짜 (기본: 어제)
- driver_name: 운전자명 검색 (옵션)

# 예시
curl "http://139.150.11.99/api/v1/driver-mileage/daily?target_date=2026-03-02"
curl "http://139.150.11.99/api/v1/driver-mileage/daily?driver_name=박운송"
```

### 2. 운전자 주행거리 재계산

```bash
POST /api/v1/driver-mileage/calculate

# 파라미터
- target_date: 계산 대상 날짜 (기본: 어제)

# 예시
curl -X POST "http://139.150.11.99/api/v1/driver-mileage/calculate?target_date=2026-03-02"
```

### 3. 응답 형식

```json
{
  "success": true,
  "date": "2026-03-02",
  "count": 9,
  "mileages": [
    {
      "driver_name": "박운송",
      "date": "2026-03-02",
      "total_distance_km": 537.25,
      "total_driving_minutes": 214,
      "engine_on_minutes": 128,
      "idle_minutes": 29,
      "max_speed_kmh": 90.0,
      "avg_speed_kmh": 76.3,
      "gps_point_count": 130,
      "start_time": "2026-03-02T17:15:56+00:00",
      "end_time": "2026-03-02T19:02:56+00:00",
      "vehicle_count": 2,
      "vehicle_ids": "20,32",
      "calculation_method": "vehicle_based"
    }
  ]
}
```

---

## ❌ 문제 해결

### 문제 1: "driver_id cannot be null" 에러

**증상:**
```
null value in column "driver_id" violates not-null constraint
```

**해결:**
```bash
# 마이그레이션을 다시 실행
cat backend/migrations/fix_driver_daily_mileage_nullable.sql | \
docker compose exec -T db psql -U uvis_user -d uvis_db
```

### 문제 2: "계산된 운전자 없음" 메시지

**원인:**
- 차량 테이블에 `driver_name`이 비어있음
- 해당 날짜에 GPS 데이터가 없음

**확인 방법:**
```bash
# 운전자가 등록된 차량 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT id, code, plate_number, driver_name, driver_phone 
FROM vehicles 
WHERE is_active = true 
  AND driver_name IS NOT NULL 
  AND driver_name != '';
"

# 해당 날짜의 차량 주행 기록 확인
docker compose exec db psql -U uvis_user -d uvis_db -c "
SELECT vehicle_id, date, total_distance_km, total_driving_minutes
FROM vehicle_daily_mileage
WHERE date = '2026-03-02'
ORDER BY total_distance_km DESC
LIMIT 10;
"
```

### 문제 3: Git Pull 실패 ("unstaged changes")

**해결:**
```bash
cd /root/uvis
git stash  # 변경사항 임시 저장
git pull origin main
git stash pop  # 변경사항 복원 (선택사항)
```

### 문제 4: 마이그레이션이 이미 적용된 경우

**증상:**
```
ERROR: constraint "..." already exists
```

**확인:**
정상입니다. 이미 적용된 마이그레이션이므로 무시하고 다음 단계로 진행하세요.

---

## 📈 예상 결과 (2026-03-02 기준)

| 운전자명 | 주행거리 | 주행시간 | 차량수 | 평균속도 | 최고속도 |
|---------|---------|---------|--------|---------|---------|
| 박운송 | 537.25 km | 214분 | 2대 | 76.3 km/h | 90 km/h |
| 김운전 | 147.90 km | 107분 | 1대 | 72.0 km/h | 86 km/h |
| 이기사 | 144.32 km | 106분 | 1대 | 60.5 km/h | 88 km/h |
| 정배차 | 144.26 km | 106분 | 1대 | 64.4 km/h | 88 km/h |
| 신작업 | 106.50 km | 106분 | 1대 | 48.8 km/h | 88 km/h |
| 최관리 | 106.07 km | 107분 | 1대 | 50.4 km/h | 89 km/h |
| 강운영 | 72.10 km | 107분 | 1대 | 53.4 km/h | 91 km/h |
| 서배송 | 83.08 km | 106분 | 1대 | 26.6 km/h | 88 km/h |
| 황택배 | 48.99 km | 106분 | 1대 | 18.8 km/h | 68 km/h |

---

## 📝 변경 파일 목록

```
backend/app/services/driver_mileage_service.py  (차량 기반 계산 로직)
backend/app/api/driver_mileage.py               (API 엔드포인트)
backend/migrations/fix_driver_daily_mileage_nullable.sql (DB 마이그레이션)
deploy_driver_mileage.sh                        (배포 스크립트)
```

---

## 🔗 관련 링크

- **Pull Request**: https://github.com/rpaakdi1-spec/3-/pull/13
- **GitHub Repository**: https://github.com/rpaakdi1-spec/3-

---

## ✅ 배포 체크리스트

- [ ] 1. 코드 업데이트 완료 (git pull)
- [ ] 2. 데이터베이스 마이그레이션 완료
- [ ] 3. 백엔드 재빌드 완료
- [ ] 4. 백엔드 재시작 완료
- [ ] 5. 서비스 상태 확인 (모두 healthy)
- [ ] 6. 운전자 주행거리 계산 테스트 성공
- [ ] 7. API 엔드포인트 테스트 성공
- [ ] 8. 데이터베이스 데이터 확인

---

## 📞 지원

문제가 발생하면 다음 정보를 제공해주세요:
1. 에러 메시지 전체
2. `docker compose ps` 출력
3. `docker compose logs backend --tail=50` 출력
4. 실행한 명령어

---

**작성일**: 2026-03-03  
**버전**: 1.0  
**작성자**: GenSpark AI Developer
