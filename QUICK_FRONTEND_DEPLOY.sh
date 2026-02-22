#!/bin/bash

echo "=========================================="
echo "🚀 프론트엔드 빠른 배포"
echo "=========================================="
echo ""

# 프론트엔드 디렉토리로 이동
cd /root/uvis/frontend

# 최신 커밋 확인
echo "📌 현재 커밋:"
git log --oneline -1

# 필터링 기능 확인
echo ""
echo "🔍 필터링 기능 확인..."
if grep -q "searchText" src/pages/DispatchesPage.tsx; then
    echo "✅ 검색 필터 확인됨"
else
    echo "❌ 검색 필터 없음"
    exit 1
fi

if grep -q "filterStatus" src/pages/DispatchesPage.tsx; then
    echo "✅ 상태 필터 확인됨"
else
    echo "❌ 상태 필터 없음"
    exit 1
fi

if grep -q "filterVehicle" src/pages/DispatchesPage.tsx; then
    echo "✅ 차량 필터 확인됨"
else
    echo "❌ 차량 필터 없음"
    exit 1
fi

if grep -q "filterDate" src/pages/DispatchesPage.tsx; then
    echo "✅ 날짜 필터 확인됨"
else
    echo "❌ 날짜 필터 없음"
    exit 1
fi

# 빌드
echo ""
echo "🔨 빌드 시작..."
npm run build

# 빌드 확인
if [ ! -d "dist" ]; then
    echo "❌ 빌드 실패"
    exit 1
fi

echo "✅ 빌드 완료"

# 컨테이너에 복사
echo ""
echo "📦 컨테이너에 복사..."
docker cp dist/. uvis-frontend:/usr/share/nginx/html/

# 캐시 클리어
echo ""
echo "🧹 캐시 클리어..."
docker exec uvis-nginx rm -rf /var/cache/nginx/* 2>/dev/null || true

# 재시작
echo ""
echo "🔄 컨테이너 재시작..."
docker restart uvis-frontend
docker restart uvis-nginx

# 대기
echo ""
echo "⏳ 대기 중 (10초)..."
sleep 10

# 확인
echo ""
echo "🔍 상태 확인..."
docker ps | grep -E "uvis-frontend|uvis-nginx"

echo ""
echo "✅ 배포 완료!"
echo ""
echo "🌐 브라우저 테스트:"
echo "  1. InPrivate 모드 열기 (Ctrl+Shift+N)"
echo "  2. http://139.150.11.99 접속"
echo "  3. 배차 관리 페이지에서 필터 확인"
echo ""
