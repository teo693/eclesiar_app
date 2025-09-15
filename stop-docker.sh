#!/bin/bash
# Eclesiar App Docker Stop Script
# Copyright (c) 2025 Teo693
# Licensed under the MIT License - see LICENSE file for details.

echo "🛑 Stopping Eclesiar App Docker Container"
echo "=========================================="

# Stop and remove containers
echo "🔄 Stopping containers..."
docker-compose down

echo "✅ Eclesiar App has been stopped"
echo ""
echo "📊 To start again, run: ./start-docker.sh"
echo "📝 To view logs from previous run: docker-compose logs eclesiar-scheduler"
echo "🗑️  To remove all data: docker-compose down -v"
