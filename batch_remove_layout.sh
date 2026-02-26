#!/bin/bash
# UVIS Layout 일괄 제거 스크립트
# 목적: 모든 페이지에서 Layout import와 태그를 안전하게 제거

set -e

PAGES_DIR="/root/uvis/frontend/src/pages"
BACKUP_DIR="/root/uvis/frontend/src/pages/layout_removal_backup_$(date +%Y%m%d_%H%M%S)"

echo "=================================================="
echo "🔧 UVIS Layout 일괄 제거 스크립트"
echo "=================================================="
echo ""

# 1. 백업 생성
echo "📦 1단계: 전체 백업 생성중..."
cd "$PAGES_DIR"
mkdir -p "$BACKUP_DIR"
cp *.tsx "$BACKUP_DIR/" 2>/dev/null || true
BACKUP_COUNT=$(ls "$BACKUP_DIR"/*.tsx 2>/dev/null | wc -l)
echo "✅ $BACKUP_COUNT 개 파일 백업 완료: $BACKUP_DIR"
echo ""

# 2. Layout 사용 페이지 분석
echo "🔍 2단계: Layout 사용 페이지 분석..."
LAYOUT_FILES=$(grep -l "import.*Layout" *.tsx 2>/dev/null | grep -v "LoginPage.tsx" | sort)
TOTAL_FILES=$(echo "$LAYOUT_FILES" | grep -c "" || echo "0")
echo "📊 Layout을 사용하는 페이지: $TOTAL_FILES 개"
echo ""

if [ "$TOTAL_FILES" -eq 0 ]; then
    echo "✅ 모든 페이지에서 Layout이 이미 제거되었습니다!"
    exit 0
fi

# 3. 각 파일에서 Layout 제거
echo "🔧 3단계: Layout 제거 시작..."
SUCCESS_COUNT=0
FAIL_COUNT=0

for file in $LAYOUT_FILES; do
    echo "  처리중: $file"
    
    # 백업 (개별 파일)
    cp "$file" "${file}.before_removal"
    
    # Layout import 라인 찾기
    IMPORT_LINES=$(grep -n "^import.*Layout" "$file" | cut -d: -f1 | tac)
    
    # Layout 태그 라인 찾기
    LAYOUT_OPEN_LINES=$(grep -n "^[[:space:]]*<Layout" "$file" | cut -d: -f1 | tac)
    LAYOUT_CLOSE_LINES=$(grep -n "^[[:space:]]*</Layout>" "$file" | cut -d: -f1 | tac)
    
    # 임시 파일 생성
    TEMP_FILE="${file}.tmp"
    cp "$file" "$TEMP_FILE"
    
    # import 제거
    for line_num in $IMPORT_LINES; do
        sed -i "${line_num}d" "$TEMP_FILE"
    done
    
    # <Layout> 태그 제거 (역순)
    for line_num in $LAYOUT_OPEN_LINES; do
        sed -i "${line_num}d" "$TEMP_FILE"
    done
    
    # </Layout> 태그 제거 (역순)
    for line_num in $LAYOUT_CLOSE_LINES; do
        sed -i "${line_num}d" "$TEMP_FILE"
    done
    
    # 연속된 빈 줄 정리
    sed -i '/^$/N;/^\n$/D' "$TEMP_FILE"
    
    # 검증: Layout 문자열이 남아있는지 확인
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
echo "💾 백업 위치: $BACKUP_DIR"
echo ""

# 4. 최종 검증
echo "🔍 4단계: 최종 검증..."
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
echo "📝 다음 단계"
echo "=================================================="
echo "1. 빌드 테스트:"
echo "   cd /root/uvis/frontend"
echo "   rm -rf dist/"
echo "   npm run build"
echo ""
echo "2. Docker 이미지 재빌드:"
echo "   cd /root/uvis"
echo "   docker-compose build --no-cache frontend"
echo ""
echo "3. 컨테이너 재시작:"
echo "   docker-compose up -d frontend"
echo ""
echo "4. 브라우저 캐시 삭제 후 테스트"
echo "=================================================="
