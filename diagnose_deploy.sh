#!/bin/bash
# Semi-Auto Dispatch Deployment Diagnostic Script

echo "=================================="
echo "UVIS Semi-Auto Dispatch Diagnostic"
echo "=================================="
echo ""

cd /root/uvis

echo "1️⃣ Container Status:"
echo "---"
docker compose ps
echo ""

echo "2️⃣ Frontend Container Logs (last 50 lines):"
echo "---"
docker compose logs frontend --tail=50
echo ""

echo "3️⃣ Backend Container Logs (last 30 lines):"
echo "---"
docker compose logs backend --tail=30
echo ""

echo "4️⃣ Frontend Container Inspection:"
echo "---"
echo "Checking if dist files exist..."
docker compose exec frontend ls -la /usr/share/nginx/html/ 2>/dev/null || echo "❌ Cannot access frontend container"
echo ""

echo "5️⃣ Nginx Configuration Test:"
echo "---"
docker compose exec frontend nginx -t 2>&1 || echo "❌ Nginx test failed"
echo ""

echo "6️⃣ Backend Health Check (internal):"
echo "---"
curl -s http://backend:8000/health 2>/dev/null || echo "❌ Backend not responding"
echo ""

echo "7️⃣ Frontend Health Check:"
echo "---"
curl -s http://localhost/health 2>/dev/null || echo "❌ Frontend not responding"
echo ""

echo "8️⃣ API Health Check:"
echo "---"
curl -s http://localhost/api/v1/health 2>/dev/null || echo "❌ API not responding"
echo ""

echo "=================================="
echo "Diagnostic Complete"
echo "=================================="
echo ""
echo "💡 If frontend is restarting:"
echo "   - Check frontend logs above for errors"
echo "   - Run: docker compose logs frontend --tail=100"
echo "   - Try: docker compose restart frontend"
echo ""
echo "💡 If 502 Bad Gateway:"
echo "   - Check if backend is running"
echo "   - Run: docker compose logs backend --tail=100"
echo "   - Try: docker compose restart backend"
echo ""
echo "💡 Complete rebuild:"
echo "   docker compose down"
echo "   docker compose build --no-cache frontend backend"
echo "   docker compose up -d"
echo ""
