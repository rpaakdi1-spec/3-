#!/bin/bash
# 서버에서 실행할 배포 스크립트
# 사용법: bash DEPLOY_LAYOUT_FIX.sh

set -e  # Exit on error

echo "============================================="
echo "🚀 Layout Fix 배포 스크립트"
echo "============================================="
echo ""

# 1. 백업
echo "📦 1. 현재 frontend 백업 중..."
cd /root/uvis
tar -czf "frontend_backup_$(date +%Y%m%d_%H%M%S).tar.gz" frontend/
echo "✅ 백업 완료"
echo ""

# 2. OrdersPage.tsx 수정
echo "🔧 2. OrdersPage.tsx 수정 중..."
cat > /tmp/fix_orders.py << 'PYEOF'
file_path = '/root/uvis/frontend/src/pages/OrdersPage.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: Replace "       </>\n  );" with "      )}\n    </>\n  );"
content = content.replace('       </>\n  );', '      )}\n    </>\n  );')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ OrdersPage.tsx 수정 완료")
PYEOF

python3 /tmp/fix_orders.py
echo ""

# 3. 빌드
echo "🏗️  3. Frontend 빌드 중..."
cd /root/uvis/frontend
npm run build
echo "✅ 빌드 완료"
echo ""

# 4. Docker 이미지 재빌드
echo "🐳 4. Docker 이미지 재빌드 중..."
cd /root/uvis
docker-compose build --no-cache frontend
echo "✅ Docker 이미지 빌드 완료"
echo ""

# 5. 컨테이너 재시작
echo "🔄 5. Frontend 컨테이너 재시작 중..."
docker-compose up -d frontend
echo "✅ 컨테이너 재시작 완료"
echo ""

# 6. 대기 및 상태 확인
echo "⏳ 6. 컨테이너 시작 대기 (15초)..."
sleep 15
echo ""

echo "📊 7. 상태 확인"
echo "============================================="
docker ps --filter name=uvis-frontend
echo ""
echo "📝 Frontend 로그 (최근 10줄):"
docker logs uvis-frontend --tail 10
echo ""

# 8. CSS 파일 확인
echo "🎨 8. CSS 파일 확인"
echo "============================================="
docker exec uvis-frontend find /usr/share/nginx/html/assets -name "*.css"
echo ""

# 9. 완료 메시지
echo "============================================="
echo "✅ 배포 완료!"
echo "============================================="
echo ""
echo "🔍 테스트 방법:"
echo "1. Chrome에서 Ctrl+Shift+Delete → 전체 캐시 삭제"
echo "2. Chrome 완전 재시작"
echo "3. http://139.150.11.99/login 접속"
echo "4. admin / admin123 로그인"
echo "5. 설정 페이지 이동 → 사이드바 1개만 확인"
echo ""
echo "📝 Git 커밋:"
echo "cd /root/uvis"
echo "git add frontend/src/pages/OrdersPage.tsx"
echo 'git commit -m "fix(frontend): OrdersPage JSX syntax"'
echo "git push origin genspark_ai_developer"
echo ""
