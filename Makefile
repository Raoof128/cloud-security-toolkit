.PHONY: help install install-dev test test-cov lint format type-check security clean docs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install black flake8 mypy bandit pytest pytest-cov moto

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

lint: ## Run linting checks
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

format: ## Format code with black
	black --line-length 100 .

format-check: ## Check code formatting without changing files
	black --check --line-length 100 .

type-check: ## Run type checking with mypy
	mypy scanners/ utils/ remediation/ --ignore-missing-imports

security: ## Run security checks
	bandit -r scanners/ utils/ remediation/ -ll
	@echo "Checking dependencies for known vulnerabilities..."
	pip freeze | safety check --stdin || true

clean: ## Clean up generated files
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type f -name '.coverage' -delete
	find . -type f -name 'coverage.xml' -delete
	rm -rf build/ dist/

demo: ## Run demo mode
	python cloud_security_audit.py --demo --output demo_report.html
	@echo "Demo report generated: demo_report.html"

verify: ## Verify installation
	python verify_installation.py

scan-aws: ## Run AWS scan (requires AWS credentials)
	python cloud_security_audit.py --provider aws --output aws_report.html

scan-dry-run: ## Run AWS scan with remediation in dry-run mode
	python cloud_security_audit.py --provider aws --remediate --dry-run

all-checks: format-check lint type-check test security ## Run all quality checks

ci: install-dev all-checks ## Run CI pipeline locally

docs: ## Generate documentation (if sphinx is installed)
	@echo "Documentation generation not yet implemented"
	@echo "See README.md, CONTRIBUTING.md, and docs/ directory"

version: ## Show version information
	@echo "Cloud Security Toolkit v2.0.0"
	@python --version
	@pip show boto3 | grep Version || echo "boto3 not installed"

pre-commit: format-check lint type-check test ## Run pre-commit checks
	@echo "✅ All pre-commit checks passed!"

setup-dev: install-dev ## Setup development environment
	@echo "Setting up development environment..."
	@echo "Installing pre-commit hooks (if available)..."
	pre-commit install || echo "pre-commit not installed, skipping hook installation"
	@echo "✅ Development environment ready!"

.DEFAULT_GOAL := help
