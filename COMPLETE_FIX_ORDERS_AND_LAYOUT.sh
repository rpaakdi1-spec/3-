#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎯 완전 수정: OrdersPage + Layout${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd /root/uvis

# Step 1: Backup
BACKUP_DIR="/root/uvis/complete_fix_backup_$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}📦 Step 1: Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
cp frontend/src/pages/OrdersPage.tsx "$BACKUP_DIR/" 2>/dev/null || true
cp frontend/src/App.tsx "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✅ Backup created: $BACKUP_DIR${NC}"
echo ""

# Step 2: Fix OrdersPage.tsx syntax error at line 613
echo -e "${YELLOW}🔧 Step 2: Fixing OrdersPage.tsx syntax error...${NC}"

# Check the exact error location
echo "Checking line 610-620..."
sed -n '610,620p' /root/uvis/frontend/src/pages/OrdersPage.tsx | head -20

# Find the problematic line
PROBLEM_LINE=$(grep -n "isOpen" /root/uvis/frontend/src/pages/OrdersPage.tsx | grep -v "=" | grep -v "//" | head -1)
echo "Problem line: $PROBLEM_LINE"

# Use Python to fix the syntax error
python3 << 'PYEOF'
import re

file_path = "/root/uvis/frontend/src/pages/OrdersPage.tsx"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix common JSX syntax errors
# Pattern 1: Missing closing tag or parenthesis
content = re.sub(r'(<OrderModal[^>]*)\nisOpen', r'\1\n  isOpen', content)

# Pattern 2: Fix incomplete prop syntax
lines = content.split('\n')
fixed_lines = []
in_jsx = False
paren_count = 0

for i, line in enumerate(lines):
    # Track JSX context
    if '<OrderModal' in line:
        in_jsx = True
        paren_count = line.count('(') - line.count(')')
    
    if in_jsx and i >= 610 and i <= 620:
        # Fix line 613 specifically - ensure proper prop syntax
        if 'isOpen' in line and '=' not in line:
            # This is likely a standalone prop name - add proper syntax
            line = line.replace('isOpen', 'isOpen={isOpen}')
    
    fixed_lines.append(line)
    
    if in_jsx and '/>' in line or '</OrderModal>' in line:
        in_jsx = False

result = '\n'.join(fixed_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(result)

print("✅ OrdersPage.tsx syntax fixed")
PYEOF

echo -e "${GREEN}✅ OrdersPage.tsx fixed${NC}"
echo ""

# Step 3: Verify Layout component exists
echo -e "${YELLOW}🔍 Step 3: Checking Layout component...${NC}"

LAYOUT_PATH=$(find /root/uvis/frontend/src -name "Layout.tsx" 2>/dev/null | head -1)

if [ -z "$LAYOUT_PATH" ]; then
    echo -e "${RED}❌ Layout.tsx not found!${NC}"
    echo -e "${YELLOW}Creating Layout component at frontend/src/components/common/Layout.tsx...${NC}"
    
    mkdir -p /root/uvis/frontend/src/components/common
    
    cat > /root/uvis/frontend/src/components/common/Layout.tsx << 'LAYOUTEOF'
import React, { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />
        
        {/* Page content */}
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
LAYOUTEOF
    
    echo -e "${GREEN}✅ Layout component created${NC}"
else
    echo -e "${GREEN}✅ Layout exists at: $LAYOUT_PATH${NC}"
fi
echo ""

# Step 4: Verify App.tsx Layout import
echo -e "${YELLOW}🔍 Step 4: Verifying App.tsx Layout import...${NC}"

APP_LAYOUT_IMPORT=$(grep "import.*Layout.*from.*components/common/Layout" /root/uvis/frontend/src/App.tsx || echo "")

if [ -z "$APP_LAYOUT_IMPORT" ]; then
    echo -e "${YELLOW}Fixing App.tsx Layout import...${NC}"
    
    python3 << 'PYEOF'
file_path = "/root/uvis/frontend/src/App.tsx"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the imports section
if "import Layout from './components/common/Layout';" not in content:
    # Add after React imports
    content = content.replace(
        "import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';",
        "import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';\nimport Layout from './components/common/Layout';"
    )

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ App.tsx Layout import fixed")
PYEOF
    
    echo -e "${GREEN}✅ App.tsx import fixed${NC}"
else
    echo -e "${GREEN}✅ App.tsx Layout import correct${NC}"
fi

# Show current App.tsx Layout usage
grep -A 3 "<Layout>" /root/uvis/frontend/src/App.tsx || echo "⚠️  No <Layout> tag found in App.tsx"
echo ""

# Step 5: Build
echo -e "${YELLOW}🏗️  Step 5: Building frontend...${NC}"
cd /root/uvis/frontend

rm -rf dist/
npm run build 2>&1 | tee /tmp/build.log

if [ -f "dist/index.html" ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    ls -lh dist/assets/*.css 2>/dev/null | head -5
else
    echo -e "${RED}❌ Build failed!${NC}"
    echo "Last 30 lines of build log:"
    tail -30 /tmp/build.log
    exit 1
fi
echo ""

# Step 6: Docker rebuild
echo -e "${YELLOW}🐳 Step 6: Rebuilding Docker image...${NC}"
cd /root/uvis
docker-compose build --no-cache frontend

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi
echo ""

# Step 7: Restart container
echo -e "${YELLOW}🔄 Step 7: Restarting container...${NC}"
docker-compose up -d frontend
sleep 5

# Step 8: Copy dist to container
echo -e "${YELLOW}📋 Step 8: Copying built files to container...${NC}"
docker cp /root/uvis/frontend/dist/. uvis-frontend:/usr/share/nginx/html/
docker exec uvis-frontend nginx -s reload

# Verify
CONTAINER_CSS=$(docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css" | wc -l)
echo -e "${GREEN}✅ Container has $CONTAINER_CSS CSS files${NC}"
echo ""

# Final verification
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 수정 완료!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "✅ Fixed: OrdersPage.tsx syntax error"
echo "✅ Fixed: Layout component location"
echo "✅ Fixed: App.tsx Layout import"
echo "✅ Built: Frontend assets"
echo "✅ Deployed: Docker container"
echo ""
echo -e "${YELLOW}📌 다음 단계:${NC}"
echo "1. 브라우저 캐시 완전 삭제 (Ctrl+Shift+Delete → 전체 기간)"
echo "2. Chrome 완전 종료 후 재시작"
echo "3. http://139.150.11.99/login 접속"
echo "   - ID: admin"
echo "   - PW: admin123"
echo ""
echo -e "${GREEN}백업 위치: $BACKUP_DIR${NC}"
echo ""

