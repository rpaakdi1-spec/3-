#!/bin/bash
# 사용자 삭제 기능 수정 배포 스크립트

set -e

echo "🗑️ 사용자 삭제 기능 수정 배포 시작..."
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "📥 1. 최신 코드 가져오기..."
git pull origin main
echo -e "${GREEN}✅ 코드 업데이트 완료${NC}"
echo ""

echo "🔨 2. 백엔드 재빌드..."
docker compose build backend
echo -e "${GREEN}✅ 백엔드 빌드 완료${NC}"
echo ""

echo "🔄 3. 백엔드 재시작..."
docker compose up -d backend
echo "⏳ 10초 대기..."
sleep 10
echo -e "${GREEN}✅ 백엔드 재시작 완료${NC}"
echo ""

echo "🔨 4. 프론트엔드 재빌드..."
docker compose build frontend
echo -e "${GREEN}✅ 프론트엔드 빌드 완료${NC}"
echo ""

echo "🔄 5. 프론트엔드 재시작..."
docker compose up -d frontend
echo "⏳ 10초 대기..."
sleep 10
echo -e "${GREEN}✅ 프론트엔드 재시작 완료${NC}"
echo ""

echo "🏥 6. 헬스체크..."
HEALTH=$(curl -s http://139.150.11.99/api/v1/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ 백엔드 정상${NC}"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo -e "${RED}❌ 백엔드 헬스체크 실패${NC}"
    echo "$HEALTH"
fi
echo ""

echo "🌐 7. 프론트엔드 확인..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://139.150.11.99/)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 프론트엔드 정상 (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ 프론트엔드 응답 이상 (HTTP $HTTP_CODE)${NC}"
fi
echo ""

echo -e "${GREEN}🎉 배포 완료!${NC}"
echo ""
echo "📋 테스트 방법:"
echo "  1. http://139.150.11.99/ 접속"
echo "  2. 회원가입: testdelete01 / test123456"
echo "  3. admin 로그인 후 승인"
echo "  4. 설정 → 사용자 관리에서 testdelete01 삭제"
echo "  5. 목록에서 즉시 사라지는지 확인"
echo ""
echo "📚 문서: USER_DELETE_FIX.md"
echo ""
