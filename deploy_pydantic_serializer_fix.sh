#!/bin/bash

set -e

echo "=================================================="
echo "Pydantic Serializer 500 Error Fix - Deployment"
echo "=================================================="
echo ""

cd /root/uvis

echo "1. Fetching latest changes from Git..."
git fetch origin genspark_ai_developer

echo ""
echo "2. Checking out genspark_ai_developer branch..."
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

echo ""
echo "3. Restarting backend service..."
docker-compose -f docker-compose.prod.yml restart backend

echo ""
echo "4. Waiting for backend to be ready..."
sleep 10

echo ""
echo "5. Checking backend health..."
docker ps | grep backend

echo ""
echo "6. Testing GET /orders/ endpoint..."
curl -X GET "http://139.150.11.99/api/v1/orders/?limit=5" \
     -H "accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n" \
     -s | head -20

echo ""
echo "=================================================="
echo "Deployment Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Open browser: http://139.150.11.99/orders"
echo "2. Check if orders list loads without 500 errors"
echo "3. Try creating a new order"
echo "4. Monitor backend logs: docker logs uvis-backend-1 --tail 50 -f"
echo ""
