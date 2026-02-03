#!/bin/bash

echo "================================================================================"
echo "🛠️  Complete Backend Rebuild - Docker 이미지 재빌드 및 배포"
echo "================================================================================"

set -e  # Exit on error

echo ""
echo "⚠️  WARNING: This will rebuild the backend Docker image from scratch."
echo "This should fix any code synchronization issues."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "📦 Step 1: Stop backend container"
echo "--------------------------------------------------------------------------------"
docker-compose -f docker-compose.prod.yml stop backend
echo "✅ Backend stopped"

echo ""
echo "🗑️  Step 2: Remove backend container and image"
echo "--------------------------------------------------------------------------------"
docker-compose -f docker-compose.prod.yml rm -f backend
docker rmi uvis-backend:latest 2>/dev/null || echo "Image already removed or doesn't exist"
echo "✅ Cleanup complete"

echo ""
echo "🏗️  Step 3: Rebuild backend image (no cache)"
echo "--------------------------------------------------------------------------------"
docker-compose -f docker-compose.prod.yml build --no-cache backend
echo "✅ Image rebuilt"

echo ""
echo "🚀 Step 4: Start backend container"
echo "--------------------------------------------------------------------------------"
docker-compose -f docker-compose.prod.yml up -d backend
echo "✅ Backend started"

echo ""
echo "⏳ Step 5: Wait for backend to be ready (45 seconds)"
echo "--------------------------------------------------------------------------------"
for i in {1..45}; do
    echo -n "."
    sleep 1
done
echo ""
echo "✅ Wait complete"

echo ""
echo "🏥 Step 6: Health check"
echo "--------------------------------------------------------------------------------"
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)
if [ "$HTTP_CODE" == "200" ]; then
    echo "✅ Backend is healthy (HTTP $HTTP_CODE)"
else
    echo "⚠️  Backend returned HTTP $HTTP_CODE"
fi

echo ""
echo "📋 Step 7: Show recent logs"
echo "--------------------------------------------------------------------------------"
docker logs uvis-backend --tail 20

echo ""
echo "================================================================================"
echo "✅ Complete rebuild finished!"
echo ""
echo "Next steps:"
echo "  1. Run the test: ./test_order_update_comprehensive.sh"
echo "  2. Check logs: docker logs uvis-backend --tail 100"
echo "================================================================================"
