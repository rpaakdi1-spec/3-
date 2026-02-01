#!/bin/bash

set -e

echo "=================================================="
echo "500 Error Emergency Hotfix"
echo "=================================================="
echo ""

cd /root/uvis

echo "1. Checking current branch and commits..."
git branch -v
git log --oneline -3

echo ""
echo "2. Fetching latest code..."
git fetch origin genspark_ai_developer

echo ""
echo "3. Checking out genspark_ai_developer branch..."
git checkout genspark_ai_developer
git pull origin genspark_ai_developer

echo ""
echo "4. Running database hotfix script..."
docker exec uvis-backend python3 /app/hotfix_500_error.py || echo "Hotfix script failed or not needed"

echo ""
echo "5. Restarting backend service..."
docker-compose -f docker-compose.prod.yml restart backend

echo ""
echo "6. Waiting for backend to be ready..."
sleep 10

echo ""
echo "7. Checking backend logs for errors..."
docker logs uvis-backend --tail 30

echo ""
echo "8. Testing GET /orders/ endpoint..."
curl -X GET "http://139.150.11.99/api/v1/orders/?limit=1" \
     -H "accept: application/json" \
     -w "\nHTTP Status: %{http_code}\n" \
     -s

echo ""
echo "=================================================="
echo "Hotfix Complete!"
echo "=================================================="
echo ""
echo "If still getting 500 errors, please check:"
echo "1. Backend logs: docker logs uvis-backend --tail 50 -f"
echo "2. Database connection"
echo "3. Share the error message for further diagnosis"
echo ""
