# =============================================================================
# Makefile - Common Development Tasks
# =============================================================================
# Usage: make <target>
# Run 'make help' to see all available targets

.PHONY: help install dev test lint format typecheck clean build run docker docs

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
RUFF := $(VENV)/bin/ruff
PYRIGHT := $(VENV)/bin/pyright

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m  # No color

# =============================================================================
# HELP
# =============================================================================
help: ## Show this help message
	@echo "$(BLUE)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# SETUP
# =============================================================================
venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Virtual environment created at $(VENV)$(NC)"
	@echo "Activate with: source $(VENV)/bin/activate"

install: venv ## Install production dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	@echo "$(GREEN)Dependencies installed$(NC)"

dev: venv ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(VENV)/bin/pre-commit install || true
	@echo "$(GREEN)Development dependencies installed$(NC)"

update: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[dev]"
	@echo "$(GREEN)Dependencies updated$(NC)"

# =============================================================================
# QUALITY
# =============================================================================
lint: ## Run linter (ruff)
	@echo "$(BLUE)Running linter...$(NC)"
	$(RUFF) check .

lint-fix: ## Run linter with auto-fix
	@echo "$(BLUE)Running linter with auto-fix...$(NC)"
	$(RUFF) check --fix .
	@echo "$(GREEN)Linting complete$(NC)"

format: ## Format code (ruff)
	@echo "$(BLUE)Formatting code...$(NC)"
	$(RUFF) format .
	@echo "$(GREEN)Formatting complete$(NC)"

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code format...$(NC)"
	$(RUFF) format --check .

typecheck: ## Run type checker (pyright)
	@echo "$(BLUE)Running type checker...$(NC)"
	$(PYRIGHT)

check: lint-fix format typecheck ## Run all checks (lint, format, typecheck)
	@echo "$(GREEN)All checks passed$(NC)"

# =============================================================================
# TESTING
# =============================================================================
test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTEST)

test-v: ## Run tests with verbose output
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	$(PYTEST) -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) --cov --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report: htmlcov/index.html$(NC)"

test-fast: ## Run tests, stop on first failure
	@echo "$(BLUE)Running tests (stop on first failure)...$(NC)"
	$(PYTEST) -x

test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(VENV)/bin/ptw

# =============================================================================
# BUILD & RUN
# =============================================================================
build: clean ## Build the package
	@echo "$(BLUE)Building package...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)Build complete$(NC)"

run: ## Run the application
	@echo "$(BLUE)Starting application...$(NC)"
	$(VENV)/bin/python -m your_app

run-dev: ## Run the application in development mode
	@echo "$(BLUE)Starting application (dev mode)...$(NC)"
	$(VENV)/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000

# =============================================================================
# DOCKER
# =============================================================================
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t myapp:latest .

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -p 8000:8000 --env-file .env myapp:latest

docker-up: ## Start docker-compose services
	@echo "$(BLUE)Starting services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Services started$(NC)"

docker-down: ## Stop docker-compose services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker compose down

docker-logs: ## Follow docker-compose logs
	docker compose logs -f

docker-shell: ## Shell into app container
	docker compose exec app /bin/sh

docker-clean: ## Remove all containers, images, volumes
	@echo "$(RED)Removing all Docker resources...$(NC)"
	docker compose down -v --rmi all
	docker system prune -af

# =============================================================================
# DATABASE
# =============================================================================
db-migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	$(VENV)/bin/alembic upgrade head

db-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back migration...$(NC)"
	$(VENV)/bin/alembic downgrade -1

db-reset: ## Reset database (drop and recreate)
	@echo "$(RED)Resetting database...$(NC)"
	$(VENV)/bin/alembic downgrade base
	$(VENV)/bin/alembic upgrade head

# =============================================================================
# DOCUMENTATION
# =============================================================================
docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd docs && make html
	@echo "$(GREEN)Docs available at docs/_build/html/index.html$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	cd docs/_build/html && $(PYTHON) -m http.server 8080

# =============================================================================
# CLEANUP
# =============================================================================
clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)Clean complete$(NC)"

clean-all: clean ## Clean everything including venv
	@echo "$(RED)Removing virtual environment...$(NC)"
	rm -rf $(VENV)
	@echo "$(GREEN)Full clean complete$(NC)"

# =============================================================================
# UTILITIES
# =============================================================================
repl: ## Start Python REPL with project imported
	@echo "$(BLUE)Starting REPL...$(NC)"
	$(VENV)/bin/python

shell: ## Start IPython shell (if installed)
	@echo "$(BLUE)Starting IPython shell...$(NC)"
	$(VENV)/bin/ipython

outdated: ## Show outdated packages
	$(PIP) list --outdated

tree: ## Show project structure
	tree -I '__pycache__|*.pyc|.git|.venv|node_modules|htmlcov|*.egg-info' -L 3

loc: ## Count lines of code
	@echo "$(BLUE)Lines of code:$(NC)"
	find . -name "*.py" -not -path "./.venv/*" | xargs wc -l | tail -1

todo: ## Find TODO comments in code
	@echo "$(BLUE)TODO comments:$(NC)"
	grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.py" . || echo "No TODOs found"

secrets-check: ## Check for secrets in code
	@echo "$(BLUE)Checking for secrets...$(NC)"
	$(VENV)/bin/detect-secrets scan . || echo "Install detect-secrets: pip install detect-secrets"

# =============================================================================
# CI/CD
# =============================================================================
ci: check test ## Run CI pipeline locally
	@echo "$(GREEN)CI pipeline passed$(NC)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	$(VENV)/bin/pre-commit run --all-files

release-patch: ## Bump patch version and tag
	@echo "$(BLUE)Creating patch release...$(NC)"
	$(VENV)/bin/bump2version patch
	git push --tags

release-minor: ## Bump minor version and tag
	@echo "$(BLUE)Creating minor release...$(NC)"
	$(VENV)/bin/bump2version minor
	git push --tags

release-major: ## Bump major version and tag
	@echo "$(BLUE)Creating major release...$(NC)"
	$(VENV)/bin/bump2version major
	git push --tags
