# 🔍 실시간 모니터링 대시보드 GPS 데이터 수정 가이드

## 🚨 발견된 문제

스크린샷에서 확인된 문제:
- **차량 위치: 0** (GPS 데이터 없음)
- **지도에 차량 마커 표시 안 됨**
- **실시간 정보 누락**

## 🎯 가능한 원인

### 1. GPS 데이터가 DB에 없음 ⭐ (가장 가능성 높음)
- UVIS API에서 GPS 데이터를 아직 동기화하지 않음
- `vehicle_gps_logs` 테이블이 비어있음

### 2. UVIS Device ID 미설정
- 차량에 `uvis_device_id`가 설정되지 않음
- GPS 데이터와 차량 매칭 실패

### 3. Frontend 캐시 문제
- 이전 버전의 Frontend가 캐시됨
- 새로고침이 필요함

## 🔧 진단 및 해결 방법

### Step 1: 진단 스크립트 실행 (필수!)

```bash
cd /root/uvis
./diagnose_realtime_dashboard.sh
```

**예상 출력:**
```
🔍 실시간 모니터링 대시보드 GPS 데이터 진단
=============================================

1️⃣  Backend Health Check...
✅ Backend is healthy

2️⃣  차량 목록 확인...
   활성 차량: 5대

3️⃣  GPS 로그 확인...
   전체 GPS 로그: 0건  ← ⚠️ 문제!
   ⚠️  GPS 로그가 없습니다!

4️⃣  온도 로그 확인...
   전체 온도 로그: 0건

🔧 문제 진단 요약
=================
   ❌ GPS 데이터가 없습니다
      → 대시보드에서 'GPS 동기화' 버튼을 클릭하세요
```

### Step 2: GPS 데이터 동기화

#### 방법 1: 브라우저에서 (권장)

```
1. 실시간 모니터링 대시보드 접속
   http://139.150.11.99/realtime-dashboard

2. 상단의 "GPS 동기화" 버튼 클릭
   - 토스트 메시지: "GPS 데이터 동기화 완료: N건"

3. 페이지 자동 새로고침
   - 지도에 차량 마커 표시됨
   - 차량 위치 정보 표시됨
```

#### 방법 2: API 직접 호출

```bash
# GPS 동기화
curl -X POST http://localhost:8000/api/v1/uvis-gps/sync/gps \
  -H "Content-Type: application/json" \
  -d '{"force_new_key": false}'

# 온도 동기화 (선택)
curl -X POST http://localhost:8000/api/v1/uvis-gps/sync/temperature \
  -H "Content-Type: application/json" \
  -d '{"force_new_key": false}'

# 또는 전체 동기화
curl -X POST http://localhost:8000/api/v1/uvis-gps/sync/all \
  -H "Content-Type: application/json" \
  -d '{"force_new_key": false}'
```

**예상 응답:**
```json
{
  "success": true,
  "message": "GPS 데이터 동기화 완료: 5건",
  "gps_count": 5,
  "access_key_issued": false
}
```

### Step 3: 차량 Device ID 확인 (필요 시)

```bash
# Device ID 확인
docker exec uvis-db psql -U uvis_user -d uvis_db -c \
  "SELECT id, code, plate_number, uvis_device_id 
   FROM vehicles 
   WHERE is_active = true;"
```

**Device ID가 없으면:**
1. 차량 관리 페이지 접속
2. 차량 수정
3. "UVIS Device ID" 필드에 입력
4. 저장

### Step 4: 재진단

```bash
./diagnose_realtime_dashboard.sh
```

**예상 출력 (성공 시):**
```
3️⃣  GPS 로그 확인...
   전체 GPS 로그: 25건  ← ✅ 증가!
   최근 GPS 로그 (최대 5건):
   vehicle_id | latitude  | longitude  | speed_kmh | is_engine_on
   -----------+-----------+------------+-----------+--------------
            1 |  37.5665  |  126.9780  |        45 | t
            2 |  35.1796  |  129.0756  |         0 | f

6️⃣  실시간 차량 상태 API 테스트...
   ✅ API 호출 성공
   응답 차량 수: 5대  ← ✅ 정상!

✅ 데이터베이스에는 문제가 없습니다
```

### Step 5: Frontend 확인

```
1. 브라우저 캐시 삭제
   Ctrl+Shift+Delete → 캐시 삭제

2. 강제 새로고침
   Ctrl+Shift+R

3. 실시간 모니터링 대시보드 접속
   http://139.150.11.99/realtime-dashboard

4. 확인 사항:
   ✅ 지도에 차량 마커 표시
   ✅ 차량 번호판 표시
   ✅ 차량 위치 (위도, 경도)
   ✅ 속도, 시동 상태, 온도
```

## 📊 정상 작동 시 화면

### 지도
- 🚗 차량 마커가 실제 위치에 표시됨
- 차량 번호판 라벨이 마커 위에 표시됨
- 색상:
  - 🟢 녹색: 시동 켜짐, 정상 온도
  - 🔵 파란색: 냉동 (-18°C 이하)
  - 🟡 노란색: 시동 꺼짐
  - ⚪ 회색: GPS 데이터 없음

### 차량 정보
```
차량번호: 12가3456
위도: 37.5665
경도: 126.9780
속도: 45 km/h
시동: 켜짐
온도 A: -20°C
온도 B: -18°C
최종 업데이트: 2026-02-03 14:30:25
```

## 🔄 자동 업데이트 설정

### Backend: 주기적 GPS 동기화 (선택)

현재는 수동 동기화만 지원합니다. 자동 동기화를 원하면:

```python
# backend/app/core/scheduler.py (새 파일)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.uvis_gps_service import UvisGPSService

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=5)
async def sync_gps_data():
    """5분마다 GPS 데이터 자동 동기화"""
    service = UvisGPSService()
    await service.get_vehicle_gps_data()
    logger.info("✅ Auto GPS sync completed")

scheduler.start()
```

### Frontend: 자동 새로고침

현재 Frontend는 이미 10초마다 자동으로 차량 데이터를 새로고침합니다:

```typescript
// RealtimeDashboardPage.tsx
useEffect(() => {
  const interval = setInterval(() => {
    fetchRealtimeVehicles();  // 10초마다 자동 새로고침
  }, 10000);
  
  return () => clearInterval(interval);
}, []);
```

## 🐛 트러블슈팅

### 문제 1: "GPS 데이터 동기화 실패"

**원인:** UVIS API 키 없음 또는 만료

**해결:**
```bash
# .env 파일 확인
grep UVIS .env

# 없으면 추가
echo "UVIS_API_URL=https://api.uvis.co.kr" >> .env
echo "UVIS_API_KEY=your_api_key" >> .env

# Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

### 문제 2: 차량이 지도에 표시되지만 위치가 0,0

**원인:** GPS 데이터가 null

**진단:**
```bash
docker exec uvis-db psql -U uvis_user -d uvis_db -c \
  "SELECT vehicle_id, latitude, longitude FROM vehicle_gps_logs 
   WHERE latitude IS NULL OR longitude IS NULL 
   LIMIT 5;"
```

**해결:**
- GPS 동기화 재실행
- UVIS API에서 실제 GPS 데이터 확인

### 문제 3: 일부 차량만 표시됨

**원인:** Device ID 미설정

**진단:**
```bash
./diagnose_realtime_dashboard.sh
# → "일부 차량에 Device ID가 없습니다" 메시지 확인
```

**해결:**
- 차량 관리에서 Device ID 입력

### 문제 4: "응답 차량 수: 0대"

**원인:** API 응답은 성공했지만 GPS 데이터 없음

**해결:**
```bash
# GPS 데이터 동기화
curl -X POST http://localhost:8000/api/v1/uvis-gps/sync/gps \
  -H "Content-Type: application/json" \
  -d '{"force_new_key": false}'

# 재확인
curl -s http://localhost:8000/api/v1/uvis-gps/realtime/vehicles | jq .
```

## 📝 핵심 파일

### Backend
- `backend/app/api/uvis_gps.py` - UVIS GPS API 엔드포인트
- `backend/app/services/uvis_gps_service.py` - UVIS API 연동 서비스
- `backend/app/models/uvis_gps.py` - GPS/온도 로그 모델

### Frontend
- `frontend/src/pages/RealtimeDashboardPage.tsx` - 실시간 대시보드
- `frontend/src/services/api.ts` - UVIS API 호출

### Database Tables
- `vehicles` - 차량 정보 (uvis_device_id 포함)
- `vehicle_gps_logs` - GPS 로그
- `vehicle_temperature_logs` - 온도 로그

## 🚀 즉시 실행 가이드

```bash
cd /root/uvis

# 1. 진단 실행
./diagnose_realtime_dashboard.sh

# 2. GPS 데이터가 없으면 동기화
curl -X POST http://localhost:8000/api/v1/uvis-gps/sync/all \
  -H "Content-Type: application/json" \
  -d '{"force_new_key": false}'

# 3. 재진단
./diagnose_realtime_dashboard.sh

# 4. 브라우저에서 확인
# http://139.150.11.99/realtime-dashboard
# Ctrl+Shift+R (강제 새로고침)
```

## 📞 결과 공유 요청

진단 후 다음 정보를 공유해주세요:

1. **진단 스크립트 출력**
   ```bash
   ./diagnose_realtime_dashboard.sh > diagnosis_result.txt
   cat diagnosis_result.txt
   ```

2. **GPS 동기화 결과**
   - 동기화된 GPS 건수
   - 에러 메시지 (있는 경우)

3. **브라우저 스크린샷**
   - 실시간 대시보드 화면
   - 지도에 차량 마커 표시 여부
   - 차량 정보 패널

4. **Backend 로그**
   ```bash
   docker logs uvis-backend --tail 50 | grep -E "GPS|UVIS|realtime"
   ```

## 🔗 리포지토리 정보

- **GitHub:** https://github.com/rpaakdi1-spec/3-
- **브랜치:** main
- **최신 커밋:** ad58441
- **커밋 메시지:** feat: Add realtime dashboard GPS diagnostic script

---

**지금 바로 진단 스크립트를 실행하고 결과를 공유해주세요!** 🚀

```bash
cd /root/uvis && ./diagnose_realtime_dashboard.sh
```
