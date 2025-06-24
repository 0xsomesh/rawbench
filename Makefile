.PHONY: help install install-dev test test-unit test-integration lint format clean build docs

help: ## Show this help message
	@echo "RawBench Prompt Eval Framework"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean ## Build the package
	python -m build

docs: ## Generate documentation
	@echo "Documentation generation not implemented yet"

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

setup-pre-commit: ## Setup pre-commit hooks
	pre-commit install

check-all: format-check lint test ## Run all checks (format, lint, test)
	@echo "All checks passed! ✅" 