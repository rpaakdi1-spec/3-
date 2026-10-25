#!/bin/bash
# 백엔드 강제 수정 스크립트
# 서버에서: cd /root/uvis && bash FIX_BACKEND.sh

cd /root/uvis

echo "=== [1/6] 현재 상태 ==="
docker compose ps | grep backend

echo ""
echo "=== [2/6] 최근 오류 로그 ==="
docker compose logs backend --tail=30 2>&1 | grep -E "Error|error|Exception|Traceback|Warning|WARN" | head -20

echo ""
echo "=== [3/6] 컨테이너 내부 파일 버전 확인 ==="
docker compose exec backend grep -n "def _status" /app/app/api/location_rooms.py 2>/dev/null && \
docker compose exec backend sed -n '150,158p' /app/app/api/location_rooms.py 2>/dev/null || \
echo "⚠ 파일 확인 실패 (컨테이너가 실행 중이 아닐 수 있음)"

echo ""
echo "=== [4/6] 전체 로그 확인 (RecursionError 검색) ==="
docker compose logs backend 2>&1 | grep -A5 "RecursionError\|ImportError\|SyntaxError\|ModuleNotFoundError" | head -30

echo ""
echo "=== [5/6] 강제 --no-cache 빌드 ==="
docker compose build --no-cache backend 2>&1 | tail -20

echo ""
echo "=== [6/6] 재시작 및 테스트 ==="
docker compose up -d backend
echo "30초 대기..."
sleep 30

echo "--- 로그 확인 ---"
docker compose logs backend --tail=20

echo ""
echo "--- 로그인 테스트 ---"
TOKEN=$(curl -s -m 15 -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('access_token', 'NO_TOKEN_IN_RESPONSE'))
except Exception as e:
    print(f'JSON_ERROR: {e}')
" 2>/dev/null)

if [ -z "$TOKEN" ] || [[ "$TOKEN" == *"ERROR"* ]] || [ "$TOKEN" = "NO_TOKEN_IN_RESPONSE" ]; then
    echo "❌ 로그인 실패: $TOKEN"
    echo ""
    echo "백엔드 로그 전체:"
    docker compose logs backend --tail=50 2>&1
else
    echo "✅ 로그인 성공"
    echo ""
    echo "--- 방 생성 테스트 ---"
    RESULT=$(curl -s -m 15 -X POST http://localhost:8000/api/v1/rooms \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"title":"테스트 방","hours_valid":24}' 2>/dev/null)
    echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
    
    if echo "$RESULT" | grep -q '"room_code"'; then
        echo ""
        echo "🎉 성공! 방 생성이 정상적으로 동작합니다."
    else
        echo ""
        echo "❌ 방 생성 실패"
    fi
fi

