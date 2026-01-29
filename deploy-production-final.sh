#!/bin/bash

###############################################################################
# Cold Chain Dispatch System - Production Deployment Script
# 완벽한 프로덕션 배포 스크립트
# Version: 2.0 (2026-01-28)
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/root/uvis"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"
BACKUP_DIR="/root/backups"
LOG_FILE="/tmp/deployment-$(date +%Y%m%d-%H%M%S).log"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_step() {
    echo -e "\n${BLUE}===== $1 =====${NC}\n" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

###############################################################################
# Step 1: Pre-deployment Checks
###############################################################################
log_step "Step 1: Pre-deployment Checks"

# Check Git
if ! command -v git &> /dev/null; then
    log_error "Git is not installed"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed"
    exit 1
fi

log_info "All prerequisites are installed"

###############################################################################
# Step 2: Backup Current State
###############################################################################
log_step "Step 2: Backing Up Current State"

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Backup database
if docker ps | grep -q uvis-db; then
    log_info "Backing up PostgreSQL database..."
    docker exec uvis-db pg_dump -U uvis_user uvis_db > "$BACKUP_DIR/db-backup-$TIMESTAMP.sql" || log_warn "Database backup failed"
fi

# Backup .env file
if [ -f "$ENV_FILE" ]; then
    log_info "Backing up .env file..."
    cp "$ENV_FILE" "$BACKUP_DIR/.env-backup-$TIMESTAMP"
fi

log_info "Backup completed: $BACKUP_DIR"

###############################################################################
# Step 3: Pull Latest Code
###############################################################################
log_step "Step 3: Pulling Latest Code from GitHub"

# Stash any local changes
git stash || true

# Fetch latest code
log_info "Fetching from origin/genspark_ai_developer..."
git fetch origin genspark_ai_developer

# Reset to latest commit
log_info "Resetting to origin/genspark_ai_developer..."
git reset --hard origin/genspark_ai_developer

# Show current commit
CURRENT_COMMIT=$(git log -1 --oneline)
log_info "Current commit: $CURRENT_COMMIT"

###############################################################################
# Step 4: Environment Configuration
###############################################################################
log_step "Step 4: Configuring Environment"

# Copy production env if .env doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    log_warn ".env file not found, copying from .env.production..."
    cp .env.production "$ENV_FILE"
fi

# Verify required environment variables
log_info "Verifying environment variables..."
REQUIRED_VARS=("DATABASE_URL" "SECRET_KEY" "NAVER_MAP_CLIENT_ID")
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^$var=" "$ENV_FILE"; then
        log_warn "Missing environment variable: $var"
    fi
done

###############################################################################
# Step 5: Stop Running Containers
###############################################################################
log_step "Step 5: Stopping Running Containers"

if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
    log_info "Stopping containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down || log_warn "Failed to stop some containers"
else
    log_info "No containers are running"
fi

###############################################################################
# Step 6: Clean Docker Cache
###############################################################################
log_step "Step 6: Cleaning Docker Cache"

log_info "Removing unused Docker images and containers..."
docker system prune -f || log_warn "Docker prune failed"

log_info "Removing old backend images..."
docker images | grep uvis-backend | awk '{print $3}' | xargs -r docker rmi -f || true

log_info "Removing old frontend images..."
docker images | grep uvis-frontend | awk '{print $3}' | xargs -r docker rmi -f || true

###############################################################################
# Step 7: Build Images
###############################################################################
log_step "Step 7: Building Docker Images"

log_info "Building backend image (this may take 5-8 minutes)..."
START_TIME=$(date +%s)
docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache --pull backend
BACKEND_BUILD_TIME=$(($(date +%s) - START_TIME))
log_info "Backend build completed in ${BACKEND_BUILD_TIME}s"

log_info "Building frontend image (this may take 8-12 minutes)..."
START_TIME=$(date +%s)
docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache --pull frontend
FRONTEND_BUILD_TIME=$(($(date +%s) - START_TIME))
log_info "Frontend build completed in ${FRONTEND_BUILD_TIME}s"

###############################################################################
# Step 8: Start Services
###############################################################################
log_step "Step 8: Starting Services"

log_info "Starting all services..."
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

log_info "Waiting for services to be healthy..."
sleep 10

###############################################################################
# Step 9: Health Checks
###############################################################################
log_step "Step 9: Running Health Checks"

# Function to check service health
check_service_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep "$service" | grep -q "healthy\|Up"; then
            log_info "$service is healthy"
            return 0
        fi
        log_info "Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    log_error "$service failed to become healthy"
    return 1
}

# Check each service
check_service_health "uvis-db"
check_service_health "uvis-redis"
check_service_health "uvis-backend"
check_service_health "uvis-frontend"
check_service_health "uvis-nginx"

# Backend API health check
log_info "Checking backend API health endpoint..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
        log_info "Backend health check passed: $HEALTH_RESPONSE"
        break
    fi
    ((RETRY_COUNT++))
    log_warn "Backend health check failed (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "Backend health check failed after $MAX_RETRIES attempts"
    log_error "Checking backend logs..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=50 backend
    exit 1
fi

###############################################################################
# Step 10: Final Verification
###############################################################################
log_step "Step 10: Final Verification"

log_info "Container Status:"
docker-compose -f "$DOCKER_COMPOSE_FILE" ps

log_info "\nBackend Logs (last 10 lines):"
docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=10 backend

log_info "\nFrontend Logs (last 5 lines):"
docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=5 frontend

###############################################################################
# Deployment Summary
###############################################################################
log_step "Deployment Summary"

echo -e "${GREEN}✅ Deployment Successful!${NC}\n"

cat << EOF
┌─────────────────────────────────────────────────────────────┐
│                  🚀 Deployment Complete 🚀                  │
├─────────────────────────────────────────────────────────────┤
│ Timestamp:       $(date +"%Y-%m-%d %H:%M:%S")                      │
│ Commit:          $CURRENT_COMMIT                   │
│ Backend Build:   ${BACKEND_BUILD_TIME}s                                    │
│ Frontend Build:  ${FRONTEND_BUILD_TIME}s                                    │
│ Log File:        $LOG_FILE                          │
├─────────────────────────────────────────────────────────────┤
│ 🌐 Access URLs:                                             │
│   Frontend:      http://139.150.11.99                      │
│   API Docs:      http://139.150.11.99:8000/docs            │
│   Health Check:  http://139.150.11.99:8000/health          │
├─────────────────────────────────────────────────────────────┤
│ 📊 Service Status:                                          │
$(docker-compose -f "$DOCKER_COMPOSE_FILE" ps | tail -n +2 | awk '{printf "│   %-20s %s\n", $1, $4}')                                               │
├─────────────────────────────────────────────────────────────┤
│ 🔧 Useful Commands:                                         │
│   View logs:     docker-compose -f $DOCKER_COMPOSE_FILE logs -f │
│   Stop services: docker-compose -f $DOCKER_COMPOSE_FILE down    │
│   Restart:       docker-compose -f $DOCKER_COMPOSE_FILE restart │
└─────────────────────────────────────────────────────────────┘
EOF

log_info "Deployment completed successfully!"
exit 0
