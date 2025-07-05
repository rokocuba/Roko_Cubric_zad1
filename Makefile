.PHONY: help run dev test test-unit test-integration lint format docker-build docker-run docker-compose clean

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
ISORT := isort
FLAKE8 := flake8

# Default target
help:
	@echo "Available commands:"
	@echo "  run              - Run the application"
	@echo "  dev              - Run in development mode with auto-reload"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  lint             - Run linting (flake8)"
	@echo "  format           - Format code (black, isort)"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-run       - Run Docker container"
	@echo "  docker-compose   - Run with docker-compose"
	@echo "  clean            - Clean up cache files"

# Application commands
run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Testing
test:
	$(PYTEST) tests/ -v --cov=src --cov-report=html --cov-report=term

test-unit:
	$(PYTEST) tests/unit/ -v

test-integration:
	$(PYTEST) tests/integration/ -v

# Code quality
lint:
	$(FLAKE8) src/ tests/
	mypy src/

format:
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

# Docker
docker-build:
	docker build -t tickethub .

docker-run:
	docker run -p 8000:8000 --env-file .env tickethub

docker-compose:
	docker-compose up --build

# Utilities
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

# Setup
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
