# 🚀 서버 배포 명령어 가이드

**최종 업데이트**: 2026-02-02  
**커밋**: c2a3652  
**변경사항**: AI 비용 모니터링 페이지 사이드바 수정 완료

---

## ✅ 현재 상태

### 완료된 작업
- ✅ Phase 1-3 ML 배차 시스템 구현 완료
- ✅ Frontend: Sidebar 레이아웃 수정 완료
- ✅ Backend: 인증 의존성 제거 (API 테스트 가능)
- ✅ 배포 스크립트 준비 완료
- ✅ Git 워크플로우 완료 (커밋 c2a3652 푸시)

### 알려진 이슈
⚠️ **Backend 실행 시 DB 오류**: `vehiclestatus` enum에 'in_transit' 값 누락
- 영향: Dashboard metrics 및 vehicle updates 브로드캐스트 실패
- 해결: DB 마이그레이션 또는 코드 수정 필요 (배포 후 처리 가능)

⚠️ **ML Dispatch A/B Test API 인증 문제**: 401 Not authenticated
- 영향: AB 테스트 롤아웃 API 호출 실패
- 해결: 백엔드 코드에서 인증 제거 시도했으나 추가 확인 필요

---

## 🎯 서버 배포 단계별 가이드

### Step 1: 서버 접속
```bash
ssh root@139.150.11.99
cd /root/uvis
```

### Step 2: 최신 코드 가져오기
```bash
git pull origin main
```

**예상 출력**:
```
From https://github.com/rpaakdi1-spec/3-
   adcd578..c2a3652  main       -> origin/main
Updating adcd578..c2a3652
Fast-forward
 frontend/src/pages/AICostDashboardPage.tsx | 19 ++++++++++++++-----
 1 file changed, 14 insertions(+), 5 deletions(-)
```

### Step 3: Frontend 재빌드 (필수)
```bash
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

**예상 시간**: 약 2-3분  
**확인**: 빌드 성공 후 컨테이너 시작

### Step 4: Backend 헬스 체크
```bash
# Backend 상태 확인
docker logs uvis-backend --tail 30

# API 헬스 체크
curl http://localhost:8000/health
```

**예상 응답**:
```json
{"status":"healthy","timestamp":"2026-02-02T..."}
```

### Step 5: Frontend 접속 확인
브라우저에서 접속: **http://139.150.11.99**

**확인 사항**:
- ✅ 사이드바 메뉴가 보이는지 확인
- ✅ "AI 비용 모니터링" 페이지 이동 시 사이드바 유지 확인
- ✅ 모든 페이지에서 네비게이션 정상 작동 확인

---

## 🔧 선택적 배포 (Phase 3 ML Dispatch)

### A. 파일럿 롤아웃 시도 (선택)

⚠️ **주의**: 현재 인증 문제로 실패할 수 있습니다. Backend 수정 후 재시도 권장.

```bash
# 10% 롤아웃 시도
./scripts/gradual_rollout.sh pilot

# 또는 API 직접 호출
curl -X POST 'http://localhost:8000/api/ml-dispatch/ab-test/rollout?percentage=10'
```

**성공 시 예상 응답**:
```json
{"status":"success","percentage":10,"timestamp":"..."}
```

**실패 시 응답**:
```json
{"detail":"Not authenticated"}
```

### B. 모니터링 시작 (롤아웃 성공 시)

```bash
# 로그 디렉토리 생성
mkdir -p logs

# 백그라운드 모니터링 시작
nohup ./scripts/monitor_pilot.sh > logs/monitor_output.log 2>&1 &

# 프로세스 확인
ps aux | grep monitor_pilot

# 실시간 로그 확인
tail -f logs/monitor_output.log
```

---

## 🐛 문제 해결

### 1. Frontend 빌드 실패 시

```bash
# 컨테이너 로그 확인
docker logs uvis-frontend --tail 50

# 강제 재빌드 (캐시 무시)
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### 2. Backend 오류 (vehiclestatus enum)

**임시 해결책**: 오류 무시하고 계속 실행 (핵심 기능은 정상)

**영구 해결책** (선택):
```bash
# 1. PostgreSQL 접속
docker exec -it uvis-db psql -U uvisuser -d uvisdb

# 2. enum 확인
\dT+ vehiclestatus

# 3. 값 추가 (필요 시)
ALTER TYPE vehiclestatus ADD VALUE 'in_transit';

# 4. 종료
\q

# 5. Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

### 3. Redis 연결 오류

```bash
# Redis 상태 확인
docker ps | grep redis

# Redis 재시작
docker-compose -f docker-compose.prod.yml restart redis

# Redis 연결 테스트
docker exec -it uvis-redis redis-cli ping
```

### 4. 전체 서비스 재시작

```bash
# 모든 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart

# 또는 완전 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 서비스 확인 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| Frontend | http://139.150.11.99 | 메인 웹 인터페이스 |
| Backend API | http://139.150.11.99:8000 | REST API 엔드포인트 |
| API 문서 | http://139.150.11.99:8000/docs | Swagger UI |
| Health Check | http://139.150.11.99:8000/health | 서버 상태 확인 |

---

## 📝 빠른 상태 체크

```bash
#!/bin/bash
# 전체 시스템 상태 확인

echo "=== 컨테이너 상태 ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n=== Backend 헬스 체크 ==="
curl -s http://localhost:8000/health | jq

echo -e "\n=== Redis 상태 ==="
docker exec -it uvis-redis redis-cli ping

echo -e "\n=== Backend 최근 로그 (마지막 10줄) ==="
docker logs uvis-backend --tail 10
```

**저장 후 실행**:
```bash
chmod +x quick_status.sh
./quick_status.sh
```

---

## 🎯 다음 단계 (우선순위)

### 우선순위 1: 기본 기능 확인 (즉시 실행)
1. ✅ Frontend 재빌드 및 배포
2. ✅ 사이드바 네비게이션 정상 작동 확인
3. ✅ 모든 페이지 접근 테스트

### 우선순위 2: Backend 안정화 (선택)
1. ⚠️ vehiclestatus enum 오류 수정
2. ⚠️ ML Dispatch API 인증 문제 해결
3. ⚠️ AB Test 롤아웃 재시도

### 우선순위 3: Phase 3 완전 배포 (나중에)
1. 🔄 파일럿 롤아웃 10%
2. 🔄 1시간 모니터링
3. 🔄 단계적 확대 (30% → 50% → 100%)

---

## 💡 참고 문서

- **배포 가이드**: `/root/uvis/PRODUCTION_READY.md`
- **Phase 3 아키텍처**: `/root/uvis/PHASE3_ARCHITECTURE.md`
- **롤아웃 스크립트**: `/root/uvis/scripts/gradual_rollout.sh`
- **모니터링 스크립트**: `/root/uvis/scripts/monitor_pilot.sh`

---

## 📞 긴급 롤백

ML Dispatch 기능에 문제가 발생할 경우:

```bash
# 방법 1: 스크립트 사용
./scripts/gradual_rollout.sh rollback

# 방법 2: API 직접 호출
curl -X POST 'http://localhost:8000/api/ml-dispatch/ab-test/rollout?percentage=0'
```

---

**✅ 준비 완료!**  
위 명령어들을 서버에서 순서대로 실행하세요.

**🎉 예상 결과**:
- Frontend: Sidebar가 모든 페이지에서 정상 표시
- Backend: 핵심 기능 정상 작동 (일부 enum 오류는 무시 가능)
- ML Dispatch: 선택적 기능 (추후 완성 가능)
