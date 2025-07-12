# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Complete integrated sleepwalker implementation**
  - Real filesystem exploration with safety patterns
  - Full CLI interface with `sleepwalker` and `ai-sleepwalker` commands
  - Console script entry points for global installation
- **Wake lock system**
  - Cross-platform sleep prevention using wakepy
  - Display sleep prevention (prevents screen lock during operation)
  - Graceful shutdown with signal handling
- **LLM integration for dream generation**
  - Support for Gemini and OpenAI APIs
  - Fallback content when API keys unavailable
  - Content-based prompts with surreal connections
- **Comprehensive testing**
  - End-to-end tests for complete workflows
  - Integration tests for wake lock functionality
  - Smoke tests for quick validation
- **Development tools and scripts**
  - Real filesystem exploration prototypes
  - Demo scripts for testing different scenarios
- Integration with uv for dependency management
- Modern Python development tools:
  - ruff for linting and formatting
  - mypy for type checking
  - pytest with coverage reporting
- GitHub Actions workflow for automated testing
- Docker development environment improvements

### Changed
- **Transformed from demo project to production CLI**
  - Main sleepwalker functionality moved from stubs to full implementation
  - CLI moved from basic interface to full feature set with confirmations
- Wake lock system upgraded from `keep.running()` to `keep.presenting()` for display sleep prevention
- README updated to clarify both system and display sleep prevention
- Switched from pip/venv to uv for environment management
- Updated example code to pass mypy type checking
- Modernized project structure and development workflow
- Updated Python version to 3.12

### Removed
- Legacy dependency management approach
- Outdated Docker configuration elements

### Fixed
- Display sleep prevention - screen no longer locks during sleepwalking sessions
- Type hints in example code to pass mypy checks
- Proper error handling for filesystem access and API failures
- Docker environment management
- Development workflow and quality checks

## [0.1.0] - 2024-04-14
- Initial fork from eugeneyan/python-collab-template
- Added Docker environment management
- Setup package installation configuration
