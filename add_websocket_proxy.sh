#!/bin/bash

cat << 'EOF'
=== Nginx WebSocket 프록시 추가 ===

다음 명령어를 실행하세요:

cd /root/uvis/frontend

# 현재 nginx.conf 백업
cp nginx.conf nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# nginx.conf에 WebSocket 블록 추가 (location /api/v1/ 블록 바로 앞에)
# sed를 사용해서 자동으로 추가

# 1. /api/v1/ 블록을 찾아서 그 앞에 WebSocket 블록 삽입
sed -i '/location \/api\/v1\/ {/i \        # WebSocket endpoints\n        location /api/v1/ws/ {\n            proxy_pass http://backend:8000/api/v1/ws/;\n            proxy_http_version 1.1;\n            proxy_set_header Upgrade $http_upgrade;\n            proxy_set_header Connection "upgrade";\n            proxy_set_header Host $host;\n            proxy_set_header X-Real-IP $remote_addr;\n            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n            proxy_set_header X-Forwarded-Proto $scheme;\n            \n            # WebSocket long timeout\n            proxy_connect_timeout 7d;\n            proxy_send_timeout 7d;\n            proxy_read_timeout 7d;\n        }\n' nginx.conf

# 2. 변경 확인
echo "=== 추가된 WebSocket 블록 확인 ==="
grep -A 15 "location /api/v1/ws/" nginx.conf

# 3. 배포
docker cp nginx.conf uvis-frontend:/etc/nginx/nginx.conf
docker exec uvis-frontend nginx -t
docker exec uvis-frontend nginx -s reload

echo ""
echo "✅ WebSocket 프록시 추가 완료!"
echo "브라우저를 새로고침(Ctrl+F5)하세요!"
EOF

