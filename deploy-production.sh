#!/bin/bash
# Production Deployment Script
# Cold Chain Delivery Management System
# Zero-downtime rolling deployment

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="coldchain"
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"
BACKUP_BEFORE_DEPLOY=true
HEALTH_CHECK_TIMEOUT=60
HEALTH_CHECK_INTERVAL=5

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Environment file $ENV_FILE not found"
        exit 1
    fi
    
    print_info "✓ All requirements met"
}

backup_system() {
    if [ "$BACKUP_BEFORE_DEPLOY" = true ]; then
        print_info "Creating backup before deployment..."
        ./scripts/backup.sh
        print_info "✓ Backup completed"
    fi
}

pull_images() {
    print_info "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" pull
    print_info "✓ Images pulled"
}

build_images() {
    print_info "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    print_info "✓ Images built"
}

health_check() {
    local url=$1
    local timeout=$HEALTH_CHECK_TIMEOUT
    local interval=$HEALTH_CHECK_INTERVAL
    local elapsed=0
    
    print_info "Performing health check on $url..."
    
    while [ $elapsed -lt $timeout ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            print_info "✓ Health check passed"
            return 0
        fi
        sleep $interval
        elapsed=$((elapsed + interval))
        echo -n "."
    done
    
    echo ""
    print_error "Health check failed after ${timeout}s"
    return 1
}

rolling_update() {
    print_info "Performing rolling update..."
    
    # Update backend with rolling strategy
    docker-compose -f "$COMPOSE_FILE" up -d --no-deps --scale backend=2 --no-recreate backend
    
    # Wait for new containers to be healthy
    sleep 10
    
    if health_check "http://localhost/health"; then
        print_info "✓ New backend containers are healthy"
        
        # Remove old containers
        docker-compose -f "$COMPOSE_FILE" up -d --no-deps --scale backend=2 --remove-orphans backend
        print_info "✓ Rolling update completed"
    else
        print_error "New backend containers failed health check"
        print_warning "Rolling back..."
        docker-compose -f "$COMPOSE_FILE" up -d --no-deps backend
        return 1
    fi
}

deploy_services() {
    print_info "Deploying services..."
    
    # Start infrastructure services first
    docker-compose -f "$COMPOSE_FILE" up -d postgres redis
    
    # Wait for database to be ready
    print_info "Waiting for database..."
    sleep 10
    
    # Deploy backend with rolling update
    rolling_update
    
    # Update other services
    docker-compose -f "$COMPOSE_FILE" up -d nginx prometheus grafana
    
    print_info "✓ All services deployed"
}

show_status() {
    print_info "Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    print_info "Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
        $(docker-compose -f "$COMPOSE_FILE" ps -q)
}

cleanup() {
    print_info "Cleaning up..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (careful!)
    # docker volume prune -f
    
    print_info "✓ Cleanup completed"
}

main() {
    echo "=========================================="
    echo "Cold Chain Deployment Script"
    echo "Environment: PRODUCTION"
    echo "=========================================="
    echo ""
    
    # Check requirements
    check_requirements
    
    # Confirm deployment
    read -p "Do you want to proceed with deployment? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    # Backup
    backup_system
    
    # Pull or build images
    read -p "Build images locally or pull from registry? (build/pull): " -r
    echo
    if [[ $REPLY =~ ^[Bb]uild$ ]]; then
        build_images
    else
        pull_images
    fi
    
    # Deploy
    deploy_services
    
    # Health checks
    print_info "Running final health checks..."
    if health_check "http://localhost/health" && \
       health_check "http://localhost/api/v1/health"; then
        print_info "✓ All health checks passed"
    else
        print_error "Health checks failed"
        exit 1
    fi
    
    # Show status
    show_status
    
    # Cleanup
    cleanup
    
    echo ""
    echo "=========================================="
    print_info "Deployment completed successfully! 🚀"
    echo "=========================================="
    echo ""
    print_info "Access your application at:"
    echo "  - Frontend: https://yourdomain.com"
    echo "  - API Docs: https://yourdomain.com/api/docs"
    echo "  - Grafana: http://localhost:3001"
    echo "  - Prometheus: http://localhost:9090"
    echo ""
    print_info "Next steps:"
    echo "  1. Monitor logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  2. Check metrics: Visit Grafana dashboard"
    echo "  3. Test API: Visit API documentation"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    backup)
        backup_system
        ;;
    build)
        build_images
        ;;
    deploy)
        deploy_services
        ;;
    status)
        show_status
        ;;
    cleanup)
        cleanup
        ;;
    health)
        health_check "http://localhost/health"
        ;;
    *)
        main
        ;;
esac
