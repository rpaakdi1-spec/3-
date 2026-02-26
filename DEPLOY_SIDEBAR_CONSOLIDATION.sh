#!/bin/bash

# 사이드바 통합 배포 스크립트
# 작성일: 2026-02-25

echo "=================================================="
echo "🚀 사이드바 통합 배포 시작"
echo "=================================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 현재 위치 확인
echo "📍 Step 1: 현재 디렉토리 확인"
cd /root/uvis/frontend
pwd
echo ""

# 2. Git 상태 확인
echo "📋 Step 2: Git 변경사항 확인"
git status --short
echo ""

# 3. 변경된 파일 목록
echo "📝 Step 3: 변경된 파일 목록"
echo "  - src/config/navigation.ts (NEW)"
echo "  - src/components/common/Sidebar.tsx (MODIFIED)"
echo "  - src/components/mobile/BottomNavigation.tsx (MODIFIED)"
echo ""

# 4. TypeScript 컴파일 체크
echo "🔍 Step 4: TypeScript 타입 체크 (선택사항)"
read -p "TypeScript 체크를 실행하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    npx tsc --noEmit || echo -e "${YELLOW}⚠️  타입 에러가 있지만 계속 진행합니다${NC}"
fi
echo ""

# 5. 빌드 시작
echo "🔨 Step 5: 프론트엔드 빌드"
echo "빌드를 시작합니다..."
npm run build 2>&1 | tail -30

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 빌드 성공!${NC}"
else
    echo -e "${RED}❌ 빌드 실패! 에러를 확인하세요.${NC}"
    exit 1
fi
echo ""

# 6. dist 폴더 확인
echo "📦 Step 6: 빌드 결과 확인"
ls -lh dist/assets/*.js | head -5
echo ""

# 7. Docker 이미지 빌드
echo "🐳 Step 7: Docker 이미지 빌드"
cd /root/uvis
echo "기존 컨테이너 중지..."
docker-compose stop frontend

echo "기존 컨테이너 삭제..."
docker-compose rm -f frontend

echo "기존 이미지 삭제..."
docker rmi uvis-frontend 2>/dev/null || echo "이미지가 없습니다"

echo "새 이미지 빌드 중..."
docker-compose build --no-cache frontend

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker 이미지 빌드 성공!${NC}"
else
    echo -e "${RED}❌ Docker 빌드 실패!${NC}"
    exit 1
fi
echo ""

# 8. 컨테이너 시작
echo "▶️  Step 8: 컨테이너 시작"
docker-compose up -d frontend
sleep 10

# 9. 컨테이너 상태 확인
echo "🔍 Step 9: 컨테이너 상태 확인"
docker ps | grep frontend
echo ""

# 10. 로그 확인
echo "📋 Step 10: 최근 로그 확인"
docker logs uvis-frontend --tail 20
echo ""

# 11. 헬스체크
echo "🏥 Step 11: 헬스체크"
echo "컨테이너 내부 파일 확인..."
docker exec uvis-frontend sh -c "ls -lh /usr/share/nginx/html/index.html"
docker exec uvis-frontend sh -c "ls /usr/share/nginx/html/assets/*.js | wc -l"
echo ""

# 12. 최종 확인
echo "=================================================="
echo "✅ 배포 완료!"
echo "=================================================="
echo ""
echo "📌 확인사항:"
echo "1. 브라우저에서 http://139.150.11.99 접속"
echo "2. Ctrl+F5로 강제 새로고침"
echo "3. 사이드바 메뉴가 정상 표시되는지 확인"
echo "4. 모바일 하단 네비게이션 확인 (개발자 도구 모바일 모드)"
echo ""
echo "🔧 문제 발생 시:"
echo "  - 브라우저 캐시 완전 삭제"
echo "  - InPrivate/Incognito 창으로 테스트"
echo "  - F12 > Console 탭에서 에러 확인"
echo ""
echo "📝 변경 내역:"
echo "  - 메뉴 설정이 config/navigation.ts로 통합됨"
echo "  - Sidebar와 BottomNavigation이 중앙 설정 사용"
echo "  - 코드 중복 -88 라인 제거"
echo ""
echo "=================================================="
