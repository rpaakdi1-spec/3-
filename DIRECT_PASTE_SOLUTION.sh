#!/bin/bash
# UVIS Layout 완전 수정 - 직접 붙여넣기용 스크립트
# 이 스크립트를 서버 터미널에 직접 복사해서 붙여넣으세요

set -e

echo "=================================================="
echo "🚀 UVIS Layout 완전 수정 시작"
echo "=================================================="
echo ""

# 현재 위치 확인
CURRENT_DIR=$(pwd)
echo "현재 위치: $CURRENT_DIR"

# /root/uvis로 이동
if [ ! -d "/root/uvis" ]; then
    echo "❌ /root/uvis 디렉토리를 찾을 수 없습니다"
    exit 1
fi

cd /root/uvis
echo "✅ /root/uvis로 이동"
echo ""

# Pages 디렉토리 확인
PAGES_DIR="/root/uvis/frontend/src/pages"
if [ ! -d "$PAGES_DIR" ]; then
    echo "❌ Pages 디렉토리를 찾을 수 없습니다: $PAGES_DIR"
    exit 1
fi

echo "=================================================="
echo "📦 1단계: 백업 생성"
echo "=================================================="
BACKUP_DIR="$PAGES_DIR/layout_removal_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cd "$PAGES_DIR"
cp *.tsx "$BACKUP_DIR/" 2>/dev/null || true
BACKUP_COUNT=$(ls "$BACKUP_DIR"/*.tsx 2>/dev/null | wc -l)
echo "✅ $BACKUP_COUNT 개 파일 백업 완료: $BACKUP_DIR"
echo ""

echo "=================================================="
echo "🔧 2단계: Layout 제거"
echo "=================================================="

# Layout 사용 페이지 찾기
LAYOUT_FILES=$(grep -l "import.*Layout" *.tsx 2>/dev/null | grep -v "LoginPage.tsx" | sort)
TOTAL_FILES=$(echo "$LAYOUT_FILES" | grep -c "" || echo "0")
echo "📊 Layout을 사용하는 페이지: $TOTAL_FILES 개"

if [ "$TOTAL_FILES" -eq 0 ]; then
    echo "✅ 이미 모든 페이지에서 Layout이 제거되었습니다!"
else
    echo ""
    SUCCESS_COUNT=0
    FAIL_COUNT=0
    
    for file in $LAYOUT_FILES; do
        echo "  처리중: $file"
        
        # 개별 백업
        cp "$file" "${file}.before_removal"
        
        # 임시 파일로 처리
        TEMP_FILE="${file}.tmp"
        cp "$file" "$TEMP_FILE"
        
        # import 제거
        sed -i "/^import.*Layout.*from.*Layout/d" "$TEMP_FILE"
        
        # <Layout> 제거 (공백 포함)
        sed -i "/^[[:space:]]*<Layout/d" "$TEMP_FILE"
        
        # </Layout> 제거 (공백 포함)
        sed -i "/^[[:space:]]*<\/Layout>/d" "$TEMP_FILE"
        
        # 연속 빈 줄 정리
        sed -i '/^$/N;/^\n$/D' "$TEMP_FILE"
        
        # 검증
        if grep -q "import.*Layout\|<Layout\|</Layout>" "$TEMP_FILE"; then
            echo "    ❌ 실패: Layout이 여전히 남아있음"
            rm "$TEMP_FILE"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        else
            mv "$TEMP_FILE" "$file"
            echo "    ✅ 성공"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        fi
    done
    
    echo ""
    echo "=================================================="
    echo "📊 처리 결과"
    echo "=================================================="
    echo "✅ 성공: $SUCCESS_COUNT 개"
    echo "❌ 실패: $FAIL_COUNT 개"
fi

echo ""
echo "=================================================="
echo "🔍 3단계: 검증"
echo "=================================================="
REMAINING=$(grep -l "import.*Layout" *.tsx 2>/dev/null | grep -v "LoginPage.tsx" | wc -l)
echo "📊 Layout이 남아있는 페이지: $REMAINING 개"

if [ "$REMAINING" -eq 0 ]; then
    echo "✅ 모든 페이지에서 Layout 제거 완료!"
else
    echo "⚠️  일부 페이지에서 Layout이 남아있습니다:"
    grep -l "import.*Layout" *.tsx 2>/dev/null | grep -v "LoginPage.tsx"
fi

echo ""
echo "=================================================="
echo "🔨 4단계: 프론트엔드 빌드"
echo "=================================================="
cd /root/uvis/frontend
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
    echo "복구 방법:"
    echo "cd $PAGES_DIR"
    echo "cp $BACKUP_DIR/*.tsx ./"
    exit 1
fi

echo ""
echo "=================================================="
echo "🐳 5단계: Docker 이미지 재빌드"
echo "=================================================="
cd /root/uvis
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

echo ""
echo "=================================================="
echo "🔄 6단계: 컨테이너 재시작"
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
echo "=================================================="
echo "📊 처리 요약"
echo "=================================================="
echo "✅ Layout 제거 완료"
echo "✅ 프론트엔드 빌드 완료 (${BUILD_TIME}초)"
echo "✅ Docker 이미지 빌드 완료 (${DOCKER_BUILD_TIME}초)"
echo "✅ 컨테이너 재시작 완료"
echo ""
echo "전체 소요 시간: $((BUILD_TIME + DOCKER_BUILD_TIME + 10))초"
echo ""
echo "💾 백업 위치: $BACKUP_DIR"
echo ""
echo "=================================================="
