.PHONY: compile-deps setup clean-pyc clean-test clean-venv clean test mypy lint format check reload demo keep-awake sleepwalk sleepwalk-here clean-example docs-install docs-build docs-serve docs-check docs-clean dev-env refresh-containers rebuild-images build-image push-image

# Module name - will be updated by init script
MODULE_NAME := ai_sleepwalker

# Development Setup
#################
compile-deps:  # Compile dependencies from pyproject.toml
	uv pip compile pyproject.toml -o requirements.txt
	uv pip compile pyproject.toml --extra dev -o requirements-dev.txt

PYTHON_VERSION ?= 3.12

ensure-uv:  # Install uv if not present
	@which uv > /dev/null || (curl -LsSf https://astral.sh/uv/install.sh | sh)

setup: ensure-uv compile-deps  # Install dependencies
	UV_PYTHON_VERSION=$(PYTHON_VERSION) uv venv
	UV_PYTHON_VERSION=$(PYTHON_VERSION) uv pip sync requirements.txt requirements-dev.txt
	$(MAKE) install-hooks

install-hooks:  # Install pre-commit hooks if in a git repo with hooks configured
	@if [ -d .git ] && [ -f .pre-commit-config.yaml ]; then \
		echo "Installing pre-commit hooks..."; \
		uv run pre-commit install; \
	fi

# Removed ensure-scripts - using main CLI instead of separate scripts

# Cleaning
#########
clean-pyc:  # Remove Python compilation artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:  # Remove test and coverage artifacts
	rm -f .coverage
	rm -f .coverage.*

clean-venv:  # Remove virtual environment
	rm -rf .venv

clean: clean-pyc clean-test clean-venv

# Testing and Quality Checks
#########################
test: setup  # Run pytest with coverage
	uv run -m pytest tests --cov=$(MODULE_NAME) --cov-report=term-missing

mypy: setup  # Run type checking
	uv run -m mypy $(MODULE_NAME)

lint: setup  # Run ruff linter with auto-fix
	uv run -m ruff check --fix $(MODULE_NAME)

format: setup  # Run ruff formatter
	uv run -m ruff format $(MODULE_NAME)

check: setup lint format test mypy  # Run all quality checks

reload:  # Reload the package to pick up source changes
	@echo "🔄 Reloading package to pick up source changes..."
	uv pip install -e .
	@echo "✅ Package reloaded"

demo: setup  # Run quick demo in /tmp directory
	@echo "🌙 Starting AI Sleepwalker Demo"
	@echo "================================"
	@if [ -z "$$GEMINI_API_KEY" ] && [ -z "$$OPENAI_API_KEY" ]; then \
		echo "⚠️  No API keys found - demo will use fallback content"; \
		echo "   To use real LLM, set one of:"; \
		echo "   export GEMINI_API_KEY='your-key'"; \
		echo "   export OPENAI_API_KEY='your-key'"; \
		echo ""; \
	else \
		echo "🔑 API keys detected - will use real LLM for generation"; \
		echo ""; \
	fi
	@echo "Running brief demo in /tmp directory..."
	timeout 30 uv run -m ai_sleepwalker --dirs /tmp --no-confirm || echo "✅ Demo completed"

keep-awake: setup  # Keep computer awake with continuous sleepwalking
	@echo "🚀 Starting AI Sleepwalker in keep-awake mode..."
	@echo "   This will run indefinitely to prevent sleep"
	@echo "   Press Ctrl+C to stop"
	@echo ""
	@if [ -z "$$GEMINI_API_KEY" ] && [ -z "$$OPENAI_API_KEY" ]; then \
		echo "⚠️  Warning: No API keys found. Will use fallback dreams."; \
		echo "   Set GEMINI_API_KEY or OPENAI_API_KEY for AI-generated dreams."; \
		echo ""; \
	fi
	uv run -m ai_sleepwalker --dirs /tmp --no-confirm

sleepwalk: setup  # Run the AI sleepwalker (main command)
	@echo "🌙 Starting AI Sleepwalker - Digital Dream Explorer"
	@echo ""
	@if [ -z "$$GEMINI_API_KEY" ] && [ -z "$$OPENAI_API_KEY" ]; then \
		echo "⚠️  Warning: No API keys found. Will use fallback dreams."; \
		echo "   Set GEMINI_API_KEY or OPENAI_API_KEY for AI-generated dreams."; \
		echo ""; \
	fi
	@if [ -n "$(DIR)" ]; then \
		uv run -m ai_sleepwalker --dirs "$(DIR)"; \
	else \
		uv run -m ai_sleepwalker; \
	fi

sleepwalk-here: setup  # Sleepwalk in current directory without confirmation  
	@echo "🌙 Sleepwalking in current directory..."
	uv run -m ai_sleepwalker --dirs . --no-confirm

# sleepwalk-script target removed - use 'make sleepwalk' instead

# Documentation
###############
DOCS_PORT ?= 8000

docs-install: setup  ## Install documentation dependencies
	@echo "Installing documentation dependencies..."
	uv sync --group dev
	@echo "Documentation dependencies installed"

docs-build: docs-install  ## Build documentation site
	@echo "Building documentation..."
	uv run mkdocs build --strict
	@echo "Documentation built successfully"
	@echo "📄 Site location: site/"
	@echo "🌐 Open site/index.html in your browser to view"

docs-serve: docs-install  ## Serve documentation locally with live reload
	@echo "Starting documentation server with live reload..."
	@echo "📍 Documentation will be available at:"
	@echo "   - Local: http://localhost:$(DOCS_PORT)"
	@echo "🔄 Changes will auto-reload (press Ctrl+C to stop)"
	@echo ""
	@echo "💡 To use a different port: make docs-serve DOCS_PORT=9999"
	uv run mkdocs serve --dev-addr 0.0.0.0:$(DOCS_PORT)

docs-check: docs-build  ## Check documentation build and links
	@echo "Checking documentation..."
	@echo "📊 Site size: $$(du -sh site/ | cut -f1)"
	@echo "📄 Pages built: $$(find site/ -name "*.html" | wc -l)"
	@echo "🔗 Checking for common issues..."
	@if grep -r "404" site/ >/dev/null 2>&1; then \
		echo "⚠️  Found potential 404 errors"; \
	else \
		echo "✅ No obvious 404 errors found"; \
	fi
	@if find site/ -name "*.html" -size 0 | grep -q .; then \
		echo "⚠️  Found empty HTML files"; \
		find site/ -name "*.html" -size 0; \
	else \
		echo "✅ No empty HTML files found"; \
	fi
	@echo "Documentation check complete"

docs-clean:  ## Clean documentation build files
	@echo "Cleaning documentation build files..."
	rm -rf site/
	rm -rf .cache/
	@echo "Documentation cleaned"

# Project Management
##################
clean-example:  # Remove example code (use this to start your own project)
	rm -rf $(MODULE_NAME)/example.py tests/test_example.py
	touch $(MODULE_NAME)/__init__.py tests/__init__.py

# init target removed - project is already initialized

# Docker
########
IMAGE_NAME = container-registry.io/python-collab-template
IMAGE_TAG = latest

dev-env: refresh-containers
	@echo "Spinning up a dev environment ."
	@docker compose -f docker/docker-compose.yml down
	@docker compose -f docker/docker-compose.yml up -d dev
	@docker exec -ti composed_dev /bin/bash

refresh-containers:
	@echo "Rebuilding containers..."
	@docker compose -f docker/docker-compose.yml build

rebuild-images:
	@echo "Rebuilding images with the --no-cache flag..."
	@docker compose -f docker/docker-compose.yml build --no-cache

build-image:
	@echo Building dev image and tagging as ${IMAGE_NAME}:${IMAGE_TAG}
	@docker compose -f docker/docker-compose.yml down
	@docker compose -f docker/docker-compose.yml up -d dev
	@docker tag dev ${IMAGE_NAME}:${IMAGE_TAG}

push-image: build-image
	@echo Pushing image to container registry
	@docker push ${IMAGE_NAME}:${IMAGE_TAG}
