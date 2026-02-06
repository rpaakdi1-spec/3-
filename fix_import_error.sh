#!/bin/bash

# UVIS - Import Error 긴급 수정
# mobile_enhanced.py의 get_current_user import 오류 해결

set -e

echo "=================================================="
echo "  Import Error 긴급 수정"
echo "=================================================="
echo ""

cd /root/uvis

echo "=== 1단계: 최신 코드 가져오기 ==="
git fetch origin genspark_ai_developer
git reset --hard origin/genspark_ai_developer
echo "✅ 최신 코드로 업데이트 완료"
echo ""

echo "=== 2단계: Import 확인 ==="
echo "수정된 import 문:"
grep -A2 "from app.core.database import get_db" backend/app/api/v1/mobile_enhanced.py
echo ""

echo "=== 3단계: Python 캐시 삭제 ==="
find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find backend -name "*.pyc" -delete 2>/dev/null || true
echo "✅ 캐시 삭제 완료"
echo ""

echo "=== 4단계: 백엔드 재시작 ==="
docker-compose restart backend
echo "✅ 백엔드 재시작 완료"
echo ""

echo "⏳ 백엔드 시작 대기 중... (40초)"
sleep 40
echo ""

echo "=== 5단계: 헬스 체크 ==="
for i in {1..5}; do
    echo "시도 $i/5..."
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "✅ 백엔드 정상 시작!"
        curl http://localhost:8000/health
        echo ""
        break
    else
        if [ $i -lt 5 ]; then
            echo "⏳ 10초 후 재시도..."
            sleep 10
        else
            echo "❌ 백엔드 시작 실패. 로그 확인 필요."
            docker logs uvis-backend --tail 30
            exit 1
        fi
    fi
done
echo ""

echo "=== 6단계: Phase 8 엔드포인트 확인 ==="
curl -s http://localhost:8000/openapi.json | grep -o '"/api/v1/billing/enhanced/[^"]*"' | sort | uniq | sed 's/"//g'
echo ""

echo "=================================================="
echo "  ✅ 수정 완료!"
echo "=================================================="
echo ""
echo "이제 Phase 8 API 테스트를 진행하세요:"
echo ""
echo "  TOKEN=\$(curl -s -X POST http://localhost:8000/api/v1/auth/login \\"
echo "    -H \"Content-Type: application/x-www-form-urlencoded\" \\"
echo "    -d \"username=admin&password=admin123\" | \\"
echo "    grep -o '\"access_token\":\"[^\"]*' | cut -d'\"' -f4)"
echo ""
echo "  curl -X GET \"http://localhost:8000/api/v1/billing/enhanced/settlement-approval\" \\"
echo "    -H \"Authorization: Bearer \$TOKEN\""
echo ""
