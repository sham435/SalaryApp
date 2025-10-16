#!/bin/bash
# ============================================
# Jatan Salary Management System - macOS Launcher
# ============================================

# Change to script directory
cd "$(dirname "$0")"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Jatan Salary Management System                       ║"
echo "║  Starting Full Stack...                               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo ""
    echo "Please install Docker Desktop from:"
    echo "https://www.docker.com/products/docker-desktop"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check Docker daemon
if ! docker info &> /dev/null; then
    echo "❌ Docker Desktop is not running!"
    echo ""
    echo "Please start Docker Desktop and try again."
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if images need to be loaded
if [ -f "jatan_stack.tar" ]; then
    echo "📦 Loading Docker images..."
    docker load -i jatan_stack.tar
    echo "✅ Images loaded"
    echo ""
fi

# Copy .env if doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠️  Created .env file from template"
        echo "   Please edit .env with your configuration"
        echo ""
    fi
fi

# Start stack
echo "🚀 Starting services..."
echo ""

docker compose -f docker-compose.production.yml --profile monitoring --profile admin up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║  ✅ Stack started successfully!                        ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "Access URLs:"
    echo "  - Grafana:   http://localhost:3000 (admin/admin)"
    echo "  - RabbitMQ:  http://localhost:15672 (admin/admin123)"
    echo "  - Flower:    http://localhost:5555"
    echo "  - PgAdmin:   http://localhost:5050"
    echo ""
    echo "Opening Grafana in your browser..."
    sleep 3
    open http://localhost:3000
else
    echo ""
    echo "❌ Failed to start stack"
    echo "Please check Docker Desktop and try again"
fi

echo ""
read -p "Press Enter to close this window..."


