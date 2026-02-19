#!/bin/bash

# 배차 관리 필터링 기능 배포 스크립트
# Deploy Dispatch Management Filtering Feature
# 작성일: 2026-02-19

set -e

echo "=========================================="
echo "🚀 배차 관리 필터링 기능 배포"
echo "=========================================="

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 백엔드 디렉토리로 이동
echo -e "${YELLOW}📂 프론트엔드 디렉토리로 이동...${NC}"
cd /root/uvis/frontend

# 2. 현재 상태 확인
echo -e "${YELLOW}📋 현재 Git 상태 확인...${NC}"
git status

# 3. 변경사항 임시 저장 (있을 경우)
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}💾 로컬 변경사항 임시 저장...${NC}"
    git stash push -m "deploy_filter_$(date +%Y%m%d_%H%M%S)"
fi

# 4. 최신 코드 가져오기
echo -e "${YELLOW}⬇️ 최신 코드 가져오기...${NC}"
git fetch origin main

# 5. 현재 커밋과 원격 커밋 확인
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)
echo -e "${GREEN}📌 로컬 커밋: $LOCAL_COMMIT${NC}"
echo -e "${GREEN}📌 원격 커밋: $REMOTE_COMMIT${NC}"

# 6. 강제로 원격 main과 동기화
echo -e "${YELLOW}🔄 원격 main과 동기화...${NC}"
git reset --hard origin/main

# 7. 최신 커밋 확인
echo -e "${YELLOW}✅ 최신 커밋 확인...${NC}"
git log --oneline -1

# 8. DispatchesPage.tsx 변경 확인
echo -e "${YELLOW}🔍 필터링 기능 추가 확인...${NC}"
if grep -q "searchText" src/pages/DispatchesPage.tsx; then
    echo -e "${GREEN}✅ 검색 필터 확인됨${NC}"
else
    echo -e "${RED}❌ 검색 필터를 찾을 수 없습니다${NC}"
    exit 1
fi

if grep -q "filterStatus" src/pages/DispatchesPage.tsx; then
    echo -e "${GREEN}✅ 상태 필터 확인됨${NC}"
else
    echo -e "${RED}❌ 상태 필터를 찾을 수 없습니다${NC}"
    exit 1
fi

if grep -q "filterVehicle" src/pages/DispatchesPage.tsx; then
    echo -e "${GREEN}✅ 차량 필터 확인됨${NC}"
else
    echo -e "${RED}❌ 차량 필터를 찾을 수 없습니다${NC}"
    exit 1
fi

if grep -q "filterDate" src/pages/DispatchesPage.tsx; then
    echo -e "${GREEN}✅ 날짜 필터 확인됨${NC}"
else
    echo -e "${RED}❌ 날짜 필터를 찾을 수 없습니다${NC}"
    exit 1
fi

# 9. 빌드
echo -e "${YELLOW}🔨 프론트엔드 빌드 중...${NC}"
npm run build

# 10. 빌드 결과 확인
if [ ! -d "dist" ]; then
    echo -e "${RED}❌ 빌드 실패: dist 디렉토리가 없습니다${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 빌드 완료${NC}"
ls -lh dist/index.html

# 11. 도커 컨테이너에 파일 복사
echo -e "${YELLOW}📦 컨테이너에 빌드 파일 복사...${NC}"
docker cp dist/. uvis-frontend:/usr/share/nginx/html/

# 12. Nginx 캐시 클리어
echo -e "${YELLOW}🧹 Nginx 캐시 클리어...${NC}"
docker exec uvis-nginx rm -rf /var/cache/nginx/* 2>/dev/null || true

# 13. 컨테이너 재시작
echo -e "${YELLOW}🔄 컨테이너 재시작...${NC}"
docker restart uvis-frontend
docker restart uvis-nginx

# 14. 대기
echo -e "${YELLOW}⏳ 컨테이너 시작 대기 (10초)...${NC}"
sleep 10

# 15. 상태 확인
echo -e "${YELLOW}🔍 컨테이너 상태 확인...${NC}"
docker ps | grep -E "uvis-frontend|uvis-nginx"

# 16. 로그 확인
echo -e "${YELLOW}📋 최근 로그 확인...${NC}"
docker logs uvis-frontend --tail 20

# 17. 헬스체크
echo -e "${YELLOW}🏥 헬스체크...${NC}"
curl -I http://localhost:80/ | head -n 1

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 배차 관리 필터링 기능 배포 완료!${NC}"
echo "=========================================="
echo ""
echo "📋 배포 내용:"
echo "  - 검색 필터: 배차번호, 차량, 운전자 검색"
echo "  - 상태 필터: 전체, 임시저장, 확정, 진행중, 완료, 취소"
echo "  - 차량 필터: 차량별 필터링"
echo "  - 날짜 필터: 날짜별 필터링"
echo "  - 결과 카운트: 필터링된 결과 수 표시"
echo ""
echo "🌐 브라우저 테스트:"
echo "  1. 모든 브라우저 탭 닫기"
echo "  2. InPrivate/Incognito 모드로 새 창 열기"
echo "  3. http://139.150.11.99 접속"
echo "  4. 로그인 후 배차 관리 페이지로 이동"
echo "  5. 필터 기능 테스트:"
echo "     - 검색창에 배차번호/차량번호 입력"
echo "     - 상태 드롭다운 선택"
echo "     - 차량 드롭다운 선택"
echo "     - 날짜 선택"
echo ""
echo "✅ 예상 결과:"
echo "  - 각 필터가 실시간으로 동작"
echo "  - 필터링된 결과 수가 표시됨"
echo "  - 여러 필터 조합 가능"
echo "  - 성능 저하 없이 부드럽게 동작"
echo ""
echo "🔧 문제 발생 시:"
echo "  1. 브라우저 캐시 완전 삭제 (Ctrl+Shift+Delete)"
echo "  2. DNS 캐시 플러시 (ipconfig /flushdns 또는 해당 OS 명령)"
echo "  3. 백엔드 로그 확인: docker logs uvis-backend --tail 50"
echo "  4. 프론트엔드 로그 확인: docker logs uvis-frontend --tail 50"
echo ""
