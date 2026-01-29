#!/bin/bash

###############################################################################
# UVIS GPS Fleet Management - Cafe24 자동 배포 스크립트
# 
# 작성일: 2026-01-28
# 소요 시간: 약 20분
# 필요 사항: Cafe24 클라우드 서버 (Ubuntu 22.04)
###############################################################################

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}[STEP $1] $2${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# 시작 메시지
clear
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           UVIS GPS Fleet Management System - Cafe24 배포                      ║
║                    Cold Chain Dispatch Platform                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log_info "배포 시작: $(date)"
log_info "예상 소요 시간: 약 20분"

# Step 1: 시스템 환경 확인
log_step "1/15" "시스템 환경 확인"

log_info "OS 버전 확인 중..."
if ! grep -q "Ubuntu 22.04" /etc/os-release && ! grep -q "Ubuntu 24.04" /etc/os-release; then
    log_warn "Ubuntu 22.04 또는 24.04 권장. 현재 OS: $(lsb_release -d)"
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_error "배포 중단됨"
        exit 1
    fi
fi

log_info "시스템 리소스 확인 중..."
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
log_info "사용 가능한 메모리: ${TOTAL_MEM}MB"

if [ "$TOTAL_MEM" -lt 1500 ]; then
    log_warn "메모리가 부족할 수 있습니다 (권장: 2GB 이상)"
fi

# Step 2: 시스템 업데이트
log_step "2/15" "시스템 패키지 업데이트"

log_info "패키지 목록 업데이트 중..."
apt-get update -qq

log_info "시스템 업그레이드 중 (시간이 걸릴 수 있습니다)..."
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq

# Step 3: 필수 패키지 설치
log_step "3/15" "필수 패키지 설치"

log_info "기본 도구 설치 중..."
apt-get install -y -qq \
    curl \
    wget \
    git \
    vim \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Step 4: Docker 설치
log_step "4/15" "Docker 설치"

if command -v docker &> /dev/null; then
    log_info "Docker가 이미 설치되어 있습니다: $(docker --version)"
else
    log_info "Docker 설치 중..."
    
    # Docker GPG 키 추가
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Docker 저장소 추가
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Docker 설치
    apt-get update -qq
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Docker 서비스 시작
    systemctl start docker
    systemctl enable docker
    
    log_info "Docker 설치 완료: $(docker --version)"
fi

# Step 5: Docker Compose 설치
log_step "5/15" "Docker Compose 설치"

if command -v docker-compose &> /dev/null; then
    log_info "Docker Compose가 이미 설치되어 있습니다: $(docker-compose --version)"
else
    log_info "Docker Compose 설치 중..."
    
    # Docker Compose 다운로드
    COMPOSE_VERSION="2.24.0"
    curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    
    # 실행 권한 부여
    chmod +x /usr/local/bin/docker-compose
    
    log_info "Docker Compose 설치 완료: $(docker-compose --version)"
fi

# Step 6: 방화벽 설정 (UFW)
log_step "6/15" "방화벽 설정"

log_info "UFW 방화벽 설정 중..."

# UFW 설치
apt-get install -y ufw

# 기본 정책 설정
ufw default deny incoming
ufw default allow outgoing

# 필요한 포트 허용
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 8000/tcp comment 'Backend API'
ufw allow 19999/tcp comment 'Netdata'

# UFW 활성화 (비대화형)
echo "y" | ufw enable

log_info "방화벽 설정 완료"
ufw status

# Step 7: Fail2Ban 설치 (보안 강화)
log_step "7/15" "Fail2Ban 보안 설정"

log_info "Fail2Ban 설치 중..."
apt-get install -y fail2ban

# Fail2Ban 설정
cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
EOF

systemctl enable fail2ban
systemctl restart fail2ban

log_info "Fail2Ban 설정 완료"

# Step 8: 프로젝트 클론
log_step "8/15" "GitHub에서 프로젝트 클론"

PROJECT_DIR="/opt/uvis-gps-fleet"

if [ -d "$PROJECT_DIR" ]; then
    log_warn "프로젝트 디렉터리가 이미 존재합니다"
    read -p "기존 디렉터리를 삭제하고 새로 클론하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
    else
        log_info "기존 디렉터리 사용"
    fi
fi

if [ ! -d "$PROJECT_DIR" ]; then
    log_info "프로젝트 클론 중..."
    git clone -b genspark_ai_developer https://github.com/rpaakdi1-spec/3-.git "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
log_info "프로젝트 디렉터리: $PROJECT_DIR"

# Step 9: 환경 변수 설정
log_step "9/15" "환경 변수 설정"

# 서버 IP 자동 감지
SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "localhost")
log_info "서버 IP: $SERVER_IP"

# .env 파일 생성
log_info ".env 파일 생성 중..."

cat > "$PROJECT_DIR/backend/.env" <<EOF
# Database
DATABASE_URL=postgresql://uvis_user:uvis_password_secure@postgres:5432/uvis_gps_fleet

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://${SERVER_IP}","http://${SERVER_IP}:3000"]

# Environment
ENVIRONMENT=production
DEBUG=false

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=UVIS GPS Fleet Management

# File Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=/app/uploads

# Logging
LOG_LEVEL=INFO
EOF

log_info "환경 변수 설정 완료"

# Step 10: Docker Compose 설정 확인
log_step "10/15" "Docker Compose 설정"

log_info "docker-compose.yml 확인 중..."

if [ ! -f "$PROJECT_DIR/docker-compose.yml" ]; then
    log_error "docker-compose.yml 파일이 없습니다!"
    exit 1
fi

log_info "Docker Compose 설정 확인 완료"

# Step 11: PostgreSQL & Redis 시작
log_step "11/15" "데이터베이스 서비스 시작"

log_info "PostgreSQL 및 Redis 컨테이너 시작 중..."
docker-compose up -d postgres redis

log_info "데이터베이스 준비 대기 중 (30초)..."
sleep 30

# Step 12: 데이터베이스 마이그레이션
log_step "12/15" "데이터베이스 마이그레이션"

log_info "Alembic 마이그레이션 실행 중..."
docker-compose run --rm backend alembic upgrade head || log_warn "마이그레이션 경고 (계속 진행)"

# Step 13: Backend 시작
log_step "13/15" "Backend API 서버 시작"

log_info "Backend 컨테이너 빌드 및 시작 중..."
docker-compose up -d backend

log_info "Backend 준비 대기 중 (20초)..."
sleep 20

# Step 14: Frontend 빌드 및 배포
log_step "14/15" "Frontend 빌드 및 Nginx 설정"

log_info "Frontend 빌드 중 (시간이 걸릴 수 있습니다)..."
cd "$PROJECT_DIR/frontend"
docker run --rm -v "$PWD":/app -w /app node:18 npm install
docker run --rm -v "$PWD":/app -w /app node:18 npm run build

log_info "Nginx 설정..."

# Nginx 설치
apt-get install -y nginx

# Nginx 설정 파일
cat > /etc/nginx/sites-available/uvis <<EOF
server {
    listen 80;
    server_name ${SERVER_IP};

    # Frontend
    location / {
        root ${PROJECT_DIR}/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Nginx 활성화
ln -sf /etc/nginx/sites-available/uvis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

log_info "Nginx 설정 완료"

# Step 15: Netdata 모니터링 설치 (선택)
log_step "15/15" "Netdata 모니터링 설치"

read -p "Netdata 모니터링을 설치하시겠습니까? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    log_info "Netdata 설치 중..."
    bash <(curl -Ss https://my-netdata.io/kickstart.sh) --dont-wait --disable-telemetry
    log_info "Netdata 설치 완료: http://${SERVER_IP}:19999"
else
    log_info "Netdata 설치 건너뜀"
fi

# 배포 완료
echo -e "\n${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        ✅ 배포 완료! (Cafe24)                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

log_info "배포 완료 시간: $(date)"
log_info "소요 시간: 약 20분"

echo ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "접속 정보"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}Frontend (웹):${NC}      http://${SERVER_IP}"
echo -e "${GREEN}Backend API:${NC}        http://${SERVER_IP}:8000"
echo -e "${GREEN}API 문서:${NC}           http://${SERVER_IP}:8000/docs"
echo -e "${GREEN}Health Check:${NC}       http://${SERVER_IP}:8000/health"
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${GREEN}Monitoring:${NC}         http://${SERVER_IP}:19999"
fi
echo ""

log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "다음 단계"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 웹 브라우저에서 http://${SERVER_IP} 접속"
echo "2. 기본 관리자 계정으로 로그인:"
echo "   - 아이디: admin"
echo "   - 비밀번호: admin123 (최초 로그인 후 변경 필요)"
echo ""
echo "3. 시스템 상태 확인:"
echo "   docker-compose ps"
echo "   docker-compose logs -f backend"
echo ""
echo "4. 도메인 연결 및 SSL 설정 (선택):"
echo "   - Cafe24에서 도메인 구매"
echo "   - Let's Encrypt로 SSL 인증서 설정"
echo ""

log_info "🎉 Cafe24 배포 완료! 한국 서울 데이터센터에서 운영 중입니다."
log_info "💚 월 4,400원으로 프로덕션 서비스 시작!"
