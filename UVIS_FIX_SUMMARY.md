# UVIS 실시간 통계 0 표시 문제 - 최종 해결 방안

**날짜**: 2026-02-28  
**상태**: ✅ 코드 수정 완료 (배포 대기 중)

---

## 🔍 문제 발견

대시보드에서 **UVIS 실시간 통계가 모두 0으로 표시**되는 문제:
- 운행 중 차량: **0대** / 46대 ❌
- 총 주행 거리: **0.0 km** ❌
- 평균 속도: **0.0 km/h** ❌
- 최고 속도: **0.0 km/h** ❌

---

## 🎯 근본 원인 (3단계)

### ✅ 1단계: 백엔드 GPS 시간 제한 (이미 해결됨)
- **파일**: `backend/app/services/vehicle_analytics_service.py`
- **문제**: GPS 데이터가 1시간 이내만 활성으로 간주
- **해결**: 1시간 → 24시간으로 확장
- **결과**: API `active_vehicles: 0` → `46`

### ✅ 2단계: 프론트엔드 날짜 범위 (이미 해결됨)
- **파일**: `frontend/src/components/vehicles/UvisFleetStats.tsx`
- **문제**: 오늘 날짜만 조회 → GPS 데이터 없음
- **해결**: 최근 7일 데이터 조회
- **결과**: API에서 183km 데이터 반환

### ✅ 3단계: 프론트엔드 카운트 로직 (🆕 신규 발견 및 수정)
- **파일**: `frontend/src/components/vehicles/UvisFleetStats.tsx`
- **문제**: 잘못된 로직으로 활성 차량 카운트
  ```typescript
  // ❌ 잘못된 로직
  const engineOnCount = vehicleStats.filter(v => v.engine_on_ratio > 50).length;
  ```
  - `engine_on_ratio`: 해당 기간 동안 엔진이 켜진 시간 비율
  - 50% 미만인 차량은 제외됨 → 0대로 표시
  
- **해결**: API의 `active_vehicles` 필드 직접 사용
  ```typescript
  // ✅ 올바른 로직
  const activeCount = stats.active_vehicles || 0;
  ```

---

## 📊 수정 전 vs 수정 후

| 항목 | 수정 전 | 수정 후 | 차이 |
|-----|---------|---------|------|
| **운행 중 차량** | 0대 / 46대 | 46대 / 46대 | +46대 |
| **총 주행 거리** | 0.0 km | 183.0 km | +183.0 km |
| **평균 속도** | 0.0 km/h | 26.8 km/h | +26.8 km/h |
| **최고 속도** | 0.0 km/h | 105.0 km/h | +105.0 km/h |

---

## 🚀 배포 방법

### **옵션 1: 자동 스크립트 사용 (권장)**
```bash
cd /root/uvis
git pull origin main
bash deploy_uvis_frontend_fix.sh
```

### **옵션 2: 수동 배포**
```bash
cd /root/uvis
git pull origin main
docker-compose down frontend
docker-compose up -d --build frontend
sleep 30
curl "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-21&end_date=2026-02-28" | python3 -m json.tool | grep active_vehicles
```

---

## ✅ 검증 방법

### 1. 브라우저에서 확인
1. http://139.150.11.99/ 접속
2. **Ctrl+Shift+R** (강력 새로고침)
3. 대시보드 하단의 **"UVIS 실시간 통계"** 섹션 확인

**기대 결과**:
```
UVIS 실시간 통계
실시간 업데이트
운행 중 차량: 46대 / 46대  ✅
총 주행 거리: 183.0 km      ✅
평균 속도: 26.8 km/h        ✅
최고 속도: 105.0 km/h       ✅
```

### 2. 개발자 도구에서 확인
**F12** → **Console** 탭:
```javascript
fetch('/api/v1/vehicles/analytics/fleet?start_date=2026-02-21&end_date=2026-02-28')
  .then(r => r.json())
  .then(d => console.log('Active:', d.active_vehicles, 'Distance:', d.total_distance_km));
```

**기대 결과**: `Active: 46 Distance: 183.0`

---

## 🔧 수정된 파일

### 백엔드
- `backend/app/services/vehicle_analytics_service.py`
  - Line 199, 247: `timedelta(hours=1)` → `timedelta(hours=24)`

### 프론트엔드
- `frontend/src/components/vehicles/UvisFleetStats.tsx`
  - Line 41-44: 오늘 → 최근 7일 조회
  - Line 88-90: `engineOnCount` 계산 제거, `activeCount = stats.active_vehicles` 사용
  - Line 99: `value: engineOnCount` → `value: activeCount`

---

## 📝 Git 커밋

```bash
# 로컬 커밋 (webapp 디렉토리)
fe19260 feat: Add UVIS frontend fix deployment script
6a65602 docs: Add comprehensive UVIS frontend display fix documentation
d022292 fix: Use API active_vehicles count instead of engine_on_ratio calculation
9ea979b fix: Change UVIS stats to query last 7 days instead of today only

# 서버 커밋 (이미 적용됨)
19d32fd fix: Relax GPS time limit to 24 hours for UVIS statistics
```

---

## 🐛 문제가 지속되면

### 디버깅 스크립트 실행
```bash
cd /root/uvis
bash debug_uvis_frontend.sh
python3 test_uvis_frontend.py
```

### 브라우저 캐시 완전 삭제
1. **Ctrl+Shift+Delete**
2. **캐시된 이미지 및 파일** 선택
3. **전체 기간** 선택
4. **데이터 삭제**
5. 브라우저 재시작

### 프라이빗 브라우징으로 테스트
- **Chrome/Edge**: Ctrl+Shift+N
- **Firefox**: Ctrl+Shift+P
- http://139.150.11.99/ 접속

---

## 📚 관련 문서

- **UVIS_FRONTEND_DISPLAY_FIX.md** - 상세 분석 및 해결 방법
- **UVIS_STATISTICS_FIX_COMPLETE.md** - 백엔드 수정 내역
- **deploy_uvis_frontend_fix.sh** - 자동 배포 스크립트
- **debug_uvis_frontend.sh** - 디버깅 스크립트
- **test_uvis_frontend.py** - API 분석 스크립트

---

## 🎯 핵심 교훈

1. **API 응답 vs 계산 값**
   - API가 제공하는 `active_vehicles` 필드를 직접 사용하는 것이 정확
   - `engine_on_ratio > 50%` 같은 임의의 계산은 예측 불가능한 결과 초래

2. **백엔드와 프론트엔드 로직 일치**
   - 백엔드: 24시간 이내 GPS = 활성
   - 프론트엔드: API의 `active_vehicles` 사용
   - 두 로직이 일치해야 일관된 결과

3. **날짜 범위 설정의 중요성**
   - 실시간 시스템에서도 과거 데이터를 포함하는 것이 안전
   - 7일 범위로 설정하여 GPS 지연에도 대응

---

**Repository**: https://github.com/rpaakdi1-spec/3-  
**현재 상태**: 로컬 커밋 완료, 서버 배포 대기  
**다음 단계**: 서버에서 `git pull origin main` 및 frontend 재빌드 🚀
