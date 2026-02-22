#!/bin/bash

# 빠른 진단 및 수정 명령어 모음
# 서버에서 실행: bash quick_diagnosis.sh

echo "=================================================="
echo "배차 최적화 빠른 진단 도구"
echo "=================================================="
echo ""

echo "1️⃣ 컨테이너 상태 확인"
echo "────────────────────────────────────────────────"
docker ps | grep uvis
echo ""

echo "2️⃣ 최근 에러 로그 (30줄)"
echo "────────────────────────────────────────────────"
docker logs uvis-backend --tail 30 2>&1 | grep -i -A 3 "error\|exception\|typeerror"
echo ""

echo "3️⃣ Import 상태 확인"
echo "────────────────────────────────────────────────"
echo "현재 Import 라인 (22-24):"
sed -n '22,24p' /root/uvis/backend/app/api/dispatches.py
echo ""

echo "4️⃣ Optimizer 코드 확인"
echo "────────────────────────────────────────────────"
echo "optimize_dispatch 함수 (29-56):"
sed -n '29,56p' /root/uvis/backend/app/api/dispatches.py
echo ""

echo "5️⃣ API 간단 테스트"
echo "────────────────────────────────────────────────"
echo "테스트 중..."
RESULT=$(curl -s -X POST "http://localhost:8000/api/v1/dispatches/optimize" \
  -H "Content-Type: application/json" \
  -d '{ "order_ids": [1], "vehicle_ids": [], "dispatch_date": "2026-02-19" }')

if echo "$RESULT" | grep -q '"success"'; then
    echo "✅ API 정상 작동!"
    echo "$RESULT" | jq .
else
    echo "❌ API 에러 발생!"
    echo "$RESULT" | jq .
fi
echo ""

echo "=================================================="
echo "진단 완료"
echo "=================================================="
echo ""

# 문제 감지
HAS_ERROR=0

# Import 확인
if ! grep -q "AdvancedDispatchOptimizationService" /root/uvis/backend/app/api/dispatches.py; then
    echo "⚠️ 경고: AdvancedDispatchOptimizationService import 누락"
    HAS_ERROR=1
fi

# 함수 호출 확인
if grep -q "optimizer.optimize_dispatch(" /root/uvis/backend/app/api/dispatches.py; then
    if ! grep -q "optimizer.optimize_dispatch_cvrptw(" /root/uvis/backend/app/api/dispatches.py; then
        echo "⚠️ 경고: optimize_dispatch_cvrptw 함수 호출 없음"
        HAS_ERROR=1
    fi
fi

if [ $HAS_ERROR -eq 1 ]; then
    echo ""
    echo "🔧 수정 명령어:"
    echo ""
    echo "# 자동 수정 스크립트 실행:"
    echo "bash /root/server_fix_optimization.sh"
    echo ""
    echo "# 또는 파일 교체:"
    echo "# (로컬에서) scp /home/user/webapp/backend/app/api/dispatches.py root@139.150.11.99:/root/uvis/backend/app/api/"
    echo "# (서버에서) cd /root/uvis && docker restart uvis-backend"
else
    echo "✅ 파일 상태 정상!"
    echo ""
    
    # API 테스트 결과 확인
    if echo "$RESULT" | grep -q '"success".*true'; then
        echo "✅ 모든 시스템 정상 작동 중!"
    else
        echo "⚠️ 파일은 정상이지만 API에서 에러 발생"
        echo "   로그를 확인하세요: docker logs uvis-backend --tail 50"
    fi
fi

echo ""
echo "=================================================="
echo "자세한 문서: TROUBLESHOOTING.md"
echo "=================================================="
