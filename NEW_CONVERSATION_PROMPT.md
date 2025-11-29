# Prompt for New Conversation - Trading Bot Monorepo

Use this prompt to start a new conversation about the trading bot monorepo:

---

**I'm working on a trading bot monorepo built with FastAPI, Docker, and Kubernetes. Here's the current state:**

## Project Overview
- **Repository**: Trading bot monorepo with microservices architecture
- **Current Tag**: `market_data_admin` (latest completed milestone)
- **Backend Framework**: FastAPI-based microservices running on ports 5000-5100
- **Web Framework**: Static HTML/CSS/JavaScript (vanilla JS, no frontend framework) served by Python's built-in http.server
- **Web Interface**: Running on port 5080
- **Database**: External PostgreSQL database accessed via web service API at `dev01.int.stortz.tech:8000`

## Current Services & Ports
- **hello-world**: Port 5000 (http://localhost:5000)
- **market-data**: Port 5001 (http://localhost:5001)
- **web**: Port 5080 (http://localhost:5080)
- **redis**: Port 6379 (caching service)

## Recently Completed Features (market_data_admin tag)

### Database Schema Updates
- Renamed `market_data.timestamp` column to `t_stamp` across all SQL files (dev, prod, simple)
- Updated all indexes, views, and partition scripts
- Added database triggers for automatic `updated_at` timestamp updates

### Error Logging Enhancements
- Enhanced database client error logging to include:
  - Full URL where JSON is being sent
  - Complete JSON payload (formatted)
  - HTTP status codes and response text
- Applied to all database operations (INSERT, SELECT, UPDATE, DELETE, VALIDATE)

### Datetime Handling
- Database API now accepts ISO format datetime strings
- Client code converts datetime objects to ISO strings for JSON serialization
- Fixed JSON serialization errors for datetime objects

### Kraken Integration Fixes
- Fixed ticker data parsing to handle string values for `open_price` from Kraken API
- Proper type conversion for all ticker fields

### Web Interface Improvements
- **Dynamic Symbol Dropdown**: "View Stored Market Data" form now populates symbols from database
- **Dynamic Timeframe Dropdown**: Timeframes are dynamically loaded based on selected symbol
- **Auto-refresh**: Symbol and timeframe dropdowns refresh after fetching OHLC data
- **Type-ahead**: Users can see available symbols and timeframes without guessing

### API Endpoints Added
- `GET /market-data/{symbol}/timeframes` - Get distinct timeframes for a symbol
- Enhanced `/symbols` endpoint with filtering options

## Key Technical Details

### Database Client (`database_client.py`)
- `DatabaseClient`: Low-level client for database API web service
- `TradingBotDatabase`: High-level trading bot operations
- Methods: `get_symbols()`, `get_market_data()`, `insert_market_data()`, `get_distinct_timeframes()`, etc.
- All methods include comprehensive error logging with URLs and payloads

### Market Data Service (`services/market-data/app/main.py`)
- Kraken integration for OHLC and ticker data
- Redis caching for Kraken pairs (1 hour expiration)
- Server-side search and pagination for pairs
- Health check with database API status
- Endpoints for fetching, storing, and viewing market data

### Web Interface (`web/`)
- **Technology Stack**: Static HTML/CSS/JavaScript (vanilla JS, no frontend framework)
- **Web Server**: Python's built-in `http.server.SimpleHTTPRequestHandler` (via `server.py`)
- **Features**:
  - Dynamic URL detection (works with reverse proxies)
  - Real-time service status monitoring
  - Market data visualization
  - Trading pair management
  - Symbol and timeframe management with database integration
- **Files**: `index.html`, `styles.css`, `app.js`, `server.py`

### Kraken Client (`services/market-data/app/kraken_client.py`)
- REST API client for Kraken exchange
- OHLC data fetching and parsing
- Ticker data fetching and parsing
- Symbol normalization (BTC → XBT, etc.)
- Timeframe mapping to Kraken intervals

## Database Schema
- **symbols**: Trading instruments
- **market_data**: OHLCV data with `t_stamp` column (partitioned in prod)
- **real_time_prices**: Current market prices
- **technical_indicators**: Technical analysis data
- **market_sessions**: Trading session definitions
- **market_status**: Market open/close status
- **data_sources**: API configuration

## Development Setup
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f market-data

# Access web interface
# http://localhost:5080

# Access market-data API
# http://localhost:5001
```

## Current State
- ✅ Market data service fully functional
- ✅ Kraken integration complete
- ✅ Web dashboard operational
- ✅ Database integration working
- ✅ Redis caching implemented
- ✅ Error logging comprehensive
- ✅ Dynamic UI components working

## Next Steps / Areas for Development
- Strategy engine service
- Order management service
- Risk management service
- Portfolio manager service
- Additional exchange integrations
- Advanced analytics and indicators

---

**Please help me continue development on this monorepo. I'm ready to work on new features or improvements.**

