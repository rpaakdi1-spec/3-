# 🚀 UVIS UI 완성 - 서버 배포 가이드

**배포 날짜**: 2026-02-26  
**최신 커밋**: `cc5fac8`  
**새로운 기능**: 알림 토스트 + 온도 차트 + 경로 이력

---

## 📦 배포 내용

### 백엔드 API (3개 신규)
1. **GET** `/api/v1/vehicles/{vehicle_id}/temperature/history`
   - 차량 온도 이력 조회
   - Query: `hours` (기본값: 24시간)

2. **GET** `/api/v1/vehicles/{vehicle_id}/gps/history`
   - 차량 GPS 경로 이력 조회
   - Query: `hours` (기본값: 24시간)

3. **GET** `/api/v1/vehicles/alerts/recent` (이미 존재, 개선됨)
   - 최근 알림 조회
   - Query: `limit`, `vehicle_id`, `alert_type`

### 프론트엔드 컴포넌트 (5개 신규)
1. `UvisAlertToast.tsx` - 실시간 알림 토스트
2. `UvisTemperatureChart.tsx` - 온도 차트
3. `TemperatureChartModal.tsx` - 온도 차트 모달
4. `RouteHistoryModal.tsx` - 경로 이력 모달
5. `DashboardPage.tsx` (수정) - 알림 토스트 통합

---

## 🔧 배포 단계

### 1단계: 서버 접속 및 코드 업데이트

```bash
# 서버 접속 후
cd /root/uvis

# 현재 브랜치 확인
git branch
# main 브랜치여야 함

# 최신 코드 가져오기
git fetch origin main
git pull origin main

# 최신 커밋 확인
git log --oneline -5
# 다음이 보여야 합니다:
# cc5fac8 - feat(uvis): Add GPS route history visualization
# fa72548 - feat(uvis): Add temperature chart visualization
# db20ecb - feat(uvis): Add temperature history API endpoint
# baea5b7 - feat(uvis): Add real-time alert toast notifications
# 7acb608 - docs: Add comprehensive v1.0 release notes
```

### 2단계: 백엔드 재빌드

```bash
cd /root/uvis

# 백엔드 중지
docker-compose stop backend

# 백엔드 컨테이너 제거
docker-compose rm -f backend

# 백엔드 재빌드 (캐시 없이)
docker-compose build --no-cache backend

# 백엔드 시작
docker-compose up -d backend

# 시작 대기 (30초)
sleep 30

# 로그 확인
docker-compose logs backend --tail=50 | grep -E "(Started|ERROR|WARNING)"
```

**확인 사항**:
- ✅ "Application startup complete" 메시지
- ✅ "Scheduler started" 메시지
- ❌ 에러 메시지 없음

### 3단계: 백엔드 API 테스트

```bash
# 1. 온도 이력 API 테스트
echo "=== 온도 이력 API 테스트 ==="
curl -s "http://localhost:8000/api/v1/vehicles/1/temperature/history?hours=24" | jq '{vehicle_plate, total_points, data_points: (.data_points | length)}'

# 2. GPS 이력 API 테스트
echo ""
echo "=== GPS 이력 API 테스트 ==="
curl -s "http://localhost:8000/api/v1/vehicles/1/gps/history?hours=24" | jq '{vehicle_plate, total_points, total_distance_km, max_speed_kmh}'

# 3. 알림 API 테스트
echo ""
echo "=== 알림 API 테스트 ==="
curl -s "http://localhost:8000/api/v1/vehicles/alerts/recent?limit=5" | jq '{total, alerts: (.alerts | length)}'
```

**예상 결과**:
- 온도 이력: `vehicle_plate`, `total_points`, `data_points` 반환
- GPS 이력: `vehicle_plate`, `total_points`, `total_distance_km` 반환
- 알림: `total`, `alerts` 배열 반환

### 4단계: 프론트엔드 빌드

```bash
cd /root/uvis/frontend

# 기존 빌드 백업 (선택사항)
if [ -d "dist" ]; then
    mv dist dist.backup.$(date +%Y%m%d_%H%M%S)
fi

# 프론트엔드 빌드
npm run build

# 빌드 확인
ls -lh dist/
ls -lh dist/assets/ | head -10
```

**확인 사항**:
- ✅ `dist/` 폴더 생성
- ✅ `dist/index.html` 존재
- ✅ `dist/assets/` 폴더에 JS/CSS 파일들
- ✅ 빌드 시간 ~13초
- ❌ 빌드 에러 없음

### 5단계: 프론트엔드 재시작

```bash
cd /root/uvis

# 프론트엔드 재시작
docker-compose restart frontend

# 재시작 대기 (10초)
sleep 10

# 로그 확인
docker-compose logs frontend --tail=20

# Nginx 재시작 (필요시)
docker-compose restart nginx

# 전체 상태 확인
docker-compose ps
```

**확인 사항**:
- ✅ frontend 컨테이너 `Up` 상태
- ✅ nginx 컨테이너 `Up` 상태
- ✅ backend 컨테이너 `Up` 상태

### 6단계: 헬스 체크

```bash
# 프론트엔드 접근 확인
echo "=== 프론트엔드 헬스 체크 ==="
curl -I http://localhost/ 2>&1 | grep "HTTP"

# 백엔드 헬스 체크
echo ""
echo "=== 백엔드 헬스 체크 ==="
curl -s http://localhost:8000/api/v1/health | jq '.'

# Nginx 상태 확인
echo ""
echo "=== Nginx 상태 ==="
docker-compose logs nginx --tail=5 | grep -E "(GET|POST|error)"
```

**예상 결과**:
- 프론트엔드: `HTTP/1.1 200 OK`
- 백엔드: `{"status": "healthy"}`
- Nginx: 최근 요청 로그 표시

---

## 🧪 브라우저 테스트

### 1. 대시보드 - 알림 토스트
**URL**: `http://139.150.11.99/`

**테스트 항목**:
- [ ] 페이지 로드 정상
- [ ] UVIS 실시간 통계 위젯 표시
- [ ] UVIS 알림 위젯 표시
- [ ] 30초 대기 후 자동 새로고침
- [ ] 새 알림 발생 시 토스트 표시 (있는 경우)

**알림 토스트 확인**:
- 브라우저 알림 권한 요청 팝업 (처음 방문 시)
- 새 알림 발생 시 우측 상단에 토스트 표시
- 토스트 클릭 시 차량 페이지로 이동
- 8초 후 자동 닫기 또는 X 버튼으로 수동 닫기

### 2. 차량 관리 - 온도 차트
**URL**: `http://139.150.11.99/vehicles`

**테스트 항목**:
- [ ] 차량 목록/지도 표시
- [ ] 차량 카드에서 온도 정보 확인
- [ ] (추후) 온도 차트 보기 버튼 클릭
- [ ] 온도 차트 모달 열림
- [ ] 현재/최저/최고/평균 온도 표시
- [ ] Chart.js 라인 차트 렌더링
- [ ] 시간 범위 변경 (6h, 12h, 24h, etc.)
- [ ] 30초 후 자동 새로고침

### 3. 차량 관리 - 경로 이력
**URL**: `http://139.150.11.99/vehicles`

**테스트 항목**:
- [ ] (추후) 경로 이력 보기 버튼 클릭
- [ ] 경로 이력 모달 열림
- [ ] Naver Maps 지도 표시
- [ ] 경로 Polyline (파란색) 표시
- [ ] 시작 마커 (초록색 "시작") 표시
- [ ] 종료 마커 (빨간색 "종료") 표시
- [ ] 정차 마커 (주황색 "P") 표시
- [ ] 우측 패널에 주행 통계 표시
- [ ] 시간 범위 변경 테스트

### 4. 브라우저 콘솔 확인
**F12 → Console 탭**

**확인 사항**:
- ❌ JavaScript 에러 없음
- ❌ API 호출 실패 (404, 500) 없음
- ✅ API 호출 성공 (200) 로그
- ✅ "WebSocket connected" 메시지 (있는 경우)

---

## 🐛 문제 해결

### 문제 1: 백엔드 API 404 에러
**증상**: 온도/GPS 이력 API 호출 시 404

**해결**:
```bash
# API 라우터 등록 확인
cd /root/uvis
grep -n "temperature/history" backend/app/api/vehicles.py
grep -n "gps/history" backend/app/api/vehicles.py

# 백엔드 재시작
docker-compose restart backend
sleep 30

# API 재테스트
curl "http://localhost:8000/api/v1/vehicles/1/temperature/history?hours=24"
```

### 문제 2: 프론트엔드 빌드 실패
**증상**: `npm run build` 에러

**해결**:
```bash
cd /root/uvis/frontend

# node_modules 재설치
rm -rf node_modules package-lock.json
npm install

# 다시 빌드
npm run build
```

### 문제 3: 차트 표시 안됨
**증상**: 온도 차트가 빈 화면

**해결**:
- F12 → Console에서 에러 확인
- Chart.js 라이브러리 로드 확인
- API 응답 데이터 확인 (F12 → Network 탭)

### 문제 4: 지도 표시 안됨
**증상**: 경로 이력 모달에 지도 안 보임

**해결**:
- Naver Maps API 키 확인
- 브라우저 콘솔에서 지도 로드 에러 확인
- `window.naver.maps` 객체 존재 확인

---

## ✅ 배포 완료 체크리스트

### 서버
- [ ] 최신 코드 pull (커밋 `cc5fac8`)
- [ ] 백엔드 재빌드 완료
- [ ] 백엔드 시작 완료 (로그 정상)
- [ ] 프론트엔드 빌드 완료 (`dist/` 폴더)
- [ ] 프론트엔드 재시작 완료
- [ ] 전체 컨테이너 `Up` 상태

### API 테스트
- [ ] 온도 이력 API 응답 정상
- [ ] GPS 이력 API 응답 정상
- [ ] 알림 API 응답 정상

### 브라우저 테스트
- [ ] 대시보드 페이지 로드
- [ ] 알림 토스트 작동 (새 알림 시)
- [ ] 차량 페이지 로드
- [ ] (추후) 온도 차트 모달 작동
- [ ] (추후) 경로 이력 모달 작동
- [ ] JavaScript 에러 없음

---

## 📊 배포 후 모니터링

### 로그 모니터링
```bash
# 백엔드 로그 실시간 확인 (새 터미널)
docker-compose logs -f backend

# 프론트엔드 로그 실시간 확인 (새 터미널)
docker-compose logs -f frontend nginx

# 에러 필터링
docker-compose logs backend --tail=100 | grep -i error
```

### 성능 모니터링
```bash
# 컨테이너 리소스 사용량
docker stats --no-stream

# API 응답 시간 측정
time curl -s "http://localhost:8000/api/v1/vehicles/1/temperature/history?hours=24" > /dev/null
time curl -s "http://localhost:8000/api/v1/vehicles/1/gps/history?hours=24" > /dev/null
```

---

## 🎉 배포 완료!

배포가 완료되면 다음 정보를 확인하세요:

**프로덕션 URL**: `http://139.150.11.99/`

**새로운 기능**:
1. ✅ 실시간 알림 토스트 (대시보드)
2. ✅ 온도 차트 (차량 상세)
3. ✅ 경로 이력 시각화 (차량 상세)

**API 엔드포인트**:
- `GET /api/v1/vehicles/{id}/temperature/history`
- `GET /api/v1/vehicles/{id}/gps/history`
- `GET /api/v1/vehicles/alerts/recent`

---

**배포 시작 시간**: _____________  
**배포 완료 시간**: _____________  
**배포 담당자**: _____________  
**배포 상태**: ⏳ 진행 중 / ✅ 완료 / ❌ 실패

---

## 📝 다음 단계

배포 완료 후:
1. 사용자 피드백 수집
2. 버그 리포트 확인
3. 다음 Phase 개발 계획
   - Phase 16: FCM Push + 파일 업로드 + 채팅
   - 프로덕션 준비: 성능 + 보안
   - Phase 17/18: 고객 포털 + 모바일 앱

---

**문의 사항이나 문제 발생 시 개발팀에 연락하세요!** 🚀
