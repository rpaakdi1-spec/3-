#!/bin/bash
# 배포 방식 완전 진단 스크립트

echo "========================================="
echo "🔍 UVIS 배포 방식 완전 진단"
echo "========================================="
echo ""

cd /root/uvis

# 1. 현재 사용 중인 docker-compose 파일들
echo "=== 1. Docker Compose 파일 구조 ==="
echo "발견된 docker-compose 파일들:"
ls -lh docker-compose*.yml
echo ""

echo "기본 docker-compose.yml의 frontend 서비스:"
cat docker-compose.yml | grep -A30 "frontend:"
echo ""

if [ -f docker-compose.override.yml ]; then
    echo "✅ docker-compose.override.yml 존재 (이것이 볼륨 마운트 설정):"
    cat docker-compose.override.yml
else
    echo "❌ docker-compose.override.yml 없음"
fi
echo ""

# 2. 실제 컨테이너 마운트 상태
echo "=== 2. 실제 컨테이너 마운트 상태 ==="
docker inspect uvis-frontend --format='{{json .Mounts}}' | python3 -m json.tool
echo ""

# 3. 컨테이너가 사용 중인 이미지
echo "=== 3. 컨테이너가 사용하는 이미지 ==="
FRONTEND_IMAGE_ID=$(docker inspect uvis-frontend --format='{{.Image}}')
echo "이미지 ID: $FRONTEND_IMAGE_ID"
echo ""
echo "이미지 상세 정보:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" | grep -E "REPOSITORY|uvis-frontend"
echo ""

# 4. 이미지 내부 파일 vs 실행 중 컨테이너 파일
echo "=== 4. 이미지 내부 파일 수 ==="
echo "이미지를 임시 컨테이너로 실행:"
docker run --rm uvis-frontend sh -c "find /usr/share/nginx/html/assets -name '*.js' -type f | wc -l" 2>/dev/null || echo "0"
echo ""

echo "실행 중인 컨테이너의 파일 수:"
docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.js" -type f 2>/dev/null | wc -l
echo ""

# 5. Dockerfile 확인
echo "=== 5. 현재 Dockerfile 내용 ==="
if [ -f frontend/Dockerfile ]; then
    echo "Dockerfile 존재:"
    cat frontend/Dockerfile
else
    echo "❌ Dockerfile 없음"
fi
echo ""

# 6. .dockerignore 확인
echo "=== 6. .dockerignore 설정 ==="
if [ -f frontend/.dockerignore ]; then
    echo ".dockerignore 내용:"
    cat frontend/.dockerignore
    echo ""
    if grep -q "^dist$" frontend/.dockerignore; then
        echo "🔴 경고: .dockerignore에 'dist' 폴더가 제외되어 있음!"
    else
        echo "✅ dist 폴더는 제외되지 않음"
    fi
else
    echo "❌ .dockerignore 없음"
fi
echo ""

# 7. nginx 이미지의 기본 entrypoint
echo "=== 7. Nginx 기본 Entrypoint 확인 ==="
echo "nginx:alpine 이미지의 기본 entrypoint:"
docker inspect nginx:alpine --format='{{.Config.Entrypoint}}' 2>/dev/null
echo ""
echo "현재 uvis-frontend의 entrypoint:"
docker inspect uvis-frontend --format='{{.Config.Entrypoint}}'
echo ""

# 8. 컨테이너 시작 시 실행되는 스크립트들
echo "=== 8. 컨테이너 시작 시 실행 스크립트 ==="
echo "/docker-entrypoint.d/ 디렉토리 내용:"
docker exec uvis-frontend ls -la /docker-entrypoint.d/ 2>/dev/null
echo ""

# 9. 호스트의 dist 폴더 상태
echo "=== 9. 호스트 dist 폴더 상태 ==="
echo "frontend/dist 폴더 크기:"
du -sh frontend/dist
echo ""
echo "JS 파일 수:"
find frontend/dist/assets -name "*.js" -type f 2>/dev/null | wc -l
echo ""
echo "샘플 파일:"
ls -lh frontend/dist/assets/*.js 2>/dev/null | head -5
echo ""

# 10. 빌드 히스토리 확인
echo "=== 10. Docker 이미지 빌드 히스토리 ==="
echo "최근 빌드된 uvis-frontend 이미지들:"
docker images uvis-frontend --format "table {{.ID}}\t{{.CreatedAt}}\t{{.Size}}"
echo ""

# 11. 볼륨 마운트 우선순위 테스트
echo "=== 11. 파일 소스 확인 (이미지 vs 마운트) ==="
echo "컨테이너의 /usr/share/nginx/html이 볼륨인지 확인:"
docker exec uvis-frontend mount | grep "/usr/share/nginx/html" || echo "볼륨 마운트 없음 (이미지 파일 사용 중)"
echo ""

# 12. 문제 진단
echo "========================================="
echo "=== 🎯 진단 결과 및 근본 원인 분석 ==="
echo "========================================="
echo ""

# 볼륨 마운트 여부 확인
HAS_OVERRIDE=$([ -f docker-compose.override.yml ] && echo "yes" || echo "no")
MOUNT_COUNT=$(docker inspect uvis-frontend --format='{{json .Mounts}}' | grep -c "frontend/dist" 2>/dev/null || echo "0")
IMAGE_FILES=$(docker run --rm uvis-frontend sh -c "find /usr/share/nginx/html/assets -name '*.js' -type f | wc -l" 2>/dev/null || echo "0")
CONTAINER_FILES=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.js" -type f 2>/dev/null | wc -l)

echo "검사 결과:"
echo "  - docker-compose.override.yml 존재: $HAS_OVERRIDE"
echo "  - 볼륨 마운트 수: $MOUNT_COUNT"
echo "  - 이미지 내부 파일: $IMAGE_FILES 개"
echo "  - 실행 중 컨테이너 파일: $CONTAINER_FILES 개"
echo ""

if [ "$MOUNT_COUNT" -gt 0 ]; then
    echo "✅ 현재 배포 방식: 볼륨 마운트"
    echo ""
    echo "장점:"
    echo "  - 호스트 파일 직접 사용 (파일 누락 없음)"
    echo "  - 빠른 업데이트 (빌드 후 restart만)"
    echo ""
    echo "단점:"
    echo "  - 서버 의존성 (호스트에 dist 필요)"
    echo "  - 이미지 이식성 감소"
    echo ""
    if [ "$CONTAINER_FILES" -gt 80 ]; then
        echo "🎉 상태: 정상 작동 중!"
    else
        echo "🔴 문제: 볼륨 마운트 설정되었지만 파일이 없음"
        echo "  → 호스트의 frontend/dist 폴더 확인 필요"
    fi
else
    echo "❌ 현재 배포 방식: Docker 이미지 (볼륨 마운트 없음)"
    echo ""
    echo "문제점:"
    echo "  - nginx:alpine의 기본 entrypoint가 파일 삭제"
    echo "  - COPY한 파일이 컨테이너 시작 시 사라짐"
    echo ""
    if [ "$IMAGE_FILES" -gt 80 ]; then
        echo "  → 이미지에는 파일이 있음 ($IMAGE_FILES 개)"
        echo "  → 하지만 컨테이너 실행 시 사라짐 ($CONTAINER_FILES 개)"
        echo ""
        echo "🔴 근본 원인: nginx:alpine의 /docker-entrypoint.sh"
        echo "   이 스크립트가 /usr/share/nginx/html을 초기화함"
    else
        echo "  → 이미지에도 파일이 없음 ($IMAGE_FILES 개)"
        echo ""
        echo "🔴 근본 원인: 빌드 단계에서 파일이 COPY되지 않음"
        echo "   가능한 이유:"
        echo "   1. .dockerignore에 dist 폴더 제외"
        echo "   2. 빌드 컨텍스트에 dist 폴더 없음"
        echo "   3. Dockerfile에 COPY 명령 없음"
    fi
fi

echo ""
echo "========================================="
echo "=== 💡 권장 해결 방법 ==="
echo "========================================="
echo ""

if [ "$MOUNT_COUNT" -gt 0 ]; then
    echo "현재 볼륨 마운트 방식 사용 중 - 이것이 최선입니다!"
    echo ""
    echo "유지 관리 방법:"
    echo "  1. 코드 수정"
    echo "  2. npm run build"
    echo "  3. docker-compose restart frontend"
    echo ""
    if [ "$CONTAINER_FILES" -lt 80 ]; then
        echo "🔧 즉시 수정:"
        echo "  cd /root/uvis/frontend && npm run build"
        echo "  docker-compose restart frontend"
    fi
else
    echo "🔄 볼륨 마운트 방식으로 전환 필요!"
    echo ""
    echo "1. docker-compose.override.yml 생성:"
    echo "   cat > docker-compose.override.yml << 'EOF'"
    echo "   version: '3.8'"
    echo "   services:"
    echo "     frontend:"
    echo "       volumes:"
    echo "         - ./frontend/dist:/usr/share/nginx/html:ro"
    echo "         - ./frontend/nginx.conf:/etc/nginx/nginx.conf:ro"
    echo "   EOF"
    echo ""
    echo "2. 재시작:"
    echo "   docker-compose down frontend"
    echo "   docker-compose up -d frontend"
fi

echo ""
echo "진단 완료!"
