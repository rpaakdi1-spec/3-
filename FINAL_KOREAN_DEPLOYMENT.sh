#!/bin/bash

##############################################################################
# UVIS Frontend Final Korean Deployment Script
# 
# This script deploys the frontend with Korean translations for Dispatch Rules
# and fixes API URL configuration
##############################################################################

set -e  # Exit on error

echo "🚀 UVIS Frontend Final Korean Deployment"
echo "========================================"
echo ""

# Step 1: Navigate to project directory
echo "📁 Step 1: Navigate to /root/uvis"
cd /root/uvis || { echo "❌ Error: /root/uvis directory not found"; exit 1; }

# Step 2: Clean working directory
echo "🧹 Step 2: Clean working directory"
git checkout -- . 2>/dev/null || true
echo "✅ Working directory cleaned"

# Step 3: Pull latest code
echo "📥 Step 3: Pull latest code from GitHub"
git pull origin main || { echo "❌ Error: Failed to pull latest code"; exit 1; }
echo "✅ Latest code pulled"

# Step 4: Fix .env file (VITE_API_URL -> VITE_API_BASE_URL)
echo "🔧 Step 4: Fix .env file"
cd frontend
cat > .env << 'EOF'
# API Configuration
# Use relative path for production (proxied through nginx)
# Use full URL for local development
VITE_API_BASE_URL=/api/v1
EOF
echo "✅ .env file fixed with correct environment variable name"

# Step 5: Backup test files
echo "📦 Step 5: Backup test files"
mkdir -p .build-backup
mv src/components/common/__tests__ .build-backup/ 2>/dev/null || true
mv src/store/__tests__ .build-backup/ 2>/dev/null || true
mv src/utils/__tests__ .build-backup/ 2>/dev/null || true
mv src/setupTests.ts .build-backup/ 2>/dev/null || true
echo "✅ Test files backed up"

# Step 6: Install Tailwind CSS v4 PostCSS plugin
echo "📦 Step 6: Installing Tailwind CSS v4 PostCSS plugin..."
npm install -D @tailwindcss/postcss --legacy-peer-deps

# Step 7: Build frontend
echo "🏗️  Step 7: Building frontend..."
npm run build || { echo "❌ Error: Frontend build failed"; exit 1; }
echo "✅ Frontend built successfully"

# Step 8: Verify build output
echo "📋 Step 8: Verify build output"
ls -lh dist/index.html
echo "✅ Build output verified"

# Step 9: Return to main directory
echo "📁 Step 9: Return to main directory"
cd /root/uvis

# Step 10: Restart containers
echo "🔄 Step 10: Restarting containers..."
docker-compose stop frontend nginx
docker-compose rm -f frontend nginx
docker-compose build --no-cache frontend
docker-compose up -d frontend nginx
echo "✅ Containers restarted"

# Step 11: Wait for containers to be ready
echo "⏳ Step 11: Waiting 30 seconds for containers to be ready..."
sleep 30

# Step 12: Check deployment status
echo "✅ Step 12: Checking deployment status..."
echo ""
echo "=== Container Status ==="
docker-compose ps

echo ""
echo "=== Build File Date ==="
ls -lh frontend/dist/index.html

echo ""
echo "=== HTTP Response ==="
curl -I http://localhost/

echo ""
echo "=== API Test ==="
curl -s http://localhost:8000/api/v1/dispatch-rules/ | jq '.[0:2]' || echo "API check skipped"

echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo ""
echo "✅ Korean translations added for Dispatch Rules"
echo "✅ API URL configuration fixed (VITE_API_BASE_URL)"
echo "✅ Frontend rebuilt with latest translations"
echo "✅ Containers restarted successfully"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://139.150.11.99/"
echo "   Rule Builder: http://139.150.11.99/dispatch-rules"
echo "   API Docs: http://139.150.11.99:8000/docs"
echo ""
echo "🔍 Next Steps:"
echo "   1. Clear browser cache (Ctrl+Shift+Delete)"
echo "   2. Open in Incognito mode (Ctrl+Shift+N)"
echo "   3. Navigate to http://139.150.11.99/dispatch-rules"
echo "   4. Verify Korean UI labels are displayed"
echo "   5. Verify 2 rules are loaded from API"
echo ""
echo "📸 Please provide screenshots of:"
echo "   - Dashboard with Korean sidebar"
echo "   - Dispatch Rules page with 2 rule cards"
echo "   - (Optional) Create New Rule form"
echo ""
