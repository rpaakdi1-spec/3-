#!/bin/bash
# 서버에서 직접 실행할 수 있는 수정 명령어들
# 이 파일의 내용을 복사해서 서버에서 실행하세요

echo "╔════════════════════════════════════════════════════════╗"
echo "║  UVIS 대시보드 에러 수정 - 단계별 실행 가이드        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

cat << 'EOF'

═══════════════════════════════════════════════════════════
🔧 1단계: 차량 API 307 리다이렉트 수정 (1분)
═══════════════════════════════════════════════════════════

cd /root/uvis/frontend

# 백업
cp nginx.conf nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# 현재 설정 확인
echo "현재 nginx.conf 내용:"
grep -A 20 "location /api/v1/ws/" nginx.conf | head -25

# 리다이렉트 규칙이 있는지 확인
if grep -q "rewrite.*vehicles.*vehicles/" nginx.conf; then
    echo "✅ 이미 리다이렉트 규칙이 있습니다"
else
    echo "❌ 리다이렉트 규칙이 없습니다. 추가가 필요합니다."
    echo ""
    echo "다음 명령어를 실행하세요:"
    echo "====================================="
    cat << 'FIXCMD'
cd /root/uvis/frontend

# nginx.conf에 리다이렉트 규칙 추가
sed -i '/location \/api\/v1\/ws\// i\        # Fix vehicle API redirect - add trailing slash\n        rewrite ^/api/v1/vehicles$ /api/v1/vehicles/ permanent;\n' nginx.conf

# 확인
echo "추가된 설정:"
grep -B 1 -A 1 "rewrite.*vehicles" nginx.conf

# 배포
docker cp nginx.conf uvis-frontend:/etc/nginx/nginx.conf
docker exec uvis-frontend nginx -t
docker exec uvis-frontend nginx -s reload

echo ""
echo "✅ 차량 API 리다이렉트 수정 완료!"
FIXCMD
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🧪 2단계: API 테스트 (2분)"
echo "═══════════════════════════════════════════════════════════"
echo ""

cat << 'TESTCMD'
# 토큰 발급
echo "1️⃣  토큰 발급 중..."
TOKEN=$(curl -s -X POST http://139.150.11.99/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | \
  python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

echo "✅ 토큰: ${TOKEN:0:30}..."
echo ""

# 차량 API 테스트 (307 → 200 확인)
echo "2️⃣  차량 API 테스트..."
echo "----------------------------------------"
curl -X GET "http://139.150.11.99/api/v1/vehicles" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP Status: %{http_code}\n" \
  -s | head -20

echo ""
echo "❗ HTTP Status가 200이면 성공, 307이면 아직 수정 필요"
echo ""

# 대시보드 통계 테스트
echo "3️⃣  대시보드 통계 API 테스트..."
echo "----------------------------------------"
curl -X GET "http://139.150.11.99/api/v1/dispatches/stats/summary" \
  -H "Authorization: Bearer $TOKEN" \
  -s | python3 -m json.tool

echo ""

# 백엔드 에러 확인
echo "4️⃣  백엔드 에러 확인..."
echo "----------------------------------------"
echo "최근 에러 (최근 50줄):"
docker logs uvis-backend --tail 50 | grep -E "Error|Exception" | tail -10

echo ""
echo "WebSocket 403 에러:"
docker logs uvis-backend --tail 50 | grep "403" | tail -5

TESTCMD

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🔍 3단계: WebSocket 진단 (선택사항)"
echo "═══════════════════════════════════════════════════════════"
echo ""

cat << 'WSCMD'
# WebSocket 엔드포인트 확인
echo "WebSocket 구현 확인:"
docker exec uvis-backend cat /app/app/api/v1/websocket.py | head -80

echo ""
echo "WebSocket 라우트 확인:"
docker exec uvis-backend grep -rn "@router.websocket" /app/app/api/v1 --include="*.py" -B 2 -A 10
WSCMD

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 4단계: 브라우저 테스트"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. 브라우저에서 Ctrl + Shift + F5 (강제 새로고침)"
echo "2. F12 → Console 확인"
echo "   - 422 에러 사라졌는지 확인"
echo "   - WebSocket 403은 여전히 있을 수 있음 (정상)"
echo "3. F12 → Network 확인"
echo "   - GET /api/v1/vehicles → 200 OK (307 아님)"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

EOF
