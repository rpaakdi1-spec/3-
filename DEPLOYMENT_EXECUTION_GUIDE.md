# 🚀 프로덕션 배포 실행 가이드

## 📋 현재 상태
- ✅ Phase 1, 2, 3 구현 완료
- ✅ Git 커밋 및 PR 생성 완료
- ✅ 배포 스크립트 생성 완료

---

## 🎯 배포 단계

### Option 1: 자동 배포 (권장) ⚡

**서버에서 한 번에 실행:**
```bash
# 1. 서버 접속
ssh root@139.150.11.99

# 2. 프로젝트 디렉토리로 이동
cd /root/uvis

# 3. 최신 코드 받기 (PR 병합 후)
git pull origin main

# 4. 배포 스크립트 실행 (모든 단계 자동 실행)
./scripts/deploy_production.sh
```

**스크립트가 자동으로 수행하는 작업:**
1. ✅ Git pull (최신 코드)
2. ✅ Redis 확인 및 시작
3. ✅ 백엔드 재빌드 및 재시작
4. ✅ 프론트엔드 재빌드 및 재시작
5. ✅ 헬스 체크 (컨테이너, API, Redis)
6. ✅ 배포 완료 요약

**예상 소요 시간: 3~5분**

---

### Option 2: 수동 배포 (단계별 확인)

```bash
# 서버 접속
ssh root@139.150.11.99
cd /root/uvis

# 1. Git Pull
git pull origin main

# 2. Redis 확인
docker ps | grep redis || docker-compose -f docker-compose.prod.yml up -d redis

# 3. 백엔드 재빌드 (5분)
docker-compose -f docker-compose.prod.yml up -d --build backend

# 대기 (30초)
sleep 30

# 4. 프론트엔드 재빌드 (5분)
docker-compose -f docker-compose.prod.yml up -d --build frontend

# 대기 (20초)
sleep 20

# 5. 헬스 체크
docker ps | grep uvis
docker logs uvis-backend --tail 20
curl http://localhost:8000/api/ml-dispatch/ab-test/stats
```

---

## 🩺 배포 후 확인 사항

### 1. 컨테이너 상태
```bash
docker ps | grep uvis
```

**확인 항목:**
- ✅ uvis-backend (Up)
- ✅ uvis-frontend (Up)
- ✅ uvis-redis (Up)
- ✅ uvis-db (Up)

### 2. 백엔드 로그
```bash
docker logs uvis-backend --tail 50
```

**확인 항목:**
- ✅ "Application startup complete" 메시지
- ✅ 에러 로그 없음
- ✅ ML Dispatch 관련 로그 정상

### 3. Redis 연결
```bash
docker exec uvis-redis redis-cli ping
```

**예상 응답:** `PONG`

### 4. ML Dispatch API
```bash
curl http://139.150.11.99:8000/api/ml-dispatch/ab-test/stats
```

**예상 응답:**
```json
{
  "total_users": 0,
  "control_count": 0,
  "treatment_count": 0,
  "actual_treatment_percentage": 0.0,
  "target_rollout_percentage": 10
}
```

### 5. API 문서
브라우저로 접속: `http://139.150.11.99:8000/docs`

**확인 항목:**
- ✅ ML Dispatch 섹션 존재
- ✅ A/B Test 엔드포인트 6개 확인
  - GET `/api/ml-dispatch/ab-test/assignment`
  - POST `/api/ml-dispatch/ab-test/rollout`
  - GET `/api/ml-dispatch/ab-test/stats`
  - GET `/api/ml-dispatch/ab-test/metrics`
  - GET `/api/ml-dispatch/ab-test/history`
  - POST `/api/ml-dispatch/ab-test/force-assign`

### 6. 프론트엔드
브라우저로 접속: `http://139.150.11.99`

**확인 항목:**
- ✅ 로그인 정상 작동
- ✅ 배차 최적화 페이지 접속
- ✅ (추후) ML 추천 패널 표시 확인

---

## 🧪 파일럿 롤아웃 (10%)

배포 확인 완료 후 파일럿 롤아웃을 시작합니다.

### 방법 A: 자동 스크립트 (권장)
```bash
cd /root/uvis
./scripts/gradual_rollout.sh pilot
```

**스크립트 동작:**
1. 현재 메트릭 확인
2. 롤아웃 비율 10%로 설정
3. 1시간 대기
4. 성공 기준 자동 체크

### 방법 B: API 직접 호출
```bash
curl -X POST "http://139.150.11.99:8000/api/ml-dispatch/ab-test/rollout?percentage=10" \
  -H "Content-Type: application/json"
```

### 방법 C: 프론트엔드 UI
1. `http://139.150.11.99` 접속
2. A/B Test Monitor 페이지 이동
3. 슬라이더를 10%로 조정
4. "적용" 버튼 클릭

---

## 📊 모니터링 (1시간)

### 실시간 메트릭 확인 (10분마다)

#### 1. A/B 테스트 통계
```bash
curl http://139.150.11.99:8000/api/ml-dispatch/ab-test/stats
```

#### 2. 성과 메트릭
```bash
curl http://139.150.11.99:8000/api/ml-dispatch/ab-test/metrics
```

**확인 항목:**
- Treatment 그룹 성공률
- Treatment 그룹 평균 ML 점수
- Control vs Treatment 비교

#### 3. 백엔드 로그 실시간 모니터링
```bash
docker logs uvis-backend --tail 50 -f | grep -i "ml\|rollback\|error"
```

#### 4. 프론트엔드 대시보드
브라우저: `http://139.150.11.99`
→ **A/B Test Monitor** 페이지에서 실시간 확인

---

## ✅ 성공 기준 검증 (1시간 후)

### 필수 확인 항목

| 메트릭 | 목표 | 확인 방법 |
|--------|------|-----------|
| ML 성공률 | ≥ 90% | A/B Test Metrics API |
| 평균 ML 점수 | ≥ 0.70 | A/B Test Metrics API |
| 에러율 | < 5% | Backend Logs |
| 응답 시간 | < 2초 | A/B Test Metrics API |
| 자동 롤백 | 미발생 | Backend Logs |

### 성공 시
✅ **다음 단계로 진행**: 30% 확대 롤아웃
```bash
./scripts/gradual_rollout.sh expand
```

### 실패 시
❌ **즉시 롤백 및 원인 분석**
```bash
# 롤백
./scripts/gradual_rollout.sh rollback

# 로그 분석
docker logs uvis-backend --tail 200 | grep -i error

# 원인 파악 후 코드 수정 및 재배포
```

---

## 🔧 트러블슈팅

### 문제 1: 배포 스크립트 실행 실패
```bash
# 증상
./scripts/deploy_production.sh: Permission denied

# 해결
chmod +x scripts/deploy_production.sh
./scripts/deploy_production.sh
```

### 문제 2: Redis 연결 실패
```bash
# 증상
Failed to connect to Redis

# 해결
docker-compose -f docker-compose.prod.yml up -d redis
docker restart uvis-backend
```

### 문제 3: 백엔드 시작 실패
```bash
# 증상
Backend container exits immediately

# 확인
docker logs uvis-backend --tail 100

# 해결 (일반적 원인)
# 1. 환경 변수 확인
cat .env | grep REDIS

# 2. 데이터베이스 연결 확인
docker exec uvis-db psql -U postgres -c "SELECT 1;"

# 3. 재빌드
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate backend
```

### 문제 4: ML Dispatch API 응답 없음
```bash
# 증상
curl: (52) Empty reply from server

# 확인
docker logs uvis-backend | grep -i "ml-dispatch"

# 해결
# 1. 백엔드 재시작
docker restart uvis-backend

# 2. 로그 확인
docker logs uvis-backend --tail 50 -f

# 3. 필요 시 재빌드
docker-compose -f docker-compose.prod.yml up -d --build backend
```

### 문제 5: 프론트엔드 화이트 스크린
```bash
# 증상
브라우저에서 빈 화면만 표시

# 해결
# 1. 프론트엔드 로그 확인
docker logs uvis-frontend --tail 50

# 2. 브라우저 콘솔 확인 (F12)

# 3. 프론트엔드 재빌드
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate frontend
```

---

## 📞 긴급 롤백

문제 발생 시 즉시 롤백하여 안정성을 확보합니다.

### 방법 A: 스크립트 (권장)
```bash
./scripts/gradual_rollout.sh rollback
```

### 방법 B: API 직접 호출
```bash
curl -X POST "http://139.150.11.99:8000/api/ml-dispatch/ab-test/rollout?percentage=0"
```

### 방법 C: 프론트엔드 UI
1. A/B Test Monitor 페이지
2. 슬라이더를 0%로 조정
3. "적용" 버튼 클릭

### 롤백 후 조치
1. ✅ 로그 수집 및 분석
2. ✅ 에러 원인 파악
3. ✅ 코드 수정
4. ✅ 테스트 환경에서 재검증
5. ✅ 재배포

---

## 📚 관련 문서

- **PHASE3_DEPLOYMENT_GUIDE.md** - 상세 배포 가이드
- **ML_DISPATCH_ARCHITECTURE.md** - ML 시스템 아키텍처
- **ML_DEPLOYMENT_GUIDE.md** - ML 배포 가이드

---

## 📝 배포 체크리스트

### 배포 전
- [ ] PR 리뷰 및 승인 완료
- [ ] main 브랜치 병합 완료
- [ ] 백업 생성 (코드 & DB)
- [ ] 롤백 계획 수립

### 배포 중
- [ ] Git pull 완료
- [ ] Redis 서비스 실행 확인
- [ ] 백엔드 재빌드 및 재시작
- [ ] 프론트엔드 재빌드 및 재시작
- [ ] 헬스 체크 통과

### 배포 후
- [ ] 파일럿 롤아웃 10% 실행
- [ ] 1시간 모니터링
- [ ] 성공 기준 충족 확인
- [ ] 다음 단계 계획 (30% 확대)

---

## 🎉 배포 완료 후

축하합니다! 프로덕션 배포가 완료되었습니다.

**다음 단계:**
1. **1시간 모니터링** - 메트릭 실시간 확인
2. **성공 기준 검증** - 성공률, ML 점수, 에러율 체크
3. **Week 2 준비** - 30% 확대 롤아웃 계획

**예상 타임라인:**
- Week 1: Pilot 10% (현재)
- Week 2: Expand 30%
- Week 3: Half 50%
- Week 4: Full 100% 🎉

---

**문의사항이 있으면 언제든지 알려주세요!**
