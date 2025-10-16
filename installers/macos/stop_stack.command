#!/bin/bash
# ============================================
# Jatan Salary Management System - Shutdown
# ============================================

cd "$(dirname "$0")"

echo ""
echo "Stopping Jatan Stack..."
echo ""

docker compose -f docker-compose.production.yml down

echo ""
echo "✅ Stack stopped successfully"
echo ""
read -p "Press Enter to close..."


