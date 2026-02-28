#!/bin/bash
# 서버에서 실행할 빌드 검증 스크립트

echo "=========================================="
echo "서버 빌드 파일 검증"
echo "=========================================="
echo ""

echo "1️⃣ 서버 Git 상태"
echo "-------------------"
cd /root/uvis
git log --oneline -5 | head -5
echo ""

echo "2️⃣ 로컬 소스 코드 확인"
echo "-------------------"
echo "UvisFleetStats.tsx 핵심 로직:"
grep -A 5 "Calculate statistics" frontend/src/components/vehicles/UvisFleetStats.tsx | head -10
echo ""

echo "3️⃣ 빌드된 JavaScript 파일 검색"
echo "-------------------"
docker exec uvis-frontend sh -c '
cd /usr/share/nginx/html/assets
echo "=== UVIS 관련 빌드 파일 검색 ==="
for f in *.js; do
  if grep -q "UVIS.*실시간.*통계\|운행.*차량\|UvisFleetStats" "$f" 2>/dev/null; then
    echo ""
    echo "📄 파일: $f"
    ls -lh "$f" | awk "{print \"   시간:\", \$6, \$7, \$8, \"크기:\", \$5}"
    
    # 최신 로직 확인
    if grep -q "activeCount" "$f" 2>/dev/null; then
      if grep -q "active_vehicles" "$f" 2>/dev/null; then
        echo "   ✅ activeCount 사용 (최신 로직)"
      fi
    fi
    
    # 이전 로직 확인  
    if grep -q "engineOnCount" "$f" 2>/dev/null; then
      if grep -q "engine_on_ratio.*50" "$f" 2>/dev/null; then
        echo "   ❌ engineOnCount 사용 (이전 버그 로직)"
      fi
    fi
    
    # 실제 코드 샘플 추출 (minified 코드)
    echo "   코드 샘플:"
    grep -o "activeCount[^,]*" "$f" 2>/dev/null | head -1 | sed "s/^/     /"
    grep -o "engineOnCount[^,]*" "$f" 2>/dev/null | head -1 | sed "s/^/     /"
  fi
done
'
echo ""

echo "4️⃣ DashboardPage 빌드 파일"
echo "-------------------"
docker exec uvis-frontend sh -c '
cd /usr/share/nginx/html/assets
for f in DashboardPage*.js; do
  if [ -f "$f" ]; then
    echo "📄 $f"
    ls -lh "$f" | awk "{print \"   시간:\", \$6, \$7, \$8, \"크기:\", \$5}"
    
    if grep -q "UvisFleetStats" "$f" 2>/dev/null; then
      echo "   ✅ UvisFleetStats 컴포넌트 포함됨"
    else
      echo "   ⚠️  UvisFleetStats 컴포넌트 없음"
    fi
  fi
done
'
echo ""

echo "5️⃣ API 응답 테스트"
echo "-------------------"
curl -s "http://localhost:8000/api/v1/vehicles/analytics/fleet?start_date=2026-02-21&end_date=2026-02-28" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f'Total vehicles: {d[\"total_vehicles\"]}')
    print(f'Active vehicles: {d[\"active_vehicles\"]}')
    print(f'Vehicle stats: {len(d[\"vehicle_stats\"])}')
    
    # 이전 로직 시뮬레이션
    engine_on_count = sum(1 for v in d['vehicle_stats'] if v.get('engine_on_ratio', 0) > 50)
    print(f'')
    print(f'✅ 최신 로직이 사용할 값: {d[\"active_vehicles\"]}')
    print(f'❌ 이전 로직이 사용할 값: {engine_on_count}')
except Exception as e:
    print(f'Error: {e}')
"
echo ""

echo "6️⃣ 빌드 날짜 확인"
echo "-------------------"
echo "Frontend 이미지 생성 시간:"
docker inspect uvis-frontend --format='{{.Created}}' | cut -d'.' -f1
echo ""

echo "index.html 빌드 시간:"
docker exec uvis-frontend stat /usr/share/nginx/html/index.html | grep Modify
echo ""

echo "=========================================="
echo "검증 완료"
echo "=========================================="
