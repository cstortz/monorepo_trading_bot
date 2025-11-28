-- Trading Bot Database Seed Data - Production
-- DML for inserting initial data with production considerations

-- =============================================
-- DATA SOURCES
-- =============================================

INSERT INTO data_sources (name, base_url, rate_limit_per_minute, is_active) VALUES
('alpha_vantage', 'https://www.alphavantage.co/query', 5, true),
('yahoo_finance', 'https://query1.finance.yahoo.com/v8/finance/chart', 100, true),
('binance', 'https://api.binance.com/api/v3', 1200, true),
('coinbase', 'https://api.exchange.coinbase.com', 10, true),
('polygon', 'https://api.polygon.io/v2', 5, true),
('finnhub', 'https://finnhub.io/api/v1', 60, true)
ON CONFLICT (name) DO NOTHING;

-- =============================================
-- MARKET SESSIONS
-- =============================================

INSERT INTO market_sessions (exchange, session_name, timezone, open_time, close_time, is_active) VALUES
('NYSE', 'Regular Trading', 'America/New_York', '09:30:00', '16:00:00', true),
('NASDAQ', 'Regular Trading', 'America/New_York', '09:30:00', '16:00:00', true),
('LSE', 'Regular Trading', 'Europe/London', '08:00:00', '16:30:00', true),
('TSE', 'Regular Trading', 'Asia/Tokyo', '09:00:00', '15:00:00', true),
('HKEX', 'Regular Trading', 'Asia/Hong_Kong', '09:30:00', '16:00:00', true),
('BINANCE', '24/7 Trading', 'UTC', '00:00:00', '23:59:59', true),
('COINBASE', '24/7 Trading', 'UTC', '00:00:00', '23:59:59', true)
ON CONFLICT DO NOTHING;

-- =============================================
-- POPULAR SYMBOLS (Production Set)
-- =============================================

-- Major US Stocks
INSERT INTO symbols (symbol, name, exchange, asset_type, currency, sector, industry, market_cap, is_active) VALUES
('AAPL', 'Apple Inc.', 'NASDAQ', 'stock', 'USD', 'Technology', 'Consumer Electronics', 3000000000000, true),
('MSFT', 'Microsoft Corporation', 'NASDAQ', 'stock', 'USD', 'Technology', 'Software', 2800000000000, true),
('GOOGL', 'Alphabet Inc. Class A', 'NASDAQ', 'stock', 'USD', 'Technology', 'Internet', 1800000000000, true),
('AMZN', 'Amazon.com Inc.', 'NASDAQ', 'stock', 'USD', 'Consumer Discretionary', 'E-commerce', 1500000000000, true),
('TSLA', 'Tesla Inc.', 'NASDAQ', 'stock', 'USD', 'Consumer Discretionary', 'Electric Vehicles', 800000000000, true),
('META', 'Meta Platforms Inc.', 'NASDAQ', 'stock', 'USD', 'Technology', 'Social Media', 700000000000, true),
('NVDA', 'NVIDIA Corporation', 'NASDAQ', 'stock', 'USD', 'Technology', 'Semiconductors', 1200000000000, true),
('BRK.A', 'Berkshire Hathaway Inc. Class A', 'NYSE', 'stock', 'USD', 'Financial Services', 'Insurance', 800000000000, true),
('JPM', 'JPMorgan Chase & Co.', 'NYSE', 'stock', 'USD', 'Financial Services', 'Banking', 400000000000, true),
('JNJ', 'Johnson & Johnson', 'NYSE', 'stock', 'USD', 'Healthcare', 'Pharmaceuticals', 400000000000, true),
('V', 'Visa Inc.', 'NYSE', 'stock', 'USD', 'Financial Services', 'Payment Processing', 500000000000, true),
('PG', 'Procter & Gamble Co.', 'NYSE', 'stock', 'USD', 'Consumer Staples', 'Household Products', 350000000000, true),
('UNH', 'UnitedHealth Group Inc.', 'NYSE', 'stock', 'USD', 'Healthcare', 'Health Insurance', 450000000000, true),
('HD', 'Home Depot Inc.', 'NYSE', 'stock', 'USD', 'Consumer Discretionary', 'Retail', 300000000000, true),
('MA', 'Mastercard Inc.', 'NYSE', 'stock', 'USD', 'Financial Services', 'Payment Processing', 400000000000, true)
ON CONFLICT (symbol) DO NOTHING;

-- Major Crypto Currencies
INSERT INTO symbols (symbol, name, exchange, asset_type, currency, sector, industry, is_active) VALUES
('BTC', 'Bitcoin', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('ETH', 'Ethereum', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('BNB', 'Binance Coin', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('ADA', 'Cardano', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('SOL', 'Solana', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('XRP', 'Ripple', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('DOT', 'Polkadot', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('DOGE', 'Dogecoin', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('AVAX', 'Avalanche', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('MATIC', 'Polygon', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('LINK', 'Chainlink', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('UNI', 'Uniswap', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('LTC', 'Litecoin', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('BCH', 'Bitcoin Cash', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true),
('ATOM', 'Cosmos', 'BINANCE', 'crypto', 'USD', 'Cryptocurrency', 'Digital Currency', true)
ON CONFLICT (symbol) DO NOTHING;

-- Major Forex Pairs
INSERT INTO symbols (symbol, name, exchange, asset_type, currency, sector, industry, is_active) VALUES
('EURUSD', 'Euro / US Dollar', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('GBPUSD', 'British Pound / US Dollar', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('USDJPY', 'US Dollar / Japanese Yen', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('USDCHF', 'US Dollar / Swiss Franc', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('AUDUSD', 'Australian Dollar / US Dollar', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('USDCAD', 'US Dollar / Canadian Dollar', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('NZDUSD', 'New Zealand Dollar / US Dollar', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('EURGBP', 'Euro / British Pound', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('EURJPY', 'Euro / Japanese Yen', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('GBPJPY', 'British Pound / Japanese Yen', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('EURCHF', 'Euro / Swiss Franc', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('AUDJPY', 'Australian Dollar / Japanese Yen', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('GBPCHF', 'British Pound / Swiss Franc', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('EURCAD', 'Euro / Canadian Dollar', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true),
('AUDCAD', 'Australian Dollar / Canadian Dollar', 'FOREX', 'forex', 'USD', 'Foreign Exchange', 'Currency Pair', true)
ON CONFLICT (symbol) DO NOTHING;

-- Major Indices
INSERT INTO symbols (symbol, name, exchange, asset_type, currency, sector, industry, is_active) VALUES
('SPX', 'S&P 500 Index', 'NYSE', 'index', 'USD', 'Market Index', 'Broad Market', true),
('DJI', 'Dow Jones Industrial Average', 'NYSE', 'index', 'USD', 'Market Index', 'Broad Market', true),
('IXIC', 'NASDAQ Composite', 'NASDAQ', 'index', 'USD', 'Market Index', 'Technology', true),
('RUT', 'Russell 2000 Index', 'NYSE', 'index', 'USD', 'Market Index', 'Small Cap', true),
('VIX', 'CBOE Volatility Index', 'CBOE', 'index', 'USD', 'Market Index', 'Volatility', true),
('FTSE', 'FTSE 100 Index', 'LSE', 'index', 'GBP', 'Market Index', 'Broad Market', true),
('N225', 'Nikkei 225 Index', 'TSE', 'index', 'JPY', 'Market Index', 'Broad Market', true),
('HSI', 'Hang Seng Index', 'HKEX', 'index', 'HKD', 'Market Index', 'Broad Market', true),
('DAX', 'DAX Index', 'XETRA', 'index', 'EUR', 'Market Index', 'Broad Market', true),
('CAC', 'CAC 40 Index', 'EPA', 'index', 'EUR', 'Market Index', 'Broad Market', true)
ON CONFLICT (symbol) DO NOTHING;

-- =============================================
-- MARKET STATUS INITIALIZATION
-- =============================================

INSERT INTO market_status (exchange, is_open, next_open, next_close) VALUES
('NYSE', false, CURRENT_TIMESTAMP + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '6.5 hours'),
('NASDAQ', false, CURRENT_TIMESTAMP + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '6.5 hours'),
('LSE', false, CURRENT_TIMESTAMP + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '8.5 hours'),
('TSE', false, CURRENT_TIMESTAMP + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '6 hours'),
('HKEX', false, CURRENT_TIMESTAMP + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '6.5 hours'),
('XETRA', false, CURRENT_TIMESTAMP + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '8 hours'),
('EPA', false, CURRENT_TIMESTAMP + INTERVAL '1 day', CURRENT_TIMESTAMP + INTERVAL '1 day' + INTERVAL '8 hours'),
('BINANCE', true, NULL, NULL),
('COINBASE', true, NULL, NULL)
ON CONFLICT (exchange) DO NOTHING;
