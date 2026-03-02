#!/bin/bash
# Check semi-auto dispatch API

echo "====================================="
echo "Semi-Auto Dispatch API 진단"
echo "====================================="
echo ""

echo "1️⃣ 백엔드 로그 확인 (startup):"
echo "---"
docker compose -f /root/uvis/docker-compose.yml logs backend --tail=100 | grep -E "(semi|dispatch|startup|Starting|route)"
echo ""

echo "2️⃣ API 경로 테스트 (내부):"
echo "---"
docker compose -f /root/uvis/docker-compose.yml exec backend curl -s http://localhost:8000/api/v1/semi-auto-dispatch/orders/1/suggest-vehicles
echo ""

echo "3️⃣ API 문서 확인:"
echo "---"
echo "Open: http://139.150.11.99:8000/docs"
echo "Look for: /api/v1/semi-auto-dispatch/orders/{order_id}/suggest-vehicles"
echo ""

echo "4️⃣ 등록된 라우터 확인:"
echo "---"
docker compose -f /root/uvis/docker-compose.yml exec backend python -c "
from app.api import semi_auto_dispatch
print('✅ semi_auto_dispatch router imported successfully')
print(f'Router prefix: {semi_auto_dispatch.router.prefix if hasattr(semi_auto_dispatch.router, \"prefix\") else \"No prefix\"}')
print(f'Routes: {len(semi_auto_dispatch.router.routes)} routes')
for route in semi_auto_dispatch.router.routes:
    print(f'  - {route.path} [{route.methods if hasattr(route, \"methods\") else \"N/A\"}]')
"
echo ""

echo "====================================="
echo "✅ 진단 완료"
echo "====================================="
