#!/bin/bash
# Eclesiar App Docker Startup Script
# Copyright (c) 2025 Teo693
# Licensed under the MIT License - see LICENSE file for details.

set -e

echo "🐳 Eclesiar App Docker Setup"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f "docker.env.template" ]; then
        cp docker.env.template .env
        echo "✅ Created .env file from template"
        echo "📝 Please edit .env file with your configuration before continuing"
        echo "   - Set your AUTH_TOKEN"
        echo "   - Configure Google Sheets settings"
        echo "   - Place google_credentials.json in cred/ directory"
        exit 1
    else
        echo "❌ docker.env.template not found. Cannot create .env file."
        exit 1
    fi
fi

# Check if credentials directory exists
if [ ! -d "cred" ]; then
    echo "📁 Creating cred directory..."
    mkdir -p cred
fi

# Check if google_credentials.json exists
if [ ! -f "cred/google_credentials.json" ]; then
    echo "⚠️  Google credentials not found in cred/google_credentials.json"
    echo "📝 Please place your Google Service Account credentials file there"
    echo "   See DOCKER_SETUP.md for detailed instructions"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs reports

# Build and start the container
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting Eclesiar scheduler..."
docker-compose up -d

echo "✅ Eclesiar App is now running!"
echo ""
echo "📊 The application will generate Google Sheets reports every 6 hours"
echo "📝 View logs with: docker-compose logs -f eclesiar-scheduler"
echo "🛑 Stop with: docker-compose down"
echo ""
echo "🔍 First report will be generated immediately, then every 6 hours"
echo "📋 Check the logs to see the first report generation"

# Show initial logs
echo ""
echo "📋 Initial logs:"
docker-compose logs --tail=20 eclesiar-scheduler
