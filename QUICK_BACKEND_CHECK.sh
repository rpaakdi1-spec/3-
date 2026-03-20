#!/bin/bash
# 빠른 백엔드 진단 - 비인터랙티브
# 서버에서: cd /root/uvis && bash QUICK_BACKEND_CHECK.sh 2>&1 | tee /tmp/backend_debug.txt

cd /root/uvis

echo "=== STEP 1: 컨테이너 상태 ==="
docker compose ps

echo ""
echo "=== STEP 2: 백엔드 로그 전체 (최근 100줄) ==="
docker compose logs backend --tail=100 2>&1

echo ""
echo "=== STEP 3: location_rooms.py 컨테이너 내부 버전 확인 ==="
docker compose exec backend cat /app/app/api/location_rooms.py | grep -n "def _status\|return room.status\|return _status\|from app.api" | head -20

echo ""
echo "=== STEP 4: Python 직접 테스트 ==="
docker compose exec backend python3 << 'PYEOF'
import traceback
try:
    # 1. 임포트 테스트
    from app.api.location_rooms import _status, router
    print("[OK] location_rooms 임포트 성공")
    
    # 2. _status 함수 재귀 테스트
    from app.models.location_room import RoomStatus
    
    class FakeRoom:
        status = RoomStatus.WAITING
    
    import sys
    sys.setrecursionlimit(100)  # 재귀 빠르게 감지
    
    result = _status(FakeRoom())
    print(f"[OK] _status(WAITING) = {result}")
    
    class FakeRoom2:
        status = None
    
    result2 = _status(FakeRoom2())
    print(f"[OK] _status(None) = {result2}")
    
    print("[OK] 모든 테스트 통과!")
    
except RecursionError:
    print("[FAIL] RecursionError 발생 - _status() 무한 재귀!")
    traceback.print_exc()
except Exception as e:
    print(f"[FAIL] {type(e).__name__}: {e}")
    traceback.print_exc()
PYEOF

echo ""
echo "=== STEP 5: 로그인 테스트 ==="
curl -s -m 10 -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" 2>&1 || echo "curl 실패"

