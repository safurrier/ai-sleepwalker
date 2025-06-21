"""Component-level tests for sleepwalker modules.

These tests will guide the implementation of individual components
following the TDD approach. Tests are organized by component and
will initially fail until implementations are created.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


class TestIdleDetector:
    """Tests for the idle detection component."""
    
    def test_idle_detector_initialization(self) -> None:
        """Test that IdleDetector initializes with correct defaults."""
        from ai_sleepwalker.core.idle_detector import IdleDetector
        
        detector = IdleDetector()
        assert detector.idle_threshold == 900  # 15 minutes default
        assert not detector.is_idle  # Should start as active
        assert detector.last_activity is not None
    
    def test_idle_detector_configurable_timeout(self) -> None:
        """Test that idle timeout can be configured."""
        from ai_sleepwalker.core.idle_detector import IdleDetector
        
        detector = IdleDetector(idle_threshold=300)  # 5 minutes
        assert detector.idle_threshold == 300
    
    def test_idle_detector_tracks_activity(self) -> None:
        """Test that detector properly tracks user activity."""
        from ai_sleepwalker.core.idle_detector import IdleDetector
        
        detector = IdleDetector(idle_threshold=5)  # 5 seconds for testing
        
        # Should start as active
        assert not detector.is_idle
        
        # Mock time to simulate passing threshold
        with patch('ai_sleepwalker.core.idle_detector.datetime') as mock_datetime:
            # Simulate 10 seconds passed
            mock_datetime.now.return_value = detector.last_activity + timedelta(seconds=10)
            assert detector.is_idle


class TestSleepPreventer:
    """Tests for the sleep prevention component."""
    
    async def test_sleep_preventer_initialization(self) -> None:
        """Test that SleepPreventer initializes correctly."""
        from ai_sleepwalker.core.sleep_preventer import SleepPreventer
        
        preventer = SleepPreventer()
        assert not preventer.is_active
    
    async def test_sleep_prevention_context_manager(self) -> None:
        """Test that sleep prevention works as async context manager."""
        from ai_sleepwalker.core.sleep_preventer import SleepPreventer
        
        preventer = SleepPreventer()
        
        with patch('wakepy.keep.running') as mock_keep:
            async with preventer.prevent_sleep():
                assert preventer.is_active
                mock_keep.assert_called_once()
            
            assert not preventer.is_active


class TestFilesystemExplorer:
    """Tests for the filesystem exploration component."""
    
    def test_filesystem_explorer_initialization(self, test_directories: list[str]) -> None:
        """Test that FilesystemExplorer initializes with allowed directories."""
        from ai_sleepwalker.core.filesystem_explorer import FilesystemExplorer
        
        explorer = FilesystemExplorer(test_directories)
        assert len(explorer.allowed_paths) == len(test_directories)
        assert explorer.current_path is not None
    
    def test_explorer_respects_directory_boundaries(self, test_directories: list[str]) -> None:
        """Test that explorer only accesses allowed directories."""
        from ai_sleepwalker.core.filesystem_explorer import FilesystemExplorer
        
        explorer = FilesystemExplorer(test_directories)
        
        # Should reject paths outside allowed directories
        assert not explorer._is_safe_path(Path("/etc/passwd"))
        assert not explorer._is_safe_path(Path("/root"))
        
        # Should accept paths within allowed directories
        for allowed_dir in test_directories:
            assert explorer._is_safe_path(Path(allowed_dir))
    
    def test_explorer_creates_observations(self, test_directories: list[str]) -> None:
        """Test that explorer creates proper observation objects."""
        from ai_sleepwalker.core.filesystem_explorer import FilesystemExplorer
        
        explorer = FilesystemExplorer(test_directories)
        
        # Test with a known test file
        test_file = Path(test_directories[0]) / "test_file.txt"
        if test_file.exists():
            observation = explorer._create_discovery(test_file)
            
            assert observation["name"] == "test_file.txt"
            assert observation["type"] == "file"
            assert "path" in observation
            assert "size_bytes" in observation


class TestExperienceFramework:
    """Tests for the experience framework architecture."""
    
    def test_experience_types_defined(self) -> None:
        """Test that experience types are properly defined."""
        from ai_sleepwalker.experiences.base import ExperienceType
        
        assert ExperienceType.DREAM == "dream"
        assert ExperienceType.ADVENTURE == "adventure"
        assert ExperienceType.SCRAPBOOK == "scrapbook"
    
    def test_experience_factory_creates_dream_components(self) -> None:
        """Test that factory creates dream mode components."""
        from ai_sleepwalker.experiences.base import ExperienceType
        from ai_sleepwalker.experiences.factory import ExperienceFactory
        from ai_sleepwalker.experiences.dream import DreamCollector, DreamSynthesizer
        
        collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
        synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)
        
        assert isinstance(collector, DreamCollector)
        assert isinstance(synthesizer, DreamSynthesizer)
        assert synthesizer.experience_type == ExperienceType.DREAM
    
    def test_dream_collector_adds_observations(self) -> None:
        """Test that dream collector properly stores observations."""
        from ai_sleepwalker.experiences.dream import DreamCollector
        
        collector = DreamCollector()
        
        test_discovery = {
            "path": "/test/file.txt",
            "name": "file.txt",
            "type": "file",
            "size_bytes": 100,
            "preview": "test content"
        }
        
        collector.add_observation(test_discovery)
        observations = collector.get_observations()
        
        assert len(observations) == 1
        assert observations[0].path == "/test/file.txt"
        assert observations[0].brief_note != ""


class TestCLIInterface:
    """Tests for the command-line interface."""
    
    def test_cli_imports_successfully(self) -> None:
        """Test that CLI module can be imported."""
        from ai_sleepwalker.cli import sleepwalk
        assert sleepwalk is not None
    
    def test_cli_help_output(self) -> None:
        """Test that CLI provides helpful usage information."""
        from click.testing import CliRunner
        from ai_sleepwalker.cli import sleepwalk
        
        runner = CliRunner()
        result = runner.invoke(sleepwalk, ["--help"])
        
        assert result.exit_code == 0
        assert "sleepwalker" in result.output.lower()
        assert "directories" in result.output.lower()
        assert "--dirs" in result.output or "--directories" in result.output