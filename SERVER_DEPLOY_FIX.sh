#!/bin/bash

# 🔥 Server Deployment Fix Script
# Git 충돌 해결 후 배포 스크립트
# 실행 방법: bash SERVER_DEPLOY_FIX.sh

echo "========================================="
echo "🔥 Critical Fix Deployment (with Git Fix)"
echo "========================================="
echo ""

# 1. 현재 디렉토리 확인
echo "1️⃣ 현재 디렉토리 확인..."
cd /root/uvis
pwd
echo ""

# 2. Git 충돌 해결 (downloaded script 제거)
echo "2️⃣ Git 충돌 해결..."
if [ -f "CRITICAL_FIX_DEPLOYMENT.sh" ]; then
    echo "📝 로컬 CRITICAL_FIX_DEPLOYMENT.sh 파일 발견 - 제거합니다..."
    rm -f CRITICAL_FIX_DEPLOYMENT.sh
    echo "✅ 파일 제거 완료"
fi
echo ""

# 3. Git Pull (clean)
echo "3️⃣ 최신 코드 가져오기..."
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer
echo "✅ 최신 코드 가져오기 완료"
echo ""

# 4. 수정 사항 확인
echo "4️⃣ 수정 사항 확인..."
echo ""
echo "📄 backend/app/api/dispatch_documents.py (line 20-22):"
sed -n '20,22p' backend/app/api/dispatch_documents.py
echo ""
echo "📄 frontend/src/App.tsx (line 70-75):"
sed -n '70,75p' frontend/src/App.tsx
echo ""

# 5. Python 구문 검증
echo "5️⃣ Python 구문 검증..."
python3 -m py_compile backend/app/api/dispatch_documents.py
if [ $? -eq 0 ]; then
    echo "✅ Python 구문 검증 OK"
else
    echo "❌ Python 구문 오류"
    exit 1
fi
echo ""

# 6. Backend 재빌드 (no-cache)
echo "6️⃣ Backend 재빌드..."
docker compose build --no-cache backend
if [ $? -ne 0 ]; then
    echo "❌ Backend 빌드 실패"
    exit 1
fi
echo "✅ Backend 빌드 완료"
echo ""

# 7. Backend 재시작
echo "7️⃣ Backend 재시작..."
docker compose up -d backend
echo "⏳ 30초 대기 (Backend 시작 대기 중)..."
sleep 30
echo ""

# 8. Backend 상태 확인
echo "8️⃣ Backend 상태 확인..."
docker compose ps | grep backend
echo ""

# 9. Backend 로그 확인 (에러 체크)
echo "9️⃣ Backend 로그 확인..."
echo "최근 로그 (에러 필터링):"
docker compose logs backend --tail=30 | grep -E "Application startup|Started|ERROR|Error|error|ModuleNotFoundError|Exception" | tail -20
echo ""

# 10. Backend Health Check
echo "🔟 Backend Health Check..."
for i in {1..3}; do
    echo "시도 $i/3..."
    HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/health)
    HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)
    BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Backend 정상 응답:"
        echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
        break
    else
        echo "⚠️  HTTP $HTTP_CODE - 재시도..."
        sleep 5
    fi
done
echo ""

# 11. Frontend 재빌드
echo "1️⃣1️⃣ Frontend 재빌드..."
docker compose build --no-cache frontend
if [ $? -ne 0 ]; then
    echo "❌ Frontend 빌드 실패"
    exit 1
fi
echo "✅ Frontend 빌드 완료"
echo ""

# 12. Frontend 재시작
echo "1️⃣2️⃣ Frontend 재시작..."
docker compose up -d frontend
echo "⏳ 10초 대기..."
sleep 10
echo ""

# 13. 전체 컨테이너 상태 확인
echo "1️⃣3️⃣ 전체 컨테이너 상태..."
docker compose ps
echo ""

# 14. Guest Delivery API 확인
echo "1️⃣4️⃣ Guest Delivery API 확인..."
echo "OpenAPI 스펙에서 /guest/delivery 엔드포인트 확인:"
curl -s http://localhost:8000/openapi.json | grep -o '"/api/v1/guest[^"]*"' | sort | uniq
echo ""

# 15. 최종 확인
echo "========================================="
echo "✅ 배포 완료!"
echo "========================================="
echo ""
echo "📊 배포 결과:"
echo "   - Backend: $(docker compose ps backend | grep backend | awk '{print $7}')"
echo "   - Frontend: $(docker compose ps frontend | grep frontend | awk '{print $7}')"
echo ""
echo "🔍 테스트 URL:"
echo "   - Main: http://139.150.11.99"
echo "   - Dashboard: http://139.150.11.99/dashboard"
echo "   - Dispatches: http://139.150.11.99/dispatches"
echo "   - API Docs: http://139.150.11.99/docs"
echo ""
echo "🧪 다음 테스트:"
echo "   1. 브라우저에서 http://139.150.11.99 접속"
echo "   2. 로그인 (admin 계정)"
echo "   3. 배차 관리 페이지 (/dispatches) 이동"
echo "   4. 배차 상세 모달 열기"
echo "   5. '기사 링크 생성' 버튼 확인"
echo "   6. 생성된 링크로 기사 페이지 테스트"
echo ""
echo "⚠️  브라우저 캐시 삭제 필수:"
echo "   - Ctrl+Shift+Delete (캐시 삭제)"
echo "   - 또는 시크릿 모드 (Ctrl+Shift+N)"
echo ""
echo "🐛 문제 발생 시 로그 확인:"
echo "   - Backend: docker compose logs backend --tail=100"
echo "   - Frontend: docker compose logs frontend --tail=50"
echo ""
