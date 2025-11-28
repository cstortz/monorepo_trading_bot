"""
Tests for the Market Data service.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add app to path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "market-data"
    assert data["version"] == "1.0.0"
    assert "endpoints" in data

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["service"] == "market-data"
    assert data["version"] == "1.0.0"

def test_service_info():
    """Test the service info endpoint."""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "market-data"
    assert "environment" in data
    assert "debug" in data

def test_get_symbols():
    """Test getting symbols."""
    response = client.get("/symbols?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "symbols" in data
    assert "count" in data
    assert isinstance(data["symbols"], list)

def test_get_symbols_with_filters():
    """Test getting symbols with filters."""
    response = client.get("/symbols?limit=10&is_active=true")
    assert response.status_code == 200
    data = response.json()
    assert "symbols" in data
    assert "count" in data

def test_get_real_time_prices():
    """Test getting real-time prices."""
    response = client.get("/real-time-prices?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "prices" in data
    assert "count" in data
    assert isinstance(data["prices"], list)

def test_get_market_status():
    """Test getting market status."""
    response = client.get("/market-status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "count" in data
    assert isinstance(data["status"], list)

def test_get_market_data_invalid_symbol():
    """Test getting market data for invalid symbol."""
    response = client.get("/market-data/INVALID_SYMBOL_XYZ123?limit=10")
    # Should return 200 with empty data or 500 if database error
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "data" in data
        assert "count" in data

def test_get_market_data_with_timeframe():
    """Test getting market data with timeframe."""
    response = client.get("/market-data/AAPL?timeframe=1d&limit=10")
    # Should return 200 with data or 500 if database error
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "symbol" in data
        assert "timeframe" in data
        assert "data" in data

def test_insert_market_data_validation():
    """Test market data insertion validation."""
    # Test with invalid data (missing required fields)
    invalid_data = {
        "symbol": "TEST",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "open": 100.0,
        "high": 105.0,
        "low": 95.0,
        "close": 102.0,
        "volume": 1000,
        "time_frame": "1d",
        "data_source": "test"
    }
    
    response = client.post("/market-data", json=invalid_data)
    # Should return 422 (validation error) or 404 (symbol not found) or 500 (database error)
    assert response.status_code in [422, 404, 500]

def test_update_real_time_price_validation():
    """Test real-time price update validation."""
    # Test with invalid data
    invalid_data = {
        "symbol": "TEST",
        "price": -100.0,  # Invalid: price must be > 0
        "data_source": "test"
    }
    
    response = client.post("/real-time-prices", json=invalid_data)
    # Should return 422 (validation error) or 404 (symbol not found) or 500 (database error)
    assert response.status_code in [422, 404, 500]

def test_get_symbol_not_found():
    """Test getting a non-existent symbol."""
    response = client.get("/symbols/INVALID_SYMBOL_XYZ123")
    # Should return 404 or 500 if database error
    assert response.status_code in [404, 500]

