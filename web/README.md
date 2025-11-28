# Trading Bot Monorepo Web Interface

A modern web dashboard for managing and interacting with the Trading Bot monorepo services.

## Features

- **Market Data Tab**: 
  - View service status
  - Browse available Kraken trading pairs
  - Add new trading pairs
  - Fetch historical OHLC data
  - Fetch real-time ticker data
  - View stored market data
  - Sync symbols to database

- **Hello World Tab**: Basic service status and information

- **Future Tabs**: Placeholders for Strategy Engine, Order Management, Portfolio Manager, and Risk Management

## Running the Web Interface

### Option 1: Using Docker Compose (Recommended)

```bash
# Start the web server
docker compose up -d web

# Access at http://localhost:5080
```

### Option 2: Using Python HTTP Server

```bash
cd web
python3 server.py

# Access at http://localhost:5080
```

### Option 3: Using Python's Built-in Server

```bash
cd web
python3 -m http.server 5080

# Access at http://localhost:5080
```

## Configuration

The web interface automatically detects API URLs based on the current page URL:

- **Same host, different ports**: If accessing `http://example.com:5080`, services are assumed at `http://example.com:5001` and `http://example.com:5000`
- **Reverse proxy**: If behind a proxy with path-based routing, services are detected from the current path
- **Default ports**: Web on 5080, Market Data on 5001, Hello World on 5000

The API URLs are dynamically determined in `web/app.js` using the `getApiBaseUrls()` function. The detected URLs are logged to the browser console for debugging.

## Development

The web interface is a static site with:
- `index.html` - Main HTML structure
- `styles.css` - Styling and layout
- `app.js` - JavaScript for API interactions
- `server.py` - Simple Python HTTP server

## Browser Compatibility

Works with all modern browsers (Chrome, Firefox, Safari, Edge).

