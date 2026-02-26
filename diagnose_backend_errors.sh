#!/bin/bash
echo "=== 1. Vehicle API Route Check ==="
ssh root@139.150.11.99 "docker exec uvis-backend cat /app/app/api/vehicles.py | head -50"

echo ""
echo "=== 2. Check WebSocket Authentication Logic ==="
ssh root@139.150.11.99 "docker exec uvis-backend grep -A 20 'async def websocket_endpoint' /app/app/api/v1/websocket.py"

echo ""
echo "=== 3. Find ChunkedIteratorResult Error Location ==="
ssh root@139.150.11.99 "docker exec uvis-backend grep -rn 'broadcast.*vehicle' /app/app/api --include='*.py' | head -10"

echo ""
echo "=== 4. Test Vehicle API With Trailing Slash ==="
TOKEN=$(ssh root@139.150.11.99 "curl -s -X POST http://139.150.11.99/api/auth/login -H 'Content-Type: application/x-www-form-urlencoded' -d 'username=admin&password=admin123' | python3 -c \"import sys,json;print(json.load(sys.stdin)['access_token'])\"")
ssh root@139.150.11.99 "curl -X GET http://139.150.11.99/api/v1/vehicles/ -H 'Authorization: Bearer $TOKEN' | python3 -m json.tool | head -20"
