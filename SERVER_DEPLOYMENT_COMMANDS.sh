#!/bin/bash
# 프론트엔드 진단 로그 배포 스크립트
# 서버: root@139.150.11.99
# 목적: 배차 최적화 시 "차량을 찾을 수 없음" 오류 진단

echo "=================================================="
echo "🚀 프론트엔드 진단 로그 배포"
echo "=================================================="
echo ""

# 1. 프론트엔드 디렉터리로 이동
echo "📂 Step 1: 프론트엔드 디렉터리로 이동..."
cd /root/uvis/frontend || { echo "❌ 디렉터리 이동 실패"; exit 1; }
echo "✅ 현재 위치: $(pwd)"
echo ""

# 2. 최신 코드 가져오기
echo "📥 Step 2: 최신 코드 가져오기..."
git fetch origin main
git pull origin main
if [ $? -eq 0 ]; then
    echo "✅ 코드 업데이트 성공"
else
    echo "❌ 코드 업데이트 실패"
    exit 1
fi
echo ""

# 3. 현재 dist 백업
echo "💾 Step 3: 현재 빌드 백업..."
BACKUP_DIR="dist.backup_$(date +%Y%m%d_%H%M%S)"
if [ -d "dist" ]; then
    cp -r dist "$BACKUP_DIR"
    echo "✅ 백업 완료: $BACKUP_DIR"
else
    echo "⚠️  기존 dist 없음 (첫 빌드)"
fi
echo ""

# 4. 의존성 확인
echo "📦 Step 4: 의존성 확인..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules 없음, 설치 필요"
    npm install
fi
echo "✅ 의존성 확인 완료"
echo ""

# 5. 프론트엔드 빌드
echo "🔨 Step 5: 프론트엔드 빌드 중..."
npm run build
if [ $? -eq 0 ]; then
    echo "✅ 빌드 성공"
else
    echo "❌ 빌드 실패"
    echo "⚠️  롤백 중..."
    if [ -d "$BACKUP_DIR" ]; then
        rm -rf dist
        mv "$BACKUP_DIR" dist
        echo "✅ 롤백 완료"
    fi
    exit 1
fi
echo ""

# 6. 빌드 결과 확인
echo "🔍 Step 6: 빌드 결과 확인..."
if [ -f "dist/index.html" ]; then
    FILE_SIZE=$(du -sh dist | cut -f1)
    FILE_COUNT=$(find dist -type f | wc -l)
    echo "✅ dist/index.html 존재"
    echo "📊 빌드 크기: $FILE_SIZE"
    echo "📊 파일 개수: $FILE_COUNT"
else
    echo "❌ dist/index.html 없음"
    exit 1
fi
echo ""

# 7. Nginx/Docker 재시작
echo "🔄 Step 7: 웹서버 재시작..."
if docker ps | grep -q uvis-frontend; then
    echo "🐳 Docker 컨테이너 재시작..."
    docker restart uvis-frontend
    sleep 3
    if docker ps | grep -q uvis-frontend; then
        echo "✅ Docker 재시작 성공"
    else
        echo "❌ Docker 재시작 실패"
        exit 1
    fi
elif systemctl is-active --quiet nginx; then
    echo "🌐 Nginx 재시작..."
    nginx -t && systemctl restart nginx
    if [ $? -eq 0 ]; then
        echo "✅ Nginx 재시작 성공"
    else
        echo "❌ Nginx 재시작 실패"
        exit 1
    fi
else
    echo "⚠️  Docker/Nginx 미실행 - 수동 확인 필요"
fi
echo ""

echo "=================================================="
echo "✅ 배포 완료!"
echo "=================================================="
echo ""
echo "📋 다음 단계:"
echo "1. 브라우저에서 Ctrl+Shift+R (캐시 무시 새로고침)"
echo "2. F12 → Console 탭 열기"
echo "3. 배차 최적화 페이지에서 주문 선택 (예: 27, 28, 30)"
echo "4. '배차 최적화' 버튼 클릭"
echo ""
echo "🔍 Console에서 확인할 로그:"
echo "   🔍 dispatch 데이터: { ... }"
echo "   🔍 찾는 vehicle_id: <값>"
echo "   🔍 사용 가능한 vehicles: [...]"
echo "   ⚠️ 차량을 찾을 수 없음: <값>"
echo ""
echo "📸 스크린샷으로 Console 로그 전체 캡처해서 공유 부탁드립니다!"
echo ""
echo "=================================================="
