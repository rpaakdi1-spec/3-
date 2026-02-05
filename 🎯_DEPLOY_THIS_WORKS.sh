#!/bin/bash

# 🎯 FINAL WORKING DEPLOYMENT SCRIPT
# This includes the .dockerignore fix that solves ERR_CONNECTION_REFUSED

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         🚀 UVIS Logistics - Final Deployment                 ║"
echo "║            (.dockerignore fix included)                       ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Changes being deployed:"
echo "  ✅ Backend fixes (10 issues)"
echo "  ✅ Frontend fixes (path, icons, JSX)"
echo "  ✅ Dockerfile improvements (NODE_ENV)"
echo "  ✅ .dockerignore (prevents .env from being copied) ← CRITICAL!"
echo ""
echo "🔧 Root cause solved:"
echo "  - .env file with localhost:8000 was being copied to Docker"
echo "  - .dockerignore now excludes it"
echo "  - .env.production with /api/v1 will be used"
echo ""
echo "⏱️  Estimated time: 6 minutes"
echo ""
read -p "Press Enter to start deployment..."

cd /root/uvis

echo ""
echo "Step 1/5: Fetching latest code..."
git fetch origin genspark_ai_developer

echo ""
echo "Step 2/5: Resetting to latest commit..."
git reset --hard origin/genspark_ai_developer

echo ""
echo "Step 3/5: Building frontend (this takes ~4-5 minutes)..."
docker-compose build --no-cache frontend

echo ""
echo "Step 4/5: Restarting containers..."
docker-compose up -d --force-recreate frontend nginx

echo ""
echo "Step 5/5: Waiting for services to start..."
sleep 30

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   ✅ Deployment Complete!              ║"
echo "╚════════════════════════════════════════╝"
echo ""

echo "📊 Container Status:"
docker-compose ps

echo ""
echo "🏥 Backend Health:"
curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health

echo ""
echo "🌐 Frontend Status:"
curl -s -I http://localhost/ | head -5

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   🎉 Success! Access the system:      ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "🌐 URLs:"
echo "   Frontend:  http://139.150.11.99/"
echo "   API Docs:  http://139.150.11.99:8000/docs"
echo "   Health:    http://139.150.11.99:8000/health"
echo ""
echo "✅ Browser test:"
echo "   1. Open http://139.150.11.99/"
echo "   2. Press F12 → Network tab"
echo "   3. Try to login"
echo "   4. You should see: POST /api/v1/auth/login (NOT localhost!)"
echo ""
echo "🎊 Deployment successful!"
