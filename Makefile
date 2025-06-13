# Makefile for Voice Assistant project

.PHONY: test test-unit test-coverage clean install-test-deps

# Run all tests
test:
	@echo "🧪 Running all tests..."
	pytest

# Run only unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	pytest -m unit

# Run tests with coverage report
test-coverage:
	@echo "📊 Running tests with coverage..."
	pytest --cov=src --cov-report=html --cov-report=term-missing

# Install test dependencies
install-test-deps:
	@echo "📦 Installing test dependencies..."
	pip install -r requirements-test.txt

# Clean test artifacts
clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +