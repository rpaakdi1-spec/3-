#!/bin/bash

# 빠른 수정 스크립트 - /root/uvis에서 실행

echo "🔧 빠른 수정 시작"

cd /root/uvis/frontend/src/pages

# 1. OptimizationPage에서 Layout import/태그만 제거 (파일 전체는 유지)
echo "1️⃣ OptimizationPage.tsx에서 Layout 제거"

# 백업
cp OptimizationPage.tsx OptimizationPage.tsx.bak_$(date +%s)

# Layout import 라인 삭제
sed -i '4d' OptimizationPage.tsx

# <Layout> 태그 삭제 (라인 328)
sed -i '327d' OptimizationPage.tsx

# </Layout> 태그 삭제 (이제 라인 705)
sed -i '705d' OptimizationPage.tsx

# 검증
echo "Layout 제거 확인:"
grep -n "Layout" OptimizationPage.tsx && echo "⚠️ Layout 아직 존재" || echo "✅ Layout 제거 완료"

# 2. 프론트엔드 빌드
echo ""
echo "2️⃣ 프론트엔드 빌드"
cd /root/uvis/frontend
rm -rf dist/
npm run build

if [ -d "dist" ]; then
    echo "✅ 빌드 성공"
    
    # 3. Docker 빌드 및 배포
    echo ""
    echo "3️⃣ Docker 빌드"
    cd /root/uvis
    docker-compose build --no-cache frontend
    
    echo ""
    echo "4️⃣ 컨테이너 재시작"
    docker-compose up -d frontend
    
    sleep 10
    
    echo ""
    echo "5️⃣ 검증"
    docker-compose ps | grep frontend
    docker exec uvis-frontend ls /usr/share/nginx/html/assets/ | grep -E "(index-|Optimization)" | head -5
    
    echo ""
    echo "✅ 배포 완료!"
else
    echo "❌ 빌드 실패 - 로그 확인 필요"
    exit 1
fi

echo ""
echo "📱 브라우저 테스트:"
echo "1. Ctrl+Shift+Delete → 모든 캐시 삭제"
echo "2. 브라우저 재시작 (시크릿 모드 추천)"
echo "3. http://139.150.11.99/optimization 접속"
echo "4. 사이드바가 하나만 표시되는지 확인"
