#!/bin/bash

# ============================================================================
# Error-Fully-Corrected Snapshot Verification Script
# ============================================================================
# 이 스크립트는 "error-fully-corrected" 상태가 올바르게 저장되었는지 검증합니다.
# ============================================================================

set -e  # 에러 발생 시 즉시 종료

echo "=================================================="
echo "🔍 Error-Fully-Corrected Snapshot 검증 시작"
echo "=================================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 성공/실패 카운터
SUCCESS_COUNT=0
FAIL_COUNT=0

# 테스트 함수
test_step() {
    local test_name=$1
    local test_command=$2
    
    echo -n "  ⏳ $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 통과${NC}"
        ((SUCCESS_COUNT++))
        return 0
    else
        echo -e "${RED}❌ 실패${NC}"
        ((FAIL_COUNT++))
        return 1
    fi
}

# 1. Git 태그 확인
echo "📌 1. Git 태그 확인"
echo "--------------------"
test_step "error-fully-corrected 태그 존재" "git tag | grep -q '^error-fully-corrected$'"
test_step "v1.0.0-all-errors-fixed 태그 존재" "git tag | grep -q '^v1.0.0-all-errors-fixed$'"
echo ""

# 2. 문서 파일 확인
echo "📚 2. 문서 파일 존재 확인"
echo "--------------------"
test_step "ROLLBACK_GUIDE.md" "test -f ROLLBACK_GUIDE.md"
test_step "DATABASE_SNAPSHOT.sql" "test -f DATABASE_SNAPSHOT.sql"
test_step "ERROR_FULLY_CORRECTED_SNAPSHOT.md" "test -f ERROR_FULLY_CORRECTED_SNAPSHOT.md"
test_step "TELEMETRY_FIX_SUMMARY.md" "test -f TELEMETRY_FIX_SUMMARY.md"
test_step "FRONTEND_ERRORS_FIX_SUMMARY.md" "test -f FRONTEND_ERRORS_FIX_SUMMARY.md"
test_step "ANALYTICS_DASHBOARD_FIX_SUMMARY.md" "test -f ANALYTICS_DASHBOARD_FIX_SUMMARY.md"
test_step "ANALYTICS_WEBSOCKET_FIX_SUMMARY.md" "test -f ANALYTICS_WEBSOCKET_FIX_SUMMARY.md"
echo ""

# 3. 배포 스크립트 확인
echo "🚀 3. 배포 스크립트 존재 및 실행 권한 확인"
echo "--------------------"
test_step "FIX_TELEMETRY_AND_REDIS.sh 존재" "test -f FIX_TELEMETRY_AND_REDIS.sh"
test_step "FIX_TELEMETRY_AND_REDIS.sh 실행 권한" "test -x FIX_TELEMETRY_AND_REDIS.sh"
test_step "FIX_REDIS_AUTH.sh 존재" "test -f FIX_REDIS_AUTH.sh"
test_step "FIX_REDIS_AUTH.sh 실행 권한" "test -x FIX_REDIS_AUTH.sh"
test_step "FIX_FRONTEND_ERRORS.sh 존재" "test -f FIX_FRONTEND_ERRORS.sh"
test_step "FIX_FRONTEND_ERRORS.sh 실행 권한" "test -x FIX_FRONTEND_ERRORS.sh"
test_step "FIX_ANALYTICS_DASHBOARD.sh 존재" "test -f FIX_ANALYTICS_DASHBOARD.sh"
test_step "FIX_ANALYTICS_DASHBOARD.sh 실행 권한" "test -x FIX_ANALYTICS_DASHBOARD.sh"
test_step "FIX_ANALYTICS_WEBSOCKET.sh 존재" "test -f FIX_ANALYTICS_WEBSOCKET.sh"
test_step "FIX_ANALYTICS_WEBSOCKET.sh 실행 권한" "test -x FIX_ANALYTICS_WEBSOCKET.sh"
echo ""

# 4. 백업 파일 확인
echo "💾 4. 백업 파일 확인"
echo "--------------------"
test_step "navigation.ts.backup3 존재" "test -f frontend/src/config/navigation.ts.backup3"
echo ""

# 5. Backend 수정 파일 확인
echo "🔧 5. Backend 수정 파일 확인"
echo "--------------------"
test_step "vehicle_location.py 존재" "test -f backend/app/models/vehicle_location.py"
test_step "vehicle_location.py에 timestamp 포함" "grep -q 'timestamp' backend/app/models/vehicle_location.py"
test_step "ab_test.py 존재" "test -f backend/app/api/ab_test.py"
test_step "ab_test.py에 Redis password 포함" "grep -q 'password=' backend/app/api/ab_test.py"
test_step "analytics.py 존재" "test -f backend/app/api/analytics.py"
test_step "analytics.py에 에러 핸들링 포함" "grep -q 'try:' backend/app/api/analytics.py"
echo ""

# 6. Frontend 수정 파일 확인
echo "🎨 6. Frontend 수정 파일 확인"
echo "--------------------"
test_step "DispatchOptimizationPage.tsx 존재" "test -f frontend/src/pages/DispatchOptimizationPage.tsx"
test_step "DispatchOptimizationPage.tsx에 '배차대기' 포함" "grep -q '배차대기' frontend/src/pages/DispatchOptimizationPage.tsx"
test_step "RealtimeTelemetryPage.tsx 존재" "test -f frontend/src/pages/RealtimeTelemetryPage.tsx"
test_step "App.tsx 존재" "test -f frontend/src/App.tsx"
test_step "useRealtimeData.ts 존재" "test -f frontend/src/hooks/useRealtimeData.ts"
test_step "useRealtimeData.ts에 NODE_ENV 체크 포함" "grep -q 'process.env.NODE_ENV' frontend/src/hooks/useRealtimeData.ts"
echo ""

# 7. Git 커밋 히스토리 확인
echo "📝 7. Git 커밋 히스토리 확인"
echo "--------------------"
test_step "a86a0d5 커밋 존재 (WebSocket 로그)" "git log --oneline | grep -q 'a86a0d5'"
test_step "895637d 커밋 존재 (중복 라우트)" "git log --oneline | grep -q '895637d'"
test_step "d5103d0 커밋 존재 (Analytics 에러)" "git log --oneline | grep -q 'd5103d0'"
test_step "6e90959 커밋 존재 (Frontend 에러)" "git log --oneline | grep -q '6e90959'"
test_step "a1f1a75 커밋 존재 (Redis 인증)" "git log --oneline | grep -q 'a1f1a75'"
test_step "1587141 커밋 존재 (timestamp)" "git log --oneline | grep -q '1587141'"
echo ""

# 8. 태그가 올바른 커밋을 가리키는지 확인
echo "🎯 8. 태그 커밋 확인"
echo "--------------------"
ERROR_TAG_COMMIT=$(git rev-parse error-fully-corrected 2>/dev/null | cut -c1-7)
V1_TAG_COMMIT=$(git rev-parse v1.0.0-all-errors-fixed 2>/dev/null | cut -c1-7)

echo "  error-fully-corrected 태그 → $ERROR_TAG_COMMIT"
echo "  v1.0.0-all-errors-fixed 태그 → $V1_TAG_COMMIT"

if [ "$ERROR_TAG_COMMIT" = "a86a0d5" ]; then
    echo -e "  ${GREEN}✅ error-fully-corrected 태그가 올바른 커밋을 가리킴${NC}"
    ((SUCCESS_COUNT++))
else
    echo -e "  ${RED}❌ error-fully-corrected 태그가 잘못된 커밋을 가리킴${NC}"
    ((FAIL_COUNT++))
fi

if [ "$V1_TAG_COMMIT" = "a86a0d5" ]; then
    echo -e "  ${GREEN}✅ v1.0.0-all-errors-fixed 태그가 올바른 커밋을 가리킴${NC}"
    ((SUCCESS_COUNT++))
else
    echo -e "  ${RED}❌ v1.0.0-all-errors-fixed 태그가 잘못된 커밋을 가리킴${NC}"
    ((FAIL_COUNT++))
fi
echo ""

# 9. 원격 저장소에 태그가 푸시되었는지 확인
echo "☁️  9. 원격 저장소 태그 확인"
echo "--------------------"
test_step "원격에 error-fully-corrected 태그 존재" "git ls-remote --tags origin | grep -q 'refs/tags/error-fully-corrected'"
test_step "원격에 v1.0.0-all-errors-fixed 태그 존재" "git ls-remote --tags origin | grep -q 'refs/tags/v1.0.0-all-errors-fixed'"
echo ""

# 10. 문서 내용 검증
echo "📄 10. 문서 내용 검증"
echo "--------------------"
test_step "ROLLBACK_GUIDE.md에 롤백 명령 포함" "grep -q 'git checkout error-fully-corrected' ROLLBACK_GUIDE.md"
test_step "ERROR_FULLY_CORRECTED_SNAPSHOT.md에 10개 에러 포함" "grep -q '해결된 에러 목록 (10개)' ERROR_FULLY_CORRECTED_SNAPSHOT.md"
test_step "DATABASE_SNAPSHOT.sql에 timestamp 컬럼 포함" "grep -q 'timestamp' DATABASE_SNAPSHOT.sql"
echo ""

# 결과 요약
echo "=================================================="
echo "📊 검증 결과 요약"
echo "=================================================="
echo ""
echo -e "  ${GREEN}✅ 통과: $SUCCESS_COUNT${NC}"
echo -e "  ${RED}❌ 실패: $FAIL_COUNT${NC}"
echo ""

TOTAL_TESTS=$((SUCCESS_COUNT + FAIL_COUNT))
SUCCESS_RATE=$((SUCCESS_COUNT * 100 / TOTAL_TESTS))

echo "  성공률: $SUCCESS_RATE% ($SUCCESS_COUNT/$TOTAL_TESTS)"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 모든 검증을 통과했습니다!${NC}"
    echo -e "${GREEN}error-fully-corrected 스냅샷이 성공적으로 저장되었습니다.${NC}"
    echo ""
    echo "📌 롤백 방법:"
    echo "  git checkout error-fully-corrected"
    echo "  docker-compose down && docker-compose up -d --build"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  일부 검증이 실패했습니다.${NC}"
    echo -e "${YELLOW}스냅샷 상태를 확인하고 누락된 파일이나 설정을 복구하세요.${NC}"
    echo ""
    exit 1
fi
