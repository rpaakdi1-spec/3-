#!/bin/bash

# 모바일 웹 최적화 배포 스크립트

echo "======================================"
echo "모바일 웹 최적화 배포"
echo "======================================"
echo ""

echo "📱 새로운 모바일 기능:"
echo "  ✅ MorePage - 더보기 메뉴"
echo "  ✅ MobileFilterSheet - 바텀 시트 필터"
echo "  ✅ MobileListItem - 터치 최적화 리스트"
echo "  ✅ MobileActionSheet - 액션 메뉴"
echo "  ✅ MobileFAB - 플로팅 버튼"
echo "  ✅ Pull to Refresh - 새로고침 제스처"
echo "  ✅ Swipeable Items - 스와이프 액션"
echo "  ✅ iOS Safe Area 대응"
echo ""

cat << 'EOF'
# 1. 프론트엔드 디렉토리로 이동
cd /root/uvis/frontend

# 2. 최신 코드 가져오기
git fetch origin main
git reset --hard origin/main

# 3. 최신 커밋 확인 (670f3e2 이어야 함)
echo "=== 현재 커밋 확인 ==="
git log --oneline -1

# 4. 새로운 파일 확인
echo ""
echo "=== 새로운 모바일 컴포넌트 확인 ==="
ls -la src/pages/MorePage.tsx
ls -la src/components/mobile/MobileFilterSheet.tsx
ls -la src/components/mobile/MobileListItem.tsx
ls -la src/components/mobile/MobileActionSheet.tsx

# 5. 프론트엔드 빌드
echo ""
echo "=== 프론트엔드 빌드 시작 ==="
npm run build

# 6. 빌드 결과물을 컨테이너에 복사
echo ""
echo "=== 컨테이너에 복사 ==="
docker cp dist/. uvis-frontend:/usr/share/nginx/html/

# 7. 프론트엔드 컨테이너 재시작
echo ""
echo "=== 프론트엔드 컨테이너 재시작 ==="
docker restart uvis-frontend

# 8. 10초 대기
sleep 10

# 9. 컨테이너 상태 확인
echo ""
echo "=== 컨테이너 상태 ==="
docker ps | grep uvis-frontend

# 10. 최근 로그 확인
echo ""
echo "=== 최근 로그 ==="
docker logs uvis-frontend --tail 20
EOF

echo ""
echo "======================================"
echo "모바일 테스트 가이드"
echo "======================================"
echo ""
echo "🧪 PC에서 테스트:"
echo "1. Chrome DevTools 열기 (F12)"
echo "2. 디바이스 툴바 켜기 (Ctrl+Shift+M)"
echo "3. 디바이스 선택 (iPhone 12, Galaxy S20 등)"
echo "4. 다음 URL 접속: http://139.150.11.99"
echo ""
echo "📱 실제 모바일에서 테스트:"
echo "1. 모바일 브라우저에서 http://139.150.11.99 접속"
echo "2. 홈 화면에 추가 (PWA 기능)"
echo "3. 앱처럼 사용"
echo ""
echo "✅ 확인 사항:"
echo "  □ 하단 네비게이션 바 표시"
echo "  □ '더보기' 탭 클릭 → MorePage 표시"
echo "  □ 사용자 프로필, 메뉴 아이템 표시"
echo "  □ 주문/배차 페이지에서 리스트 뷰 확인"
echo "  □ 검색 바 터치 동작 확인"
echo "  □ 아래로 당겨서 새로고침 동작 확인"
echo "  □ 스와이프 제스처 동작 확인"
echo ""
echo "🎨 디자인 확인:"
echo "  □ 버튼 터치 영역 충분 (최소 44x44px)"
echo "  □ 부드러운 애니메이션"
echo "  □ 스크롤 부드러움"
echo "  □ 텍스트 크기 적절"
echo "  □ 여백 충분"
echo ""
echo "📱 다양한 디바이스 테스트:"
echo "  □ iPhone 12 (390x844)"
echo "  □ iPhone SE (375x667)"
echo "  □ Galaxy S20 (360x800)"
echo "  □ iPad (768x1024)"
echo ""
echo "======================================"
echo "문제 해결"
echo "======================================"
echo ""
echo "❌ 하단 네비게이션이 안 보임:"
echo "   → 화면 크기 768px 미만인지 확인"
echo "   → useResponsive 훅 동작 확인"
echo ""
echo "❌ 더보기 페이지가 비어있음:"
echo "   → /more 라우트 등록 확인"
echo "   → MorePage.tsx 로드 확인"
echo ""
echo "❌ 터치 반응이 느림:"
echo "   → index.css 의 터치 최적화 CSS 확인"
echo "   → touch-action: manipulation 적용 확인"
echo ""
echo "======================================"
