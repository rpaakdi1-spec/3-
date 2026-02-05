#!/bin/bash
# Frontend Build Fix - Quick Deploy Script
# 실행: chmod +x QUICK_FRONTEND_FIX.sh && ./QUICK_FRONTEND_FIX.sh

set -e

echo "=================================================="
echo "🚀 Frontend Build Fix 배포 스크립트"
echo "=================================================="
echo ""

# Step 1: 최신 코드 가져오기
echo "Step 1/5: 최신 코드 가져오기..."
cd /root/uvis
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer
echo "✅ 코드 업데이트 완료 (commit: 4aacfe4)"
echo ""

# Step 2: Frontend 재빌드
echo "Step 2/5: Frontend 재빌드..."
docker-compose build --no-cache frontend
echo "✅ Frontend 빌드 완료"
echo ""

# Step 3: Frontend & Nginx 재시작
echo "Step 3/5: Frontend & Nginx 재시작..."
docker-compose up -d --force-recreate frontend nginx
echo "✅ 컨테이너 재시작 완료"
echo ""

# Step 4: 안정화 대기
echo "Step 4/5: 서비스 안정화 대기 (30초)..."
sleep 30
echo "✅ 대기 완료"
echo ""

# Step 5: 최종 상태 확인
echo "Step 5/5: 최종 상태 확인..."
echo ""

echo "=== 컨테이너 상태 ==="
docker-compose ps
echo ""

echo "=== Frontend 로그 (최근 15줄) ==="
docker-compose logs --tail=15 frontend
echo ""

echo "=== Backend Health Check ==="
HEALTH=$(curl -s http://localhost:8000/health)
echo "$HEALTH"
if echo "$HEALTH" | grep -q "healthy"; then
  echo "✅ Backend: Healthy"
else
  echo "⚠️  Backend: Not Healthy"
fi
echo ""

echo "=== Frontend Access Test ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Frontend: Accessible (HTTP $HTTP_CODE)"
else
  echo "⚠️  Frontend: HTTP $HTTP_CODE"
fi
echo ""

echo "=================================================="
echo "🎉 배포 완료!"
echo "=================================================="
echo ""
echo "📍 접속 정보:"
echo "   - Frontend: http://YOUR_SERVER_IP/"
echo "   - Backend API: http://YOUR_SERVER_IP:8000/docs"
echo "   - Health Check: http://YOUR_SERVER_IP:8000/health"
echo ""
echo "📝 추가 확인이 필요한 경우:"
echo "   docker-compose logs frontend"
echo "   docker-compose logs backend"
echo "   docker-compose logs nginx"
echo ""
echo "=================================================="
