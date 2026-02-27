#!/bin/bash

# ============================================================================
# WebSocket Overload Fix Deployment Script
# ============================================================================
# 이 스크립트는 WebSocket 무한 재연결 문제를 수정한 버전을 배포합니다
# ============================================================================

set -e

echo "=================================================="
echo "🔧 WebSocket 과부하 수정 배포"
echo "=================================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "📥 1. 최신 코드 가져오기..."
git pull origin main

echo ""
echo "🛑 2. Frontend 컨테이너 중지..."
docker-compose stop frontend

echo ""
echo "🗑️  3. Frontend 컨테이너 제거..."
docker-compose rm -f frontend

echo ""
echo "🏗️  4. Frontend 이미지 재빌드..."
echo "   (캐시 없이 완전 재빌드: ~5분 소요)"
docker-compose build --no-cache frontend

echo ""
echo "🚀 5. Frontend 컨테이너 시작..."
docker-compose up -d frontend

echo ""
echo "⏳ 6. Frontend 시작 대기 (10초)..."
sleep 10

echo ""
echo "🔍 7. Frontend 컨테이너 상태 확인..."
docker-compose ps frontend

echo ""
echo "📝 8. Frontend 로그 확인..."
docker-compose logs frontend --tail 30

echo ""
echo "=================================================="
echo -e "${GREEN}✅ 배포 완료!${NC}"
echo "=================================================="
echo ""
echo "📌 주요 변경사항:"
echo "  ✅ WebSocket 무한 재연결 방지"
echo "  ✅ 최대 재연결 시도 횟수 제한 (5회)"
echo "  ✅ Exponential backoff 적용 (5s → 80s)"
echo "  ✅ 컴포넌트 unmount 시 올바른 cleanup"
echo "  ✅ Production 환경 로그 억제"
echo ""
echo "🧪 테스트 방법:"
echo "  1. 브라우저에서 http://139.150.11.99 접속"
echo "  2. F12 → Console 탭 열기"
echo "  3. localStorage.clear(); sessionStorage.clear(); location.reload();"
echo "  4. 로그인: admin / admin123"
echo "  5. 대시보드 페이지 확인 (과부하 없어야 함)"
echo "  6. Console에서 WebSocket 로그 확인"
echo ""
echo "🎯 기대 결과:"
echo "  ✅ 페이지 로딩 정상 (느려지지 않음)"
echo "  ✅ 브라우저 CPU 사용량 정상"
echo "  ✅ WebSocket 연결 최대 1개"
echo "  ✅ 연결 실패 시 최대 5회 재시도 후 중단"
echo ""
echo "⚠️  문제 발생 시:"
echo "  - 브라우저 캐시 강제 새로고침: Ctrl+Shift+R"
echo "  - 시크릿/프라이빗 모드로 테스트"
echo "  - Frontend 로그 확인: docker-compose logs frontend --tail 100"
echo ""
