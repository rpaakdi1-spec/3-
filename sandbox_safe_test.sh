#!/bin/bash

################################################################################
# Phase 10 샌드박스 안전 테스트 스크립트
# 소요 시간: 약 10분
# Docker 없이 실행 가능
################################################################################

set -e

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/tmp/sandbox_test_$(date '+%Y%m%d_%H%M%S').log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Phase 10 샌드박스 안전 테스트"
echo "시작: $TIMESTAMP"
echo "로그: $LOG_FILE"
echo "=========================================="
echo ""

# Error counter
ERROR_COUNT=0

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
    echo "[TEST] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    echo "[✓] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    echo "[✗] $1" >> "$LOG_FILE"
    ((ERROR_COUNT++))
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    echo "[⚠] $1" >> "$LOG_FILE"
}

################################################################################
# 1. Git 상태 확인
################################################################################
log_test "1. Git 상태 확인 중..."
cd /home/user/webapp

if git status &>/dev/null; then
    BRANCH=$(git branch --show-current)
    log_success "현재 브랜치: $BRANCH"
    
    UNCOMMITTED=$(git status --porcelain | wc -l)
    if [ "$UNCOMMITTED" -eq 0 ]; then
        log_success "커밋되지 않은 변경사항 없음"
    else
        log_warning "$UNCOMMITTED개의 커밋되지 않은 변경사항 존재"
        git status --short >> "$LOG_FILE"
    fi
    
    # 최신 커밋 확인
    LAST_COMMIT=$(git log -1 --oneline)
    log_success "최신 커밋: $LAST_COMMIT"
else
    log_error "Git 저장소가 아닙니다"
fi

echo ""

################################################################################
# 2. Phase 10 파일 존재 확인
################################################################################
log_test "2. Phase 10 핵심 파일 확인 중..."

PHASE10_FILES=(
    "FCM_SERVICE_FIX_COMPLETE.md"
    "PHASE10_COMPLETE_FINAL_REPORT.md"
    "PHASE10_MERGE_COMPLETE.md"
    "PHASE10_STAGING_DEPLOYMENT_FIX.md"
    "SERVER_SANDBOX_SYNC_GUIDE.md"
    "backend/app/api/v1/endpoints/dispatch_rules.py"
    "backend/alembic/versions/add_dispatch_rules_tables.py"
    "frontend/src/pages/DispatchRulesPage.tsx"
    "frontend/src/components/RuleBuilderCanvas.tsx"
    "frontend/src/components/RuleTestDialog.tsx"
    "frontend/src/components/RuleLogsDialog.tsx"
    "frontend/src/components/RulePerformanceDialog.tsx"
    "frontend/src/components/RuleSimulationDialog.tsx"
    "frontend/src/components/RuleTemplateGallery.tsx"
    "frontend/src/components/RuleVersionHistory.tsx"
    "frontend/src/services/fcmService.ts"
)

MISSING_FILES=0
for file in "${PHASE10_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "✓ $file"
    else
        log_error "✗ $file (누락)"
        ((MISSING_FILES++))
    fi
done

if [ "$MISSING_FILES" -eq 0 ]; then
    log_success "모든 Phase 10 파일 존재 확인"
else
    log_error "$MISSING_FILES개의 파일 누락"
fi

echo ""

################################################################################
# 3. FCM Service Toast 수정 확인
################################################################################
log_test "3. FCM Service Toast 수정 확인 중..."

if [ -f "frontend/src/services/fcmService.ts" ]; then
    if grep -q "toast.custom" "frontend/src/services/fcmService.ts"; then
        log_error "fcmService.ts에 toast.custom이 여전히 존재합니다"
    else
        log_success "toast.custom 제거 확인"
    fi
    
    if grep -q "toast(\`\${payload.notification.title}: \${payload.notification.body}\`" "frontend/src/services/fcmService.ts"; then
        log_success "새로운 toast 형식 확인"
    else
        log_warning "새로운 toast 형식을 찾을 수 없습니다"
    fi
else
    log_error "fcmService.ts 파일을 찾을 수 없습니다"
fi

echo ""

################################################################################
# 4. Backend Python 문법 체크
################################################################################
log_test "4. Backend Python 문법 체크 중..."

if command -v python3 &>/dev/null; then
    PYTHON_ERRORS=0
    
    # dispatch_rules.py 문법 체크
    if [ -f "backend/app/api/v1/endpoints/dispatch_rules.py" ]; then
        if python3 -m py_compile "backend/app/api/v1/endpoints/dispatch_rules.py" 2>/dev/null; then
            log_success "dispatch_rules.py 문법 체크 통과"
        else
            log_error "dispatch_rules.py 문법 오류"
            ((PYTHON_ERRORS++))
        fi
    else
        log_error "dispatch_rules.py 파일 없음"
        ((PYTHON_ERRORS++))
    fi
    
    # main.py 문법 체크
    if [ -f "backend/main.py" ]; then
        if python3 -m py_compile "backend/main.py" 2>/dev/null; then
            log_success "main.py 문법 체크 통과"
        else
            log_error "main.py 문법 오류"
            ((PYTHON_ERRORS++))
        fi
    fi
    
    if [ "$PYTHON_ERRORS" -eq 0 ]; then
        log_success "모든 Python 파일 문법 체크 통과"
    else
        log_error "$PYTHON_ERRORS개의 Python 파일에 문법 오류"
    fi
else
    log_warning "Python3가 설치되지 않음 - 문법 체크 건너뜀"
fi

echo ""

################################################################################
# 5. Frontend 패키지 확인
################################################################################
log_test "5. Frontend 패키지 확인 중..."

cd /home/user/webapp/frontend

if [ -f "package.json" ]; then
    log_success "package.json 존재"
    
    # Phase 10 필수 패키지 확인
    REQUIRED_PACKAGES=(
        "reactflow"
        "@mui/material"
        "@mui/lab"
        "@mui/icons-material"
    )
    
    MISSING_PACKAGES=0
    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        if grep -q "\"$pkg\"" package.json; then
            log_success "✓ $pkg"
        else
            log_error "✗ $pkg (package.json에 없음)"
            ((MISSING_PACKAGES++))
        fi
    done
    
    if [ "$MISSING_PACKAGES" -eq 0 ]; then
        log_success "모든 필수 패키지가 package.json에 존재"
    else
        log_error "$MISSING_PACKAGES개의 필수 패키지 누락"
    fi
else
    log_error "package.json을 찾을 수 없습니다"
fi

echo ""

################################################################################
# 6. Timeline 컴포넌트 Import 확인
################################################################################
log_test "6. RuleVersionHistory.tsx Timeline Import 확인 중..."

if [ -f "src/components/RuleVersionHistory.tsx" ]; then
    if grep -q "from '@mui/lab'" "src/components/RuleVersionHistory.tsx"; then
        log_success "Timeline 컴포넌트가 @mui/lab에서 import됨"
    elif grep -q "from '@mui/material'" "src/components/RuleVersionHistory.tsx"; then
        log_error "Timeline 컴포넌트가 여전히 @mui/material에서 import됨 (수정 필요)"
    else
        log_warning "Timeline import를 찾을 수 없습니다"
    fi
else
    log_error "RuleVersionHistory.tsx 파일 없음"
fi

echo ""

################################################################################
# 7. TypeScript 파일 구조 확인
################################################################################
log_test "7. TypeScript 파일 구조 확인 중..."

REQUIRED_TS_FILES=(
    "src/pages/DispatchRulesPage.tsx"
    "src/components/RuleBuilderCanvas.tsx"
    "src/components/RuleTestDialog.tsx"
    "src/components/RuleLogsDialog.tsx"
    "src/components/RulePerformanceDialog.tsx"
    "src/components/RuleSimulationDialog.tsx"
    "src/components/RuleTemplateGallery.tsx"
    "src/components/RuleVersionHistory.tsx"
)

MISSING_TS=0
for file in "${REQUIRED_TS_FILES[@]}"; do
    if [ -f "$file" ]; then
        # 기본 React 컴포넌트 구조 확인
        if grep -q "export.*function\|export.*const.*=.*(" "$file"; then
            log_success "✓ $file (export 확인)"
        else
            log_warning "✓ $file (export 미확인)"
        fi
    else
        log_error "✗ $file (누락)"
        ((MISSING_TS++))
    fi
done

if [ "$MISSING_TS" -eq 0 ]; then
    log_success "모든 TypeScript 컴포넌트 존재"
else
    log_error "$MISSING_TS개의 TypeScript 파일 누락"
fi

echo ""

################################################################################
# 8. Backend Alembic 마이그레이션 파일 확인
################################################################################
log_test "8. Alembic 마이그레이션 파일 확인 중..."

cd /home/user/webapp/backend

if [ -f "alembic/versions/add_dispatch_rules_tables.py" ]; then
    log_success "add_dispatch_rules_tables.py 존재"
    
    # 필수 테이블 생성 코드 확인
    if grep -q "'dispatch_rules'" "alembic/versions/add_dispatch_rules_tables.py"; then
        log_success "dispatch_rules 테이블 생성 코드 확인"
    else
        log_error "dispatch_rules 테이블 생성 코드 없음"
    fi
    
    if grep -q "'rule_execution_logs'" "alembic/versions/add_dispatch_rules_tables.py"; then
        log_success "rule_execution_logs 테이블 생성 코드 확인"
    else
        log_error "rule_execution_logs 테이블 생성 코드 없음"
    fi
else
    log_error "add_dispatch_rules_tables.py 마이그레이션 파일 없음"
fi

echo ""

################################################################################
# 9. Backend API 엔드포인트 코드 확인
################################################################################
log_test "9. Backend API 엔드포인트 확인 중..."

if [ -f "app/api/v1/endpoints/dispatch_rules.py" ]; then
    log_success "dispatch_rules.py 존재"
    
    # 필수 엔드포인트 확인
    ENDPOINTS=(
        "@router.post"
        "@router.get"
        "@router.put"
        "@router.delete"
    )
    
    for endpoint in "${ENDPOINTS[@]}"; do
        COUNT=$(grep -c "$endpoint" "app/api/v1/endpoints/dispatch_rules.py" || echo "0")
        if [ "$COUNT" -gt 0 ]; then
            log_success "$endpoint 엔드포인트 $COUNT개 발견"
        else
            log_warning "$endpoint 엔드포인트 없음"
        fi
    done
else
    log_error "dispatch_rules.py 파일 없음"
fi

echo ""

################################################################################
# 10. 문서 파일 확인
################################################################################
log_test "10. Phase 10 문서 파일 확인 중..."

cd /home/user/webapp

PHASE10_DOCS=(
    "FCM_SERVICE_FIX_COMPLETE.md"
    "PHASE10_COMPLETE_FINAL_REPORT.md"
    "PHASE10_MERGE_COMPLETE.md"
    "PHASE10_PR_REVIEW.md"
    "PHASE10_STAGING_DEPLOYMENT_FIX.md"
    "SERVER_SANDBOX_SYNC_GUIDE.md"
)

MISSING_DOCS=0
for doc in "${PHASE10_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        SIZE=$(wc -c < "$doc")
        log_success "✓ $doc (${SIZE} bytes)"
    else
        log_error "✗ $doc (누락)"
        ((MISSING_DOCS++))
    fi
done

if [ "$MISSING_DOCS" -eq 0 ]; then
    log_success "모든 문서 파일 존재"
else
    log_error "$MISSING_DOCS개의 문서 파일 누락"
fi

echo ""

################################################################################
# 최종 결과
################################################################################
echo "=========================================="
echo -e "${BLUE}테스트 결과 요약${NC}"
echo "=========================================="

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ 모든 테스트 통과!${NC}"
    echo ""
    echo "서버 배포가 가능한 상태입니다."
    echo ""
    echo "다음 단계:"
    echo "1. 스테이징 서버에서 다음 명령어 실행:"
    echo "   cd /root/uvis"
    echo "   git pull origin main"
    echo "   docker-compose down"
    echo "   docker-compose up -d --build"
    echo ""
    echo "2. 배포 후 확인:"
    echo "   - Health: http://139.150.11.99:8000/health"
    echo "   - Swagger: http://139.150.11.99:8000/docs"
    echo "   - Frontend: http://139.150.11.99:3000"
    echo "   - Phase 10: http://139.150.11.99:3000/dispatch-rules"
    
    exit 0
else
    echo -e "${RED}❌ $ERROR_COUNT 개의 에러 발견${NC}"
    echo ""
    echo "로그 파일: $LOG_FILE"
    echo ""
    echo "에러를 수정한 후 다시 테스트하세요:"
    echo "  ./sandbox_safe_test.sh"
    
    exit 1
fi
