#!/bin/bash
# UVIS Layout 제거 검증 스크립트

set -e

PAGES_DIR="/root/uvis/frontend/src/pages"
APP_TSX="/root/uvis/frontend/src/App.tsx"

echo "=================================================="
echo "🔍 UVIS Layout 제거 검증"
echo "=================================================="
echo ""

# 1. Pages 디렉토리 검증
echo "📂 1. Pages 디렉토리 검증"
if [ ! -d "$PAGES_DIR" ]; then
    echo "❌ Pages 디렉토리를 찾을 수 없습니다: $PAGES_DIR"
    exit 1
fi
echo "✅ Pages 디렉토리 존재"
echo ""

# 2. Layout 사용 페이지 확인
echo "🔍 2. Layout import 확인"
cd "$PAGES_DIR"
LAYOUT_PAGES=$(grep -l "import.*Layout" *.tsx 2>/dev/null | grep -v "LoginPage.tsx" || true)
LAYOUT_COUNT=$(echo "$LAYOUT_PAGES" | grep -c . || echo "0")

if [ "$LAYOUT_COUNT" -eq 0 ]; then
    echo "✅ Layout을 사용하는 페이지 없음 (LoginPage 제외)"
else
    echo "⚠️  Layout을 사용하는 페이지: $LAYOUT_COUNT 개"
    echo "$LAYOUT_PAGES" | while read -r page; do
        echo "   - $page"
    done
fi
echo ""

# 3. Layout 태그 확인
echo "🔍 3. Layout 태그 확인"
LAYOUT_TAG_FILES=$(grep -l "<Layout\|</Layout>" *.tsx 2>/dev/null | grep -v "LoginPage.tsx" || true)
LAYOUT_TAG_COUNT=$(echo "$LAYOUT_TAG_FILES" | grep -c . || echo "0")

if [ "$LAYOUT_TAG_COUNT" -eq 0 ]; then
    echo "✅ Layout 태그를 사용하는 페이지 없음"
else
    echo "⚠️  Layout 태그를 사용하는 페이지: $LAYOUT_TAG_COUNT 개"
    echo "$LAYOUT_TAG_FILES" | while read -r page; do
        OPEN_COUNT=$(grep -c "<Layout" "$page" 2>/dev/null || echo "0")
        CLOSE_COUNT=$(grep -c "</Layout>" "$page" 2>/dev/null || echo "0")
        echo "   - $page: <Layout> $OPEN_COUNT 개, </Layout> $CLOSE_COUNT 개"
    done
fi
echo ""

# 4. App.tsx Layout 확인
echo "🔍 4. App.tsx Layout 확인"
if [ ! -f "$APP_TSX" ]; then
    echo "❌ App.tsx를 찾을 수 없습니다: $APP_TSX"
    exit 1
fi

APP_LAYOUT_IMPORT=$(grep -c "import.*Layout" "$APP_TSX" 2>/dev/null || echo "0")
APP_LAYOUT_TAG=$(grep -c "<Layout" "$APP_TSX" 2>/dev/null || echo "0")

if [ "$APP_LAYOUT_IMPORT" -gt 0 ] && [ "$APP_LAYOUT_TAG" -gt 0 ]; then
    echo "✅ App.tsx에 Layout import와 사용이 존재"
    echo "   - Import: $APP_LAYOUT_IMPORT 개"
    echo "   - 태그: $APP_LAYOUT_TAG 개"
else
    echo "⚠️  App.tsx에 Layout이 없거나 불완전합니다"
    echo "   - Import: $APP_LAYOUT_IMPORT 개"
    echo "   - 태그: $APP_LAYOUT_TAG 개"
fi
echo ""

# 5. LoginPage 확인
echo "🔍 5. LoginPage.tsx 확인"
LOGIN_PAGE="$PAGES_DIR/LoginPage.tsx"
if [ ! -f "$LOGIN_PAGE" ]; then
    echo "⚠️  LoginPage.tsx를 찾을 수 없습니다"
else
    LOGIN_LAYOUT=$(grep -c "Layout" "$LOGIN_PAGE" 2>/dev/null || echo "0")
    if [ "$LOGIN_LAYOUT" -eq 0 ]; then
        echo "✅ LoginPage에 Layout 없음 (정상)"
    else
        echo "⚠️  LoginPage에 Layout이 있습니다 (제거 권장)"
    fi
fi
echo ""

# 6. 최종 점수
echo "=================================================="
echo "📊 최종 검증 결과"
echo "=================================================="

TOTAL_SCORE=0
MAX_SCORE=5

# 점수 계산
if [ "$LAYOUT_COUNT" -eq 0 ]; then
    TOTAL_SCORE=$((TOTAL_SCORE + 1))
    echo "✅ [1/5] 페이지 Layout import 제거"
else
    echo "❌ [0/5] 페이지 Layout import 제거 - $LAYOUT_COUNT 개 남음"
fi

if [ "$LAYOUT_TAG_COUNT" -eq 0 ]; then
    TOTAL_SCORE=$((TOTAL_SCORE + 1))
    echo "✅ [1/5] 페이지 Layout 태그 제거"
else
    echo "❌ [0/5] 페이지 Layout 태그 제거 - $LAYOUT_TAG_COUNT 개 남음"
fi

if [ "$APP_LAYOUT_IMPORT" -gt 0 ]; then
    TOTAL_SCORE=$((TOTAL_SCORE + 1))
    echo "✅ [1/5] App.tsx Layout import 존재"
else
    echo "❌ [0/5] App.tsx Layout import 없음"
fi

if [ "$APP_LAYOUT_TAG" -gt 0 ]; then
    TOTAL_SCORE=$((TOTAL_SCORE + 1))
    echo "✅ [1/5] App.tsx Layout 태그 사용"
else
    echo "❌ [0/5] App.tsx Layout 태그 없음"
fi

if [ -f "$LOGIN_PAGE" ]; then
    LOGIN_LAYOUT_CHECK=$(grep -c "Layout" "$LOGIN_PAGE" 2>/dev/null || echo "0")
    if [ "$LOGIN_LAYOUT_CHECK" -eq 0 ]; then
        TOTAL_SCORE=$((TOTAL_SCORE + 1))
        echo "✅ [1/5] LoginPage Layout 없음"
    else
        echo "❌ [0/5] LoginPage에 Layout 있음"
    fi
else
    echo "⚠️  [0/5] LoginPage 확인 불가"
fi

echo ""
echo "=================================================="
echo "🎯 총점: $TOTAL_SCORE / $MAX_SCORE"
echo "=================================================="

if [ "$TOTAL_SCORE" -eq "$MAX_SCORE" ]; then
    echo "🎉 완벽합니다! Layout 구조가 올바르게 설정되었습니다."
    echo ""
    echo "다음 단계:"
    echo "1. cd /root/uvis/frontend && npm run build"
    echo "2. cd /root/uvis && docker-compose build --no-cache frontend"
    echo "3. docker-compose up -d frontend"
    echo "4. 브라우저 캐시 삭제 후 테스트"
    exit 0
elif [ "$TOTAL_SCORE" -ge 3 ]; then
    echo "⚠️  거의 완료되었습니다. 남은 문제를 해결하세요."
    exit 1
else
    echo "❌ Layout 구조에 문제가 있습니다."
    echo ""
    echo "해결 방법:"
    echo "1. ./batch_remove_layout.sh 실행"
    echo "2. App.tsx 확인 (Layout은 App.tsx에만 있어야 함)"
    exit 1
fi
