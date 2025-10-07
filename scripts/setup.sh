#!/bin/bash

# Trading Bot Monorepo Setup Script

set -e

echo "🚀 Setting up Trading Bot Monorepo..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp env.example .env
fi

echo "✅ Setup complete!"
echo ""
echo "To start development:"
echo "  docker-compose up -d"
echo ""
echo "To run tests:"
echo "  python -m pytest services/hello-world/tests/"
echo ""
echo "To deploy to Kubernetes:"
echo "  kubectl apply -f k8s/"
