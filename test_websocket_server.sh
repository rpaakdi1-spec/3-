#!/bin/bash

echo "================================================================"
echo "🔍 WebSocket 연결 테스트 (서버 측)"
echo "================================================================"
echo ""

echo "1️⃣ wscat으로 Dashboard WebSocket 테스트 (10초간 수신):"
echo "────────────────────────────────────────────────────────────────"
echo "연결 중... ws://localhost/api/v1/dispatches/ws/dashboard"
timeout 10 wscat -c ws://localhost/api/v1/dispatches/ws/dashboard 2>&1 &
WSCAT_PID=$!
sleep 10
kill $WSCAT_PID 2>/dev/null
echo ""

echo "2️⃣ wscat으로 Alerts WebSocket 테스트 (10초간 수신):"
echo "────────────────────────────────────────────────────────────────"
echo "연결 중... ws://localhost/api/v1/dispatches/ws/alerts"
timeout 10 wscat -c ws://localhost/api/v1/dispatches/ws/alerts 2>&1 &
WSCAT_PID=$!
sleep 10
kill $WSCAT_PID 2>/dev/null
echo ""

echo "3️⃣ curl로 WebSocket Upgrade 요청:"
echo "────────────────────────────────────────────────────────────────"
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost/api/v1/dispatches/ws/dashboard 2>&1 | head -20
echo ""

echo "4️⃣ 백엔드로 직접 WebSocket 연결 (컨테이너 내부):"
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend sh -c "timeout 5 nc backend 8000 <<EOF
GET /api/v1/dispatches/ws/dashboard HTTP/1.1
Host: backend:8000
Connection: Upgrade
Upgrade: websocket
Sec-WebSocket-Version: 13
Sec-WebSocket-Key: test

EOF" 2>&1 | head -15
echo ""

echo "5️⃣ Nginx가 WebSocket을 백엔드로 프록시하는지 확인:"
echo "────────────────────────────────────────────────────────────────"
docker exec uvis-frontend nginx -T 2>&1 | grep -A 3 "proxy_set_header Upgrade"
echo ""

echo "================================================================"
echo "✅ 테스트 완료!"
echo "================================================================"
echo ""
echo "📋 결과 판단:"
echo "   • 1️⃣, 2️⃣에서 JSON 데이터 수신: ✅ 서버 정상"
echo "   • 3️⃣에서 HTTP 101 응답: ✅ Nginx 프록시 정상"
echo "   • 4️⃣에서 HTTP 101 응답: ✅ 백엔드 직접 연결 정상"
echo "   • 모두 성공했는데 브라우저 실패: 🔥 브라우저 캐시/CORS 문제"
echo ""
