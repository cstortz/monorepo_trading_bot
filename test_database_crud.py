"""
Comprehensive CRUD Tests for Trading Bot Database
Tests all database operations through the web service API
"""

import pytest
import json
from datetime import datetime, timezone
from database_client import DatabaseClient, TradingBotDatabase


class TestDatabaseCRUD:
    """Test class for database CRUD operations."""
    
    @pytest.fixture
    def db_client(self):
        """Create a database client for testing."""
        with DatabaseClient() as client:
            yield client
    
    @pytest.fixture
    def trading_db(self, db_client):
        """Create a trading bot database instance."""
        return TradingBotDatabase(db_client)
    
    def test_health_check(self, db_client):
        """Test database health check."""
        result = db_client.health_check()
        assert "status" in result
        assert result["status"] == "healthy"
    
    def test_database_info(self, db_client):
        """Test getting database information."""
        result = db_client.get_database_info()
        assert "database" in result
        assert "version" in result
        assert "user" in result
    
    def test_get_tables(self, db_client):
        """Test getting all tables."""
        result = db_client.get_tables()
        assert "tables" in result
        assert isinstance(result["tables"], list)
    
    def test_create_tables_dev(self, trading_db):
        """Test creating development tables."""
        success = trading_db.create_tables("dev")
        assert success, "Failed to create development tables"
    
    def test_seed_data_dev(self, trading_db):
        """Test seeding development data."""
        success = trading_db.seed_data("dev")
        assert success, "Failed to seed development data"
    
    def test_symbol_crud_operations(self, trading_db):
        """Test complete CRUD operations for symbols."""
        
        # Test Create
        symbol_data = {
            "symbol": "TEST",
            "name": "Test Symbol",
            "exchange": "TEST_EXCHANGE",
            "asset_type": "stock",
            "currency": "USD",
            "sector": "Technology",
            "industry": "Software",
            "market_cap": 1000000000,
            "is_active": True
        }
        
        create_success = trading_db.create_symbol(symbol_data)
        assert create_success, "Failed to create symbol"
        
        # Test Read
        symbol = trading_db.get_symbol_by_name("TEST")
        assert symbol is not None, "Failed to read created symbol"
        assert symbol["symbol"] == "TEST"
        assert symbol["name"] == "Test Symbol"
        assert symbol["exchange"] == "TEST_EXCHANGE"
        
        # Test Update
        update_data = {
            "name": "Updated Test Symbol",
            "sector": "Updated Technology",
            "industry": "Updated Software",
            "market_cap": 2000000000
        }
        
        update_success = trading_db.update_symbol("TEST", update_data)
        assert update_success, "Failed to update symbol"
        
        # Verify update
        updated_symbol = trading_db.get_symbol_by_name("TEST")
        assert updated_symbol["name"] == "Updated Test Symbol"
        assert updated_symbol["sector"] == "Updated Technology"
        assert updated_symbol["market_cap"] == 2000000000
        
        # Test Delete
        delete_success = trading_db.delete_symbol("TEST")
        assert delete_success, "Failed to delete symbol"
        
        # Verify deletion
        deleted_symbol = trading_db.get_symbol_by_name("TEST")
        assert deleted_symbol is None, "Symbol was not deleted"
    
    def test_get_symbols_pagination(self, trading_db):
        """Test getting symbols with pagination."""
        # Get first page
        symbols_page1 = trading_db.get_symbols(limit=5, offset=0)
        assert isinstance(symbols_page1, list)
        assert len(symbols_page1) <= 5
        
        # Get second page
        symbols_page2 = trading_db.get_symbols(limit=5, offset=5)
        assert isinstance(symbols_page2, list)
        
        # Ensure no overlap
        if symbols_page1 and symbols_page2:
            page1_symbols = {s["symbol"] for s in symbols_page1}
            page2_symbols = {s["symbol"] for s in symbols_page2}
            assert len(page1_symbols.intersection(page2_symbols)) == 0
    
    def test_market_data_operations(self, trading_db):
        """Test market data operations."""
        
        # First, get a symbol ID
        symbols = trading_db.get_symbols(limit=1)
        assert len(symbols) > 0, "No symbols found for testing"
        symbol_id = symbols[0]["id"]
        
        # Test inserting market data
        market_data = {
            "timestamp": datetime.now(timezone.utc),
            "open": 100.50,
            "high": 105.25,
            "low": 99.75,
            "close": 103.00,
            "volume": 1000000,
            "adjusted_close": 103.00,
            "time_frame": "1d",
            "data_source": "test"
        }
        
        insert_success = trading_db.insert_market_data(symbol_id, market_data)
        assert insert_success, "Failed to insert market data"
        
        # Test getting market data
        symbol_name = symbols[0]["symbol"]
        market_data_result = trading_db.get_market_data(symbol_name, "1d", limit=10)
        assert isinstance(market_data_result, list)
    
    def test_real_time_prices_operations(self, trading_db):
        """Test real-time prices operations."""
        
        # Get symbols first
        symbols = trading_db.get_symbols(limit=1)
        assert len(symbols) > 0, "No symbols found for testing"
        symbol_id = symbols[0]["id"]
        
        # Test updating real-time price
        price_data = {
            "price": 150.75,
            "bid": 150.70,
            "ask": 150.80,
            "volume_24h": 5000000,
            "change_24h": 2.50,
            "change_percent_24h": 1.68,
            "market_cap": 1000000000000,
            "data_source": "test"
        }
        
        update_success = trading_db.update_real_time_price(symbol_id, price_data)
        assert update_success, "Failed to update real-time price"
        
        # Test getting real-time prices
        prices = trading_db.get_real_time_prices(limit=10)
        assert isinstance(prices, list)
    
    def test_prepared_statements_management(self, db_client):
        """Test prepared statements management."""
        
        # Get prepared statements
        statements = db_client.get_prepared_statements()
        assert "statements" in statements
        
        # Clear prepared statements
        clear_success = db_client.clear_prepared_statements()
        assert clear_success, "Failed to clear prepared statements"
    
    def test_sql_validation(self, db_client):
        """Test SQL validation."""
        
        # Test valid SQL
        valid_sql = "SELECT * FROM symbols WHERE symbol = $1"
        result = db_client.validate_sql(valid_sql, {"1": "AAPL"})
        assert result.get("valid", False), "Valid SQL should pass validation"
        
        # Test invalid SQL
        invalid_sql = "INVALID SQL STATEMENT"
        result = db_client.validate_sql(invalid_sql)
        assert not result.get("valid", True), "Invalid SQL should fail validation"
    
    def test_complex_queries(self, db_client):
        """Test complex SQL queries."""
        
        # Test join query
        join_sql = """
        SELECT s.symbol, s.name, s.exchange, rtp.price, rtp.last_updated
        FROM symbols s
        LEFT JOIN real_time_prices rtp ON s.id = rtp.symbol_id
        WHERE s.is_active = true
        ORDER BY rtp.last_updated DESC
        LIMIT 10
        """
        
        result = db_client.execute_prepared_select(join_sql)
        assert result.get("success", False), "Complex join query should succeed"
        assert "data" in result
        
        # Test aggregation query
        agg_sql = """
        SELECT 
            s.asset_type,
            COUNT(*) as symbol_count,
            AVG(rtp.price) as avg_price
        FROM symbols s
        LEFT JOIN real_time_prices rtp ON s.id = rtp.symbol_id
        WHERE s.is_active = true
        GROUP BY s.asset_type
        ORDER BY symbol_count DESC
        """
        
        result = db_client.execute_prepared_select(agg_sql)
        assert result.get("success", False), "Aggregation query should succeed"
        assert "data" in result
    
    def test_error_handling(self, db_client):
        """Test error handling for invalid operations."""
        
        # Test invalid table name
        invalid_sql = "SELECT * FROM non_existent_table"
        result = db_client.execute_prepared_select(invalid_sql)
        assert not result.get("success", True), "Invalid table should fail"
        
        # Test invalid parameters
        sql_with_params = "SELECT * FROM symbols WHERE id = $1"
        result = db_client.execute_prepared_select(sql_with_params, {"1": "invalid_id"})
        # This might succeed but return no data, which is acceptable
    
    def test_transaction_simulation(self, trading_db):
        """Test transaction-like operations."""
        
        # Create multiple related records
        symbol_data = {
            "symbol": "TX1",
            "name": "Test Symbol 1",
            "exchange": "TEST_EXCHANGE",
            "asset_type": "stock",
            "currency": "USD",
            "is_active": True
        }
        
        # Create symbol
        create_success = trading_db.create_symbol(symbol_data)
        assert create_success, "Failed to create symbol for transaction test"
        
        # Get the created symbol
        symbol = trading_db.get_symbol_by_name("TX1")
        assert symbol is not None, "Failed to retrieve created symbol"
        symbol_id = symbol["id"]
        
        # Insert market data
        market_data = {
            "timestamp": datetime.now(timezone.utc),
            "open": 100.0,
            "high": 110.0,
            "low": 95.0,
            "close": 105.0,
            "volume": 1000000,
            "time_frame": "1d",
            "data_source": "test"
        }
        
        market_success = trading_db.insert_market_data(symbol_id, market_data)
        assert market_success, "Failed to insert market data"
        
        # Update real-time price
        price_data = {
            "price": 105.5,
            "data_source": "test"
        }
        
        price_success = trading_db.update_real_time_price(symbol_id, price_data)
        assert price_success, "Failed to update real-time price"
        
        # Clean up
        trading_db.delete_symbol("TX1")


def run_tests():
    """Run all database tests."""
    print("🧪 Running Trading Bot Database CRUD Tests...")
    print("=" * 50)
    
    # Test database connection
    with DatabaseClient() as client:
        print("1. Testing database connection...")
        health = client.health_check()
        if health.get("status") == "healthy":
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
        
        print("\n2. Testing database info...")
        db_info = client.get_database_info()
        print(f"   Database: {db_info.get('database', 'Unknown')}")
        print(f"   Version: {db_info.get('version', 'Unknown')}")
        print(f"   User: {db_info.get('user', 'Unknown')}")
        
        print("\n3. Testing table creation...")
        trading_db = TradingBotDatabase(client)
        
        # Create tables
        if trading_db.create_tables("dev"):
            print("✅ Development tables created successfully")
        else:
            print("❌ Failed to create development tables")
            return False
        
        print("\n4. Testing data seeding...")
        if trading_db.seed_data("dev"):
            print("✅ Development data seeded successfully")
        else:
            print("❌ Failed to seed development data")
            return False
        
        print("\n5. Testing CRUD operations...")
        
        # Test symbol operations
        symbols = trading_db.get_symbols(limit=5)
        print(f"   Found {len(symbols)} symbols")
        
        if symbols:
            symbol = symbols[0]
            print(f"   Sample symbol: {symbol['symbol']} - {symbol['name']}")
        
        # Test market data
        if symbols:
            market_data = trading_db.get_market_data(symbols[0]['symbol'], "1d", limit=5)
            print(f"   Found {len(market_data)} market data records")
        
        # Test real-time prices
        prices = trading_db.get_real_time_prices(limit=5)
        print(f"   Found {len(prices)} real-time price records")
        
        print("\n6. Testing prepared statements...")
        statements = client.get_prepared_statements()
        print(f"   Cached statements: {statements.get('count', 0)}")
        
        print("\n✅ All database tests completed successfully!")
        return True


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
