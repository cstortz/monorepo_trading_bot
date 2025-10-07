# Trading Bot Monorepo

A comprehensive trading bot monorepo built with FastAPI, Docker, and Kubernetes.

## Architecture

- **Services**: FastAPI-based microservices
- **Development**: Docker Compose for local development
- **Production**: Kubernetes deployment
- **Logging**: Structured logging with dev/prod configurations

## Services

- `hello-world`: Initial service for testing
- `market-data`: Market data collection and processing
- `strategy-engine`: Trading strategy execution
- `risk-management`: Risk assessment and position sizing
- `order-management`: Order execution and tracking
- `portfolio-manager`: Portfolio monitoring and rebalancing

## Quick Start

### Development
```bash
# Start all services
make dev

# Or manually:
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Available Commands
```bash
make help          # Show all available commands
make setup         # Set up development environment
make dev           # Start development environment
make test          # Run tests
make clean         # Clean up containers and volumes
make build         # Build all services
make deploy        # Deploy to Kubernetes
make logs          # View logs
make status        # Check service status
```

### Production
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check status
kubectl get pods
```

## Current Status

✅ **Hello World Service** - Running and tested
- **URL**: http://localhost:8003
- **Endpoints**: 
  - `GET /` - Hello world message
  - `GET /health` - Health check
  - `GET /info` - Service information
  - `GET /logs/test` - Test logging functionality
- **Logging**: Development format with file, function, and line numbers
- **Status**: Fully functional

## Development

Each service is independently deployable and follows the same structure:
- `app/`: FastAPI application code
- `tests/`: Unit and integration tests
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container configuration

### Logging Configuration

The monorepo includes a sophisticated logging system:

**Development Logging** (current):
```
2025-10-07 20:52:51 | INFO | hello-world | main.py:test_logging:96 | This is an INFO message
```

**Production Logging** (JSON format):
```json
{
  "timestamp": "2025-10-07T20:52:51",
  "level": "INFO",
  "service": "hello-world",
  "message": "This is an INFO message",
  "module": "main",
  "function": "test_logging",
  "line": 96
}
```