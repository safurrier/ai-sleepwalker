"""Test configuration and shared fixtures."""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_directories(temp_dir: Path) -> list[str]:
    """Create test directories for filesystem exploration."""
    # Create test directory structure
    desktop = temp_dir / "Desktop"
    documents = temp_dir / "Documents"
    
    desktop.mkdir()
    documents.mkdir()
    
    # Add some test files
    (desktop / "test_file.txt").write_text("This is a test file on desktop")
    (documents / "grocery_list.txt").write_text("milk\nbread\neggs\nremember to call mom")
    (documents / "old_projects").mkdir()
    (documents / "old_projects" / "README.md").write_text("# Old Project\nSome old project documentation")
    
    return [str(desktop), str(documents)]


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    """Mock LLM client that returns consistent dream responses."""
    mock = AsyncMock()
    mock.acompletion.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="I wandered through digital corridors of forgotten intentions..."
                )
            )
        ]
    )
    return mock


@pytest.fixture
def mock_idle_detector() -> MagicMock:
    """Mock idle detector for controlling test flow."""
    mock = MagicMock()
    mock.is_idle = False  # Start as active
    mock.idle_threshold = 5  # Short timeout for tests
    return mock


@pytest.fixture
def mock_sleep_preventer() -> AsyncMock:
    """Mock sleep prevention for testing."""
    mock = AsyncMock()
    mock.is_active = False
    mock.prevent_sleep.return_value.__aenter__ = AsyncMock()
    mock.prevent_sleep.return_value.__aexit__ = AsyncMock()
    return mock


@pytest.fixture
def mock_filesystem_explorer() -> MagicMock:
    """Mock filesystem explorer with predictable discoveries."""
    mock = MagicMock()
    mock.wander.side_effect = [
        {
            "path": "/test/Desktop/test_file.txt",
            "name": "test_file.txt", 
            "type": "file",
            "size_bytes": 25,
            "preview": "This is a test file on desktop"
        },
        {
            "path": "/test/Documents/grocery_list.txt",
            "name": "grocery_list.txt",
            "type": "file", 
            "size_bytes": 50,
            "preview": "milk\nbread\neggs\nremember to call mom"
        },
        None  # End exploration
    ]
    return mock


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()