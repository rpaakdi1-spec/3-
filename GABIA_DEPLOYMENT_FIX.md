# Gabia Cloud 배포 수정사항

## 서버 정보
- **서버명**: Server-s1uvis
- **공인 IP**: 139.150.11.99
- **사설 IP**: 192.168.0.143
- **OS**: Rocky Linux 8.10
- **사양**: 2vCore CPU, 4GB RAM, 100GB SSD
- **로그인**: root / igG5v@iJ (임시 비밀번호)

## 수정된 파일 목록

### 1. Frontend Dockerfile.prod
**문제점:**
- `npm ci --only=production` 사용 시 devDependencies 누락
- TypeScript, Vite 등 빌드 도구가 devDependencies에 있어 빌드 실패
- 환경 변수 미설정

**수정사항:**
```dockerfile
# 변경 전
RUN npm ci --only=production

# 변경 후
RUN npm ci  # 모든 dependencies 설치 (devDependencies 포함)

# 환경 변수 추가
ARG REACT_APP_API_URL=http://139.150.11.99:8000
ARG REACT_APP_WS_URL=ws://139.150.11.99:8000/ws
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL
```

### 2. Backend requirements.txt
**문제점:**
- aiosmtplib==3.0.1과 fastapi-mail==1.4.1 의존성 충돌

**수정사항:**
```txt
# 변경 전
aiosmtplib==3.0.1

# 변경 후
aiosmtplib==2.0.2  # fastapi-mail과 호환
```

### 3. Docker 데몬 설정
**문제점:**
- Docker 컨테이너 내부에서 apt-get 타임아웃
- DNS 해석 실패

**수정사항:**
```json
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 4. docker-compose.yml
**문제점:**
- 개발 모드 설정 (target: development)
- Dockerfile 경로가 Dockerfile.prod가 아닌 Dockerfile 참조

**수정사항:**
- 프로덕션 모드로 전환
- 모든 서비스에서 Dockerfile.prod 사용
- 환경 변수 설정
- Health check 추가
- 네트워크 설정

## 배포 명령어

### 1. 준비 작업 (서버에서 실행)
```bash
# Docker Compose 설치 확인
docker-compose --version

# 프로젝트 디렉토리로 이동
cd /root/uvis

# 최신 코드 가져오기
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer

# 파일 확인
ls -la frontend/Dockerfile.prod
grep aiosmtplib backend/requirements.txt
```

### 2. 환경 설정
```bash
# .env 파일 생성
cat > .env << 'EOF'
# Database
POSTGRES_USER=uvis_user
POSTGRES_PASSWORD=uvis_password
POSTGRES_DB=uvis_db

# Backend
DATABASE_URL=postgresql://uvis_user:uvis_password@db:5432/uvis_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=gabia-uvis-production-secret-key-2026
ENVIRONMENT=production
DEBUG=false

# Frontend
REACT_APP_API_URL=http://139.150.11.99:8000
REACT_APP_WS_URL=ws://139.150.11.99:8000/ws
EOF
```

### 3. 빌드 및 실행
```bash
# 기존 컨테이너 정리
docker-compose down -v

# Docker 캐시 클리어
docker system prune -af

# 빌드 (15-20분 소요)
docker-compose build --no-cache

# 실행
docker-compose up -d

# 상태 확인
docker-compose ps
docker-compose logs --tail=50
```

### 4. 확인
```bash
# 컨테이너 상태
docker-compose ps

# Health check
curl http://localhost:8000/health
curl http://139.150.11.99:8000/health

# 로그 확인
docker-compose logs -f
```

## 예상 결과

### 컨테이너 목록 (5개)
```
NAME              IMAGE               STATUS
uvis-backend      uvis-backend        Up (healthy)
uvis-db           postgis/postgis     Up (healthy)
uvis-redis        redis:7-alpine      Up (healthy)
uvis-frontend     uvis-frontend       Up
uvis-nginx        nginx:alpine        Up
```

### 포트 매핑
- **80**: Nginx (메인 엔트리포인트)
- **3000**: Frontend (React)
- **8000**: Backend (FastAPI)
- **5432**: PostgreSQL
- **6379**: Redis

## 접속 URL

- 🌐 **Frontend**: http://139.150.11.99
- 📚 **API Docs**: http://139.150.11.99:8000/docs
- ❤️ **Health Check**: http://139.150.11.99:8000/health
- 📊 **Database**: postgresql://139.150.11.99:5432/uvis_db
- 🔴 **Redis**: redis://139.150.11.99:6379

## 테스트 계정

### 관리자
- **Email**: admin@example.com
- **Password**: admin123

### 드라이버
- **Username**: driver1
- **Password**: password123

## 문제 해결

### Frontend 빌드 실패
```bash
# Dockerfile.prod 확인
cat frontend/Dockerfile.prod | grep "npm ci"

# package-lock.json 존재 확인
ls -la frontend/package-lock.json

# 수동 빌드 테스트
docker build -f frontend/Dockerfile.prod -t test-frontend ./frontend
```

### Backend 빌드 실패
```bash
# requirements.txt 확인
grep aiosmtplib backend/requirements.txt

# 수동 빌드 테스트
docker build -f backend/Dockerfile.prod -t test-backend ./backend
```

### DNS/네트워크 문제
```bash
# Docker DNS 설정 확인
cat /etc/docker/daemon.json

# Docker 재시작
systemctl restart docker

# 네트워크 테스트
docker run --rm busybox ping -c 3 google.com
```

### 컨테이너 시작 실패
```bash
# 로그 확인
docker-compose logs backend
docker-compose logs frontend

# 개별 컨테이너 재시작
docker-compose restart backend
docker-compose restart frontend
```

## 모바일 앱 연결

### 설정 변경
모바일 앱의 `/mobile/.env` 파일:
```env
EXPO_PUBLIC_API_URL=http://139.150.11.99:8000
EXPO_PUBLIC_WS_URL=ws://139.150.11.99:8000/ws
```

### Expo 재시작
```bash
cd /home/user/webapp/mobile
npx expo start --clear
```

## 보안 강화 (배포 후)

### 1. 비밀번호 변경
```bash
passwd root
```

### 2. 방화벽 설정
```bash
# 가비아 보안 그룹에서 설정
# 인바운드: 22, 80, 443, 8000
# 아웃바운드: 모든 트래픽 허용
```

### 3. SSL 인증서 (선택)
```bash
# Let's Encrypt 설치
dnf install -y certbot python3-certbot-nginx

# 인증서 발급 (도메인 필요)
certbot --nginx -d your-domain.com
```

## 비용 정보

### 가비아 클라우드 Gen2
- **월 비용**: ₩75,350
- **연 비용**: ₩904,200
- **5년 비용**: ₩4,521,000
- **포함 사항**:
  - 2vCore CPU, 4GB RAM, 100GB SSD
  - 공인 IP 1개
  - 트래픽 4TB/월

### 비교 (5년 기준)
- **Hetzner CX22**: ₩390,000 (91% 저렴)
- **Oracle Cloud Free**: ₩0 (100% 절감)
- **가비아**: ₩4,521,000

## 다음 단계

1. ✅ 코드 수정 완료 (로컬)
2. ✅ GitHub에 푸시
3. ⏳ 서버에서 최신 코드 가져오기
4. ⏳ Docker 빌드 및 실행
5. ⏳ 접속 테스트
6. ⏳ 모바일 앱 연결
7. ⏳ 보안 설정

## 지원 연락처

- **가비아 고객센터**: 1544-4755
- **웹 콘솔**: https://console.gabiacloud.com/
- **문서**: https://customer.gabia.com/

---

**작성일**: 2026-01-28
**버전**: 1.0
**상태**: 준비 완료
