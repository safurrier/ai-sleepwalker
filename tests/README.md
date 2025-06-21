# Sleepwalker Test Suite

This test suite follows the progressive testing approach and anti-pattern avoidance guidelines from the testing domain documentation.

## 🧪 Test Organization

### Directory Structure
```
tests/
├── conftest.py              # Minimal shared fixtures only
├── smoke/                   # High-level system validation
├── integration/             # Component interaction tests  
├── unit/                    # Individual component tests
└── fixtures/                # Test doubles and test data
    ├── test_doubles.py      # Fakes, stubs (NO mocks)
    └── test_data.py         # Sample data
```

### Test Categories

#### 🔥 Smoke Tests (`tests/smoke/`)
- **Purpose**: Validate critical user journeys (20% of features used 80% of the time)
- **Scope**: High-level system health and core workflows
- **Speed**: Fast and reliable
- **Dependencies**: Uses test doubles for external services

#### 🔗 Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and boundaries
- **Scope**: How modules work together, data flow validation
- **Dependencies**: Real components when possible, fakes for external services

#### ⚙️ Unit Tests (`tests/unit/`)
- **Purpose**: Test individual component contracts and logic
- **Scope**: Single component behavior in isolation
- **Dependencies**: Minimal, focused on component interface

## 🚫 Anti-Patterns Avoided

Based on testing domain guidance, this test suite **avoids**:

1. **❌ Excessive Mocking/Patching** (Major Code Smell)
   - Instead: Uses test doubles (fakes, stubs) from `fixtures/test_doubles.py`
   - Focuses on dependency injection rather than patching imports

2. **❌ Testing Implementation Details**
   - Instead: Tests observable behavior and outcomes
   - Verifies what the system does, not how it does it

3. **❌ Testing Specific Strings** (Brittle)
   - Instead: Tests content structure, length, format
   - Focuses on functional behavior rather than exact wording

4. **❌ Complex Mock Hierarchies**
   - Instead: Simple test doubles with predictable behavior
   - Clear, readable test setup

## 🧰 Test Doubles Usage

### From `tests.fixtures.test_doubles`:

```python
# ✅ Good: Use test doubles
from tests.fixtures.test_doubles import (
    TestIdleDetector,
    InMemoryFilesystemExplorer,
    TestExperienceSynthesizer
)

idle_detector = TestIdleDetector(is_idle=True)
explorer = InMemoryFilesystemExplorer(discoveries)

# ❌ Bad: Excessive patching
with patch("ai_sleepwalker.main.IdleDetector") as mock:
    mock.return_value.is_idle = True
```

## 🏃 Running Tests

### By Category
```bash
# Smoke tests (critical paths)
pytest -m smoke

# Integration tests
pytest -m integration

# Unit tests  
pytest -m unit

# All tests
pytest
```

### By Speed
```bash
# Fast tests only
pytest -m "not slow"

# Exclude external dependencies
pytest -m "not external"
```

### Development Workflow
```bash
# Quick feedback loop
pytest -m smoke -x         # Stop on first failure

# Full validation
pytest -m "smoke or integration"

# Before commit
pytest                      # Run all tests
```

## 📋 Test Writing Guidelines

### 1. Focus on Behavior
```python
# ✅ Good: Test observable outcomes
def test_dream_file_creation():
    # ... setup ...
    assert dream_file.exists()
    assert dream_file.stat().st_size > 0
    assert dream_file.suffix == ".md"

# ❌ Bad: Test implementation details  
def test_dream_calls_llm():
    mock_llm.assert_called_once()
```

### 2. Use Test Doubles
```python
# ✅ Good: Predictable test double
explorer = InMemoryFilesystemExplorer([
    {"name": "test.txt", "type": "file"}
])

# ❌ Bad: Complex mock setup
with patch("module.Explorer") as mock:
    mock.wander.side_effect = [discovery, None]
```

### 3. Test Structure, Not Strings
```python
# ✅ Good: Test content structure
lines = content.split('\n')
assert lines[0].startswith('#')      # Has header
assert len(lines) > 3                # Multiple sections

# ❌ Bad: Brittle string matching
assert "Digital Dream" in content
assert "wandered through" in content.lower()
```

## 🎯 Test Naming

Use descriptive names following the pattern:
`test_[unit_of_work]_[scenario]_[expected_outcome]`

Examples:
- `test_sleepwalker_creates_dream_when_idle()`
- `test_experience_collection_handles_empty_session()`
- `test_factory_creates_compatible_components()`

## 📈 Progressive Testing Approach

Following domain guidance, tests were developed in this order:

1. **✅ Smoke Tests** - Critical paths and system health
2. **🔄 Integration Tests** - Component interactions  
3. **⏳ Unit Tests** - Individual component contracts (next phase)

This approach ensures we validate the most important behaviors first and build a solid foundation for TDD implementation.