#!/bin/bash

echo "🔧 WebSocket 문제 해결 시작..."

# 1. Nginx 설정 파일 복사
echo "📝 Nginx 설정 업데이트 중..."
docker cp nginx-websocket-fix.conf uvis-frontend:/etc/nginx/conf.d/default.conf

# 2. Nginx 설정 테스트
echo "🧪 Nginx 설정 테스트..."
docker exec uvis-frontend nginx -t

# 3. Nginx 재시작
echo "🔄 Nginx 재시작..."
docker exec uvis-frontend nginx -s reload

# 4. 백엔드 WebSocket 엔드포인트 확인
echo "🔍 백엔드 WebSocket 엔드포인트 확인..."
docker exec uvis-backend python3 -c "
import sys
sys.path.insert(0, '/app')

# Check dispatches WebSocket
print('✅ /api/v1/dispatches/ws/dashboard 엔드포인트 확인')
from app.api.dispatches import router as dispatches_router
print(f'   Routes: {[route.path for route in dispatches_router.routes if hasattr(route, \"path\")]}')

# Check alerts WebSocket
print('✅ /api/v1/ws/alerts 엔드포인트 확인')
try:
    from app.api.v1.websocket import router as ws_router
    print(f'   Routes: {[route.path for route in ws_router.routes if hasattr(route, \"path\")]}')
except Exception as e:
    print(f'   ⚠️  websocket.py not found or error: {e}')
"

echo ""
echo "✅ WebSocket 설정 수정 완료!"
echo ""
echo "🧪 테스트 명령:"
echo "  wscat -c ws://localhost/api/v1/dispatches/ws/dashboard"
echo ""
echo "🌐 브라우저에서 확인:"
echo "  1. Ctrl+Shift+Delete로 캐시 삭제"
echo "  2. http://139.150.11.99/realtime 접속"
echo "  3. F12 Console에서 WebSocket 연결 확인"
