#!/bin/bash
# ======================================
# 완전 초기화 백엔드 수정 스크립트
# 서버에서: cd /root/uvis && bash DEFINITIVE_FIX.sh
# ======================================

set -e  # 오류시 중단
cd /root/uvis

echo "============================================"
echo " UVIS 백엔드 완전 수정 스크립트"
echo "============================================"

# 1. git 최신 코드 확인
echo ""
echo "[1/7] Git 상태 확인"
git log --oneline -3
echo "현재 파일 위치: $(git show HEAD:backend/app/api/location_rooms.py | grep 'def _status' -A 5 | head -6)"

# 2. _status 함수 확인
echo ""
echo "[2/7] _status() 함수 버전 확인 (컨테이너 외부 소스)"
grep -n "def _status\|return _status\|return room.status.value" backend/app/api/location_rooms.py | head -5

# 3. 기존 컨테이너 완전 제거
echo ""
echo "[3/7] 기존 백엔드 컨테이너 완전 제거"
docker compose stop backend 2>/dev/null || true
docker compose rm -f backend 2>/dev/null || true
docker rmi uvis-backend 2>/dev/null || true
echo "기존 이미지 제거 완료"

# 4. 완전 새 빌드 (캐시 없음)
echo ""
echo "[4/7] --no-cache 빌드 시작 (약 2-5분 소요)"
docker compose build --no-cache backend
echo "빌드 완료"

# 5. 컨테이너 시작
echo ""
echo "[5/7] 백엔드 컨테이너 시작"
docker compose up -d backend
echo "시작 명령 전송 완료, 30초 대기..."
sleep 30

# 6. 로그 확인
echo ""
echo "[6/7] 백엔드 시작 로그"
docker compose logs backend --tail=25

# 7. API 테스트
echo ""
echo "[7/7] API 테스트"

echo "  - 헬스체크..."
HEALTH=$(curl -s -m 10 http://localhost:8000/api/v1/health 2>/dev/null || echo "FAIL")
echo "  health: $HEALTH"

echo "  - 로그인..."
TOKEN_JSON=$(curl -s -m 15 -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" 2>/dev/null)
echo "  login response: $TOKEN_JSON" | head -c 200

TOKEN=$(echo "$TOKEN_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','NO_TOKEN'))" 2>/dev/null || echo "PARSE_FAIL")

if [ "$TOKEN" = "NO_TOKEN" ] || [ "$TOKEN" = "PARSE_FAIL" ] || [ -z "$TOKEN" ]; then
    echo ""
    echo "❌ 로그인 실패! 전체 백엔드 로그:"
    docker compose logs backend --tail=50 2>&1
    exit 1
fi

echo ""
echo "  ✅ 로그인 성공"
echo "  - 방 생성 테스트..."
ROOM_RESULT=$(curl -s -m 15 -X POST http://localhost:8000/api/v1/rooms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"수정 확인 테스트","hours_valid":1}' 2>/dev/null)

echo "$ROOM_RESULT" | python3 -m json.tool 2>/dev/null || echo "$ROOM_RESULT"

if echo "$ROOM_RESULT" | grep -q '"room_code"'; then
    echo ""
    echo "🎉 성공! POST /api/v1/rooms 정상 작동"
    echo ""
    echo "외부 URL 테스트:"
    ROOM_RESULT2=$(curl -s -m 15 -X POST http://139.150.11.99/api/v1/rooms \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"title":"외부 테스트","hours_valid":1}' 2>/dev/null)
    if echo "$ROOM_RESULT2" | grep -q '"room_code"'; then
        echo "✅ 외부 URL (139.150.11.99) 도 정상"
    else
        echo "⚠ 외부 URL 응답: $ROOM_RESULT2"
    fi
else
    echo ""
    echo "❌ 방 생성 실패: $ROOM_RESULT"
fi

