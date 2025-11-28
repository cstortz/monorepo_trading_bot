"""
Database Client for Trading Bot Monorepo
Interacts with the database web service at dev01.int.stortz.tech:8000
"""

import httpx
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger(__name__)


class DateTimeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            # Return datetime object as-is for httpx to handle
            # httpx will serialize it properly
            return obj
        return super().default(obj)


class DatabaseClient:
    """Client for interacting with the database web service."""
    
    def __init__(self, base_url: str = "http://dev01.int.stortz.tech:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the database service is healthy."""
        try:
            response = self.client.get(f"{self.base_url}/admin/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information."""
        try:
            response = self.client.get(f"{self.base_url}/admin/db-info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get database info", error=str(e))
            return {"error": str(e)}
    
    def get_tables(self) -> Dict[str, Any]:
        """Get all tables in the database."""
        try:
            response = self.client.get(f"{self.base_url}/admin/tables")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get tables", error=str(e))
            return {"error": str(e)}
    
    def execute_prepared_sql(self, sql: str, parameters: Optional[Dict] = None, operation_type: str = "read") -> Dict[str, Any]:
        """Execute a prepared SQL statement."""
        url = f"{self.base_url}/crud/prepared/execute"
        try:
            payload = {
                "sql": sql,
                "parameters": parameters or {},
                "operation_type": operation_type
            }
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared SQL - HTTP error",
                error=str(e),
                url=url,
                status_code=e.response.status_code,
                response_text=e.response.text if e.response else None,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
        except Exception as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared SQL",
                error=str(e),
                url=url,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
    
    def execute_prepared_select(self, sql: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a prepared SELECT statement."""
        url = f"{self.base_url}/crud/prepared/select"
        try:
            payload = {
                "sql": sql,
                "parameters": parameters or {}
            }
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared SELECT - HTTP error",
                error=str(e),
                url=url,
                status_code=e.response.status_code,
                response_text=e.response.text if e.response else None,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
        except Exception as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared SELECT",
                error=str(e),
                url=url,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
    
    def execute_prepared_insert(self, sql: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a prepared INSERT statement."""
        url = f"{self.base_url}/crud/prepared/insert"
        try:
            payload = {
                "sql": sql,
                "parameters": parameters or {}
            }
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared INSERT - HTTP error",
                error=str(e),
                url=url,
                status_code=e.response.status_code,
                response_text=e.response.text if e.response else None,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
        except Exception as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared INSERT",
                error=str(e),
                url=url,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
    
    def execute_prepared_update(self, sql: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a prepared UPDATE statement."""
        url = f"{self.base_url}/crud/prepared/update"
        try:
            payload = {
                "sql": sql,
                "parameters": parameters or {}
            }
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared UPDATE - HTTP error",
                error=str(e),
                url=url,
                status_code=e.response.status_code,
                response_text=e.response.text if e.response else None,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
        except Exception as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared UPDATE",
                error=str(e),
                url=url,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
    
    def execute_prepared_delete(self, sql: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a prepared DELETE statement."""
        url = f"{self.base_url}/crud/prepared/delete"
        try:
            payload = {
                "sql": sql,
                "parameters": parameters or {}
            }
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared DELETE - HTTP error",
                error=str(e),
                url=url,
                status_code=e.response.status_code,
                response_text=e.response.text if e.response else None,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
        except Exception as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to execute prepared DELETE",
                error=str(e),
                url=url,
                payload_json=payload_json,
                sql=sql
            )
            return {"success": False, "error": str(e)}
    
    def validate_sql(self, sql: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate a SQL statement without executing it."""
        url = f"{self.base_url}/crud/prepared/validate"
        try:
            payload = {
                "sql": sql,
                "parameters": parameters or {}
            }
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to validate SQL - HTTP error",
                error=str(e),
                url=url,
                status_code=e.response.status_code,
                response_text=e.response.text if e.response else None,
                payload_json=payload_json,
                sql=sql
            )
            return {"valid": False, "error": str(e)}
        except Exception as e:
            # Log the JSON payload that was sent
            payload_json = json.dumps(payload, indent=2, default=str)
            logger.error(
                "Failed to validate SQL",
                error=str(e),
                url=url,
                payload_json=payload_json,
                sql=sql
            )
            return {"valid": False, "error": str(e)}
    
    def get_prepared_statements(self) -> Dict[str, Any]:
        """Get information about cached prepared statements."""
        try:
            response = self.client.get(f"{self.base_url}/crud/prepared/statements")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get prepared statements", error=str(e))
            return {"error": str(e)}
    
    def clear_prepared_statements(self) -> bool:
        """Clear all prepared statements from cache."""
        try:
            response = self.client.delete(f"{self.base_url}/crud/prepared/statements")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error("Failed to clear prepared statements", error=str(e))
            return False


class TradingBotDatabase:
    """High-level database operations for the trading bot."""
    
    def __init__(self, client: DatabaseClient):
        self.client = client
    
    def create_tables(self, environment: str = "dev") -> bool:
        """Create all trading bot tables."""
        try:
            # Read the appropriate SQL file (use simple version for now)
            sql_file = f"sql/{environment}/01_create_tables_simple.sql"
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement.upper().startswith(('CREATE', 'ALTER', 'DROP', 'INSERT')):
                    result = self.client.execute_prepared_sql(statement, operation_type="write")
                    if not result.get("success", False):
                        logger.error("Failed to execute statement", statement=statement, result=result)
                        return False
            
            logger.info("Successfully created all tables", environment=environment)
            return True
            
        except Exception as e:
            logger.error("Failed to create tables", error=str(e), environment=environment)
            return False
    
    def seed_data(self, environment: str = "dev") -> bool:
        """Seed the database with initial data."""
        try:
            # Read the appropriate SQL file
            sql_file = f"sql/{environment}/02_seed_data.sql" if environment == "dev" else f"sql/{environment}/03_seed_data.sql"
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement.upper().startswith('INSERT'):
                    result = self.client.execute_prepared_sql(statement, operation_type="write")
                    if not result.get("success", False):
                        logger.error("Failed to execute statement", statement=statement, result=result)
                        return False
            
            logger.info("Successfully seeded database", environment=environment)
            return True
            
        except Exception as e:
            logger.error("Failed to seed database", error=str(e), environment=environment)
            return False
    
    def get_symbols(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all symbols."""
        sql = "SELECT * FROM symbols ORDER BY symbol LIMIT $1 OFFSET $2"
        result = self.client.execute_prepared_select(sql, {"1": limit, "2": offset})
        return result.get("data", []) if result.get("success") else []
    
    def get_symbol_by_name(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get a symbol by its name."""
        sql = "SELECT * FROM symbols WHERE symbol = $1"
        result = self.client.execute_prepared_select(sql, {"1": symbol})
        data = result.get("data", [])
        return data[0] if data else None
    
    def create_symbol(self, symbol_data: Dict[str, Any]) -> bool:
        """Create a new symbol."""
        sql = """
        INSERT INTO symbols (symbol, name, exchange, asset_type, currency, sector, industry, market_cap, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
        """
        result = self.client.execute_prepared_insert(sql, {
            "1": symbol_data["symbol"],
            "2": symbol_data["name"],
            "3": symbol_data["exchange"],
            "4": symbol_data["asset_type"],
            "5": symbol_data.get("currency", "USD"),
            "6": symbol_data.get("sector"),
            "7": symbol_data.get("industry"),
            "8": symbol_data.get("market_cap"),
            "9": symbol_data.get("is_active", True)
        })
        return result.get("success", False)
    
    def update_symbol(self, symbol: str, update_data: Dict[str, Any]) -> bool:
        """Update a symbol."""
        sql = "UPDATE symbols SET name = $1, sector = $2, industry = $3, market_cap = $4, updated_at = CURRENT_TIMESTAMP WHERE symbol = $5 RETURNING *"
        result = self.client.execute_prepared_update(sql, {
            "1": update_data.get("name"),
            "2": update_data.get("sector"),
            "3": update_data.get("industry"),
            "4": update_data.get("market_cap"),
            "5": symbol
        })
        return result.get("success", False)
    
    def delete_symbol(self, symbol: str) -> bool:
        """Delete a symbol."""
        sql = "DELETE FROM symbols WHERE symbol = $1 RETURNING *"
        result = self.client.execute_prepared_delete(sql, {"1": symbol})
        return result.get("success", False)
    
    def get_market_data(self, symbol: str, timeframe: str = "1d", limit: int = 100) -> List[Dict[str, Any]]:
        """Get market data for a symbol."""
        sql = """
        SELECT md.*, md.t_stamp AS timestamp, s.symbol, s.name 
        FROM market_data md
        JOIN symbols s ON md.symbol_id = s.id
        WHERE s.symbol = $1 AND md.time_frame = $2
        ORDER BY md.t_stamp DESC
        LIMIT $3
        """
        result = self.client.execute_prepared_select(sql, {
            "1": symbol,
            "2": timeframe,
            "3": limit
        })
        return result.get("data", []) if result.get("success") else []
    
    def get_distinct_timeframes(self, symbol: str) -> List[str]:
        """Get distinct timeframes available for a symbol."""
        sql = """
        SELECT DISTINCT md.time_frame
        FROM market_data md
        JOIN symbols s ON md.symbol_id = s.id
        WHERE s.symbol = $1
        ORDER BY md.time_frame
        """
        result = self.client.execute_prepared_select(sql, {"1": symbol})
        if result.get("success"):
            data = result.get("data", [])
            return [item.get("time_frame") for item in data if item.get("time_frame")]
        return []
    
    def insert_market_data(self, symbol_id: int, market_data: Dict[str, Any]) -> bool:
        """Insert market data."""
        sql = """
        INSERT INTO market_data (symbol_id, t_stamp, open, high, low, close, volume, adjusted_close, time_frame, data_source)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (symbol_id, t_stamp, time_frame, data_source) DO NOTHING
        RETURNING *
        """
        # Convert datetime to ISO format string for JSON serialization
        # The database API now accepts ISO format strings
        timestamp = market_data["timestamp"]
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()
        elif hasattr(timestamp, 'isoformat'):
            timestamp = timestamp.isoformat()
        # If it's already a string, keep it as-is (assume it's already in ISO format)
        
        result = self.client.execute_prepared_insert(sql, {
            "1": symbol_id,
            "2": timestamp,
            "3": market_data["open"],
            "4": market_data["high"],
            "5": market_data["low"],
            "6": market_data["close"],
            "7": market_data.get("volume", 0),
            "8": market_data.get("adjusted_close"),
            "9": market_data["time_frame"],
            "10": market_data["data_source"]
        })
        return result.get("success", False)
    
    def get_real_time_prices(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get real-time prices."""
        sql = """
        SELECT rtp.*, s.symbol, s.name, s.exchange, s.asset_type
        FROM real_time_prices rtp
        JOIN symbols s ON rtp.symbol_id = s.id
        ORDER BY rtp.last_updated DESC
        LIMIT $1
        """
        result = self.client.execute_prepared_select(sql, {"1": limit})
        return result.get("data", []) if result.get("success") else []
    
    def update_real_time_price(self, symbol_id: int, price_data: Dict[str, Any]) -> bool:
        """Update real-time price."""
        sql = """
        INSERT INTO real_time_prices (symbol_id, price, bid, ask, volume_24h, change_24h, change_percent_24h, market_cap, data_source)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (symbol_id, data_source) 
        DO UPDATE SET
            price = EXCLUDED.price,
            bid = EXCLUDED.bid,
            ask = EXCLUDED.ask,
            volume_24h = EXCLUDED.volume_24h,
            change_24h = EXCLUDED.change_24h,
            change_percent_24h = EXCLUDED.change_percent_24h,
            market_cap = EXCLUDED.market_cap,
            last_updated = CURRENT_TIMESTAMP
        RETURNING *
        """
        result = self.client.execute_prepared_insert(sql, {
            "1": symbol_id,
            "2": price_data["price"],
            "3": price_data.get("bid"),
            "4": price_data.get("ask"),
            "5": price_data.get("volume_24h"),
            "6": price_data.get("change_24h"),
            "7": price_data.get("change_percent_24h"),
            "8": price_data.get("market_cap"),
            "9": price_data["data_source"]
        })
        return result.get("success", False)
