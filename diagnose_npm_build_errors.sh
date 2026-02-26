#!/bin/bash
# NPM 빌드 에러 진단 스크립트

set -e

echo "========================================="
echo "NPM 빌드 에러 진단"
echo "========================================="

cd /root/uvis/frontend

echo ""
echo "=== 1. 서버 리소스 확인 ==="
echo "메모리:"
free -h
echo ""
echo "디스크:"
df -h /root
echo ""
echo "CPU:"
nproc
echo ""

echo "=== 2. Node.js 환경 확인 ==="
echo "Node 버전: $(node --version 2>/dev/null || echo 'Node.js not installed')"
echo "NPM 버전: $(npm --version 2>/dev/null || echo 'NPM not installed')"
echo ""

echo "=== 3. 로컬 빌드 테스트 (에러 확인) ==="
echo "package.json 확인:"
if [ -f package.json ]; then
    echo "✅ package.json 존재"
    echo "Scripts:"
    cat package.json | grep -A10 '"scripts"' | head -15
else
    echo "❌ package.json 없음"
    exit 1
fi

echo ""
echo "=== 4. Docker 빌드 시뮬레이션 (에러 로그 수집) ==="
echo "Docker 빌드 테스트 중... (5-10분 소요)"
echo ""

# Create a test Dockerfile with verbose logging
cat > Dockerfile.test << 'DOCKERFILE_EOF'
FROM node:18-alpine AS builder

WORKDIR /app

# Show environment
RUN echo "=== Environment ===" && \
    node --version && \
    npm --version && \
    df -h && \
    free -m 2>/dev/null || true

# Copy package files
COPY package*.json ./

# Install with verbose logging
RUN echo "=== Installing dependencies ===" && \
    npm ci --loglevel=verbose 2>&1 | tee /tmp/npm-install.log || \
    (echo "NPM INSTALL FAILED!" && cat /tmp/npm-install.log && exit 1)

# Copy source
COPY . .

# Build with verbose logging
RUN echo "=== Building application ===" && \
    npm run build 2>&1 | tee /tmp/npm-build.log || \
    (echo "NPM BUILD FAILED!" && cat /tmp/npm-build.log && exit 1)

# Verify output
RUN echo "=== Build output ===" && \
    ls -lh /app/dist/ && \
    ls -lh /app/dist/assets/*.js | wc -l && \
    echo "Total JS files: $(ls /app/dist/assets/*.js 2>/dev/null | wc -l)"

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
RUN ls -lh /usr/share/nginx/html/assets/*.js | wc -l
DOCKERFILE_EOF

echo "테스트 Dockerfile 생성 완료"
echo ""

# Build with the test Dockerfile
echo "빌드 시작..."
docker build -f Dockerfile.test -t frontend-test --progress=plain . 2>&1 | tee /tmp/docker_build_diagnosis.log

BUILD_EXIT_CODE=$?

echo ""
echo "========================================="
echo "=== 5. 진단 결과 분석 ==="
echo "========================================="
echo ""

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✅ 빌드 성공!"
    echo ""
    echo "이미지 내 파일 수:"
    docker run --rm --entrypoint sh frontend-test -c "ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l"
    echo ""
    echo "샘플 파일:"
    docker run --rm --entrypoint sh frontend-test -c "ls -lh /usr/share/nginx/html/assets/*.js | head -5"
    echo ""
    echo "✅ 문제 없음! 기존 이미지를 이것으로 교체하세요:"
    echo "   docker tag frontend-test uvis-frontend"
    echo "   docker-compose up -d frontend"
else
    echo "❌ 빌드 실패!"
    echo ""
    echo "=== 에러 분석 ==="
    echo ""
    
    # Check for common errors
    if grep -q "ENOSPC\|no space left" /tmp/docker_build_diagnosis.log; then
        echo "🔴 디스크 공간 부족!"
        echo "해결: docker system prune -af --volumes"
    fi
    
    if grep -q "JavaScript heap out of memory\|FATAL ERROR" /tmp/docker_build_diagnosis.log; then
        echo "🔴 메모리 부족!"
        echo "해결: NODE_OPTIONS='--max-old-space-size=4096' npm run build"
    fi
    
    if grep -q "Cannot find module\|Error: Cannot find" /tmp/docker_build_diagnosis.log; then
        echo "🔴 의존성 설치 실패!"
        echo "해결: package-lock.json 확인 및 npm install 재실행"
    fi
    
    if grep -q "ECONNREFUSED\|ETIMEDOUT\|network" /tmp/docker_build_diagnosis.log; then
        echo "🔴 네트워크 문제!"
        echo "해결: npm registry 확인 또는 재시도"
    fi
    
    if grep -q "peer dep\|ERESOLVE" /tmp/docker_build_diagnosis.log; then
        echo "🔴 의존성 충돌!"
        echo "해결: npm install --legacy-peer-deps"
    fi
    
    echo ""
    echo "=== 상세 에러 로그 (최근 50줄) ==="
    tail -50 /tmp/docker_build_diagnosis.log | grep -i "error\|fail\|fatal" || echo "구체적인 에러 메시지 없음"
    echo ""
    echo "전체 로그: /tmp/docker_build_diagnosis.log"
fi

echo ""
echo "========================================="
echo "=== 6. 추천 해결 방법 ==="
echo "========================================="
echo ""

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "A) 현재 테스트 이미지로 교체 (즉시 해결):"
    echo "   docker tag frontend-test uvis-frontend:latest"
    echo "   docker-compose stop frontend && docker-compose rm -f frontend"
    echo "   docker-compose up -d frontend"
    echo ""
    echo "B) Dockerfile 교체 (향후 재빌드용):"
    echo "   cp Dockerfile.test Dockerfile"
    echo "   docker-compose build frontend --no-cache"
    echo "   docker-compose up -d frontend"
else
    echo "A) 로컬에서 미리 빌드한 dist 사용 (가장 빠름):"
    echo "   cat > Dockerfile.simple << 'EOF'"
    echo "   FROM nginx:alpine"
    echo "   COPY dist /usr/share/nginx/html"
    echo "   COPY nginx.conf /etc/nginx/nginx.conf"
    echo "   EXPOSE 80"
    echo "   CMD [\"nginx\", \"-g\", \"daemon off;\"]"
    echo "   EOF"
    echo "   docker build -f Dockerfile.simple -t uvis-frontend ."
    echo "   docker-compose up -d frontend"
    echo ""
    echo "B) 메모리 제한 완화 (메모리 부족인 경우):"
    echo "   cat > Dockerfile.memory << 'EOF'"
    echo "   FROM node:18-alpine AS builder"
    echo "   WORKDIR /app"
    echo "   ENV NODE_OPTIONS='--max-old-space-size=4096'"
    echo "   COPY package*.json ./"
    echo "   RUN npm ci"
    echo "   COPY . ."
    echo "   RUN npm run build"
    echo "   FROM nginx:alpine"
    echo "   COPY --from=builder /app/dist /usr/share/nginx/html"
    echo "   EOF"
    echo "   docker build -f Dockerfile.memory -t uvis-frontend --no-cache ."
    echo ""
    echo "C) 전체 로그 확인 후 수동 수정:"
    echo "   less /tmp/docker_build_diagnosis.log"
    echo "   # 구체적인 에러 확인 후 조치"
fi

echo ""
echo "진단 완료!"
