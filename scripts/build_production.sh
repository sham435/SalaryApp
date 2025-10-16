#!/usr/bin/env bash
# ============================================
# Production Deployment Script
# PostgreSQL + Redis + RabbitMQ + Celery
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
echo "============================================"
echo "  Jatan Jewellery - Production Deployment"
echo "  PostgreSQL + Redis + RabbitMQ + Celery"
echo "============================================"
echo ""

# Check Docker
print_info "Checking Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker not installed!"
    exit 1
fi
print_success "Docker is installed"

# Check Docker Compose
if ! command -v docker-compose && ! docker compose version &> /dev/null; then
    print_error "Docker Compose not installed!"
    exit 1
fi
print_success "Docker Compose is available"

# Check Docker daemon
print_info "Checking Docker daemon..."
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running!"
    exit 1
fi
print_success "Docker daemon is running"

# Change to project directory
cd "$(dirname "$0")/.."

# Check .env file
print_info "Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    if [ -f "env.production.example" ]; then
        print_info "Copying env.production.example to .env..."
        cp env.production.example .env
        print_warning "Please update .env before proceeding!"
        read -p "Press Enter after updating .env to continue..."
    else
        print_error "env.production.example not found!"
        exit 1
    fi
fi
print_success ".env file found"

# Parse command
ACTION=${1:-up}
WITH_MONITORING=${2:-false}
WITH_ADMIN=${3:-false}

echo ""
print_info "Starting production deployment..."
echo ""

# Build profile arguments
PROFILES=""
if [ "$WITH_MONITORING" = "monitoring" ]; then
    PROFILES="$PROFILES --profile monitoring"
fi
if [ "$WITH_ADMIN" = "admin" ]; then
    PROFILES="$PROFILES --profile admin"
fi

case "$ACTION" in
    up|start)
        print_info "Building and starting services..."
        docker-compose -f docker-compose.production.yml --env-file .env $PROFILES up --build -d
        print_success "Services started"
        ;;
    
    down|stop)
        print_info "Stopping services..."
        docker-compose -f docker-compose.production.yml down
        print_success "Services stopped"
        ;;
    
    restart)
        print_info "Restarting services..."
        docker-compose -f docker-compose.production.yml down
        docker-compose -f docker-compose.production.yml --env-file .env $PROFILES up --build -d
        print_success "Services restarted"
        ;;
    
    logs)
        print_info "Showing logs..."
        docker-compose -f docker-compose.production.yml logs -f
        ;;
    
    scale)
        WORKERS=${2:-3}
        print_info "Scaling Celery workers to $WORKERS..."
        docker-compose -f docker-compose.production.yml up -d --scale celery_worker=$WORKERS
        print_success "Scaled to $WORKERS workers"
        ;;
    
    status)
        print_info "Service status:"
        docker-compose -f docker-compose.production.yml ps
        ;;
    
    backup)
        print_info "Triggering database backup..."
        docker exec jatan_celery_worker celery -A celery_app.celery call tasks.backup_database
        print_success "Backup task queued"
        ;;
    
    monitor)
        print_info "Opening monitoring dashboards..."
        echo "RabbitMQ Management: http://localhost:15672"
        echo "Flower (Celery): http://localhost:5555"
        echo "PgAdmin: http://localhost:5050"
        ;;
    
    test-celery)
        print_info "Testing Celery worker..."
        docker exec jatan_celery_worker celery -A celery_app.celery inspect ping
        ;;
    
    clean)
        print_warning "This will remove all containers and volumes!"
        read -p "Are you sure? (yes/no): " -r
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            docker-compose -f docker-compose.production.yml down -v
            print_success "Cleaned up"
        fi
        ;;
    
    *)
        echo "Usage: $0 {up|down|restart|logs|scale|status|backup|monitor|test-celery|clean} [options]"
        echo ""
        echo "Commands:"
        echo "  up/start      - Start all services"
        echo "  down/stop     - Stop all services"
        echo "  restart       - Restart all services"
        echo "  logs          - View logs"
        echo "  scale N       - Scale Celery workers to N instances"
        echo "  status        - Show service status"
        echo "  backup        - Trigger database backup"
        echo "  monitor       - Show monitoring URLs"
        echo "  test-celery   - Test Celery worker connection"
        echo "  clean         - Remove all containers and volumes"
        echo ""
        echo "Options:"
        echo "  monitoring    - Start with Flower monitoring"
        echo "  admin         - Start with PgAdmin"
        echo ""
        echo "Examples:"
        echo "  $0 up"
        echo "  $0 up monitoring"
        echo "  $0 scale 5"
        echo "  $0 logs"
        exit 1
        ;;
esac

# Show container status
echo ""
print_info "Container Status:"
docker ps --filter "name=jatan_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
print_success "Deployment complete!"
echo ""
echo "Service URLs:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - RabbitMQ AMQP: localhost:5672"
echo "  - RabbitMQ Management: http://localhost:15672 (admin/admin123)"
echo "  - Application: localhost:8000"
if [ "$WITH_MONITORING" = "monitoring" ]; then
    echo "  - Flower: http://localhost:5555"
fi
if [ "$WITH_ADMIN" = "admin" ]; then
    echo "  - PgAdmin: http://localhost:5050"
fi
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  - Scale workers: $0 scale 5"
echo "  - Test Celery: $0 test-celery"
echo "  - Monitor tasks: $0 monitor"
echo ""


