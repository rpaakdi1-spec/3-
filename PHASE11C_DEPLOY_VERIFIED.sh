#!/bin/bash

###############################################################################
# Phase 11-C: Complete Deployment Script (Verified & Tested)
# Date: 2026-02-10
# Description: Deploy Rule Simulation Engine with full validation
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

# Step counter
STEP=0
step() {
    STEP=$((STEP + 1))
    echo ""
    echo "========================================="
    echo "Step $STEP: $1"
    echo "========================================="
}

###############################################################################
# Pre-flight Checks
###############################################################################

step "Pre-flight Checks"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (or with sudo)"
    exit 1
fi

# Check if in correct directory
if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml not found. Please run from /root/uvis"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker not found. Please install Docker first."
    exit 1
fi

# Check disk space (need at least 5GB)
AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 5 ]; then
    log_warning "Low disk space: ${AVAILABLE_SPACE}GB available. Recommended: 5GB+"
fi

log_success "Pre-flight checks passed"

###############################################################################
# Git Operations
###############################################################################

step "Clean Working Directory"

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    log_warning "Working directory has changes. Stashing..."
    git stash
    log_success "Changes stashed"
else
    log_success "Working directory clean"
fi

step "Pull Latest Code"

log_info "Fetching from origin..."
git fetch origin main

log_info "Current commit: $(git rev-parse --short HEAD)"
git pull origin main

LATEST_COMMIT=$(git rev-parse --short HEAD)
log_success "Updated to commit: $LATEST_COMMIT"

# Show recent commits
log_info "Recent commits:"
git log --oneline -3

###############################################################################
# Backend: Database Migration
###############################################################################

step "Backend - Database Migration"

log_info "Checking backend container status..."
if ! docker-compose ps backend | grep -q "Up"; then
    log_warning "Backend container not running. Starting..."
    docker-compose up -d backend
    sleep 10
fi

log_info "Running Alembic migrations..."
docker-compose exec -T backend alembic upgrade heads

if [ $? -eq 0 ]; then
    log_success "Database migrations completed"
else
    log_error "Migration failed!"
    exit 1
fi

# Verify simulation tables exist
log_info "Verifying simulation tables..."
TABLE_COUNT=$(docker-compose exec -T db psql -U postgres -d uvis -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('rule_simulations', 'simulation_comparisons', 'simulation_templates');" | tr -d ' ')

if [ "$TABLE_COUNT" -eq "3" ]; then
    log_success "All simulation tables verified"
else
    log_warning "Expected 3 simulation tables, found $TABLE_COUNT"
fi

# Check template data
TEMPLATE_COUNT=$(docker-compose exec -T db psql -U postgres -d uvis -t -c \
    "SELECT COUNT(*) FROM simulation_templates;" | tr -d ' ')
log_info "Simulation templates in database: $TEMPLATE_COUNT"

###############################################################################
# Frontend: Build
###############################################################################

step "Frontend - Build Production Bundle"

cd frontend

log_info "Checking for package updates..."
if git diff HEAD~1 HEAD --name-only | grep -q "package.json"; then
    log_warning "package.json updated. Installing dependencies..."
    npm install --legacy-peer-deps
    log_success "Dependencies updated"
else
    log_info "No package changes detected"
fi

log_info "Building frontend... (this may take 2-3 minutes)"
npm run build

if [ $? -eq 0 ]; then
    log_success "Frontend build completed"
else
    log_error "Frontend build failed!"
    exit 1
fi

# Verify build output
if [ -f "dist/index.html" ]; then
    BUILD_SIZE=$(du -sh dist | cut -f1)
    log_success "Build output verified: $BUILD_SIZE"
    ls -lh dist/index.html
else
    log_error "Build output not found!"
    exit 1
fi

cd /root/uvis

###############################################################################
# Docker: Container Restart
###############################################################################

step "Docker - Stop Containers"

log_info "Stopping frontend and nginx containers..."
docker-compose stop frontend nginx

if [ $? -eq 0 ]; then
    log_success "Containers stopped"
else
    log_warning "Some containers may not have stopped cleanly"
fi

step "Docker - Remove Old Containers"

log_info "Removing old containers..."
docker-compose rm -f frontend nginx

log_success "Old containers removed"

step "Docker - Build New Images"

log_warning "Building new images (no cache)..."
log_warning "This will take 3-5 minutes..."

docker-compose build --no-cache backend frontend

if [ $? -eq 0 ]; then
    log_success "New images built successfully"
else
    log_error "Docker build failed!"
    exit 1
fi

step "Docker - Start Containers"

log_info "Starting all containers..."
docker-compose up -d

log_success "Containers started"

###############################################################################
# Health Checks
###############################################################################

step "Health Checks"

log_info "Waiting for containers to be healthy (30 seconds)..."
sleep 30

# Check container status
log_info "Container status:"
docker-compose ps

# Count healthy containers
HEALTHY_COUNT=$(docker-compose ps | grep -c "healthy")
log_info "Healthy containers: $HEALTHY_COUNT"

# Check backend health
log_info "Testing backend health..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
if [ "$BACKEND_STATUS" = "200" ]; then
    log_success "Backend health check passed"
else
    log_warning "Backend health check returned: $BACKEND_STATUS"
fi

# Check frontend
log_info "Testing frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    log_success "Frontend check passed"
else
    log_warning "Frontend check returned: $FRONTEND_STATUS"
fi

###############################################################################
# API Validation
###############################################################################

step "API Validation"

# Test simulations templates endpoint
log_info "Testing simulations templates API..."
TEMPLATES_RESPONSE=$(curl -s http://localhost:8000/api/v1/simulations/templates)

if [ -n "$TEMPLATES_RESPONSE" ]; then
    TEMPLATE_COUNT=$(echo "$TEMPLATES_RESPONSE" | grep -o '"id"' | wc -l)
    log_success "Simulations API working: $TEMPLATE_COUNT templates found"
    
    # Show template names
    echo "$TEMPLATES_RESPONSE" | grep -o '"name":"[^"]*"' | head -3
else
    log_warning "Simulations API returned empty response"
fi

# Test simulations list endpoint
log_info "Testing simulations list API..."
SIMULATIONS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/simulations)
if [ "$SIMULATIONS_STATUS" = "200" ]; then
    log_success "Simulations list API working"
else
    log_warning "Simulations list API returned: $SIMULATIONS_STATUS"
fi

###############################################################################
# Summary
###############################################################################

step "Deployment Summary"

echo ""
echo "========================================="
echo "✅ Phase 11-C Deployment Complete!"
echo "========================================="
echo ""
echo "📊 Status:"
echo "   • Latest Commit: $LATEST_COMMIT"
echo "   • Database: Migrated"
echo "   • Templates: $TEMPLATE_COUNT in database"
echo "   • Frontend: Built ($BUILD_SIZE)"
echo "   • Containers: $HEALTHY_COUNT healthy"
echo "   • Backend API: $BACKEND_STATUS"
echo "   • Frontend: $FRONTEND_STATUS"
echo ""
echo "🌐 Next Steps:"
echo "   1. Open browser: http://139.150.11.99/"
echo "   2. Clear cache: Ctrl+Shift+Delete (전체 기간)"
echo "   3. Login and check sidebar for '규칙 시뮬레이션'"
echo "   4. Navigate to /simulations"
echo "   5. Test template gallery (6 templates)"
echo "   6. Run a simulation"
echo ""
echo "📋 API Endpoints:"
echo "   • Templates: GET /api/v1/simulations/templates"
echo "   • List: GET /api/v1/simulations"
echo "   • Run: POST /api/v1/simulations"
echo "   • Compare: POST /api/v1/simulations/compare"
echo ""
echo "📝 Logs:"
echo "   • Backend: docker-compose logs -f backend"
echo "   • Frontend: docker-compose logs -f frontend"
echo ""
echo "🎉 Phase 11-C is now live!"
echo ""
