# 🚀 프로덕션 배포 시작 - 지금 바로 실행하세요!

**작성일**: 2026-02-02  
**상태**: ✅ 배포 준비 완료  
**예상 시간**: 12분 (모니터링 제외)

---

## ⚡ 빠른 시작 (3가지 방법)

### 🎯 방법 1: 한 줄 자동 배포 (가장 빠름!)

서버에 접속하여 다음 명령어를 **복사-붙여넣기**하세요:

```bash
ssh root@139.150.11.99
```

접속 후:

```bash
cd /root/uvis && git pull origin main && ./scripts/deploy_production.sh && ./scripts/gradual_rollout.sh pilot && nohup ./scripts/monitor_pilot.sh > logs/monitor_output.log 2>&1 & && echo "배포 시작 완료! 로그 확인: tail -f logs/monitor_output.log"
```

**이 한 줄이 모든 것을 처리합니다!**

---

### 📝 방법 2: 단계별 실행 (권장 - 각 단계 확인)

#### Step 1: 서버 접속
```bash
ssh root@139.150.11.99
```

#### Step 2: 프로젝트 디렉토리로 이동
```bash
cd /root/uvis
```

#### Step 3: 현재 상태 확인
```bash
# 현재 브랜치 확인
git branch

# 현재 커밋 확인
git log --oneline -1

# 컨테이너 상태 확인
docker ps | grep uvis
```

#### Step 4: 최신 코드 가져오기
```bash
git pull origin main
```

**예상 출력:**
```
From https://github.com/rpaakdi1-spec/3-
 * branch            main       -> FETCH_HEAD
Updating d63310d..0573357
Fast-forward
 3 files changed, 753 insertions(+)
```

#### Step 5: 환경 변수 확인
```bash
# OpenAI API 키 확인 (중요!)
grep OPENAI_API_KEY backend/.env
```

**출력이 다음과 같아야 합니다:**
```
OPENAI_API_KEY=sk-proj-...
```

⚠️ **만약 설정되지 않았다면:**
```bash
nano backend/.env
# OPENAI_API_KEY=sk-your-actual-key-here 추가
```

#### Step 6: 배포 스크립트 실행
```bash
./scripts/deploy_production.sh
```

**이 스크립트가 자동으로:**
- ✅ Redis 확인 및 시작
- ✅ Backend 재빌드 (약 3분)
- ✅ Frontend 재빌드 (약 2분)
- ✅ 헬스 체크
- ✅ 배포 완료 요약

**배포 중 로그 확인:**
다른 터미널을 열어서:
```bash
ssh root@139.150.11.99
docker logs uvis-backend --tail 50 -f
```

#### Step 7: 배포 완료 확인
```bash
# 컨테이너 상태
docker ps | grep uvis

# Backend API 확인
curl http://localhost:8000/health

# Redis 확인
docker exec -it uvis-redis redis-cli ping
```

**성공 확인:**
- ✅ 3개 컨테이너 실행 중 (backend, frontend, redis)
- ✅ Backend health: `{"status":"healthy"}`
- ✅ Redis: `PONG`

#### Step 8: 파일럿 롤아웃 시작 (10%)
```bash
./scripts/gradual_rollout.sh pilot
```

**예상 출력:**
```
[INFO] Phase: Pilot (10%)
[INFO] Setting rollout percentage to 10%
[SUCCESS] ✓ Rollout updated to 10%
[SUCCESS] ✓ Pilot rollout complete
```

#### Step 9: 자동 모니터링 시작 (1시간)
```bash
# logs 디렉토리 생성
mkdir -p logs

# 백그라운드로 모니터링 시작
nohup ./scripts/monitor_pilot.sh > logs/monitor_output.log 2>&1 &

# 프로세스 확인
ps aux | grep monitor_pilot
```

#### Step 10: 실시간 로그 확인
```bash
tail -f logs/monitor_output.log
```

**예상 출력:**
```
════════════════════════════════════════════════════════════════
  🔍 ML Dispatch System - 파일럿 모니터링 (1시간)
════════════════════════════════════════════════════════════════

[INFO] 모니터링 시작: 2026-02-02 10:00:00
[INFO] 체크 간격: 10분
[INFO] 총 체크 횟수: 6회

────────────────────────────────────────────────────────────────
[CHECK 1/6] 10:00:00
────────────────────────────────────────────────────────────────
[INFO] 메트릭 수집 중...
[SUCCESS] ✓ ML 성공률: 92.5%
[SUCCESS] ✓ 평균 ML 점수: 0.75
[SUCCESS] ✓ 에러율: 1.2%
[SUCCESS] ✓ 응답 시간: 1.5s
[SUCCESS] ✓ 체크 1 통과
```

**Ctrl+C로 로그 모니터링 중단 (모니터링은 계속 실행)**

---

### 🔧 방법 3: 수동 단계별 실행 (문제 해결용)

문제가 발생하면 이 방법으로 각 단계를 수동으로 실행:

```bash
# 1. 서버 접속
ssh root@139.150.11.99
cd /root/uvis

# 2. 코드 업데이트
git fetch origin main
git pull origin main

# 3. Redis 확인 및 시작
docker ps | grep redis
# Redis가 없으면:
docker-compose -f docker-compose.prod.yml up -d redis
sleep 3
docker exec -it uvis-redis redis-cli ping

# 4. Backend 재빌드
docker-compose -f docker-compose.prod.yml up -d --build --no-deps backend
# 시작 대기 (약 30초)
sleep 30
# 확인
curl http://localhost:8000/health

# 5. Frontend 재빌드
docker-compose -f docker-compose.prod.yml up -d --build --no-deps frontend
# 시작 대기 (약 20초)
sleep 20
# 확인
docker ps | grep uvis-frontend

# 6. 전체 상태 확인
docker ps | grep uvis
curl http://localhost:8000/api/ml-dispatch/ab-test/stats

# 7. 파일럿 롤아웃
curl -X POST 'http://localhost:8000/api/ml-dispatch/ab-test/rollout?percentage=10' \
  -H 'Content-Type: application/json'

# 8. 메트릭 확인
curl http://localhost:8000/api/ml-dispatch/ab-test/stats | jq
```

---

## ⏱️ 타임라인

```
00:00 - 서버 접속
00:30 - Git Pull 완료
01:00 - 환경 확인 완료
01:30 - Redis 시작 완료
02:00 - Backend 빌드 시작
05:00 - Backend 빌드 완료, Frontend 빌드 시작
07:00 - Frontend 빌드 완료
08:00 - 헬스 체크 완료
10:00 - 파일럿 롤아웃 완료 (10%)
12:00 - 모니터링 시작
─────────────────────────────────────
01:12:00 - 1시간 모니터링 완료, 결과 확인
```

---

## ✅ 성공 확인 체크리스트

배포 후 다음 항목들을 확인하세요:

### 컨테이너 상태
```bash
docker ps | grep uvis
```

**예상 출력:**
```
uvis-frontend   Up 2 minutes   0.0.0.0:80->80/tcp
uvis-backend    Up 5 minutes   0.0.0.0:8000->8000/tcp
uvis-redis      Up 8 minutes   6379/tcp
```

### API 엔드포인트
```bash
# Health Check
curl http://localhost:8000/health
# 예상: {"status":"healthy"}

# ML Dispatch API
curl http://localhost:8000/api/ml-dispatch/ab-test/stats
# 예상: {"rollout_percentage":10,"control_users":90,"treatment_users":10,...}

# API 문서
curl -I http://localhost:8000/docs
# 예상: HTTP/1.1 200 OK
```

### 프론트엔드 접속
```bash
# 로컬에서 브라우저 열기
curl -I http://139.150.11.99
# 예상: HTTP/1.1 200 OK
```

**브라우저에서 확인:**
1. http://139.150.11.99 접속
2. 로그인
3. "A/B Test Monitor" 메뉴 클릭
4. 실시간 대시보드 확인

---

## 📊 모니터링 대시보드

### 터미널에서 실시간 확인

```bash
# 1. A/B 테스트 통계
watch -n 10 'curl -s http://localhost:8000/api/ml-dispatch/ab-test/stats | jq'

# 2. 실시간 메트릭
watch -n 10 'curl -s http://localhost:8000/api/ml-dispatch/ab-test/metrics | jq'

# 3. Backend 로그
docker logs uvis-backend --tail 50 -f | grep -i "ml\|rollback\|error"
```

### 웹 브라우저에서 확인

1. **A/B Test Monitor 페이지**:
   - URL: http://139.150.11.99
   - 메뉴: A/B Test Monitor
   - 확인 항목:
     - 현재 롤아웃 비율: 10%
     - ML 성공률: 실시간 업데이트
     - 평균 ML 점수: 실시간 업데이트
     - 에러율: 실시간 업데이트
     - 응답 시간: 실시간 업데이트

2. **API 문서**:
   - URL: http://139.150.11.99:8000/docs
   - 확인: ML Dispatch API 엔드포인트

---

## ✅ 1시간 후 성공 기준

모니터링 스크립트가 자동으로 확인하는 항목:

| 지표 | 목표 | 통과 기준 |
|------|------|-----------|
| **ML 성공률** | ≥ 90% | 6회 중 5회 이상 |
| **평균 ML 점수** | ≥ 0.70 | 6회 중 5회 이상 |
| **에러율** | < 5% | 6회 모두 |
| **응답 시간** | < 2초 | 6회 모두 |
| **자동 롤백** | 미발생 | - |

### 최종 판정

1시간 후 `logs/monitor_output.log`에서 확인:

```bash
# 로그 마지막 부분 확인
tail -50 logs/monitor_output.log
```

**SUCCESS 출력 예시:**
```
════════════════════════════════════════════════════════════════
  🎉 최종 판정: SUCCESS
════════════════════════════════════════════════════════════════

✓ 모든 성공 기준 충족
✓ 6/6 체크 통과
✓ 연속 실패 없음

다음 단계:
  1. 30% 롤아웃 실행:
     ./scripts/gradual_rollout.sh expand

  2. 추가 1시간 모니터링
```

### 성공 시 다음 단계

```bash
# 30%로 확대
./scripts/gradual_rollout.sh expand

# 다시 1시간 모니터링
nohup ./scripts/monitor_pilot.sh > logs/monitor_30pct.log 2>&1 &
tail -f logs/monitor_30pct.log
```

---

## 🚨 문제 해결

### Backend 시작 실패

```bash
# 로그 확인
docker logs uvis-backend --tail 100

# 일반적인 문제:
# 1. OpenAI API 키 미설정
grep OPENAI_API_KEY backend/.env

# 2. Redis 연결 실패
docker exec -it uvis-redis redis-cli ping

# 3. 포트 충돌
netstat -tlnp | grep 8000

# 해결: 완전 재빌드
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### Redis 연결 실패

```bash
# Redis 상태 확인
docker ps | grep redis

# Redis 재시작
docker-compose -f docker-compose.prod.yml restart redis

# Redis 로그
docker logs uvis-redis --tail 50

# 해결: Redis 재생성
docker-compose -f docker-compose.prod.yml stop redis
docker-compose -f docker-compose.prod.yml rm -f redis
docker-compose -f docker-compose.prod.yml up -d redis
```

### ML API 응답 없음

```bash
# 1. OpenAI API 키 확인
grep OPENAI_API_KEY backend/.env

# 2. Backend 로그 확인
docker logs uvis-backend | grep -i "openai\|error"

# 3. Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 4. API 직접 테스트
curl -X POST http://localhost:8000/api/ml-dispatch/simulate \
  -H 'Content-Type: application/json' \
  -d '{"target_date":"2026-02-02"}'
```

### 긴급 롤백

```bash
# 방법 1: 스크립트
./scripts/gradual_rollout.sh rollback

# 방법 2: API
curl -X POST 'http://localhost:8000/api/ml-dispatch/ab-test/rollout?percentage=0'

# 방법 3: 전체 재시작
docker-compose -f docker-compose.prod.yml restart

# 확인
curl http://localhost:8000/api/ml-dispatch/ab-test/stats | jq '.rollout_percentage'
# 예상: 0
```

---

## 📞 지원

### 로그 파일 위치

```bash
# Backend 로그
docker logs uvis-backend > backend_logs.txt

# Frontend 로그
docker logs uvis-frontend > frontend_logs.txt

# Redis 로그
docker logs uvis-redis > redis_logs.txt

# 모니터링 로그
cat logs/monitor_output.log > monitoring_logs.txt
```

### 상태 스냅샷 생성

```bash
# 현재 상태 저장
cat > deployment_status.txt << EOF
=== Deployment Status ===
Date: $(date)
Commit: $(git rev-parse HEAD)

=== Containers ===
$(docker ps | grep uvis)

=== API Health ===
$(curl -s http://localhost:8000/health)

=== A/B Test Stats ===
$(curl -s http://localhost:8000/api/ml-dispatch/ab-test/stats | jq)

=== Recent Backend Logs ===
$(docker logs uvis-backend --tail 50)
EOF

cat deployment_status.txt
```

---

## 📚 관련 문서

1. **PRODUCTION_READY.md** - 배포 준비 완료 체크리스트
2. **REMOTE_DEPLOY_COMMANDS.md** - 명령어 모음
3. **EXECUTE_ON_SERVER.sh** - 자동 배포 스크립트
4. **FINAL_DEPLOYMENT_STEPS.md** - 최종 배포 단계
5. **PHASE3_DEPLOYMENT_GUIDE.md** - Phase 3 기술 문서

---

## 🎯 다음 단계 (성공 후)

### Week 1: 파일럿 (10%)
- [x] 배포 완료
- [ ] 1시간 모니터링
- [ ] 성공 검증
- [ ] 다음 단계 진행

### Week 2: 확대 (30%)
- [ ] 30% 롤아웃
- [ ] 1시간 모니터링
- [ ] 성공 검증
- [ ] 다음 단계 진행

### Week 3: 절반 (50%)
- [ ] 50% 롤아웃
- [ ] 1시간 모니터링
- [ ] 성공 검증
- [ ] 다음 단계 진행

### Week 4: 전면 (100%)
- [ ] 100% 롤아웃
- [ ] 24시간 모니터링
- [ ] 프로덕션 안정화
- [ ] 프로젝트 완료 🎉

---

**🚀 지금 바로 시작하세요!**

```bash
ssh root@139.150.11.99
cd /root/uvis && git pull origin main && ./scripts/deploy_production.sh
```

**축하합니다! Phase 1-3 ML 배차 시스템을 프로덕션에 배포합니다!** 🎉
