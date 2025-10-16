#!/usr/bin/env bash
# ============================================
# Jatan Salary Management System
# Linux Installer Script
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
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Jatan Salary Management System                       ║"
echo "║  Linux Installer                                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root for system-wide install
if [ "$EUID" -eq 0 ]; then
    INSTALL_DIR="/opt/jatan_stack"
    print_info "Installing system-wide to $INSTALL_DIR"
else
    INSTALL_DIR="$HOME/jatan_stack"
    print_info "Installing for current user to $INSTALL_DIR"
fi

# Check Docker
print_info "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo ""
    echo "Install Docker with:"
    echo "  curl -fsSL https://get.docker.com | sh"
    echo "  sudo usermod -aG docker \$USER"
    echo ""
    exit 1
fi
print_success "Docker is installed"

# Check Docker daemon
print_info "Checking Docker daemon..."
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running!"
    echo ""
    echo "Start Docker with:"
    echo "  sudo systemctl start docker"
    echo ""
    exit 1
fi
print_success "Docker daemon is running"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed!"
    echo ""
    echo "Install with:"
    echo "  sudo apt install docker-compose-plugin"
    echo ""
    exit 1
fi
print_success "Docker Compose is available"

# Create installation directory
print_info "Creating installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Extract files (if run from archive)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/jatan_stack.tar" ]; then
    print_info "Copying installation files..."
    cp "$SCRIPT_DIR/jatan_stack.tar" .
    cp "$SCRIPT_DIR/docker-compose.production.yml" .
    cp "$SCRIPT_DIR/.env.example" .
    cp -r "$SCRIPT_DIR/monitoring" . 2>/dev/null || true
fi

# Load Docker images
if [ -f "jatan_stack.tar" ]; then
    print_info "Loading Docker images (this may take a few minutes)..."
    docker load -i jatan_stack.tar
    print_success "Docker images loaded"
else
    print_warning "jatan_stack.tar not found, will pull images from registry"
fi

# Create .env if doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env with your configuration"
    fi
fi

# Create launcher script
print_info "Creating launcher script..."
cat > "$INSTALL_DIR/start.sh" << 'LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")"
docker compose -f docker-compose.production.yml --profile monitoring --profile admin up -d
echo ""
echo "✅ Stack started!"
echo "Access Grafana: http://localhost:3000"
LAUNCHER

chmod +x "$INSTALL_DIR/start.sh"

# Create stop script
cat > "$INSTALL_DIR/stop.sh" << 'STOPPER'
#!/bin/bash
cd "$(dirname "$0")"
docker compose -f docker-compose.production.yml down
echo "✅ Stack stopped"
STOPPER

chmod +x "$INSTALL_DIR/stop.sh"

# Create desktop entry (if running with GUI)
if [ -n "$DISPLAY" ] && [ ! "$EUID" -eq 0 ]; then
    print_info "Creating desktop launcher..."
    mkdir -p "$HOME/.local/share/applications"

    cat > "$HOME/.local/share/applications/jatan-salary.desktop" << DESKTOP
[Desktop Entry]
Version=1.0
Type=Application
Name=Jatan Salary System
Comment=Salary Management System
Exec=$INSTALL_DIR/start.sh
Icon=$INSTALL_DIR/jatan_icon.png
Terminal=true
Categories=Office;Finance;
DESKTOP

    print_success "Desktop launcher created"
fi

# Start stack
print_info "Would you like to start the stack now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    print_info "Starting stack..."
    cd "$INSTALL_DIR"
    ./start.sh

    echo ""
    print_success "Installation complete!"
    echo ""
    echo "Access URLs:"
    echo "  - Grafana:   http://localhost:3000 (admin/admin)"
    echo "  - RabbitMQ:  http://localhost:15672 (admin/admin123)"
    echo "  - Flower:    http://localhost:5555"
    echo "  - PgAdmin:   http://localhost:5050"
    echo ""
else
    print_success "Installation complete!"
    echo ""
    echo "Start the stack with:"
    echo "  cd $INSTALL_DIR && ./start.sh"
fi

echo ""
print_info "Installation location: $INSTALL_DIR"
print_info "To uninstall, run: rm -rf $INSTALL_DIR"
echo ""


