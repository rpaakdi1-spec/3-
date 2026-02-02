# 🎯 다음 할 일 - 우선순위별 로드맵

**날짜**: 2026-02-02  
**프로젝트**: Cold Chain Dispatch System  
**현재 상태**: ✅ Phase 3 완료, 프로덕션 배포 완료

---

## 📋 현재 상태 요약

### ✅ 완료된 작업
- Frontend 15개 관리자 페이지 Layout/Sidebar 통합
- Backend 안정화 및 ML Dispatch API 인증 제거
- ML Dispatch Phase 3: 10% 파일럿 롤아웃 활성화
- AB Test 시스템 정상 작동 (1명 treatment 그룹 할당)
- CVRPTW 배차 최적화 성공 (2건 주문 → 2건 배차)
- 자동 백업 시스템 구축 (일일 백업, 30일 보관)
- 성능 모니터링 스크립트 작성

### 📊 시스템 지표
```
✅ Frontend:      http://139.150.11.99 (Running, Healthy)
✅ Backend:       http://139.150.11.99:8000 (Running, Healthy)
✅ Database:      Running, Healthy
✅ Redis:         Running, Healthy
✅ API 응답:      5-20ms (매우 빠름)
✅ 메모리:        적정 수준 (26.69%)
✅ 디스크:        여유 충분 (72%)
```

### ⚠️ 알려진 이슈
1. **vehiclestatus enum**: `in_transit` 값이 DB에 제대로 추가되지 않음
2. **AI API 키 미설정**: OpenAI/Gemini API 키가 없어 AI 기능 사용 불가
3. **AB Test UI 미활성화**: Frontend에 ABTestMonitor 라우팅 필요

---

## 🔥 우선순위 1: 즉시 처리 (핵심 기능)

### 1️⃣ GitHub 커밋 및 푸시 (5분)

**목표**: 로컬 변경사항을 GitHub에 동기화

**실행 명령** (로컬 개발 환경):
```bash
cd /home/user/webapp

# FINAL_SYSTEM_SUMMARY.md 커밋
git add FINAL_SYSTEM_SUMMARY.md
git commit -m "docs: Add final system summary and completion report for Phase 3"
git push origin main

# 기타 untracked 파일 정리 (선택 사항)
git status
```

**결과 확인**:
- GitHub 저장소에 최신 커밋 반영 확인
- https://github.com/rpaakdi1-spec/3-

---

### 2️⃣ AI API 키 설정 (15분)

**목표**: AI 채팅 및 비용 모니터링 기능 활성화

**현재 문제**:
- AI 요청 5회 모두 실패 (API 키 미설정)
- AI Cost Dashboard 데이터 없음

**해결 방법** (서버에서):

```bash
cd /root/uvis

# 1. 현재 .env 백업
cp .env .env.backup_$(date +%Y%m%d)

# 2. OpenAI API 키 추가
nano .env
# 또는
vi .env
```

**.env에 추가할 내용**:
```env
# OpenAI API Key (필수)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Gemini API Key (선택)
GEMINI_API_KEY=your-gemini-api-key-here

# AI 기능 활성화
ENABLE_AI_FEATURES=true
AI_MODEL=gpt-4
```

**API 키 발급 방법**:
1. **OpenAI**: https://platform.openai.com/api-keys
   - 계정 로그인 → API Keys → Create new secret key
   - 키 복사 후 `.env`에 붙여넣기

2. **Gemini (선택)**: https://makersuite.google.com/app/apikey
   - Google 계정으로 로그인 → Get API key
   - 키 복사 후 `.env`에 붙여넣기

**Backend 재시작**:
```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml restart backend

# 30초 대기
sleep 30

# 테스트
curl -s http://localhost:8000/api/v1/ai-usage/stats | jq '.'
```

**예상 결과**:
- AI 채팅 기능 정상 작동
- AI Cost Dashboard에 실시간 데이터 표시
- 비용 추적 시작

---

### 3️⃣ AB Test 모니터링 UI 활성화 (30분)

**목표**: Frontend에서 AB Test 결과를 실시간으로 볼 수 있도록 UI 활성화

**현재 상태**:
- ABTestMonitor 컴포넌트는 이미 생성됨
- 라우팅만 추가하면 사용 가능

**실행 순서** (로컬 개발 환경):

#### Step 1: App.tsx 라우팅 추가
```bash
cd /home/user/webapp

# 1. App.tsx 파일 확인
grep -n "ABTestMonitor" frontend/src/App.tsx

# 2. 라우팅이 없다면 추가 필요
```

**frontend/src/App.tsx에 추가**:
```tsx
import ABTestMonitor from './pages/ABTestMonitor';

// 보호된 경로 섹션에 추가
<Route 
  path="/ml-dispatch/ab-test" 
  element={
    <ProtectedRoute>
      <ABTestMonitor />
    </ProtectedRoute>
  } 
/>
```

#### Step 2: Sidebar에 메뉴 추가
**frontend/src/components/Layout/Sidebar.tsx**:
```tsx
// ML Dispatch 섹션에 추가
{
  title: 'AB Test 모니터링',
  path: '/ml-dispatch/ab-test',
  icon: <Activity className="w-5 h-5" />,
}
```

#### Step 3: 빌드 및 배포
```bash
cd /home/user/webapp

# 변경사항 커밋
git add frontend/src/App.tsx frontend/src/components/Layout/Sidebar.tsx
git commit -m "feat: Add AB Test monitoring UI route and sidebar menu"
git push origin main

# 서버에서 배포 (SSH 접속 후)
cd /root/uvis
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build frontend
```

#### Step 4: 테스트
1. http://139.150.11.99 접속
2. 로그인
3. Sidebar에서 "AB Test 모니터링" 클릭
4. 실시간 데이터 확인:
   - Total Users: 1
   - Treatment: 100%
   - Target Rollout: 10%

**예상 결과**:
- AB Test 통계를 실시간으로 모니터링 가능
- 그래프와 차트로 시각화
- 롤아웃 비율 조정 가능

---

## 🎯 우선순위 2: 중요 (이번 주 내)

### 4️⃣ ML Dispatch 파일럿 모니터링 (계속 진행)

**목표**: 10% 롤아웃 결과 분석 및 성능 확인

**모니터링 항목**:
```bash
cd /root/uvis

# 1. AB Test 통계
curl -s http://localhost:8000/api/ml-dispatch/ab-test/stats | jq '.'

# 2. 배차 성공률 확인
curl -s "http://localhost:8000/api/v1/dispatches/?dispatch_date=2026-02-07" | jq '.items | length'

# 3. 성능 메트릭
bash scripts/performance_monitor.sh
```

**분석 포인트**:
- Treatment 그룹 vs Control 그룹 성공률
- ML 기반 배차 vs 수동 배차 비교
- 응답 시간 및 배차 품질

**롤아웃 확대 계획**:
```
현재: 10%
↓ (1주 후, 문제 없으면)
Phase 2: 25%
↓ (1주 후, 문제 없으면)
Phase 3: 50%
↓ (1주 후, 문제 없으면)
Phase 4: 100% 전면 배포
```

---

### 5️⃣ vehiclestatus enum 수정 (30분)

**목표**: DB enum에 `in_transit` 값 정상 추가

**현재 문제**:
```
Error: invalid input value for enum vehiclestatus: "in_transit"
```

**해결 방법** (서버에서):
```bash
cd /root/uvis

# 1. DB 사용자 확인
grep POSTGRES_USER .env

# 2. DB 접속 및 enum 수정
docker exec -it uvis-db psql -U <DB_USER> -d uvisdb

# SQL 실행:
-- 현재 enum 값 확인
SELECT enumlabel FROM pg_enum 
WHERE enumtypid = 'vehiclestatus'::regtype 
ORDER BY enumsortorder;

-- in_transit 추가
ALTER TYPE vehiclestatus ADD VALUE IF NOT EXISTS 'in_transit';

-- 확인
SELECT enumlabel FROM pg_enum 
WHERE enumtypid = 'vehiclestatus'::regtype 
ORDER BY enumsortorder;

-- 종료
\q
```

**Backend 재시작**:
```bash
docker-compose -f docker-compose.prod.yml restart backend
sleep 30

# 로그 확인 (in_transit 에러가 사라졌는지)
docker logs uvis-backend --tail 50 | grep -i "in_transit"
```

---

### 6️⃣ Frontend 페이지 통합 검증 (1시간)

**목표**: 모든 관리자 페이지에서 Sidebar가 정상 작동하는지 확인

**테스트 시나리오**:
```
✅ 체크리스트:
1. 로그인 (http://139.150.11.99)
2. Dashboard → Sidebar 표시 확인
3. 주문 관리 → Sidebar 표시 및 메뉴 이동 확인
4. 배차 관리 → Sidebar 표시 확인
5. 차량 관리 → Sidebar 표시 확인
6. 거래처 관리 → Sidebar 표시 확인
7. AI 채팅 → Sidebar 표시 확인
8. AI 비용 대시보드 → Sidebar 표시 확인
9. Analytics → Sidebar 표시 확인
10. BI 대시보드 → Sidebar 표시 확인
11. ML 학습 → Sidebar 표시 확인
12. 최적화 → Sidebar 표시 확인
13. 주문 캘린더 → Sidebar 표시 확인
14. 실시간 모니터링 → Sidebar 표시 확인
15. 리포트 → Sidebar 표시 확인
16. 설정 → Sidebar 표시 확인
```

**문제 발견 시**:
```bash
cd /home/user/webapp

# 해당 페이지 파일 확인
ls -l frontend/src/pages/<PageName>.tsx

# Layout wrapper 확인
grep -n "Layout" frontend/src/pages/<PageName>.tsx
```

---

## 📈 우선순위 3: 개선 (다음 주)

### 7️⃣ Sentry 에러 추적 통합 (2시간)

**목표**: 프로덕션 에러를 실시간으로 추적하고 알림 받기

**설정 순서**:

#### 1. Sentry 계정 생성
- https://sentry.io/signup/
- 무료 플랜으로 시작

#### 2. Backend 통합
```bash
cd /home/user/webapp

# Sentry SDK 설치 (backend/requirements.txt에 추가)
echo "sentry-sdk[fastapi]==1.40.0" >> backend/requirements.txt
```

**backend/app/main.py에 추가**:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

# Sentry 초기화
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN_HERE",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production",
)
```

#### 3. Frontend 통합
```bash
cd /home/user/webapp/frontend

# Sentry SDK 설치
npm install --save @sentry/react @sentry/tracing
```

**frontend/src/main.tsx에 추가**:
```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN_HERE",
  integrations: [new Sentry.BrowserTracing()],
  tracesSampleRate: 1.0,
  environment: "production",
});
```

#### 4. 배포 및 테스트
```bash
# 로컬에서 커밋
git add .
git commit -m "feat: Add Sentry error tracking integration"
git push origin main

# 서버에서 배포
cd /root/uvis
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

**결과 확인**:
- Sentry 대시보드에서 에러 실시간 모니터링
- 에러 알림 이메일/Slack 수신

---

### 8️⃣ 데이터베이스 인덱스 최적화 (2시간)

**목표**: 자주 사용하는 쿼리의 성능 개선

**현재 상태 분석**:
```bash
cd /root/uvis

# 느린 쿼리 확인
docker exec -it uvis-db psql -U <DB_USER> -d uvisdb

-- 실행:
SELECT 
    query,
    calls,
    total_time / 1000 as total_seconds,
    mean_time / 1000 as avg_seconds
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
```

**인덱스 추가 예시**:
```sql
-- 주문 조회 최적화
CREATE INDEX IF NOT EXISTS idx_orders_status 
ON orders(status);

CREATE INDEX IF NOT EXISTS idx_orders_created_at 
ON orders(created_at DESC);

-- 배차 조회 최적화
CREATE INDEX IF NOT EXISTS idx_dispatches_date 
ON dispatches(dispatch_date);

CREATE INDEX IF NOT EXISTS idx_dispatches_vehicle 
ON dispatches(vehicle_id);

-- 차량 조회 최적화
CREATE INDEX IF NOT EXISTS idx_vehicles_status 
ON vehicles(status);
```

**결과 확인**:
```sql
-- 인덱스 사용 확인
EXPLAIN ANALYZE 
SELECT * FROM orders WHERE status = '배차대기' LIMIT 10;
```

---

### 9️⃣ 오프사이트 백업 설정 (3시간)

**목표**: 서버 장애 시에도 데이터를 안전하게 보관

**옵션 1: AWS S3 백업**
```bash
# AWS CLI 설치
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# AWS 자격증명 설정
aws configure

# S3 버킷 생성
aws s3 mb s3://uvis-backups-$(date +%Y)

# 백업 스크립트 업데이트
nano /root/uvis/scripts/auto_backup.sh
```

**스크립트에 추가**:
```bash
# S3 업로드
echo "☁️ S3에 백업 업로드 중..."
aws s3 cp "$BACKUP_DIR/backup_$DATE.sql" \
    s3://uvis-backups-2026/ \
    --storage-class STANDARD_IA

aws s3 cp "$BACKUP_DIR/config_backup_$DATE_SHORT.tar.gz" \
    s3://uvis-backups-2026/
```

**옵션 2: Google Cloud Storage**
```bash
# gcloud CLI 설치
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 인증
gcloud auth login

# 버킷 생성
gsutil mb gs://uvis-backups-2026

# 백업 업로드
gsutil cp backup_*.sql gs://uvis-backups-2026/
```

---

## 🔍 모니터링 및 유지보수

### 일일 체크리스트
```bash
cd /root/uvis

# 1. 시스템 상태
docker ps

# 2. 디스크 사용량
df -h | grep /dev/sda

# 3. API 응답 시간
bash scripts/performance_monitor.sh

# 4. 백업 확인
ls -lh backups/ | tail -5

# 5. 로그 확인
docker logs uvis-backend --tail 50 | grep -i error
```

### 주간 체크리스트
```bash
# 1. AB Test 통계 분석
curl -s http://localhost:8000/api/ml-dispatch/ab-test/stats | jq '.'

# 2. AI 비용 확인
curl -s http://localhost:8000/api/v1/ai-usage/cost-summary | jq '.'

# 3. 백업 무결성 테스트
tar -tzf backups/config_backup_$(date +%Y%m%d).tar.gz | head

# 4. 보안 업데이트
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 성공 지표

### KPI 정의
```
✅ 시스템 가용성: 99.9% 이상
✅ API 응답 시간: 평균 20ms 이하
✅ 배차 성공률: 95% 이상
✅ ML 배차 정확도: 90% 이상 (치유 Control 그룹 대비)
✅ 에러율: 1% 이하
✅ 백업 성공률: 100%
```

### 모니터링 대시보드
```
📈 실시간 모니터링:
- Grafana: http://139.150.11.99:3000 (설정 시)
- Sentry: https://sentry.io/dashboard (설정 시)
- AB Test: http://139.150.11.99/ml-dispatch/ab-test

📊 주요 지표:
- API 응답 시간
- 메모리/CPU 사용률
- 배차 성공률
- AI 비용
- 에러 발생 횟수
```

---

## 🎓 학습 리소스

### 문서
- `BACKUP_GUIDE.md` - 백업 및 복구
- `ML_DISPATCH_AUTH_REMOVAL.md` - ML Dispatch 인증
- `SERVER_DEPLOYMENT_COMMANDS.md` - 서버 배포
- `FINAL_SYSTEM_SUMMARY.md` - 시스템 요약

### API 문서
- Swagger UI: http://139.150.11.99:8000/docs
- ReDoc: http://139.150.11.99:8000/redoc

### GitHub
- 저장소: https://github.com/rpaakdi1-spec/3-
- Issues: https://github.com/rpaakdi1-spec/3-/issues
- Wiki: https://github.com/rpaakdi1-spec/3-/wiki

---

## ❓ 문제 해결

### Frontend 빌드 실패
```bash
cd /home/user/webapp/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Backend 오류
```bash
cd /root/uvis
docker logs uvis-backend --tail 100
docker-compose -f docker-compose.prod.yml restart backend
```

### Database 연결 실패
```bash
docker exec -it uvis-db psql -U <DB_USER> -d uvisdb -c "\conninfo"
```

### Redis 문제
```bash
docker exec -it uvis-redis redis-cli ping
docker-compose -f docker-compose.prod.yml restart redis
```

---

## 📞 지원

**긴급 이슈**:
1. 로그 확인: `docker logs <container-name> --tail 100`
2. 컨테이너 재시작: `docker-compose restart <service>`
3. GitHub Issue 생성: https://github.com/rpaakdi1-spec/3-/issues

**계획된 유지보수**:
- 매주 일요일 새벽 2-3시 (백업 시간)
- 필요 시 추가 유지보수 공지

---

## 🎯 최종 목표

### Phase 3 완료 ✅
- [x] Frontend 통합
- [x] ML Dispatch 파일럿 롤아웃
- [x] 자동 백업 시스템
- [x] 성능 모니터링

### Phase 4 목표 (진행 중)
- [ ] AI API 키 설정
- [ ] AB Test UI 활성화
- [ ] ML Dispatch 확대 (10% → 100%)
- [ ] 에러 추적 시스템
- [ ] 오프사이트 백업

### Phase 5 계획 (미래)
- [ ] Mobile App 개발
- [ ] 고급 분석 대시보드
- [ ] 자동화된 알림 시스템
- [ ] 멀티 테넌트 지원

---

**시작할 준비가 되셨나요?**

**추천 순서**:
1. ✅ GitHub 푸시 (5분)
2. ✅ AI API 키 설정 (15분)
3. ✅ AB Test UI 활성화 (30분)
4. 📊 ML Dispatch 모니터링 (계속)

**문의사항**:
- GitHub Issues: https://github.com/rpaakdi1-spec/3-/issues
- Email: [프로젝트 관리자 이메일]

---

**생성일**: 2026-02-02  
**작성자**: AI Assistant  
**버전**: 1.0

---

**프로젝트를 성공적으로 운영하시길 바랍니다! 🚀**
