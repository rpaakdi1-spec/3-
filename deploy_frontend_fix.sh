#!/bin/bash

echo "🚀 프론트엔드 배포 시작..."

SERVER="root@139.150.11.99"
FRONTEND_DIST="/home/user/webapp/frontend/dist"
SERVER_PATH="/root/uvis/frontend/dist"

# 1. 빌드된 파일 압축
echo "📦 빌드 파일 압축 중..."
cd /home/user/webapp/frontend
tar -czf dist.tar.gz dist/

# 2. 서버로 전송
echo "📤 서버로 전송 중..."
scp dist.tar.gz $SERVER:/root/uvis/frontend/

# 3. 서버에서 압축 해제 및 배포
echo "🔧 서버에서 배포 중..."
ssh $SERVER << 'ENDSSH'
cd /root/uvis/frontend
rm -rf dist.backup
mv dist dist.backup 2>/dev/null || true
tar -xzf dist.tar.gz
rm dist.tar.gz
echo "✅ 프론트엔드 배포 완료"
ENDSSH

# 4. 로컬 임시 파일 삭제
rm /home/user/webapp/frontend/dist.tar.gz

echo "🎉 배포 완료!"
echo ""
echo "📋 테스트 방법:"
echo "1. 브라우저에서 Ctrl+Shift+R (캐시 무시 새로고침)"
echo "2. F12 개발자 도구 → Console 탭 열기"
echo "3. 배차 최적화 실행"
echo "4. Console에서 진단 로그 확인:"
echo "   - '🔍 dispatch 데이터:'"
echo "   - '🔍 찾는 vehicle_id:'"
echo "   - '🔍 사용 가능한 vehicles:'"
