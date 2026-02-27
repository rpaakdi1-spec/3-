#!/bin/bash

# ============================================================================
# Naver Map API 설정 배포 스크립트
# ============================================================================
# 이 스크립트는 네이버 지도 API Client ID를 적용한 버전을 배포합니다
# ============================================================================

set -e

echo "=================================================="
echo "🗺️  네이버 지도 API 설정 배포"
echo "=================================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📥 1. 최신 코드 가져오기...${NC}"
git pull origin main

echo ""
echo -e "${BLUE}🔍 2. 환경변수 확인...${NC}"
if grep -q "VITE_NAVER_MAP_CLIENT_ID=oimsa0yj4k" frontend/.env.production; then
    echo -e "   ${GREEN}✅ VITE_NAVER_MAP_CLIENT_ID 설정됨: oimsa0yj4k${NC}"
else
    echo -e "   ${YELLOW}⚠️  VITE_NAVER_MAP_CLIENT_ID 없음${NC}"
fi

echo ""
echo -e "${BLUE}🛑 3. Frontend 컨테이너 중지...${NC}"
docker-compose stop frontend

echo ""
echo -e "${BLUE}🗑️  4. Frontend 컨테이너 제거...${NC}"
docker-compose rm -f frontend

echo ""
echo -e "${BLUE}🏗️  5. Frontend 이미지 재빌드...${NC}"
echo "   (환경변수 적용을 위해 캐시 없이 재빌드: ~5분 소요)"
docker-compose build --no-cache frontend

echo ""
echo -e "${BLUE}🚀 6. Frontend 컨테이너 시작...${NC}"
docker-compose up -d frontend

echo ""
echo -e "${BLUE}⏳ 7. Frontend 시작 대기 (10초)...${NC}"
sleep 10

echo ""
echo -e "${BLUE}🔍 8. Frontend 컨테이너 상태 확인...${NC}"
docker-compose ps frontend

echo ""
echo -e "${BLUE}📝 9. Frontend 로그 확인...${NC}"
docker-compose logs frontend --tail 20

echo ""
echo "=================================================="
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}📌 주요 변경사항:${NC}"
echo "  ✅ 네이버 지도 API Client ID 설정 (oimsa0yj4k)"
echo "  ✅ 환경변수 VITE_NAVER_MAP_CLIENT_ID 추가"
echo ""
echo -e "${YELLOW}⚠️  중요: 네이버 클라우드 플랫폼에서 URL 등록 필요!${NC}"
echo ""
echo -e "${BLUE}🔧 네이버 클라우드 플랫폼 설정:${NC}"
echo "  1. https://www.ncloud.com/ 접속 및 로그인"
echo "  2. Console → Services → AI·NAVER API → Maps"
echo "  3. Client ID 'oimsa0yj4k' 애플리케이션 찾기"
echo "  4. 'Web 서비스 URL' 섹션에 다음 URL 추가:"
echo "     - http://139.150.11.99"
echo "     - http://139.150.11.99/vehicles"
echo "     - http://139.150.11.99*  (와일드카드)"
echo "  5. 저장 후 5-10분 대기"
echo ""
echo -e "${BLUE}🧪 테스트 방법:${NC}"
echo "  1. 브라우저: http://139.150.11.99/vehicles"
echo "  2. F12 → Console → localStorage.clear(); location.reload();"
echo "  3. 로그인: admin / admin123"
echo "  4. '지도' 탭 클릭"
echo ""
echo -e "${BLUE}🎯 기대 결과:${NC}"
echo "  ✅ 지도가 정상적으로 로드됨"
echo "  ✅ 차량 마커가 표시됨"
echo "  ✅ Console에 Authentication Failed 에러 없음"
echo ""
echo -e "${YELLOW}⚠️  주의사항:${NC}"
echo "  - 네이버 클라우드에서 URL을 등록하지 않으면"
echo "    여전히 'Authentication Failed' 에러가 발생합니다"
echo "  - URL 등록 후 5-10분 DNS 전파 시간 필요"
echo "  - 브라우저 캐시 클리어 필수"
echo ""
echo -e "${BLUE}📚 상세 가이드:${NC}"
echo "  NAVER_MAP_SETUP_GUIDE.md 파일 참조"
echo ""
