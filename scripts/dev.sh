#!/bin/bash

# Development script for Trading Bot Monorepo

set -e

echo "🔧 Starting development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "🐳 Building and starting services..."
docker compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
curl -f http://localhost:5000/health || echo "❌ Hello World service is not responding"
curl -f http://localhost:5001/health || echo "❌ Market Data service is not responding"

echo ""
echo "✅ Development environment is running!"
echo ""
echo "Services:"
echo "  Hello World: http://localhost:5000"
echo "  Market Data: http://localhost:5001"
echo ""
echo "Useful commands:"
echo "  View logs: docker compose logs -f"
echo "  Stop services: docker compose down"
echo "  Restart: docker compose restart"
