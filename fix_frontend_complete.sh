#!/bin/bash
# 프론트엔드 배포 완전 해결 - 3가지 방법 제공

set -e

echo "========================================="
echo "프론트엔드 배포 완전 해결"
echo "========================================="

cd /root/uvis

echo ""
echo "=== 현재 상태 ==="
LOCAL_COUNT=$(ls frontend/dist/assets/*.js 2>/dev/null | wc -l)
CONTAINER_COUNT=$(docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l || echo 0)

echo "로컬 빌드 파일: $LOCAL_COUNT 개"
echo "컨테이너 파일: $CONTAINER_COUNT 개"
echo ""

if [ "$CONTAINER_COUNT" -lt 80 ]; then
    echo "❌ 문제 확인됨 - 해결 진행"
else
    echo "✅ 파일이 정상입니다"
    exit 0
fi

echo ""
echo "========================================="
echo "해결 방법 선택"
echo "========================================="
echo ""
echo "1) 빠른 수정 (1분) - 로컬 빌드 파일 직접 복사"
echo "   → 장점: 즉시 해결, 실패 없음"
echo "   → 단점: 향후 재빌드 시 다시 설정 필요"
echo ""
echo "2) 표준 수정 (3-5분) - Multi-stage build 개선"
echo "   → 장점: 정석적인 방법, CI/CD 호환"
echo "   → 단점: 서버 리소스 필요, 실패 가능성 있음"
echo ""
echo "3) 진단 모드 (5-10분) - 에러 원인 상세 분석"
echo "   → 장점: 근본 원인 파악, 로그 저장"
echo "   → 단점: 시간 소요"
echo ""
read -p "선택하세요 (1/2/3): " CHOICE

case $CHOICE in
    1)
        echo ""
        echo "========================================="
        echo "방법 1: 빠른 수정 (로컬 빌드 직접 사용)"
        echo "========================================="
        echo ""
        
        # Backup current Dockerfile
        cp frontend/Dockerfile frontend/Dockerfile.backup.$(date +%Y%m%d_%H%M%S)
        
        # Create simple Dockerfile
        cat > frontend/Dockerfile << 'SIMPLE_EOF'
FROM nginx:alpine

LABEL maintainer="UVIS Team"
LABEL description="UVIS Logistics Frontend"

# Copy pre-built dist directory
COPY dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Verify files are present
RUN echo "Checking files..." && \
    ls -lh /usr/share/nginx/html/assets/*.js | head -5 && \
    JS_COUNT=$(ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l) && \
    echo "Total JS files: $JS_COUNT" && \
    if [ "$JS_COUNT" -lt 50 ]; then \
        echo "ERROR: Not enough JS files!" && exit 1; \
    fi

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
SIMPLE_EOF
        
        echo "✅ 간단한 Dockerfile 생성"
        
        # Remove old images
        docker rmi $(docker images -q uvis-frontend) 2>/dev/null || true
        
        echo ""
        echo "빌드 중..."
        docker build -t uvis-frontend frontend/ --progress=plain 2>&1 | tee /tmp/frontend_build_simple.log
        
        if [ $? -ne 0 ]; then
            echo "❌ 빌드 실패!"
            echo "로그: /tmp/frontend_build_simple.log"
            exit 1
        fi
        
        echo ""
        echo "컨테이너 재시작..."
        docker-compose stop frontend
        docker-compose rm -f frontend
        docker-compose up -d frontend
        
        sleep 10
        
        FINAL_COUNT=$(docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l)
        echo ""
        echo "최종 파일 수: $FINAL_COUNT"
        
        if [ "$FINAL_COUNT" -gt 80 ]; then
            echo ""
            echo "✅✅✅ 성공! ✅✅✅"
            echo ""
            echo "샘플 파일:"
            docker exec uvis-frontend ls -lh /usr/share/nginx/html/assets/*.js | grep -i dispatch | head -3
            echo ""
            echo "🌐 브라우저 테스트:"
            echo "   1. Ctrl+Shift+Delete로 캐시 삭제"
            echo "   2. http://139.150.11.99"
            echo "   3. 로그인: admin / admin123"
        else
            echo "❌ 실패 - 진단 모드(3번)를 실행하세요"
        fi
        ;;
        
    2)
        echo ""
        echo "========================================="
        echo "방법 2: 표준 Multi-stage Build"
        echo "========================================="
        echo ""
        
        # Update .dockerignore
        cat > frontend/.dockerignore << 'IGNORE_EOF'
node_modules
.env
.env.local
.env.development.local
.env.test.local
.git
.gitignore
*.md
*.log
.vscode
.idea
*.swp
.DS_Store
cypress
__tests__
dist-backup-*
IGNORE_EOF
        
        echo "✅ .dockerignore 업데이트"
        
        # Create optimized Dockerfile
        cp frontend/Dockerfile frontend/Dockerfile.backup.$(date +%Y%m%d_%H%M%S)
        
        cat > frontend/Dockerfile << 'MULTI_EOF'
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies with better error handling
COPY package*.json ./

RUN echo "=== Installing dependencies ===" && \
    npm ci --prefer-offline --no-audit 2>&1 | tee /tmp/npm-install.log || \
    (echo "NPM Install failed!" && cat /tmp/npm-install.log && exit 1)

# Copy source files
COPY . .

# Build with memory optimization
ENV NODE_ENV=production
ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN echo "=== Building application ===" && \
    npm run build 2>&1 | tee /tmp/npm-build.log || \
    (echo "Build failed!" && cat /tmp/npm-build.log && exit 1)

# Verify build output
RUN echo "=== Verifying build ===" && \
    ls -lh /app/dist/assets/*.js | head -5 && \
    JS_COUNT=$(ls /app/dist/assets/*.js 2>/dev/null | wc -l) && \
    echo "Built JS files: $JS_COUNT" && \
    if [ "$JS_COUNT" -lt 50 ]; then \
        echo "ERROR: Build produced too few files!" && exit 1; \
    fi

# Production stage
FROM nginx:alpine

LABEL maintainer="UVIS Team"

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Final verification
RUN ls -lh /usr/share/nginx/html/assets/*.js | head -5 && \
    echo "Total files: $(ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l)"

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
MULTI_EOF
        
        echo "✅ 최적화된 Dockerfile 생성"
        
        # Clean up
        docker rmi $(docker images -q uvis-frontend) 2>/dev/null || true
        docker builder prune -af
        
        echo ""
        echo "빌드 중... (3-5분 소요)"
        docker build -t uvis-frontend frontend/ --no-cache --progress=plain 2>&1 | tee /tmp/frontend_build_multi.log
        
        BUILD_CODE=$?
        
        if [ $BUILD_CODE -ne 0 ]; then
            echo ""
            echo "❌ 빌드 실패!"
            echo ""
            echo "에러 분석:"
            grep -i "error\|fail\|fatal" /tmp/frontend_build_multi.log | tail -20
            echo ""
            echo "전체 로그: /tmp/frontend_build_multi.log"
            echo ""
            echo "권장: 방법 1(빠른 수정)을 선택하세요"
            exit 1
        fi
        
        echo ""
        echo "컨테이너 재시작..."
        docker-compose stop frontend
        docker-compose rm -f frontend
        docker-compose up -d frontend
        
        sleep 10
        
        FINAL_COUNT=$(docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l)
        echo ""
        echo "최종 파일 수: $FINAL_COUNT"
        
        if [ "$FINAL_COUNT" -gt 80 ]; then
            echo ""
            echo "✅✅✅ 성공! ✅✅✅"
        else
            echo "❌ 실패 - 방법 1을 시도하세요"
        fi
        ;;
        
    3)
        echo ""
        echo "========================================="
        echo "방법 3: 진단 모드"
        echo "========================================="
        echo ""
        
        echo "서버 리소스:"
        echo "메모리: $(free -h | grep Mem | awk '{print $2 " total, " $3 " used, " $4 " available"}')"
        echo "디스크: $(df -h /root | tail -1 | awk '{print $2 " total, " $3 " used, " $4 " available"}')"
        echo "CPU: $(nproc) cores"
        echo ""
        
        # Create diagnostic Dockerfile
        cat > frontend/Dockerfile.diag << 'DIAG_EOF'
FROM node:18-alpine AS builder

WORKDIR /app

RUN echo "=== Environment Info ===" && \
    node --version && \
    npm --version && \
    df -h && \
    free -m 2>/dev/null || true

COPY package*.json ./

RUN echo "=== NPM Install (verbose) ===" && \
    npm ci --loglevel=verbose 2>&1 | tee /tmp/npm-install.log

COPY . .

RUN echo "=== NPM Build (verbose) ===" && \
    NODE_OPTIONS="--max-old-space-size=4096" npm run build 2>&1 | tee /tmp/npm-build.log

RUN echo "=== Build Output ===" && \
    find /app/dist -name "*.js" -type f | wc -l && \
    ls -lh /app/dist/assets/*.js | head -10

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
RUN ls -lh /usr/share/nginx/html/assets/*.js | wc -l
DIAG_EOF
        
        echo "진단 빌드 시작... (5-10분 소요)"
        docker build -f frontend/Dockerfile.diag -t frontend-diag --progress=plain . 2>&1 | tee /tmp/frontend_diagnostic.log
        
        DIAG_CODE=$?
        
        echo ""
        echo "========================================="
        echo "진단 결과"
        echo "========================================="
        echo ""
        
        if [ $DIAG_CODE -eq 0 ]; then
            echo "✅ 빌드 성공!"
            docker run --rm --entrypoint sh frontend-diag -c "ls /usr/share/nginx/html/assets/*.js | wc -l"
            echo ""
            echo "→ 빌드는 성공하지만 기존 Dockerfile에 문제가 있습니다"
            echo "→ 방법 2를 다시 시도하거나 방법 1을 사용하세요"
        else
            echo "❌ 빌드 실패 - 에러 분석:"
            echo ""
            
            if grep -q "heap out of memory" /tmp/frontend_diagnostic.log; then
                echo "🔴 메모리 부족 (JavaScript heap out of memory)"
                echo "   해결: 서버 메모리 증설 또는 방법 1 사용"
            fi
            
            if grep -q "ENOSPC" /tmp/frontend_diagnostic.log; then
                echo "🔴 디스크 공간 부족"
                echo "   해결: docker system prune -af --volumes"
            fi
            
            if grep -q "Cannot find module" /tmp/frontend_diagnostic.log; then
                echo "🔴 의존성 문제"
                echo "   해결: package-lock.json 확인"
            fi
            
            if grep -q "ECONNREFUSED\|ETIMEDOUT" /tmp/frontend_diagnostic.log; then
                echo "🔴 네트워크 문제"
                echo "   해결: npm registry 접근 확인"
            fi
            
            echo ""
            echo "상세 로그: /tmp/frontend_diagnostic.log"
            echo ""
            echo "→ 권장: 방법 1(빠른 수정) 사용"
        fi
        ;;
        
    *)
        echo "잘못된 선택입니다"
        exit 1
        ;;
esac

echo ""
echo "완료!"
