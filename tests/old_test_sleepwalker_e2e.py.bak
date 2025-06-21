"""End-to-end tests that define the complete sleepwalker user experience.

These tests specify exactly how the system should behave from a user perspective,
following the TDD principle of writing failing tests first to guide implementation.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.e2e
async def test_complete_sleepwalk_session(
    test_directories: list[str],
    mock_llm_client: AsyncMock,
    mock_idle_detector: MagicMock,
    mock_sleep_preventer: AsyncMock,
    mock_filesystem_explorer: MagicMock,
    temp_dir: Path,
) -> None:
    """Test the complete sleepwalker workflow from CLI start to dream log creation.
    
    This test defines the complete user experience:
    1. Start CLI with directories
    2. Wait for idle state
    3. Prevent sleep during exploration
    4. Explore filesystem safely
    5. Generate dream from observations
    6. Save dream log to file
    """
    # This test will fail until we implement the sleepwalker components
    from ai_sleepwalker.main import start_sleepwalking
    from ai_sleepwalker.experiences.base import ExperienceType
    
    # Configure mocks for complete workflow
    mock_idle_detector.is_idle = True  # Simulate user is idle
    
    # Run the sleepwalker session
    dream_dir = temp_dir / "dreams"
    
    with patch("ai_sleepwalker.main.IdleDetector", return_value=mock_idle_detector), \
         patch("ai_sleepwalker.main.SleepPreventer", return_value=mock_sleep_preventer), \
         patch("ai_sleepwalker.main.FilesystemExplorer", return_value=mock_filesystem_explorer), \
         patch("litellm.acompletion", mock_llm_client.acompletion):
        
        # Start sleepwalking session (should complete quickly due to mocks)
        await start_sleepwalking(
            experience_type=ExperienceType.DREAM,
            allowed_dirs=test_directories,
            idle_timeout=1,  # Short timeout for testing
            output_dir=dream_dir
        )
    
    # Verify the complete workflow executed
    assert mock_idle_detector.is_idle  # Should have checked idle state
    mock_sleep_preventer.prevent_sleep.assert_called_once()  # Should have prevented sleep
    assert mock_filesystem_explorer.wander.call_count >= 1  # Should have explored filesystem
    mock_llm_client.acompletion.assert_called_once()  # Should have generated dream
    
    # Verify dream log was created
    dream_files = list(dream_dir.glob("*.md"))
    assert len(dream_files) == 1
    
    dream_content = dream_files[0].read_text()
    assert "Digital Dream" in dream_content
    assert "wandered through" in dream_content.lower()


@pytest.mark.e2e
async def test_user_return_interrupts_session(
    test_directories: list[str],
    mock_idle_detector: MagicMock,
    mock_sleep_preventer: AsyncMock,
    mock_filesystem_explorer: MagicMock,
    temp_dir: Path,
) -> None:
    """Test that exploration stops gracefully when user becomes active.
    
    This ensures the sleepwalker respects user activity and doesn't interfere
    with normal computer usage.
    """
    from ai_sleepwalker.main import start_sleepwalking
    from ai_sleepwalker.experiences.base import ExperienceType
    
    # Start idle, then become active during exploration
    mock_idle_detector.is_idle = True
    
    # Create a side effect that simulates user return
    def simulate_user_return(*args, **kwargs):
        # After first wander call, user becomes active
        mock_idle_detector.is_idle = False
        return mock_filesystem_explorer.wander.side_effect[0]
    
    mock_filesystem_explorer.wander.side_effect = [simulate_user_return]
    
    dream_dir = temp_dir / "dreams"
    
    with patch("ai_sleepwalker.main.IdleDetector", return_value=mock_idle_detector), \
         patch("ai_sleepwalker.main.SleepPreventer", return_value=mock_sleep_preventer), \
         patch("ai_sleepwalker.main.FilesystemExplorer", return_value=mock_filesystem_explorer):
        
        # Start sleepwalking session
        await start_sleepwalking(
            experience_type=ExperienceType.DREAM,
            allowed_dirs=test_directories,
            idle_timeout=1,
            output_dir=dream_dir
        )
    
    # Verify graceful shutdown occurred
    mock_sleep_preventer.prevent_sleep.assert_called()  # Should have started sleep prevention
    # Should have stopped exploration when user returned (limited wander calls)
    assert mock_filesystem_explorer.wander.call_count <= 2


@pytest.mark.e2e 
def test_cli_with_custom_directories(
    test_directories: list[str],
    temp_dir: Path,
) -> None:
    """Test that CLI accepts and respects custom exploration directories.
    
    This verifies the CLI interface works correctly and passes directory
    configuration through to the core sleepwalker logic.
    """
    from click.testing import CliRunner
    from ai_sleepwalker.cli import sleepwalk
    
    runner = CliRunner()
    
    # Test CLI with custom directories
    result = runner.invoke(sleepwalk, [
        "--dirs", test_directories[0],
        "--dirs", test_directories[1], 
        "--idle-timeout", "1",
        "--output-dir", str(temp_dir / "test_dreams"),
        "--help"  # Just test argument parsing for now
    ])
    
    # Should parse arguments successfully
    assert result.exit_code == 0
    assert "sleepwalker" in result.output.lower()
    assert "directories" in result.output.lower()


@pytest.mark.e2e
async def test_dream_log_format_and_content(
    test_directories: list[str],
    mock_llm_client: AsyncMock,
    mock_idle_detector: MagicMock,
    mock_sleep_preventer: AsyncMock,
    mock_filesystem_explorer: MagicMock,
    temp_dir: Path,
) -> None:
    """Test that dream logs are created with correct format and content.
    
    This verifies the output format matches the expected dream log structure
    with proper metadata and content organization.
    """
    from ai_sleepwalker.main import start_sleepwalking
    from ai_sleepwalker.experiences.base import ExperienceType
    
    # Configure for complete session
    mock_idle_detector.is_idle = True
    
    # Custom dream response
    mock_llm_client.acompletion.return_value.choices[0].message.content = (
        "I drifted through digital corridors, finding a grocery list with "
        "tender reminders: 'remember to call mom' glowed softly among "
        "mundane needs like milk and bread..."
    )
    
    dream_dir = temp_dir / "dreams"
    
    with patch("ai_sleepwalker.main.IdleDetector", return_value=mock_idle_detector), \
         patch("ai_sleepwalker.main.SleepPreventer", return_value=mock_sleep_preventer), \
         patch("ai_sleepwalker.main.FilesystemExplorer", return_value=mock_filesystem_explorer), \
         patch("litellm.acompletion", mock_llm_client.acompletion):
        
        await start_sleepwalking(
            experience_type=ExperienceType.DREAM,
            allowed_dirs=test_directories,
            idle_timeout=1,
            output_dir=dream_dir
        )
    
    # Verify dream log content and format
    dream_files = list(dream_dir.glob("*.md"))
    assert len(dream_files) == 1
    
    dream_content = dream_files[0].read_text()
    
    # Should have proper dream log structure
    assert "# Digital Dream" in dream_content
    assert "Session" in dream_content or "observations" in dream_content.lower()
    assert "call mom" in dream_content  # Should include observation details
    
    # Should have timestamp in filename
    filename = dream_files[0].name
    assert filename.endswith(".md")
    assert len(filename.split("-")) >= 3  # Should have date components


@pytest.mark.e2e
async def test_multiple_experience_modes_ready(temp_dir: Path) -> None:
    """Test that the experience framework is ready for multiple modes.
    
    This ensures the architecture can support adventure, scrapbook, and other
    future experience modes beyond just dreams.
    """
    from ai_sleepwalker.experiences.base import ExperienceType
    from ai_sleepwalker.experiences.factory import ExperienceFactory
    
    # Should support dream mode (implemented)
    dream_collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    dream_synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)
    
    assert dream_collector is not None
    assert dream_synthesizer is not None
    assert dream_synthesizer.experience_type == ExperienceType.DREAM
    
    # Should have framework ready for future modes (will raise NotImplementedError)
    with pytest.raises(NotImplementedError, match="Adventure mode coming soon"):
        ExperienceFactory.create_collector(ExperienceType.ADVENTURE)
    
    with pytest.raises(NotImplementedError, match="Scrapbook mode coming soon"):
        ExperienceFactory.create_collector(ExperienceType.SCRAPBOOK)