# 🚀 프로덕션 서버 원격 배포 명령어

## 📋 사전 확인사항

- [x] PR #3 병합 완료 ✅
- [x] main 브랜치 최신 상태 ✅
- [x] 배포 스크립트 준비 완료 ✅
- [ ] **→ 프로덕션 서버 배포** ← **지금 여기**

---

## 🎯 빠른 실행 (복사-붙여넣기)

### 방법 1: 로컬에서 원격 실행 (권장)

```bash
# 1. 스크립트를 서버로 복사하고 실행
scp EXECUTE_ON_SERVER.sh root@139.150.11.99:/root/uvis/
ssh root@139.150.11.99 'cd /root/uvis && bash EXECUTE_ON_SERVER.sh'
```

### 방법 2: 서버에 직접 접속

```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 프로젝트 디렉토리로 이동
cd /root/uvis

# 3. 최신 코드 가져오기
git pull origin main

# 4. 배포 스크립트 실행
./scripts/deploy_production.sh
```

---

## 📝 단계별 상세 실행

### Step 1: 서버 접속 및 코드 업데이트

```bash
ssh root@139.150.11.99
cd /root/uvis
git pull origin main
```

**예상 출력:**
```
From https://github.com/rpaakdi1-spec/3-
 * branch            main       -> FETCH_HEAD
Updating 02fe029..d63310d
Fast-forward
 86 files changed, 22842 insertions(+), 624 deletions(-)
```

---

### Step 2: 환경 변수 확인

```bash
# OpenAI API 키 확인
grep OPENAI_API_KEY backend/.env
```

**필수 설정:**
- `OPENAI_API_KEY=sk-...` (유효한 OpenAI API 키)
- `REDIS_HOST=redis`
- `REDIS_PORT=6379`

**만약 설정되지 않았다면:**
```bash
# .env 파일 편집
nano backend/.env

# 또는 직접 추가
echo "OPENAI_API_KEY=sk-your-actual-key-here" >> backend/.env
```

---

### Step 3: Redis 확인 및 시작

```bash
# Redis 상태 확인
docker ps | grep redis

# Redis가 없다면 시작
docker-compose -f docker-compose.prod.yml up -d redis

# Redis 연결 테스트
docker exec -it uvis-redis redis-cli ping
```

**예상 출력:** `PONG`

---

### Step 4: Backend 재빌드 (약 3분)

```bash
# Backend 재빌드 및 재시작
docker-compose -f docker-compose.prod.yml up -d --build --no-deps backend

# 로그 확인
docker logs uvis-backend --tail 50 -f
```

**성공 확인:**
- `Application startup complete` 메시지 확인
- `http://0.0.0.0:8000` 서버 시작 확인

**Ctrl+C로 로그 중단 후 다음 단계 진행**

---

### Step 5: Frontend 재빌드 (약 2분)

```bash
# Frontend 재빌드 및 재시작
docker-compose -f docker-compose.prod.yml up -d --build --no-deps frontend

# 상태 확인
docker ps | grep uvis
```

**예상 출력:**
```
uvis-frontend   Up 30 seconds   0.0.0.0:80->80/tcp
uvis-backend    Up 2 minutes    0.0.0.0:8000->8000/tcp
uvis-redis      Up 5 minutes    6379/tcp
```

---

### Step 6: 헬스 체크

```bash
# 1. 컨테이너 상태
docker ps | grep uvis

# 2. Backend API 체크
curl http://localhost:8000/health

# 3. Redis 연결 체크
docker exec -it uvis-redis redis-cli ping

# 4. ML Dispatch API 체크
curl http://localhost:8000/api/ml-dispatch/ab-test/stats

# 5. API 문서 확인
curl -I http://localhost:8000/docs
```

---

## 🧪 파일럿 롤아웃 (10%)

배포가 완료되면 파일럿 롤아웃을 시작합니다:

```bash
# 1. 파일럿 롤아웃 시작 (10%)
./scripts/gradual_rollout.sh pilot

# 2. 자동 모니터링 시작 (1시간, 백그라운드)
mkdir -p logs
nohup ./scripts/monitor_pilot.sh > logs/monitor_output.log 2>&1 &

# 3. 실시간 로그 확인
tail -f logs/monitor_output.log
```

---

## 📊 모니터링

### 실시간 메트릭 확인

```bash
# A/B 테스트 통계
curl http://localhost:8000/api/ml-dispatch/ab-test/stats | jq

# 실시간 메트릭
curl http://localhost:8000/api/ml-dispatch/ab-test/metrics | jq

# Backend 로그 모니터링
docker logs uvis-backend --tail 50 -f | grep -i "ml\|rollback\|error"
```

### 프론트엔드에서 확인

1. **브라우저 접속**: http://139.150.11.99
2. **A/B Test Monitor 페이지** 이동
3. **실시간 대시보드** 확인:
   - ML 성공률
   - 평균 ML 점수
   - 에러율
   - 응답 시간

---

## ✅ 성공 기준 (1시간 후)

| 지표 | 목표 | 확인 방법 |
|------|------|-----------|
| **ML 성공률** | ≥ 90% | A/B 테스트 통계 |
| **평균 ML 점수** | ≥ 0.70 | 메트릭 API |
| **에러율** | < 5% | 로그 확인 |
| **응답 시간** | < 2초 | 성능 모니터링 |
| **자동 롤백** | 미발생 | 시스템 로그 |

### 성공 시 다음 단계

```bash
# 30%로 확대
./scripts/gradual_rollout.sh expand
```

---

## 🚨 긴급 롤백

문제 발생 시 즉시 롤백:

```bash
# 방법 1: 스크립트 사용
./scripts/gradual_rollout.sh rollback

# 방법 2: API 직접 호출
curl -X POST 'http://localhost:8000/api/ml-dispatch/ab-test/rollout?percentage=0' \
  -H 'Content-Type: application/json'

# 방법 3: 프론트엔드에서 롤백
# A/B Test Monitor → Rollout Control → 0% 적용
```

---

## 🔍 트러블슈팅

### Backend 시작 실패

```bash
# 로그 확인
docker logs uvis-backend --tail 100

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 완전 재빌드
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate backend
```

### Redis 연결 실패

```bash
# Redis 재시작
docker-compose -f docker-compose.prod.yml restart redis

# Redis 로그 확인
docker logs uvis-redis --tail 50
```

### ML API 응답 없음

```bash
# OpenAI API 키 확인
grep OPENAI_API_KEY backend/.env

# Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 로그에서 에러 확인
docker logs uvis-backend | grep -i "openai\|error"
```

---

## 📚 관련 문서

- `FINAL_DEPLOYMENT_STEPS.md` - 최종 배포 가이드
- `DEPLOYMENT_EXECUTION_GUIDE.md` - 상세 실행 가이드
- `PHASE3_DEPLOYMENT_GUIDE.md` - Phase 3 기술 문서
- `ML_DEPLOYMENT_GUIDE.md` - ML 시스템 배포 가이드
- `ML_QUICK_START.md` - ML 시스템 빠른 시작

---

## 🎯 타임라인

| 단계 | 예상 시간 | 누적 시간 |
|------|-----------|-----------|
| Git Pull | 30초 | 30초 |
| 환경 변수 확인 | 1분 | 1분 30초 |
| Redis 확인/시작 | 30초 | 2분 |
| Backend 재빌드 | 3분 | 5분 |
| Frontend 재빌드 | 2분 | 7분 |
| 헬스 체크 | 1분 | 8분 |
| **총 배포 시간** | **약 8분** | - |
| 파일럿 롤아웃 | 2분 | 10분 |
| 모니터링 설정 | 2분 | 12분 |
| **전체 시간** | **약 12분** | - |

---

## 🎉 배포 완료 후

1. ✅ 브라우저에서 http://139.150.11.99 접속 확인
2. ✅ API 문서 확인: http://139.150.11.99:8000/docs
3. ✅ A/B Test Monitor 페이지에서 실시간 메트릭 확인
4. ✅ 1시간 모니터링 후 성공 검증
5. ✅ 성공 시 30% 확대

---

**축하합니다!** 🚀 Phase 1-3 ML 배차 시스템이 프로덕션에 성공적으로 배포됩니다!
