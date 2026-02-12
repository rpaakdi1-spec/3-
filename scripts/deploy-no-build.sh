#!/bin/bash

# ============================================
# Server Deployment Script (No Build)
# 서버에서 빌드 없이 배포만 수행
# ============================================

set -e

echo "🚀 Server Deployment Script (No Build)"
echo "======================================"
echo ""

# 변수 설정
PROJECT_ROOT="/root/uvis"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# 1. 현재 위치 확인
if [ ! -d "$PROJECT_ROOT" ]; then
    echo "❌ Error: Project directory not found: $PROJECT_ROOT"
    exit 1
fi

cd "$PROJECT_ROOT"
echo "📂 Working directory: $PROJECT_ROOT"
echo ""

# 2. Git 동기화
echo "🔄 Pulling latest code from GitHub..."
git pull origin main
echo "✅ Code synchronized"
echo ""

# 3. 최신 패키지 찾기
echo "🔍 Finding latest frontend package..."
LATEST_PACKAGE=$(ls -t frontend-dist-*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_PACKAGE" ]; then
    echo "❌ Error: No frontend package found (frontend-dist-*.tar.gz)"
    echo "   Please run build-and-package.sh in sandbox first!"
    exit 1
fi

echo "📦 Found package: $LATEST_PACKAGE"
PACKAGE_SIZE=$(du -h "$LATEST_PACKAGE" | cut -f1)
echo "📊 Package size: $PACKAGE_SIZE"
echo ""

# 4. 기존 dist 백업
if [ -d "$FRONTEND_DIR/dist" ]; then
    echo "💾 Backing up current dist..."
    BACKUP_NAME="dist-backup-$(date +%Y%m%d-%H%M%S)"
    mv "$FRONTEND_DIR/dist" "$FRONTEND_DIR/$BACKUP_NAME"
    echo "✅ Backup created: $BACKUP_NAME"
    echo ""
fi

# 5. 새 dist 압축 해제
echo "📦 Extracting package..."
tar -xzf "$LATEST_PACKAGE" -C "$FRONTEND_DIR/"
echo "✅ Package extracted"
echo ""

# 6. dist 확인
if [ ! -f "$FRONTEND_DIR/dist/index.html" ]; then
    echo "❌ Error: dist/index.html not found after extraction"
    exit 1
fi

echo "✅ Dist verification passed"
echo ""

# 7. Docker 컨테이너 확인
echo "🐳 Checking Docker containers..."
if ! docker-compose ps | grep -q "uvis-nginx.*Up"; then
    echo "⚠️  Warning: nginx container not running"
    echo "   Starting containers..."
    docker-compose up -d nginx
    sleep 5
fi

echo "✅ Docker containers ready"
echo ""

# 8. nginx에 dist 복사
echo "📤 Copying dist to nginx container..."
docker cp "$FRONTEND_DIR/dist/." uvis-nginx:/usr/share/nginx/html/
echo "✅ Dist copied to nginx"
echo ""

# 9. nginx 재시작
echo "🔄 Restarting nginx..."
docker-compose restart nginx
echo "✅ Nginx restarted"
echo ""

# 10. 대기
echo "⏳ Waiting for nginx to initialize..."
sleep 5
echo ""

# 11. 상태 확인
echo "🔍 Verifying deployment..."
echo ""

# HTTP 응답 확인
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ HTTP Status: $HTTP_STATUS OK"
else
    echo "⚠️  HTTP Status: $HTTP_STATUS"
fi

# API 확인
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/simulations/templates)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ API Status: $API_STATUS OK"
else
    echo "⚠️  API Status: $API_STATUS"
fi

echo ""

# 12. 컨테이너 상태
echo "📊 Container status:"
docker-compose ps | grep -E "uvis-(nginx|frontend|backend)"
echo ""

# 13. 완료 메시지
echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "🌐 Access your application:"
echo "   http://localhost/"
echo "   http://139.150.11.99/"
echo ""
echo "📋 Next steps:"
echo "   1. Clear browser cache (Ctrl+Shift+Delete)"
echo "   2. Open http://139.150.11.99/"
echo "   3. Check '규칙 시뮬레이션' menu"
echo "   4. Verify 6 templates are displayed"
echo ""
