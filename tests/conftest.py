"""Test configuration and shared fixtures for sleepwalker tests.

Minimal conftest.py that provides only essential shared fixtures,
avoiding the excessive mocking anti-pattern identified in domain guidance.
"""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_dir() -> Path:
    """Temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_directories() -> list[str]:
    """Real test directories for filesystem-based tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        
        # Create realistic test directory structure
        (test_dir / "documents").mkdir()
        (test_dir / "documents" / "notes.txt").write_text("Personal notes content")
        (test_dir / "documents" / "journal.md").write_text("# Daily Journal\n\nToday's thoughts...")
        
        (test_dir / "photos").mkdir()
        (test_dir / "photos" / "vacation").mkdir()
        
        (test_dir / "projects").mkdir()
        (test_dir / "projects" / "readme.md").write_text("# Important Project\n\nProject details...")
        (test_dir / "projects" / "todo.txt").write_text("- Fix bugs\n- Add tests")
        
        yield [str(test_dir)]


# Note: Removed excessive mock fixtures following domain guidance.
# Tests should use test doubles from tests.fixtures.test_doubles instead
# of brittle mocking setups that couple tests to implementation details.