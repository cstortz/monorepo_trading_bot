"""
Tests for the Hello World service.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from main import app

client = TestClient(app)

def test_hello_endpoint():
    """Test the hello endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello from the Trading Bot Monorepo!"
    assert data["service"] == "hello-world"
    assert data["version"] == "1.0.0"

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "hello-world"

def test_service_info():
    """Test the service info endpoint."""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "hello-world"
    assert "environment" in data
    assert "debug" in data

def test_logging_test():
    """Test the logging test endpoint."""
    response = client.get("/logs/test")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logging test completed - check the logs!"

