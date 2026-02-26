#!/bin/bash

# 현재 상태 진단 스크립트

echo "🔍 현재 상태 진단"
echo "===================="
echo ""

cd /root/uvis

echo "1️⃣ OptimizationPage.tsx 상태"
echo "----------------------------"
echo "Layout import/usage:"
grep -n "Layout" frontend/src/pages/OptimizationPage.tsx | head -5

echo ""
echo "include_gps 설정:"
grep -n "include_gps" frontend/src/pages/OptimizationPage.tsx

echo ""
echo "파일 크기:"
wc -l frontend/src/pages/OptimizationPage.tsx

echo ""
echo "2️⃣ App.tsx 상태"
echo "----------------------------"
echo "Import 경로:"
grep -n "import.*Store" frontend/src/App.tsx | head -5

echo ""
echo "Layout 사용:"
grep -n "Layout" frontend/src/App.tsx | head -5

echo ""
echo "3️⃣ 디렉토리 구조"
echo "----------------------------"
echo "Store 디렉토리:"
ls -la frontend/src/ | grep -E "store|stores"

echo ""
echo "Services 디렉토리:"
ls -la frontend/src/services/ 2>/dev/null | head -10 || echo "services 폴더 없음"

echo ""
echo "4️⃣ Docker 컨테이너 상태"
echo "----------------------------"
docker-compose ps

echo ""
echo "5️⃣ 컨테이너 내부 파일"
echo "----------------------------"
echo "index.html에서 로드하는 JS:"
docker exec uvis-frontend cat /usr/share/nginx/html/index.html 2>/dev/null | grep -o 'src="/assets/[^"]*\.js"' || echo "컨테이너 접근 불가"

echo ""
echo "실제 존재하는 index-*.js:"
docker exec uvis-frontend ls /usr/share/nginx/html/assets/index-*.js 2>/dev/null || echo "index-*.js 없음 또는 컨테이너 접근 불가"

echo ""
echo "OptimizationPage JS:"
docker exec uvis-frontend ls /usr/share/nginx/html/assets/Optimization*.js 2>/dev/null || echo "OptimizationPage JS 없음 또는 컨테이너 접근 불가"

echo ""
echo "6️⃣ 로컬 빌드 상태"
echo "----------------------------"
if [ -d "frontend/dist" ]; then
    echo "✅ dist 폴더 존재"
    echo "빌드 시간:"
    ls -ld frontend/dist
    echo ""
    echo "index-*.js 파일:"
    ls -lh frontend/dist/assets/index-*.js 2>/dev/null || echo "없음"
    echo ""
    echo "OptimizationPage JS:"
    ls -lh frontend/dist/assets/Optimization*.js 2>/dev/null || echo "없음"
else
    echo "❌ dist 폴더 없음 - 빌드 필요"
fi

echo ""
echo "7️⃣ Git 상태"
echo "----------------------------"
git status --short frontend/src/ 2>/dev/null | head -10 || echo "Git 저장소 아님"

echo ""
echo "===================="
echo "진단 완료"
