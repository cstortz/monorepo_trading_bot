"""
Kraken API Client for Market Data Collection

Fetches OHLCV data and real-time prices from Kraken exchange.
"""

import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger(__name__)


class KrakenClient:
    """Client for interacting with Kraken REST API."""
    
    BASE_URL = "https://api.kraken.com/0/public"
    
    # Kraken timeframe mapping to our timeframes
    TIMEFRAME_MAP = {
        "1m": 1,      # 1 minute
        "5m": 5,      # 5 minutes
        "15m": 15,    # 15 minutes
        "30m": 30,    # 30 minutes
        "1h": 60,     # 1 hour
        "4h": 240,    # 4 hours
        "1d": 1440,   # 1 day
        "1w": 10080,  # 1 week
        "1M": 21600,  # 1 month (approximate)
    }
    
    def __init__(self, timeout: float = 30.0):
        """Initialize Kraken client."""
        self.client = httpx.Client(timeout=timeout)
        self.base_url = self.BASE_URL
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to Kraken API."""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error"):
                error_msg = ", ".join(data["error"])
                logger.error(f"Kraken API error: {error_msg}")
                raise Exception(f"Kraken API error: {error_msg}")
            
            return data.get("result", {})
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Kraken API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Kraken API: {e}")
            raise
    
    def get_ohlc(
        self, 
        pair: str, 
        interval: int = 60, 
        since: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get OHLC (Open, High, Low, Close) data for a trading pair.
        
        Args:
            pair: Trading pair (e.g., 'XBTUSD' for BTC/USD)
            interval: Time interval in minutes (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
            since: Return committed OHLC data since given ID (optional)
            
        Returns:
            Dictionary with 'pair' and 'data' (list of OHLC records)
        """
        params = {
            "pair": pair,
            "interval": interval
        }
        
        if since:
            params["since"] = since
        
        result = self._make_request("OHLC", params)
        
        # Kraken returns data keyed by the pair name
        pair_key = list(result.keys())[0] if result else None
        if pair_key:
            return {
                "pair": pair_key,
                "data": result[pair_key],
                "last": result.get("last", 0)
            }
        
        return {"pair": pair, "data": [], "last": 0}
    
    def get_ticker(self, pair: str) -> Dict[str, Any]:
        """
        Get ticker information for a trading pair.
        
        Args:
            pair: Trading pair (e.g., 'XBTUSD' for BTC/USD)
            
        Returns:
            Dictionary with ticker data including current price, bid, ask, volume
        """
        params = {"pair": pair}
        result = self._make_request("Ticker", params)
        
        pair_key = list(result.keys())[0] if result else None
        if pair_key:
            return result[pair_key]
        
        return {}
    
    def get_asset_pairs(self) -> Dict[str, Any]:
        """
        Get all available asset pairs from Kraken.
        
        Returns:
            Dictionary of asset pairs with their metadata
        """
        result = self._make_request("AssetPairs")
        return result
    
    def normalize_pair(self, pair: str) -> str:
        """
        Normalize pair name to Kraken format.
        Converts common formats like 'BTC/USD' or 'BTCUSD' to 'XBTUSD'
        
        Args:
            pair: Trading pair in various formats
            
        Returns:
            Normalized pair name for Kraken API
        """
        # Remove slashes and convert to uppercase
        pair = pair.replace("/", "").replace("-", "").upper()
        
        # Common mappings
        mappings = {
            "BTC": "XBT",
            "BTCUSD": "XBTUSD",
            "BTCUSDT": "XBTUSDT",
            "ETHUSD": "ETHUSD",
            "ETHUSDT": "ETHUSDT",
        }
        
        return mappings.get(pair, pair)
    
    def parse_ohlc_data(
        self, 
        ohlc_data: List, 
        timeframe: str,
        pair: str
    ) -> List[Dict[str, Any]]:
        """
        Parse Kraken OHLC data into our format.
        
        Kraken OHLC format: [time, open, high, low, close, vwap, volume, count]
        
        Args:
            ohlc_data: List of OHLC records from Kraken
            timeframe: Timeframe string (e.g., '1d', '1h')
            pair: Trading pair name
            
        Returns:
            List of parsed market data dictionaries
        """
        parsed_data = []
        
        for record in ohlc_data:
            if len(record) < 8:
                continue
            
            timestamp_unix = int(record[0])
            timestamp = datetime.fromtimestamp(timestamp_unix, tz=timezone.utc)
            
            parsed_data.append({
                "timestamp": timestamp,
                "open": float(record[1]),
                "high": float(record[2]),
                "low": float(record[3]),
                "close": float(record[4]),
                "volume": float(record[6]),  # Volume is at index 6
                "adjusted_close": float(record[4]),  # Use close as adjusted_close
                "time_frame": timeframe,
                "data_source": "kraken",
                "pair": pair
            })
        
        return parsed_data
    
    def parse_ticker_data(self, ticker_data: Dict, pair: str) -> Dict[str, Any]:
        """
        Parse Kraken ticker data into our real-time price format.
        
        Args:
            ticker_data: Ticker data from Kraken API
            pair: Trading pair name
            
        Returns:
            Dictionary with real-time price data
        """
        # Kraken ticker format: {'a': [price, volume, volume], 'b': [price, volume, volume], 'c': [price, volume], ...}
        ask = ticker_data.get("a", [0, 0, 0])
        bid = ticker_data.get("b", [0, 0, 0])
        close = ticker_data.get("c", [0, 0])
        volume = ticker_data.get("v", [0, 0])
        high_low = ticker_data.get("h", [0, 0])
        open_price_raw = ticker_data.get("o", 0)
        
        # Convert all values to float to ensure type safety
        current_price = float(close[0]) if close else 0.0
        ask_price = float(ask[0]) if ask else None
        bid_price = float(bid[0]) if bid else None
        volume_24h = float(volume[1]) if len(volume) > 1 else None
        
        # Calculate 24h change
        high_24h = float(high_low[0]) if high_low else current_price
        low_24h = float(high_low[1]) if len(high_low) > 1 else current_price
        
        # Convert open_price to float (it might be a string from the API)
        try:
            open_price = float(open_price_raw) if open_price_raw else None
        except (ValueError, TypeError):
            open_price = None
        
        change_24h = (current_price - open_price) if open_price is not None else None
        change_percent_24h = ((current_price - open_price) / open_price * 100) if open_price is not None and open_price > 0 else None
        
        return {
            "price": current_price,
            "bid": bid_price,
            "ask": ask_price,
            "volume_24h": int(volume_24h) if volume_24h else None,
            "change_24h": change_24h,
            "change_percent_24h": change_percent_24h,
            "data_source": "kraken",
            "pair": pair
        }
    
    def get_timeframe_interval(self, timeframe: str) -> int:
        """Convert timeframe string to Kraken interval in minutes."""
        return self.TIMEFRAME_MAP.get(timeframe, 60)


def get_kraken_symbol_mapping() -> Dict[str, str]:
    """
    Map Kraken pair names to our database symbols.
    
    Returns:
        Dictionary mapping Kraken pairs to database symbols
    """
    return {
        "XBTUSD": "BTC/USD",
        "XBTUSDT": "BTC/USDT",
        "ETHUSD": "ETH/USD",
        "ETHUSDT": "ETH/USDT",
        "ADAUSD": "ADA/USD",
        "ADAUSDT": "ADA/USDT",
        "SOLUSD": "SOL/USD",
        "SOLUSDT": "SOL/USDT",
        "DOTUSD": "DOT/USD",
        "DOTUSDT": "DOT/USDT",
        "MATICUSD": "MATIC/USD",
        "MATICUSDT": "MATIC/USDT",
        "LINKUSD": "LINK/USD",
        "LINKUSDT": "LINK/USDT",
        "AVAXUSD": "AVAX/USD",
        "AVAXUSDT": "AVAX/USDT",
        "ATOMUSD": "ATOM/USD",
        "ATOMUSDT": "ATOM/USDT",
        "ALGOUSD": "ALGO/USD",
        "ALGOUSDT": "ALGO/USDT",
        # Add more pairs here as needed
        # Format: "KRAKENPAIR": "SYMBOL/QUOTE"
        # Example: "DOGEUSD": "DOGE/USD",
    }

