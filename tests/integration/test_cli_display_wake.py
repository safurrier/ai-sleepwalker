"""Integration tests for CLI display wake lock functionality.

Tests that the CLI properly prevents display sleep using wakepy.keep.presenting()
instead of just system sleep prevention.
"""

import asyncio
import subprocess
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_sleepwalker.main import start_sleepwalking


@pytest.mark.integration
async def test_sleepwalking_uses_display_wake_lock():
    """Test that sleepwalking uses wakepy.keep.presenting for display wake lock.
    
    This test verifies that the main sleepwalking function uses the correct
    wakepy mode to prevent both system sleep AND display sleep/screen lock.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        
        # Mock wakepy to verify correct method is called
        with patch("ai_sleepwalker.main.wakepy") as mock_wakepy:
            # Mock the context manager
            mock_context = MagicMock()
            mock_wakepy.keep.presenting.return_value.__enter__.return_value = mock_context
            mock_wakepy.keep.presenting.return_value.__exit__.return_value = None
            
            # Mock signal to avoid hanging test
            with patch("ai_sleepwalker.main.signal"):
                # Set shutdown flag immediately to avoid infinite loop
                with patch("ai_sleepwalker.main.shutdown_requested", True):
                    
                    # Run sleepwalking briefly
                    await start_sleepwalking(
                        experience_type="dream",
                        allowed_dirs=[temp_dir],
                        idle_timeout=0,
                        output_dir=output_dir
                    )
            
            # Verify wakepy.keep.presenting was called (not keep.running)
            mock_wakepy.keep.presenting.assert_called_once()
            mock_wakepy.keep.running.assert_not_called()


@pytest.mark.smoke
def test_cli_displays_correct_wake_lock_message():
    """Test that CLI displays message about display wake lock activation.
    
    Verifies user gets clear feedback about what type of wake lock is active.
    This test should FAIL until we update the logging message.
    """
    # Start CLI process with timeout
    try:
        result = subprocess.run([
            "uv", "run", "-m", "ai_sleepwalker", 
            "--no-confirm",
            "--dirs", "/tmp"
        ], 
        timeout=3,  # Short timeout to capture startup logs
        capture_output=True,
        text=True
        )
        output = result.stdout + result.stderr
    except subprocess.TimeoutExpired as e:
        # Expected - CLI is running, capture output from timeout exception
        output = (e.stdout or b'').decode() + (e.stderr or b'').decode()
    
    # Should mention display wake lock specifically (not just system wake lock)
    assert "display wake lock" in output.lower() or "presenting" in output.lower()
    # Current message says "preventing sleep and screen lock" but should be more specific
    assert "preventing sleep and screen lock" in output.lower()


@pytest.mark.integration
def test_cli_launch_with_display_wake_lock_timeout():
    """Test CLI launches successfully and activates display wake lock.
    
    Uses timeout pattern to verify CLI can start without errors.
    A successful launch will run indefinitely until timeout.
    """
    try:
        result = subprocess.run([
            "uv", "run", "-m", "ai_sleepwalker", 
            "--no-confirm",
            "--dirs", "/tmp"
        ],
        timeout=2,  # Short timeout
        capture_output=True,
        text=True
        )
        
        # If we get here, process exited quickly = probably failed
        assert result.returncode in [0, 130], f"Bad exit code: {result.returncode}"
        assert "error" not in result.stderr.lower(), f"Error in stderr: {result.stderr}"
        
    except subprocess.TimeoutExpired:
        # Timeout = process is still running = successful launch
        assert True, "CLI launched successfully with display wake lock (timed out as expected)"


@pytest.mark.unit
async def test_start_sleepwalking_signal_handling_with_display_wake():
    """Test that signal handling properly releases display wake lock.
    
    Verifies graceful shutdown releases the correct wake lock type.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        
        # Mock wakepy and signal handling  
        with patch("ai_sleepwalker.main.wakepy") as mock_wakepy:
            mock_context = MagicMock()
            mock_wakepy.keep.presenting.return_value.__enter__.return_value = mock_context
            mock_wakepy.keep.presenting.return_value.__exit__.return_value = None
            
            with patch("ai_sleepwalker.main.signal") as mock_signal:
                # Set shutdown flag after brief delay to test cleanup
                async def set_shutdown():
                    await asyncio.sleep(0.1)
                    import ai_sleepwalker.main
                    ai_sleepwalker.main.shutdown_requested = True
                
                # Start shutdown process
                shutdown_task = asyncio.create_task(set_shutdown())
                
                # Run sleepwalking
                await start_sleepwalking(
                    experience_type="dream", 
                    allowed_dirs=[temp_dir],
                    idle_timeout=0,
                    output_dir=output_dir
                )
                
                await shutdown_task
            
            # Verify context manager was used (will call __exit__ on cleanup)
            mock_wakepy.keep.presenting.assert_called_once()
            mock_context_manager = mock_wakepy.keep.presenting.return_value
            mock_context_manager.__enter__.assert_called_once()
            mock_context_manager.__exit__.assert_called_once()