# Developer Guide

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management

## Development Setup

```bash
# Clone and setup
git clone https://github.com/safurrier/ai-sleepwalker.git
cd ai-sleepwalker
make setup

# Run tests
make test

# Start development server
uv run python -m ai_sleepwalker.cli ~/Documents
```

## Available Commands

- `make setup` - Install dependencies and setup environment
- `make test` - Run test suite with coverage
- `make check` - Run all quality checks (tests, lint, type check)
- `make format` - Format code with ruff
- `make lint` - Lint code with ruff
- `make mypy` - Type check with mypy
- `make docs-serve` - Serve documentation locally
- `make docs-build` - Build documentation

## Testing

The project uses pytest with custom markers for different test types:

```bash
# Run all tests
make test

# Run specific test types
uv run pytest -m "e2e"          # End-to-end tests
uv run pytest -m "integration"  # Integration tests  
uv run pytest -m "unit"         # Unit tests
uv run pytest -m "smoke"        # Smoke tests

# Run with coverage
uv run pytest --cov=ai_sleepwalker --cov-report=html
```

### Test Categories

- **E2E Tests**: Complete user workflows from CLI to dream log creation
- **Integration Tests**: Component interactions with real dependencies
- **Unit Tests**: Individual component behavior
- **Smoke Tests**: Basic functionality verification

## TDD Workflow

This project follows test-driven development:

1. **Red**: Write failing tests that define expected behavior
2. **Green**: Implement minimal code to pass tests  
3. **Refactor**: Improve code while keeping tests green

See existing tests in `tests/` for patterns and examples.

## Architecture

The sleepwalker is designed with an extensible experience framework:

```
ai_sleepwalker/
├── core/                   # Core components
│   ├── idle_detector.py   # User activity monitoring
│   ├── sleep_preventer.py # Cross-platform sleep prevention  
│   └── filesystem_explorer.py # Safe directory wandering
├── experiences/            # Experience modes
│   ├── base.py            # Abstract framework
│   ├── dream.py           # Dream mode (poetic reflections)
│   ├── adventure.py       # Adventure mode (coming soon)
│   └── scrapbook.py       # Scrapbook mode (coming soon)
├── cli.py                 # Command-line interface
└── main.py                # Main orchestrator
```

## Contributing

### Code Style

- Python 3.10+ with strict type hints
- Follow project's ruff configuration
- All functions should have docstrings
- Use dataclasses for structured data

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Write tests first (TDD approach)
4. Implement your changes
5. Run all quality checks: `make check`
6. Update documentation if needed
7. Submit a pull request

### Pre-commit Hooks

The project uses pre-commit hooks for quality assurance:

- **Type checking** with mypy
- **Linting** with ruff
- **Formatting** with ruff
- **Testing** - all tests must pass

Never bypass pre-commit hooks with `--no-verify` unless absolutely necessary.

### API Keys for Development

Set up at least one API key for testing:

```bash
# Recommended for development (free tier)
export GEMINI_API_KEY="your-key"

# Or use other providers
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

For CI/CD, the project skips tests requiring API keys automatically.

## Documentation

### Building Docs

```bash
# Serve locally with live reload
make docs-serve

# Build static site
make docs-build
```

Documentation is auto-deployed to GitHub Pages when changes are pushed to main.

### Writing Documentation

- Follow the [writing conventions](https://github.com/safurrier/ai-sleepwalker/docs) 
- Avoid LLM buzzwords and academic language
- Focus on practical examples and user needs
- Test all code examples before committing

## Release Process

1. Update version in `pyproject.toml`
2. Update changelog
3. Create release PR
4. Merge to main
5. Tag release
6. GitHub Actions will handle publishing

## Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Contributing**: See this guide and existing code patterns