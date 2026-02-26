#!/bin/bash
# Frontend 배포 문제 완전 해결 스크립트

set -e

echo "========================================="
echo "Frontend 배포 문제 완전 해결"
echo "========================================="

cd /root/uvis

echo ""
echo "=== 1. 현재 상태 확인 ==="
echo "로컬 dist 파일 수: $(ls frontend/dist/assets/*.js 2>/dev/null | wc -l)"
echo "컨테이너 파일 수: $(docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l || echo 0)"

echo ""
echo "=== 2. .dockerignore 확인 및 수정 ==="
cat > frontend/.dockerignore << 'DOCKERIGNORE_EOF'
# Node modules will be installed in container
node_modules

# Don't copy .env file to Docker - use .env.production instead
.env
.env.local
.env.development.local
.env.test.local

# Development files
.git
.gitignore
*.md
*.log
build.log

# IDE
.vscode
.idea
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test files
cypress
*.test.*
*.spec.*
__tests__

# Documentation backup
dist-backup-*
DOCKERIGNORE_EOF

echo "✅ .dockerignore 업데이트 완료"

echo ""
echo "=== 3. 개선된 Dockerfile 생성 ==="
cat > frontend/Dockerfile.optimized << 'DOCKERFILE_EOF'
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies first (for better caching)
COPY package*.json ./
RUN npm ci --only=production=false

# Copy source files
COPY . .

# Build for production
ENV NODE_ENV=production
RUN npm run build

# Verify build output
RUN ls -lh /app/dist/assets/*.js | head -5 && \
    echo "Total JS files: $(ls /app/dist/assets/*.js | wc -l)"

# Production stage
FROM nginx:alpine

LABEL maintainer="UVIS Team"
LABEL description="UVIS Logistics Frontend"

# Copy build artifacts
COPY --from=builder /app/dist /usr/share/nginx/html

# Verify files were copied
RUN ls -lh /usr/share/nginx/html/assets/*.js | head -5 && \
    echo "Total JS files in nginx: $(ls /usr/share/nginx/html/assets/*.js | wc -l)"

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE_EOF

echo "✅ 개선된 Dockerfile 생성 완료"

echo ""
echo "=== 4. 방법 선택 ==="
echo "A) Multi-stage build 사용 (권장 - 이미지 크기 작음)"
echo "B) Pre-built dist 직접 복사 (빠름 - 로컬 빌드 사용)"
echo ""
read -p "선택하세요 (A/B): " CHOICE

if [ "$CHOICE" = "B" ] || [ "$CHOICE" = "b" ]; then
    echo ""
    echo "=== 방법 B: Pre-built 파일 직접 복사 ==="
    
    # Simple Dockerfile that copies pre-built dist
    cat > frontend/Dockerfile << 'SIMPLE_DOCKERFILE_EOF'
FROM nginx:alpine

LABEL maintainer="UVIS Team"
LABEL description="UVIS Logistics Frontend"

# Copy pre-built files directly
COPY dist /usr/share/nginx/html

# Verify files
RUN ls -lh /usr/share/nginx/html/assets/*.js | head -5 || echo "No JS files found!"

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
SIMPLE_DOCKERFILE_EOF
    
    echo "✅ 간단한 Dockerfile 생성 완료 (pre-built 사용)"
    
else
    echo ""
    echo "=== 방법 A: Multi-stage build 사용 ==="
    cp frontend/Dockerfile.optimized frontend/Dockerfile
    echo "✅ 개선된 Dockerfile로 교체 완료"
fi

echo ""
echo "=== 5. 기존 이미지 및 캐시 완전 삭제 ==="
docker rmi $(docker images -q uvis-frontend) 2>/dev/null || echo "기존 이미지 없음"
docker builder prune -af
echo "✅ 캐시 정리 완료"

echo ""
echo "=== 6. 새 이미지 빌드 (빌드 로그 확인) ==="
docker-compose build frontend --no-cache --progress=plain 2>&1 | tee /tmp/frontend_build.log

echo ""
echo "=== 7. 빌드된 이미지에서 파일 확인 ==="
TEMP_CONTAINER=$(docker create uvis-frontend)
FILE_COUNT=$(docker run --rm --entrypoint sh uvis-frontend -c "ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l" || echo 0)
echo "빌드된 이미지 내 JS 파일 수: $FILE_COUNT"

if [ "$FILE_COUNT" -lt 80 ]; then
    echo "❌ 빌드 실패! 로그 확인:"
    echo ""
    grep -i "error" /tmp/frontend_build.log | tail -20
    echo ""
    echo "전체 로그: /tmp/frontend_build.log"
    exit 1
fi

echo ""
echo "=== 8. 컨테이너 재시작 ==="
docker-compose stop frontend
docker-compose rm -f frontend
docker-compose up -d frontend

echo ""
echo "=== 9. 최종 확인 (10초 대기) ==="
sleep 10

CONTAINER_FILES=$(docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l)
echo "컨테이너 내 JS 파일 수: $CONTAINER_FILES"

if [ "$CONTAINER_FILES" -gt 80 ]; then
    echo ""
    echo "✅✅✅ 성공! ✅✅✅"
    echo ""
    echo "파일 샘플:"
    docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/*.js | grep -i dispatch | head -3
    echo ""
    echo "🌐 브라우저에서 테스트:"
    echo "   1. Ctrl+Shift+Delete로 모든 캐시 삭제"
    echo "   2. 또는 시크릿 모드 사용"
    echo "   3. http://139.150.11.99 접속"
    echo "   4. 로그인: admin / admin123"
    echo "   5. Dispatch Rules 페이지 확인"
    echo ""
    echo "✅ 문제 완전 해결!"
else
    echo ""
    echo "❌ 여전히 실패"
    echo ""
    echo "추가 디버깅:"
    echo "1. 빌드 로그 확인: cat /tmp/frontend_build.log | less"
    echo "2. 이미지 레이어 확인: docker history uvis-frontend"
    echo "3. 수동 빌드 테스트:"
    echo "   cd /root/uvis/frontend"
    echo "   docker build -t test-frontend --progress=plain ."
fi
