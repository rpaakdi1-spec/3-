#!/bin/bash

# UVIS Phase 8 - 파일명 오타 긴급 수정 스크립트
# billing_enchanced.py → billing_enhanced.py

set -e

echo "=================================================="
echo "  Phase 8 긴급 수정: 파일명 오타 수정"
echo "=================================================="
echo ""

REPO_DIR="/root/uvis"
cd "$REPO_DIR"

echo "📍 현재 위치: $(pwd)"
echo ""

# 1. 파일명 확인
echo "=== 1단계: 현재 파일 확인 ==="
ls -la backend/app/api/v1/billing_en*.py 2>/dev/null || echo "billing_en*.py 파일 없음"
echo ""

# 2. 오타 파일 수정
echo "=== 2단계: 파일명 오타 수정 ==="
if [ -f "backend/app/api/v1/billing_enchanced.py" ]; then
    echo "⚠️  오타 파일 발견: billing_enchanced.py"
    mv backend/app/api/v1/billing_enchanced.py backend/app/api/v1/billing_enhanced.py
    echo "✅ 파일명 수정 완료: billing_enhanced.py"
else
    echo "✅ 파일명이 이미 올바름: billing_enhanced.py"
fi
echo ""

# 3. Import 문 확인 및 수정
echo "=== 3단계: Import 문 확인 ==="
if grep -q "billing_enchanced" backend/main.py 2>/dev/null; then
    echo "⚠️  main.py에서 오타 발견! 수정 중..."
    sed -i 's/billing_enchanced/billing_enhanced/g' backend/main.py
    echo "✅ main.py 수정 완료"
else
    echo "✅ main.py 이미 올바름"
fi
echo ""

# 4. 전체 파일 검색
echo "=== 4단계: 전체 파일에서 오타 검색 ==="
TYPO_FILES=$(grep -r "billing_enchanced" backend/ 2>/dev/null | wc -l)
if [ "$TYPO_FILES" -gt 0 ]; then
    echo "⚠️  오타 발견: $TYPO_FILES 개 파일"
    grep -r "billing_enchanced" backend/ 2>/dev/null || true
    echo ""
    echo "자동 수정 중..."
    find backend -type f -name "*.py" -exec sed -i 's/billing_enchanced/billing_enhanced/g' {} +
    echo "✅ 모든 파일 수정 완료"
else
    echo "✅ 오타 없음"
fi
echo ""

# 5. Python 캐시 삭제
echo "=== 5단계: Python 캐시 삭제 ==="
find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find backend -name "*.pyc" -delete 2>/dev/null || true
echo "✅ 캐시 삭제 완료"
echo ""

# 6. Git 상태 확인
echo "=== 6단계: Git 상태 ==="
git status --short
echo ""

# 7. 변경사항 커밋
if [ -n "$(git status --porcelain)" ]; then
    echo "=== 7단계: 변경사항 커밋 ==="
    git add -A
    git commit -m "fix(backend): Correct typo billing_enchanced -> billing_enhanced"
    echo "✅ 커밋 완료"
else
    echo "=== 7단계: 변경사항 없음 ==="
fi
echo ""

# 8. 백엔드 재시작
echo "=== 8단계: 백엔드 재시작 ==="
docker-compose restart backend
echo "✅ 백엔드 재시작 완료"
echo ""

# 9. 대기
echo "⏳ 백엔드 시작 대기 중... (30초)"
sleep 30
echo ""

# 10. 헬스 체크
echo "=== 9단계: 헬스 체크 ==="
HEALTH_STATUS=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*' | cut -d'"' -f4)
if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ 백엔드: $HEALTH_STATUS"
else
    echo "❌ 백엔드 상태 확인 실패"
    exit 1
fi
echo ""

# 11. API 엔드포인트 확인
echo "=== 10단계: Phase 8 엔드포인트 확인 ==="
echo "OpenAPI에 등록된 Phase 8 엔드포인트:"
curl -s http://localhost:8000/openapi.json | grep -o '"/api/v1/billing/enhanced/[^"]*"' | sort | uniq | sed 's/"//g'
echo ""

echo "=================================================="
echo "  ✅ 수정 완료!"
echo "=================================================="
echo ""
echo "다음 명령어로 API를 테스트하세요:"
echo ""
echo "  TOKEN=\$(curl -s -X POST http://localhost:8000/api/v1/auth/login \\"
echo "    -H \"Content-Type: application/x-www-form-urlencoded\" \\"
echo "    -d \"username=admin&password=admin123\" | \\"
echo "    grep -o '\"access_token\":\"[^\"]*' | cut -d'\"' -f4)"
echo ""
echo "  curl -X GET \"http://localhost:8000/api/v1/billing/enhanced/settlement-approval\" \\"
echo "    -H \"Authorization: Bearer \$TOKEN\""
echo ""
echo "  curl -X GET \"http://localhost:8000/api/v1/billing/enhanced/payment-reminder\" \\"
echo "    -H \"Authorization: Bearer \$TOKEN\""
echo ""
echo "  curl -X GET \"http://localhost:8000/api/v1/billing/enhanced/export\" \\"
echo "    -H \"Authorization: Bearer \$TOKEN\""
echo ""
