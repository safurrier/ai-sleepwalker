# ai-sleepwalker

Don't let your computer go to sleep, let AI sleepwalk through it

## Features

- 🔧 Modern Python tooling with UV package manager
- 🧪 Comprehensive testing with pytest
- 🎨 Code formatting with Ruff
- 🔍 Type checking with MyPy
- 📚 Documentation with MkDocs + Material
- 🚀 CI/CD with GitHub Actions
- 🐳 Docker support for development

## Quick Start

```bash
# Clone the repository
git clone https://github.com/safurrier/ai-sleepwalker.git
cd ai-sleepwalker

# Set up the development environment
make setup

# Run quality checks
make check
```

## Installation

### For Users

```bash
pip install ai-sleepwalker
```

### For Development

```bash
# Clone the repository
git clone https://github.com/safurrier/ai-sleepwalker.git
cd ai-sleepwalker

# Set up development environment
make setup

# Install pre-commit hooks (optional)
make install-hooks
```

## Project Structure

```
ai-sleepwalker/
├── ai_sleepwalker/      # Main package
├── tests/                      # Test files
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── docker/                     # Docker configuration
└── .github/workflows/          # CI/CD automation
```

## Usage

```python
import ai_sleepwalker

# Your usage examples here
```

## Development

See the [Getting Started](getting-started.md) guide for detailed development instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite: `make check`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.