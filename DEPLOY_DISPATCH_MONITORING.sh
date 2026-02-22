#!/bin/bash

echo "=================================================="
echo "🚀 AI 배차 모니터링 대시보드 배포 스크립트"
echo "=================================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 에러 발생시 스크립트 중단
set -e

# 프로젝트 루트 디렉토리 (서버 경로)
PROJECT_ROOT="/root/uvis"

echo "📂 프로젝트 디렉토리: $PROJECT_ROOT"
echo ""

# 1. Git Pull
echo "=================================================="
echo "📥 1. Git Pull - 최신 코드 가져오기"
echo "=================================================="
cd "$PROJECT_ROOT"
git pull origin main
echo -e "${GREEN}✅ Git pull 완료${NC}"
echo ""

# 2. 백엔드 재시작
echo "=================================================="
echo "🔄 2. 백엔드 재시작"
echo "=================================================="
cd "$PROJECT_ROOT"

# Docker Compose 사용 여부 확인
if [ -f "docker-compose.yml" ]; then
    echo "🐳 Docker Compose 사용"
    
    # 백엔드 컨테이너 재시작
    echo "Backend 컨테이너 재시작 중..."
    docker-compose restart backend
    
    # 상태 확인
    sleep 3
    if docker-compose ps | grep -q "backend.*Up"; then
        echo -e "${GREEN}✅ 백엔드 컨테이너 재시작 완료${NC}"
    else
        echo -e "${RED}❌ 백엔드 컨테이너 시작 실패${NC}"
        docker-compose logs --tail=20 backend
        exit 1
    fi
else
    echo "⚠️  Docker Compose 파일이 없습니다."
    echo "PM2 또는 systemd 서비스를 재시작해주세요:"
    echo ""
    echo "  # PM2 사용 시:"
    echo "  pm2 restart uvis-backend"
    echo ""
    echo "  # systemd 사용 시:"
    echo "  sudo systemctl restart uvis-backend"
    echo ""
fi
echo ""

# 3. 프론트엔드 빌드 및 배포
echo "=================================================="
echo "🎨 3. 프론트엔드 빌드 및 배포"
echo "=================================================="
cd "$PROJECT_ROOT/frontend"

# 빌드
echo "Frontend 빌드 중..."
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend 빌드 완료${NC}"
else
    echo -e "${RED}❌ Frontend 빌드 실패${NC}"
    exit 1
fi
echo ""

# 4. 빌드 파일 배포
echo "=================================================="
echo "📦 4. 빌드 파일 배포"
echo "=================================================="

# Docker 사용 시
if [ -f "../docker-compose.yml" ]; then
    echo "🐳 Docker 컨테이너로 배포"
    
    # 기존 파일 삭제
    echo "기존 파일 삭제 중..."
    docker exec uvis-frontend rm -rf /usr/share/nginx/html/*
    
    # 새 빌드 파일 복사
    echo "새 빌드 파일 복사 중..."
    docker cp dist/. uvis-frontend:/usr/share/nginx/html/
    
    # 프론트엔드 컨테이너 재시작
    echo "Frontend 컨테이너 재시작 중..."
    docker-compose restart frontend
    
    # 상태 확인
    sleep 2
    if docker-compose ps | grep -q "frontend.*Up"; then
        echo -e "${GREEN}✅ 프론트엔드 배포 완료${NC}"
    else
        echo -e "${RED}❌ 프론트엔드 컨테이너 시작 실패${NC}"
        docker-compose logs --tail=20 frontend
        exit 1
    fi
else
    echo "⚠️  Docker Compose 파일이 없습니다."
    echo "빌드 파일을 수동으로 배포해주세요:"
    echo ""
    echo "  # Nginx 사용 시:"
    echo "  sudo cp -r dist/* /var/www/html/"
    echo "  sudo systemctl reload nginx"
    echo ""
fi
echo ""

# 5. 배포 완료 확인
echo "=================================================="
echo "✅ 배포 완료!"
echo "=================================================="
echo ""
echo "🌐 접속 URL:"
echo "   메인: http://139.150.11.99"
echo "   모니터링: http://139.150.11.99/dispatch/monitoring"
echo ""
echo "📊 API 엔드포인트:"
echo "   GET  http://139.150.11.99/api/v1/dispatch/monitoring/live-stats"
echo "   GET  http://139.150.11.99/api/v1/dispatch/monitoring/agent-performance"
echo "   GET  http://139.150.11.99/api/v1/dispatch/monitoring/top-vehicles"
echo "   WS   ws://139.150.11.99/api/v1/dispatch/monitoring/ws/live-updates"
echo ""
echo "🔍 로그 확인:"
if [ -f "../docker-compose.yml" ]; then
    echo "   docker-compose logs -f backend"
    echo "   docker-compose logs -f frontend"
else
    echo "   tail -f logs/app.log"
    echo "   sudo tail -f /var/log/nginx/access.log"
fi
echo ""
echo "🧪 테스트 명령어:"
echo "   curl http://139.150.11.99/api/v1/dispatch/monitoring/live-stats"
echo ""
echo -e "${GREEN}=================================================="
echo "🎉 배포가 성공적으로 완료되었습니다!"
echo "==================================================${NC}"
echo ""

# 간단한 헬스 체크
echo "🏥 헬스 체크 중..."
sleep 3

# API 헬스 체크
if curl -s http://139.150.11.99/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 백엔드 API 정상${NC}"
else
    echo -e "${YELLOW}⚠️  백엔드 API 응답 없음 (확인 필요)${NC}"
fi

# 프론트엔드 헬스 체크
if curl -s http://139.150.11.99 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 프론트엔드 정상${NC}"
else
    echo -e "${YELLOW}⚠️  프론트엔드 응답 없음 (확인 필요)${NC}"
fi

echo ""
echo "📝 브라우저에서 Ctrl+Shift+R로 새로고침하세요!"
