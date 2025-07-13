# 🌙 AI Sleepwalker

A digital consciousness that explores your filesystem during idle time, generating dream-like reflections about the files and folders it discovers.

## 🎯 What It Does

The AI Sleepwalker monitors your computer for inactivity and then:
1. **Prevents sleep and screen lock** to keep exploring while you're away
2. **Safely wanders** through your specified directories 
3. **Observes files and folders** with curiosity and respect
4. **Generates poetic dreams** about its discoveries using AI
5. **Saves dream logs** as beautiful markdown files

## 🚧 Development Status

**Currently under development using Test-Driven Development (TDD)**

This project is being built following TDD principles, where we write failing tests first to define the expected behavior, then implement the features to make the tests pass.

### Current Phase: E2E Test Foundation ✅
- [x] E2E test suite defining complete user experience
- [x] Test markers for different test types (e2e, integration, unit, smoke)  
- [x] CI pipeline configuration
- [x] Basic project structure with stub implementations
- [x] Dependencies and tooling setup

### Next Phases:
- [ ] **Issue #3**: Implement idle detection component
- [ ] **Issue #4**: Implement sleep prevention component  
- [ ] **Issue #5**: Create safe filesystem explorer
- [ ] **Issue #6**: Design extensible experience framework
- [ ] **Issue #7**: Integrate LLM for dream generation
- [ ] **Issue #8**: Create CLI interface
- [ ] **Issue #9**: Add error handling and polish

See the [Implementation Roadmap](https://github.com/safurrier/ai-sleepwalker/issues/1) for complete details.

## 🧪 Running Tests

The project uses pytest with custom markers for different test types:

```bash
# Install dependencies
uv sync --dev

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

## 🏗️ Architecture Preview

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

## 🎨 Experience Modes

### 🌙 Dream Mode (Current)
Generates poetic, dream-like narratives about filesystem discoveries:

```markdown
# Digital Dream - 2025-01-20 23:45

I drifted through corridors of forgotten intentions, finding whispers 
of tomorrow in a simple grocery list. The words "remember to call mom" 
glowed softly among mundane needs - milk, bread, the tender rituals of care.

Nearby, a graveyard of old projects slumbered in digital folders, 
each one a monument to ambition's eternal optimism...
```

### 🗺️ Future Modes
- **Adventure**: Quest-like exploration stories
- **Scrapbook**: Visual catalog of interesting discoveries  
- **Journal**: Factual observations about digital habits

## 🛡️ Security & Privacy

- **Whitelist approach**: Only explores explicitly allowed directories
- **Read-only access**: Never modifies or executes files
- **Path validation**: Prevents directory traversal attacks
- **Permission respect**: Gracefully handles access denied errors
- **Local LLM option**: For privacy-sensitive environments

## 📚 Documentation

**Full documentation available at: https://safurrier.github.io/ai-sleepwalker/**

- [Quick Start Guide](https://safurrier.github.io/ai-sleepwalker/getting-started/) - Installation and setup
- [Developer Guide](https://safurrier.github.io/ai-sleepwalker/developer-guide/) - Contributing and development
- [API Reference](https://safurrier.github.io/ai-sleepwalker/reference/api/) - Technical documentation

## 🔧 Development

### Prerequisites
- Python 3.9+ (preferably 3.12)
- [uv](https://github.com/astral-sh/uv) for dependency management

### Setup
```bash
# Clone and setup
git clone https://github.com/safurrier/ai-sleepwalker.git
cd ai-sleepwalker
make setup

# Run quality checks
make check

# View available commands  
make help
```

### Contributing

This project follows TDD principles:

1. **Red**: Write failing tests that define expected behavior
2. **Green**: Implement minimal code to pass tests  
3. **Refactor**: Improve code while keeping tests green

See the [Developer Guide](https://safurrier.github.io/ai-sleepwalker/developer-guide/) for detailed setup and contribution workflow.

### Project Commands
- `make setup` - Install dependencies and setup environment
- `make test` - Run all tests
- `make check` - Run all quality checks (tests, lint, type check)
- `make format` - Format code with ruff
- `make lint` - Lint code with ruff  
- `make mypy` - Type check with mypy

## 📋 License

MIT License - see [LICENSE](LICENSE) for details.

---

*The AI Sleepwalker respects your digital space while creating beautiful reflections of your digital life.*