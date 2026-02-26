#!/bin/bash

################################################################################
# 모든 페이지에서 Layout import 및 태그 제거
# App.tsx에 이미 전역 Layout이 있으므로 개별 페이지에서는 제거 필요
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🗑️  모든 페이지에서 Layout 제거 시작...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

PAGES_DIR="/root/uvis/frontend/src/pages"
BACKUP_DIR="/root/uvis/frontend/src/pages/layout_complete_removal_$(date +%Y%m%d_%H%M%S)"

# 백업 생성
echo -e "${YELLOW}📦 백업 생성 중...${NC}"
mkdir -p "$BACKUP_DIR"
cp "$PAGES_DIR"/*.tsx "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✅ 백업 완료: $BACKUP_DIR${NC}"
echo ""

# Layout import가 있는 모든 페이지 찾기 (LoginPage 제외)
echo -e "${YELLOW}🔍 Layout을 사용하는 페이지 찾는 중...${NC}"
LAYOUT_PAGES=$(grep -l "import Layout" "$PAGES_DIR"/*.tsx 2>/dev/null | grep -v "LoginPage.tsx" || true)

if [ -z "$LAYOUT_PAGES" ]; then
    echo -e "${GREEN}✅ Layout을 사용하는 페이지가 없습니다${NC}"
    exit 0
fi

PAGE_COUNT=$(echo "$LAYOUT_PAGES" | wc -l)
echo -e "${BLUE}📊 총 ${PAGE_COUNT}개 페이지에서 Layout 제거 예정${NC}"
echo ""

# Python 스크립트로 정확하게 제거
echo -e "${YELLOW}🔧 Layout 제거 중...${NC}"

SUCCESS_COUNT=0
FAIL_COUNT=0

for PAGE_PATH in $LAYOUT_PAGES; do
    PAGE_NAME=$(basename "$PAGE_PATH")
    
    python3 << PYTHON_END
import re

try:
    with open('$PAGE_PATH', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Layout import 제거
    content = re.sub(r'^import Layout from [^\n]+;\n', '', content, flags=re.MULTILINE)
    
    # 2. <Layout> 태그 제거 (여러 패턴)
    # Pattern 1: <Layout>\n
    content = re.sub(r'<Layout>\n', '', content)
    # Pattern 2: </Layout>
    content = re.sub(r'</Layout>', '', content)
    # Pattern 3: 단독 <Layout>
    content = re.sub(r'<Layout>', '', content)
    
    # 3. 연속된 빈 줄 정리 (3개 이상 → 2개로)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # 변경사항이 있으면 저장
    if content != original_content:
        with open('$PAGE_PATH', 'w', encoding='utf-8') as f:
            f.write(content)
        print('✓ $PAGE_NAME')
        exit(0)
    else:
        print('⚠ $PAGE_NAME (변경사항 없음)')
        exit(1)
except Exception as e:
    print(f'✗ $PAGE_NAME (오류: {e})')
    exit(2)
PYTHON_END
    
    if [ $? -eq 0 ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo -e "${GREEN}  ✓${NC} $PAGE_NAME"
    elif [ $? -eq 1 ]; then
        echo -e "${YELLOW}  ⚠${NC} $PAGE_NAME (변경 없음)"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo -e "${RED}  ✗${NC} $PAGE_NAME (실패)"
    fi
done

echo ""
echo -e "${GREEN}✅ Layout 제거 완료${NC}"
echo -e "   성공: ${GREEN}$SUCCESS_COUNT${NC} 개"
echo -e "   실패: ${RED}$FAIL_COUNT${NC} 개"
echo ""

# 검증
echo -e "${YELLOW}🔍 검증 중...${NC}"
REMAINING=$(grep -r "import Layout" "$PAGES_DIR"/*.tsx 2>/dev/null | grep -v "LoginPage" | wc -l)

if [ "$REMAINING" -eq 0 ]; then
    echo -e "${GREEN}✅ 모든 페이지에서 Layout import 제거 완료${NC}"
else
    echo -e "${YELLOW}⚠️  $REMAINING 개 파일에 여전히 Layout 남음${NC}"
    grep -r "import Layout" "$PAGES_DIR"/*.tsx 2>/dev/null | grep -v "LoginPage"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 작업 완료!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📝 다음 단계:${NC}"
echo -e "   cd /root/uvis/frontend"
echo -e "   rm -rf dist/"
echo -e "   npm run build"
echo -e "   cd /root/uvis"
echo -e "   docker-compose build --no-cache frontend"
echo -e "   docker-compose up -d frontend"
echo ""
echo -e "${YELLOW}📝 롤백 (문제 발생 시):${NC}"
echo -e "   cp $BACKUP_DIR/*.tsx /root/uvis/frontend/src/pages/"
echo ""
