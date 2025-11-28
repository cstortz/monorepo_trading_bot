// API Base URLs - Dynamically determined from current page location
function getApiBaseUrls() {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port;
    const pathname = window.location.pathname;
    
    // Get the base URL (protocol + hostname)
    const baseHost = `${protocol}//${hostname}`;
    
    // Check if we're behind a reverse proxy (path-based routing)
    // Look for patterns like /web, /dashboard, etc. in the path
    const pathParts = pathname.split('/').filter(p => p);
    const isProxied = pathParts.length > 0 && (pathParts[0] === 'web' || pathParts[0] === 'dashboard');
    
    if (isProxied) {
        // Behind reverse proxy - services likely on same host/port with different paths
        const basePath = pathname.substring(0, pathname.lastIndexOf('/'));
        const rootPath = pathname.split('/').slice(0, -pathParts.length).join('/') || '';
        return {
            marketData: `${baseHost}${port ? ':' + port : ''}${rootPath}/market-data`,
            helloWorld: `${baseHost}${port ? ':' + port : ''}${rootPath}/hello-world`
        };
    }
    
    // Not behind proxy - use port-based routing
    // Default ports: Web=5080, Market Data=5001, Hello World=5000
    const webPort = port ? parseInt(port) : (protocol === 'https:' ? 443 : 80);
    
    // Standard setup: web on 5080, services on 5000 and 5001
    if (webPort === 5080 || webPort === 80 || webPort === 443 || !port) {
        return {
            marketData: `${baseHost}:5001`,
            helloWorld: `${baseHost}:5000`
        };
    }
    
    // If web is on a different port in the 5000-5100 range, 
    // assume services are on the standard ports
    if (webPort >= 5000 && webPort <= 5100) {
        return {
            marketData: `${baseHost}:5001`,
            helloWorld: `${baseHost}:5000`
        };
    }
    
    // Fallback: try to use relative API paths (for reverse proxy scenarios)
    return {
        marketData: `${baseHost}${port ? ':' + port : ''}/api/market-data`,
        helloWorld: `${baseHost}${port ? ':' + port : ''}/api/hello-world`
    };
}

// Initialize API base URLs
// Allow manual override via window.API_CONFIG
let API_BASE;
if (window.API_CONFIG && window.API_CONFIG.marketData && window.API_CONFIG.helloWorld) {
    // Use manual configuration if provided
    API_BASE = window.API_CONFIG;
    console.log('Using manual API configuration:', API_BASE);
} else {
    // Auto-detect from current URL
    API_BASE = getApiBaseUrls();
    console.log('Current page URL:', window.location.href);
    console.log('Auto-detected API URLs:', API_BASE);
}

// Display API URLs in the UI
function updateApiConfigDisplay() {
    const marketDataEl = document.getElementById('api-market-data-url');
    const helloWorldEl = document.getElementById('api-hello-world-url');
    
    if (marketDataEl) {
        marketDataEl.textContent = API_BASE.marketData;
        marketDataEl.style.color = 'var(--primary-color)';
    }
    if (helloWorldEl) {
        helloWorldEl.textContent = API_BASE.helloWorld;
        helloWorldEl.style.color = 'var(--primary-color)';
    }
}

// Tab Management
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        
        // Load tab-specific data
        if (tabName === 'market-data') {
            checkMarketDataStatus();
        }
    });
});

// Market Data Functions
async function checkMarketDataStatus() {
    const statusEl = document.getElementById('market-data-status');
    const statusDot = statusEl.querySelector('.status-dot');
    const statusText = statusEl.querySelector('span:last-child');
    const statusDetails = document.getElementById('status-details');
    const statusDetailsContent = document.getElementById('status-details-content');
    
    statusText.textContent = 'Checking...';
    statusDot.className = 'status-dot';
    if (statusDetails) statusDetails.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE.marketData}/health`);
        const data = await response.json();
        
        statusDot.classList.add(data.status === 'healthy' ? 'healthy' : 'degraded');
        statusText.innerHTML = `Status: <strong>${data.status.toUpperCase()}</strong> - ${data.service} v${data.version}`;
        
        // Show detailed status information
        if (statusDetails && statusDetailsContent) {
            let detailsHTML = '';
            
            if (data.database_status) {
                const dbStatusClass = data.database_status === 'healthy' ? 'success' : 'error';
                const dbStatusIcon = data.database_status === 'healthy' ? '✅' : '⚠️';
                detailsHTML += `
                    <div style="margin-bottom: 8px;">
                        <strong>Database API Web Service Status:</strong> 
                        <span class="result-message ${dbStatusClass}" style="display: inline-block; padding: 4px 8px; margin-left: 8px;">
                            ${dbStatusIcon} ${data.database_status.toUpperCase()}
                        </span>
                    </div>
                `;
                
                if (data.database_url) {
                    detailsHTML += `<div style="margin-bottom: 8px;"><strong>Database API URL:</strong> <code>${data.database_url}</code></div>`;
                }
            }
            
            if (data.message && data.status === 'degraded') {
                detailsHTML += `
                    <div class="result-message error" style="margin-top: 8px;">
                        <strong>Note:</strong> ${data.message}<br>
                        <small>The service is running but cannot connect to the database API web service. Kraken API features (fetching pairs, OHLC data, ticker data) will still work, but data cannot be stored/retrieved from the database.</small>
                    </div>
                `;
            }
            
            if (data.status === 'healthy') {
                detailsHTML += `
                    <div class="result-message success" style="margin-top: 8px;">
                        ✅ All systems operational
                    </div>
                `;
            }
            
            statusDetailsContent.innerHTML = detailsHTML;
            statusDetails.style.display = 'block';
        }
    } catch (error) {
        statusDot.classList.add('unhealthy');
        statusText.textContent = 'Status: OFFLINE - Service unavailable';
        if (statusDetails && statusDetailsContent) {
            statusDetailsContent.innerHTML = `
                <div class="result-message error">
                    <strong>Error:</strong> ${error.message}<br>
                    <small>Unable to reach the market-data service. Check if the service is running.</small>
                </div>
            `;
            statusDetails.style.display = 'block';
        }
    }
}

document.getElementById('check-status-btn').addEventListener('click', checkMarketDataStatus);

// Load Kraken Pairs
let currentPairsOffset = 0;
const pairsLimit = 200; // Load 200 at a time
let searchTimeout = null;

async function loadKrakenPairs(reset = false) {
    const pairsList = document.getElementById('pairs-list');
    const searchInput = document.getElementById('pair-search');
    const loadBtn = document.getElementById('load-pairs-btn');
    const loadMoreBtn = document.getElementById('load-more-pairs-btn');
    
    if (reset) {
        currentPairsOffset = 0;
        pairsList.innerHTML = '';
    }
    
    loadBtn.disabled = true;
    loadBtn.innerHTML = '<span class="loading"></span> Loading...';
    if (reset) {
        pairsList.innerHTML = '<p class="info-text">Loading pairs...</p>';
    }
    
    try {
        const searchTerm = searchInput.value.trim();
        
        // Build URL with search parameter (server-side search through all pairs)
        let url = `${API_BASE.marketData}/kraken/pairs?limit=${pairsLimit}&offset=${currentPairsOffset}`;
        if (searchTerm) {
            url += `&search=${encodeURIComponent(searchTerm)}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            const pairs = data.pairs;
            
            if (pairs.length === 0 && currentPairsOffset === 0) {
                const searchMsg = searchTerm 
                    ? `No pairs found matching "${searchTerm}".` 
                    : 'No pairs found.';
                pairsList.innerHTML = `<p class="info-text">${searchMsg}</p>`;
            } else {
                // Use detailed pairs if available (with readable names), otherwise fallback to simple list
                const pairsToDisplay = data.pairs_detail || pairs.map(p => ({ pair: p, name: p }));
                
                const pairsHTML = pairsToDisplay.map(pairData => {
                    const pair = typeof pairData === 'string' ? pairData : pairData.pair;
                    const name = typeof pairData === 'string' ? pairData : (pairData.name || pairData.pair);
                    const base = typeof pairData === 'object' ? pairData.base : '';
                    const quote = typeof pairData === 'object' ? pairData.quote : '';
                    
                    // Display readable name prominently, with pair code as secondary info
                    return `
                        <div class="pair-item" onclick="selectPair('${pair}')" title="Pair: ${pair}${base ? ` | Base: ${base}` : ''}${quote ? ` | Quote: ${quote}` : ''}">
                            <span>
                                <strong style="font-size: 1rem;">${name}</strong>
                                <small style="color: #666; margin-left: 8px;">${pair}</small>
                            </span>
                            <button class="btn btn-primary" style="padding: 4px 8px; font-size: 0.875rem;" onclick="event.stopPropagation(); usePair('${pair}')">Use</button>
                        </div>
                    `;
                }).join('');
                
                if (reset) {
                    pairsList.innerHTML = pairsHTML;
                } else {
                    pairsList.innerHTML += pairsHTML;
                }
                
                // Update pagination info
                const totalShown = currentPairsOffset + data.pagination.returned;
                const cacheIndicator = data.from_cache ? ' (from cache)' : ' (from API)';
                const searchInfo = data.search ? ` | Searching: "${data.search}"` : '';
                const paginationInfo = `
                    <div style="margin-top: 12px; padding: 12px; background: var(--bg-color); border-radius: 8px;">
                        <p class="info-text" style="margin: 0;">
                            Showing ${totalShown} of ${data.pagination.total} ${data.search ? 'matching ' : ''}pairs 
                            (${data.active_pairs} active, ${data.total_pairs} total)${searchInfo}
                            <span style="color: ${data.from_cache ? 'var(--primary-color)' : 'var(--success-color)'}; font-size: 0.875rem;">
                                ${data.from_cache ? '💾' : '🌐'}${cacheIndicator}
                            </span>
                        </p>
                        ${data.pagination.has_more ? `
                            <button id="load-more-pairs-btn" class="btn btn-primary" style="margin-top: 8px; width: 100%;">
                                Load More (${data.pagination.total - totalShown} remaining)
                            </button>
                        ` : ''}
                    </div>
                `;
                
                // Remove old pagination info and add new
                const oldPagination = pairsList.querySelector('.pagination-info');
                if (oldPagination) oldPagination.remove();
                
                const paginationDiv = document.createElement('div');
                paginationDiv.className = 'pagination-info';
                paginationDiv.innerHTML = paginationInfo;
                pairsList.appendChild(paginationDiv);
                
                // Add event listener for load more button
                if (data.pagination.has_more) {
                    const newLoadMoreBtn = document.getElementById('load-more-pairs-btn');
                    if (newLoadMoreBtn) {
                        newLoadMoreBtn.addEventListener('click', () => {
                            currentPairsOffset += pairsLimit;
                            loadKrakenPairs(false);
                        });
                    }
                }
            }
        } else {
            pairsList.innerHTML = '<p class="info-text" style="color: var(--danger-color);">Failed to load pairs</p>';
        }
    } catch (error) {
        pairsList.innerHTML = `<p class="info-text" style="color: var(--danger-color);">Error: ${error.message}</p>`;
    } finally {
        loadBtn.disabled = false;
        loadBtn.textContent = 'Load Pairs';
    }
}

document.getElementById('load-pairs-btn').addEventListener('click', () => loadKrakenPairs(true));
document.getElementById('refresh-pairs-btn').addEventListener('click', refreshKrakenPairsCache);

// Search with debounce - searches through ALL pairs server-side
document.getElementById('pair-search').addEventListener('input', (e) => {
    // Clear existing timeout
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // Debounce search - wait 300ms after user stops typing
    searchTimeout = setTimeout(() => {
        currentPairsOffset = 0;
        loadKrakenPairs(true);
    }, 300);
});

// Also trigger search on Enter key
document.getElementById('pair-search').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        currentPairsOffset = 0;
        loadKrakenPairs(true);
    }
});

function selectPair(pair) {
    document.getElementById('kraken-pair-input').value = pair;
    document.getElementById('ohlc-pair').value = pair;
    document.getElementById('ticker-pair').value = pair;
}

function usePair(pair) {
    selectPair(pair);
    document.getElementById('kraken-pair-input').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Search for a specific pair
function searchPair(searchTerm) {
    const searchInput = document.getElementById('pair-search');
    searchInput.value = searchTerm;
    currentPairsOffset = 0;
    loadKrakenPairs(true);
}

// Refresh Kraken Pairs Cache
async function refreshKrakenPairsCache() {
    const refreshBtn = document.getElementById('refresh-pairs-btn');
    const pairsList = document.getElementById('pairs-list');
    
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '<span class="loading"></span> Refreshing...';
    pairsList.innerHTML = '<p class="info-text">Refreshing Kraken pairs cache...</p>';
    
    try {
        const response = await fetch(`${API_BASE.marketData}/kraken/pairs/refresh`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            pairsList.innerHTML = `
                <div class="result-message success" style="margin-bottom: 12px;">
                    ✅ Cache refreshed successfully!<br>
                    <small>Total pairs: ${data.total_pairs}, Active pairs: ${data.active_pairs}</small>
                </div>
            `;
            
            // Automatically reload pairs after refresh
            setTimeout(() => {
                currentPairsOffset = 0;
                loadKrakenPairs(true);
            }, 1000);
        } else {
            pairsList.innerHTML = '<p class="info-text" style="color: var(--danger-color);">Failed to refresh cache</p>';
        }
    } catch (error) {
        pairsList.innerHTML = `<p class="info-text" style="color: var(--danger-color);">Error: ${error.message}</p>`;
        console.error('Error refreshing Kraken pairs cache:', error);
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.textContent = '🔄 Refresh Cache';
    }
}

// Add Pair
async function addPair() {
    const krakenPair = document.getElementById('kraken-pair-input').value.trim();
    const dbSymbol = document.getElementById('db-symbol-input').value.trim();
    const resultEl = document.getElementById('add-pair-result');
    const addBtn = document.getElementById('add-pair-btn');
    
    if (!krakenPair) {
        showResult(resultEl, 'Please enter a Kraken pair name', 'error');
        return;
    }
    
    addBtn.disabled = true;
    addBtn.innerHTML = '<span class="loading"></span> Adding...';
    resultEl.className = 'result-message';
    
    try {
        let url = `${API_BASE.marketData}/kraken/add-pair?kraken_pair=${encodeURIComponent(krakenPair)}`;
        if (dbSymbol) {
            url += `&db_symbol=${encodeURIComponent(dbSymbol)}`;
        }
        
        const response = await fetch(url, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showResult(resultEl, `✅ ${data.message}`, 'success');
            document.getElementById('kraken-pair-input').value = '';
            document.getElementById('db-symbol-input').value = '';
        } else {
            showResult(resultEl, `❌ Error: ${data.message || 'Failed to add pair'}`, 'error');
        }
    } catch (error) {
        showResult(resultEl, `❌ Error: ${error.message}`, 'error');
    } finally {
        addBtn.disabled = false;
        addBtn.textContent = 'Add Pair';
    }
}

document.getElementById('add-pair-btn').addEventListener('click', addPair);

// Fetch OHLC Data
async function fetchOHLC() {
    const pair = document.getElementById('ohlc-pair').value.trim();
    const timeframe = document.getElementById('ohlc-timeframe').value;
    const limit = document.getElementById('ohlc-limit').value;
    const resultEl = document.getElementById('ohlc-result');
    const fetchBtn = document.getElementById('fetch-ohlc-btn');
    
    if (!pair) {
        showResult(resultEl, 'Please enter a pair name', 'error');
        return;
    }
    
    fetchBtn.disabled = true;
    fetchBtn.innerHTML = '<span class="loading"></span> Fetching...';
    resultEl.className = 'result-message';
    
    try {
        const url = `${API_BASE.marketData}/kraken/fetch-ohlc?pair=${encodeURIComponent(pair)}&timeframe=${timeframe}&limit=${limit}`;
        const response = await fetch(url, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showResult(resultEl, 
                `✅ ${data.message}<br>Records fetched: ${data.records_fetched}, Inserted: ${data.records_inserted}`, 
                'success'
            );
        } else {
            showResult(resultEl, `❌ Error: ${data.message || 'Failed to fetch data'}`, 'error');
        }
    } catch (error) {
        showResult(resultEl, `❌ Error: ${error.message}`, 'error');
    } finally {
        fetchBtn.disabled = false;
        fetchBtn.textContent = 'Fetch OHLC Data';
    }
}

document.getElementById('fetch-ohlc-btn').addEventListener('click', fetchOHLC);

// Fetch Ticker Data
async function fetchTicker() {
    const pair = document.getElementById('ticker-pair').value.trim();
    const resultEl = document.getElementById('ticker-result');
    const fetchBtn = document.getElementById('fetch-ticker-btn');
    
    if (!pair) {
        showResult(resultEl, 'Please enter a pair name', 'error');
        return;
    }
    
    fetchBtn.disabled = true;
    fetchBtn.innerHTML = '<span class="loading"></span> Fetching...';
    resultEl.className = 'result-message';
    
    try {
        const url = `${API_BASE.marketData}/kraken/fetch-ticker?pair=${encodeURIComponent(pair)}`;
        const response = await fetch(url, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showResult(resultEl, 
                `✅ ${data.message}<br>Price: $${data.price?.toLocaleString() || 'N/A'}`, 
                'success'
            );
        } else {
            showResult(resultEl, `❌ Error: ${data.message || 'Failed to fetch ticker'}`, 'error');
        }
    } catch (error) {
        showResult(resultEl, `❌ Error: ${error.message}`, 'error');
    } finally {
        fetchBtn.disabled = false;
        fetchBtn.textContent = 'Fetch Ticker';
    }
}

document.getElementById('fetch-ticker-btn').addEventListener('click', fetchTicker);

// View Market Data
async function viewMarketData() {
    const symbol = document.getElementById('view-symbol').value.trim();
    const timeframe = document.getElementById('view-timeframe').value;
    const limit = document.getElementById('view-limit').value;
    const tableContainer = document.getElementById('market-data-table');
    const viewBtn = document.getElementById('view-data-btn');
    
    if (!symbol) {
        tableContainer.innerHTML = '<p class="info-text" style="color: var(--danger-color);">Please enter a symbol</p>';
        return;
    }
    
    viewBtn.disabled = true;
    viewBtn.innerHTML = '<span class="loading"></span> Loading...';
    tableContainer.innerHTML = '<p class="info-text">Loading data...</p>';
    
    try {
        const url = `${API_BASE.marketData}/market-data/${encodeURIComponent(symbol)}?timeframe=${timeframe}&limit=${limit}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.data && data.data.length > 0) {
            let tableHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Open</th>
                            <th>High</th>
                            <th>Low</th>
                            <th>Close</th>
                            <th>Volume</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            data.data.forEach(item => {
                const timestamp = new Date(item.timestamp).toLocaleString();
                tableHTML += `
                    <tr>
                        <td>${timestamp}</td>
                        <td>$${item.open.toFixed(2)}</td>
                        <td>$${item.high.toFixed(2)}</td>
                        <td>$${item.low.toFixed(2)}</td>
                        <td>$${item.close.toFixed(2)}</td>
                        <td>${item.volume.toLocaleString()}</td>
                    </tr>
                `;
            });
            
            tableHTML += `
                    </tbody>
                </table>
                <p class="info-text" style="margin-top: 12px;">Showing ${data.count} records for ${data.symbol} (${data.timeframe})</p>
            `;
            
            tableContainer.innerHTML = tableHTML;
        } else {
            tableContainer.innerHTML = '<p class="info-text">No data found for this symbol and timeframe.</p>';
        }
    } catch (error) {
        tableContainer.innerHTML = `<p class="info-text" style="color: var(--danger-color);">Error: ${error.message}</p>`;
    } finally {
        viewBtn.disabled = false;
        viewBtn.textContent = 'View Data';
    }
}

document.getElementById('view-data-btn').addEventListener('click', viewMarketData);

// Sync Symbols
async function syncSymbols() {
    const resultEl = document.getElementById('sync-result');
    const syncBtn = document.getElementById('sync-symbols-btn');
    
    syncBtn.disabled = true;
    syncBtn.innerHTML = '<span class="loading"></span> Syncing...';
    resultEl.className = 'result-message';
    
    try {
        const response = await fetch(`${API_BASE.marketData}/kraken/sync-symbols`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showResult(resultEl, 
                `✅ ${data.message}<br>Created: ${data.created}, Updated: ${data.updated}, Total: ${data.total_pairs}`, 
                'success'
            );
        } else {
            showResult(resultEl, `❌ Error: ${data.message || 'Failed to sync symbols'}`, 'error');
        }
    } catch (error) {
        showResult(resultEl, `❌ Error: ${error.message}`, 'error');
    } finally {
        syncBtn.disabled = false;
        syncBtn.textContent = 'Sync All Symbols';
    }
}

document.getElementById('sync-symbols-btn').addEventListener('click', syncSymbols);

// Hello World Functions
async function checkHelloWorldStatus() {
    const resultEl = document.getElementById('hello-world-result');
    const checkBtn = document.getElementById('hello-world-status-btn');
    
    checkBtn.disabled = true;
    checkBtn.innerHTML = '<span class="loading"></span> Checking...';
    resultEl.className = 'result-message';
    
    try {
        const response = await fetch(`${API_BASE.helloWorld}/health`);
        const data = await response.json();
        
        showResult(resultEl, 
            `✅ Service: ${data.service}<br>Status: ${data.status}<br>Version: ${data.version}`, 
            'success'
        );
    } catch (error) {
        showResult(resultEl, `❌ Error: ${error.message}`, 'error');
    } finally {
        checkBtn.disabled = false;
        checkBtn.textContent = 'Check Service Status';
    }
}

document.getElementById('hello-world-status-btn').addEventListener('click', checkHelloWorldStatus);

// Utility Functions
function showResult(element, message, type) {
    element.innerHTML = message;
    element.className = `result-message ${type}`;
    element.style.display = 'block';
    
    // Auto-hide after 10 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 10000);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateApiConfigDisplay();
    checkMarketDataStatus();
});

