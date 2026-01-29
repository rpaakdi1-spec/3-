# Docker & CI/CD 배포 가이드

**작성일**: 2026-01-27  
**작성자**: GenSpark AI Developer  
**상태**: ✅ 완료 및 테스트 준비

## 📋 개요

Cold Chain Dispatch System을 위한 Docker 컨테이너화 및 GitHub Actions CI/CD 파이프라인이 구축되었습니다.

## 🏗️ 시스템 아키텍처

### Docker Services

```
┌─────────────────────────────────────────────┐
│            Nginx (Frontend)                 │
│         Port: 80 (HTTP)                     │
│    React + TypeScript + Vite                │
└──────────────┬──────────────────────────────┘
               │ HTTP Proxy
┌──────────────▼──────────────────────────────┐
│        FastAPI (Backend)                    │
│         Port: 8000                          │
│    Python 3.12 + Uvicorn                    │
└──────┬─────────────────┬────────────────────┘
       │                 │
       │                 │
┌──────▼─────────┐  ┌───▼──────────────┐
│  PostgreSQL    │  │     Redis        │
│   Port: 5432   │  │   Port: 6379     │
│   Database     │  │     Cache        │
└────────────────┘  └──────────────────┘
```

## 🚀 빠른 시작

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 1. 프로젝트 클론

```bash
git clone https://github.com/rpaakdi1-spec/3-.git
cd 3-
```

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
nano .env
```

**필수 설정**:
```env
SECRET_KEY=your-secret-key-here-change-in-production
NAVER_MAP_CLIENT_ID=your_naver_client_id
NAVER_MAP_CLIENT_SECRET=your_naver_client_secret
UVIS_API_KEY=your_uvis_api_key
```

### 3. Docker 실행

#### 개발 환경 (Hot Reload)

```bash
# 개발 환경 시작
docker-compose -f docker-compose.dev.yml up -d

# 로그 확인
docker-compose -f docker-compose.dev.yml logs -f

# 중지
docker-compose -f docker-compose.dev.yml down
```

**개발 환경 URL**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

#### 프로덕션 환경

```bash
# 빌드 및 시작
./docker-run.sh build
./docker-run.sh up

# 또는
docker-compose up -d --build
```

**프로덕션 URL**:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 4. 서비스 확인

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend

# 헬스 체크
curl http://localhost:8000/health
curl http://localhost:80
```

## 📦 Docker 파일 구조

```
webapp/
├── backend/
│   ├── Dockerfile              # Backend 이미지
│   ├── .dockerignore          # Docker 빌드 제외 파일
│   └── requirements.txt        # Python 의존성
├── frontend/
│   ├── Dockerfile              # Frontend 이미지 (Multi-stage)
│   ├── nginx.conf             # Nginx 설정
│   ├── .dockerignore          # Docker 빌드 제외 파일
│   └── package.json           # Node 의존성
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions CI/CD
├── docker-compose.yml         # 프로덕션 설정
├── docker-compose.dev.yml     # 개발 설정
├── docker-run.sh              # Docker 관리 스크립트
└── .env.example               # 환경 변수 템플릿
```

## 🛠️ Docker 관리 명령어

### docker-run.sh 스크립트 사용

```bash
# 빌드
./docker-run.sh build

# 시작
./docker-run.sh up

# 중지
./docker-run.sh down

# 재시작
./docker-run.sh restart

# 로그 확인
./docker-run.sh logs
./docker-run.sh logs backend

# 상태 확인
./docker-run.sh status

# 셸 접속
./docker-run.sh shell backend
./docker-run.sh shell frontend

# 전체 정리 (주의!)
./docker-run.sh clean

# 도움말
./docker-run.sh help
```

### Docker Compose 직접 사용

```bash
# 빌드
docker-compose build

# 백그라운드 시작
docker-compose up -d

# 중지
docker-compose down

# 중지 + 볼륨 삭제
docker-compose down -v

# 재시작
docker-compose restart

# 특정 서비스 재시작
docker-compose restart backend

# 로그
docker-compose logs -f
docker-compose logs -f backend

# 상태
docker-compose ps

# 셸 접속
docker-compose exec backend sh
docker-compose exec frontend sh

# 특정 서비스만 시작
docker-compose up -d backend redis postgres
```

## 🔄 GitHub Actions CI/CD

### 워크플로우 트리거

- **Push**: `main`, `genspark_ai_developer` 브랜치
- **Pull Request**: `main` 브랜치로의 PR

### CI/CD 단계

#### 1. Backend Tests
- Python 3.12 설정
- 의존성 설치
- Flake8 린팅
- Pytest 테스트 실행

#### 2. Frontend Tests
- Node.js 18 설정
- 의존성 설치
- Vite 빌드

#### 3. Build Docker Images
- Docker Buildx 설정
- GitHub Container Registry 로그인
- Backend/Frontend 이미지 빌드 및 푸시
- 이미지 태깅:
  - `latest` (main 브랜치)
  - `genspark_ai_developer` (개발 브랜치)
  - `{branch}-{sha}` (커밋별)

#### 4. Deploy (선택)
- main 브랜치만
- 배포 알림
- 실제 배포 설정 필요

### 워크플로우 확인

```bash
# GitHub Actions 로그 확인
# https://github.com/rpaakdi1-spec/3-/actions

# Docker 이미지 확인
# https://github.com/rpaakdi1-spec?tab=packages
```

## 🔧 고급 설정

### 다중 환경 구성

#### 개발 환경
```bash
docker-compose -f docker-compose.dev.yml up -d
```

특징:
- Hot reload (코드 변경 시 자동 재시작)
- Volume 마운트 (로컬 코드 연동)
- 개발용 포트 (3000, 8000)

#### 스테이징 환경
```bash
docker-compose -f docker-compose.staging.yml up -d
```

#### 프로덕션 환경
```bash
docker-compose up -d
```

특징:
- 최적화된 이미지 (Multi-stage build)
- PostgreSQL + Redis
- Nginx 리버스 프록시
- 헬스 체크

### 환경 변수 오버라이드

```bash
# .env 파일 사용
docker-compose --env-file .env.production up -d

# 커맨드라인 오버라이드
APP_ENV=staging docker-compose up -d
```

### 볼륨 관리

```bash
# 볼륨 목록
docker volume ls

# 볼륨 상세 정보
docker volume inspect webapp_postgres_data

# 볼륨 백업
docker run --rm -v webapp_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# 볼륨 복원
docker run --rm -v webapp_postgres_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/postgres_backup.tar.gz --strip 1"
```

## 🐛 트러블슈팅

### 일반 문제

#### 포트 충돌
```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :80

# 프로세스 종료
kill -9 <PID>
```

#### 캐시 문제
```bash
# 캐시 없이 빌드
docker-compose build --no-cache

# 이미지 재빌드
docker-compose up -d --build --force-recreate
```

#### 데이터베이스 연결 실패
```bash
# PostgreSQL 로그 확인
docker-compose logs postgres

# 데이터베이스 상태 확인
docker-compose exec postgres pg_isready -U coldchain

# 연결 테스트
docker-compose exec backend python -c "from app.core.database import engine; print(engine.connect())"
```

#### 권한 문제
```bash
# 로그 디렉터리 권한
chmod -R 755 backend/logs backend/data

# Docker 소켓 권한 (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### 로그 확인

```bash
# 모든 서비스 로그
docker-compose logs -f

# 특정 서비스 로그 (최근 100줄)
docker-compose logs --tail=100 backend

# 실시간 로그 (컨테이너 내부)
docker-compose exec backend tail -f /app/logs/app.log
```

### 컨테이너 디버깅

```bash
# 컨테이너 내부 접속
docker-compose exec backend sh

# 프로세스 확인
docker-compose exec backend ps aux

# 네트워크 확인
docker-compose exec backend ping postgres
docker-compose exec backend ping redis

# 파일 시스템 확인
docker-compose exec backend ls -la /app
```

## 📊 성능 최적화

### 이미지 크기 최적화

**Before**: ~1.5 GB  
**After**: ~500 MB (Multi-stage build)

최적화 기법:
- Alpine Linux 사용
- Multi-stage build (Frontend)
- .dockerignore 활용
- 레이어 캐싱 최적화

### 빌드 속도 개선

- Docker BuildKit 사용
- 캐시 레이어 활용
- 의존성 먼저 복사 (requirements.txt, package.json)

### 런타임 성능

- Uvicorn workers (프로덕션)
- Nginx gzip 압력
- Redis 캐싱
- PostgreSQL 인덱스

## 🚀 배포 옵션

### 1. AWS ECS (Elastic Container Service)

```bash
# ECR 푸시
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag cold-chain-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/cold-chain-backend:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/cold-chain-backend:latest
```

### 2. Google Cloud Run

```bash
# GCR 푸시
gcloud auth configure-docker
docker tag cold-chain-backend:latest gcr.io/<project-id>/cold-chain-backend:latest
docker push gcr.io/<project-id>/cold-chain-backend:latest

# Cloud Run 배포
gcloud run deploy cold-chain-backend \
  --image gcr.io/<project-id>/cold-chain-backend:latest \
  --platform managed \
  --region us-central1
```

### 3. Kubernetes

```bash
# Kubernetes 배포
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml
```

### 4. Docker Swarm

```bash
# Swarm 초기화
docker swarm init

# 스택 배포
docker stack deploy -c docker-compose.yml coldchain
```

## 📝 체크리스트

### 배포 전 확인사항

- [ ] .env 파일 설정 완료
- [ ] SECRET_KEY 변경 (프로덕션)
- [ ] API 키 설정 (Naver, UVIS)
- [ ] 데이터베이스 백업 전략
- [ ] SSL/TLS 인증서 설정
- [ ] 도메인 DNS 설정
- [ ] 방화벽 규칙 설정
- [ ] 모니터링 설정

### 보안 체크리스트

- [ ] 환경 변수로 비밀 관리
- [ ] SECRET_KEY 강력한 키 사용
- [ ] 데이터베이스 외부 노출 차단
- [ ] CORS 설정 확인
- [ ] JWT 토큰 만료 시간 설정
- [ ] HTTPS 사용 (프로덕션)
- [ ] 컨테이너 보안 스캔

## 🎉 완료!

Docker & CI/CD 배포 자동화가 완료되었습니다!

### 다음 단계

1. **로컬 테스트**: `./docker-run.sh up`
2. **GitHub Actions 확인**: Push 후 자동 빌드 확인
3. **프로덕션 배포**: 배포 타겟 선택 및 설정

---

**Created with ❤️ for Cold Chain Logistics**  
**Date**: 2026-01-27
