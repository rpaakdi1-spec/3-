#!/bin/bash
# Deploy faster GPS update version

echo "🚀 더 빠른 GPS 업데이트 버전 배포"
echo "=================================="
echo ""
echo "📋 변경사항:"
echo "   • GPS 데이터 갱신: 30초 → 10초"
echo "   • 자동 GPS 동기화: 2분마다 실행"
echo "   • 업데이트 주기 UI에 표시"
echo ""
echo "⚠️  서버에서 실행할 명령어:"
echo ""
cat << 'DEPLOY'
# SSH로 서버 접속
ssh root@139.150.11.99

# 배포 실행
cd /root/uvis/frontend
docker exec uvis-frontend rm -rf /usr/share/nginx/html/*
docker cp dist/. uvis-frontend:/usr/share/nginx/html/
docker restart uvis-frontend

# 완료 확인
sleep 10
echo "✅ 배포 완료!"
echo "📡 GPS 업데이트: 10초마다"
echo "🔄 GPS 동기화: 2분마다"
echo "🌐 테스트: http://139.150.11.99/realtime"
DEPLOY

echo ""
echo "📦 빌드 파일 위치: /home/user/webapp/frontend/dist/"
echo "📊 빌드 크기: $(du -sh /home/user/webapp/frontend/dist | cut -f1)"
echo ""
