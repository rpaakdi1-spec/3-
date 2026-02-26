#!/bin/bash

###############################################################################
# UVIS Phase 16 프로덕션 배포 스크립트
# 버전: 1.0
# 날짜: 2026-02-26
###############################################################################

set -e  # 에러 발생 시 즉시 중단

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

# 배포 시작
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     UVIS Phase 16 프로덕션 배포 스크립트 v1.0            ║"
echo "║     FCM + File Upload + Real-time Chat                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: 환경 확인
log_info "Step 1: 환경 확인 중..."

if [ ! -f ".env" ]; then
    log_error ".env 파일이 없습니다!"
    log_info "docs/PRODUCTION_DEPLOYMENT_GUIDE.md를 참조하여 .env 파일을 생성하세요."
    exit 1
fi

if [ ! -f "frontend/.env" ]; then
    log_warning "frontend/.env 파일이 없습니다."
    log_info "FCM 기능을 사용하려면 frontend/.env 파일이 필요합니다."
fi

log_success "환경 파일 확인 완료"

# Step 2: Git 저장소 업데이트
log_info "Step 2: Git 저장소 업데이트 중..."

if [ -d ".git" ]; then
    git fetch origin
    CURRENT_BRANCH=$(git branch --show-current)
    log_info "현재 브랜치: $CURRENT_BRANCH"
    
    read -p "최신 변경사항을 pull 하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git pull origin $CURRENT_BRANCH
        log_success "Git pull 완료"
    fi
else
    log_warning "Git 저장소가 아닙니다. 건너뜁니다."
fi

# Step 3: 프론트엔드 빌드
log_info "Step 3: 프론트엔드 빌드 중..."

cd frontend

if [ ! -d "node_modules" ]; then
    log_info "npm install 실행 중..."
    npm install
fi

log_info "프로덕션 빌드 시작..."
npm run build

if [ $? -eq 0 ]; then
    log_success "프론트엔드 빌드 완료"
    BUILD_SIZE=$(du -sh dist | cut -f1)
    log_info "빌드 크기: $BUILD_SIZE"
else
    log_error "프론트엔드 빌드 실패!"
    exit 1
fi

cd ..

# Step 4: Docker 이미지 빌드
log_info "Step 4: Docker 이미지 빌드 중..."

read -p "기존 컨테이너를 중지하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "기존 컨테이너 중지 중..."
    docker-compose down
    log_success "컨테이너 중지 완료"
fi

read -p "캐시 없이 새로 빌드하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "캐시 없이 빌드 중... (시간이 걸릴 수 있습니다)"
    docker-compose build --no-cache
else
    log_info "빌드 중..."
    docker-compose build
fi

if [ $? -eq 0 ]; then
    log_success "Docker 이미지 빌드 완료"
else
    log_error "Docker 이미지 빌드 실패!"
    exit 1
fi

# Step 5: 컨테이너 시작
log_info "Step 5: 컨테이너 시작 중..."

docker-compose up -d

if [ $? -eq 0 ]; then
    log_success "컨테이너 시작 완료"
else
    log_error "컨테이너 시작 실패!"
    exit 1
fi

# 컨테이너가 올라올 때까지 대기
log_info "컨테이너 초기화 대기 중... (30초)"
sleep 30

# Step 6: 상태 확인
log_info "Step 6: 서비스 상태 확인 중..."

echo ""
echo "═══════════════════════════════════════"
echo "  컨테이너 상태"
echo "═══════════════════════════════════════"
docker-compose ps
echo ""

# 헬스 체크
log_info "백엔드 헬스 체크..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)

if [ "$BACKEND_HEALTH" == "200" ]; then
    log_success "백엔드 정상 (HTTP $BACKEND_HEALTH)"
else
    log_error "백엔드 비정상 (HTTP $BACKEND_HEALTH)"
fi

log_info "프론트엔드 헬스 체크..."
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health 2>/dev/null || echo "000")

if [ "$FRONTEND_HEALTH" == "200" ]; then
    log_success "프론트엔드 정상 (HTTP $FRONTEND_HEALTH)"
else
    log_warning "프론트엔드 헬스 체크 실패 (HTTP $FRONTEND_HEALTH)"
fi

# MinIO 체크
log_info "MinIO 상태 확인..."
MINIO_HEALTH=$(docker-compose exec -T minio curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/minio/health/live 2>/dev/null || echo "000")

if [ "$MINIO_HEALTH" == "200" ]; then
    log_success "MinIO 정상 (HTTP $MINIO_HEALTH)"
else
    log_warning "MinIO 상태 확인 실패 (HTTP $MINIO_HEALTH)"
fi

# Step 7: MinIO 버킷 확인
log_info "Step 7: MinIO 버킷 확인 중..."

echo ""
read -p "MinIO 버킷을 생성하시겠습니까? (처음 배포 시 필수) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "MinIO 버킷 생성 중..."
    
    # mc (MinIO Client) 설치 확인
    if ! command -v mc &> /dev/null; then
        log_info "MinIO Client 설치 중..."
        wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
        chmod +x /usr/local/bin/mc
    fi
    
    # MinIO alias 설정
    MINIO_USER=$(grep MINIO_ROOT_USER .env | cut -d '=' -f2)
    MINIO_PASS=$(grep MINIO_ROOT_PASSWORD .env | cut -d '=' -f2)
    
    mc alias set local http://localhost:9000 ${MINIO_USER:-minioadmin} ${MINIO_PASS:-minioadmin123}
    
    # 버킷 생성
    mc mb local/uvis-files 2>/dev/null || log_warning "버킷이 이미 존재합니다"
    
    # 폴더 생성 (더미 파일로)
    echo "placeholder" | mc pipe local/uvis-files/uploads/.keep
    echo "placeholder" | mc pipe local/uvis-files/images/.keep
    echo "placeholder" | mc pipe local/uvis-files/documents/.keep
    echo "placeholder" | mc pipe local/uvis-files/orders/.keep
    echo "placeholder" | mc pipe local/uvis-files/vehicles/.keep
    
    log_success "MinIO 버킷 및 폴더 생성 완료"
fi

# Step 8: 배포 요약
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  배포 완료!                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 서비스 접속 정보:"
echo "  - 프론트엔드: http://$(hostname -I | awk '{print $1}')"
echo "  - 백엔드 API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  - API 문서: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "  - MinIO Console: http://$(hostname -I | awk '{print $1}'):9001"
echo ""
echo "🔧 다음 단계:"
echo "  1. MinIO Console에서 버킷 확인"
echo "  2. Firebase 프로젝트 설정 (FCM)"
echo "  3. 기능 테스트 실행"
echo "  4. 로그 모니터링: docker-compose logs -f"
echo ""
echo "📚 문서:"
echo "  - docs/PRODUCTION_DEPLOYMENT_GUIDE.md"
echo "  - docs/PHASE_16_COMPLETION_REPORT.md"
echo ""

read -p "로그를 실시간으로 보시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose logs -f
fi
