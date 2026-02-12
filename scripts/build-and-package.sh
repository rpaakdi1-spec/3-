#!/bin/bash

# ============================================
# Frontend Build & Package Script
# 빌드를 샌드박스에서만 수행하고 서버로 전송
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PACKAGE_NAME="frontend-dist-${TIMESTAMP}.tar.gz"

echo "🚀 Frontend Build & Package Script"
echo "=================================="
echo ""

# 1. 프론트엔드 디렉토리로 이동
cd "$FRONTEND_DIR"
echo "📂 Working directory: $FRONTEND_DIR"
echo ""

# 2. 빌드 전 정리
echo "🧹 Cleaning previous build..."
rm -rf dist/
rm -rf node_modules/.vite
echo "✅ Clean complete"
echo ""

# 3. 의존성 설치
echo "📦 Installing dependencies..."
npm install --legacy-peer-deps
echo "✅ Dependencies installed"
echo ""

# 4. 빌드
echo "🔨 Building frontend..."
npm run build
echo "✅ Build complete"
echo ""

# 5. 빌드 결과 확인
if [ ! -f "dist/index.html" ]; then
    echo "❌ Build failed: dist/index.html not found"
    exit 1
fi

echo "✅ Build verification passed"
echo ""

# 6. 압축
echo "📦 Creating package..."
cd "$PROJECT_ROOT"
tar -czf "$PACKAGE_NAME" -C frontend dist/
echo "✅ Package created: $PACKAGE_NAME"
echo ""

# 7. 파일 크기 확인
PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)
echo "📊 Package size: $PACKAGE_SIZE"
echo ""

# 8. Git에 추가 (선택적)
echo "📝 Adding package to Git..."
git add "$PACKAGE_NAME"
echo "✅ Package added to Git staging"
echo ""

# 9. 완료 메시지
echo "=================================="
echo "✅ Build & Package Complete!"
echo "=================================="
echo ""
echo "📦 Package: $PACKAGE_NAME"
echo "📊 Size: $PACKAGE_SIZE"
echo ""
echo "🚀 Next steps (on server):"
echo "   1. git pull origin main"
echo "   2. tar -xzf $PACKAGE_NAME -C frontend/"
echo "   3. docker cp frontend/dist/. uvis-nginx:/usr/share/nginx/html/"
echo "   4. docker-compose restart nginx"
echo ""
