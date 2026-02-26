#!/bin/bash
# UI 파일 충돌 해결 스크립트

echo "🔧 UI 파일 충돌 해결 시작..."
echo ""

cd /root/uvis

# 1. 현재 상태 백업 (안전장치)
echo "📦 1. 안전 백업 생성 중..."
docker exec uvis-frontend cp -r /usr/share/nginx/html /usr/share/nginx/html.backup.emergency.$(date +%Y%m%d_%H%M%S)

# 2. 혼합된 파일들 완전 삭제
echo "🗑️  2. 기존 파일 완전 삭제 중..."
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*

# 3. 깨끗한 빌드 복사
echo "📂 3. 새 빌드 복사 중..."
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/

# 4. 권한 수정
echo "🔐 4. 파일 권한 수정 중..."
docker exec uvis-frontend chown -R nginx:nginx /usr/share/nginx/html 2>/dev/null || true

# 5. Nginx 재시작
echo "🔄 5. Nginx 재시작 중..."
docker exec uvis-frontend nginx -s reload

echo ""
echo "✅ 복구 완료!"
echo ""

# 6. 검증
echo "🔍 6. 결과 검증 중..."
echo ""
echo "=== index.html 참조 ==="
docker exec uvis-frontend grep -o 'src="/assets/index-[^"]*\.js"' /usr/share/nginx/html/index.html

echo ""
echo "=== 실제 index-*.js 파일 (1개만 있어야 정상) ==="
docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/index-*.js 2>&1

echo ""
echo "=== CSS 파일 개수 ==="
CSS_COUNT=$(docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.css 2>/dev/null | wc -l)
echo "$CSS_COUNT 개"

echo ""
echo "=== rule_update 확인 ==="
docker exec uvis-frontend grep -l "rule_update" /usr/share/nginx/html/assets/DispatchRulesPage-*.js 2>/dev/null || echo "❌ rule_update 파일 없음"

echo ""
echo "=========================================="
echo "🎉 완료!"
echo ""
echo "📋 다음 단계:"
echo "1. 브라우저 캐시 완전 삭제 (Ctrl+Shift+Delete)"
echo "2. 또는 시크릿 모드로 테스트 (Ctrl+Shift+N)"
echo "3. http://139.150.11.99 접속"
echo "4. UI 정상 확인"
echo ""
echo "🐛 문제 계속되면:"
echo "   F12 → Console 탭에서 404 에러 확인"
echo "   Network 탭에서 실패한 요청 확인"
echo "=========================================="
