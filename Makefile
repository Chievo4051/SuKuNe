# Makefile untuk SeKuNe Docker Management

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

# Help target
help: ## Tampilkan bantuan penggunaan
	@echo "$(BLUE)SeKuNe Docker Management$(NC)"
	@echo "=========================="
	@echo ""
	@echo "$(GREEN)Production Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(build|up|down|logs|clean)"
	@echo ""
	@echo "$(GREEN)Development Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(dev|test)"
	@echo ""
	@echo "$(GREEN)Utility Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -v -E "(build|up|down|logs|clean|dev|test)"

# Production Commands
build: ## Build semua Docker images untuk production
	@echo "$(GREEN)Building production images...$(NC)"
	docker-compose build --no-cache

up: ## Jalankan aplikasi production
	@echo "$(GREEN)Starting production services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started! Access:$(NC)"
	@echo "  Frontend: $(BLUE)http://localhost$(NC)"
	@echo "  Backend API: $(BLUE)http://localhost:5000$(NC)"

down: ## Stop aplikasi production
	@echo "$(YELLOW)Stopping production services...$(NC)"
	docker-compose down

restart: ## Restart aplikasi production
	@echo "$(YELLOW)Restarting production services...$(NC)"
	docker-compose restart

logs: ## Lihat logs aplikasi production
	docker-compose logs -f

logs-backend: ## Lihat logs backend saja
	docker-compose logs -f backend

logs-frontend: ## Lihat logs frontend saja
	docker-compose logs -f frontend

# Development Commands
dev-build: ## Build Docker images untuk development
	@echo "$(GREEN)Building development images...$(NC)"
	docker-compose -f docker-compose.dev.yml build --no-cache

dev-up: ## Jalankan aplikasi development dengan hot reload
	@echo "$(GREEN)Starting development services...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)Development services started! Access:$(NC)"
	@echo "  Frontend: $(BLUE)http://localhost:5173$(NC)"
	@echo "  Backend API: $(BLUE)http://localhost:5000$(NC)"

dev-down: ## Stop aplikasi development
	@echo "$(YELLOW)Stopping development services...$(NC)"
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## Lihat logs aplikasi development
	docker-compose -f docker-compose.dev.yml logs -f

dev-shell-backend: ## Masuk ke shell backend development
	docker-compose -f docker-compose.dev.yml exec backend-dev sh

dev-shell-frontend: ## Masuk ke shell frontend development
	docker-compose -f docker-compose.dev.yml exec frontend-dev sh

# Testing Commands
test-backend: ## Jalankan test backend
	docker-compose -f docker-compose.dev.yml exec backend-dev python -m pytest

test-frontend: ## Jalankan test frontend
	docker-compose -f docker-compose.dev.yml exec frontend-dev npm test

# Utility Commands
status: ## Lihat status semua container
	@echo "$(BLUE)Container Status:$(NC)"
	docker-compose ps

clean: ## Bersihkan semua container, images, dan volumes
	@echo "$(RED)Cleaning up Docker resources...$(NC)"
	docker-compose down -v --remove-orphans
	docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-volumes: ## Hapus semua volumes (HATI-HATI: Data akan hilang!)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		docker-compose down -v; \
		docker volume prune -f; \
		echo "$(GREEN)Volumes cleaned!$(NC)"; \
	else \
		echo ""; \
		echo "$(YELLOW)Cancelled.$(NC)"; \
	fi

backup-db: ## Backup database
	@echo "$(GREEN)Creating database backup...$(NC)"
	docker-compose exec backend cp /app/sekune.db /app/data/sekune_backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "$(GREEN)Backup created in backend_data volume$(NC)"

shell-backend: ## Masuk ke shell backend production
	docker-compose exec backend sh

shell-frontend: ## Masuk ke shell frontend production
	docker-compose exec frontend sh

shell-db: ## Masuk ke shell database
	docker-compose exec database psql -U sekune_user -d sekune_db

update: ## Update dan rebuild aplikasi
	@echo "$(GREEN)Updating application...$(NC)"
	git pull
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d
	@echo "$(GREEN)Update completed!$(NC)"

install: ## Install aplikasi pertama kali
	@echo "$(GREEN)Installing SeKuNe...$(NC)"
	@echo "1. Building images..."
	make build
	@echo "2. Starting services..."
	make up
	@echo "3. Waiting for services to be ready..."
	sleep 30
	@echo "$(GREEN)Installation completed!$(NC)"
	@echo ""
	@echo "$(BLUE)Access your application:$(NC)"
	@echo "  Frontend: $(BLUE)http://localhost$(NC)"
	@echo "  Backend API: $(BLUE)http://localhost:5000$(NC)"
	@echo ""
	@echo "$(YELLOW)Default admin credentials:$(NC)"
	@echo "  Email: admin@sekune.com"
	@echo "  Password: admin123"

# Monitoring Commands
monitor: ## Monitor resource usage
	@echo "$(BLUE)Resource Usage:$(NC)"
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

health: ## Check health status semua services
	@echo "$(BLUE)Health Status:$(NC)"
	@docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Security Commands
security-scan: ## Scan keamanan images
	@echo "$(BLUE)Scanning images for vulnerabilities...$(NC)"
	@if command -v trivy >/dev/null 2>&1; then \
		trivy image sekune_backend:latest; \
		trivy image sekune_frontend:latest; \
	else \
		echo "$(YELLOW)Trivy not installed. Install with: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin$(NC)"; \
	fi

.PHONY: help build up down restart logs logs-backend logs-frontend dev-build dev-up dev-down dev-logs dev-shell-backend dev-shell-frontend test-backend test-frontend status clean clean-volumes backup-db shell-backend shell-frontend shell-db update install monitor health security-scan

