#!/bin/bash
# Quick script to create jatan_stack.tar

set -e

echo "🔨 Creating jatan_stack.tar..."
echo ""

# Pull base images
echo "📥 Pulling base images..."
docker pull postgres:16-alpine
docker pull redis:7-alpine
docker pull rabbitmq:3-management-alpine
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
docker pull prom/node-exporter:latest
docker pull dpage/pgadmin4:latest

echo ""
echo "💾 Exporting images to jatan_stack.tar..."
docker save \
  postgres:16-alpine \
  redis:7-alpine \
  rabbitmq:3-management-alpine \
  prom/prometheus:latest \
  grafana/grafana:latest \
  prom/node-exporter:latest \
  dpage/pgadmin4:latest \
  -o jatan_stack.tar

echo ""
echo "✅ Created jatan_stack.tar"
ls -lh jatan_stack.tar
echo ""
echo "Done! You can now use jatan_stack.tar for installation packages."
