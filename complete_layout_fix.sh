#!/bin/bash
# UVIS Layout 완전 수정 - 원클릭 실행 스크립트
# 이 스크립트는 Layout 제거부터 배포까지 전체 과정을 자동화합니다

set -e

echo "=================================================="
echo "🚀 UVIS Layout 완전 수정 시작"
echo "=================================================="
echo ""
echo "이 스크립트는 다음을 수행합니다:"
echo "1. 모든 페이지에서 Layout 제거"
echo "2. 검증"
echo "3. 프론트엔드 빌드"
echo "4. Docker 이미지 재빌드"
echo "5. 컨테이너 재시작"
echo ""
read -p "계속하시겠습니까? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "취소되었습니다."
    exit 1
fi

SCRIPT_DIR="/root/uvis"
cd "$SCRIPT_DIR"

# 1단계: Layout 제거
echo ""
echo "=================================================="
echo "📝 1단계: Layout 제거"
echo "=================================================="
if [ -f "./batch_remove_layout.sh" ]; then
    ./batch_remove_layout.sh
else
    echo "❌ batch_remove_layout.sh를 찾을 수 없습니다"
    echo "   파일 위치 확인: /root/uvis/batch_remove_layout.sh"
    exit 1
fi

# 2단계: 검증
echo ""
echo "=================================================="
echo "🔍 2단계: Layout 제거 검증"
echo "=================================================="
if [ -f "./verify_layout_fix.sh" ]; then
    if ./verify_layout_fix.sh; then
        echo "✅ 검증 통과"
    else
        echo "❌ 검증 실패"
        echo ""
        read -p "계속하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  verify_layout_fix.sh를 찾을 수 없습니다 (건너뜀)"
fi

# 3단계: 프론트엔드 빌드
echo ""
echo "=================================================="
echo "🔨 3단계: 프론트엔드 빌드"
echo "=================================================="
cd "$SCRIPT_DIR/frontend"

echo "▶ dist/ 디렉토리 삭제..."
rm -rf dist/

echo "▶ npm run build 실행..."
BUILD_START=$(date +%s)
if npm run build; then
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    echo "✅ 빌드 성공 (소요 시간: ${BUILD_TIME}초)"
else
    echo "❌ 빌드 실패"
    echo ""
    echo "문제 해결:"
    echo "1. 로그 확인"
    echo "2. 백업에서 복구: cd /root/uvis/frontend/src/pages && cp layout_removal_backup_*/*.tsx ./"
    echo "3. 다시 시도"
    exit 1
fi

# 4단계: Docker 이미지 재빌드
echo ""
echo "=================================================="
echo "🐳 4단계: Docker 이미지 재빌드"
echo "=================================================="
cd "$SCRIPT_DIR"

echo "▶ docker-compose build --no-cache frontend 실행..."
DOCKER_BUILD_START=$(date +%s)
if docker-compose build --no-cache frontend; then
    DOCKER_BUILD_END=$(date +%s)
    DOCKER_BUILD_TIME=$((DOCKER_BUILD_END - DOCKER_BUILD_START))
    echo "✅ Docker 이미지 빌드 성공 (소요 시간: ${DOCKER_BUILD_TIME}초)"
else
    echo "❌ Docker 이미지 빌드 실패"
    exit 1
fi

# 5단계: 컨테이너 재시작
echo ""
echo "=================================================="
echo "🔄 5단계: 컨테이너 재시작"
echo "=================================================="

echo "▶ docker-compose up -d frontend 실행..."
if docker-compose up -d frontend; then
    echo "✅ 컨테이너 시작됨"
else
    echo "❌ 컨테이너 시작 실패"
    exit 1
fi

echo "▶ 컨테이너 안정화 대기 (10초)..."
sleep 10

echo "▶ 컨테이너 상태 확인..."
if docker-compose ps | grep -q "frontend.*Up"; then
    echo "✅ 컨테이너 정상 실행 중"
else
    echo "⚠️  컨테이너 상태 확인 필요"
    docker-compose ps | grep frontend
fi

# 최종 결과
echo ""
echo "=================================================="
echo "🎉 배포 완료!"
echo "=================================================="
echo ""
echo "📋 다음 단계 (중요!):"
echo ""
echo "1️⃣  브라우저 캐시 완전 삭제 (필수!)"
echo "   - Chrome: Ctrl + Shift + Delete"
echo "   - 기간: 전체 기간"
echo "   - 항목: 쿠키, 캐시 모두 체크"
echo "   - Chrome 완전 종료 후 재시작"
echo ""
echo "2️⃣  로그인 및 테스트"
echo "   - URL: http://139.150.11.99/login"
echo "   - 계정: admin / admin123"
echo ""
echo "3️⃣  UI 확인 사항"
echo "   ✅ 모든 페이지에서 사이드바 표시"
echo "   ✅ 실시간 배차 모니터링 메뉴 동작"
echo "   ✅ 페이지 전환 시 레이아웃 유지"
echo ""
echo "4️⃣  문제 발생 시"
echo "   - 콘솔 로그 확인 (F12)"
echo "   - Docker 로그: docker logs uvis-frontend"
echo "   - 복구: cd /root/uvis/frontend/src/pages && cp layout_removal_backup_*/*.tsx ./"
echo ""
echo "=================================================="
echo "📊 처리 요약"
echo "=================================================="
echo "✅ Layout 제거 완료"
echo "✅ 프론트엔드 빌드 완료 (${BUILD_TIME}초)"
echo "✅ Docker 이미지 빌드 완료 (${DOCKER_BUILD_TIME}초)"
echo "✅ 컨테이너 재시작 완료"
echo ""
echo "전체 소요 시간: $((BUILD_TIME + DOCKER_BUILD_TIME + 10))초"
echo "=================================================="
