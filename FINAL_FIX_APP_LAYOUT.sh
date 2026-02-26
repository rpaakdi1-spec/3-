#!/bin/bash

################################################################################
# UVIS UI 완전 수정 스크립트
# 목적: App.tsx에 Layout 추가 + 모든 페이지에서 Layout 제거
# 소요 시간: 5-7분
################################################################################

set -e  # 에러 시 즉시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 시작 시간
START_TIME=$(date +%s)

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 UVIS UI 완전 수정 시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

################################################################################
# Step 1: 백업 생성
################################################################################
echo -e "${YELLOW}📦 Step 1/8: 백업 생성 중...${NC}"

BACKUP_DIR="/root/uvis/frontend/src/pages/layout_final_fix_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# App.tsx 백업
cp /root/uvis/frontend/src/App.tsx "$BACKUP_DIR/App.tsx.backup"

# 모든 페이지 백업
cp /root/uvis/frontend/src/pages/*.tsx "$BACKUP_DIR/" 2>/dev/null || true

echo -e "${GREEN}✅ 백업 완료: $BACKUP_DIR${NC}"
echo ""

################################################################################
# Step 2: App.tsx 수정 (Layout 추가)
################################################################################
echo -e "${YELLOW}🔧 Step 2/8: App.tsx에 Layout 추가 중...${NC}"

APP_FILE="/root/uvis/frontend/src/App.tsx"

# Layout import 추가 (이미 있으면 스킵)
if ! grep -q "import Layout from" "$APP_FILE"; then
    # lazy import 다음 줄에 Layout import 추가
    sed -i "/const RecurringOrdersPage = lazy/a\\import Layout from './components/common/Layout';" "$APP_FILE"
    echo -e "${GREEN}✅ Layout import 추가됨${NC}"
else
    echo -e "${YELLOW}⚠️  Layout import 이미 존재${NC}"
fi

# 인증된 라우트를 Layout으로 감싸기
# <div className="h-screen"> 부분을 Layout으로 교체
sed -i 's/<div className="h-screen">/<Layout>/g' "$APP_FILE"
sed -i 's/<\/div>  {\/\* h-screen \*\/}/<\/Layout>/g' "$APP_FILE"

echo -e "${GREEN}✅ App.tsx 수정 완료${NC}"
echo ""

################################################################################
# Step 3: 모든 페이지에서 Layout 제거
################################################################################
echo -e "${YELLOW}🗑️  Step 3/8: 페이지에서 Layout 제거 중...${NC}"

PAGES_DIR="/root/uvis/frontend/src/pages"
SUCCESS_COUNT=0
FAIL_COUNT=0

# 처리할 페이지 목록 (LoginPage 제외)
PAGES=(
    "ABTestMonitorPage.tsx"
    "AIChatPage.tsx"
    "AlertSettingsPage.tsx"
    "AnalyticsDashboardPage.tsx"
    "AnalyticsPage.tsx"
    "ClientsPage.tsx"
    "DashboardPage.tsx"
    "DispatchMonitoringPage.tsx"
    "DispatchRulesPage.tsx"
    "FinancialDashboardPage.tsx"
    "MorePage.tsx"
    "OptimizationPage.tsx"
    "OrderCalendarPage.tsx"
    "OrdersPage.tsx"
    "RealtimeDashboardPage.tsx"
    "RecurringOrdersPage.tsx"
    "ReportsPage.tsx"
    "SettingsPage.tsx"
    "TemperatureMonitoringPage.tsx"
    "TrackingPage.tsx"
    "VehiclesPage.tsx"
)

for PAGE in "${PAGES[@]}"; do
    FILE_PATH="$PAGES_DIR/$PAGE"
    
    if [ -f "$FILE_PATH" ]; then
        # Layout import 제거
        sed -i '/^import.*Layout.*from/d' "$FILE_PATH"
        
        # <Layout> 태그 제거
        sed -i 's/<Layout>//g' "$FILE_PATH"
        sed -i 's/<\/Layout>//g' "$FILE_PATH"
        
        # 빈 줄 정리
        sed -i '/^$/N;/^\n$/D' "$FILE_PATH"
        
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo -e "${GREEN}  ✓${NC} $PAGE"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo -e "${RED}  ✗${NC} $PAGE (파일 없음)"
    fi
done

echo ""
echo -e "${GREEN}✅ Layout 제거 완료${NC}"
echo -e "   성공: ${GREEN}$SUCCESS_COUNT${NC} 개"
echo -e "   실패: ${RED}$FAIL_COUNT${NC} 개"
echo ""

################################################################################
# Step 4: 검증
################################################################################
echo -e "${YELLOW}🔍 Step 4/8: 수정 사항 검증 중...${NC}"

# App.tsx에 Layout import 있는지 확인
if grep -q "import Layout from" "$APP_FILE"; then
    echo -e "${GREEN}  ✓${NC} App.tsx에 Layout import 존재"
else
    echo -e "${RED}  ✗${NC} App.tsx에 Layout import 없음"
fi

# App.tsx에 <Layout> 태그 있는지 확인
if grep -q "<Layout>" "$APP_FILE"; then
    echo -e "${GREEN}  ✓${NC} App.tsx에 <Layout> 태그 사용 중"
else
    echo -e "${RED}  ✗${NC} App.tsx에 <Layout> 태그 없음"
fi

# 페이지에서 Layout 제거 확인
REMAINING=$(grep -r "import.*Layout" "$PAGES_DIR"/*.tsx 2>/dev/null | grep -v "LoginPage" | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo -e "${GREEN}  ✓${NC} 모든 페이지에서 Layout 제거됨"
else
    echo -e "${YELLOW}  ⚠${NC}  $REMAINING 개 파일에 여전히 Layout 남음"
fi

echo ""

################################################################################
# Step 5: 프론트엔드 빌드
################################################################################
echo -e "${YELLOW}🔨 Step 5/8: 프론트엔드 빌드 중...${NC}"

cd /root/uvis/frontend

# 기존 빌드 제거
rm -rf dist/

# 빌드 실행
BUILD_START=$(date +%s)
if npm run build; then
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    echo -e "${GREEN}✅ 빌드 성공 (${BUILD_TIME}초)${NC}"
    
    # CSS 파일 확인
    CSS_COUNT=$(find dist/assets -name "*.css" 2>/dev/null | wc -l)
    echo -e "${GREEN}   CSS 파일: ${CSS_COUNT}개${NC}"
    find dist/assets -name "*.css" -exec ls -lh {} \;
else
    echo -e "${RED}❌ 빌드 실패${NC}"
    echo -e "${YELLOW}💡 백업에서 복구하려면:${NC}"
    echo -e "   cp $BACKUP_DIR/*.tsx /root/uvis/frontend/src/pages/"
    echo -e "   cp $BACKUP_DIR/App.tsx.backup /root/uvis/frontend/src/App.tsx"
    exit 1
fi

echo ""

################################################################################
# Step 6: Docker 이미지 빌드
################################################################################
echo -e "${YELLOW}🐳 Step 6/8: Docker 이미지 빌드 중... (3-4분 소요)${NC}"

cd /root/uvis

DOCKER_BUILD_START=$(date +%s)
if docker-compose build --no-cache frontend; then
    DOCKER_BUILD_END=$(date +%s)
    DOCKER_BUILD_TIME=$((DOCKER_BUILD_END - DOCKER_BUILD_START))
    echo -e "${GREEN}✅ Docker 이미지 빌드 완료 (${DOCKER_BUILD_TIME}초)${NC}"
else
    echo -e "${RED}❌ Docker 빌드 실패${NC}"
    exit 1
fi

echo ""

################################################################################
# Step 7: 컨테이너 재시작
################################################################################
echo -e "${YELLOW}🔄 Step 7/8: 컨테이너 재시작 중...${NC}"

docker-compose up -d frontend
sleep 5

# 컨테이너 상태 확인
if docker ps | grep -q "uvis-frontend"; then
    echo -e "${GREEN}✅ 컨테이너 재시작 완료${NC}"
else
    echo -e "${RED}❌ 컨테이너 시작 실패${NC}"
    docker logs uvis-frontend --tail 50
    exit 1
fi

echo ""

################################################################################
# Step 8: 최종 검증
################################################################################
echo -e "${YELLOW}✅ Step 8/8: 최종 검증 중...${NC}"

# CSS 파일 확인
echo -e "${BLUE}컨테이너 내 CSS 파일:${NC}"
docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css" 2>/dev/null || echo "  (CSS 파일 확인 실패)"

# index.html에서 CSS 링크 확인
echo -e "${BLUE}index.html CSS 링크:${NC}"
docker exec uvis-frontend cat /usr/share/nginx/html/index.html | grep -o 'href="/assets/[^"]*\.css"' || echo "  (CSS 링크 확인 실패)"

echo ""

################################################################################
# 완료 보고
################################################################################
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
MINUTES=$((TOTAL_TIME / 60))
SECONDS=$((TOTAL_TIME % 60))

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📊 실행 요약:${NC}"
echo -e "   • 총 소요 시간: ${YELLOW}${MINUTES}분 ${SECONDS}초${NC}"
echo -e "   • 백업 위치: ${YELLOW}$BACKUP_DIR${NC}"
echo -e "   • Layout 제거: ${GREEN}$SUCCESS_COUNT${NC} 성공, ${RED}$FAIL_COUNT${NC} 실패"
echo -e "   • 빌드 시간: ${YELLOW}${BUILD_TIME}초${NC}"
echo -e "   • Docker 빌드: ${YELLOW}${DOCKER_BUILD_TIME}초${NC}"
echo ""
echo -e "${YELLOW}🌐 다음 단계:${NC}"
echo -e "   1. 브라우저 캐시 완전 삭제 (Ctrl+Shift+Delete)"
echo -e "      → '전체 기간' 선택"
echo -e "      → 쿠키, 캐시된 이미지/파일 모두 체크"
echo -e "   2. Chrome 완전 종료 후 재시작"
echo -e "   3. http://139.150.11.99/login 접속"
echo -e "      ID: admin"
echo -e "      PW: admin123"
echo -e "   4. UI 확인:"
echo -e "      • 로그인 페이지 중앙 정렬"
echo -e "      • 모든 페이지에 사이드바 표시"
echo -e "      • 페이지 전환 정상 동작"
echo -e "      • 콘솔 에러 없음"
echo ""
echo -e "${YELLOW}📝 롤백 (문제 발생 시):${NC}"
echo -e "   cp $BACKUP_DIR/*.tsx /root/uvis/frontend/src/pages/"
echo -e "   cp $BACKUP_DIR/App.tsx.backup /root/uvis/frontend/src/App.tsx"
echo -e "   cd /root/uvis/frontend && npm run build"
echo -e "   cd /root/uvis && docker-compose build --no-cache frontend"
echo -e "   docker-compose up -d frontend"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
