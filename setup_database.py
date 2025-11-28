#!/usr/bin/env python3
"""
Database Setup Script for Trading Bot Monorepo
Initializes the database using the web service API
"""

import sys
import argparse
from datetime import datetime
from database_client import DatabaseClient, TradingBotDatabase


def setup_database(environment: str = "dev", force: bool = False):
    """Set up the database for the specified environment."""
    
    print(f"🚀 Setting up Trading Bot Database - {environment.upper()} Environment")
    print("=" * 60)
    
    try:
        with DatabaseClient() as client:
            # Check database health
            print("1. Checking database health...")
            health = client.health_check()
            if health.get("status") != "healthy":
                print(f"❌ Database is not healthy: {health}")
                return False
            print("✅ Database is healthy")
            
            # Get database info
            print("\n2. Getting database information...")
            db_info = client.get_database_info()
            print(f"   Database: {db_info.get('database', 'Unknown')}")
            print(f"   Version: {db_info.get('version', 'Unknown')}")
            print(f"   User: {db_info.get('user', 'Unknown')}")
            print(f"   Host: {db_info.get('host', 'Unknown')}")
            print(f"   Port: {db_info.get('port', 'Unknown')}")
            
            # Check existing tables
            print("\n3. Checking existing tables...")
            tables_result = client.get_tables()
            existing_tables = [table['table_name'] for table in tables_result.get('tables', [])]
            print(f"   Found {len(existing_tables)} existing tables")
            
            if existing_tables and not force:
                print("   ⚠️  Tables already exist. Use --force to recreate them.")
                return True
            
            # Create trading bot database instance
            trading_db = TradingBotDatabase(client)
            
            # Create tables
            print(f"\n4. Creating {environment} tables...")
            if trading_db.create_tables(environment):
                print("✅ Tables created successfully")
            else:
                print("❌ Failed to create tables")
                return False
            
            # Seed data
            print(f"\n5. Seeding {environment} data...")
            if trading_db.seed_data(environment):
                print("✅ Data seeded successfully")
            else:
                print("❌ Failed to seed data")
                return False
            
            # Verify setup
            print("\n6. Verifying setup...")
            
            # Check symbols
            symbols = trading_db.get_symbols(limit=5)
            print(f"   Symbols: {len(symbols)} found")
            if symbols:
                print(f"   Sample: {symbols[0]['symbol']} - {symbols[0]['name']}")
            
            # Check data sources
            data_sources_sql = "SELECT COUNT(*) as count FROM data_sources"
            result = client.execute_prepared_select(data_sources_sql)
            if result.get("success"):
                count = result.get("data", [{}])[0].get("count", 0)
                print(f"   Data sources: {count} configured")
            
            # Check market sessions
            sessions_sql = "SELECT COUNT(*) as count FROM market_sessions"
            result = client.execute_prepared_select(sessions_sql)
            if result.get("success"):
                count = result.get("data", [{}])[0].get("count", 0)
                print(f"   Market sessions: {count} configured")
            
            print(f"\n✅ Database setup completed successfully for {environment} environment!")
            print("\n📋 Next steps:")
            print("   1. Run tests: python test_database_crud.py")
            print("   2. Start market-data service")
            print("   3. Configure API keys in environment variables")
            
            return True
            
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def test_database():
    """Test the database setup."""
    print("🧪 Testing Database Setup")
    print("=" * 30)
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            
            # Test basic operations
            print("1. Testing symbol operations...")
            symbols = trading_db.get_symbols(limit=3)
            print(f"   Found {len(symbols)} symbols")
            
            if symbols:
                symbol = symbols[0]
                print(f"   Testing with symbol: {symbol['symbol']}")
                
                # Test getting symbol by name
                found_symbol = trading_db.get_symbol_by_name(symbol['symbol'])
                if found_symbol:
                    print("   ✅ Symbol lookup successful")
                else:
                    print("   ❌ Symbol lookup failed")
            
            # Test market data
            print("\n2. Testing market data operations...")
            if symbols:
                market_data = trading_db.get_market_data(symbols[0]['symbol'], "1d", limit=3)
                print(f"   Found {len(market_data)} market data records")
            
            # Test real-time prices
            print("\n3. Testing real-time prices...")
            prices = trading_db.get_real_time_prices(limit=3)
            print(f"   Found {len(prices)} real-time price records")
            
            print("\n✅ Database tests completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Trading Bot Database Setup")
    parser.add_argument("--env", choices=["dev", "prod"], default="dev", 
                       help="Environment to set up (default: dev)")
    parser.add_argument("--force", action="store_true", 
                       help="Force recreation of existing tables")
    parser.add_argument("--test", action="store_true", 
                       help="Run database tests only")
    
    args = parser.parse_args()
    
    if args.test:
        success = test_database()
    else:
        success = setup_database(args.env, args.force)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
