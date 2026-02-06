#!/bin/bash

##############################################################################
# UVIS 빠른 진단 스크립트
# 목적: 현재 시스템 상태를 빠르게 진단
##############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=================================================================="
echo -e "${BLUE}UVIS 시스템 진단 리포트${NC}"
echo "=================================================================="
echo ""

REPO_DIR="/root/uvis"
cd "$REPO_DIR" || exit 1

##############################################################################
# 1. Docker 컨테이너 상태
##############################################################################
echo -e "${BLUE}1. Docker 컨테이너 상태${NC}"
echo "----------------------------------------"
docker-compose ps
echo ""

##############################################################################
# 2. 백엔드 상태
##############################################################################
echo -e "${BLUE}2. 백엔드 상태${NC}"
echo "----------------------------------------"

# 백엔드 헬스 체크
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
if [ "$BACKEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓${NC} 백엔드 헬스: $BACKEND_STATUS OK"
else
    echo -e "${RED}✗${NC} 백엔드 헬스: $BACKEND_STATUS 실패"
fi

# 백엔드 최근 오류
echo ""
echo "백엔드 최근 오류 (최근 10줄):"
docker logs uvis-backend --tail 100 | grep -i "error" | tail -10 || echo "오류 없음"
echo ""

##############################################################################
# 3. 프론트엔드 상태
##############################################################################
echo -e "${BLUE}3. 프론트엔드 상태${NC}"
echo "----------------------------------------"

# 프론트엔드 헬스 체크
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")
if [ "$FRONTEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓${NC} 프론트엔드 헬스: $FRONTEND_STATUS OK"
else
    echo -e "${RED}✗${NC} 프론트엔드 헬스: $FRONTEND_STATUS 실패"
fi

# 빌드 파일 확인
if [ -f "$REPO_DIR/frontend/dist/index.html" ]; then
    echo -e "${GREEN}✓${NC} 프론트엔드 빌드 파일 존재"
else
    echo -e "${RED}✗${NC} 프론트엔드 빌드 파일 없음"
fi

# 프론트엔드 최근 오류
echo ""
echo "프론트엔드 최근 오류 (최근 10줄):"
docker logs uvis-frontend --tail 100 | grep -i "error" | tail -10 || echo "오류 없음"
echo ""

##############################################################################
# 4. 데이터베이스 상태
##############################################################################
echo -e "${BLUE}4. 데이터베이스 상태${NC}"
echo "----------------------------------------"

if docker exec uvis-db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} 데이터베이스 연결: OK"
else
    echo -e "${RED}✗${NC} 데이터베이스 연결: 실패"
fi

# 데이터베이스 테이블 수
TABLE_COUNT=$(docker exec uvis-db psql -U postgres -d coldchain_dispatch -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | xargs)
echo "데이터베이스 테이블 수: $TABLE_COUNT"
echo ""

##############################################################################
# 5. Git 상태
##############################################################################
echo -e "${BLUE}5. Git 저장소 상태${NC}"
echo "----------------------------------------"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "현재 브랜치: $CURRENT_BRANCH"
echo "현재 커밋: $CURRENT_COMMIT"

# 로컬 변경사항 확인
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠${NC} 커밋되지 않은 변경사항이 있습니다:"
    git status -s | head -10
else
    echo -e "${GREEN}✓${NC} 작업 디렉토리 깨끗함"
fi
echo ""

##############################################################################
# 6. 환경 설정 파일
##############################################################################
echo -e "${BLUE}6. 환경 설정 파일${NC}"
echo "----------------------------------------"

if [ -f "$REPO_DIR/.env" ]; then
    echo -e "${GREEN}✓${NC} 백엔드 .env 존재"
else
    echo -e "${RED}✗${NC} 백엔드 .env 없음"
fi

if [ -f "$REPO_DIR/frontend/.env" ]; then
    echo -e "${GREEN}✓${NC} 프론트엔드 .env 존재"
    VITE_API_URL=$(grep "VITE_API_URL" "$REPO_DIR/frontend/.env" | cut -d'=' -f2)
    echo "  VITE_API_URL=$VITE_API_URL"
else
    echo -e "${RED}✗${NC} 프론트엔드 .env 없음"
fi
echo ""

##############################################################################
# 7. API 테스트
##############################################################################
echo -e "${BLUE}7. API 엔드포인트 테스트${NC}"
echo "----------------------------------------"

# 로그인 테스트
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓${NC} 로그인 API: 성공"
    
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    # 대시보드 API 테스트
    DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/v1/dispatches/stats/summary 2>/dev/null)
    
    if [ "$DASHBOARD_STATUS" == "200" ]; then
        echo -e "${GREEN}✓${NC} 대시보드 API: $DASHBOARD_STATUS OK"
    else
        echo -e "${RED}✗${NC} 대시보드 API: $DASHBOARD_STATUS 실패"
    fi
    
    # Phase 8 API 테스트
    PHASE8_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/v1/billing/enhanced/dashboard/financial 2>/dev/null)
    
    if [ "$PHASE8_STATUS" == "200" ]; then
        echo -e "${GREEN}✓${NC} Phase 8 API: $PHASE8_STATUS OK"
    else
        echo -e "${YELLOW}⚠${NC} Phase 8 API: $PHASE8_STATUS"
    fi
else
    echo -e "${RED}✗${NC} 로그인 API: 실패"
fi
echo ""

##############################################################################
# 8. 디스크 사용량
##############################################################################
echo -e "${BLUE}8. 디스크 사용량${NC}"
echo "----------------------------------------"
df -h / | tail -1
echo ""

##############################################################################
# 9. 메모리 사용량
##############################################################################
echo -e "${BLUE}9. 메모리 사용량${NC}"
echo "----------------------------------------"
free -h
echo ""

##############################################################################
# 요약 및 권장사항
##############################################################################
echo "=================================================================="
echo -e "${BLUE}진단 요약 및 권장사항${NC}"
echo "=================================================================="
echo ""

# 백엔드 체크
if [ "$BACKEND_STATUS" != "200" ]; then
    echo -e "${RED}❌ 백엔드가 작동하지 않습니다${NC}"
    echo "   해결방법: docker-compose restart backend"
    echo ""
fi

# 프론트엔드 체크
if [ "$FRONTEND_STATUS" != "200" ]; then
    echo -e "${RED}❌ 프론트엔드가 작동하지 않습니다${NC}"
    echo "   해결방법: cd frontend && npm run build && cd .. && docker-compose restart frontend"
    echo ""
fi

# 데이터베이스 체크
if ! docker exec uvis-db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${RED}❌ 데이터베이스가 작동하지 않습니다${NC}"
    echo "   해결방법: docker-compose restart uvis-db"
    echo ""
fi

# 환경 설정 체크
if [ ! -f "$REPO_DIR/frontend/.env" ]; then
    echo -e "${YELLOW}⚠ 프론트엔드 환경 설정 파일이 없습니다${NC}"
    echo "   해결방법: echo 'VITE_API_URL=/api/v1' > frontend/.env"
    echo ""
fi

# 빌드 파일 체크
if [ ! -f "$REPO_DIR/frontend/dist/index.html" ]; then
    echo -e "${YELLOW}⚠ 프론트엔드 빌드 파일이 없습니다${NC}"
    echo "   해결방법: cd frontend && npm run build"
    echo ""
fi

# 로컬 변경사항 체크
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠ 커밋되지 않은 변경사항이 있습니다${NC}"
    echo "   해결방법: git reset --hard origin/genspark_ai_developer"
    echo ""
fi

# 전체적으로 OK인 경우
if [ "$BACKEND_STATUS" == "200" ] && [ "$FRONTEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ 시스템이 정상적으로 작동하고 있습니다!${NC}"
    echo ""
    echo "접속 URL:"
    echo "  - 프론트엔드: http://139.150.11.99/"
    echo "  - API 문서: http://139.150.11.99:8000/docs"
    echo "  - 로그인: admin / admin123"
else
    echo -e "${RED}❌ 시스템에 문제가 있습니다${NC}"
    echo ""
    echo "전체 오류 수정 스크립트 실행:"
    echo "  ./fix_all_errors.sh"
fi

echo ""
echo "상세 로그 확인:"
echo "  - 백엔드: docker logs uvis-backend -f"
echo "  - 프론트엔드: docker logs uvis-frontend -f"
echo "  - 데이터베이스: docker logs uvis-db --tail 50"
echo ""
