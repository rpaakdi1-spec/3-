#!/bin/bash

# 🔥 Critical Fix Deployment Script
# 수정 사항:
# 1. backend/app/api/dispatch_documents.py - import 경로 수정 (app.core.auth → app.api.auth)
# 2. frontend/src/App.tsx - TemplateManagementPage 중복 선언 제거
#
# 실행 방법: bash CRITICAL_FIX_DEPLOYMENT.sh

echo "========================================="
echo "🔥 Critical Fix Deployment"
echo "========================================="
echo ""

# 1. 현재 디렉토리 확인
echo "1️⃣ 현재 디렉토리 확인..."
pwd
cd /root/uvis
pwd
echo ""

# 2. Git Pull
echo "2️⃣ 최신 코드 가져오기..."
git fetch origin genspark_ai_developer
git pull origin genspark_ai_developer
if [ $? -ne 0 ]; then
    echo "❌ Git pull 실패 - unstaged changes가 있을 수 있습니다"
    echo "📝 다음 명령어로 로컬 변경사항 처리:"
    echo "   git stash && git pull origin genspark_ai_developer && git stash pop"
    echo ""
    echo "또는 로컬 변경사항 버리기:"
    echo "   git reset --hard HEAD && git pull origin genspark_ai_developer"
    exit 1
fi
echo "✅ 최신 코드 가져오기 완료"
echo ""

# 3. 수정 사항 확인
echo "3️⃣ 수정 사항 확인..."
echo "backend/app/api/dispatch_documents.py (line 21):"
sed -n '20,22p' backend/app/api/dispatch_documents.py
echo ""
echo "frontend/src/App.tsx (line 70-83):"
sed -n '70,83p' frontend/src/App.tsx
echo ""

# 4. Backend 재빌드 (no-cache)
echo "4️⃣ Backend 재빌드..."
docker compose build --no-cache backend
if [ $? -ne 0 ]; then
    echo "❌ Backend 빌드 실패"
    exit 1
fi
echo "✅ Backend 빌드 완료"
echo ""

# 5. Backend 재시작
echo "5️⃣ Backend 재시작..."
docker compose up -d backend
echo "⏳ 30초 대기..."
sleep 30
echo ""

# 6. Backend 상태 확인
echo "6️⃣ Backend 상태 확인..."
docker compose ps | grep backend
echo ""
echo "Backend 로그 확인:"
docker compose logs backend --tail=20 | grep -E "Application startup|ERROR|error|ModuleNotFoundError"
echo ""

# 7. Backend Health Check
echo "7️⃣ Backend Health Check..."
curl -s http://localhost:8000/api/v1/health | jq .
echo ""

# 8. Frontend 재빌드
echo "8️⃣ Frontend 재빌드..."
docker compose build --no-cache frontend
if [ $? -ne 0 ]; then
    echo "❌ Frontend 빌드 실패"
    exit 1
fi
echo "✅ Frontend 빌드 완료"
echo ""

# 9. Frontend 재시작
echo "9️⃣ Frontend 재시작..."
docker compose up -d frontend
echo "⏳ 10초 대기..."
sleep 10
echo ""

# 10. 전체 컨테이너 상태 확인
echo "🔟 전체 컨테이너 상태..."
docker compose ps
echo ""

# 11. 최종 확인
echo "========================================="
echo "✅ 배포 완료!"
echo "========================================="
echo ""
echo "🔍 테스트 URL:"
echo "   - Main: http://139.150.11.99"
echo "   - Dashboard: http://139.150.11.99/dashboard"
echo "   - Dispatches: http://139.150.11.99/dispatches"
echo "   - Guest Delivery: http://139.150.11.99/guest/delivery/{TOKEN}"
echo "   - API Docs: http://139.150.11.99/docs"
echo ""
echo "🧪 확인 사항:"
echo "   1. Backend가 Healthy 상태인지 확인"
echo "   2. Frontend가 정상 실행되는지 확인"
echo "   3. 브라우저에서 로그인 가능한지 확인"
echo "   4. 배차 페이지에서 기사 링크 생성 버튼 확인"
echo ""
echo "⚠️  브라우저 캐시 삭제 필수:"
echo "   - Ctrl+Shift+Delete (캐시 삭제)"
echo "   - 또는 시크릿 모드 (Ctrl+Shift+N)"
echo ""
