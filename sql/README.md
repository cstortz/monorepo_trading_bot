# Trading Bot Database Schema

This directory contains the complete database schema and setup for the Trading Bot monorepo using the database web service at `dev01.int.stortz.tech:8000`.

## 📁 Directory Structure

```
sql/
├── dev/
│   ├── 01_create_tables.sql      # Development table definitions
│   └── 02_seed_data.sql          # Development seed data
├── prod/
│   ├── 01_create_tables.sql      # Production table definitions
│   ├── 02_create_partitions.sql  # Production partitioning
│   └── 03_seed_data.sql          # Production seed data
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Set Up Development Database

```bash
# Set up development database
python setup_database.py --env dev

# Force recreation if tables exist
python setup_database.py --env dev --force
```

### 2. Set Up Production Database

```bash
# Set up production database
python setup_database.py --env prod

# Force recreation if tables exist
python setup_database.py --env prod --force
```

### 3. Test Database Operations

```bash
# Run comprehensive CRUD tests
python test_database_crud.py

# Test database setup only
python setup_database.py --test
```

## 📊 Database Schema Overview

### Core Tables

#### 1. **symbols** - Tradeable Instruments
- Stores all tradeable symbols (stocks, crypto, forex, indices)
- Includes metadata like exchange, sector, market cap
- Supports multiple asset types and currencies

#### 2. **market_data** - OHLCV Data
- Time-series data for all symbols
- Supports multiple timeframes (1m, 5m, 1h, 1d, etc.)
- Multiple data sources (Alpha Vantage, Yahoo Finance, Binance)
- **Production**: Partitioned by timestamp for performance

#### 3. **real_time_prices** - Current Prices
- Real-time price data
- Bid/ask spreads
- 24h volume and change data
- Market cap information

#### 4. **technical_indicators** - Calculated Indicators
- Moving averages (SMA, EMA)
- Oscillators (RSI, MACD, Stochastic)
- Volatility indicators (Bollinger Bands, ATR)
- Volume indicators (OBV)
- Trend indicators (ADX, CCI, Williams %R)

### Supporting Tables

- **market_sessions** - Trading session definitions
- **market_status** - Market open/close status
- **data_sources** - API configuration and rate limits

## 🔧 Database Web Service Integration

The database operations use the Prepared SQL Operations from your web service:

### Available Endpoints
- **Health Check**: `/admin/health`
- **Database Info**: `/admin/db-info`
- **Tables**: `/admin/tables`
- **Prepared SQL**: `/crud/prepared/execute`
- **Prepared SELECT**: `/crud/prepared/select`
- **Prepared INSERT**: `/crud/prepared/insert`
- **Prepared UPDATE**: `/crud/prepared/update`
- **Prepared DELETE**: `/crud/prepared/delete`
- **Validate SQL**: `/crud/prepared/validate`

### Python Client Usage

```python
from database_client import DatabaseClient, TradingBotDatabase

# Create client
with DatabaseClient() as client:
    # Check health
    health = client.health_check()
    
    # Create trading bot database
    trading_db = TradingBotDatabase(client)
    
    # Get symbols
    symbols = trading_db.get_symbols(limit=10)
    
    # Get market data
    market_data = trading_db.get_market_data("AAPL", "1d", limit=100)
    
    # Update real-time price
    trading_db.update_real_time_price(symbol_id, price_data)
```

## 📈 Production Optimizations

### Partitioning
- Monthly partitions for `market_data` table
- Automatic partition creation
- Efficient data archiving

### Indexes
- Composite indexes on (symbol_id, timestamp)
- Timeframe-specific indexes
- Data source indexes
- Real-time price indexes

### Views
- `latest_prices` - Current prices with symbol info
- `market_data_with_symbols` - OHLCV data with symbol details
- `technical_indicators_with_symbols` - Indicators with symbol info

## 🧪 Testing

### CRUD Operations Test
```bash
python test_database_crud.py
```

Tests include:
- ✅ Health check and database info
- ✅ Table creation and data seeding
- ✅ Symbol CRUD operations
- ✅ Market data operations
- ✅ Real-time price operations
- ✅ Complex queries and joins
- ✅ Error handling
- ✅ Prepared statements management

### Manual Testing
```python
# Test database connection
python -c "
from database_client import DatabaseClient
with DatabaseClient() as client:
    print('Health:', client.health_check())
    print('DB Info:', client.get_database_info())
"
```

## 🔍 Sample Queries

### Get Latest Prices
```sql
SELECT s.symbol, s.name, rtp.price, rtp.last_updated
FROM symbols s
JOIN real_time_prices rtp ON s.id = rtp.symbol_id
WHERE s.is_active = true
ORDER BY rtp.last_updated DESC
LIMIT 10;
```

### Get Market Data with Technical Indicators
```sql
SELECT 
    s.symbol,
    md.timestamp,
    md.close,
    ti.sma_20,
    ti.rsi_14,
    ti.macd
FROM symbols s
JOIN market_data md ON s.id = md.symbol_id
LEFT JOIN technical_indicators ti ON s.id = ti.symbol_id 
    AND md.timestamp = ti.timestamp
WHERE s.symbol = 'AAPL'
ORDER BY md.timestamp DESC;
```

### Get Market Status
```sql
SELECT 
    exchange,
    is_open,
    next_open,
    next_close
FROM market_status
ORDER BY exchange;
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if the web service is running
   curl http://dev01.int.stortz.tech:8000/health
   ```

2. **Table Already Exists**
   ```bash
   # Use --force flag to recreate
   python setup_database.py --env dev --force
   ```

3. **Permission Denied**
   - Check database web service permissions
   - Verify API endpoint accessibility

### Debug Mode
```python
# Enable debug logging
import structlog
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer()
    ]
)
```

## 📋 Next Steps

1. **Set up database**: `python setup_database.py --env dev`
2. **Run tests**: `python test_database_crud.py`
3. **Implement market-data service** with this database foundation
4. **Configure API keys** for data sources
5. **Set up monitoring** and alerting

---

For more information, see the main [README.md](../README.md) in the project root.
