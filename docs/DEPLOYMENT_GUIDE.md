# Phase 10~16 전체 배포 가이드

## 현재 상태 요약

### ✅ 완료된 Phase
- **Phase 10**: Smart Dispatch Rule Engine (배차 규칙 엔진)
- **Phase 11-C**: Rule Simulation (규칙 시뮬레이션)
- **Phase 11-B**: Traffic Information Integration (교통 정보 연동)
- **Phase 12**: Integrated Dispatch (통합 배차 - Naver Map + GPS + AI)
- **Phase 13-14**: IoT Sensor Monitoring + Predictive Maintenance
- **Phase 15**: ML Auto-Learning (AI 자동 학습)
- **Phase 16**: Driver App Enhancement (드라이버 앱 고도화) ✨ **최신**

### 📊 통합 테스트 결과
- **Phase 16**: ✅ 정상 작동 (서버에 배포됨)
- **Phase 10~15**: ❌ 서버 배포 필요

---

## 🚀 긴급 배포 절차

서버(139.150.11.99)에 SSH로 접속하여 다음 명령어를 순서대로 실행하세요.

### Step 1: 서버 코드 업데이트

```bash
# SSH 접속
ssh root@139.150.11.99

# 프로젝트 디렉토리로 이동
cd /root/uvis

# 현재 커밋 확인
git log --oneline -5

# 로컬 변경사항 임시 저장
git stash

# 최신 코드 받기
git pull origin main

# 업데이트 확인
git log --oneline -5

# 최신 커밋이 다음 중 하나여야 함:
# - be3adc4: fix(integration-test): Add health check endpoint, GPS method
# - b327f1c: docs(phase11-b): Add Phase 11-B complete documentation
# - acc4528: feat(phase11-b): Complete Traffic Information Integration
```

---

### Step 2: Backend 재빌드 및 재가동

```bash
# 현재 실행 중인 백엔드 중지
docker-compose stop backend

# 컨테이너 삭제
docker-compose rm -f backend

# 이미지 재빌드 (캐시 없이)
docker-compose build --no-cache backend

# 백엔드 재가동
docker-compose up -d backend

# 30초 대기
sleep 30

# 로그 확인
docker logs uvis-backend --tail 50

# 정상 기동 확인
# "Application startup complete!" 메시지가 나와야 함
```

---

### Step 3: Database 테이블 생성

```bash
# 백엔드 컨테이너 접속
docker exec -it uvis-backend bash

# Python 스크립트 실행
python3 create_all_tables.py

# 출력 예시:
# ✅ Phase 10 models imported
# ✅ Phase 11-C models imported
# ✅ Phase 11-B models imported
# ✅ Phase 12 models imported
# ✅ Phase 13-14 models imported
# ✅ Phase 15 models imported
# ✅ Phase 16 models imported
# 🚀 Creating all Phase tables...
# ✅ 모든 Phase 테이블 생성 완료!
# 📊 총 XX개의 테이블이 생성되었습니다

# 컨테이너 종료
exit
```

---

### Step 4: API 정상성 확인

```bash
# Health Check
curl http://localhost:8000/api/v1/health
# 예상 응답: {"status":"healthy","timestamp":"...","service":"Cold Chain Dispatch System","version":"1.0.0"}

# Phase 10: Dispatch Rules
curl http://localhost:8000/api/v1/dispatch-rules
# 예상 응답: 401 (Not authenticated) 또는 데이터

# Phase 11-B: Traffic Info
curl http://localhost:8000/api/v1/traffic/current
# 예상 응답: 401 또는 데이터

# Phase 12: Integrated Dispatch
curl http://localhost:8000/api/v1/integrated-dispatch/vehicles/tracking
# 예상 응답: 401 또는 데이터

# Phase 13-14: IoT Sensors
curl http://localhost:8000/api/v1/iot/sensors
# 예상 응답: 401 또는 데이터

# Phase 15: ML Auto-Learning
curl http://localhost:8000/api/v1/ml-autolearning/experiments
# 예상 응답: 401 또는 데이터

# Phase 16: Driver App
curl http://localhost:8000/api/v1/driver/notifications
# 예상 응답: 401 또는 데이터

# Core APIs
curl http://localhost:8000/api/v1/orders
# 예상 응답: 401 또는 데이터 (500 에러가 나오면 안 됨)
```

---

### Step 5: Frontend 배포 (필요시)

```bash
# Frontend 디렉토리로 이동
cd /root/uvis/frontend

# 빌드 패키지 확인
ls -lh ../*.tar.gz

# 가장 최신 패키지 찾기
# frontend-dist-phase16.tar.gz 또는 frontend-dist-phase11-b.tar.gz

# 압축 해제
tar -xzf ../frontend-dist-phase16.tar.gz

# Nginx 컨테이너에 복사
docker cp dist/. uvis-frontend:/usr/share/nginx/html/

# Frontend 및 Nginx 재시작
docker-compose restart frontend nginx

# 확인
curl -I http://localhost/
# 예상 응답: HTTP/1.1 200 OK
```

---

### Step 6: 브라우저 테스트

1. **캐시 완전 삭제**
   - Chrome/Edge: `Ctrl + Shift + Delete`
   - 시간 범위: "전체 기간"
   - 삭제 항목: "쿠키 및 기타 사이트 데이터", "캐시된 이미지 및 파일"
   - "데이터 삭제" 클릭
   - 브라우저 완전 종료 후 재시작

2. **로그인**
   - URL: http://139.150.11.99
   - 관리자 계정으로 로그인

3. **사이드바 메뉴 확인**
   - [ ] 배차 규칙 (Phase 10)
   - [ ] 규칙 시뮬레이션 (Phase 11-C)
   - [ ] 교통 정보 대시보드 (Phase 11-B)
   - [ ] 실시간 차량 추적 (Phase 12)
   - [ ] AI 자동 배차 (Phase 12)
   - [ ] IoT 센서 모니터링 (Phase 13-14)
   - [ ] 예측 유지보수 (Phase 13-14)
   - [ ] AI 자동 학습 (Phase 15) ⭐ NEW
   - [ ] 드라이버 대시보드 (Phase 16) ⭐ NEW
   - [ ] 드라이버 알림 (Phase 16) ⭐ NEW

4. **각 페이지 테스트**
   - 각 메뉴 클릭하여 페이지 로드 확인
   - 개발자 도구 (F12) → Network 탭에서 API 호출 확인
   - Console 탭에서 에러 없는지 확인

---

## 🔧 트러블슈팅

### 문제 1: Backend 500 에러

**증상**: Core APIs (orders, dispatches, vehicles, clients)에서 500 에러

**원인**: Database relationship 에러

**해결**:
```bash
# 백엔드 로그 확인
docker logs uvis-backend --tail 100

# "Driver.notifications" 관련 에러가 있으면:
# 1. 테이블 재생성
docker exec -it uvis-backend python3 create_all_tables.py

# 2. 백엔드 재시작
docker-compose restart backend
```

---

### 문제 2: Frontend 페이지 로드 안 됨

**증상**: 새로운 Phase 메뉴가 안 보임

**원인**: 브라우저 캐시

**해결**:
1. 시크릿/프라이빗 창으로 테스트
2. 캐시 완전 삭제 (전체 기간)
3. 브라우저 완전 종료 후 재시작
4. Frontend 재배포:
```bash
cd /root/uvis/frontend
docker cp dist/. uvis-frontend:/usr/share/nginx/html/
docker-compose restart frontend nginx
```

---

### 문제 3: API 404 에러

**증상**: Phase 10~15 API가 404 응답

**원인**: 서버 코드가 최신이 아님

**해결**:
```bash
cd /root/uvis
git log --oneline -1
# 최신 커밋 확인: be3adc4 또는 이후

# 최신이 아니면:
git stash
git pull origin main
docker-compose stop backend
docker-compose rm -f backend
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

### 문제 4: 테이블 생성 실패

**증상**: create_all_tables.py 실행 시 import 에러

**원인**: 모델 파일 누락

**해결**:
```bash
# 백엔드 컨테이너에서 파일 확인
docker exec -it uvis-backend ls -la /app/app/models/

# 다음 파일이 있어야 함:
# - dispatch_rules.py (Phase 10)
# - simulations.py (Phase 11-C)
# - traffic.py (Phase 11-B)
# - integrated_dispatch.py (Phase 12)
# - iot_maintenance.py (Phase 13-14)
# - ml_autolearning.py (Phase 15)
# - driver_app.py (Phase 16)

# 파일이 없으면 git pull 후 재빌드
cd /root/uvis
git pull origin main
docker-compose build --no-cache backend
docker-compose up -d backend
```

---

## 📊 배포 체크리스트

### Backend
- [ ] Git pull 완료 (최신 커밋: be3adc4 이상)
- [ ] Backend 재빌드 완료
- [ ] Backend 정상 기동 ("Application startup complete!")
- [ ] Health check 정상 (200 OK)
- [ ] 모든 Phase 테이블 생성 완료
- [ ] Phase 10~16 API 정상 응답 (401 또는 데이터)
- [ ] Core APIs 정상 작동 (500 에러 없음)

### Frontend
- [ ] Frontend 빌드 패키지 배포 완료
- [ ] Nginx 재시작 완료
- [ ] 브라우저 캐시 삭제 완료
- [ ] 로그인 정상 작동
- [ ] 사이드바에 모든 Phase 메뉴 표시
- [ ] 각 페이지 정상 로드

### Database
- [ ] Phase 10 테이블 (dispatch_rules, rule_conditions, rule_actions, rule_executions)
- [ ] Phase 11-C 테이블 (simulations, simulation_results)
- [ ] Phase 11-B 테이블 (traffic_conditions, route_optimizations, traffic_alerts, route_history, traffic_rules)
- [ ] Phase 12 테이블 (vehicle_gps_locations, auto_dispatch_logs, naver_map_cache)
- [ ] Phase 13-14 테이블 (iot_sensors, sensor_readings, maintenance_schedules, maintenance_histories, predictive_alerts)
- [ ] Phase 15 테이블 (dispatch_training_data, ml_experiments, model_versions, dispatch_features, rl_reward_history)
- [ ] Phase 16 테이블 (driver_notifications, push_tokens, delivery_proofs, chat_rooms, chat_messages, driver_performance, navigation_sessions, driver_locations)

---

## 🎯 배포 후 검증

### 1. Health Check
```bash
curl http://139.150.11.99:8000/api/v1/health
```

예상 응답:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T...",
  "service": "Cold Chain Dispatch System",
  "version": "1.0.0"
}
```

### 2. API 응답 확인
모든 Phase API가 다음 중 하나여야 함:
- ✅ `401 Unauthorized` (인증 필요)
- ✅ `200 OK` + 데이터
- ❌ `404 Not Found` (엔드포인트 미존재) - 재배포 필요
- ❌ `500 Internal Server Error` (서버 에러) - 로그 확인 필요

### 3. 브라우저 테스트
모든 페이지가 정상 로드되어야 함:
- UI 렌더링 정상
- API 호출 정상
- Console 에러 없음

---

## 🎉 배포 완료 후

### 다음 단계 옵션

1. **성능 최적화**
   - Database 인덱스 최적화
   - API 응답 속도 개선
   - Frontend 렌더링 최적화

2. **보안 강화**
   - API Rate Limiting
   - SQL Injection 방지
   - XSS 방지

3. **모니터링 & 로깅**
   - Prometheus + Grafana
   - ELK Stack
   - Sentry

4. **CI/CD 파이프라인**
   - GitHub Actions
   - 자동 테스트
   - 자동 배포

5. **문서화**
   - API 문서 (Swagger/ReDoc)
   - 사용자 매뉴얼
   - 개발자 가이드

---

## 📞 지원

배포 중 문제가 발생하면:
1. `docker logs uvis-backend --tail 100`로 로그 확인
2. 통합 테스트 리포트 참조: `/home/user/webapp/docs/INTEGRATION_TEST_REPORT.md`
3. GitHub 이슈 생성

---

**작성일**: 2026-02-11  
**최종 업데이트**: Phase 16 완료 후  
**최신 커밋**: be3adc4
