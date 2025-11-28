-- Trading Bot Database Schema - Production
-- DDL for creating market data tables with production optimizations

-- =============================================
-- CORE MARKET DATA TABLES
-- =============================================

-- Symbols table - stores all tradeable instruments
CREATE TABLE IF NOT EXISTS symbols (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    asset_type VARCHAR(20) NOT NULL, -- 'stock', 'crypto', 'forex', 'commodity', 'index'
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Market data table - stores OHLCV data (partitioned for production)
CREATE TABLE IF NOT EXISTS market_data (
    id BIGSERIAL,
    symbol_id INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(20,8) NOT NULL,
    high DECIMAL(20,8) NOT NULL,
    low DECIMAL(20,8) NOT NULL,
    close DECIMAL(20,8) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    adjusted_close DECIMAL(20,8),
    time_frame VARCHAR(10) NOT NULL, -- '1m', '5m', '15m', '1h', '4h', '1d', '1w', '1M'
    data_source VARCHAR(50) NOT NULL, -- 'alpha_vantage', 'yahoo', 'binance', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id, timestamp),
    UNIQUE(symbol_id, timestamp, time_frame, data_source)
) PARTITION BY RANGE (timestamp);

-- Real-time prices table - for current market prices
CREATE TABLE IF NOT EXISTS real_time_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol_id INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
    price DECIMAL(20,8) NOT NULL,
    bid DECIMAL(20,8),
    ask DECIMAL(20,8),
    volume_24h BIGINT,
    change_24h DECIMAL(20,8),
    change_percent_24h DECIMAL(10,4),
    market_cap BIGINT,
    data_source VARCHAR(50) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol_id, data_source)
);

-- =============================================
-- TECHNICAL INDICATORS TABLES
-- =============================================

-- Technical indicators table
CREATE TABLE IF NOT EXISTS technical_indicators (
    id BIGSERIAL PRIMARY KEY,
    symbol_id INTEGER NOT NULL REFERENCES symbols(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    time_frame VARCHAR(10) NOT NULL,
    
    -- Moving Averages
    sma_5 DECIMAL(20,8),
    sma_10 DECIMAL(20,8),
    sma_20 DECIMAL(20,8),
    sma_50 DECIMAL(20,8),
    sma_200 DECIMAL(20,8),
    ema_12 DECIMAL(20,8),
    ema_26 DECIMAL(20,8),
    
    -- Oscillators
    rsi_14 DECIMAL(10,4),
    macd DECIMAL(20,8),
    macd_signal DECIMAL(20,8),
    macd_histogram DECIMAL(20,8),
    stoch_k DECIMAL(10,4),
    stoch_d DECIMAL(10,4),
    
    -- Volatility
    bollinger_upper DECIMAL(20,8),
    bollinger_middle DECIMAL(20,8),
    bollinger_lower DECIMAL(20,8),
    atr_14 DECIMAL(20,8),
    
    -- Volume indicators
    volume_sma_20 BIGINT,
    obv DECIMAL(20,8),
    
    -- Trend indicators
    adx DECIMAL(10,4),
    cci DECIMAL(20,8),
    williams_r DECIMAL(10,4),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(symbol_id, timestamp, time_frame)
);

-- =============================================
-- MARKET STATUS AND METADATA
-- =============================================

-- Market sessions table
CREATE TABLE IF NOT EXISTS market_sessions (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    session_name VARCHAR(100) NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Market status table
CREATE TABLE IF NOT EXISTS market_status (
    id SERIAL PRIMARY KEY,
    exchange VARCHAR(50) NOT NULL,
    is_open BOOLEAN NOT NULL,
    next_open TIMESTAMP WITH TIME ZONE,
    next_close TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(exchange)
);

-- Data sources configuration
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    api_key VARCHAR(255),
    base_url VARCHAR(255) NOT NULL,
    rate_limit_per_minute INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- PRODUCTION INDEXES
-- =============================================

-- Market data indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol_id, timestamp DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_market_data_timeframe ON market_data(time_frame);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_market_data_symbol_timeframe ON market_data(symbol_id, time_frame, timestamp DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_market_data_source_timestamp ON market_data(data_source, timestamp DESC);

-- Real-time prices indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_real_time_prices_symbol ON real_time_prices(symbol_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_real_time_prices_updated ON real_time_prices(last_updated DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_real_time_prices_source ON real_time_prices(data_source, last_updated DESC);

-- Technical indicators indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technical_indicators_symbol_timestamp ON technical_indicators(symbol_id, timestamp DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technical_indicators_timeframe ON technical_indicators(time_frame);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technical_indicators_timeframe_timestamp ON technical_indicators(time_frame, timestamp DESC);

-- Symbols indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_symbols_symbol ON symbols(symbol);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_symbols_asset_type ON symbols(asset_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_symbols_exchange ON symbols(exchange);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_symbols_active ON symbols(is_active);

-- =============================================
-- PRODUCTION VIEWS
-- =============================================

-- View for latest prices with symbol information
CREATE OR REPLACE VIEW latest_prices AS
SELECT 
    s.symbol,
    s.name,
    s.exchange,
    s.asset_type,
    s.currency,
    rtp.price,
    rtp.bid,
    rtp.ask,
    rtp.volume_24h,
    rtp.change_24h,
    rtp.change_percent_24h,
    rtp.market_cap,
    rtp.data_source,
    rtp.last_updated
FROM real_time_prices rtp
JOIN symbols s ON rtp.symbol_id = s.id
WHERE s.is_active = TRUE;

-- View for market data with symbol information
CREATE OR REPLACE VIEW market_data_with_symbols AS
SELECT 
    s.symbol,
    s.name,
    s.exchange,
    s.asset_type,
    md.timestamp,
    md.open,
    md.high,
    md.low,
    md.close,
    md.volume,
    md.adjusted_close,
    md.time_frame,
    md.data_source,
    md.created_at
FROM market_data md
JOIN symbols s ON md.symbol_id = s.id
WHERE s.is_active = TRUE;

-- View for technical indicators with symbol information
CREATE OR REPLACE VIEW technical_indicators_with_symbols AS
SELECT 
    s.symbol,
    s.name,
    s.exchange,
    ti.timestamp,
    ti.time_frame,
    ti.sma_5, ti.sma_10, ti.sma_20, ti.sma_50, ti.sma_200,
    ti.ema_12, ti.ema_26,
    ti.rsi_14,
    ti.macd, ti.macd_signal, ti.macd_histogram,
    ti.stoch_k, ti.stoch_d,
    ti.bollinger_upper, ti.bollinger_middle, ti.bollinger_lower,
    ti.atr_14,
    ti.volume_sma_20, ti.obv,
    ti.adx, ti.cci, ti.williams_r,
    ti.created_at
FROM technical_indicators ti
JOIN symbols s ON ti.symbol_id = s.id
WHERE s.is_active = TRUE;
