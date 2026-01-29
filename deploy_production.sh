#!/bin/bash

################################################################################
# UVIS 프로덕션 배포 스크립트
# 온도 자동입력 기능 포함 최신 버전 배포
# 
# 사용법:
#   서버에서 직접 실행:
#   bash deploy_production.sh
#
# 또는 원격에서:
#   ssh root@139.150.11.99 'bash -s' < deploy_production.sh
################################################################################

set -e  # 에러 발생 시 즉시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
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

# 배포 정보
DEPLOY_DATE=$(date '+%Y-%m-%d %H:%M:%S')
PROJECT_DIR="/root/uvis"
COMPOSE_FILE="docker-compose.prod.yml"
TARGET_COMMIT="7780df5"  # 또는 그 이후 버전

################################################################################
# 1. 시작 안내
################################################################################
echo ""
echo "=========================================="
echo "  🚀 UVIS 프로덕션 배포 시작"
echo "=========================================="
echo "배포 시작 시간: $DEPLOY_DATE"
echo "대상 서버: 139.150.11.99"
echo "프로젝트 경로: $PROJECT_DIR"
echo ""

################################################################################
# 2. 사전 확인
################################################################################
log_info "사전 확인 단계..."

# 프로젝트 디렉토리 존재 확인
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "프로젝트 디렉토리가 존재하지 않습니다: $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR
log_success "프로젝트 디렉토리 확인 완료"

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    log_error "Docker가 설치되어 있지 않습니다"
    exit 1
fi
log_success "Docker 확인 완료: $(docker --version)"

# Docker Compose 설치 확인
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose가 설치되어 있지 않습니다"
    exit 1
fi
log_success "Docker Compose 확인 완료: $(docker-compose --version)"

# Git 설치 확인
if ! command -v git &> /dev/null; then
    log_error "Git이 설치되어 있지 않습니다"
    exit 1
fi
log_success "Git 확인 완료: $(git --version)"

################################################################################
# 3. 현재 상태 백업
################################################################################
log_info "현재 상태 백업 중..."

BACKUP_DIR="/root/uvis_backups"
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 현재 커밋 정보 저장
git log --oneline -1 > "$BACKUP_DIR/$BACKUP_NAME.commit"
log_success "현재 커밋 정보 백업: $BACKUP_DIR/$BACKUP_NAME.commit"

# 현재 .env 파일 백업
if [ -f "backend/.env" ]; then
    cp backend/.env "$BACKUP_DIR/$BACKUP_NAME.env"
    log_success ".env 파일 백업 완료"
fi

################################################################################
# 4. Git 상태 확인 및 업데이트
################################################################################
log_info "Git 저장소 업데이트 중..."

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
log_info "현재 브랜치: $CURRENT_BRANCH"

# Unstaged 변경사항 확인
if [ -n "$(git status --porcelain)" ]; then
    log_warning "작업 디렉토리에 변경사항이 있습니다"
    git status --short
    
    # 사용자 확인 (자동화를 위해 주석 처리 가능)
    # read -p "계속하시겠습니까? (y/n): " -n 1 -r
    # echo
    # if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    #     log_error "배포 취소됨"
    #     exit 1
    # fi
    
    # Stash 생성
    log_warning "변경사항을 임시 저장합니다 (stash)"
    git stash save "Auto-stash before deployment - $DEPLOY_DATE"
fi

# main 브랜치로 전환
if [ "$CURRENT_BRANCH" != "main" ]; then
    log_info "main 브랜치로 전환 중..."
    git checkout main
fi

# 원격 저장소에서 가져오기
log_info "원격 저장소에서 최신 코드 가져오는 중..."
git fetch origin main

# 로컬 main 업데이트
log_info "로컬 main 브랜치 업데이트 중..."
git pull origin main

# 현재 커밋 확인
CURRENT_COMMIT=$(git rev-parse --short HEAD)
log_success "현재 커밋: $CURRENT_COMMIT"

# 목표 커밋과 비교
if [ "$CURRENT_COMMIT" != "$TARGET_COMMIT" ]; then
    COMMIT_MESSAGE=$(git log --oneline -1)
    log_warning "목표 커밋($TARGET_COMMIT)과 다른 버전입니다: $CURRENT_COMMIT"
    log_info "현재 커밋: $COMMIT_MESSAGE"
else
    log_success "목표 커밋과 일치합니다"
fi

################################################################################
# 5. 서비스 중지
################################################################################
log_info "서비스 중지 중..."

if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    docker-compose -f $COMPOSE_FILE down
    log_success "서비스 중지 완료"
else
    log_info "실행 중인 서비스가 없습니다"
fi

################################################################################
# 6. Docker 이미지 빌드
################################################################################
log_info "Docker 이미지 빌드 중..."

# 프론트엔드 빌드 (캐시 없이)
log_info "프론트엔드 이미지 빌드 중 (캐시 없이)..."
docker-compose -f $COMPOSE_FILE build --no-cache frontend
log_success "프론트엔드 이미지 빌드 완료"

# 백엔드 빌드
log_info "백엔드 이미지 빌드 중..."
docker-compose -f $COMPOSE_FILE build backend
log_success "백엔드 이미지 빌드 완료"

################################################################################
# 7. 서비스 시작
################################################################################
log_info "서비스 시작 중..."

docker-compose -f $COMPOSE_FILE up -d

log_success "서비스 시작 완료"

################################################################################
# 8. 서비스 상태 확인
################################################################################
log_info "서비스 안정화 대기 중..."
sleep 15

log_info "서비스 상태 확인 중..."
echo ""
docker-compose -f $COMPOSE_FILE ps
echo ""

# 각 서비스 상태 확인
SERVICES=("frontend" "backend" "db" "redis" "nginx")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    if docker-compose -f $COMPOSE_FILE ps $service | grep -q "Up"; then
        log_success "✓ $service: Running"
    else
        log_error "✗ $service: Not Running"
        ALL_HEALTHY=false
    fi
done

################################################################################
# 9. Health Check
################################################################################
log_info "Health check 수행 중..."

# Backend health check
sleep 5
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    log_success "✓ Backend health check passed"
else
    log_warning "✗ Backend health check failed (retry in 10s)"
    sleep 10
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log_success "✓ Backend health check passed (retry)"
    else
        log_error "✗ Backend health check failed"
        ALL_HEALTHY=false
    fi
fi

# Frontend check
if curl -sf http://localhost:3000 > /dev/null 2>&1; then
    log_success "✓ Frontend health check passed"
else
    log_warning "✗ Frontend health check failed"
    ALL_HEALTHY=false
fi

################################################################################
# 10. 데이터베이스 마이그레이션 확인
################################################################################
log_info "데이터베이스 마이그레이션 상태 확인 중..."

# Alembic 현재 버전 확인
MIGRATION_STATUS=$(docker-compose -f $COMPOSE_FILE exec -T backend alembic current 2>&1 || echo "ERROR")

if echo "$MIGRATION_STATUS" | grep -q "ERROR"; then
    log_warning "마이그레이션 상태를 확인할 수 없습니다"
else
    log_success "마이그레이션 상태 확인 완료"
    echo "$MIGRATION_STATUS" | sed 's/^/  /'
fi

################################################################################
# 11. 로그 확인
################################################################################
log_info "최근 로그 확인 중..."
echo ""
echo "=== Frontend 로그 (최근 20줄) ==="
docker-compose -f $COMPOSE_FILE logs --tail=20 frontend
echo ""
echo "=== Backend 로그 (최근 20줄) ==="
docker-compose -f $COMPOSE_FILE logs --tail=20 backend
echo ""

################################################################################
# 12. 배포 결과 요약
################################################################################
echo ""
echo "=========================================="
echo "  🎉 배포 완료"
echo "=========================================="
echo "배포 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo "배포된 커밋: $CURRENT_COMMIT"
echo "백업 위치: $BACKUP_DIR/$BACKUP_NAME"
echo ""

if [ "$ALL_HEALTHY" = true ]; then
    log_success "✅ 모든 서비스가 정상 작동 중입니다"
else
    log_warning "⚠️  일부 서비스에 문제가 있습니다. 로그를 확인하세요."
fi

echo ""
echo "=========================================="
echo "  📊 접속 정보"
echo "=========================================="
echo "Frontend:  http://139.150.11.99"
echo "Backend:   http://139.150.11.99:8000"
echo "API Docs:  http://139.150.11.99:8000/docs"
echo ""

################################################################################
# 13. 다음 단계 안내
################################################################################
echo "=========================================="
echo "  📝 다음 단계"
echo "=========================================="
echo "1. 브라우저에서 http://139.150.11.99/orders 접속"
echo "2. 신규 주문 등록 테스트"
echo "3. 온도대 선택 시 자동 입력 확인:"
echo "   - 냉동: -30°C ~ -18°C"
echo "   - 냉장: 0°C ~ 6°C"
echo "   - 상온: -30°C ~ 60°C"
echo "4. 주문 등록 완료 테스트"
echo "5. 팀에 배포 완료 알림"
echo ""

################################################################################
# 14. 모니터링 명령어 안내
################################################################################
echo "=========================================="
echo "  🔍 모니터링 명령어"
echo "=========================================="
echo "# 서비스 상태 확인"
echo "docker-compose -f $COMPOSE_FILE ps"
echo ""
echo "# 실시간 로그 확인"
echo "docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "# 에러 로그만 확인"
echo "docker-compose -f $COMPOSE_FILE logs | grep -i error"
echo ""
echo "# 서비스 재시작"
echo "docker-compose -f $COMPOSE_FILE restart [service-name]"
echo ""

################################################################################
# 15. 롤백 안내
################################################################################
echo "=========================================="
echo "  🔙 롤백이 필요한 경우"
echo "=========================================="
echo "# 이전 커밋으로 롤백"
echo "git checkout <previous-commit>"
echo "bash deploy_production.sh"
echo ""
echo "# 백업에서 복원"
echo "cat $BACKUP_DIR/$BACKUP_NAME.commit"
echo ""

log_success "배포 스크립트 완료! 🎉"
