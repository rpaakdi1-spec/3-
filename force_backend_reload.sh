#!/bin/bash

echo "================================================================================"
echo "🔄 Force Backend Code Reload - 백엔드 코드 강제 리로드"
echo "================================================================================"

set -e  # Exit on error

echo ""
echo "📦 Step 1: Remove Python bytecode cache"
echo "--------------------------------------------------------------------------------"
docker exec uvis-backend find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
docker exec uvis-backend find /app -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Python cache cleared"

echo ""
echo "🔄 Step 2: Restart backend container (full stop/start)"
echo "--------------------------------------------------------------------------------"
docker-compose -f docker-compose.prod.yml stop backend
echo "Waiting 5 seconds..."
sleep 5
docker-compose -f docker-compose.prod.yml start backend
echo "✅ Backend restarted"

echo ""
echo "⏳ Step 3: Wait for backend to be ready (30 seconds)"
echo "--------------------------------------------------------------------------------"
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""
echo "✅ Wait complete"

echo ""
echo "🏥 Step 4: Health check"
echo "--------------------------------------------------------------------------------"
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)
if [ "$HTTP_CODE" == "200" ]; then
    echo "✅ Backend is healthy (HTTP $HTTP_CODE)"
else
    echo "⚠️  Backend returned HTTP $HTTP_CODE"
fi

echo ""
echo "📝 Step 5: Check if code changes are loaded"
echo "--------------------------------------------------------------------------------"
echo "Checking orders.py modification time in container..."
docker exec uvis-backend stat /app/app/api/orders.py | grep Modify || echo "File stat check skipped"

echo ""
echo "================================================================================"
echo "✅ Backend code reload complete!"
echo ""
echo "Next steps:"
echo "  1. Run the test: ./test_order_update_comprehensive.sh"
echo "  2. Check logs: docker logs uvis-backend --tail 50"
echo "================================================================================"
