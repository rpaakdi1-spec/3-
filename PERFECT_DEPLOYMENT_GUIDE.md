# 🚀 완벽한 프로덕션 배포 가이드

**최종 업데이트:** 2026-01-28  
**작성자:** GenSpark AI Developer  
**배포 환경:** Gabia 서버 (139.150.11.99)

---

## 📋 목차

1. [배포 전 확인사항](#배포-전-확인사항)
2. [완전 자동 배포](#완전-자동-배포)
3. [수동 단계별 배포](#수동-단계별-배포)
4. [배포 후 검증](#배포-후-검증)
5. [문제 해결 가이드](#문제-해결-가이드)
6. [롤백 절차](#롤백-절차)

---

## 배포 전 확인사항

### ✅ 필수 사항

1. **서버 접속 정보**
   - IP: `139.150.11.99`
   - User: `root`
   - SSH 키 또는 비밀번호 준비

2. **GitHub 저장소**
   - Repository: `https://github.com/rpaakdi1-spec/3-`
   - Branch: `genspark_ai_developer`
   - Latest Commit: 최신 커밋 확인

3. **환경변수 설정**
   - `.env` 파일에 모든 필수 값 설정
   - 특히 `NAVER_MAP_CLIENT_SECRET` 확인

4. **Docker 및 Docker Compose 설치 확인**
   ```bash
   docker --version
   docker-compose --version
   ```

---

## 완전 자동 배포

### 🎯 원클릭 배포 (권장)

서버에 SSH 접속 후 다음 명령어 실행:

```bash
cd /root/uvis && \
git fetch origin genspark_ai_developer && \
git reset --hard origin/genspark_ai_developer && \
chmod +x deploy-production-final.sh && \
./deploy-production-final.sh
```

### 📊 예상 소요 시간

| 단계 | 소요 시간 |
|-----|---------|
| 코드 동기화 | 10초 |
| 환경 설정 | 30초 |
| Docker 캐시 클리어 | 1분 |
| Backend 빌드 | 5-8분 |
| Frontend 빌드 | 8-12분 |
| 컨테이너 시작 | 1-2분 |
| Health Check | 30초 |
| **총 소요 시간** | **16-24분** |

### 📝 배포 스크립트 주요 기능

1. ✅ 자동 백업 (DB, .env)
2. ✅ 최신 코드 동기화
3. ✅ 환경변수 검증
4. ✅ Docker 캐시 완전 클리어
5. ✅ 무중단 이미지 빌드
6. ✅ 자동 Health Check
7. ✅ 실패 시 자동 로그 출력
8. ✅ 배포 완료 보고서 생성

---

## 수동 단계별 배포

자동 배포가 실패하거나 세밀한 제어가 필요한 경우:

### Step 1: 서버 접속 및 백업

```bash
# SSH 접속
ssh root@139.150.11.99

# 백업 디렉토리 생성
mkdir -p /root/backups
cd /root/uvis

# 현재 상태 백업
docker exec uvis-db pg_dump -U uvis_user uvis_db > /root/backups/db-backup-$(date +%Y%m%d-%H%M%S).sql
cp .env /root/backups/.env-backup-$(date +%Y%m%d-%H%M%S)
```

### Step 2: 최신 코드 동기화

```bash
cd /root/uvis

# 로컬 변경사항 stash
git stash

# 최신 코드 가져오기
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer

# 현재 커밋 확인
git log -1 --oneline
```

### Step 3: 환경변수 설정

```bash
# .env 파일 확인
cat .env

# 필수 변수 확인
grep "NAVER_MAP_CLIENT_ID" .env
grep "DATABASE_URL" .env
grep "SECRET_KEY" .env
```

### Step 4: 기존 컨테이너 중지

```bash
cd /root/uvis
docker-compose -f docker-compose.prod.yml down
```

### Step 5: Docker 캐시 완전 클리어

```bash
# 시스템 정리
docker system prune -f

# 기존 이미지 제거
docker rmi uvis-backend uvis-frontend || true

# 확인
docker images | grep uvis
```

### Step 6: 이미지 빌드

```bash
# Backend 빌드 (5-8분 소요)
docker-compose -f docker-compose.prod.yml build --no-cache --pull backend

# Frontend 빌드 (8-12분 소요)
docker-compose -f docker-compose.prod.yml build --no-cache --pull frontend

# 다른 서비스 빌드
docker-compose -f docker-compose.prod.yml build --no-cache db redis nginx
```

### Step 7: 서비스 시작

```bash
# 모든 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

### Step 8: Health Check

```bash
# 30초 대기
sleep 30

# Health Check
curl -s http://localhost:8000/health | python3 -m json.tool

# 로그 확인
docker-compose -f docker-compose.prod.yml logs --tail=30 backend
docker-compose -f docker-compose.prod.yml logs --tail=10 frontend
```

---

## 배포 후 검증

### 1. 컨테이너 상태 확인

```bash
docker-compose -f docker-compose.prod.yml ps
```

**기대 결과:**
```
NAME            STATUS
uvis-backend    Up (healthy)
uvis-db         Up (healthy)
uvis-frontend   Up (healthy)
uvis-nginx      Up (healthy)
uvis-redis      Up (healthy)
```

### 2. Backend Health Check

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

**기대 결과:**
```json
{
  "status": "healthy",
  "app_name": "Cold Chain Dispatch System",
  "environment": "production"
}
```

### 3. 외부 접속 테스트

브라우저에서 다음 URL 테스트:

| URL | 설명 | 기대 결과 |
|-----|------|----------|
| `http://139.150.11.99` | Frontend | 로그인 페이지 표시 |
| `http://139.150.11.99:8000/docs` | API 문서 | Swagger UI 표시 |
| `http://139.150.11.99:8000/health` | Health Check | JSON 응답 |

### 4. 로그인 테스트

**테스트 계정:**
- **관리자:** `admin@example.com` / `admin123`
- **드라이버 1:** `driver1` / `password123`
- **드라이버 2:** `driver2` / `password123`

### 5. 주요 기능 테스트

- [ ] 로그인/로그아웃
- [ ] 대시보드 조회
- [ ] 차량 목록 조회
- [ ] 주문 생성
- [ ] 배차 생성
- [ ] 실시간 모니터링
- [ ] UVIS GPS 연동

---

## 문제 해결 가이드

### ❌ 문제: Backend 컨테이너가 unhealthy

**증상:**
```bash
uvis-backend   Up (unhealthy)
```

**해결 방법:**

1. **로그 확인**
   ```bash
   docker-compose -f docker-compose.prod.yml logs --tail=100 backend
   ```

2. **일반적인 에러 및 해결책**

   | 에러 메시지 | 원인 | 해결 방법 |
   |-----------|------|----------|
   | `PydanticUndefinedAnnotation` | Forward reference 문제 | `from __future__ import annotations` 추가 |
   | `ModuleNotFoundError` | Import 경로 오류 | Import 경로 수정 |
   | `PermissionError` | 파일 권한 문제 | 경로를 `/app/` 로 수정 |
   | `Database connection failed` | DB 미준비 | `docker-compose restart db backend` |

3. **컨테이너 재시작**
   ```bash
   docker-compose -f docker-compose.prod.yml restart backend
   sleep 30
   docker-compose -f docker-compose.prod.yml logs --tail=30 backend
   ```

### ❌ 문제: Frontend 빌드 실패

**증상:**
```
npm ci requires a package-lock.json
```

**해결 방법:**

`frontend/Dockerfile.prod` 수정:
```dockerfile
# Before
RUN npm ci

# After
RUN npm install --prefer-offline --no-audit
```

### ❌ 문제: 환경변수가 로드되지 않음

**증상:**
```
NAVER_MAP_CLIENT_ID is required
```

**해결 방법:**

1. `.env` 파일 확인
   ```bash
   cat .env | grep NAVER_MAP
   ```

2. Docker Compose 재시작
   ```bash
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d
   ```

### ❌ 문제: Port 충돌

**증상:**
```
bind: address already in use
```

**해결 방법:**

1. 사용 중인 포트 확인
   ```bash
   netstat -tlnp | grep :8000
   netstat -tlnp | grep :3000
   ```

2. 프로세스 종료
   ```bash
   kill -9 <PID>
   ```

---

## 롤백 절차

배포가 실패하거나 문제가 발생한 경우:

### 1. 이전 버전으로 롤백

```bash
cd /root/uvis

# 이전 커밋으로 되돌리기
git log --oneline -10  # 이전 커밋 해시 확인
git reset --hard <COMMIT_HASH>

# 재배포
./deploy-production-final.sh
```

### 2. 데이터베이스 복원

```bash
# 백업 파일 확인
ls -lh /root/backups/db-backup-*.sql

# 복원
docker exec -i uvis-db psql -U uvis_user uvis_db < /root/backups/db-backup-YYYYMMDD-HHMMSS.sql
```

### 3. 환경변수 복원

```bash
cp /root/backups/.env-backup-YYYYMMDD-HHMMSS /root/uvis/.env
```

---

## 🎓 Best Practices

### 배포 전

- [ ] 로컬 환경에서 충분히 테스트
- [ ] GitHub에 최신 코드 푸시 확인
- [ ] PR 리뷰 완료
- [ ] 데이터베이스 백업 완료

### 배포 중

- [ ] 배포 시간 공지 (유지보수 시간)
- [ ] 배포 로그 모니터링
- [ ] Health Check 통과 확인
- [ ] 에러 발생 시 즉시 롤백 준비

### 배포 후

- [ ] 전체 기능 테스트
- [ ] 로그 모니터링 (최소 30분)
- [ ] 성능 모니터링
- [ ] 사용자 피드백 수집

---

## 📞 지원 및 문의

**배포 관련 문제:**
- GitHub Issues: https://github.com/rpaakdi1-spec/3-/issues
- 담당자: GenSpark AI Developer

**긴급 연락:**
- 서버 다운: 즉시 롤백 수행
- 데이터 손실: 백업에서 복구

---

## 📚 추가 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [React 문서](https://react.dev/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)

---

**배포 성공을 기원합니다! 🚀**
