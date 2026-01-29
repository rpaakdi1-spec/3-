#!/bin/bash

# UVIS Gabia Server Final Deployment Script
# This script handles complete deployment with all fixes

set -e

echo "======================================"
echo "🚀 UVIS Gabia 서버 최종 배포 시작"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Navigate to project directory
echo "Step 1: 프로젝트 디렉토리로 이동..."
cd /root/uvis || { echo -e "${RED}❌ 디렉토리 없음. 먼저 git clone 필요${NC}"; exit 1; }
pwd

# Step 2: Fetch latest code
echo ""
echo "Step 2: 최신 코드 가져오기..."
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer
echo -e "${GREEN}✓ 최신 코드 동기화 완료${NC}"
git log -1 --oneline

# Step 3: Verify required files
echo ""
echo "Step 3: 필수 파일 확인..."
echo "Backend config:"
head -5 backend/app/core/config.py

echo ""
echo "Docker compose files:"
ls -lh docker-compose*.yml

# Step 4: Setup environment variables
echo ""
echo "Step 4: 환경 변수 설정..."
if [ -f ".env.production" ]; then
    cp .env.production .env
    echo -e "${GREEN}✓ .env 파일 생성 완료${NC}"
else
    cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://uvis_user:uvis_password@db:5432/uvis_db

# Redis
REDIS_URL=redis://redis:6379/0

# Backend
SECRET_KEY=gabia-uvis-production-secret-2026
ENVIRONMENT=production

# Naver Maps API
NAVER_MAP_CLIENT_ID=pkciiaux61
NAVER_MAP_CLIENT_SECRET=dBi4yjpGEj7SJTYwAz00e8pab6XuumhdQH4WbFy5

# CORS
CORS_ORIGINS=http://139.150.11.99,http://139.150.11.99:3000,http://139.150.11.99:8000,http://localhost:3000

# Frontend
REACT_APP_API_URL=http://139.150.11.99:8000
REACT_APP_WS_URL=ws://139.150.11.99:8000/ws
EOF
    echo -e "${GREEN}✓ .env 파일 생성 완료${NC}"
fi

echo "Environment variables:"
cat .env | grep -v SECRET

# Step 5: Stop and cleanup existing containers
echo ""
echo "Step 5: 기존 컨테이너 정리..."
docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
docker system prune -af
echo -e "${GREEN}✓ 정리 완료${NC}"

# Step 6: Build images
echo ""
echo "Step 6: Docker 이미지 빌드 (15-20분 예상)..."
echo "이 과정은 시간이 걸립니다. 커피 한 잔 하세요 ☕"
echo ""

# Build backend
echo "Building backend..."
docker-compose -f docker-compose.prod.yml build --no-cache backend 2>&1 | tee /tmp/backend-build.log
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✓ Backend 빌드 성공${NC}"
else
    echo -e "${RED}❌ Backend 빌드 실패. 로그 확인: /tmp/backend-build.log${NC}"
    exit 1
fi

# Build frontend
echo ""
echo "Building frontend..."
docker-compose -f docker-compose.prod.yml build --no-cache frontend 2>&1 | tee /tmp/frontend-build.log
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend 빌드 성공${NC}"
else
    echo -e "${RED}❌ Frontend 빌드 실패. 로그 확인: /tmp/frontend-build.log${NC}"
    exit 1
fi

# Step 7: Start containers
echo ""
echo "Step 7: 컨테이너 시작..."
docker-compose -f docker-compose.prod.yml up -d

echo "Waiting for services to initialize (30 seconds)..."
sleep 30

# Step 8: Check container status
echo ""
echo "Step 8: 컨테이너 상태 확인..."
docker-compose -f docker-compose.prod.yml ps

# Step 9: Health check with retries
echo ""
echo "Step 9: Health Check 수행..."
MAX_RETRIES=10
RETRY_COUNT=0
HEALTH_OK=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        HEALTH_OK=true
        echo -e "${GREEN}✓ Backend Health Check 성공!${NC}"
        curl -s http://localhost:8000/health | python3 -m json.tool
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "Retry $RETRY_COUNT/$MAX_RETRIES..."
        sleep 5
    fi
done

if [ "$HEALTH_OK" = false ]; then
    echo -e "${RED}❌ Backend Health Check 실패${NC}"
    echo "Backend logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=50 backend
    exit 1
fi

# Step 10: Display logs
echo ""
echo "Step 10: 최근 로그 확인..."
echo "Backend logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20 backend
echo ""
echo "Frontend logs:"
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend

# Final success message
echo ""
echo "======================================"
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo "======================================"
echo ""
echo "📍 접속 정보:"
echo "  - Frontend: http://139.150.11.99"
echo "  - Frontend (직접): http://139.150.11.99:3000"
echo "  - API Docs: http://139.150.11.99:8000/docs"
echo "  - Health: http://139.150.11.99:8000/health"
echo "  - Backend API: http://139.150.11.99:8000"
echo ""
echo "👤 테스트 계정:"
echo "  - 관리자: admin@example.com / admin123"
echo "  - 드라이버 1: driver1 / password123"
echo "  - 드라이버 2: driver2 / password123"
echo ""
echo "📊 컨테이너 관리:"
echo "  - 상태 확인: docker-compose -f docker-compose.prod.yml ps"
echo "  - 로그 확인: docker-compose -f docker-compose.prod.yml logs -f"
echo "  - 재시작: docker-compose -f docker-compose.prod.yml restart [service]"
echo ""
echo "🎉 배포가 성공적으로 완료되었습니다!"
