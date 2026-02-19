#!/bin/bash
# Deploy Enhanced Realtime Dashboard to Production Server
# This script deploys the built frontend to the uvis-frontend Docker container

set -e

echo "🚀 실시간 대시보드 향상 버전 배포"
echo "=================================="
echo ""

# Check if dist directory exists
if [ ! -d "/home/user/webapp/frontend/dist" ]; then
  echo "❌ Error: dist directory not found"
  echo "   Please run 'npm run build' first"
  exit 1
fi

echo "📦 배포 파일 확인..."
DIST_SIZE=$(du -sh /home/user/webapp/frontend/dist | cut -f1)
FILE_COUNT=$(find /home/user/webapp/frontend/dist -type f | wc -l)
echo "   • 크기: ${DIST_SIZE}"
echo "   • 파일 수: ${FILE_COUNT}개"
echo ""

# Note: This is a template script
# The actual deployment should be done on the production server at 139.150.11.99

cat << 'EOF'
⚠️  이 스크립트는 샌드박스 환경에서 실행됩니다.
실제 프로덕션 서버에 배포하려면 아래 명령어를 서버에서 실행하세요:

📌 배포 명령어 (서버: 139.150.11.99)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Step 1: SSH로 서버 접속
ssh root@139.150.11.99

# Step 2: 프론트엔드 빌드
cd /root/uvis/frontend
npm run build

# Step 3: Docker 컨테이너에 배포
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*
docker cp dist/. uvis-frontend:/usr/share/nginx/html/
docker restart uvis-frontend

# Step 4: 배포 확인 (10초 대기)
echo "⏳ Nginx 재시작 대기 중..."
sleep 10

# Step 5: 헬스 체크
curl -I http://localhost/realtime

echo ""
echo "✅ 배포 완료!"
echo "   테스트 URL: http://139.150.11.99/realtime"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 배포 후 확인사항:
1. 브라우저에서 http://139.150.11.99/realtime 접속
2. F12 → Console 탭에서 WebSocket 연결 로그 확인
3. 차량 마커 클릭 → 운전자 정보 및 전화번호 표시 확인
4. 전화번호 클릭 → 전화 앱 실행 확인

🐛 문제 발생 시:
# 백엔드 로그 확인
docker logs uvis-backend --tail=50

# 프론트엔드 로그 확인
docker logs uvis-frontend --tail=50

# 브라우저 캐시 클리어
Ctrl+Shift+Delete → 캐시 삭제 → 새로고침 (Ctrl+F5)

EOF

echo ""
echo "📦 로컬 빌드 파일 준비 완료"
echo "   위 명령어를 프로덕션 서버에서 실행하세요."
echo ""
