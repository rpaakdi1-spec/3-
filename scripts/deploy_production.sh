#!/bin/bash

# Phase 3 Production Deployment Script
# 프로덕션 서버 배포 자동화 스크립트

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 배너
echo ""
echo "========================================================================"
echo "  🚀 UVIS ML Dispatch System - Production Deployment"
echo "========================================================================"
echo ""

# Step 1: Git Pull
log_info "Step 1: Pulling latest code from main branch..."
cd /root/uvis
git fetch origin main
git pull origin main
log_success "Code updated successfully"

# Step 2: 권한 설정
log_info "Step 2: Setting script permissions..."
chmod +x scripts/gradual_rollout.sh
log_success "Permissions set"

# Step 3: Redis 확인
log_info "Step 3: Checking Redis service..."
if docker ps | grep -q redis; then
    log_success "Redis is already running"
else
    log_warning "Redis not found, starting Redis..."
    docker-compose -f docker-compose.prod.yml up -d redis
    sleep 5
    log_success "Redis started"
fi

# Redis 연결 테스트
log_info "Testing Redis connection..."
if docker exec uvis-redis redis-cli ping | grep -q PONG; then
    log_success "Redis connection successful"
else
    log_error "Redis connection failed"
    exit 1
fi

# Step 4: 백엔드 재빌드
log_info "Step 4: Rebuilding backend service..."
docker-compose -f docker-compose.prod.yml up -d --build backend

log_info "Waiting for backend to start (30 seconds)..."
sleep 30

# 백엔드 상태 확인
if docker ps | grep -q uvis-backend; then
    log_success "Backend is running"
else
    log_error "Backend failed to start"
    docker logs uvis-backend --tail 50
    exit 1
fi

# Step 5: 프론트엔드 재빌드
log_info "Step 5: Rebuilding frontend service..."
docker-compose -f docker-compose.prod.yml up -d --build frontend

log_info "Waiting for frontend to start (20 seconds)..."
sleep 20

# 프론트엔드 상태 확인
if docker ps | grep -q uvis-frontend; then
    log_success "Frontend is running"
else
    log_error "Frontend failed to start"
    docker logs uvis-frontend --tail 50
    exit 1
fi

# Step 6: 헬스 체크
echo ""
log_info "Step 6: Health Check..."
echo ""

# 컨테이너 상태
log_info "Container status:"
docker ps | grep uvis

echo ""

# 백엔드 로그 확인
log_info "Backend logs (last 20 lines):"
docker logs uvis-backend --tail 20

echo ""

# API 테스트
log_info "Testing ML Dispatch API..."
API_RESPONSE=$(curl -s http://localhost:8000/api/ml-dispatch/ab-test/stats || echo "FAILED")

if echo "$API_RESPONSE" | grep -q "total_users"; then
    log_success "ML Dispatch API is working"
    echo "Response: $API_RESPONSE"
else
    log_error "ML Dispatch API test failed"
    echo "Response: $API_RESPONSE"
fi

# Step 7: 배포 완료 요약
echo ""
echo "========================================================================"
log_success "🎉 Deployment Complete!"
echo "========================================================================"
echo ""
log_info "Services Status:"
echo "  ✅ Backend:  http://139.150.11.99:8000"
echo "  ✅ Frontend: http://139.150.11.99"
echo "  ✅ API Docs: http://139.150.11.99:8000/docs"
echo "  ✅ Redis:    Running"
echo ""

log_info "Next Steps:"
echo "  1. Verify API: curl http://139.150.11.99:8000/api/ml-dispatch/ab-test/stats"
echo "  2. Pilot Rollout (10%): ./scripts/gradual_rollout.sh pilot"
echo "  3. Monitor: http://139.150.11.99 (A/B Test Monitor)"
echo ""

log_warning "Important:"
echo "  • Monitor the system for 1 hour before scaling up"
echo "  • Success criteria: Success rate ≥ 90%, ML score ≥ 0.70"
echo "  • Emergency rollback: ./scripts/gradual_rollout.sh rollback"
echo ""
echo "========================================================================"
