#!/bin/bash

# Test script for Trading Bot Monorepo

set -e

echo "🧪 Running tests for Trading Bot Monorepo..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Install test dependencies
echo "📚 Installing test dependencies..."
pip install pytest pytest-asyncio httpx

# Run tests for hello-world service
echo "🔍 Running tests for hello-world service..."
python -m pytest services/hello-world/tests/ -v

echo "✅ All tests passed!"

