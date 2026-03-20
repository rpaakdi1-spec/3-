#!/bin/bash
# 템플릿 관리 페이지 배포 스크립트
# Usage: bash DEPLOY_TEMPLATE_MANAGEMENT.sh

set -e  # 에러 발생 시 스크립트 중단

echo "================================================"
echo "템플릿 관리 페이지 배포 시작"
echo "================================================"
echo ""

# Step 1: 현재 디렉토리 확인
echo "✅ Step 1: 현재 디렉토리 확인"
pwd
echo ""

# Step 2: Git 상태 확인
echo "✅ Step 2: Git 상태 확인"
git status --short
echo ""

# Step 3: 변경된 파일 확인
echo "✅ Step 3: 변경된 파일 확인"
echo "- frontend/src/pages/TemplateManagementPage.tsx (새 파일)"
echo "- frontend/src/config/navigation.ts (수정)"
echo "- frontend/src/App.tsx (수정)"
ls -lh frontend/src/pages/TemplateManagementPage.tsx 2>/dev/null || echo "⚠️  파일이 생성되지 않았습니다!"
echo ""

# Step 4: 프론트엔드 빌드
echo "✅ Step 4: 프론트엔드 빌드 (캐시 없이)"
echo "빌드 시작... (약 3-5분 소요)"
docker compose build --no-cache frontend
if [ $? -eq 0 ]; then
    echo "✅ 빌드 성공!"
else
    echo "❌ 빌드 실패! 로그를 확인하세요."
    exit 1
fi
echo ""

# Step 5: 컨테이너 재시작
echo "✅ Step 5: 프론트엔드 컨테이너 재시작"
docker compose up -d frontend
docker compose ps frontend
echo ""

# Step 6: 로그 확인
echo "✅ Step 6: 프론트엔드 로그 확인 (최근 20줄)"
docker compose logs frontend --tail=20
echo ""

# Step 7: 배포 완료 메시지
echo "================================================"
echo "✅ 배포 완료!"
echo "================================================"
echo ""
echo "📋 확인 사항:"
echo "1. 브라우저에서 강력 새로고침 (Ctrl+Shift+R)"
echo "2. 또는 시크릿 모드로 접속"
echo "3. URL: http://139.150.11.99/template-management"
echo "4. 사이드바 메뉴: 운영 관리 > 템플릿 관리 (NEW)"
echo ""
echo "🧪 테스트 항목:"
echo "- [ ] 템플릿 목록 표시"
echo "- [ ] 검색/필터 기능"
echo "- [ ] 즐겨찾기 추가/제거"
echo "- [ ] 활성화/비활성화"
echo "- [ ] 템플릿 복제"
echo "- [ ] 템플릿 삭제"
echo ""
echo "💡 다음 단계:"
echo "1. 기능 테스트 완료 후"
echo "2. Git 커밋 & 푸시"
echo "   git add ."
echo "   git commit -m \"feat(template-management): add template management page\""
echo "   git push origin genspark_ai_developer"
echo ""
echo "================================================"
