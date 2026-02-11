# 서버 배포 가이드

**대상**: 운영 서버 (139.150.11.99)  
**날짜**: 2026-02-11  
**목적**: Order 모델 수정 및 최종 통합 테스트 결과 반영

---

## 🎯 배포 개요

### 변경 사항
1. **Order 모델**: `delivery_proofs` relationship 추가
2. **최종 통합 테스트 리포트**: 전체 시스템 상태 문서화

### 예상 효과
- ✅ SQLAlchemy mapper 초기화 에러 완전 해결
- ✅ Core APIs 500 에러 완전 제거
- ✅ WebSocket 브로드캐스트 안정화

---

## 📋 배포 전 체크리스트

- [ ] 운영 서버 접속 확인 (139.150.11.99)
- [ ] 백업 생성 완료
- [ ] Docker 컨테이너 상태 확인
- [ ] 배포 시간대 확인 (서비스 중단 최소화)

---

## 🚀 배포 절차

### Step 1: 서버 접속 및 백업

```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 프로젝트 디렉토리 이동
cd /root/uvis

# 3. 현재 상태 백업
cp backend/app/models/order.py backend/app/models/order.py.backup_$(date +%Y%m%d_%H%M%S)

# 4. 데이터베이스 백업 (선택사항, 권장)
docker exec uvis-db pg_dump -U postgres uvis > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

### Step 2: 최신 코드 가져오기

```bash
# 1. Git stash (혹시 로컬 변경사항이 있다면)
git stash

# 2. 최신 코드 pull
git pull origin main

# 3. 변경 사항 확인
git log --oneline -5

# 예상 출력:
# f412836 fix(models): Add delivery_proofs relationship to Order model
# cdc3442 docs(integration): Add integration test completion report
# ...
```

---

### Step 3: Backend 재배포

```bash
# 1. Backend 컨테이너 중지
docker-compose stop backend

# 2. Backend 컨테이너 삭제
docker-compose rm -f backend

# 3. Backend 이미지 재빌드 (캐시 없이)
docker-compose build --no-cache backend

# 4. Backend 컨테이너 재시작
docker-compose up -d backend

# 5. 30초 대기 (시작 시간 확보)
sleep 30
```

---

### Step 4: 배포 검증

#### 4.1 컨테이너 상태 확인

```bash
# 모든 컨테이너 상태 확인
docker ps -a

# 예상 출력: 모든 컨테이너가 Up/Healthy 상태
# uvis-backend    Up (healthy)
# uvis-frontend   Up
# uvis-nginx      Up (healthy)
# uvis-db         Up (healthy)
# uvis-redis      Up (healthy)
```

#### 4.2 Backend 로그 확인

```bash
# 최신 로그 50줄 확인
docker logs uvis-backend --tail 50

# 성공 메시지 확인:
# - "Application startup complete!"
# - mapper 초기화 에러 없음
# - WebSocket 브로드캐스트 정상 작동
```

#### 4.3 Health Check 테스트

```bash
# Health endpoint 확인
curl http://localhost:8000/api/v1/health

# 예상 응답:
# {
#   "status": "healthy",
#   "timestamp": "2026-02-11T...",
#   "service": "Cold Chain Dispatch System",
#   "version": "1.0.0"
# }
```

#### 4.4 Core APIs 테스트

```bash
# Orders API
curl http://localhost:8000/api/v1/orders/ | jq

# Dispatches API
curl http://localhost:8000/api/v1/dispatches/ | jq

# Vehicles API
curl http://localhost:8000/api/v1/vehicles/ | jq

# Clients API
curl http://localhost:8000/api/v1/clients/ | jq

# 모든 API가 200 OK + JSON 데이터 응답해야 함
# 500 Internal Server Error가 없어야 함
```

#### 4.5 Phase 11-B Traffic APIs 테스트

```bash
# Traffic Conditions
curl http://localhost:8000/api/v1/traffic/conditions

# Traffic Alerts
curl http://localhost:8000/api/v1/traffic/alerts

# Route Optimization
curl -X POST http://localhost:8000/api/v1/routes/optimize \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": 1}'

# 예상 응답: 401 Unauthorized (인증 필요하지만 엔드포인트 존재)
# 404 Not Found가 없어야 함
```

#### 4.6 Phase 16 Driver APIs 테스트

```bash
# Driver Notifications
curl http://localhost:8000/api/v1/driver/notifications

# Driver Performance
curl http://localhost:8000/api/v1/driver/performance/statistics

# Driver Chat
curl http://localhost:8000/api/v1/driver/chat/rooms

# 예상 응답: 401 Unauthorized (인증 필요하지만 엔드포인트 존재)
# 404 Not Found가 없어야 함
```

---

### Step 5: 통합 테스트 실행

```bash
# 1. 테스트 디렉토리 이동
cd /root/uvis

# 2. 통합 테스트 실행 (sandbox에서 작성한 스크립트 있다면)
# python3 test_integration.py

# 3. 결과 확인
# 예상: 12개 통과 (50%), 12개 실패 (배포 대기 Phase)
```

---

### Step 6: Frontend 브라우저 테스트

```bash
# 1. 브라우저 열기
# URL: http://139.150.11.99

# 2. 확인 사항
# - [ ] 로그인 페이지 로드
# - [ ] 대시보드 접근
# - [ ] Orders 페이지 로드
# - [ ] Vehicles 페이지 로드
# - [ ] Dispatches 페이지 로드
# - [ ] Phase 16 Driver Dashboard 로드

# 3. 개발자 도구 확인 (F12)
# - [ ] Console 에러 없음
# - [ ] Network 탭에서 API 응답 확인
# - [ ] 401 Unauthorized는 정상 (인증 필요)
# - [ ] 500 Internal Server Error 없음
```

---

## ✅ 배포 성공 기준

### 필수 조건
1. ✅ Backend 컨테이너 정상 기동 ("Application startup complete!")
2. ✅ Health Check 응답 200 OK
3. ✅ Core APIs 모두 200 OK + 데이터 반환
4. ✅ Backend 로그에 SQLAlchemy mapper 에러 없음

### 추가 확인
1. ✅ Phase 11-B APIs: 401 Unauthorized (404 아님)
2. ✅ Phase 16 APIs: 401 Unauthorized (404 아님)
3. ✅ WebSocket 브로드캐스트 에러 감소 (vehicle driver_id 경고만 남음)
4. ✅ Frontend 페이지 정상 로드

---

## 🔧 문제 발생 시 대응

### 1. Backend 시작 실패

```bash
# 로그 상세 확인
docker logs uvis-backend --tail 100

# 컨테이너 재시작
docker-compose restart backend

# 여전히 실패 시 재빌드
docker-compose stop backend
docker-compose rm -f backend
docker-compose build --no-cache backend
docker-compose up -d backend
```

### 2. Mapper 초기화 에러 지속

**증상**: "One or more mappers failed to initialize"

**해결**:
```bash
# 1. Order 모델 확인
cat backend/app/models/order.py | tail -10

# delivery_proofs relationship이 있는지 확인
# 없다면 수동 추가 필요

# 2. 백업에서 복원 후 다시 pull
git reset --hard HEAD
git pull origin main
```

### 3. Core APIs 여전히 500 에러

**원인**: 다른 모델의 relationship 문제

**확인**:
```bash
# Backend 로그에서 에러 메시지 확인
docker logs uvis-backend --tail 50 | grep -i "error"

# 특정 모델 관련 에러 찾기
docker logs uvis-backend --tail 100 | grep -i "mapper"
```

### 4. Frontend 접속 불가

```bash
# Frontend/Nginx 컨테이너 재시작
docker-compose restart frontend nginx

# 5초 대기
sleep 5

# 상태 확인
curl -I http://localhost/

# 200 OK 응답 확인
```

---

## 🔙 롤백 절차 (비상시)

```bash
# 1. 이전 버전으로 코드 되돌리기
git reset --hard cdc3442  # Order 모델 수정 이전 커밋

# 2. Backend 재빌드
docker-compose stop backend
docker-compose rm -f backend
docker-compose build --no-cache backend
docker-compose up -d backend

# 3. 검증
curl http://localhost:8000/api/v1/health
```

---

## 📊 배포 후 모니터링

### 1시간 후 확인사항

```bash
# 1. Backend 로그 확인 (에러 없는지)
docker logs uvis-backend --tail 100 --since 1h

# 2. 메모리 사용량 확인
docker stats --no-stream

# 3. API 응답 시간 확인
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/health

# curl-format.txt 내용:
# time_total: %{time_total}s\n
```

### 24시간 후 확인사항

```bash
# 1. 전체 로그 검토
docker logs uvis-backend --since 24h > backend_24h.log

# 2. 에러 통계
grep -i "error" backend_24h.log | wc -l

# 3. WebSocket 브로드캐스트 성공률
grep "broadcast" backend_24h.log | grep -v "Error" | wc -l
```

---

## 📞 지원 연락처

### 문제 발생 시 보고 사항
1. **에러 로그**: `docker logs uvis-backend --tail 100`
2. **컨테이너 상태**: `docker ps -a`
3. **API 응답 예시**: Core APIs 테스트 결과
4. **발생 시간**: 정확한 타임스탬프

### 로그 수집 명령

```bash
# 모든 컨테이너 로그 수집
docker logs uvis-backend > backend.log 2>&1
docker logs uvis-frontend > frontend.log 2>&1
docker logs uvis-nginx > nginx.log 2>&1
docker logs uvis-db > db.log 2>&1

# 압축하여 전달
tar -czf logs_$(date +%Y%m%d_%H%M%S).tar.gz *.log
```

---

## 🎯 배포 후 다음 단계

### 우선순위 1: 시스템 안정화
- [ ] 24시간 모니터링 완료
- [ ] WebSocket 브로드캐스트 안정성 확인
- [ ] 메모리/CPU 사용량 정상 범위 확인

### 우선순위 2: 인증 시스템 구축
- [ ] JWT 토큰 발급 로직 검증
- [ ] Driver 전용 로그인 기능 구현
- [ ] Frontend 로그인 페이지 연동

### 우선순위 3: 추가 Phase 배포 준비
- [ ] Phase 12: Integrated Dispatch
- [ ] Phase 13-14: IoT & Predictive Maintenance
- [ ] Phase 15: ML Auto-Learning

---

## ✅ 배포 완료 체크리스트

배포를 완료한 후 아래 항목을 체크해 주세요:

- [ ] Step 1: 백업 생성 완료
- [ ] Step 2: 최신 코드 pull 완료 (커밋 f412836 확인)
- [ ] Step 3: Backend 재배포 완료 (컨테이너 Up)
- [ ] Step 4.1: 모든 컨테이너 Healthy 상태
- [ ] Step 4.2: Backend 로그 정상 (Application startup complete)
- [ ] Step 4.3: Health Check 200 OK
- [ ] Step 4.4: Core APIs 모두 200 OK
- [ ] Step 4.5: Phase 11-B APIs 401 Unauthorized (404 아님)
- [ ] Step 4.6: Phase 16 APIs 401 Unauthorized (404 아님)
- [ ] Step 5: 통합 테스트 실행 완료 (12개 통과 확인)
- [ ] Step 6: Frontend 브라우저 정상 로드 확인

---

**배포 담당자**: _________________  
**배포 일시**: _________________  
**배포 결과**: ⬜ 성공 / ⬜ 실패 / ⬜ 부분 성공  
**특이사항**: _________________

---

**문서 작성**: AI Developer  
**최종 업데이트**: 2026-02-11 14:30 (KST)  
**버전**: 1.0.0
