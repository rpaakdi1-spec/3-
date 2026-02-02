#!/bin/bash
# 서버 배포 한 번에 실행
# 사용법: ssh root@139.150.11.99 < DEPLOY_NOW.sh

set -e

echo "🚀 배포 시작..."
echo ""

echo "📥 Step 1: 최신 코드 가져오기..."
cd /root/uvis
git pull origin main
echo "✅ 코드 업데이트 완료"
echo ""

echo "🔨 Step 2: Frontend 재빌드..."
docker-compose -f docker-compose.prod.yml up -d --build frontend
echo "✅ Frontend 재빌드 완료"
echo ""

echo "⏳ Step 3: 서비스 안정화 대기 (20초)..."
sleep 20
echo ""

echo "🏥 Step 4: 헬스 체크..."
echo "Backend:"
curl -s http://localhost:8000/health | jq || echo "⚠️  Backend 응답 없음"
echo ""

echo "📊 Step 5: 컨테이너 상태 확인..."
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""

echo "✅ 배포 완료!"
echo ""
echo "🌐 접속 URL:"
echo "   - Frontend: http://139.150.11.99"
echo "   - Backend:  http://139.150.11.99:8000"
echo "   - API Docs: http://139.150.11.99:8000/docs"
echo ""
echo "📝 상세 가이드: /root/uvis/SERVER_DEPLOYMENT_COMMANDS.md"
