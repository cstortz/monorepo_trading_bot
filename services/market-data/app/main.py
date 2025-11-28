"""
Market Data FastAPI Service

Service for managing market data collection, storage, and retrieval.
Handles OHLCV data, real-time prices, and market status.
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add shared modules and root to path
root_path = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_path / "shared"))
sys.path.append(str(root_path))

from shared.logging.config import setup_service_logging
from shared.config.settings import get_config
from shared.cache.redis_client import RedisCache, get_cache
from database_client import DatabaseClient, TradingBotDatabase

# Import Kraken client
try:
    from .kraken_client import KrakenClient, get_kraken_symbol_mapping
except ImportError:
    # Fallback for when running as script
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from kraken_client import KrakenClient, get_kraken_symbol_mapping

# Configuration
config = get_config()
logger = setup_service_logging("market-data", config.environment)

# FastAPI app
app = FastAPI(
    title="Market Data Service",
    description="Market data collection, storage, and retrieval service for the trading bot monorepo",
    version="1.0.0",
    debug=config.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    database_status: Optional[str] = None
    database_url: Optional[str] = None
    message: Optional[str] = None

class MarketDataPoint(BaseModel):
    id: Optional[int] = None
    symbol: str
    symbol_name: Optional[str] = None
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: Optional[float] = None
    time_frame: str
    data_source: str
    created_at: Optional[datetime] = None

class MarketDataResponse(BaseModel):
    symbol: str
    timeframe: str
    data: List[MarketDataPoint]
    count: int

class MarketDataInsert(BaseModel):
    symbol: str
    timestamp: datetime
    open: float = Field(..., gt=0)
    high: float = Field(..., gt=0)
    low: float = Field(..., gt=0)
    close: float = Field(..., gt=0)
    volume: int = Field(..., ge=0)
    adjusted_close: Optional[float] = None
    time_frame: str = Field(..., pattern="^(1m|5m|15m|30m|1h|4h|1d|1w|1M)$")
    data_source: str

class RealTimePrice(BaseModel):
    id: Optional[int] = None
    symbol: str
    symbol_name: Optional[str] = None
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume_24h: Optional[int] = None
    change_24h: Optional[float] = None
    change_percent_24h: Optional[float] = None
    market_cap: Optional[int] = None
    data_source: str
    last_updated: datetime

class RealTimePriceResponse(BaseModel):
    prices: List[RealTimePrice]
    count: int

class RealTimePriceUpdate(BaseModel):
    symbol: str
    price: float = Field(..., gt=0)
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume_24h: Optional[int] = None
    change_24h: Optional[float] = None
    change_percent_24h: Optional[float] = None
    market_cap: Optional[int] = None
    data_source: str

class SymbolInfo(BaseModel):
    id: int
    symbol: str
    name: str
    exchange: str
    asset_type: str
    currency: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class SymbolsResponse(BaseModel):
    symbols: List[SymbolInfo]
    count: int

class MarketStatus(BaseModel):
    exchange: str
    is_open: bool
    next_open: Optional[datetime] = None
    next_close: Optional[datetime] = None
    last_updated: datetime

class MarketStatusResponse(BaseModel):
    status: List[MarketStatus]
    count: int

# Routes
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with service information."""
    logger.info("Root endpoint accessed")
    return {
        "service": "market-data",
        "version": "1.0.0",
        "description": "Market data collection, storage, and retrieval service",
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "market_data": "/market-data/{symbol}",
            "real_time_prices": "/real-time-prices",
            "symbols": "/symbols",
            "market_status": "/market-status",
            "kraken_fetch_ohlc": "/kraken/fetch-ohlc",
            "kraken_fetch_ticker": "/kraken/fetch-ticker",
            "kraken_pairs": "/kraken/pairs",
            "kraken_sync_symbols": "/kraken/sync-symbols",
            "kraken_add_pair": "/kraken/add-pair"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check endpoint accessed")
    
    # Get database API web service URL from environment or default
    import os
    db_url = os.getenv("DATABASE_API_URL", os.getenv("DATABASE_URL", "http://dev01.int.stortz.tech:8000"))
    
    # Check database API web service connection
    db_status = "unknown"
    db_message = None
    try:
        with DatabaseClient(base_url=db_url) as client:
            health = client.health_check()
            db_status = health.get("status", "unknown")
            if db_status == "healthy":
                db_message = "Database API web service connection successful"
            else:
                db_message = health.get("error", "Database API web service connection failed")
    except Exception as e:
        logger.error(f"Database API web service health check failed: {e}")
        db_status = "unhealthy"
        error_msg = str(e)
        # Provide more helpful error messages
        if "No address associated with hostname" in error_msg or "Name or service not known" in error_msg:
            db_message = f"Cannot resolve hostname or connect to database API: {db_url}. Check network connectivity and DNS."
        elif "Connection refused" in error_msg:
            db_message = f"Connection refused to database API: {db_url}. The service may not be running or accessible."
        else:
            db_message = f"Database API connection error: {error_msg}"
    
    # Service is healthy if it's running, but degraded if database API is unavailable
    # This allows the service to still function for Kraken API calls even without database storage
    status = "healthy" if db_status == "healthy" else "degraded"
    
    return HealthResponse(
        status=status,
        service="market-data",
        version="1.0.0",
        database_status=db_status,
        database_url=db_url,
        message=db_message if status == "degraded" else None
    )

@app.get("/info")
async def service_info():
    """Service information endpoint."""
    logger.info("Service info endpoint accessed")
    
    return {
        "service": "market-data",
        "version": "1.0.0",
        "environment": config.environment,
        "debug": config.debug,
        "log_level": config.log_level
    }

@app.get("/market-data/{symbol}", response_model=MarketDataResponse)
async def get_market_data(
    symbol: str,
    timeframe: str = Query(default="1d", pattern="^(1m|5m|15m|30m|1h|4h|1d|1w|1M)$"),
    limit: int = Query(default=100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get market data (OHLCV) for a symbol."""
    logger.info(f"Getting market data for {symbol}, timeframe: {timeframe}, limit: {limit}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            
            # Get market data
            market_data = trading_db.get_market_data(symbol, timeframe, limit)
            
            # Filter by date range if provided
            if start_date or end_date:
                filtered_data = []
                for item in market_data:
                    item_timestamp = item.get("timestamp")
                    if isinstance(item_timestamp, str):
                        item_timestamp = datetime.fromisoformat(item_timestamp.replace('Z', '+00:00'))
                    
                    if start_date and item_timestamp < start_date:
                        continue
                    if end_date and item_timestamp > end_date:
                        continue
                    filtered_data.append(item)
                market_data = filtered_data
            
            # Transform to response format
            data_points = []
            for item in market_data:
                timestamp = item.get("timestamp")
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                data_points.append(MarketDataPoint(
                    id=item.get("id"),
                    symbol=item.get("symbol", symbol),
                    symbol_name=item.get("name"),
                    timestamp=timestamp,
                    open=float(item.get("open", 0)),
                    high=float(item.get("high", 0)),
                    low=float(item.get("low", 0)),
                    close=float(item.get("close", 0)),
                    volume=int(item.get("volume", 0)),
                    adjusted_close=float(item.get("adjusted_close")) if item.get("adjusted_close") else None,
                    time_frame=item.get("time_frame", timeframe),
                    data_source=item.get("data_source", ""),
                    created_at=datetime.fromisoformat(item.get("created_at").replace('Z', '+00:00')) if item.get("created_at") else None
                ))
            
            return MarketDataResponse(
                symbol=symbol,
                timeframe=timeframe,
                data=data_points,
                count=len(data_points)
            )
            
    except Exception as e:
        logger.error(f"Failed to get market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve market data: {str(e)}")

@app.get("/market-data/{symbol}/timeframes")
async def get_symbol_timeframes(symbol: str):
    """Get distinct timeframes available for a symbol."""
    logger.info(f"Getting available timeframes for {symbol}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            
            # Get distinct timeframes
            timeframes = trading_db.get_distinct_timeframes(symbol)
            
            return {
                "symbol": symbol,
                "timeframes": timeframes,
                "count": len(timeframes)
            }
            
    except Exception as e:
        logger.error(f"Failed to get timeframes for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve timeframes: {str(e)}")

@app.post("/market-data")
async def insert_market_data(data: MarketDataInsert):
    """Insert market data for a symbol."""
    logger.info(f"Inserting market data for {data.symbol}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            
            # Get symbol by name
            symbol_info = trading_db.get_symbol_by_name(data.symbol)
            if not symbol_info:
                raise HTTPException(status_code=404, detail=f"Symbol {data.symbol} not found")
            
            symbol_id = symbol_info["id"]
            
            # Prepare market data dict
            market_data_dict = {
                "timestamp": data.timestamp,
                "open": data.open,
                "high": data.high,
                "low": data.low,
                "close": data.close,
                "volume": data.volume,
                "adjusted_close": data.adjusted_close,
                "time_frame": data.time_frame,
                "data_source": data.data_source
            }
            
            # Insert market data
            success = trading_db.insert_market_data(symbol_id, market_data_dict)
            
            if success:
                return {
                    "success": True,
                    "message": f"Market data inserted for {data.symbol}",
                    "symbol": data.symbol,
                    "timestamp": data.timestamp,
                    "timeframe": data.time_frame
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to insert market data")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to insert market data for {data.symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to insert market data: {str(e)}")

@app.get("/real-time-prices", response_model=RealTimePriceResponse)
async def get_real_time_prices(
    symbol: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000)
):
    """Get real-time prices."""
    logger.info(f"Getting real-time prices, symbol: {symbol}, limit: {limit}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            
            # Get real-time prices
            prices = trading_db.get_real_time_prices(limit)
            
            # Filter by symbol if provided
            if symbol:
                prices = [p for p in prices if p.get("symbol") == symbol]
            
            # Transform to response format
            price_list = []
            for item in prices:
                last_updated = item.get("last_updated")
                if isinstance(last_updated, str):
                    last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                
                price_list.append(RealTimePrice(
                    id=item.get("id"),
                    symbol=item.get("symbol", ""),
                    symbol_name=item.get("name"),
                    price=float(item.get("price", 0)),
                    bid=float(item.get("bid")) if item.get("bid") else None,
                    ask=float(item.get("ask")) if item.get("ask") else None,
                    volume_24h=int(item.get("volume_24h")) if item.get("volume_24h") else None,
                    change_24h=float(item.get("change_24h")) if item.get("change_24h") else None,
                    change_percent_24h=float(item.get("change_percent_24h")) if item.get("change_percent_24h") else None,
                    market_cap=int(item.get("market_cap")) if item.get("market_cap") else None,
                    data_source=item.get("data_source", ""),
                    last_updated=last_updated
                ))
            
            return RealTimePriceResponse(
                prices=price_list,
                count=len(price_list)
            )
            
    except Exception as e:
        logger.error(f"Failed to get real-time prices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve real-time prices: {str(e)}")

@app.post("/real-time-prices")
async def update_real_time_price(price_data: RealTimePriceUpdate):
    """Update real-time price for a symbol."""
    logger.info(f"Updating real-time price for {price_data.symbol}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            
            # Get symbol by name
            symbol_info = trading_db.get_symbol_by_name(price_data.symbol)
            if not symbol_info:
                raise HTTPException(status_code=404, detail=f"Symbol {price_data.symbol} not found")
            
            symbol_id = symbol_info["id"]
            
            # Prepare price data dict
            price_dict = {
                "price": price_data.price,
                "bid": price_data.bid,
                "ask": price_data.ask,
                "volume_24h": price_data.volume_24h,
                "change_24h": price_data.change_24h,
                "change_percent_24h": price_data.change_percent_24h,
                "market_cap": price_data.market_cap,
                "data_source": price_data.data_source
            }
            
            # Update real-time price
            success = trading_db.update_real_time_price(symbol_id, price_dict)
            
            if success:
                return {
                    "success": True,
                    "message": f"Real-time price updated for {price_data.symbol}",
                    "symbol": price_data.symbol,
                    "price": price_data.price
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to update real-time price")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update real-time price for {price_data.symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update real-time price: {str(e)}")

@app.get("/symbols", response_model=SymbolsResponse)
async def get_symbols(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    asset_type: Optional[str] = None,
    exchange: Optional[str] = None,
    is_active: Optional[bool] = True
):
    """Get symbols."""
    logger.info(f"Getting symbols, limit: {limit}, offset: {offset}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            
            # Get symbols
            symbols = trading_db.get_symbols(limit, offset)
            
            # Filter by asset_type if provided
            if asset_type:
                symbols = [s for s in symbols if s.get("asset_type") == asset_type]
            
            # Filter by exchange if provided
            if exchange:
                symbols = [s for s in symbols if s.get("exchange") == exchange]
            
            # Filter by is_active if provided
            if is_active is not None:
                symbols = [s for s in symbols if s.get("is_active") == is_active]
            
            # Transform to response format
            symbol_list = []
            for item in symbols:
                created_at = item.get("created_at")
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                
                updated_at = item.get("updated_at")
                if isinstance(updated_at, str):
                    updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                
                symbol_list.append(SymbolInfo(
                    id=item.get("id"),
                    symbol=item.get("symbol", ""),
                    name=item.get("name", ""),
                    exchange=item.get("exchange", ""),
                    asset_type=item.get("asset_type", ""),
                    currency=item.get("currency", "USD"),
                    sector=item.get("sector"),
                    industry=item.get("industry"),
                    market_cap=int(item.get("market_cap")) if item.get("market_cap") else None,
                    is_active=item.get("is_active", True),
                    created_at=created_at,
                    updated_at=updated_at
                ))
            
            return SymbolsResponse(
                symbols=symbol_list,
                count=len(symbol_list)
            )
            
    except Exception as e:
        logger.error(f"Failed to get symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve symbols: {str(e)}")

@app.get("/symbols/{symbol}", response_model=SymbolInfo)
async def get_symbol(symbol: str):
    """Get a specific symbol by name."""
    logger.info(f"Getting symbol: {symbol}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            
            # Get symbol by name
            symbol_info = trading_db.get_symbol_by_name(symbol)
            
            if not symbol_info:
                raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
            
            created_at = symbol_info.get("created_at")
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            updated_at = symbol_info.get("updated_at")
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            return SymbolInfo(
                id=symbol_info.get("id"),
                symbol=symbol_info.get("symbol", ""),
                name=symbol_info.get("name", ""),
                exchange=symbol_info.get("exchange", ""),
                asset_type=symbol_info.get("asset_type", ""),
                currency=symbol_info.get("currency", "USD"),
                sector=symbol_info.get("sector"),
                industry=symbol_info.get("industry"),
                market_cap=int(symbol_info.get("market_cap")) if symbol_info.get("market_cap") else None,
                is_active=symbol_info.get("is_active", True),
                created_at=created_at,
                updated_at=updated_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve symbol: {str(e)}")

@app.get("/market-status", response_model=MarketStatusResponse)
async def get_market_status(exchange: Optional[str] = None):
    """Get market status for exchanges."""
    logger.info(f"Getting market status, exchange: {exchange}")
    
    try:
        with DatabaseClient() as client:
            # Query market status
            sql = "SELECT * FROM market_status"
            if exchange:
                sql += " WHERE exchange = $1"
                result = client.execute_prepared_select(sql, {"1": exchange})
            else:
                result = client.execute_prepared_select(sql)
            
            if not result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to retrieve market status")
            
            status_list = []
            for item in result.get("data", []):
                last_updated = item.get("last_updated")
                if isinstance(last_updated, str):
                    last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                
                next_open = item.get("next_open")
                if next_open and isinstance(next_open, str):
                    next_open = datetime.fromisoformat(next_open.replace('Z', '+00:00'))
                
                next_close = item.get("next_close")
                if next_close and isinstance(next_close, str):
                    next_close = datetime.fromisoformat(next_close.replace('Z', '+00:00'))
                
                status_list.append(MarketStatus(
                    exchange=item.get("exchange", ""),
                    is_open=item.get("is_open", False),
                    next_open=next_open,
                    next_close=next_close,
                    last_updated=last_updated
                ))
            
            return MarketStatusResponse(
                status=status_list,
                count=len(status_list)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get market status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve market status: {str(e)}")

@app.post("/kraken/fetch-ohlc")
async def fetch_kraken_ohlc(
    pair: str = Query(..., description="Kraken trading pair (e.g., XBTUSD, ETHUSD)"),
    timeframe: str = Query(default="1d", pattern="^(1m|5m|15m|30m|1h|4h|1d|1w|1M)$"),
    limit: Optional[int] = Query(default=None, ge=1, le=720)
):
    """Fetch OHLC data from Kraken and store in database."""
    logger.info(f"Fetching Kraken OHLC data for {pair}, timeframe: {timeframe}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            kraken = KrakenClient()
            
            # Normalize pair name
            normalized_pair = kraken.normalize_pair(pair)
            
            # Get interval for Kraken API
            interval = kraken.get_timeframe_interval(timeframe)
            
            # Fetch OHLC data from Kraken
            ohlc_result = kraken.get_ohlc(normalized_pair, interval=interval)
            ohlc_data = ohlc_result.get("data", [])
            
            if not ohlc_data:
                raise HTTPException(status_code=404, detail=f"No OHLC data found for pair {pair}")
            
            # Limit results if specified
            if limit:
                ohlc_data = ohlc_data[-limit:]
            
            # Parse Kraken data
            parsed_data = kraken.parse_ohlc_data(ohlc_data, timeframe, normalized_pair)
            
            # Get or create symbol in database
            symbol_mapping = get_kraken_symbol_mapping()
            db_symbol = symbol_mapping.get(normalized_pair, normalized_pair)
            
            symbol_info = trading_db.get_symbol_by_name(db_symbol)
            if not symbol_info:
                # Create symbol if it doesn't exist
                symbol_data = {
                    "symbol": db_symbol,
                    "name": db_symbol,
                    "exchange": "Kraken",
                    "asset_type": "crypto",
                    "currency": "USD",
                    "is_active": True
                }
                trading_db.create_symbol(symbol_data)
                symbol_info = trading_db.get_symbol_by_name(db_symbol)
            
            symbol_id = symbol_info["id"]
            
            # Insert market data
            inserted_count = 0
            for data_point in parsed_data:
                success = trading_db.insert_market_data(symbol_id, data_point)
                if success:
                    inserted_count += 1
            
            return {
                "success": True,
                "message": f"Fetched and stored {inserted_count} OHLC records from Kraken",
                "pair": normalized_pair,
                "symbol": db_symbol,
                "timeframe": timeframe,
                "records_fetched": len(parsed_data),
                "records_inserted": inserted_count
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch Kraken OHLC data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Kraken data: {str(e)}")

@app.post("/kraken/fetch-ticker")
async def fetch_kraken_ticker(
    pair: str = Query(..., description="Kraken trading pair (e.g., XBTUSD, ETHUSD)")
):
    """Fetch real-time ticker data from Kraken and update database."""
    logger.info(f"Fetching Kraken ticker data for {pair}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            kraken = KrakenClient()
            
            # Normalize pair name
            normalized_pair = kraken.normalize_pair(pair)
            
            # Fetch ticker data from Kraken
            ticker_data = kraken.get_ticker(normalized_pair)
            
            if not ticker_data:
                raise HTTPException(status_code=404, detail=f"No ticker data found for pair {pair}")
            
            # Parse ticker data
            parsed_data = kraken.parse_ticker_data(ticker_data, normalized_pair)
            
            # Get or create symbol in database
            symbol_mapping = get_kraken_symbol_mapping()
            db_symbol = symbol_mapping.get(normalized_pair, normalized_pair)
            
            symbol_info = trading_db.get_symbol_by_name(db_symbol)
            if not symbol_info:
                # Create symbol if it doesn't exist
                symbol_data = {
                    "symbol": db_symbol,
                    "name": db_symbol,
                    "exchange": "Kraken",
                    "asset_type": "crypto",
                    "currency": "USD",
                    "is_active": True
                }
                trading_db.create_symbol(symbol_data)
                symbol_info = trading_db.get_symbol_by_name(db_symbol)
            
            symbol_id = symbol_info["id"]
            
            # Update real-time price
            success = trading_db.update_real_time_price(symbol_id, parsed_data)
            
            if success:
                return {
                    "success": True,
                    "message": f"Updated real-time price from Kraken",
                    "pair": normalized_pair,
                    "symbol": db_symbol,
                    "price": parsed_data["price"]
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to update real-time price")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch Kraken ticker data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Kraken ticker: {str(e)}")

@app.get("/kraken/pairs")
async def get_kraken_pairs(
    limit: int = Query(default=100, ge=1, le=2000, description="Maximum number of pairs to return"),
    offset: int = Query(default=0, ge=0, description="Number of pairs to skip"),
    status: Optional[str] = Query(default="online", description="Filter by status: 'online', 'cancel_only', 'post_only', 'limit_only', or 'all'"),
    search: Optional[str] = Query(default=None, description="Search term to filter pairs by name (case-insensitive)"),
    refresh: bool = Query(default=False, description="Force refresh from Kraken API, bypassing cache")
):
    """Get available trading pairs from Kraken with pagination, search, and Redis caching."""
    logger.info(f"Fetching available Kraken pairs, limit: {limit}, offset: {offset}, status: {status}, search: {search}, refresh: {refresh}")
    
    try:
        cache = get_cache()
        pairs = None
        from_cache = False
        
        # Try to get from cache first (unless refresh is requested)
        if not refresh and cache:
            cached_data = cache.get_kraken_pairs()
            if cached_data:
                pairs = cached_data.get("pairs")
                from_cache = True
                logger.info("Retrieved Kraken pairs from cache")
        
        # If not in cache or refresh requested, fetch from Kraken
        if pairs is None:
            logger.info("Fetching Kraken pairs from API")
            kraken = KrakenClient()
            pairs = kraken.get_asset_pairs()
            
            # Cache the pairs with 1 hour expiration
            if cache:
                cache_data = {
                    "pairs": pairs,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                cache.set_kraken_pairs(cache_data, expiration=3600)  # 1 hour
                logger.info("Cached Kraken pairs for 1 hour")
        
        # Filter by status if specified
        if status and status != "all":
            filtered_pairs = {
                name: info for name, info in pairs.items()
                if info.get("status") == status
            }
        else:
            filtered_pairs = pairs
        
        # Apply search filter if provided (search through all pairs, not just loaded ones)
        # Search in pair name, wsname (readable name), and altname
        # Also handle special mappings like DOGE -> XDG
        if search:
            search_lower = search.lower()
            # Handle special currency mappings for search
            search_terms = [search_lower]
            if "doge" in search_lower:
                search_terms.append("xdg")  # DOGE is XDG on Kraken
            if "btc" in search_lower and "xbt" not in search_lower:
                search_terms.append("xbt")  # BTC is XBT on Kraken
            
            filtered_pairs = {
                name: info for name, info in filtered_pairs.items()
                if any(
                    term in name.lower() or
                    term in info.get("wsname", "").lower() or
                    term in info.get("altname", "").lower() or
                    term in info.get("base", "").lower() or
                    term in info.get("quote", "").lower()
                    for term in search_terms
                )
            }
            logger.info(f"Applied search filter '{search}' (terms: {search_terms}), found {len(filtered_pairs)} matching pairs")
        
        # Get total counts (before search filter for reference)
        active_pairs = {
            name: info for name, info in pairs.items()
            if info.get("status") == "online"
        }
        
        # Sort pairs alphabetically for consistent pagination
        sorted_pairs = sorted(filtered_pairs.keys())
        
        # Apply pagination
        paginated_pairs = sorted_pairs[offset:offset + limit]
        
        # Build pairs with readable names
        pairs_with_names = []
        for pair_name in paginated_pairs:
            pair_info = filtered_pairs[pair_name]
            pair_data = {
                "pair": pair_name,
                "name": pair_info.get("wsname") or pair_info.get("altname") or pair_name,
                "altname": pair_info.get("altname", pair_name),
                "base": pair_info.get("base", ""),
                "quote": pair_info.get("quote", ""),
                "status": pair_info.get("status", "unknown")
            }
            pairs_with_names.append(pair_data)
        
        return {
            "success": True,
            "total_pairs": len(pairs),
            "active_pairs": len(active_pairs),
            "filtered_pairs": len(filtered_pairs),
            "pairs": paginated_pairs,  # Keep simple list for backward compatibility
            "pairs_detail": pairs_with_names,  # New: detailed pairs with readable names
            "from_cache": from_cache,
            "search": search,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "returned": len(paginated_pairs),
                "has_more": (offset + limit) < len(filtered_pairs),
                "total": len(filtered_pairs)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch Kraken pairs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Kraken pairs: {str(e)}")

@app.post("/kraken/pairs/refresh")
async def refresh_kraken_pairs():
    """Clear Kraken pairs cache and force refresh from Kraken API."""
    logger.info("Refreshing Kraken pairs cache")
    
    try:
        cache = get_cache()
        
        # Clear the cache
        if cache:
            cache.clear_kraken_pairs_cache()
            logger.info("Cleared Kraken pairs cache")
        
        # Fetch fresh data from Kraken
        kraken = KrakenClient()
        pairs = kraken.get_asset_pairs()
        
        # Cache the new pairs with 1 hour expiration
        if cache:
            cache_data = {
                "pairs": pairs,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            cache.set_kraken_pairs(cache_data, expiration=3600)  # 1 hour
            logger.info("Refreshed and cached Kraken pairs for 1 hour")
        
        # Get counts
        active_pairs = {
            name: info for name, info in pairs.items()
            if info.get("status") == "online"
        }
        
        return {
            "success": True,
            "message": "Kraken pairs cache refreshed successfully",
            "total_pairs": len(pairs),
            "active_pairs": len(active_pairs),
            "cached": cache is not None and cache.is_connected()
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh Kraken pairs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh Kraken pairs: {str(e)}")

@app.post("/kraken/sync-symbols")
async def sync_kraken_symbols():
    """Sync Kraken trading pairs to database symbols."""
    logger.info("Syncing Kraken symbols to database")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            kraken = KrakenClient()
            
            # Get available pairs from Kraken
            pairs = kraken.get_asset_pairs()
            symbol_mapping = get_kraken_symbol_mapping()
            
            created_count = 0
            updated_count = 0
            
            # Sync mapped pairs
            for kraken_pair, db_symbol in symbol_mapping.items():
                if kraken_pair in pairs:
                    pair_info = pairs[kraken_pair]
                    
                    # Check if symbol exists
                    symbol_info = trading_db.get_symbol_by_name(db_symbol)
                    
                    if not symbol_info:
                        # Create new symbol
                        symbol_data = {
                            "symbol": db_symbol,
                            "name": pair_info.get("altname", db_symbol),
                            "exchange": "Kraken",
                            "asset_type": "crypto",
                            "currency": "USD",
                            "is_active": pair_info.get("status") == "online"
                        }
                        trading_db.create_symbol(symbol_data)
                        created_count += 1
                    else:
                        # Update existing symbol if needed
                        if symbol_info.get("is_active") != (pair_info.get("status") == "online"):
                            update_data = {
                                "is_active": pair_info.get("status") == "online"
                            }
                            trading_db.update_symbol(db_symbol, update_data)
                            updated_count += 1
            
            return {
                "success": True,
                "message": "Synced Kraken symbols to database",
                "created": created_count,
                "updated": updated_count,
                "total_pairs": len(symbol_mapping)
            }
            
    except Exception as e:
        logger.error(f"Failed to sync Kraken symbols: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync symbols: {str(e)}")

@app.post("/kraken/add-pair")
async def add_kraken_pair(
    kraken_pair: str = Query(..., description="Kraken pair name (e.g., XBTUSD, DOGEUSD)"),
    db_symbol: Optional[str] = Query(default=None, description="Database symbol (e.g., BTC/USD). If not provided, will use Kraken pair name")
):
    """
    Add a new Kraken trading pair to the database.
    This will create the symbol if it doesn't exist and fetch initial data.
    """
    logger.info(f"Adding Kraken pair: {kraken_pair}")
    
    try:
        with DatabaseClient() as client:
            trading_db = TradingBotDatabase(client)
            kraken = KrakenClient()
            
            # Normalize pair name
            normalized_pair = kraken.normalize_pair(kraken_pair)
            
            # Use provided db_symbol or default to normalized pair
            if not db_symbol:
                # Try to infer from common patterns
                if normalized_pair.startswith("XBT"):
                    db_symbol = normalized_pair.replace("XBT", "BTC")
                else:
                    db_symbol = normalized_pair
                
                # Add slash if not present and looks like a pair
                if "/" not in db_symbol and len(db_symbol) > 6:
                    # Try to split (e.g., "BTCUSD" -> "BTC/USD")
                    for quote in ["USD", "USDT", "EUR", "GBP"]:
                        if db_symbol.endswith(quote):
                            base = db_symbol[:-len(quote)]
                            db_symbol = f"{base}/{quote}"
                            break
            
            # Verify pair exists on Kraken
            pairs = kraken.get_asset_pairs()
            if normalized_pair not in pairs:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Pair {normalized_pair} not found on Kraken. Use /kraken/pairs to see available pairs."
                )
            
            pair_info = pairs[normalized_pair]
            
            # Check if symbol already exists
            symbol_info = trading_db.get_symbol_by_name(db_symbol)
            
            if symbol_info:
                return {
                    "success": True,
                    "message": f"Symbol {db_symbol} already exists",
                    "pair": normalized_pair,
                    "symbol": db_symbol,
                    "symbol_id": symbol_info["id"]
                }
            
            # Create new symbol
            symbol_data = {
                "symbol": db_symbol,
                "name": pair_info.get("altname", db_symbol),
                "exchange": "Kraken",
                "asset_type": "crypto",
                "currency": "USD" if "USD" in db_symbol else "EUR",
                "is_active": pair_info.get("status") == "online"
            }
            
            success = trading_db.create_symbol(symbol_data)
            
            if success:
                # Optionally fetch initial ticker data
                try:
                    ticker_data = kraken.get_ticker(normalized_pair)
                    if ticker_data:
                        parsed_data = kraken.parse_ticker_data(ticker_data, normalized_pair)
                        symbol_info = trading_db.get_symbol_by_name(db_symbol)
                        if symbol_info:
                            trading_db.update_real_time_price(symbol_info["id"], parsed_data)
                except Exception as e:
                    logger.warning(f"Could not fetch initial ticker data: {e}")
                
                return {
                    "success": True,
                    "message": f"Added pair {normalized_pair} as {db_symbol}",
                    "pair": normalized_pair,
                    "symbol": db_symbol,
                    "status": pair_info.get("status", "unknown")
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to create symbol")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add Kraken pair: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add pair: {str(e)}")

if __name__ == "__main__":
    logger.info(f"Starting Market Data service on {config.api_host}:{config.api_port}")
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug,
        log_level=config.log_level.lower()
    )

