#!/bin/bash

# Docker Build and Run Script for Cold Chain Dispatch System

set -e

echo "🐳 Cold Chain Dispatch System - Docker Setup"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
    read -p "Press enter to continue after editing .env..."
fi

# Parse command line arguments
COMMAND=${1:-up}

case $COMMAND in
    build)
        echo -e "${YELLOW}🔨 Building Docker images...${NC}"
        docker-compose build --no-cache
        echo -e "${GREEN}✓ Build complete${NC}"
        ;;
    
    up|start)
        echo -e "${YELLOW}🚀 Starting services...${NC}"
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✓ Services started${NC}"
        echo ""
        echo "📊 Service URLs:"
        echo "  - Frontend: http://localhost:80"
        echo "  - Backend API: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - PostgreSQL: localhost:5432"
        echo "  - Redis: localhost:6379"
        echo ""
        echo "📝 View logs: docker-compose logs -f"
        ;;
    
    down|stop)
        echo -e "${YELLOW}🛑 Stopping services...${NC}"
        docker-compose down
        echo -e "${GREEN}✓ Services stopped${NC}"
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 Restarting services...${NC}"
        docker-compose restart
        echo -e "${GREEN}✓ Services restarted${NC}"
        ;;
    
    logs)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            docker-compose logs -f
        else
            docker-compose logs -f $SERVICE
        fi
        ;;
    
    ps|status)
        echo "📊 Service Status:"
        docker-compose ps
        ;;
    
    clean)
        echo -e "${YELLOW}🧹 Cleaning up...${NC}"
        read -p "This will remove all containers, volumes, and images. Continue? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker system prune -af
            echo -e "${GREEN}✓ Cleanup complete${NC}"
        else
            echo "Cancelled"
        fi
        ;;
    
    shell)
        SERVICE=${2:-backend}
        echo -e "${YELLOW}🐚 Opening shell in $SERVICE...${NC}"
        docker-compose exec $SERVICE sh
        ;;
    
    help|*)
        echo "Usage: ./docker-run.sh [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  build      - Build Docker images"
        echo "  up/start   - Start all services"
        echo "  down/stop  - Stop all services"
        echo "  restart    - Restart all services"
        echo "  logs       - View logs (optional: specify service)"
        echo "  ps/status  - Show service status"
        echo "  clean      - Remove all containers, volumes, and images"
        echo "  shell      - Open shell in service (default: backend)"
        echo "  help       - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./docker-run.sh build"
        echo "  ./docker-run.sh up"
        echo "  ./docker-run.sh logs backend"
        echo "  ./docker-run.sh shell frontend"
        ;;
esac
