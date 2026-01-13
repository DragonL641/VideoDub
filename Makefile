.PHONY: install update test lint format check clean help

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_0-9%-]+:.*?## .*$$' $(word 1,$(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-30s %s\n", $$1, $$2}'

install: ## Install the package and dependencies
	pip install -r requirements.txt
	pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

update: ## Update dependencies
	pip install --upgrade -r requirements.txt

test: ## Run tests
	python -m pytest videodub/tests/

clean: ## Clean temporary files
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf */*/__pycache__
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info