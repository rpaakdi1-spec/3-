#!/bin/bash
# Deploy Dispatch Rules Frontend Fix
# This script updates the frontend on the server with the fix

set -e

echo "=================================================="
echo "  Dispatch Rules Frontend Fix Deployment"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}이 스크립트를 서버에서 실행하세요!${NC}"
echo ""
echo "서버 접속:"
echo "  ssh root@139.150.11.99"
echo ""
echo "=================================================="
echo ""

# 1. Navigate to frontend directory
echo -e "${YELLOW}Step 1: Frontend 디렉토리로 이동${NC}"
echo "  cd /root/uvis/frontend"
cd /root/uvis/frontend
echo -e "${GREEN}✅ Complete${NC}"
echo ""

# 2. Pull latest code
echo -e "${YELLOW}Step 2: 최신 코드 Pull${NC}"
echo "  git pull origin main"
git pull origin main
echo -e "${GREEN}✅ Complete${NC}"
echo ""

# 3. Verify the fix
echo -e "${YELLOW}Step 3: 수정 사항 확인${NC}"
echo "  grep -A 3 'update: async' src/api/dispatch-rules.ts"
grep -A 3 "update: async" src/api/dispatch-rules.ts
echo ""
if grep -q "rule_update: payload" src/api/dispatch-rules.ts; then
    echo -e "${GREEN}✅ Fix verified: rule_update wrapper present${NC}"
else
    echo -e "${RED}❌ Fix not found! Please check git pull${NC}"
    exit 1
fi
echo ""

# 4. Build frontend
echo -e "${YELLOW}Step 4: Frontend 빌드${NC}"
echo "  npm run build"
npm run build
echo -e "${GREEN}✅ Complete${NC}"
echo ""

# 5. Rebuild Docker image
echo -e "${YELLOW}Step 5: Docker 이미지 다시 빌드${NC}"
cd /root/uvis
docker-compose build uvis-frontend
echo -e "${GREEN}✅ Complete${NC}"
echo ""

# 6. Restart container
echo -e "${YELLOW}Step 6: 컨테이너 재시작${NC}"
docker-compose restart uvis-frontend
echo ""
echo "Waiting 10 seconds for container to start..."
sleep 10
echo -e "${GREEN}✅ Complete${NC}"
echo ""

# 7. Check logs
echo -e "${YELLOW}Step 7: 로그 확인${NC}"
docker logs uvis-frontend --tail 20
echo ""

# 8. Test instructions
echo "=================================================="
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo "=================================================="
echo ""
echo "다음 단계: 브라우저 테스트"
echo ""
echo "1. 캐시 클리어 (중요!)"
echo "   - Chrome: Ctrl+Shift+Delete"
echo "   - '캐시된 이미지 및 파일' 체크"
echo "   - 삭제"
echo "   또는 시크릿 모드 사용"
echo ""
echo "2. URL 접속"
echo "   http://139.150.11.99/dispatch-rules"
echo ""
echo "3. 규칙 수정 테스트"
echo "   - 규칙 선택"
echo "   - '수정' 버튼 클릭"
echo "   - 이름 또는 우선순위 변경"
echo "   - '수정' 버튼 클릭"
echo "   - ✅ 성공 메시지 확인!"
echo ""
echo "4. 개발자 도구로 확인 (F12)"
echo "   - Network 탭"
echo "   - PUT 요청 찾기"
echo "   - Payload: {\"rule_update\": {...}} ✅"
echo "   - Response: 200 OK ✅"
echo ""
echo "=================================================="
echo ""

# 9. Quick API test
echo -e "${YELLOW}Step 8: Quick API Test${NC}"
echo ""
echo "Testing backend API with correct format..."
RESPONSE=$(curl -s -X PUT http://localhost:8000/api/v1/dispatch-rules/1 \
  -H "Content-Type: application/json" \
  -d '{"rule_update": {"name": "자동테스트_'$(date +%s)'", "priority": 888}}')

echo "Response:"
echo "$RESPONSE" | jq .
echo ""

if echo "$RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API 정상 작동!${NC}"
else
    echo -e "${RED}❌ Backend API 에러 - 로그 확인 필요${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 모든 작업 완료!${NC}"
echo "=================================================="
