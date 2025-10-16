#!/usr/bin/env bash
# ============================================
# Jatan Jewellery - Cross-Platform Build Script
# For macOS and Linux
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Banner
echo "============================================"
echo "  Jatan Jewellery - Salary Management"
echo "  Docker Deployment Script"
echo "============================================"
echo ""

# Check Docker installation
print_info "Checking Docker installation..."
if ! command_exists docker; then
    print_error "Docker is not installed!"
    echo ""
    echo "Please install Docker:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  brew install --cask docker"
        echo "  Or download from: https://www.docker.com/products/docker-desktop"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "  curl -fsSL https://get.docker.com | sh"
        echo "  sudo usermod -aG docker \$USER"
    fi
    exit 1
fi
print_success "Docker is installed: $(docker --version)"

# Check Docker Compose
print_info "Checking Docker Compose..."
if ! command_exists docker-compose && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed!"
    echo ""
    echo "Please install Docker Compose:"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi
print_success "Docker Compose is available"

# Check if Docker daemon is running
print_info "Checking Docker daemon..."
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running!"
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Please start Docker Desktop"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Start Docker with: sudo systemctl start docker"
    fi
    exit 1
fi
print_success "Docker daemon is running"

# Change to script directory
cd "$(dirname "$0")/.."

# Check for .env file
print_info "Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    if [ -f "env.docker.example" ]; then
        print_info "Copying env.docker.example to .env..."
        cp env.docker.example .env
        print_warning "Please update .env with your configuration before proceeding!"
        echo ""
        echo "Edit .env and update:"
        echo "  - DB_PASSWORD"
        echo "  - CRM_API_KEY (if using CRM integration)"
        echo ""
        read -p "Press Enter after updating .env to continue, or Ctrl+C to cancel..."
    else
        print_error "env.docker.example not found!"
        exit 1
    fi
fi
print_success ".env file found"

# Parse command line arguments
ACTION=${1:-up}
WITH_PGADMIN=${2:-false}

# Build and run
echo ""
print_info "Starting deployment..."
echo ""

case "$ACTION" in
    up|start)
        print_info "Building and starting services..."
        if [ "$WITH_PGADMIN" = "admin" ]; then
            docker-compose --env-file .env --profile admin up --build -d
            print_success "Services started (including PgAdmin)"
            echo ""
            echo "Access PgAdmin at: http://localhost:5050"
            echo "  Email: admin@jatan.com (change in .env)"
            echo "  Password: Check PGADMIN_PASSWORD in .env"
        else
            docker-compose --env-file .env up --build -d
            print_success "Services started"
        fi
        ;;

    down|stop)
        print_info "Stopping services..."
        docker-compose down
        print_success "Services stopped"
        ;;

    restart)
        print_info "Restarting services..."
        docker-compose down
        docker-compose --env-file .env up --build -d
        print_success "Services restarted"
        ;;

    logs)
        print_info "Showing logs..."
        docker-compose logs -f
        ;;

    clean)
        print_warning "This will remove all containers, volumes, and data!"
        read -p "Are you sure? (yes/no): " -r
        echo
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            docker-compose down -v
            print_success "Cleaned up all containers and volumes"
        else
            print_info "Cleanup cancelled"
        fi
        ;;

    backup)
        print_info "Creating database backup..."
        docker exec jatan_postgres pg_dump -U salary_admin labor_salary_db > "backups/backup_$(date +%Y%m%d_%H%M%S).sql"
        print_success "Backup created in ./backups/"
        ;;

    *)
        echo "Usage: $0 {up|down|restart|logs|clean|backup} [admin]"
        echo ""
        echo "Commands:"
        echo "  up/start    - Build and start services"
        echo "  down/stop   - Stop services"
        echo "  restart     - Restart services"
        echo "  logs        - Show container logs"
        echo "  clean       - Remove all containers and volumes"
        echo "  backup      - Create database backup"
        echo ""
        echo "Options:"
        echo "  admin       - Also start PgAdmin for database management"
        echo ""
        echo "Examples:"
        echo "  $0 up"
        echo "  $0 up admin"
        echo "  $0 logs"
        echo "  $0 backup"
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
echo "Application URLs:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Application: localhost:8000"
if [ "$WITH_PGADMIN" = "admin" ]; then
    echo "  - PgAdmin: http://localhost:5050"
fi
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop: docker-compose down"
echo "  - Access PostgreSQL: docker exec -it jatan_postgres psql -U salary_admin -d labor_salary_db"
echo ""


