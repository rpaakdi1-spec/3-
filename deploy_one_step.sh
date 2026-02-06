#!/bin/bash

##############################################################################
# Phase 8 원스텝 배포 스크립트
# 최신 코드를 가져와서 프론트엔드를 재빌드하고 배포합니다
##############################################################################

set -e  # 오류 발생 시 중단

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_DIR="/root/uvis"

echo "=================================================================="
echo -e "${BLUE}Phase 8 원스텝 배포${NC}"
echo "=================================================================="
echo ""

# 1단계: 최신 코드 가져오기
echo -e "${BLUE}1단계: 최신 코드 가져오기${NC}"
echo "-------------------------------------------"
cd "$REPO_DIR"

CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "현재 커밋: $CURRENT_COMMIT"

git fetch origin genspark_ai_developer
git pull origin genspark_ai_developer

NEW_COMMIT=$(git rev-parse --short HEAD)
echo "최신 커밋: $NEW_COMMIT"

if [ "$CURRENT_COMMIT" != "$NEW_COMMIT" ]; then
    echo -e "${GREEN}✓ 새로운 코드가 업데이트되었습니다${NC}"
else
    echo -e "${YELLOW}⚠ 이미 최신 코드입니다${NC}"
fi
echo ""

# 2단계: 프론트엔드 빌드
echo -e "${BLUE}2단계: 프론트엔드 빌드${NC}"
echo "-------------------------------------------"
cd "$REPO_DIR/frontend"

# 이전 빌드 삭제
if [ -d "dist" ]; then
    rm -rf dist
fi

# 빌드
echo "빌드 중... (약 15초 소요)"
npm run build

if [ ! -d "dist" ]; then
    echo -e "${RED}✗ 빌드 실패!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 빌드 성공${NC}"
echo ""

# 3단계: Docker 컨테이너 재시작
echo -e "${BLUE}3단계: Docker 컨테이너 재시작${NC}"
echo "-------------------------------------------"
cd "$REPO_DIR"

echo "Docker 이미지 재빌드 중..."
docker-compose build --no-cache frontend

echo "프론트엔드 컨테이너 재시작 중..."
docker-compose up -d frontend

echo "서비스 시작 대기 중... (10초)"
sleep 10

# 4단계: 헬스 체크
echo ""
echo -e "${BLUE}4단계: 헬스 체크${NC}"
echo "-------------------------------------------"

# 프론트엔드 체크
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null)
if [ "$FRONTEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ 프론트엔드: $FRONTEND_STATUS OK${NC}"
else
    echo -e "${RED}✗ 프론트엔드: $FRONTEND_STATUS 실패${NC}"
fi

# 백엔드 체크
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
if [ "$BACKEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ 백엔드: $BACKEND_STATUS OK${NC}"
else
    echo -e "${RED}✗ 백엔드: $BACKEND_STATUS 실패${NC}"
fi

echo ""

# 5단계: 완료
echo "=================================================================="
echo -e "${GREEN}✓ 배포 완료!${NC}"
echo "=================================================================="
echo ""
echo "📊 배포 정보:"
echo "  - 커밋: $NEW_COMMIT"
echo "  - 빌드: 성공"
echo "  - 프론트엔드: $FRONTEND_STATUS"
echo "  - 백엔드: $BACKEND_STATUS"
echo ""
echo "🌐 접속 URL:"
echo "  - 메인 페이지: http://139.150.11.99/"
echo "  - API 문서: http://139.150.11.99:8000/docs"
echo "  - 로그인: admin / admin123"
echo ""
echo "📋 Phase 8 페이지:"
echo "  - 재무 대시보드: http://139.150.11.99/billing/financial-dashboard"
echo "  - 요금 미리보기: http://139.150.11.99/billing/charge-preview"
echo "  - 자동 청구: http://139.150.11.99/billing/auto-schedule"
echo "  - 정산 승인: http://139.150.11.99/billing/settlement-approval"
echo "  - 결제 알림: http://139.150.11.99/billing/payment-reminder"
echo "  - 데이터 내보내기: http://139.150.11.99/billing/export-task"
echo ""
echo "💡 브라우저에서:"
echo "  1. Ctrl + Shift + R (강력 새로고침)"
echo "  2. 사이드바에서 Phase 8 메뉴 확인"
echo "  3. 각 페이지 정상 작동 확인"
echo ""
echo "🔧 문제가 있으면:"
echo "  - 진단: ./diagnose_system.sh"
echo "  - 로그: docker logs uvis-frontend --tail 50"
echo ""
