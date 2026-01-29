# 🚀 Oracle Cloud Free 배포 가이드

**시작일**: 2026-01-28  
**예상 비용**: $0/월 (완전 무료, 영구)  
**예상 소요 시간**: 30-60분

---

## 📋 목차
1. [Oracle Cloud 가입](#1-oracle-cloud-가입)
2. [VM 인스턴스 생성](#2-vm-인스턴스-생성)
3. [네트워크 설정](#3-네트워크-설정)
4. [애플리케이션 배포](#4-애플리케이션-배포)
5. [도메인 및 SSL 설정](#5-도메인-및-ssl-설정)
6. [모니터링 설정](#6-모니터링-설정)

---

## 1. Oracle Cloud 가입

### Step 1.1: 계정 생성
```
1. 브라우저에서 접속:
   https://www.oracle.com/cloud/free/

2. "Start for free" 또는 "무료 시작하기" 클릭

3. 필수 정보 입력:
   ✅ 이메일 주소
   ✅ 국가/지역: South Korea
   ✅ 이름
   
4. 이메일 인증 완료

5. 계정 정보 입력:
   ✅ Cloud Account Name (고유 이름)
   ✅ Home Region: South Korea Central (Seoul) 권장
      (또는 Japan Central (Tokyo) - 가까움)
   
6. 결제 정보 입력 (검증용, 청구되지 않음):
   ⚠️ 신용카드 필요 (본인 확인용)
   ⚠️ $1 임시 승인 후 취소됨
   ⚠️ 무료 티어 한도 내에서는 절대 청구 안됨
```

### Step 1.2: 가입 확인
```
✅ 이메일로 확인 링크 수신
✅ 계정 활성화 완료
✅ Oracle Cloud Console 접속 가능
   https://cloud.oracle.com/
```

---

## 2. VM 인스턴스 생성

### Step 2.1: VM 1 생성 (Backend + Database)

#### 콘솔 접속
```
1. Oracle Cloud Console 로그인
   https://cloud.oracle.com/

2. 좌측 메뉴 → "Compute" → "Instances" 클릭

3. "Create Instance" 클릭
```

#### 인스턴스 설정
```yaml
Name: coldchain-backend

Placement:
  ✅ Availability domain: AD-1 (기본값)

Image and Shape:
  Image: 
    ✅ "Change Image" 클릭
    ✅ Ubuntu 22.04 선택
    ✅ Canonical Ubuntu 22.04 (Latest)
  
  Shape:
    ✅ "Change Shape" 클릭
    ✅ VM.Standard.E2.1.Micro 선택
       - 1/8 OCPU (1 vCPU)
       - 1 GB RAM
       - Always Free 뱃지 확인!

Networking:
  ✅ Create new virtual cloud network (첫 VM)
  ✅ VCN Name: coldchain-vcn
  ✅ Subnet Name: coldchain-subnet
  ✅ Assign a public IPv4 address: 체크

Add SSH keys:
  ✅ Generate a key pair for me (권장)
     - Save Private Key 클릭하여 저장
     - 파일명: coldchain-backend.key
  또는
  ✅ Upload public key files (.pub 파일)

Boot volume:
  ✅ 기본값 (50 GB) - 충분함
  ✅ Use in-transit encryption: 체크 (보안)
```

#### 생성 완료
```
1. "Create" 버튼 클릭

2. 인스턴스 상태:
   Provisioning... → Running (약 1-2분)

3. Public IP 확인 및 복사:
   예: 132.145.XXX.XXX
```

### Step 2.2: VM 2 생성 (Frontend)

#### 같은 방식으로 생성
```yaml
Name: coldchain-frontend

Image and Shape:
  ✅ Ubuntu 22.04
  ✅ VM.Standard.E2.1.Micro (Always Free)

Networking:
  ✅ Select existing virtual cloud network
  ✅ VCN: coldchain-vcn (기존 VCN 선택)
  ✅ Subnet: coldchain-subnet
  ✅ Assign a public IPv4 address: 체크

SSH Keys:
  ✅ Generate a key pair
     - Save as: coldchain-frontend.key
```

### Step 2.3: VM IP 주소 확인
```
VM 1 (Backend):  132.145.XXX.XXX
VM 2 (Frontend): 132.145.YYY.YYY

⚠️ 이 IP 주소를 메모해두세요!
```

---

## 3. 네트워크 설정

### Step 3.1: 방화벽 규칙 설정 (Ingress Rules)

#### VCN Security List 설정
```
1. 좌측 메뉴 → "Networking" → "Virtual Cloud Networks"

2. "coldchain-vcn" 클릭

3. "Security Lists" → "Default Security List" 클릭

4. "Add Ingress Rules" 클릭

규칙 1 - HTTP:
  ✅ Source CIDR: 0.0.0.0/0
  ✅ IP Protocol: TCP
  ✅ Destination Port Range: 80
  ✅ Description: HTTP

규칙 2 - HTTPS:
  ✅ Source CIDR: 0.0.0.0/0
  ✅ IP Protocol: TCP
  ✅ Destination Port Range: 443
  ✅ Description: HTTPS

규칙 3 - Backend API:
  ✅ Source CIDR: 0.0.0.0/0
  ✅ IP Protocol: TCP
  ✅ Destination Port Range: 8000
  ✅ Description: Backend API

규칙 4 - WebSocket:
  ✅ Source CIDR: 0.0.0.0/0
  ✅ IP Protocol: TCP
  ✅ Destination Port Range: 8001
  ✅ Description: WebSocket

규칙 5 - Grafana (선택):
  ✅ Source CIDR: 0.0.0.0/0
  ✅ IP Protocol: TCP
  ✅ Destination Port Range: 3001
  ✅ Description: Grafana
```

### Step 3.2: OS 방화벽 설정 (SSH 접속 후)

이 부분은 Step 4에서 SSH 접속 후 진행합니다.

---

## 4. 애플리케이션 배포

### Step 4.1: SSH 접속 준비

#### Private Key 권한 설정
```bash
# Windows (Git Bash 또는 PowerShell)
icacls coldchain-backend.key /inheritance:r
icacls coldchain-backend.key /grant:r "%username%:R"

# Mac/Linux
chmod 400 coldchain-backend.key
chmod 400 coldchain-frontend.key
```

#### SSH 접속
```bash
# VM 1 (Backend) 접속
ssh -i coldchain-backend.key ubuntu@132.145.XXX.XXX

# 처음 접속 시 fingerprint 확인
# yes 입력
```

### Step 4.2: VM 1 (Backend) 설정

#### 시스템 업데이트
```bash
# 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y \
  git \
  curl \
  wget \
  vim \
  ufw \
  certbot
```

#### OS 방화벽 설정
```bash
# UFW 방화벽 설정
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 8001/tcp  # WebSocket

# 방화벽 활성화
sudo ufw --force enable

# 상태 확인
sudo ufw status
```

#### Docker 설치
```bash
# Docker 공식 설치 스크립트
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 로그아웃 후 재접속 (권한 적용)
exit
ssh -i coldchain-backend.key ubuntu@132.145.XXX.XXX

# Docker 버전 확인
docker --version
docker-compose --version
```

#### 프로젝트 클론
```bash
# 프로젝트 디렉토리 생성
sudo mkdir -p /opt/coldchain
sudo chown ubuntu:ubuntu /opt/coldchain

# Git 클론
cd /opt/coldchain
git clone https://github.com/rpaakdi1-spec/3-.git .

# 브랜치 확인
git branch -a
git checkout genspark_ai_developer
```

#### 환경 변수 설정
```bash
# .env 파일 생성
cd /opt/coldchain
cp .env.example .env

# .env 파일 편집
nano .env
```

**중요 환경 변수 설정**:
```bash
# 데이터베이스 (SQLite 사용 - 간단함)
DATABASE_URL=sqlite:///./coldchain.db

# 또는 PostgreSQL 사용 시
# DATABASE_URL=postgresql://coldchain:PASSWORD@localhost:5432/coldchain_db

# 보안
SECRET_KEY=<강력한_랜덤_키_생성>
# Python으로 생성:
# python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# API Keys (선택 사항)
NAVER_MAP_CLIENT_ID=your_naver_client_id
NAVER_MAP_CLIENT_SECRET=your_naver_client_secret

# Redis (선택 - 로컬에서 실행)
REDIS_URL=redis://localhost:6379/0

# CORS (Frontend IP 추가)
CORS_ORIGINS=["http://132.145.YYY.YYY","http://localhost:3000"]

# 기타
ENVIRONMENT=production
```

#### Docker Compose 설정 수정
```bash
# docker-compose.prod.yml 확인
cat docker-compose.prod.yml

# 필요시 수정 (로컬 DB 사용)
nano docker-compose.prod.yml
```

**간단한 docker-compose.prod.yml** (PostgreSQL 포함):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: coldchain-postgres
    environment:
      POSTGRES_DB: coldchain_db
      POSTGRES_USER: coldchain
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: coldchain-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.production
    container_name: coldchain-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://coldchain:${DB_PASSWORD:-changeme123}@postgres:5432/coldchain_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    volumes:
      - ./backend/data:/app/data

volumes:
  postgres_data:
  redis_data:
```

#### 배포 실행
```bash
cd /opt/coldchain

# Docker Compose로 전체 스택 시작
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 컨테이너 상태 확인
docker ps
```

#### 데이터베이스 마이그레이션
```bash
# Backend 컨테이너에 접속
docker exec -it coldchain-backend bash

# Alembic 마이그레이션
alembic upgrade head

# 초기 데이터 로드 (선택)
python scripts/seed_data.py

# 컨테이너 종료
exit
```

#### Health Check
```bash
# Backend API 확인
curl http://localhost:8000/health

# 예상 응답:
# {"status":"healthy","database":"connected"}

# API 문서 확인
curl http://localhost:8000/docs
```

### Step 4.3: VM 2 (Frontend) 설정

#### 새 터미널에서 SSH 접속
```bash
ssh -i coldchain-frontend.key ubuntu@132.145.YYY.YYY
```

#### 시스템 업데이트 및 패키지 설치
```bash
# 업데이트
sudo apt update && sudo apt upgrade -y

# Nginx 및 필수 패키지 설치
sudo apt install -y nginx certbot python3-certbot-nginx git curl
```

#### 방화벽 설정
```bash
# UFW 방화벽
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

#### 프로젝트 클론
```bash
# 프로젝트 디렉토리
sudo mkdir -p /opt/coldchain
sudo chown ubuntu:ubuntu /opt/coldchain

cd /opt/coldchain
git clone https://github.com/rpaakdi1-spec/3-.git .
git checkout genspark_ai_developer
```

#### Node.js 설치 (Frontend 빌드용)
```bash
# NodeSource repository 추가
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Node.js 설치
sudo apt install -y nodejs

# 버전 확인
node --version  # v18.x
npm --version
```

#### Frontend 빌드
```bash
cd /opt/coldchain/frontend

# 환경 변수 설정
cat > .env << EOF
VITE_API_URL=http://132.145.XXX.XXX:8000/api/v1
VITE_WS_URL=ws://132.145.XXX.XXX:8001/ws
EOF

# 의존성 설치
npm install

# 프로덕션 빌드
npm run build

# 빌드 결과 확인
ls -la dist/
```

#### Nginx 설정
```bash
# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/coldchain
```

**Nginx 설정 내용**:
```nginx
server {
    listen 80;
    server_name 132.145.YYY.YYY;  # Frontend IP

    root /opt/coldchain/frontend/dist;
    index index.html;

    # Frontend static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://132.145.XXX.XXX:8000;  # Backend IP
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://132.145.XXX.XXX:8001;  # Backend IP
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json application/javascript;
}
```

#### Nginx 활성화
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/coldchain /etc/nginx/sites-enabled/

# 기본 사이트 비활성화 (선택)
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx

# 상태 확인
sudo systemctl status nginx
```

#### 접속 테스트
```bash
# Frontend 접속 (브라우저에서)
http://132.145.YYY.YYY

# Backend API 접속
http://132.145.YYY.YYY/api/v1/health
```

---

## 5. 도메인 및 SSL 설정

### Step 5.1: 도메인 연결 (선택 사항)

#### 도메인이 있는 경우
```
1. 도메인 DNS 설정:
   A Record:
   - @ → 132.145.YYY.YYY (Frontend IP)
   - api → 132.145.XXX.XXX (Backend IP)

2. 전파 대기 (5-30분)

3. 확인:
   nslookup yourdomain.com
```

### Step 5.2: SSL 인증서 (Let's Encrypt)

#### Frontend VM에서 실행
```bash
# Certbot으로 SSL 인증서 자동 설치
sudo certbot --nginx -d yourdomain.com

# 이메일 입력
# 약관 동의: Y
# 뉴스레터: N (선택)

# 인증서 자동 갱신 테스트
sudo certbot renew --dry-run

# Nginx 재시작
sudo systemctl restart nginx
```

#### SSL 자동 갱신 설정
```bash
# Cron job 확인 (자동 설정됨)
sudo systemctl status certbot.timer
```

---

## 6. 모니터링 설정

### Step 6.1: Netdata 설치 (무료 모니터링)

#### Backend VM에 설치
```bash
ssh -i coldchain-backend.key ubuntu@132.145.XXX.XXX

# Netdata 설치 (자동 스크립트)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# 설치 완료 후
# 접속: http://132.145.XXX.XXX:19999
```

### Step 6.2: Uptime Robot 설정 (무료)

```
1. 사이트 접속:
   https://uptimerobot.com

2. 무료 가입

3. 모니터 추가:
   - Type: HTTP(s)
   - URL: http://132.145.YYY.YYY
   - Monitoring Interval: 5분
   
4. 알림 설정:
   - Email 알림
   - Down 시 즉시 알림
```

---

## 7. 최종 확인 체크리스트

### ✅ VM 상태 확인
```bash
# Backend VM
ssh -i coldchain-backend.key ubuntu@132.145.XXX.XXX
docker ps
# 예상: postgres, redis, backend 실행 중

# Frontend VM
ssh -i coldchain-frontend.key ubuntu@132.145.YYY.YYY
sudo systemctl status nginx
# 예상: active (running)
```

### ✅ 서비스 접속 확인
```
Frontend:
  http://132.145.YYY.YYY
  또는 https://yourdomain.com

Backend API:
  http://132.145.YYY.YYY/api/v1/health
  http://132.145.YYY.YYY/api/v1/docs

Netdata:
  http://132.145.XXX.XXX:19999
```

### ✅ 기능 테스트
```
1. Frontend 로딩 확인
2. 로그인 테스트
3. 대시보드 확인
4. API 응답 확인
5. WebSocket 연결 확인
```

---

## 8. 유지보수

### 일일 모니터링
```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# 디스크 사용량
df -h

# 메모리 사용량
free -h

# Docker 상태
docker stats
```

### 업데이트
```bash
# 코드 업데이트
cd /opt/coldchain
git pull origin genspark_ai_developer

# 재배포
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### 백업
```bash
# 데이터베이스 백업
docker exec coldchain-postgres pg_dump -U coldchain coldchain_db > backup_$(date +%Y%m%d).sql

# 업로드 파일 백업
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz /opt/coldchain/backend/data/uploads/
```

---

## 🎉 완료!

### 배포 요약
```yaml
✅ VM 2개 생성 (Always Free)
✅ Docker + Docker Compose 설치
✅ Backend 배포 (PostgreSQL + Redis + FastAPI)
✅ Frontend 배포 (React + Nginx)
✅ 방화벽 설정
✅ SSL 인증서 (선택)
✅ 모니터링 설정

월 비용: $0
서비스 상태: 운영 중
접속 URL: http://132.145.YYY.YYY
```

### 다음 단계
```
✅ 실제 데이터 입력
✅ 사용자 교육
✅ 운영 모니터링
✅ 정기 백업
```

---

**작성일**: 2026-01-28  
**배포 플랫폼**: Oracle Cloud Free Tier  
**월 비용**: $0 (완전 무료)  
**상태**: ✅ 배포 준비 완료
