#!/bin/bash

###############################################################################
# Gabia Cloud 배포 스크립트 (최종 수정본)
# 서버: Server-s1uvis (139.150.11.99)
# OS: Rocky Linux 8.10
###############################################################################

set -e  # 에러 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
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

# 배너 출력
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     UVIS GPS Fleet Management System                        ║
║     Gabia Cloud Deployment (Fixed)                          ║
║     Version: 1.0.1                                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF

echo ""
log_info "서버 정보:"
echo "  - 서버명: Server-s1uvis"
echo "  - 공인 IP: 139.150.11.99"
echo "  - OS: Rocky Linux 8.10"
echo "  - 사양: 2vCore, 4GB RAM, 100GB SSD"
echo ""

# Step 1: 프로젝트 디렉토리 이동
log_info "Step 1: 프로젝트 디렉토리로 이동..."
cd /root/uvis || { log_error "프로젝트 디렉토리를 찾을 수 없습니다."; exit 1; }
log_success "디렉토리 이동 완료"

# Step 2: 최신 코드 가져오기
log_info "Step 2: 최신 코드 가져오기..."
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer
CURRENT_COMMIT=$(git rev-parse --short HEAD)
log_success "최신 코드 업데이트 완료 (Commit: $CURRENT_COMMIT)"

# Step 3: 파일 확인
log_info "Step 3: 수정된 파일 확인..."
log_info "Frontend Dockerfile.prod:"
if grep -q "npm ci$" frontend/Dockerfile.prod; then
    log_success "  ✓ npm ci 수정 확인 (devDependencies 포함)"
else
    log_error "  ✗ npm ci 수정 누락"
    exit 1
fi

if grep -q "REACT_APP_API_URL" frontend/Dockerfile.prod; then
    log_success "  ✓ 환경 변수 설정 확인"
else
    log_error "  ✗ 환경 변수 설정 누락"
    exit 1
fi

log_info "Backend requirements.txt:"
AIOSMTPLIB_VERSION=$(grep aiosmtplib backend/requirements.txt)
if [[ "$AIOSMTPLIB_VERSION" == *"2.0.2"* ]]; then
    log_success "  ✓ aiosmtplib 버전 확인: $AIOSMTPLIB_VERSION"
else
    log_error "  ✗ aiosmtplib 버전 오류: $AIOSMTPLIB_VERSION"
    exit 1
fi

# Step 4: .env 파일 생성
log_info "Step 4: 환경 변수 설정..."
cat > .env << 'ENVEOF'
# Database
POSTGRES_USER=uvis_user
POSTGRES_PASSWORD=uvis_password
POSTGRES_DB=uvis_db

# Backend
DATABASE_URL=postgresql://uvis_user:uvis_password@db:5432/uvis_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=gabia-uvis-production-secret-key-2026-$(date +%s)
ENVIRONMENT=production
DEBUG=false

# Frontend
REACT_APP_API_URL=http://139.150.11.99:8000
REACT_APP_WS_URL=ws://139.150.11.99:8000/ws
ENVEOF
log_success ".env 파일 생성 완료"

# Step 5: 기존 컨테이너 정리
log_info "Step 5: 기존 컨테이너 정리..."
docker-compose down -v 2>/dev/null || true
log_success "기존 컨테이너 정리 완료"

# Step 6: Docker 캐시 클리어
log_info "Step 6: Docker 캐시 클리어..."
log_warning "이 작업은 1-2분 소요됩니다..."
docker system prune -af
log_success "Docker 캐시 클리어 완료"

# Step 7: Docker 빌드
log_info "Step 7: Docker 이미지 빌드 시작..."
log_warning "이 작업은 15-20분 소요됩니다. 잠시만 기다려주세요..."
echo ""

START_TIME=$(date +%s)

# 백그라운드에서 빌드하고 실시간 로그 출력
docker-compose build --no-cache 2>&1 | tee /tmp/docker-build.log

BUILD_EXIT_CODE=${PIPESTATUS[0]}
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
if [ $BUILD_EXIT_CODE -eq 0 ]; then
    log_success "Docker 빌드 완료 (소요 시간: ${DURATION}초)"
else
    log_error "Docker 빌드 실패"
    log_error "로그를 확인하세요: /tmp/docker-build.log"
    exit 1
fi

# Step 8: 컨테이너 실행
log_info "Step 8: 컨테이너 실행..."
docker-compose up -d
log_success "컨테이너 실행 완료"

# Step 9: 컨테이너 시작 대기
log_info "Step 9: 컨테이너 초기화 대기 (30초)..."
for i in {30..1}; do
    echo -ne "  대기 중... ${i}초 남음\r"
    sleep 1
done
echo ""
log_success "대기 완료"

# Step 10: 컨테이너 상태 확인
log_info "Step 10: 컨테이너 상태 확인..."
echo ""
docker-compose ps
echo ""

# Step 11: Health Check
log_info "Step 11: Health Check 수행..."
echo ""

# Backend Health Check
log_info "Backend Health Check..."
for i in {1..10}; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log_success "  ✓ Backend is healthy"
        BACKEND_RESPONSE=$(curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "OK")
        echo "$BACKEND_RESPONSE" | head -5
        break
    else
        if [ $i -eq 10 ]; then
            log_error "  ✗ Backend health check failed"
        else
            echo -ne "  Retry $i/10...\r"
            sleep 3
        fi
    fi
done

echo ""

# Database Health Check
log_info "Database Health Check..."
if docker exec uvis-db pg_isready -U uvis_user > /dev/null 2>&1; then
    log_success "  ✓ Database is healthy"
else
    log_error "  ✗ Database health check failed"
fi

# Redis Health Check
log_info "Redis Health Check..."
if docker exec uvis-redis redis-cli ping > /dev/null 2>&1; then
    log_success "  ✓ Redis is healthy"
else
    log_error "  ✗ Redis health check failed"
fi

echo ""

# Step 12: 최종 결과
log_success "╔══════════════════════════════════════════════════════════════╗"
log_success "║          배포 완료!                                          ║"
log_success "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "접속 정보:"
echo "  🌐 Frontend:    http://139.150.11.99"
echo "  🌐 Frontend:    http://139.150.11.99:3000"
echo "  📚 API Docs:    http://139.150.11.99:8000/docs"
echo "  ❤️  Health:      http://139.150.11.99:8000/health"
echo "  🔧 Backend API: http://139.150.11.99:8000"
echo ""
echo "테스트 계정:"
echo "  👨‍💼 관리자: admin@example.com / admin123"
echo "  🚗 드라이버 1: driver1 / password123"
echo "  🚗 드라이버 2: driver2 / password123"
echo ""
echo "컨테이너 관리:"
echo "  - 로그 확인: docker-compose logs -f"
echo "  - 상태 확인: docker-compose ps"
echo "  - 재시작: docker-compose restart"
echo "  - 중지: docker-compose down"
echo ""
log_info "배포 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "빌드 소요 시간: ${DURATION}초 ($(($DURATION / 60))분)"

# Step 13: 모니터링 정보
echo ""
log_info "다음 명령으로 실시간 로그를 확인하세요:"
echo "  docker-compose logs -f --tail=100"
