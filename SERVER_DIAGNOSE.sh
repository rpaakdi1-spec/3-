#!/bin/bash
# ===== 서버 진단 및 수정 스크립트 =====
# /root/uvis 에서 실행: bash SERVER_DIAGNOSE.sh

set -e
cd /root/uvis

echo "=============================="
echo "1. 현재 컨테이너 상태 확인"
echo "=============================="
docker compose ps

echo ""
echo "=============================="
echo "2. 백엔드 컨테이너 최근 로그 (오류 포함)"
echo "=============================="
docker compose logs backend --tail=50 2>&1 | tail -60

echo ""
echo "=============================="
echo "3. 백엔드 직접 연결 테스트"
echo "=============================="
curl -s -m 5 http://localhost:8000/api/v1/health 2>&1 || echo "⚠ 백엔드 직접 접속 실패"

echo ""
echo "=============================="
echo "4. 로그인 테스트"
echo "=============================="
LOGIN_RESULT=$(curl -s -m 10 -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" 2>&1)
echo "Login response: $LOGIN_RESULT"

echo ""
echo "=============================="
echo "5. Python 임포트 테스트 (컨테이너 내부)"  
echo "=============================="
docker compose exec backend python3 -c "
import sys
try:
    from app.api.location_rooms import router, _status
    print('✅ location_rooms 임포트 OK')
    
    from app.models.location_room import LocationRoom, RoomStatus
    r = type('R', (), {'status': RoomStatus.WAITING})()
    print(f'✅ _status(WAITING) = {_status(r)}')
    
    r2 = type('R', (), {'status': None})()
    print(f'✅ _status(None) = {_status(r2)}')
except RecursionError as e:
    print(f'❌ RecursionError: {e}')
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f'❌ Error: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 || echo "⚠ 컨테이너 exec 실패"

echo ""
echo "=============================="
echo "6. 컨테이너 내부 파일 확인"
echo "=============================="
docker compose exec backend head -30 /app/app/api/location_rooms.py 2>&1 || echo "⚠ 파일 확인 실패"

echo ""
echo "=============================="
echo "7. 강제 rebuild 및 재시작"
echo "=============================="
echo "실행할 명령어:"
echo "  docker compose build --no-cache backend"
echo "  docker compose up -d backend"
echo ""
read -p "강제 rebuild 실행? (y/N): " CONFIRM
if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    docker compose build --no-cache backend
    docker compose up -d backend
    sleep 15
    echo ""
    echo "재시작 후 로그:"
    docker compose logs backend --tail=30
    
    echo ""
    echo "로그인 재테스트:"
    TOKEN=$(curl -s -m 10 -X POST http://localhost:8000/api/v1/auth/login \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=admin&password=admin123" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','NO_TOKEN'))" 2>/dev/null)
    
    if [ -z "$TOKEN" ] || [ "$TOKEN" = "NO_TOKEN" ]; then
        echo "❌ 토큰 획득 실패 - 로그 확인 필요"
    else
        echo "✅ 토큰 획득 성공"
        
        echo ""
        echo "방 생성 테스트:"
        curl -s -X POST http://localhost:8000/api/v1/rooms \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer $TOKEN" \
          -d '{"title":"테스트 방","hours_valid":24}' | python3 -m json.tool
    fi
fi

