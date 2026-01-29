#!/bin/bash

# Oracle Cloud Free Tier 자동 배포 스크립트
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
║  Oracle Cloud Free Tier Deployment                       ║
║  Cost: $0/month (Forever Free)                           ║
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

# 1. 시스템 확인
echo ""
log_info "Step 1: 시스템 환경 확인..."

# OS 확인
if [ -f /etc/os-release ]; then
    . /etc/os-release
    log_success "OS: $NAME $VERSION"
else
    log_error "지원하지 않는 운영체제입니다."
    exit 1
fi

# 2. 시스템 업데이트
echo ""
log_info "Step 2: 시스템 업데이트 중..."
sudo apt update -qq
sudo apt upgrade -y -qq
log_success "시스템 업데이트 완료"

# 3. 필수 패키지 설치
echo ""
log_info "Step 3: 필수 패키지 설치 중..."

PACKAGES="git curl wget vim ufw certbot python3-certbot-nginx"
for pkg in $PACKAGES; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        log_info "Installing $pkg..."
        sudo apt install -y $pkg -qq
    else
        log_success "$pkg already installed"
    fi
done

log_success "필수 패키지 설치 완료"

# 4. 방화벽 설정
echo ""
log_info "Step 4: 방화벽 설정 중..."

sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 8000/tcp comment 'Backend API'
sudo ufw allow 8001/tcp comment 'WebSocket'
sudo ufw allow 19999/tcp comment 'Netdata'
sudo ufw --force enable

log_success "방화벽 설정 완료"

# 5. Docker 설치
echo ""
log_info "Step 5: Docker 설치 중..."

if ! command -v docker &> /dev/null; then
    log_info "Docker 설치 중..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker $USER
    log_success "Docker 설치 완료"
else
    log_success "Docker 이미 설치됨"
fi

# Docker Compose 설치
if ! command -v docker-compose &> /dev/null; then
    log_info "Docker Compose 설치 중..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    log_success "Docker Compose 설치 완료"
else
    log_success "Docker Compose 이미 설치됨"
fi

# Docker 버전 확인
DOCKER_VERSION=$(docker --version)
COMPOSE_VERSION=$(docker-compose --version)
log_info "Docker: $DOCKER_VERSION"
log_info "Docker Compose: $COMPOSE_VERSION"

# 6. 프로젝트 클론
echo ""
log_info "Step 6: 프로젝트 클론 중..."

PROJECT_DIR="/opt/coldchain"

if [ -d "$PROJECT_DIR" ]; then
    log_warning "프로젝트 디렉토리가 이미 존재합니다: $PROJECT_DIR"
    read -p "기존 디렉토리를 삭제하고 새로 클론하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf $PROJECT_DIR
        log_success "기존 디렉토리 삭제 완료"
    else
        log_info "기존 디렉토리 사용"
    fi
fi

if [ ! -d "$PROJECT_DIR" ]; then
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    
    log_info "Git 클론 중..."
    git clone https://github.com/rpaakdi1-spec/3-.git $PROJECT_DIR
    cd $PROJECT_DIR
    git checkout genspark_ai_developer
    log_success "프로젝트 클론 완료"
else
    cd $PROJECT_DIR
    log_info "Git pull 실행..."
    git pull origin genspark_ai_developer
fi

# 7. 환경 변수 설정
echo ""
log_info "Step 7: 환경 변수 설정..."

ENV_FILE="$PROJECT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    log_info ".env 파일 생성 중..."
    
    # 랜덤 비밀번호 생성
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    SECRET_KEY=$(openssl rand -base64 48 | tr -d "=+/" | cut -c1-64)
    
    cat > $ENV_FILE << EOF
# Database
DB_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://coldchain:$DB_PASSWORD@postgres:5432/coldchain_db

# Redis
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0

# Security
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# API Keys (선택 사항 - 나중에 설정)
NAVER_MAP_CLIENT_ID=
NAVER_MAP_CLIENT_SECRET=

# Monitoring
SENTRY_DSN=
EOF

    log_success ".env 파일 생성 완료"
    log_warning "생성된 비밀번호를 안전하게 보관하세요!"
    log_info "DB Password: $DB_PASSWORD"
    log_info "Redis Password: $REDIS_PASSWORD"
else
    log_success ".env 파일이 이미 존재합니다"
fi

# 8. 디렉토리 생성
echo ""
log_info "Step 8: 필요한 디렉토리 생성..."

mkdir -p $PROJECT_DIR/backend/data/uploads
mkdir -p $PROJECT_DIR/backend/data/templates
mkdir -p $PROJECT_DIR/backend/data/backups
mkdir -p $PROJECT_DIR/backend/logs
mkdir -p $PROJECT_DIR/logs

log_success "디렉토리 생성 완료"

# 9. Docker Compose 배포
echo ""
log_info "Step 9: Docker Compose로 서비스 시작..."

cd $PROJECT_DIR

# 기존 컨테이너 정리
if [ "$(docker ps -aq)" ]; then
    log_info "기존 컨테이너 정리 중..."
    docker-compose -f docker-compose.oracle.yml down 2>/dev/null || true
fi

# 서비스 시작
log_info "서비스 시작 중 (약 2-3분 소요)..."
docker-compose -f docker-compose.oracle.yml up -d --build

# 서비스 시작 대기
log_info "서비스 초기화 대기 중..."
sleep 10

# 컨테이너 상태 확인
log_info "컨테이너 상태 확인..."
docker-compose -f docker-compose.oracle.yml ps

log_success "Docker Compose 배포 완료"

# 10. 데이터베이스 마이그레이션
echo ""
log_info "Step 10: 데이터베이스 마이그레이션..."

# Backend 컨테이너가 준비될 때까지 대기
log_info "Backend 서비스 준비 대기 중..."
for i in {1..30}; do
    if docker exec coldchain-backend curl -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend 서비스 준비 완료"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "Backend 서비스 시작 실패"
        docker logs coldchain-backend
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""

# Alembic 마이그레이션 실행
log_info "Alembic 마이그레이션 실행 중..."
docker exec coldchain-backend alembic upgrade head

log_success "데이터베이스 마이그레이션 완료"

# 11. Health Check
echo ""
log_info "Step 11: Health Check..."

# API Health Check
API_HEALTH=$(curl -s http://localhost:8000/health)
if echo "$API_HEALTH" | grep -q "healthy"; then
    log_success "Backend API: 정상"
    echo "$API_HEALTH"
else
    log_error "Backend API: 비정상"
    docker logs coldchain-backend --tail=50
fi

# 12. Netdata 설치 (모니터링)
echo ""
read -p "Netdata 모니터링 도구를 설치하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Netdata 설치 중..."
    bash <(curl -Ss https://my-netdata.io/kickstart.sh) --dont-wait
    log_success "Netdata 설치 완료"
    log_info "Netdata 접속: http://$(curl -s ifconfig.me):19999"
fi

# 13. 최종 정보 출력
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              배포 완료!                                    ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Public IP 확인
PUBLIC_IP=$(curl -s ifconfig.me)
log_success "배포 완료!"
echo ""
log_info "=== 서비스 접속 정보 ==="
echo ""
echo -e "${BLUE}Backend API:${NC}"
echo "  - Health: http://$PUBLIC_IP:8000/health"
echo "  - API Docs: http://$PUBLIC_IP:8000/docs"
echo ""
echo -e "${BLUE}WebSocket:${NC}"
echo "  - WebSocket: ws://$PUBLIC_IP:8001/ws"
echo ""
if command -v netdata &> /dev/null; then
    echo -e "${BLUE}Monitoring:${NC}"
    echo "  - Netdata: http://$PUBLIC_IP:19999"
    echo ""
fi

echo -e "${YELLOW}=== 다음 단계 ===${NC}"
echo "1. Frontend VM에서 이 IP를 Backend URL로 설정"
echo "   - VITE_API_URL=http://$PUBLIC_IP:8000/api/v1"
echo "   - VITE_WS_URL=ws://$PUBLIC_IP:8001/ws"
echo ""
echo "2. 로그 확인:"
echo "   docker-compose -f docker-compose.oracle.yml logs -f"
echo ""
echo "3. 컨테이너 상태:"
echo "   docker ps"
echo ""
echo "4. 서비스 재시작:"
echo "   docker-compose -f docker-compose.oracle.yml restart"
echo ""
echo "5. 환경 변수 편집:"
echo "   nano /opt/coldchain/.env"
echo ""
echo -e "${GREEN}배포 완료! 월 비용: $0 (Oracle Cloud Free)${NC}"
echo ""
