# Phase 12 배포 가이드

## 배포 날짜
2026-02-11

## 🎉 Phase 12 완료!

Phase 12 "핵심 통합: 네이버 맵 + UVIS GPS + AI 배차"가 완전히 완료되었습니다!

## 📦 완성된 기능

### Backend Services (3개)
1. **IntegratedDispatchService** (17KB)
   - 자동 배차 로직
   - 거리/시간 계산 (네이버 맵 API)
   - 배차 규칙 적용 (Phase 10 통합)
   - 설명 가능한 AI

2. **VehicleTrackingService** (5.6KB)
   - 실시간 위치 추적
   - WebSocket 브로드캐스팅
   - 30초 주기 업데이트

3. **DispatchAnalyticsService** (10.3KB)
   - 배차 통계 분석
   - 기사 성과 분석
   - 최적화 제안
   - 시간대별 패턴 분석

### Backend APIs (9개)
- POST `/api/v1/dispatch/auto` - 자동 배차 실행
- POST `/api/v1/dispatch/batch` - 일괄 배차
- GET `/api/v1/vehicles/map` - 지도용 차량 위치
- GET `/api/v1/routes/{order_id}` - 경로 조회
- GET `/api/v1/vehicles/{vehicle_id}/location` - 실시간 위치
- GET `/api/v1/dispatch/analytics/statistics` - 배차 통계
- GET `/api/v1/dispatch/analytics/driver-performance` - 기사 성과
- GET `/api/v1/dispatch/analytics/suggestions` - 최적화 제안
- GET `/api/v1/dispatch/analytics/hourly-pattern` - 시간대별 패턴

### Frontend Pages (3개)
1. **실시간 차량 추적** (`/vehicle-tracking`)
   - 네이버 맵 통합
   - 실시간 차량 위치 표시
   - 차량 상태별 필터링
   - 차량 상세 정보

2. **AI 자동 배차** (`/auto-dispatch`)
   - 주문 선택
   - 시뮬레이션 모드
   - AI 자동 배차 실행
   - 배차 결과 및 AI 설명

3. **배차 분석 대시보드** (`/dispatch-analytics`)
   - 실시간 통계 카드
   - 기사 성과 차트
   - 시간대별 패턴 분석
   - AI 최적화 제안

### Frontend Components (1개)
1. **NaverMap** (9.1KB)
   - 네이버 맵 React 컴포넌트
   - 차량 마커 표시 (상태별 색상)
   - 경로 표시
   - 정보창 & 범례

## 🚀 서버 배포 방법

### 전제 조건
- 서버 위치: `/root/uvis`
- Git 저장소: 최신 상태
- Docker & Docker Compose 실행 중

### 방법 1: 자동 스크립트 (권장, 30초)

```bash
# 서버에서 실행
cd /root/uvis
git pull origin main
./scripts/deploy-no-build.sh
```

이 스크립트는 자동으로:
1. Git 최신 코드 가져오기
2. frontend-dist-phase12.tar.gz 압축 해제
3. Docker 컨테이너에 복사
4. Nginx 재시작
5. 배포 검증

### 방법 2: 수동 배포 (15초)

```bash
# 서버에서 실행
cd /root/uvis

# 1. 최신 코드 받기
git pull origin main

# 2. 빌드 패키지 압축 해제
cd frontend
tar -xzf ../frontend-dist-phase12.tar.gz

# 3. Nginx 컨테이너 이름 확인
docker ps --format "{{.Names}}" | grep -E "(nginx|frontend)"

# 4. dist를 Nginx 컨테이너에 복사 (컨테이너 이름에 맞게 수정)
docker cp dist/. uvis-frontend-1:/usr/share/nginx/html/
# 또는
docker cp dist/. uvis_frontend_1:/usr/share/nginx/html/

# 5. Nginx 재시작
docker-compose restart nginx

# 6. 대기
sleep 5

# 7. 배포 확인
curl -I http://localhost/
curl http://localhost:8000/api/v1/dispatch/analytics/statistics
```

## ✅ 배포 검증

### 1. Backend API 확인

```bash
# 서버에서 실행

# 배차 통계
curl http://localhost:8000/api/v1/dispatch/analytics/statistics | jq

# 차량 위치
curl http://localhost:8000/api/v1/vehicles/map | jq

# 기사 성과
curl http://localhost:8000/api/v1/dispatch/analytics/driver-performance | jq
```

### 2. Frontend 확인

브라우저에서 다음 URL을 차례로 테스트:

1. **실시간 차량 추적**
   - URL: `http://139.150.11.99/vehicle-tracking`
   - 체크리스트:
     - [ ] 네이버 맵이 표시되는가?
     - [ ] 차량 마커가 표시되는가?
     - [ ] 차량 필터링이 작동하는가?
     - [ ] 차량 클릭 시 상세 정보가 표시되는가?

2. **AI 자동 배차**
   - URL: `http://139.150.11.99/auto-dispatch`
   - 체크리스트:
     - [ ] 주문 선택이 가능한가?
     - [ ] 시뮬레이션 모드가 작동하는가?
     - [ ] 배차 실행이 성공하는가?
     - [ ] AI 설명이 표시되는가?

3. **배차 분석 대시보드**
   - URL: `http://139.150.11.99/dispatch-analytics`
   - 체크리스트:
     - [ ] 통계 카드가 표시되는가?
     - [ ] 기사 성과 차트가 표시되는가?
     - [ ] 시간대별 패턴 차트가 표시되는가?
     - [ ] 최적화 제안이 표시되는가?

### 3. 메뉴 확인

좌측 사이드바에서 다음 메뉴들이 "NEW" 배지와 함께 표시되는지 확인:

- [ ] 실시간 차량 추적 (MapPin 아이콘)
- [ ] AI 자동 배차 (Zap 아이콘)
- [ ] 배차 분석 대시보드 (TrendingUp 아이콘)

### 4. Docker 상태 확인

```bash
# 서버에서 실행
docker-compose ps

# 예상 출력: 모든 컨테이너가 "Up (healthy)" 상태
```

## 🔧 문제 해결

### 문제 1: Frontend가 표시되지 않음

```bash
# Nginx 로그 확인
docker logs uvis-frontend-1

# Nginx 재시작
docker-compose restart frontend nginx

# 브라우저 캐시 완전 삭제
# Chrome: Ctrl+Shift+Delete → "전체 기간" 선택 → 쿠키 및 캐시 삭제
```

### 문제 2: Backend API가 응답하지 않음

```bash
# Backend 로그 확인
docker logs uvis-backend

# Backend 재시작
docker-compose restart backend

# API 엔드포인트 확인
curl http://localhost:8000/api/v1/health
```

### 문제 3: 네이버 맵이 표시되지 않음

환경 변수 확인:
```bash
# .env 파일에서 네이버 맵 API 키 확인
grep NAVER_MAP /root/uvis/backend/.env

# 필요한 환경 변수:
NAVER_MAP_CLIENT_ID=your_client_id
NAVER_MAP_CLIENT_SECRET=your_client_secret
```

### 문제 4: WebSocket 연결 실패

```bash
# Redis 상태 확인
docker-compose ps redis

# Redis 로그 확인
docker logs uvis-redis

# Backend WebSocket 엔드포인트 확인
curl http://localhost:8000/api/v1/ws
```

## 📊 성능 지표

### 예상 응답 시간
- 자동 배차 API: < 2초
- 차량 위치 조회: < 500ms
- 배차 통계: < 1초
- 실시간 위치 업데이트: 30초 주기

### 리소스 사용량
- Backend 메모리: ~1.2GB
- Frontend 메모리: ~100MB
- Redis 메모리: ~50MB
- 총 CPU: < 50%

## 🎯 다음 단계

Phase 12 배포가 완료되면:

1. **운영 테스트** (1-2일)
   - 실제 주문으로 자동 배차 테스트
   - 실시간 차량 추적 모니터링
   - 분석 데이터 수집

2. **성능 최적화** (필요 시)
   - API 응답 시간 개선
   - WebSocket 연결 안정성 개선
   - 캐싱 전략 적용

3. **Phase 11-A: 날씨 기반 배차** (5일)
   - 날씨 API 통합
   - 날씨 기반 배차 규칙
   - 악천후 대응

4. **Phase 11-B: 교통 정보 연동** (7일)
   - 실시간 교통 정보
   - 경로 최적화
   - 도착 시간 예측

5. **Phase 15: AI 자동 학습** (15일)
   - 강화학습 모델
   - 자동 규칙 생성
   - 지속적 개선

## 📝 커밋 히스토리

### Phase 12 관련 커밋
- `0b085d5` - fix: Fix API imports and add Phase 12 build package
- `8826ede` - feat: Day 6-7 - Complete Analytics Dashboard & Integration
- `fdec04e` - feat: Day 4-5 - Frontend Naver Map & Auto Dispatch UI
- `9dbe45e` - feat: Day 2-3 - Backend enhancement complete
- `f2d148b` - feat: Day 1 - Add IntegratedDispatchService

### 파일 변경 요약
```
Backend:
- backend/app/services/integrated_dispatch_service.py (신규)
- backend/app/services/vehicle_tracking_service.py (신규)
- backend/app/services/dispatch_analytics_service.py (신규)
- backend/app/api/integrated_dispatch.py (신규)
- backend/main.py (수정)

Frontend:
- frontend/src/components/map/NaverMap.tsx (신규)
- frontend/src/pages/VehicleTrackingPage.tsx (신규)
- frontend/src/pages/AutoDispatchPage.tsx (신규)
- frontend/src/pages/DispatchAnalyticsDashboard.tsx (신규)
- frontend/src/App.tsx (수정)
- frontend/src/components/common/Sidebar.tsx (수정)

Documentation:
- docs/PHASE12_DAY6-7_COMPLETE.md (신규)
- docs/PHASE12_DEPLOYMENT.md (신규)

Build:
- frontend-dist-phase12.tar.gz (신규, 546KB)
```

## 🏆 Phase 12 완료 기념!

축하합니다! Phase 12가 완전히 완료되었습니다!

### 주요 성과
- ✅ 완전 자동화된 배차 시스템
- ✅ 실시간 차량 추적
- ✅ AI 기반 의사결정 지원
- ✅ 데이터 기반 최적화
- ✅ 확장 가능한 아키텍처

### 통합된 시스템
- ✅ 네이버 맵 API
- ✅ UVIS GPS API
- ✅ Phase 10 Rule Engine
- ✅ WebSocket 실시간 통신
- ✅ AI 분석 및 최적화

이제 서버에 배포하고 실제 운영 환경에서 테스트할 준비가 완료되었습니다! 🚀
