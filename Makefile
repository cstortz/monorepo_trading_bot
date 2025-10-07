# Trading Bot Monorepo Makefile

.PHONY: help setup dev test clean build deploy

help: ## Show this help message
	@echo "Trading Bot Monorepo Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Set up the development environment
	@echo "🚀 Setting up Trading Bot Monorepo..."
	@./scripts/setup.sh

dev: ## Start development environment
	@echo "🔧 Starting development environment..."
	@./scripts/dev.sh

test: ## Run tests
	@echo "🧪 Running tests..."
	@./scripts/test.sh

clean: ## Clean up containers and volumes
	@echo "🧹 Cleaning up..."
	docker compose down -v
	docker system prune -f

build: ## Build all services
	@echo "🔨 Building services..."
	docker compose build

deploy: ## Deploy to Kubernetes
	@echo "🚀 Deploying to Kubernetes..."
	kubectl apply -f k8s/

logs: ## View logs
	@echo "📋 Viewing logs..."
	docker compose logs -f

status: ## Check service status
	@echo "📊 Checking service status..."
	@echo "Docker services:"
	@docker compose ps
	@echo ""
	@echo "Kubernetes services:"
	@kubectl get pods -n trading-bot 2>/dev/null || echo "Kubernetes not configured"
