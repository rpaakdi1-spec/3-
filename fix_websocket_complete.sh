#!/bin/bash

echo "================================================================"
echo "🔧 UVIS WebSocket 완전 복구 스크립트"
echo "================================================================"
echo ""

# 백업
echo "1️⃣ 설정 파일 백업..."
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
cp /root/uvis/nginx/nginx.conf /root/uvis/nginx/nginx.conf.backup_${BACKUP_DATE} 2>/dev/null || true
echo "✅ 백업 완료: nginx.conf.backup_${BACKUP_DATE}"
echo ""

# Nginx 설정 수정 확인
echo "2️⃣ Nginx 설정 확인..."
echo "────────────────────────────────────────────────────────────────"

# proxy_pass 확인
echo "현재 proxy_pass 설정:"
grep "proxy_pass" /root/uvis/nginx/nginx.conf | grep -v "#"
echo ""

# WebSocket location 블록 확인
echo "WebSocket location 블록:"
grep -A 15 "location.*dispatches.*ws" /root/uvis/nginx/nginx.conf | head -20
echo ""

# conf.d/default.conf 비활성화
echo "3️⃣ conf.d/default.conf 비활성화..."
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend bash -c '
if [ -f /etc/nginx/conf.d/default.conf ]; then
    mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.disabled
    echo "✅ default.conf 비활성화 완료"
else
    echo "ℹ️  default.conf 이미 비활성화됨"
fi
'
echo ""

# Nginx 설정 복사 및 테스트
echo "4️⃣ Nginx 설정 배포..."
echo "────────────────────────────────────────────────────────────────"
docker cp /root/uvis/nginx/nginx.conf uvis-frontend:/etc/nginx/nginx.conf
echo "✅ nginx.conf 복사 완료"
echo ""

echo "설정 테스트 중..."
docker exec uvis-frontend nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Nginx 설정 테스트 통과"
else
    echo "❌ Nginx 설정 오류!"
    exit 1
fi
echo ""

# Nginx 재로드
echo "5️⃣ Nginx 재로드..."
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend nginx -s reload
echo "✅ Nginx 재로드 완료"
echo ""

# 프론트엔드 빌드 확인
echo "6️⃣ 프론트엔드 빌드 파일 확인..."
echo "────────────────────────────────────────────────────────────────"
echo "index.html 존재 여부:"
docker exec uvis-frontend ls -lh /usr/share/nginx/html/index.html
echo ""
echo "JavaScript 파일 (최근 5개):"
docker exec uvis-frontend ls -lht /usr/share/nginx/html/assets/*.js 2>/dev/null | head -5
echo ""

# WebSocket URL 확인
echo "7️⃣ 빌드 파일의 WebSocket URL 확인..."
echo "────────────────────────────────────────────────────────────────"
WRONG_URL=$(docker exec uvis-frontend grep -r "ws/alerts" /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l)
CORRECT_URL=$(docker exec uvis-frontend grep -r "dispatches/ws" /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l)

echo "잘못된 URL (/api/v1/ws/alerts): $WRONG_URL 개"
echo "올바른 URL (/api/v1/dispatches/ws/...): $CORRECT_URL 개"
echo ""

if [ $WRONG_URL -gt 0 ]; then
    echo "⚠️  경고: 잘못된 WebSocket URL이 빌드 파일에 존재합니다!"
    echo "   프론트엔드를 다시 빌드하고 배포해야 합니다."
    echo ""
    echo "   해결 방법:"
    echo "   1. /root/uvis/frontend/src/hooks/useRealtimeData.ts 수정"
    echo "   2. cd /root/uvis/frontend && npm run build"
    echo "   3. docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/"
    echo "   4. docker restart uvis-frontend"
    echo ""
fi

# 백엔드 확인
echo "8️⃣ 백엔드 상태 확인..."
echo "────────────────────────────────────────────────────────────────"
docker ps | grep uvis-backend
echo ""
docker logs uvis-backend --tail=10 | grep -E "INFO|WARNING|ERROR"
echo ""

# 연결 테스트
echo "9️⃣ WebSocket 연결 테스트..."
echo "────────────────────────────────────────────────────────────────"
echo "Health endpoint:"
curl -s -I http://localhost/health | head -3
echo ""

echo "WebSocket 테스트 (5초):"
timeout 5 wscat -c ws://localhost/api/v1/dispatches/ws/dashboard 2>&1 | head -5 || echo "⚠️ 연결 실패"
echo ""

# 최종 체크리스트
echo "================================================================"
echo "✅ 복구 스크립트 완료!"
echo "================================================================"
echo ""
echo "📋 최종 체크리스트:"
echo "   □ Nginx 설정 테스트 통과"
echo "   □ conf.d/default.conf 비활성화"
echo "   □ index.html 존재"
echo "   □ 빌드 파일에 올바른 WebSocket URL"
echo "   □ 백엔드 정상 실행"
echo "   □ wscat 테스트 성공"
echo ""
echo "🌐 브라우저 테스트 방법:"
echo "   1. 모든 브라우저 창 완전히 종료 (작업 관리자 확인)"
echo "   2. 시크릿/인코그니토 모드로 열기"
echo "   3. F12 → Console 탭 열기"
echo "   4. http://139.150.11.99/realtime 접속"
echo "   5. Ctrl+Shift+R로 강력 새로고침 3회"
echo ""
echo "예상 콘솔 출력:"
echo "   ✅ WebSocket connected: ws://139.150.11.99/api/v1/dispatches/ws/dashboard"
echo "   📊 Dashboard WebSocket connected"
echo "   { total_orders: 0, available_vehicles: 46, ... }"
echo ""
