# 🚀 최종 실행 가이드 - 프로덕션 배포

## ⚡ 빠른 시작 (3단계, 15분)

이 가이드는 **지금 바로 실행 가능**한 명령어만 포함합니다.

---

## 📋 Step 1: PR 병합 (2분)

### GitHub 웹에서 병합 (권장)

1. **브라우저에서 PR 열기:**
   ```
   https://github.com/rpaakdi1-spec/3-/pull/3
   ```

2. **"Squash and merge" 버튼 클릭**

3. **커밋 메시지 확인:**
   ```
   feat: Complete ML Dispatch System (Phase 1-3)
   
   - Phase 1: ML dispatch service implementation
   - Phase 2: Historical simulation & API endpoints
   - Phase 3: A/B testing & gradual rollout
   - Deployment automation scripts
   ```

4. **"Confirm squash and merge" 클릭**

5. **브랜치 삭제 선택** (genspark_ai_developer 브랜치)

✅ **완료!** main 브랜치에 코드가 반영되었습니다.

---

## 🖥️ Step 2: 프로덕션 배포 (5-10분)

### 서버 접속 및 배포 실행

**단일 명령어로 실행:**

```bash
ssh root@139.150.11.99 << 'ENDSSH'
cd /root/uvis
git pull origin main
./scripts/deploy_production.sh
ENDSSH
```

**또는 서버에 직접 접속:**

```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 프로젝트 디렉토리로 이동
cd /root/uvis

# 3. 최신 코드 받기
git pull origin main

# 4. 배포 스크립트 실행
./scripts/deploy_production.sh
```

### 예상 출력 (정상 배포 시)

```
========================================================================
  🚀 UVIS ML Dispatch System - Production Deployment
========================================================================

[INFO] Step 1: Pulling latest code from main branch...
[SUCCESS] Code updated successfully

[INFO] Step 2: Setting script permissions...
[SUCCESS] Permissions set

[INFO] Step 3: Checking Redis service...
[SUCCESS] Redis is already running
[INFO] Testing Redis connection...
[SUCCESS] Redis connection successful

[INFO] Step 4: Rebuilding backend service...
[INFO] Waiting for backend to start (30 seconds)...
[SUCCESS] Backend is running

[INFO] Step 5: Rebuilding frontend service...
[INFO] Waiting for frontend to start (20 seconds)...
[SUCCESS] Frontend is running

[INFO] Step 6: Health Check...
[SUCCESS] ML Dispatch API is working

========================================================================
[SUCCESS] 🎉 Deployment Complete!
========================================================================

[INFO] Services Status:
  ✅ Backend:  http://139.150.11.99:8000
  ✅ Frontend: http://139.150.11.99
  ✅ API Docs: http://139.150.11.99:8000/docs
  ✅ Redis:    Running

[INFO] Next Steps:
  1. Verify API: curl http://139.150.11.99:8000/api/ml-dispatch/ab-test/stats
  2. Pilot Rollout (10%): ./scripts/gradual_rollout.sh pilot
  3. Monitor: http://139.150.11.99 (A/B Test Monitor)
```

---

## ✅ Step 3: 배포 검증 (3분)

### 필수 확인 항목

```bash
# 아직 서버에 접속 중이어야 합니다
cd /root/uvis

# 1. 컨테이너 상태 확인
docker ps | grep uvis
# 예상: uvis-backend, uvis-frontend, uvis-redis, uvis-db 모두 Up 상태

# 2. 백엔드 로그 확인 (에러 없는지)
docker logs uvis-backend --tail 30 | grep -i error
# 예상: 출력 없음 (에러 없음)

# 3. ML Dispatch API 테스트
curl http://localhost:8000/api/ml-dispatch/ab-test/stats
# 예상: {"total_users":0,"control_count":0,"treatment_count":0,...}

# 4. Redis 연결 확인
docker exec uvis-redis redis-cli ping
# 예상: PONG
```

### 브라우저 확인

1. **API 문서:** http://139.150.11.99:8000/docs
   - "ML Dispatch" 섹션 확인
   - A/B Test 엔드포인트 6개 존재 확인

2. **프론트엔드:** http://139.150.11.99
   - 로그인 정상 작동 확인
   - 배차 최적화 페이지 접속 확인

✅ **모두 정상이면 다음 단계로!**

---

## 🧪 Step 4: 파일럿 롤아웃 10% (2분)

### 방법 A: 자동 스크립트 (권장)

```bash
# 아직 서버에 접속 중
cd /root/uvis

# 파일럿 롤아웃 실행
./scripts/gradual_rollout.sh pilot
```

### 방법 B: API 직접 호출

```bash
curl -X POST "http://localhost:8000/api/ml-dispatch/ab-test/rollout?percentage=10" \
  -H "Content-Type: application/json"
```

### 방법 C: 프론트엔드 UI

1. http://139.150.11.99 접속
2. **A/B Test Monitor** 페이지 이동
3. 슬라이더를 **10%**로 조정
4. **"적용"** 버튼 클릭

### 확인

```bash
curl http://localhost:8000/api/ml-dispatch/ab-test/stats
```

**예상 출력:**
```json
{
  "total_users": 0,
  "control_count": 0,
  "treatment_count": 0,
  "actual_treatment_percentage": 0.0,
  "target_rollout_percentage": 10
}
```

✅ `target_rollout_percentage: 10` 확인!

---

## 📊 Step 5: 자동 모니터링 시작 (1시간)

### 모니터링 스크립트 실행

```bash
# 아직 서버에 접속 중
cd /root/uvis

# 백그라운드에서 모니터링 실행
nohup ./scripts/monitor_pilot.sh > /root/uvis/logs/monitor_output.log 2>&1 &

# PID 확인
echo $!
```

### 모니터링 확인

```bash
# 실시간 로그 확인
tail -f /root/uvis/logs/monitor_output.log

# 또는 최근 로그만 확인
tail -50 /root/uvis/logs/monitor_output.log
```

### 수동 모니터링 (10분마다)

```bash
# A/B 테스트 통계
curl http://localhost:8000/api/ml-dispatch/ab-test/stats | jq '.'

# 성과 메트릭
curl http://localhost:8000/api/ml-dispatch/ab-test/metrics | jq '.'

# 백엔드 로그 (에러 체크)
docker logs uvis-backend --tail 20 | grep -i "error\|rollback"
```

### 프론트엔드 대시보드

브라우저: **http://139.150.11.99**
→ **A/B Test Monitor** 페이지에서 실시간 확인

---

## ✅ Step 6: 성공 기준 검증 (1시간 후)

### 자동 검증 (모니터링 스크립트 완료 시)

모니터링 스크립트가 1시간 후 자동으로 종료되며 최종 판정을 출력합니다:

**성공 시:**
```
========================================================================
  ✅ PILOT PHASE SUCCESSFUL - READY FOR 30% EXPANSION
========================================================================
All success criteria met during 1-hour monitoring
Next step: ./scripts/gradual_rollout.sh expand
```

**실패 시:**
```
========================================================================
  ❌ PILOT PHASE FAILED - ROLLBACK RECOMMENDED
========================================================================
Execute rollback: ./scripts/gradual_rollout.sh rollback
```

### 수동 검증

```bash
# 최종 메트릭 조회
curl http://localhost:8000/api/ml-dispatch/ab-test/metrics | jq '.'
```

**확인 항목:**
- ✅ `treatment.success_rate` ≥ 0.90 (90%)
- ✅ `treatment.avg_score` ≥ 0.70
- ✅ `treatment.avg_response_time` < 2.0초
- ✅ 에러율 < 5%

---

## 🎯 다음 단계

### 파일럿 성공 시 → 30% 확대

```bash
cd /root/uvis
./scripts/gradual_rollout.sh expand
```

**그 후:**
- 2시간 모니터링
- 성공 시 → 50% 확대
- 50% 성공 시 → 100% 전면 배포!

### 파일럿 실패 시 → 롤백

```bash
cd /root/uvis
./scripts/gradual_rollout.sh rollback
```

**그 후:**
- 로그 분석: `docker logs uvis-backend --tail 200 | grep -i error`
- 원인 파악 및 수정
- 재배포 및 재테스트

---

## 🔧 문제 해결

### 문제 1: 배포 스크립트 실행 권한 없음

```bash
chmod +x /root/uvis/scripts/*.sh
./scripts/deploy_production.sh
```

### 문제 2: Redis 연결 실패

```bash
docker-compose -f docker-compose.prod.yml up -d redis
docker restart uvis-backend
```

### 문제 3: ML Dispatch API 응답 없음

```bash
docker logs uvis-backend --tail 50
docker restart uvis-backend
```

### 문제 4: jq 명령어 없음 (선택적)

```bash
# Ubuntu/Debian
apt-get update && apt-get install -y jq

# CentOS/RHEL
yum install -y jq
```

### 긴급 롤백

```bash
./scripts/gradual_rollout.sh rollback
# 또는
curl -X POST "http://localhost:8000/api/ml-dispatch/ab-test/rollout?percentage=0"
```

---

## 📞 지원

### 로그 위치

- **배포 로그:** 배포 스크립트 실행 시 콘솔 출력
- **모니터링 로그:** `/root/uvis/logs/ml_monitoring_*.log`
- **백엔드 로그:** `docker logs uvis-backend`
- **프론트엔드 로그:** `docker logs uvis-frontend`

### 상태 확인 명령어

```bash
# 전체 상태 확인
docker ps | grep uvis
curl http://localhost:8000/api/ml-dispatch/ab-test/stats | jq '.'

# 상세 메트릭
curl http://localhost:8000/api/ml-dispatch/ab-test/metrics | jq '.'

# 롤아웃 이력
curl http://localhost:8000/api/ml-dispatch/ab-test/history | jq '.'
```

---

## 📚 관련 문서

- **DEPLOYMENT_EXECUTION_GUIDE.md** - 상세 배포 가이드
- **PHASE3_DEPLOYMENT_GUIDE.md** - Phase 3 배포 가이드
- **PHASE3_ARCHITECTURE.md** - 아키텍처 설계
- **ML_DISPATCH_ARCHITECTURE.md** - ML 시스템 전체

---

## 🎉 체크리스트

### 배포 전
- [x] Phase 1, 2, 3 구현 완료
- [x] 배포 스크립트 생성
- [x] 모니터링 스크립트 생성
- [ ] PR 병합

### 배포 중
- [ ] Git pull 완료
- [ ] 배포 스크립트 실행
- [ ] 헬스 체크 통과

### 배포 후
- [ ] 파일럿 롤아웃 10%
- [ ] 자동 모니터링 시작
- [ ] 1시간 후 성공 기준 검증
- [ ] 성공 시 30% 확대 또는 실패 시 롤백

---

## 🚀 지금 바로 시작!

**복사해서 실행하세요:**

```bash
# 1. PR 병합 (GitHub 웹에서)
# https://github.com/rpaakdi1-spec/3-/pull/3

# 2. 배포
ssh root@139.150.11.99 << 'ENDSSH'
cd /root/uvis
git pull origin main
./scripts/deploy_production.sh
ENDSSH

# 3. 파일럿 롤아웃 (배포 성공 후)
ssh root@139.150.11.99 << 'ENDSSH'
cd /root/uvis
./scripts/gradual_rollout.sh pilot
nohup ./scripts/monitor_pilot.sh > /root/uvis/logs/monitor_output.log 2>&1 &
ENDSSH

# 4. 모니터링 확인
ssh root@139.150.11.99
tail -f /root/uvis/logs/monitor_output.log
```

**축하합니다! 배포 준비가 완료되었습니다!** 🎉
