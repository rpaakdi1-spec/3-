#!/bin/bash

# 템플릿 관리 401 오류 해결 스크립트
# ======================================

set -e

cd /root/uvis

echo "================================================"
echo "🔧 템플릿 관리 401 오류 해결 스크립트"
echo "================================================"
echo ""

# 1. 프론트엔드 완전 재빌드
echo "=== 1단계: 프론트엔드 완전 재빌드 ==="
echo "⏳ 기존 컨테이너 중지 및 제거..."
docker compose stop frontend
docker compose rm -f frontend

echo "⏳ 이전 이미지 제거..."
docker rmi uvis-frontend 2>/dev/null || echo "  (이미지 없음 - 건너뜀)"

echo ""
echo "⏳ 완전 재빌드 시작 (--no-cache, 약 4분 소요)..."
echo "  - npm install"
echo "  - vite build"
echo "  - nginx 이미지 생성"
echo ""
docker compose build --no-cache frontend

echo ""
echo "=== 2단계: 컨테이너 재시작 ==="
docker compose up -d frontend

sleep 3

echo ""
echo "=== 3단계: 컨테이너 상태 확인 ==="
docker compose ps frontend

echo ""
echo "=== 4단계: Nginx 로그 확인 ==="
docker compose logs frontend --tail=15

echo ""
echo "✅ 서버 측 작업 완료!"
echo ""
echo "================================================"
echo "📱 브라우저에서 수행할 작업"
echo "================================================"
echo ""
echo "🔴 중요: 브라우저 캐시를 완전히 삭제해야 합니다!"
echo ""
echo "방법 1: 시크릿 모드 (가장 확실)"
echo "  1. Ctrl + Shift + N (Chrome) 또는 Ctrl + Shift + P (Firefox)"
echo "  2. http://139.150.11.99 접속"
echo "  3. 로그인 (username: admin, password: 확인 필요)"
echo "  4. 템플릿 관리 페이지로 이동"
echo ""
echo "방법 2: 캐시 삭제 + 강력 새로고침"
echo "  1. Ctrl + Shift + Delete → 전체 기간 선택"
echo "  2. '쿠키 및 캐시' 체크 → 데이터 삭제"
echo "  3. F12 개발자 도구 열기"
echo "  4. Network 탭 → 'Disable cache' 체크"
echo "  5. 개발자 도구 열린 상태에서 Ctrl + Shift + R"
echo ""
echo "방법 3: 콘솔에서 강제 로그아웃"
echo "  1. F12 → Console 탭"
echo "  2. 다음 명령어 실행:"
echo "     localStorage.clear();"
echo "     sessionStorage.clear();"
echo "     location.href = '/login';"
echo ""
echo "================================================"
echo "✅ 테스트 체크리스트"
echo "================================================"
echo ""
echo "로그인 후 http://139.150.11.99/template-management 에서:"
echo ""
echo "  1. F12 → Network 탭 열기"
echo "  2. 즐겨찾기 별(⭐) 아이콘 클릭"
echo "  3. PUT 요청 찾기 (templates/40 등)"
echo "  4. Request Headers 확인:"
echo "     ✅ Authorization: Bearer eyJhbGci..."
echo "     ❌ Authorization 헤더 없음 → 브라우저 캐시 다시 삭제"
echo ""
echo "  5. Response 확인:"
echo "     ✅ Status 200 OK"
echo "     ❌ Status 401 → 토큰 만료, 다시 로그인"
echo ""
echo "================================================"
echo "🔍 DB 확인 명령어"
echo "================================================"
echo ""
echo "# 최근 변경된 템플릿 5개 확인"
echo "docker compose exec -T db psql -U uvis_user -d uvis_db -c \\"
echo "  \"SELECT id, name, is_favorite, is_active, updated_at"
echo "   FROM dispatch_form_templates"
echo "   ORDER BY updated_at DESC LIMIT 5;\""
echo ""
echo "# 즐겨찾기 템플릿만 확인"
echo "docker compose exec -T db psql -U uvis_user -d uvis_db -c \\"
echo "  \"SELECT id, name, is_favorite"
echo "   FROM dispatch_form_templates"
echo "   WHERE is_favorite = true;\""
echo ""
echo "================================================"
echo "📞 문제 해결 안 될 시"
echo "================================================"
echo ""
echo "1. Network 탭 스크린샷 (Request Headers 부분)"
echo "2. Console 탭 에러 메시지"
echo "3. 다음 명령어 결과:"
echo "   docker compose logs backend --tail=50 | grep 'dispatch-form/templates'"
echo ""
echo "이 정보를 제공해주세요."
echo ""
echo "================================================"
echo "🎉 완료!"
echo "================================================"
