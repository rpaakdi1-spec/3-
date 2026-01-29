#!/bin/bash
# ==============================================
# 완벽한 프로덕션 배포 스크립트 (v3.0)
# ==============================================
# 작성일: 2026-01-28
# 목적: 모든 경우의 수를 고려한 완벽한 배포
# ==============================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

# Check if running in correct directory
if [ ! -f "docker-compose.prod.yml" ]; then
    log_error "docker-compose.prod.yml not found!"
    log_error "Please run this script from the project root directory"
    exit 1
fi

log_step "Step 1: Sync with Latest Code"
log_info "Fetching latest code from GitHub..."
git fetch origin genspark_ai_developer
log_info "Resetting to latest commit..."
git reset --hard origin/genspark_ai_developer
git log -1 --oneline
log_info "✅ Code synced successfully"

log_step "Step 2: Environment Configuration"
if [ ! -f ".env" ]; then
    log_warn ".env file not found, copying from .env.production..."
    cp .env.production .env
fi
log_info "Checking environment variables..."
grep -q "NAVER_MAP_CLIENT_ID" .env && log_info "✅ NAVER_MAP_CLIENT_ID found" || log_warn "⚠️  NAVER_MAP_CLIENT_ID not found"
grep -q "DATABASE_URL" .env && log_info "✅ DATABASE_URL found" || log_warn "⚠️  DATABASE_URL not found"
grep -q "UPLOAD_BASE_DIR" .env && log_info "✅ UPLOAD_BASE_DIR found" || log_warn "⚠️  UPLOAD_BASE_DIR not found in .env"

log_step "Step 3: Docker Cleanup"
log_info "Stopping all containers..."
docker-compose -f docker-compose.prod.yml down || true
log_info "Removing old images..."
docker rmi -f uvis-backend uvis-frontend 2>/dev/null || true
log_info "Pruning Docker system..."
docker system prune -f
log_info "✅ Docker cleanup complete"

log_step "Step 4: Building Backend (5-8 minutes)"
log_info "Building backend with --no-cache..."
docker-compose -f docker-compose.prod.yml build --no-cache --pull backend
log_info "✅ Backend built successfully"

log_step "Step 5: Building Frontend (8-12 minutes)"
log_info "Building frontend with --no-cache..."
docker-compose -f docker-compose.prod.yml build --no-cache --pull frontend
log_info "✅ Frontend built successfully"

log_step "Step 6: Starting All Services"
log_info "Starting all containers..."
docker-compose -f docker-compose.prod.yml up -d
log_info "✅ All containers started"

log_step "Step 7: Waiting for Services (60 seconds)"
log_info "Waiting for services to initialize..."
for i in {1..60}; do
    echo -n "."
    sleep 1
done
echo ""
log_info "✅ Wait complete"

log_step "Step 8: Container Status Check"
docker-compose -f docker-compose.prod.yml ps

log_step "Step 9: Health Check"
log_info "Checking backend health..."
HEALTH_ATTEMPTS=0
MAX_ATTEMPTS=10

while [ $HEALTH_ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    log_info "Health check attempt $((HEALTH_ATTEMPTS + 1))/$MAX_ATTEMPTS..."
    
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ Backend is healthy!"
        echo ""
        curl -s http://localhost:8000/health | python3 -m json.tool
        break
    else
        log_warn "Backend not ready yet, waiting 10 seconds..."
        sleep 10
        HEALTH_ATTEMPTS=$((HEALTH_ATTEMPTS + 1))
    fi
done

if [ $HEALTH_ATTEMPTS -eq $MAX_ATTEMPTS ]; then
    log_error "❌ Backend health check failed after $MAX_ATTEMPTS attempts"
    log_error "Checking backend logs..."
    docker-compose -f docker-compose.prod.yml logs --tail=50 backend
    exit 1
fi

log_step "Step 10: Final Verification"
log_info "Container status:"
docker-compose -f docker-compose.prod.yml ps | grep -E "healthy|Up"

log_info "\nBackend logs (last 10 lines):"
docker-compose -f docker-compose.prod.yml logs --tail=10 backend

log_info "\nFrontend logs (last 5 lines):"
docker-compose -f docker-compose.prod.yml logs --tail=5 frontend

log_step "✅✅✅ DEPLOYMENT SUCCESSFUL! ✅✅✅"
echo ""
log_info "🌐 Access URLs:"
log_info "   Frontend:        http://139.150.11.99"
log_info "   Frontend (dir):  http://139.150.11.99:3000"
log_info "   Backend API:     http://139.150.11.99:8000"
log_info "   API Docs:        http://139.150.11.99:8000/docs"
log_info "   Health Check:    http://139.150.11.99:8000/health"
echo ""
log_info "👤 Test Accounts:"
log_info "   Admin:    admin@example.com / admin123"
log_info "   Driver 1: driver1 / password123"
log_info "   Driver 2: driver2 / password123"
echo ""
log_info "📋 Useful Commands:"
log_info "   View logs:      docker-compose -f docker-compose.prod.yml logs -f [service]"
log_info "   Restart:        docker-compose -f docker-compose.prod.yml restart [service]"
log_info "   Stop all:       docker-compose -f docker-compose.prod.yml down"
log_info "   Check status:   docker-compose -f docker-compose.prod.yml ps"
echo ""
log_info "🎉 Deployment completed successfully at $(date)"
