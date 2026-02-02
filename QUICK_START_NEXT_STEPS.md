# ⚡ 빠른 시작 가이드 - 다음 할 일

**날짜**: 2026-02-02  
**상태**: Phase 3 완료, 다음 단계 준비

---

## 🎯 즉시 실행 가능한 작업 (복사 & 붙여넣기)

### 1️⃣ AI API 키 설정 (15분)

**서버에서 실행**:

```bash
# 서버 SSH 접속
ssh root@139.150.11.99

# 작업 디렉토리 이동
cd /root/uvis

# .env 백업
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)

# .env 파일 편집
nano .env
```

**.env에 추가할 내용**:
```env
# OpenAI API Key (필수)
OPENAI_API_KEY=sk-proj-your-api-key-here

# Gemini API Key (선택)
GEMINI_API_KEY=your-gemini-api-key-here

# AI 기능 활성화
ENABLE_AI_FEATURES=true
AI_MODEL=gpt-4
```

**API 키 발급 링크**:
- OpenAI: https://platform.openai.com/api-keys
- Gemini: https://makersuite.google.com/app/apikey

**Backend 재시작**:
```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml restart backend

# 30초 대기
sleep 30

# Health Check
curl http://localhost:8000/health

# AI 기능 테스트
curl -s http://localhost:8000/api/v1/ai-usage/stats | jq '.'
```

**예상 결과**: ✅ AI 채팅 및 비용 모니터링 활성화

---

### 2️⃣ AB Test UI 활성화 (30분)

**로컬 개발 환경에서**:

#### Step 1: App.tsx 라우팅 확인
```bash
cd /home/user/webapp

# ABTestMonitor 라우팅 확인
grep -n "ABTestMonitor" frontend/src/App.tsx
```

**라우팅이 없다면 frontend/src/App.tsx에 추가**:
```tsx
// Import 추가
import ABTestMonitor from './pages/ABTestMonitor';

// 보호된 경로 섹션에 라우트 추가
<Route 
  path="/ml-dispatch/ab-test" 
  element={
    <ProtectedRoute>
      <ABTestMonitor />
    </ProtectedRoute>
  } 
/>
```

#### Step 2: Sidebar 메뉴 추가
**frontend/src/components/Layout/Sidebar.tsx 확인**:
```bash
grep -A 10 "ML Dispatch" frontend/src/components/Layout/Sidebar.tsx
```

**ML Dispatch 섹션에 메뉴 항목 추가**:
```tsx
{
  title: 'AB Test 모니터링',
  path: '/ml-dispatch/ab-test',
  icon: <Activity className="w-5 h-5" />,
}
```

#### Step 3: 커밋 및 배포
```bash
cd /home/user/webapp

# 변경사항 확인
git status
git diff frontend/src/App.tsx
git diff frontend/src/components/Layout/Sidebar.tsx

# 커밋
git add frontend/src/App.tsx frontend/src/components/Layout/Sidebar.tsx
git commit -m "feat: Add AB Test monitoring UI route and sidebar menu"
git push origin main
```

#### Step 4: 서버에서 배포
```bash
# 서버 SSH 접속
ssh root@139.150.11.99

# 코드 업데이트
cd /root/uvis
git pull origin main

# Frontend 재배포
docker-compose -f docker-compose.prod.yml up -d --build frontend

# 30초 대기
sleep 30

# 상태 확인
docker ps
curl http://localhost:80
```

#### Step 5: 브라우저에서 확인
1. http://139.150.11.99 접속
2. 로그인
3. Sidebar에서 "AB Test 모니터링" 메뉴 확인
4. 클릭하여 대시보드 표시 확인

**예상 결과**: ✅ AB Test 실시간 모니터링 UI 활성화

---

### 3️⃣ vehiclestatus enum 수정 (15분)

**서버에서 실행**:

```bash
# 서버 SSH 접속
ssh root@139.150.11.99
cd /root/uvis

# DB 사용자 확인
grep POSTGRES_USER .env

# PostgreSQL 접속 (DB_USER를 실제 값으로 대체)
docker exec -it uvis-db psql -U postgres -d uvisdb
```

**PostgreSQL 내에서 실행**:
```sql
-- 1. 현재 enum 값 확인
SELECT enumlabel FROM pg_enum 
WHERE enumtypid = 'vehiclestatus'::regtype 
ORDER BY enumsortorder;

-- 2. in_transit 값 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumlabel = 'in_transit' 
        AND enumtypid = 'vehiclestatus'::regtype
    ) THEN
        ALTER TYPE vehiclestatus ADD VALUE 'in_transit';
        RAISE NOTICE 'Added in_transit to vehiclestatus enum';
    ELSE
        RAISE NOTICE 'in_transit already exists';
    END IF;
END $$;

-- 3. 최종 확인
SELECT enumlabel FROM pg_enum 
WHERE enumtypid = 'vehiclestatus'::regtype 
ORDER BY enumsortorder;

-- 4. 종료
\q
```

**Backend 재시작**:
```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml restart backend

# 30초 대기
sleep 30

# 로그 확인 (in_transit 에러 확인)
docker logs uvis-backend --tail 50 | grep -i "in_transit"
docker logs uvis-backend --tail 50 | grep -i "error"
```

**예상 결과**: ✅ in_transit enum 오류 해결

---

### 4️⃣ 시스템 상태 확인 (5분)

**서버에서 실행**:

```bash
# 서버 SSH 접속
ssh root@139.150.11.99
cd /root/uvis

# 컨테이너 상태
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Health Check
curl http://localhost:8000/health | jq '.'
curl http://localhost:80

# ML Dispatch 통계
curl -s http://localhost:8000/api/ml-dispatch/ab-test/stats | jq '.'

# 성능 모니터링
bash scripts/performance_monitor.sh

# 최근 백업 확인
ls -lh backups/ | tail -5
```

**예상 출력**:
```
✅ uvis-frontend:  Running (healthy)
✅ uvis-backend:   Running (healthy)
✅ uvis-db:        Running (healthy)
✅ uvis-redis:     Running (healthy)

Health: {"status": "healthy", "environment": "production"}
AB Test: {"total_users": 1, "target_rollout_percentage": 10}
```

---

## 📊 모니터링 명령어 모음

### 일일 체크 (5분)
```bash
cd /root/uvis

# 전체 시스템 상태
echo "=== 컨테이너 상태 ==="
docker ps

echo -e "\n=== API Health Check ==="
curl -s http://localhost:8000/health | jq '.'

echo -e "\n=== 디스크 사용량 ==="
df -h | grep -E "Filesystem|/dev/sda"

echo -e "\n=== 최근 백업 ==="
ls -lh backups/ | tail -3

echo -e "\n=== Backend 에러 로그 ==="
docker logs uvis-backend --tail 20 | grep -i error || echo "No errors"
```

### ML Dispatch 모니터링 (5분)
```bash
cd /root/uvis

echo "=== AB Test 통계 ==="
curl -s http://localhost:8000/api/ml-dispatch/ab-test/stats | jq '.'

echo -e "\n=== 그룹 할당 ==="
curl -s http://localhost:8000/api/ml-dispatch/ab-test/assignment | jq '.'

echo -e "\n=== 최근 배차 ==="
curl -s "http://localhost:8000/api/v1/dispatches/?limit=5" | jq '.items[] | {id, dispatch_number, status}'

echo -e "\n=== ML Dispatch 성능 ==="
curl -s http://localhost:8000/api/ml-dispatch/performance | jq '.' || echo "Performance metrics not available"
```

### AI 비용 모니터링 (5분)
```bash
cd /root/uvis

echo "=== AI 사용 통계 ==="
curl -s http://localhost:8000/api/v1/ai-usage/stats | jq '.'

echo -e "\n=== AI 비용 요약 ==="
curl -s "http://localhost:8000/api/v1/ai-usage/cost-summary?period=7d" | jq '.'

echo -e "\n=== 최근 AI 로그 ==="
curl -s "http://localhost:8000/api/v1/ai-usage/logs?limit=5" | jq '.items[] | {model, cost, created_at}'
```

---

## 🚨 문제 해결 가이드

### Frontend 접속 불가
```bash
# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart frontend nginx

# 로그 확인
docker logs uvis-frontend --tail 50
docker logs uvis-nginx --tail 30

# 포트 확인
netstat -tlnp | grep -E "80|443"
```

### Backend API 오류
```bash
# Backend 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 상세 로그
docker logs uvis-backend --tail 100 | grep -i error

# Health Check
curl -v http://localhost:8000/health
```

### Database 연결 문제
```bash
# DB 상태 확인
docker exec uvis-db pg_isready -U postgres

# DB 접속 테스트
docker exec -it uvis-db psql -U postgres -d uvisdb -c "\conninfo"

# DB 재시작
docker-compose -f docker-compose.prod.yml restart db
```

### Redis 문제
```bash
# Redis 연결 테스트
docker exec uvis-redis redis-cli ping

# Redis 재시작
docker-compose -f docker-compose.prod.yml restart redis

# Redis 메모리 확인
docker exec uvis-redis redis-cli info memory
```

### 전체 시스템 재시작 (최후 수단)
```bash
cd /root/uvis

# 모든 컨테이너 중지
docker-compose -f docker-compose.prod.yml down

# 30초 대기
sleep 30

# 다시 시작
docker-compose -f docker-compose.prod.yml up -d

# 상태 확인
docker ps
```

---

## 📝 체크리스트

### ✅ 완료된 작업
- [x] Frontend 15개 페이지 Layout 통합
- [x] Backend ML Dispatch API 인증 제거
- [x] ML Dispatch 10% 파일럿 롤아웃
- [x] AB Test 시스템 작동
- [x] 자동 백업 시스템 (일일)
- [x] 성능 모니터링 스크립트
- [x] GitHub 문서 동기화

### 🎯 다음 작업 (우선순위)
- [ ] **AI API 키 설정** (15분) ← 지금 바로!
- [ ] **AB Test UI 활성화** (30분) ← 지금 바로!
- [ ] **vehiclestatus enum 수정** (15분)
- [ ] ML Dispatch 모니터링 (계속)
- [ ] Frontend 페이지 검증 (1시간)
- [ ] Sentry 통합 (2시간)
- [ ] DB 인덱스 최적화 (2시간)
- [ ] 오프사이트 백업 (3시간)

---

## 🔗 유용한 링크

### 시스템 접근
- **Frontend**: http://139.150.11.99
- **Backend API**: http://139.150.11.99:8000
- **API 문서**: http://139.150.11.99:8000/docs
- **ReDoc**: http://139.150.11.99:8000/redoc

### 외부 서비스
- **OpenAI Platform**: https://platform.openai.com/
- **Google AI Studio**: https://makersuite.google.com/
- **Sentry**: https://sentry.io/
- **GitHub Repo**: https://github.com/rpaakdi1-spec/3-

### 문서
- `NEXT_STEPS_PRIORITY.md` - 상세 로드맵
- `FINAL_SYSTEM_SUMMARY.md` - 시스템 요약
- `BACKUP_GUIDE.md` - 백업 가이드
- `SERVER_DEPLOYMENT_COMMANDS.md` - 배포 가이드
- `ML_DISPATCH_AUTH_REMOVAL.md` - ML Dispatch 문서

---

## 💡 팁

### 1. SSH 접속 간편화
```bash
# ~/.ssh/config에 추가
Host uvis-server
    HostName 139.150.11.99
    User root
    Port 22

# 접속
ssh uvis-server
```

### 2. 자주 사용하는 별칭
```bash
# ~/.bashrc에 추가
alias uvis='cd /root/uvis'
alias uvis-status='cd /root/uvis && docker ps'
alias uvis-logs='cd /root/uvis && docker logs uvis-backend --tail 50'
alias uvis-health='curl -s http://localhost:8000/health | jq .'
alias uvis-monitor='cd /root/uvis && bash scripts/performance_monitor.sh'

# 적용
source ~/.bashrc
```

### 3. 로그 실시간 모니터링
```bash
# Backend 로그 실시간 보기
docker logs -f uvis-backend

# 특정 키워드 필터링
docker logs -f uvis-backend | grep -i error

# 모든 컨테이너 로그
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🎉 시작하기

**지금 바로 실행할 수 있는 3가지:**

1. **AI API 키 설정** (15분)
   ```bash
   ssh root@139.150.11.99
   cd /root/uvis
   nano .env  # OPENAI_API_KEY 추가
   docker-compose -f docker-compose.prod.yml restart backend
   ```

2. **시스템 상태 확인** (5분)
   ```bash
   ssh root@139.150.11.99
   cd /root/uvis
   bash scripts/performance_monitor.sh
   ```

3. **AB Test UI 활성화** (30분)
   - 로컬에서 App.tsx와 Sidebar.tsx 수정
   - 커밋 및 푸시
   - 서버에서 배포

---

**궁금한 점이 있으시면 언제든지 문의하세요!**

**생성일**: 2026-02-02  
**버전**: 1.0

**프로젝트 성공을 응원합니다! 🚀**
