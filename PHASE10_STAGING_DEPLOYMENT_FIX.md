# Phase 10 스테이징 배포 문제 해결 가이드

## 🚨 발생한 문제

### 문제 1: Unstaged Changes
```bash
error: cannot pull with rebase: You have unstaged changes.
error: Please commit or stash them.
```
**원인**: frontend 디렉토리에 커밋되지 않은 변경사항이 있음

### 문제 2: 디렉토리 위치
```bash
cd: backend: No such file or directory
```
**원인**: 현재 `/root/uvis/frontend`에 있는데, `backend` 디렉토리는 `/root/uvis/backend`에 있음

### 문제 3: 환경 변수 누락
```bash
required variable DB_PASSWORD is missing a value: Database password required
```
**원인**: `.env` 파일이 없거나 `DB_PASSWORD`가 설정되지 않음

---

## ✅ 해결 방법

### 단계별 해결 가이드

#### 1️⃣ 프로젝트 루트로 이동
```bash
# 현재 위치 확인
pwd
# 출력: /root/uvis/frontend

# 프로젝트 루트로 이동
cd /root/uvis

# 확인
pwd
# 출력: /root/uvis
```

#### 2️⃣ Git 변경사항 처리
```bash
# 변경사항 확인
git status

# 옵션 A: 변경사항을 임시 저장 (권장)
git stash

# 또는 옵션 B: 변경사항을 커밋
git add .
git commit -m "temp: Save changes before Phase 10 deployment"
```

#### 3️⃣ 최신 코드 가져오기
```bash
# main 브랜치 최신 코드 가져오기
git pull origin main

# 변경사항 확인
git log --oneline -5
# Phase 10 커밋이 보여야 함: 507bb1d, 43729e5 등
```

#### 4️⃣ 환경 변수 설정

##### 4-1. .env 파일 확인
```bash
# .env 파일 존재 여부 확인
ls -la .env

# .env 파일 내용 확인
cat .env | grep -E "DB_PASSWORD|DB_HOST|DB_NAME"
```

##### 4-2. .env 파일이 없거나 불완전한 경우
```bash
# .env 파일 편집
vi .env
```

아래 내용을 추가/수정하세요:

```env
# =================================
# Database Configuration
# =================================
DB_HOST=db
DB_PORT=5432
DB_NAME=uvis_db
DB_USER=uvis_user
DB_PASSWORD=YourSecurePassword123!  # 안전한 비밀번호로 변경

# =================================
# JWT Configuration
# =================================
JWT_SECRET_KEY=YourJWTSecretKey123!  # 안전한 시크릿 키로 변경
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# =================================
# CORS Configuration
# =================================
ALLOWED_ORIGINS=http://localhost:3000,http://139.150.11.99:3000,http://139.150.11.99

# =================================
# Environment
# =================================
ENVIRONMENT=staging
DEBUG=False

# =================================
# API Configuration
# =================================
API_V1_STR=/api/v1
PROJECT_NAME="UVIS - Unified Vehicle Intelligence System"

# =================================
# Redis (if using)
# =================================
REDIS_HOST=redis
REDIS_PORT=6379

# =================================
# Email (if configured)
# =================================
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your_email@gmail.com
# SMTP_PASSWORD=your_app_password
```

**⚠️ 중요**: 
- `DB_PASSWORD`를 안전한 비밀번호로 변경하세요
- `JWT_SECRET_KEY`를 안전한 시크릿 키로 변경하세요
- 프로덕션 환경에서는 절대 기본값을 사용하지 마세요

#### 5️⃣ 데이터베이스 마이그레이션

##### 5-1. 백엔드 디렉토리로 이동
```bash
cd /root/uvis/backend
```

##### 5-2. Alembic 마이그레이션 실행
```bash
# Phase 10 테이블 생성 (dispatch_rules, rule_execution_logs)
docker-compose run --rm backend alembic upgrade head

# 또는 Docker를 사용하지 않는 경우
alembic upgrade head
```

**예상 출력**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade xxx -> yyy, add_dispatch_rules_tables
```

##### 5-3. 마이그레이션 확인
```bash
# 현재 리비전 확인
docker-compose run --rm backend alembic current

# 마이그레이션 히스토리 확인
docker-compose run --rm backend alembic history
```

#### 6️⃣ Docker 컨테이너 재시작

##### 6-1. 프로젝트 루트로 돌아가기
```bash
cd /root/uvis
```

##### 6-2. 기존 컨테이너 중지
```bash
docker-compose down
```

##### 6-3. 새로 빌드 및 시작
```bash
# 이미지 재빌드 및 컨테이너 시작
docker-compose up -d --build

# 또는 백그라운드 로그 확인하며 시작
docker-compose up --build
```

**예상 출력**:
```
Building backend
[+] Building 45.2s (18/18) FINISHED
...
Creating uvis_db_1       ... done
Creating uvis_redis_1    ... done
Creating uvis_backend_1  ... done
Creating uvis_frontend_1 ... done
```

#### 7️⃣ 배포 확인

##### 7-1. 컨테이너 상태 확인
```bash
docker-compose ps
```

**예상 출력**:
```
       Name                      Command               State           Ports
----------------------------------------------------------------------------------
uvis_backend_1    uvicorn main:app --host 0. ...   Up      0.0.0.0:8000->8000/tcp
uvis_db_1         docker-entrypoint.sh postgres    Up      5432/tcp
uvis_frontend_1   docker-entrypoint.sh /bin/ ...   Up      0.0.0.0:3000->3000/tcp
uvis_redis_1      docker-entrypoint.sh redis ...   Up      6379/tcp
```

모든 컨테이너가 **Up** 상태여야 합니다.

##### 7-2. 백엔드 로그 확인
```bash
# 최근 50줄 로그 확인
docker-compose logs backend --tail=50

# 실시간 로그 확인
docker-compose logs -f backend
```

**정상 로그 예시**:
```
backend_1   | INFO:     Started server process [1]
backend_1   | INFO:     Waiting for application startup.
backend_1   | INFO:     Application startup complete.
backend_1   | INFO:     Uvicorn running on http://0.0.0.0:8000
```

##### 7-3. API 엔드포인트 테스트

**Health Check**:
```bash
curl http://localhost:8000/health
# 또는
curl http://139.150.11.99:8000/health
```

**Swagger UI**:
```bash
curl -I http://localhost:8000/docs
# 또는 브라우저에서
# http://139.150.11.99:8000/docs
```

**Phase 10 API 테스트**:
```bash
# 규칙 목록 조회
curl http://localhost:8000/api/v1/dispatch-rules

# Swagger에서 테스트 (권장)
# http://139.150.11.99:8000/docs#/dispatch-rules
```

##### 7-4. 프론트엔드 확인
```bash
# 프론트엔드 로그 확인
docker-compose logs frontend --tail=20

# 브라우저에서 접속
# http://139.150.11.99:3000
```

##### 7-5. 데이터베이스 테이블 확인
```bash
# PostgreSQL에 접속
docker-compose exec db psql -U uvis_user -d uvis_db

# 테이블 목록 확인
\dt

# dispatch_rules 테이블 구조 확인
\d dispatch_rules

# rule_execution_logs 테이블 구조 확인
\d rule_execution_logs

# 나가기
\q
```

**예상 출력**:
```
                 List of relations
 Schema |           Name            | Type  |   Owner   
--------+---------------------------+-------+-----------
 public | alembic_version          | table | uvis_user
 public | dispatch_rules           | table | uvis_user
 public | rule_execution_logs      | table | uvis_user
 public | orders                   | table | uvis_user
 ...
```

---

## 🚀 빠른 배포 스크립트

전체 배포를 한 번에 실행하려면 아래 명령어를 복사해서 실행하세요:

```bash
#!/bin/bash

# Phase 10 스테이징 배포 스크립트

echo "=========================================="
echo "Phase 10 스테이징 배포 시작"
echo "=========================================="

# 1. 프로젝트 루트로 이동
cd /root/uvis
echo "✓ 프로젝트 루트로 이동: $(pwd)"

# 2. Git 변경사항 stash
echo "✓ Git 변경사항 저장 중..."
git stash

# 3. 최신 코드 가져오기
echo "✓ 최신 코드 가져오기..."
git pull origin main

# 4. .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. 생성해주세요."
    exit 1
fi

if ! grep -q "DB_PASSWORD=" .env; then
    echo "⚠️  DB_PASSWORD가 .env에 설정되지 않았습니다."
    exit 1
fi

echo "✓ .env 파일 확인 완료"

# 5. 데이터베이스 마이그레이션
echo "✓ 데이터베이스 마이그레이션 실행..."
cd backend
docker-compose run --rm backend alembic upgrade head
cd ..

# 6. Docker 재시작
echo "✓ Docker 컨테이너 재시작..."
docker-compose down
docker-compose up -d --build

# 7. 컨테이너 시작 대기
echo "✓ 컨테이너 시작 대기 (30초)..."
sleep 30

# 8. 상태 확인
echo "=========================================="
echo "배포 결과 확인"
echo "=========================================="

echo ""
echo "컨테이너 상태:"
docker-compose ps

echo ""
echo "백엔드 로그 (최근 20줄):"
docker-compose logs backend --tail=20

echo ""
echo "API Health Check:"
curl -s http://localhost:8000/health || echo "❌ API 응답 없음"

echo ""
echo "=========================================="
echo "배포 완료!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "1. Swagger UI 확인: http://139.150.11.99:8000/docs"
echo "2. 프론트엔드 확인: http://139.150.11.99:3000"
echo "3. Phase 10 규칙 페이지: http://139.150.11.99:3000/dispatch-rules"
echo ""
```

스크립트 실행:
```bash
# 스크립트 저장
vi /tmp/deploy_phase10.sh
# 위 내용 복사/붙여넣기

# 실행 권한 부여
chmod +x /tmp/deploy_phase10.sh

# 실행
/tmp/deploy_phase10.sh
```

---

## 🔍 문제 해결 (Troubleshooting)

### 문제: Docker 이미지 빌드 실패
```bash
# 캐시 없이 다시 빌드
docker-compose build --no-cache backend

# 또는 전체 재빌드
docker-compose down -v
docker-compose up -d --build
```

### 문제: 포트 충돌
```bash
# 포트 사용 확인
netstat -tuln | grep -E "3000|8000|5432"

# 기존 프로세스 종료
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:3000 | xargs kill -9
```

### 문제: 데이터베이스 연결 실패
```bash
# 데이터베이스 컨테이너 확인
docker-compose logs db --tail=50

# 데이터베이스 재시작
docker-compose restart db

# 연결 테스트
docker-compose exec backend python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://uvis_user:password@db:5432/uvis_db'); print('Connected!' if engine.connect() else 'Failed')"
```

### 문제: 마이그레이션 실패
```bash
# 현재 리비전 확인
docker-compose exec backend alembic current

# 마이그레이션 강제 실행
docker-compose exec backend alembic upgrade head --sql

# 마이그레이션 롤백 (필요시)
docker-compose exec backend alembic downgrade -1
```

### 문제: 프론트엔드 빌드 실패
```bash
# 프론트엔드 컨테이너 로그 확인
docker-compose logs frontend

# 의존성 재설치
docker-compose exec frontend npm install --legacy-peer-deps

# 재시작
docker-compose restart frontend
```

---

## 📋 배포 후 체크리스트

### 1. 백엔드 확인 ✅
- [ ] 컨테이너가 실행 중 (`docker-compose ps`)
- [ ] API Health Check 성공 (`/health`)
- [ ] Swagger UI 접근 가능 (`/docs`)
- [ ] Phase 10 API 응답 확인 (`/api/v1/dispatch-rules`)

### 2. 데이터베이스 확인 ✅
- [ ] dispatch_rules 테이블 생성됨
- [ ] rule_execution_logs 테이블 생성됨
- [ ] 기존 데이터 유지됨

### 3. 프론트엔드 확인 ✅
- [ ] 프론트엔드 접근 가능 (`http://139.150.11.99:3000`)
- [ ] 로그인 가능
- [ ] 사이드바에 "스마트 배차 규칙" 메뉴 표시
- [ ] `/dispatch-rules` 페이지 접근 가능
- [ ] Visual Rule Builder 동작 확인

### 4. Phase 10 기능 확인 ✅
- [ ] 규칙 생성 가능
- [ ] 규칙 목록 조회 가능
- [ ] Visual Rule Builder 작동
- [ ] 템플릿 갤러리 열림
- [ ] 규칙 테스트 다이얼로그 작동
- [ ] 규칙 활성화/비활성화 가능

---

## 🎯 최종 확인 명령어

```bash
# 전체 상태 한 번에 확인
cd /root/uvis

echo "=== Git 상태 ==="
git log --oneline -3

echo ""
echo "=== Docker 상태 ==="
docker-compose ps

echo ""
echo "=== API Health ==="
curl -s http://localhost:8000/health | jq .

echo ""
echo "=== 데이터베이스 테이블 ==="
docker-compose exec -T db psql -U uvis_user -d uvis_db -c "\dt" | grep -E "dispatch_rules|rule_execution"

echo ""
echo "=== Phase 10 API ==="
curl -s http://localhost:8000/api/v1/dispatch-rules | jq . | head -20

echo ""
echo "=== 배포 완료! ==="
echo "Swagger UI: http://139.150.11.99:8000/docs"
echo "Frontend: http://139.150.11.99:3000"
echo "Phase 10: http://139.150.11.99:3000/dispatch-rules"
```

---

## 📞 추가 도움말

### 로그 실시간 모니터링
```bash
# 모든 컨테이너 로그
docker-compose logs -f

# 특정 컨테이너만
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 컨테이너 내부 접속
```bash
# 백엔드 컨테이너 접속
docker-compose exec backend bash

# 데이터베이스 접속
docker-compose exec db psql -U uvis_user -d uvis_db

# 프론트엔드 컨테이너 접속
docker-compose exec frontend sh
```

### 디스크 공간 정리
```bash
# 사용하지 않는 Docker 이미지/컨테이너 정리
docker system prune -a

# 볼륨 포함 전체 정리 (주의!)
docker system prune -a --volumes
```

---

## 📝 문서 작성
- **작성일**: 2026-02-08
- **버전**: 1.0
- **Phase**: Phase 10 Staging Deployment
- **상태**: Ready for Use

문제가 계속되면 로그를 확인하고 이 가이드를 참고하세요!
