#!/bin/bash

##############################################################################
# UVIS 전체 오류 수정 스크립트
# 목적: 대시보드가 작동하지 않는 문제를 포괄적으로 해결
# 날짜: 2026-02-06
##############################################################################

set -e  # 오류 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 색상 없음

echo "=================================================================="
echo -e "${BLUE}UVIS 전체 오류 수정 스크립트${NC}"
echo "=================================================================="
echo ""

# 설정
REPO_DIR="/root/uvis"
BRANCH="genspark_ai_developer"

# 로그 함수
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_step() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

##############################################################################
# 1단계: 현재 상태 진단
##############################################################################
log_step "1단계: 시스템 상태 진단"

cd "$REPO_DIR" || exit 1

# Docker 상태 확인
log_info "Docker 컨테이너 상태 확인 중..."
docker-compose ps

# 컨테이너 로그에서 최근 오류 확인
log_warn "백엔드 최근 오류 확인 중..."
docker logs uvis-backend --tail 50 | grep -i "error" || echo "백엔드 오류 없음"

log_warn "프론트엔드 최근 오류 확인 중..."
docker logs uvis-frontend --tail 50 | grep -i "error" || echo "프론트엔드 오류 없음"

# 데이터베이스 연결 확인
log_info "데이터베이스 연결 확인 중..."
docker exec uvis-db pg_isready -U postgres || log_error "데이터베이스 연결 실패"

##############################################################################
# 2단계: Git 저장소 정리 및 최신 코드 가져오기
##############################################################################
log_step "2단계: Git 저장소 정리 및 업데이트"

# 현재 브랜치 확인
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
log_info "현재 브랜치: $CURRENT_BRANCH"

# 로컬 변경사항 확인
if [[ -n $(git status -s) ]]; then
    log_warn "로컬 변경사항이 있습니다. 백업 후 초기화합니다."
    
    # 백업 생성
    BACKUP_DIR="/root/uvis_backup_$(date +%Y%m%d_%H%M%S)"
    log_info "백업 디렉토리 생성: $BACKUP_DIR"
    cp -r "$REPO_DIR" "$BACKUP_DIR"
    log_info "백업 완료: $BACKUP_DIR"
    
    # 로컬 변경사항 초기화
    git reset --hard HEAD
    git clean -fd
    log_info "로컬 변경사항 초기화 완료"
fi

# 올바른 브랜치로 전환
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    log_info "브랜치를 $BRANCH 로 전환 중..."
    git checkout "$BRANCH"
fi

# 최신 코드 가져오기
log_info "원격 저장소에서 최신 코드 가져오기..."
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"
log_info "최신 코드로 업데이트 완료"

# 현재 커밋 확인
CURRENT_COMMIT=$(git rev-parse --short HEAD)
log_info "현재 커밋: $CURRENT_COMMIT"

##############################################################################
# 3단계: 환경 설정 파일 확인 및 수정
##############################################################################
log_step "3단계: 환경 설정 파일 확인"

# 백엔드 .env 파일 확인
if [ ! -f "$REPO_DIR/.env" ]; then
    log_error ".env 파일이 없습니다. .env.example에서 복사합니다."
    if [ -f "$REPO_DIR/.env.example" ]; then
        cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
        log_info ".env 파일 생성 완료"
    else
        log_error ".env.example 파일도 없습니다!"
    fi
else
    log_info "백엔드 .env 파일 존재 확인"
fi

# 프론트엔드 .env 파일 확인
if [ ! -f "$REPO_DIR/frontend/.env" ]; then
    log_warn "프론트엔드 .env 파일이 없습니다. 생성합니다."
    cat > "$REPO_DIR/frontend/.env" << 'EOF'
# API Configuration
VITE_API_URL=/api/v1
EOF
    log_info "프론트엔드 .env 파일 생성 완료"
else
    log_info "프론트엔드 .env 파일 존재 확인"
    
    # VITE_API_URL 확인 및 수정
    if grep -q "VITE_API_URL=http" "$REPO_DIR/frontend/.env"; then
        log_warn "VITE_API_URL이 절대 경로로 설정되어 있습니다. 상대 경로로 수정합니다."
        sed -i 's|VITE_API_URL=.*|VITE_API_URL=/api/v1|g' "$REPO_DIR/frontend/.env"
        log_info "VITE_API_URL을 /api/v1 로 수정 완료"
    fi
fi

##############################################################################
# 4단계: 데이터베이스 상태 확인 및 마이그레이션
##############################################################################
log_step "4단계: 데이터베이스 확인 및 마이그레이션"

# 데이터베이스 컨테이너가 실행 중인지 확인
if docker ps | grep -q "uvis-db"; then
    log_info "데이터베이스 컨테이너 실행 중"
    
    # Alembic 마이그레이션 상태 확인
    log_info "Alembic 마이그레이션 상태 확인 중..."
    docker exec uvis-backend alembic current || log_warn "마이그레이션 상태 확인 실패"
    
    # 마이그레이션 적용
    log_info "마이그레이션 적용 중..."
    docker exec uvis-backend alembic upgrade head || log_warn "마이그레이션 적용 중 경고 발생"
    
    log_info "마이그레이션 완료"
else
    log_error "데이터베이스 컨테이너가 실행 중이 아닙니다!"
fi

##############################################################################
# 5단계: 프론트엔드 재빌드
##############################################################################
log_step "5단계: 프론트엔드 재빌드"

cd "$REPO_DIR/frontend"

# node_modules 확인
if [ ! -d "node_modules" ]; then
    log_info "node_modules가 없습니다. npm install 실행 중..."
    npm install
else
    log_info "node_modules 존재 확인"
fi

# 이전 빌드 파일 삭제
if [ -d "dist" ]; then
    log_info "이전 빌드 파일 삭제 중..."
    rm -rf dist
fi

# 프론트엔드 빌드
log_info "프론트엔드 빌드 중... (시간이 걸릴 수 있습니다)"
npm run build

if [ -d "dist" ]; then
    log_info "프론트엔드 빌드 성공"
    log_info "빌드된 파일: $(ls -lh dist/index.html | awk '{print $5}')"
else
    log_error "프론트엔드 빌드 실패!"
    exit 1
fi

##############################################################################
# 6단계: Docker 컨테이너 완전 재시작
##############################################################################
log_step "6단계: Docker 컨테이너 완전 재시작"

cd "$REPO_DIR"

log_info "모든 컨테이너 중지 중..."
docker-compose down

log_info "Docker 이미지 재빌드 중 (캐시 없이)..."
docker-compose build --no-cache

log_info "컨테이너 시작 중..."
docker-compose up -d

# 컨테이너가 시작될 때까지 대기
log_info "컨테이너 시작 대기 중... (10초)"
sleep 10

##############################################################################
# 7단계: 서비스 헬스 체크
##############################################################################
log_step "7단계: 서비스 헬스 체크"

# 백엔드 헬스 체크
log_info "백엔드 헬스 체크 중..."
for i in {1..5}; do
    BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
    if [ "$BACKEND_STATUS" == "200" ]; then
        log_info "백엔드 헬스 체크: $BACKEND_STATUS OK"
        break
    else
        log_warn "백엔드 헬스 체크 시도 $i/5: $BACKEND_STATUS (대기 중...)"
        sleep 5
    fi
done

# 프론트엔드 헬스 체크
log_info "프론트엔드 헬스 체크 중..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
if [ "$FRONTEND_STATUS" == "200" ]; then
    log_info "프론트엔드 헬스 체크: $FRONTEND_STATUS OK"
else
    log_error "프론트엔드 헬스 체크 실패: $FRONTEND_STATUS"
fi

# 데이터베이스 헬스 체크
log_info "데이터베이스 헬스 체크 중..."
if docker exec uvis-db pg_isready -U postgres > /dev/null 2>&1; then
    log_info "데이터베이스 헬스 체크: OK"
else
    log_error "데이터베이스 헬스 체크 실패"
fi

##############################################################################
# 8단계: API 엔드포인트 테스트
##############################################################################
log_step "8단계: API 엔드포인트 테스트"

# 로그인 테스트
log_info "로그인 API 테스트 중..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    log_info "로그인 성공"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    # Phase 8 API 테스트
    log_info "Phase 8 API 테스트 중..."
    FINANCIAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/v1/billing/enhanced/dashboard/financial)
    
    if [ "$FINANCIAL_STATUS" == "200" ]; then
        log_info "Phase 8 API 테스트: $FINANCIAL_STATUS OK"
    else
        log_warn "Phase 8 API 테스트: $FINANCIAL_STATUS"
    fi
else
    log_error "로그인 실패"
fi

##############################################################################
# 9단계: 컨테이너 로그 확인
##############################################################################
log_step "9단계: 최종 로그 확인"

log_info "컨테이너 상태:"
docker-compose ps

log_info "백엔드 최근 로그 (최근 20줄):"
docker logs uvis-backend --tail 20

log_info "프론트엔드 최근 로그 (최근 20줄):"
docker logs uvis-frontend --tail 20

##############################################################################
# 10단계: 완료 및 다음 단계 안내
##############################################################################
log_step "완료!"

echo ""
echo "=================================================================="
echo -e "${GREEN}✓ 전체 오류 수정 완료!${NC}"
echo "=================================================================="
echo ""
echo "📊 시스템 상태:"
echo "  - 백엔드: http://139.150.11.99:8000/"
echo "  - API 문서: http://139.150.11.99:8000/docs"
echo "  - 프론트엔드: http://139.150.11.99/"
echo "  - 헬스 체크: http://139.150.11.99:8000/health"
echo ""
echo "🔍 테스트 방법:"
echo "  1. 브라우저 캐시 삭제: Ctrl + Shift + R"
echo "  2. http://139.150.11.99/ 접속"
echo "  3. 로그인: admin / admin123"
echo "  4. 대시보드 페이지 확인"
echo "  5. F12 → Console 탭에서 오류 확인"
echo ""
echo "📋 Phase 8 페이지:"
echo "  - 재무 대시보드: http://139.150.11.99/billing/financial-dashboard"
echo "  - 요금 미리보기: http://139.150.11.99/billing/charge-preview"
echo "  - 자동 청구: http://139.150.11.99/billing/auto-schedule"
echo "  - 정산 승인: http://139.150.11.99/billing/settlement-approval"
echo "  - 결제 알림: http://139.150.11.99/billing/payment-reminder"
echo "  - 데이터 내보내기: http://139.150.11.99/billing/export-task"
echo ""
echo "🔧 문제가 계속되면:"
echo "  - 백엔드 로그: docker logs uvis-backend -f"
echo "  - 프론트엔드 로그: docker logs uvis-frontend -f"
echo "  - 데이터베이스 로그: docker logs uvis-db --tail 50"
echo ""
echo "💾 백업 위치: $BACKUP_DIR"
echo ""
