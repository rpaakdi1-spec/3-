#!/bin/bash

# Hetzner Cloud 자동 배포 스크립트
# UVIS GPS Fleet Management System
# Version: 1.0.0

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
║  Hetzner Cloud Deployment                                ║
║  Cost: €4.49/month ($4.90)                               ║
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
        read -p "서버 IP를 입력하세요: " SERVER_IP
    fi
    log_info "서버 IP: $SERVER_IP"
}

# 1. 시스템 확인
echo ""
log_info "Step 1: 시스템 환경 확인..."

# OS 확인
if [ -f /etc/os-release ]; then
    . /etc/os-release
    log_success "OS: $PRETTY_NAME"
else
    log_error "지원하지 않는 OS입니다."
    exit 1
fi

# Root 권한 확인
if [ "$EUID" -ne 0 ]; then 
    log_error "이 스크립트는 root 권한이 필요합니다. 'sudo'를 사용하세요."
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

# 2. 시스템 업데이트
echo ""
log_info "Step 2: 시스템 업데이트..."
apt update && apt upgrade -y
log_success "시스템 업데이트 완료"

# 3. 필수 패키지 설치
echo ""
log_info "Step 3: 필수 패키지 설치..."
apt install -y curl wget git ufw fail2ban nginx postgresql-client redis-tools jq
log_success "필수 패키지 설치 완료"

# 4. Docker 설치
echo ""
log_info "Step 4: Docker 설치..."
if ! command -v docker &> /dev/null; then
    log_info "Docker를 설치합니다..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    log_success "Docker 설치 완료"
else
    log_info "Docker가 이미 설치되어 있습니다."
fi

# Docker Compose 설치
if ! command -v docker compose &> /dev/null; then
    log_info "Docker Compose를 설치합니다..."
    apt install -y docker-compose-plugin
    log_success "Docker Compose 설치 완료"
else
    log_info "Docker Compose가 이미 설치되어 있습니다."
fi

# Docker 시작
systemctl enable docker
systemctl start docker
log_success "Docker 서비스 시작"

# 5. 방화벽 설정 (UFW)
echo ""
log_info "Step 5: 방화벽 설정..."
ufw --force disable  # 기존 규칙 초기화
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw allow 8000/tcp    # Backend API
ufw allow 19999/tcp   # Netdata
ufw --force enable
log_success "방화벽 설정 완료"

# 6. Fail2Ban 설정
echo ""
log_info "Step 6: Fail2Ban 설정..."
systemctl enable fail2ban
systemctl start fail2ban
log_success "Fail2Ban 시작"

# 7. 프로젝트 클론
echo ""
log_info "Step 7: 프로젝트 클론..."
PROJECT_DIR="/opt/uvis"
if [ -d "$PROJECT_DIR" ]; then
    log_warning "프로젝트 디렉토리가 이미 존재합니다. 기존 디렉토리를 백업합니다..."
    mv "$PROJECT_DIR" "${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

git clone https://github.com/rpaakdi1-spec/3-.git "$PROJECT_DIR"
cd "$PROJECT_DIR"
git checkout genspark_ai_developer
log_success "프로젝트 클론 완료"

# 8. 환경 변수 설정
echo ""
log_info "Step 8: 환경 변수 설정..."

# .env 파일 생성
cat > "$PROJECT_DIR/.env" << EOF
# Server
SERVER_IP=$SERVER_IP

# Database
DATABASE_URL=postgresql://uvis_user:uvis_$(openssl rand -hex 12)@postgres:5432/uvis_db
POSTGRES_USER=uvis_user
POSTGRES_PASSWORD=uvis_$(openssl rand -hex 12)
POSTGRES_DB=uvis_db

# Redis
REDIS_URL=redis://redis:6379/0

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
VITE_API_URL=http://$SERVER_IP:8000/api/v1
VITE_WS_URL=ws://$SERVER_IP:8001/ws

# CORS
CORS_ORIGINS=["http://$SERVER_IP","http://localhost:3000"]

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=production
EOF

log_success "환경 변수 설정 완료"

# 9. Docker Compose 파일 확인
echo ""
log_info "Step 9: Docker Compose 설정 확인..."
if [ ! -f "$PROJECT_DIR/docker-compose.prod.yml" ]; then
    log_error "docker-compose.prod.yml 파일이 없습니다."
    exit 1
fi
log_success "Docker Compose 설정 확인 완료"

# 10. PostgreSQL & Redis 시작
echo ""
log_info "Step 10: 데이터베이스 및 Redis 시작..."
cd "$PROJECT_DIR"
docker compose -f docker-compose.prod.yml up -d postgres redis
sleep 10  # DB 초기화 대기
log_success "PostgreSQL 및 Redis 시작"

# 11. 데이터베이스 초기화
echo ""
log_info "Step 11: 데이터베이스 초기화..."

# Alembic 마이그레이션 실행
if [ -d "$PROJECT_DIR/backend/alembic" ]; then
    log_info "Alembic 마이그레이션 실행..."
    docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
    log_success "데이터베이스 마이그레이션 완료"
else
    log_warning "Alembic 디렉토리가 없습니다. 마이그레이션을 건너뜁니다."
fi

# 12. Backend API 시작
echo ""
log_info "Step 12: Backend API 시작..."
docker compose -f docker-compose.prod.yml up -d backend
sleep 5
log_success "Backend API 시작"

# 13. Frontend 빌드 및 Nginx 설정
echo ""
log_info "Step 13: Frontend 빌드 및 Nginx 설정..."

# Node.js 설치 (필요시)
if ! command -v node &> /dev/null; then
    log_info "Node.js 설치..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
    log_success "Node.js 설치 완료"
fi

# Frontend 빌드
cd "$PROJECT_DIR/frontend"
npm install
npm run build
log_success "Frontend 빌드 완료"

# Nginx 설정
cat > /etc/nginx/sites-available/uvis << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    # Frontend
    location / {
        root $PROJECT_DIR/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # API Docs
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
    }
}
EOF

# Nginx 심볼릭 링크 및 재시작
ln -sf /etc/nginx/sites-available/uvis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
log_success "Nginx 설정 완료"

# 14. Netdata 설치 (모니터링)
echo ""
log_info "Step 14: Netdata 모니터링 설치..."
if ! command -v netdata &> /dev/null; then
    bash <(curl -Ss https://my-netdata.io/kickstart.sh) --dont-wait --disable-telemetry
    log_success "Netdata 설치 완료"
else
    log_info "Netdata가 이미 설치되어 있습니다."
fi

# 15. 헬스체크
echo ""
log_info "Step 15: 배포 검증 중..."
sleep 5

# Backend Health Check
HEALTH_CHECK=$(curl -s http://localhost:8000/health || echo "FAILED")
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    log_success "Backend API 정상 작동"
else
    log_warning "Backend API 헬스체크 실패. 로그를 확인하세요."
fi

# Frontend Check
if curl -s http://localhost/ > /dev/null; then
    log_success "Frontend 정상 작동"
else
    log_warning "Frontend 접속 실패. Nginx 로그를 확인하세요."
fi

# 16. 배포 완료 정보 출력
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           배포 완료!                                      ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}접속 정보:${NC}"
echo -e "  🌐 Frontend:        http://$SERVER_IP"
echo -e "  🔧 Backend API:     http://$SERVER_IP:8000"
echo -e "  📖 API Docs:        http://$SERVER_IP:8000/docs"
echo -e "  ❤️  Health Check:   http://$SERVER_IP:8000/health"
echo -e "  📊 Monitoring:      http://$SERVER_IP:19999"
echo ""
echo -e "${BLUE}관리 명령어:${NC}"
echo -e "  📋 로그 보기:       docker compose -f /opt/uvis/docker-compose.prod.yml logs -f"
echo -e "  🔄 서비스 재시작:   docker compose -f /opt/uvis/docker-compose.prod.yml restart"
echo -e "  ⏹️  서비스 중지:    docker compose -f /opt/uvis/docker-compose.prod.yml down"
echo -e "  ▶️  서비스 시작:    docker compose -f /opt/uvis/docker-compose.prod.yml up -d"
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo -e "  1️⃣  브라우저에서 http://$SERVER_IP 접속"
echo -e "  2️⃣  API 문서 확인: http://$SERVER_IP:8000/docs"
echo -e "  3️⃣  모니터링 확인: http://$SERVER_IP:19999"
echo -e "  4️⃣  도메인 연결 (선택): HETZNER_DEPLOYMENT_GUIDE.md 참고"
echo -e "  5️⃣  SSL 인증서 설정 (선택): Let's Encrypt 사용"
echo ""
echo -e "${GREEN}🎉 UVIS GPS Fleet Management System이 성공적으로 배포되었습니다!${NC}"
echo ""
