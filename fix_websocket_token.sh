#!/bin/bash

cat << 'EOF'
=== WebSocket 토큰 인증 추가 ===

다음 명령어를 실행하세요:

cd /root/uvis/frontend

# 1. 백업
cp src/pages/DashboardPage.tsx src/pages/DashboardPage.tsx.backup.ws

# 2. 38번 줄 수정 (토큰 추가)
sed -i '38s|const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/dashboard`;|const token = localStorage.getItem('\''access_token'\'');\n    const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/dashboard?token=${token}`;|' src/pages/DashboardPage.tsx

# 3. 변경 확인
echo "=== 수정된 코드 확인 ==="
sed -n '36,42p' src/pages/DashboardPage.tsx

# 4. 빌드
npm run build

# 5. 배포
cd /root/uvis
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker exec uvis-frontend nginx -s reload

echo ""
echo "✅ WebSocket 토큰 인증 추가 완료!"
echo "브라우저를 새로고침(Ctrl+F5)하세요!"
echo "WebSocket 연결이 성공하면 녹색 점이 표시됩니다."
EOF

