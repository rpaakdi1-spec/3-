#!/bin/bash

echo "================================================================"
echo "🔍 UVIS WebSocket 최종 진단 스크립트"
echo "================================================================"
echo ""

# 컨테이너 상태
echo "1️⃣ 컨테이너 상태 확인"
echo "────────────────────────────────────────────────────────────────"
docker ps --filter "name=uvis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Nginx 설정 확인 (실제 적용된 설정)
echo "2️⃣ Nginx 실제 적용 설정 (nginx -T)"
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend nginx -T 2>&1 | grep -B 3 -A 30 "location.*dispatches.*ws"
echo ""

# conf.d 확인
echo "3️⃣ conf.d 디렉토리 확인"
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend ls -la /etc/nginx/conf.d/
echo ""
echo "conf.d/default.conf 내용:"
docker exec uvis-frontend cat /etc/nginx/conf.d/default.conf 2>/dev/null || echo "❌ 파일 없음"
echo ""

# 정적 파일 확인
echo "4️⃣ 프론트엔드 빌드 파일 확인"
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/*.html /usr/share/nginx/html/assets/*.js 2>/dev/null | tail -10
echo ""

# WebSocket URL 확인 (빌드 파일 내부)
echo "5️⃣ 빌드 파일 내 WebSocket URL 확인"
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend grep -oh "ws://[^\"']*" /usr/share/nginx/html/assets/*.js 2>/dev/null | sort -u
echo ""

# Nginx 에러 로그
echo "6️⃣ Nginx 에러 로그 (최근 30줄)"
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend cat /var/log/nginx/error.log | tail -30
if [ -z "$(docker exec uvis-frontend cat /var/log/nginx/error.log)" ]; then
    echo "✅ 에러 로그 없음"
fi
echo ""

# Nginx 액세스 로그 (WebSocket 요청만)
echo "7️⃣ Nginx 액세스 로그 (WebSocket 요청)"
echo "────────────────────────────────────────────────────────────────"
docker logs uvis-frontend 2>&1 | grep -E "ws/dashboard|ws/alerts" | tail -20
echo ""

# 백엔드 로그
echo "8️⃣ 백엔드 WebSocket 로그"
echo "────────────────────────────────────────────────────────────────"
docker logs uvis-backend --tail=50 2>&1 | grep -E "WebSocket|Dashboard|Alerts|Stats|connection"
echo ""

# 네트워크 연결 테스트
echo "9️⃣ 네트워크 연결 테스트"
echo "────────────────────────────────────────────────────────────────"
echo "Frontend → Backend 연결:"
docker exec uvis-frontend nc -zv backend 8000 2>&1
echo ""
echo "외부 → Frontend 80 포트:"
curl -s -I http://localhost/ | head -5
echo ""

# WebSocket 직접 테스트
echo "🔟 WebSocket 직접 테스트 (wscat, 5초 타임아웃)"
echo "────────────────────────────────────────────────────────────────"
timeout 5 wscat -c ws://localhost/api/v1/dispatches/ws/dashboard 2>&1 | head -10 || echo "⚠️ 연결 실패 또는 타임아웃"
echo ""

# 브라우저 캐시 문제 진단
echo "1️⃣1️⃣ 빌드 파일 타임스탬프"
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend stat /usr/share/nginx/html/assets/RealtimeDashboardPage-*.js 2>/dev/null | grep -E "File:|Modify:" || echo "❌ 파일 찾을 수 없음"
echo ""

echo "================================================================"
echo "✅ 진단 완료!"
echo "================================================================"
echo ""
echo "📋 다음 정보를 확인하세요:"
echo "   • 2️⃣: location ~ ^/api/v1/(dispatches/)?ws/ 블록이 올바른지"
echo "   • 3️⃣: conf.d/default.conf가 비활성화되었는지"
echo "   • 5️⃣: 빌드 파일에 올바른 WebSocket URL이 있는지"
echo "   • 6️⃣: Nginx 에러가 있는지"
echo "   • 8️⃣: 백엔드가 연결을 수락하고 데이터를 전송하는지"
echo "   • 🔟: wscat 테스트가 성공하는지"
echo ""
