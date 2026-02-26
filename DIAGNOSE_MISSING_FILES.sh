#!/bin/bash
# 빌드 파일 누락 진단 스크립트

echo "🔍 빌드 파일 누락 원인 진단..."
echo ""

cd /root/uvis

echo "=== 1. 로컬 빌드 디렉토리 확인 ==="
ls -lh frontend/dist/assets/*DispatchRules*.js 2>&1 | head -5

echo ""
echo "=== 2. 로컬 빌드의 전체 JS 파일 개수 ==="
ls frontend/dist/assets/*.js 2>/dev/null | wc -l

echo ""
echo "=== 3. 컨테이너의 전체 JS 파일 개수 ==="
docker exec uvis-frontend ls /usr/share/nginx/html/assets/*.js 2>/dev/null | wc -l

echo ""
echo "=== 4. 로컬에 rule_update 있는지 확인 ==="
grep -l "rule_update" frontend/dist/assets/*.js 2>/dev/null || echo "❌ 로컬 빌드에도 rule_update 없음!"

echo ""
echo "=== 5. 로컬 소스코드 확인 (dispatch-rules.ts) ==="
if [ -f "frontend/src/api/dispatch-rules.ts" ]; then
  grep -A10 "async update" frontend/src/api/dispatch-rules.ts | head -15
else
  echo "❌ dispatch-rules.ts 파일 없음"
fi

echo ""
echo "=== 6. 최근 빌드 시간 확인 ==="
stat -c "%y %n" frontend/dist/index.html 2>/dev/null || echo "❌ 빌드 파일 없음"

echo ""
echo "=========================================="
echo "📋 진단 요약"
echo "=========================================="
