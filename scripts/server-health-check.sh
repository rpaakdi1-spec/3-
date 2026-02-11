#!/bin/bash

# ============================================
# Server Health Check & Diagnostic Script
# 서버 전체 환경 점검 및 문제 진단
# ============================================

set -e

echo "🏥 Server Health Check & Diagnostic"
echo "===================================="
echo ""
echo "📅 Date: $(date)"
echo "🖥️  Hostname: $(hostname)"
echo ""

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 결과 저장
REPORT_FILE="server-diagnostic-$(date +%Y%m%d-%H%M%S).txt"

exec > >(tee -a "$REPORT_FILE")
exec 2>&1

# ============================================
# 1. 시스템 리소스
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  System Resources"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📊 Memory Usage:"
free -h
echo ""

echo "💾 Disk Usage:"
df -h | grep -E "Filesystem|/dev/"
echo ""

echo "⚙️  CPU Info:"
lscpu | grep -E "Model name|CPU\(s\)|Thread"
echo ""

echo "📈 Load Average:"
uptime
echo ""

echo "🔄 Swap:"
swapon --show
echo ""

# ============================================
# 2. Docker 환경
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Docker Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🐳 Docker Version:"
docker --version
docker-compose --version
echo ""

echo "📦 Docker Containers:"
docker-compose ps
echo ""

echo "📊 Docker Stats:"
docker stats --no-stream
echo ""

echo "🔍 Docker Networks:"
docker network ls
echo ""

echo "💾 Docker Volumes:"
docker volume ls
echo ""

echo "🖼️  Docker Images:"
docker images | grep -E "REPOSITORY|uvis"
echo ""

# ============================================
# 3. 서비스 상태
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Service Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🌐 Port Listening:"
netstat -tlnp | grep -E "LISTEN|:80|:8000|:5432|:6379" || ss -tlnp | grep -E "LISTEN|:80|:8000|:5432|:6379"
echo ""

echo "🔌 HTTP Services:"
echo "Frontend (port 80):"
curl -I http://localhost/ 2>&1 | head -5 || echo "❌ Frontend not responding"
echo ""

echo "Backend (port 8000):"
curl -I http://localhost:8000/docs 2>&1 | head -5 || echo "❌ Backend not responding"
echo ""

echo "Backend API:"
curl -s http://localhost:8000/api/v1/simulations/templates 2>&1 | head -10 || echo "❌ API not responding"
echo ""

# ============================================
# 4. 프로젝트 상태
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Project Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "/root/uvis" ]; then
    cd /root/uvis
    
    echo "📂 Project Directory:"
    ls -lh | head -20
    echo ""
    
    echo "🔀 Git Status:"
    git status
    echo ""
    
    echo "📝 Git Log (last 5):"
    git log --oneline -5
    echo ""
    
    echo "🔧 Docker Compose Config:"
    docker-compose config --services
    echo ""
    
    echo "📄 Frontend dist:"
    if [ -d "frontend/dist" ]; then
        ls -lh frontend/dist/
        echo "✅ dist exists"
    else
        echo "❌ dist NOT found"
    fi
    echo ""
    
    echo "📄 Environment Files:"
    ls -la .env backend/.env frontend/.env 2>&1 || echo "Some .env files missing"
    echo ""
fi

# ============================================
# 5. 로그 분석
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Recent Logs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🔴 Backend Errors (last 20 lines):"
docker-compose logs backend 2>&1 | tail -20 || echo "No backend logs"
echo ""

echo "🔵 Frontend Logs (last 10 lines):"
docker-compose logs frontend 2>&1 | tail -10 || echo "No frontend logs"
echo ""

# ============================================
# 6. 네트워크 진단
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Network Diagnostics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "🌐 Public IP:"
curl -s ifconfig.me || echo "Cannot detect public IP"
echo ""

echo "🔌 Active Connections:"
netstat -an | grep -E "ESTABLISHED|LISTEN" | grep -E ":80|:8000|:5432|:6379" | head -20 || echo "No active connections"
echo ""

# ============================================
# 7. 문제 진단
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Problem Diagnosis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PROBLEMS=0

# 메모리 체크
TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
USED_MEM=$(free -m | awk '/^Mem:/{print $3}')
MEM_PERCENT=$((USED_MEM * 100 / TOTAL_MEM))

if [ $MEM_PERCENT -gt 90 ]; then
    echo "❌ CRITICAL: Memory usage > 90% ($MEM_PERCENT%)"
    PROBLEMS=$((PROBLEMS + 1))
elif [ $MEM_PERCENT -gt 80 ]; then
    echo "⚠️  WARNING: Memory usage > 80% ($MEM_PERCENT%)"
    PROBLEMS=$((PROBLEMS + 1))
else
    echo "✅ Memory usage OK ($MEM_PERCENT%)"
fi

# 디스크 체크
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "❌ CRITICAL: Disk usage > 90% ($DISK_USAGE%)"
    PROBLEMS=$((PROBLEMS + 1))
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  WARNING: Disk usage > 80% ($DISK_USAGE%)"
    PROBLEMS=$((PROBLEMS + 1))
else
    echo "✅ Disk usage OK ($DISK_USAGE%)"
fi

# Docker 컨테이너 체크
RUNNING_CONTAINERS=$(docker-compose ps --services --filter "status=running" 2>/dev/null | wc -l)
TOTAL_CONTAINERS=$(docker-compose ps --services 2>/dev/null | wc -l)

if [ $RUNNING_CONTAINERS -lt $TOTAL_CONTAINERS ]; then
    echo "⚠️  WARNING: Some containers not running ($RUNNING_CONTAINERS/$TOTAL_CONTAINERS)"
    PROBLEMS=$((PROBLEMS + 1))
else
    echo "✅ All containers running ($RUNNING_CONTAINERS/$TOTAL_CONTAINERS)"
fi

# HTTP 서비스 체크
if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
    echo "✅ Frontend responding (HTTP 200)"
else
    echo "❌ Frontend NOT responding"
    PROBLEMS=$((PROBLEMS + 1))
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo "✅ Backend responding (HTTP 200)"
else
    echo "❌ Backend NOT responding"
    PROBLEMS=$((PROBLEMS + 1))
fi

# Git 상태 체크
if [ -d "/root/uvis" ]; then
    cd /root/uvis
    if git diff --quiet && git diff --cached --quiet; then
        echo "✅ Git working tree clean"
    else
        echo "⚠️  WARNING: Uncommitted changes in Git"
        PROBLEMS=$((PROBLEMS + 1))
    fi
fi

echo ""

# ============================================
# 8. 권장 조치
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8️⃣  Recommended Actions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $PROBLEMS -eq 0 ]; then
    echo "✅ No critical problems detected!"
    echo ""
    echo "👍 System is healthy. Proceed with deployment."
else
    echo "⚠️  Found $PROBLEMS problem(s). Recommendations:"
    echo ""
    
    if [ $MEM_PERCENT -gt 80 ]; then
        echo "💡 Memory issue:"
        echo "   - Add swap: sudo fallocate -l 4G /swapfile"
        echo "   - Restart containers: docker-compose restart"
        echo "   - Consider server upgrade"
        echo ""
    fi
    
    if [ "$DISK_USAGE" -gt 80 ]; then
        echo "💡 Disk issue:"
        echo "   - Clean Docker: docker system prune -a"
        echo "   - Remove old logs: find /var/log -type f -name '*.log' -mtime +30 -delete"
        echo ""
    fi
    
    if [ $RUNNING_CONTAINERS -lt $TOTAL_CONTAINERS ]; then
        echo "💡 Container issue:"
        echo "   - Restart all: docker-compose down && docker-compose up -d"
        echo "   - Check logs: docker-compose logs"
        echo ""
    fi
    
    if ! curl -s http://localhost/ > /dev/null; then
        echo "💡 Frontend issue:"
        echo "   - Copy dist: docker cp frontend/dist/. uvis-frontend:/usr/share/nginx/html/"
        echo "   - Restart: docker-compose restart frontend"
        echo ""
    fi
    
    if ! curl -s http://localhost:8000/docs > /dev/null; then
        echo "💡 Backend issue:"
        echo "   - Check logs: docker-compose logs backend"
        echo "   - Restart: docker-compose restart backend"
        echo "   - Run migrations: docker-compose exec backend alembic upgrade heads"
        echo ""
    fi
fi

# ============================================
# 9. 요약
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9️⃣  Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Problems Found: $PROBLEMS"
echo "📄 Report saved: $REPORT_FILE"
echo ""

if [ $PROBLEMS -eq 0 ]; then
    echo "✅ Server is healthy and ready for deployment!"
else
    echo "⚠️  Please review and fix the issues above."
fi

echo ""
echo "===================================="
echo "✅ Health Check Complete!"
echo "===================================="
