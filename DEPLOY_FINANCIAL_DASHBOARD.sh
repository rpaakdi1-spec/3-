#!/bin/bash
# Single command to fix Financial Dashboard on production server
# Copy this entire block and run on /root/uvis

cd /root/uvis && \
cd frontend && \
echo "🔨 Building frontend..." && \
npm run build && \
cd /root/uvis && \
echo "📦 Deploying to Docker..." && \
docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/ && \
echo "🔄 Restarting frontend container..." && \
docker-compose restart frontend && \
echo "⏳ Waiting for container to start..." && \
sleep 15 && \
echo "" && \
echo "✅✅✅ DEPLOYMENT COMPLETE! ✅✅✅" && \
echo "" && \
echo "🌐 Open browser: http://139.150.11.99" && \
echo "🔑 Login: admin / admin123" && \
echo "📊 Navigate: 청구/정산 → 재무 대시보드" && \
echo "🔄 Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)" && \
echo "" && \
echo "Expected UI:" && \
echo "  ✓ 4 summary cards" && \
echo "  ✓ Monthly trend line chart" && \
echo "  ✓ Monthly profit bar chart" && \
echo "  ✓ Top 10 clients table" && \
echo "" && \
docker-compose ps | grep frontend
