#!/bin/bash
# WebSocket 403 진단 스크립트

echo "======================================"
echo "WebSocket 403 진단 시작"
echo "======================================"
echo ""

# 1. Nginx WebSocket 설정 확인
echo "=== 1. Nginx WebSocket 프록시 설정 확인 ==="
docker exec uvis-frontend cat /etc/nginx/nginx.conf | grep -A 30 "location /api/v1/ws"
echo ""

# 2. Backend main.py에서 CORS 설정 확인
echo "=== 2. Backend CORS 설정 확인 ==="
docker exec uvis-backend cat /app/app/main.py | grep -B 5 -A 20 "CORSMiddleware\|add_middleware"
echo ""

# 3. Backend 앱 라우터 등록 확인
echo "=== 3. WebSocket 라우터 등록 확인 ==="
docker exec uvis-backend cat /app/app/main.py | grep -B 3 -A 3 "websocket\|ws"
echo ""

# 4. 현재 WebSocket 엔드포인트 코드 확인 (첫 50줄)
echo "=== 4. WebSocket 엔드포인트 현재 코드 (첫 50줄) ==="
docker exec uvis-backend cat /app/app/api/v1/websocket.py | head -50
echo ""

# 5. 토큰 검증 로직 확인
echo "=== 5. JWT 토큰 검증 설정 확인 ==="
docker exec uvis-backend python3 -c "
try:
    from app.core.config import settings
    print(f'SECRET_KEY: {settings.SECRET_KEY[:20]}...')
    print(f'ALGORITHM: {settings.ALGORITHM}')
    print(f'ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}')
except Exception as e:
    print(f'Error: {e}')
"
echo ""

# 6. 최근 백엔드 WebSocket 로그 확인
echo "=== 6. 최근 WebSocket 연결 로그 ==="
docker logs uvis-backend --tail 100 | grep -E "WebSocket|ws/dashboard|403|✅|🔵" | tail -20
echo ""

echo "======================================"
echo "진단 완료"
echo "======================================"
echo ""
echo "📋 확인사항:"
echo "1. Nginx가 /api/v1/ws/ 경로를 backend로 프록시하는지"
echo "2. Backend CORS 설정이 WebSocket을 허용하는지"
echo "3. WebSocket 라우터가 main.py에 제대로 등록되어 있는지"
echo "4. JWT 토큰 검증이 올바르게 설정되어 있는지"
echo ""
