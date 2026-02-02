#!/bin/bash
# 서버에서 실행: Settings 페이지 Sidebar 수정 배포

echo "🚀 Settings 페이지 Sidebar 추가 배포 시작..."
echo ""

cd /root/uvis

echo "📥 Step 1: 최신 코드 가져오기..."
git pull origin main
echo ""

echo "🔨 Step 2: Frontend 재빌드..."
docker-compose -f docker-compose.prod.yml up -d --build frontend
echo ""

echo "⏳ Step 3: 빌드 완료 대기 (25초)..."
sleep 25
echo ""

echo "📊 Step 4: 컨테이너 상태 확인..."
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""

echo "✅ 배포 완료!"
echo ""
echo "🌐 확인 URL:"
echo "   - Frontend: http://139.150.11.99"
echo "   - Settings: http://139.150.11.99 → 설정 메뉴 클릭"
echo ""
echo "✨ 이제 설정 페이지에서도 사이드바가 표시됩니다!"
