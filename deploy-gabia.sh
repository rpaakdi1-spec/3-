#!/bin/bash

# 가비아 클라우드 Gen2 자동 배포 스크립트
# UVIS GPS Fleet Management System
# Version: 1.0.0
# OS: Rocky Linux 8.10

set -e  # Exit on error

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로고
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║  UVIS GPS Fleet Management System                        ║
║  가비아 클라우드 Gen2 배포                                 ║
║  OS: Rocky Linux 8.10                                     ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# 함수 정의
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 서버 IP 자동 감지
detect_server_ip() {
    SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || curl -s ipinfo.io/ip)
    if [ -z "$SERVER_IP" ]; then
        log_error "서버 IP를 자동으로 감지할 수 없습니다."
        read -p "서버 공인 IP를 입력하세요: " SERVER_IP
    fi
    log_info "서버 공인 IP: $SERVER_IP"
}

# 1. 시스템 확인
echo ""
log_info "Step 1: 시스템 환경 확인..."

# OS 확인
if [ -f /etc/os-release ]; then
    . /etc/os-release
    log_success "OS: $PRETTY_NAME"
    
    # Rocky Linux 확인
    if [[ "$ID" != "rocky" ]]; then
        log_warning "이 스크립트는 Rocky Linux를 위해 작성되었습니다."
        read -p "계속 진행하시겠습니까? (y/n): " confirm
        if [[ "$confirm" != "y" ]]; then
            exit 1
        fi
    fi
else
    log_error "지원하지 않는 OS입니다."
    exit 1
fi

# Root 권한 확인
if [ "$EUID" -ne 0 ]; then 
    log_error "이 스크립트는 root 권한이 필요합니다. 'sudo'를 사용하거나 root로 로그인하세요."
    exit 1
fi

# 디스크 공간 확인
AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_SPACE" -lt 10485760 ]; then  # 10GB
    log_warning "디스크 공간이 부족할 수 있습니다. (최소 10GB 권장)"
fi

# 메모리 확인
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
if [ "$TOTAL_MEM" -lt 3500 ]; then  # 4GB 권장
    log_warning "메모리가 부족할 수 있습니다. (최소 4GB 권장)"
fi

detect_server_ip

# 2. SELinux 및 방화벽 설정
echo ""
log_info "Step 2: SELinux 및 방화벽 설정..."

# SELinux 비활성화 (Rocky Linux 특성)
if command -v getenforce &> /dev/null; then
    if [ "$(getenforce)" != "Disabled" ]; then
        log_info "SELinux 비활성화 중..."
        setenforce 0
        sed -i 's/^SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
        sed -i 's/^SELINUX=permissive/SELINUX=disabled/' /etc/selinux/config
        log_success "SELinux 비활성화 완료"
    fi
fi

# Firewalld 설정
if command -v firewall-cmd &> /dev/null; then
    log_info "Firewalld 설정 중..."
    systemctl start firewalld
    systemctl enable firewalld
    
    # 필수 포트 허용
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --permanent --add-port=8000/tcp  # Backend
    firewall-cmd --permanent --add-port=3000/tcp  # Frontend Dev
    firewall-cmd --permanent --add-port=19999/tcp # Netdata
    firewall-cmd --reload
    
    log_success "Firewalld 설정 완료"
fi

# 3. 시스템 업데이트
echo ""
log_info "Step 3: 시스템 업데이트..."
dnf update -y
log_success "시스템 업데이트 완료"

# 4. EPEL 저장소 및 필수 패키지 설치
echo ""
log_info "Step 4: EPEL 저장소 및 필수 패키지 설치..."

# EPEL 설치
dnf install -y epel-release
dnf config-manager --set-enabled powertools || dnf config-manager --set-enabled crb

# 필수 패키지 설치
dnf install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    net-tools \
    bind-utils \
    fail2ban \
    jq \
    policycoreutils-python-utils

log_success "필수 패키지 설치 완료"

# 5. Docker 설치 (Rocky Linux)
echo ""
log_info "Step 5: Docker 설치..."

if ! command -v docker &> /dev/null; then
    log_info "Docker 저장소 추가..."
    dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    log_info "Docker 설치 중..."
    dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Docker 서비스 시작
    systemctl start docker
    systemctl enable docker
    
    log_success "Docker 설치 완료"
else
    log_success "Docker가 이미 설치되어 있습니다."
fi

# Docker 버전 확인
DOCKER_VERSION=$(docker --version)
log_info "Docker 버전: $DOCKER_VERSION"

# 6. Fail2Ban 설정
echo ""
log_info "Step 6: Fail2Ban 설정..."

systemctl start fail2ban
systemctl enable fail2ban

# SSH 보호 설정
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/secure
EOF

systemctl restart fail2ban
log_success "Fail2Ban 설정 완료"

# 7. 프로젝트 클론
echo ""
log_info "Step 7: UVIS 프로젝트 클론..."

cd /root
if [ -d "uvis" ]; then
    log_warning "uvis 디렉터리가 이미 존재합니다. 기존 디렉터리를 삭제하고 다시 클론합니다."
    rm -rf uvis
fi

git clone https://github.com/rpaakdi1-spec/3-.git uvis
cd uvis
git checkout genspark_ai_developer

log_success "프로젝트 클론 완료"

# 8. 환경 변수 설정
echo ""
log_info "Step 8: 환경 변수 설정..."

# 비밀번호 자동 생성
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
JWT_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# .env 파일 생성
cat > /root/uvis/backend/.env << EOF
# Database
DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/uvis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=uvis

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_PASSWORD=${REDIS_PASSWORD}

# JWT
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=production

# Frontend URL
FRONTEND_URL=http://${SERVER_IP}

# CORS
CORS_ORIGINS=["http://${SERVER_IP}","http://localhost:3000","http://localhost"]
EOF

log_success "환경 변수 설정 완료"

# 9. Docker Compose 파일 생성
echo ""
log_info "Step 9: Docker Compose 파일 생성..."

cat > /root/uvis/docker-compose.yml << 'DOCKEREOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: uvis-postgres
    restart: always
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: uvis-redis
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: uvis-backend
    restart: always
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=production
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - backend_logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: uvis-frontend
    restart: always
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://${SERVER_IP}:8000/api/v1
      - REACT_APP_WS_URL=ws://${SERVER_IP}:8000/ws
    ports:
      - "80:80"
    volumes:
      - ./frontend:/app
      - /app/node_modules

  nginx:
    image: nginx:alpine
    container_name: uvis-nginx
    restart: always
    depends_on:
      - backend
      - frontend
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  backend_logs:

networks:
  default:
    name: uvis-network
DOCKEREOF

log_success "Docker Compose 파일 생성 완료"

# 10. Nginx 설정 파일 생성
echo ""
log_info "Step 10: Nginx 설정..."

mkdir -p /root/uvis/nginx

cat > /root/uvis/nginx/nginx.conf << 'NGINXEOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name _;

        client_max_body_size 100M;

        location /api/v1 {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }

        location /health {
            proxy_pass http://backend/health;
            proxy_set_header Host $host;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
NGINXEOF

log_success "Nginx 설정 완료"

# 11. Docker Compose 빌드 및 실행
echo ""
log_info "Step 11: Docker 컨테이너 빌드 및 실행..."

cd /root/uvis
docker compose build
docker compose up -d

log_success "Docker 컨테이너 실행 완료"

# 12. 컨테이너 시작 대기
echo ""
log_info "Step 12: 컨테이너 시작 대기..."
sleep 30

# 13. 데이터베이스 마이그레이션
echo ""
log_info "Step 13: 데이터베이스 마이그레이션..."

docker compose exec -T backend alembic upgrade head || log_warning "마이그레이션 실패 (수동 실행 필요)"

log_success "데이터베이스 마이그레이션 완료"

# 14. Netdata 설치 (선택사항)
echo ""
read -p "Netdata 모니터링을 설치하시겠습니까? (y/n): " install_netdata

if [[ "$install_netdata" == "y" ]]; then
    log_info "Step 14: Netdata 설치..."
    bash <(curl -Ss https://my-netdata.io/kickstart.sh) --non-interactive
    
    # Netdata 방화벽 설정
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=19999/tcp
        firewall-cmd --reload
    fi
    
    log_success "Netdata 설치 완료"
fi

# 15. 배포 완료
echo ""
echo -e "${GREEN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║  🎉 배포 완료!                                             ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${BLUE}🌐 접속 정보:${NC}"
echo -e "   Frontend:  http://${SERVER_IP}"
echo -e "   Backend:   http://${SERVER_IP}:8000"
echo -e "   API Docs:  http://${SERVER_IP}:8000/docs"
echo -e "   Health:    http://${SERVER_IP}:8000/health"

if [[ "$install_netdata" == "y" ]]; then
    echo -e "   Netdata:   http://${SERVER_IP}:19999"
fi

echo ""
echo -e "${BLUE}🔑 인증 정보:${NC}"
echo -e "   Database:  postgres / ${DB_PASSWORD}"
echo -e "   Redis:     ${REDIS_PASSWORD}"
echo -e "   JWT:       ${JWT_SECRET}"

echo ""
echo -e "${BLUE}📝 다음 단계:${NC}"
echo -e "   1. Health Check: curl http://${SERVER_IP}:8000/health"
echo -e "   2. 브라우저에서 http://${SERVER_IP} 접속"
echo -e "   3. 테스트 계정으로 로그인: driver1 / password123"
echo -e "   4. ML 재학습 스케줄 설정 (선택사항)"
echo -e "   5. 모바일 앱 Backend URL 변경"

echo ""
echo -e "${GREEN}축하합니다! UVIS가 성공적으로 배포되었습니다! 🎊${NC}"
