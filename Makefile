# Makefile for VideoDub development

.PHONY: help install test check clean build docs publish

# Default target
help:
	@echo "VideoDub Development Commands:"
	@echo "  install    - Install development dependencies"
	@echo "  test       - Run tests with coverage"
	@echo "  check      - Run all code quality checks"
	@echo "  format     - Format code with Black"
	@echo "  lint       - Run linting checks"
	@echo "  type-check - Run type checking"
	@echo "  clean      - Clean build artifacts"
	@echo "  build      - Build package distributions"
	@echo "  docs       - Build documentation"
	@echo "  publish    - Publish to PyPI (requires credentials)"

# Install development dependencies
install:
	pip install -e .[dev]

# Run tests
test:
	pytest --cov=videodub --cov-report=html --cov-report=term-missing

# Run all code quality checks
check: format lint type-check

# Format code
format:
	black src/ tests/
	isort src/ tests/

# Run linting
lint:
	flake8 src/ tests/
	bandit -r src/

# Run type checking
type-check:
	mypy src/

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage

# Build package
build: clean
	python -m build
	twine check dist/*

# Build documentation
docs:
	@echo "Building documentation..."
	@echo "Documentation available in docs/"

# Publish to PyPI
publish: build
	twine upload dist/*

# Security scanning
security:
	bandit -r src/
	safety check

# Generate SBOM
sbom:
	cyclonedx-py -i requirements.txt -o bom.xml --format xml

# Run all CI checks locally
ci: check test security sbom

# Development environment setup
dev-setup: install check test
	@echo "Development environment ready!"

# Pre-commit hook
pre-commit:
	$(MAKE) check
	$(MAKE) test