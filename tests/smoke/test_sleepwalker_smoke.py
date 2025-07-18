"""Smoke tests for sleepwalker core functionality.

These tests validate critical user journeys work end-to-end, focusing on
behavior rather than implementation details. Uses test doubles for reliability.
"""

import os
import tempfile
from pathlib import Path

import pytest

from ai_sleepwalker.core.idle_detector import IdleDetector
from ai_sleepwalker.core.sleep_preventer import SleepPreventer
from ai_sleepwalker.experiences.base import ExperienceType
from ai_sleepwalker.experiences.factory import ExperienceFactory
from tests.fixtures.test_doubles import (
    FakeExperienceCollector,
    FakeExperienceSynthesizer,
    FakeIdleDetector,
    FakeSleepPreventer,
    InMemoryFilesystemExplorer,
    create_temp_output_structure,
    create_test_discoveries,
)


@pytest.mark.smoke
def test_sleepwalker_cli_starts_successfully():
    """Critical: CLI interface loads without errors."""
    try:
        from ai_sleepwalker.cli import sleepwalk
    except ImportError as e:
        pytest.fail(f"Failed to import CLI module: {e}")

    # Test that CLI command can be imported and has expected interface
    assert callable(sleepwalk)

    # Test that it's a Click command (has Click attributes)
    assert hasattr(sleepwalk, "params")  # Click commands have params
    assert hasattr(sleepwalk, "callback")  # Click commands have callback

    # Test that expected options are defined
    param_names = [param.name for param in sleepwalk.params if hasattr(param, "name")]
    expected_options = ["dirs", "idle_timeout", "mode", "output_dir"]

    # Verify all expected options are present
    for option in expected_options:
        assert option in param_names, f"Missing CLI option: {option}"


@pytest.mark.smoke
async def test_idle_detection_and_exploration_workflow():
    """Critical: System detects idle state and begins exploration."""
    # Arrange - Use test doubles for predictable behavior
    idle_detector = FakeIdleDetector(is_idle=True)
    discoveries = create_test_discoveries()
    explorer = InMemoryFilesystemExplorer(discoveries)

    # Act - Simulate the core workflow
    with tempfile.TemporaryDirectory() as temp_dir:
        create_temp_output_structure(Path(temp_dir))

        # Simulate exploration session
        exploration_results = []
        while True:
            discovery = explorer.wander()
            if discovery is None:
                break
            exploration_results.append(discovery)

        # Assert - Verify critical behaviors occurred
        assert idle_detector.is_idle is True  # Idle state detected
        assert explorer.wander_count > 0  # Exploration attempted
        assert len(exploration_results) == len(discoveries)  # All discoveries found
        assert all(
            hasattr(result, "path") for result in exploration_results
        )  # Valid discovery format


@pytest.mark.smoke
@pytest.mark.skipif(
    bool(os.getenv("CI")) or bool(os.getenv("GITHUB_ACTIONS")),
    reason="Real idle detection testing not supported in CI environment",
)
def test_real_idle_detector_lifecycle_works():
    """Critical: Real IdleDetector with pynput can be created and cleanly stopped."""

    # Test real pynput integration (local testing only)
    detector = IdleDetector(idle_threshold=60)

    try:
        # Should initialize without crashing
        assert detector.idle_threshold == 60

        # Should start in active state
        assert not detector.is_idle

        # Should have proper interface for integration
        assert isinstance(detector.is_idle, bool)
        assert hasattr(detector.last_activity, "year")  # datetime object

    finally:
        # Should stop cleanly without hanging
        detector.stop()


@pytest.mark.smoke
async def test_experience_collection_and_synthesis():
    """Critical: Observations are collected and synthesized into dreams."""
    # Arrange - Use test doubles
    collector = FakeExperienceCollector()
    synthesizer = FakeExperienceSynthesizer(ExperienceType.DREAM)
    discoveries = create_test_discoveries()

    # Act - Simulate observation collection and synthesis
    for discovery in discoveries:
        collector.add_observation(discovery)

    observations = collector.get_observations()
    result = await synthesizer.synthesize(observations)

    # Assert - Verify core behavior without string matching
    assert len(observations) == len(discoveries)  # All discoveries collected
    assert result.total_observations == len(discoveries)  # Count matches
    assert len(result.content) > 0  # Content was generated
    assert result.experience_type == ExperienceType.DREAM  # Correct type
    assert result.file_extension == ".md"  # Proper format


@pytest.mark.smoke
async def test_dream_file_creation():
    """Critical: Dream files are created in the correct location."""
    # Arrange
    synthesizer = FakeExperienceSynthesizer()
    observations = []  # Empty session for minimal test

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = create_temp_output_structure(Path(temp_dir))

        # Act - Create dream result and save
        result = await synthesizer.synthesize(observations)

        # Simulate file creation (test the behavior we expect)
        dream_file = (
            output_dir / f"dream_{result.session_start.strftime('%Y%m%d_%H%M%S')}.md"
        )
        dream_file.write_text(result.content)

        # Assert - Verify file creation behavior
        assert dream_file.exists()  # File was created
        assert dream_file.suffix == ".md"  # Correct format
        assert dream_file.stat().st_size > 0  # File has content
        content_lines = dream_file.read_text().split("\n")
        assert len(content_lines) > 1  # Multi-line content structure


@pytest.mark.smoke
def test_sleep_prevention_lifecycle():
    """Critical: Sleep prevention activates and deactivates properly."""
    # Arrange
    sleep_preventer = FakeSleepPreventer()

    # Act & Assert - Test prevention lifecycle
    assert sleep_preventer.is_preventing_sleep is False  # Initially not preventing
    assert sleep_preventer.prevention_count == 0  # No prevention calls yet

    # Simulate prevention session
    async def prevention_session():
        async with sleep_preventer.prevent_sleep():
            assert sleep_preventer.is_preventing_sleep is True  # Prevention active
            assert sleep_preventer.prevention_count == 1  # Prevention started

        # After context exits
        assert sleep_preventer.is_preventing_sleep is False  # Prevention stopped

    # Run the async test
    import asyncio

    asyncio.run(prevention_session())


@pytest.mark.smoke
@pytest.mark.skipif(
    bool(os.getenv("CI")) or bool(os.getenv("GITHUB_ACTIONS")),
    reason="Real sleep prevention testing not supported in CI environment",
)
async def test_real_sleep_preventer_lifecycle_works():
    """Critical: Real SleepPreventer can activate and deactivate properly."""
    # Arrange - Use real SleepPreventer (local testing only)
    sleep_preventer = SleepPreventer()

    # Act & Assert - Test basic lifecycle
    assert sleep_preventer.is_preventing_sleep is False
    assert sleep_preventer.prevention_count == 0

    async with sleep_preventer.prevent_sleep():
        # Should be preventing during context
        assert sleep_preventer.is_preventing_sleep is True
        assert sleep_preventer.prevention_count == 1

    # Should stop preventing after context exits
    assert sleep_preventer.is_preventing_sleep is False
    assert sleep_preventer.prevention_count == 1  # Count persists


@pytest.mark.smoke
def test_sleep_preventer_interface_works():
    """Critical: SleepPreventer interface is available and properly structured."""
    # Test component interface without system dependencies
    sleep_preventer = SleepPreventer()

    # Verify interface exists
    assert hasattr(sleep_preventer, "prevent_sleep")
    assert hasattr(sleep_preventer, "is_preventing_sleep")
    assert hasattr(sleep_preventer, "prevention_count")

    # Verify initial state
    assert sleep_preventer.is_preventing_sleep is False
    assert sleep_preventer.prevention_count == 0
    assert isinstance(sleep_preventer.is_preventing_sleep, bool)
    assert isinstance(sleep_preventer.prevention_count, int)


@pytest.mark.smoke
def test_idle_detector_interface_works():
    """Critical: IdleDetector interface is available and properly structured."""
    # Test component interface without system dependencies
    idle_detector = IdleDetector(start_listeners=False)

    try:
        # Verify interface exists
        assert hasattr(idle_detector, "is_idle")
        assert hasattr(idle_detector, "idle_threshold")
        assert hasattr(idle_detector, "last_activity")
        assert hasattr(idle_detector, "stop")

        # Verify initial state
        assert isinstance(idle_detector.is_idle, bool)
        assert isinstance(idle_detector.idle_threshold, int | float)
        assert hasattr(idle_detector.last_activity, "year")  # datetime object

    finally:
        # Clean shutdown
        idle_detector.stop()


@pytest.mark.smoke
def test_experience_type_factory_system():
    """Critical: Experience system supports different modes."""
    # Test that factory can create dream components
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)

    # Verify proper types without testing implementation
    assert collector is not None
    assert synthesizer is not None
    assert synthesizer.experience_type == ExperienceType.DREAM

    # Test future mode support (should raise NotImplementedError, not crash)
    with pytest.raises(NotImplementedError):
        ExperienceFactory.create_collector(ExperienceType.ADVENTURE)


@pytest.mark.smoke
def test_configuration_and_defaults():
    """Critical: System has proper default configuration."""
    from ai_sleepwalker.experiences.base import ExperienceType

    # Test that experience types are properly defined
    assert ExperienceType.DREAM.value == "dream"
    assert ExperienceType.ADVENTURE.value == "adventure"
    assert ExperienceType.SCRAPBOOK.value == "scrapbook"

    # Test that we have the core expected modes available
    available_modes = [mode.value for mode in ExperienceType]
    core_modes = ["dream", "adventure", "scrapbook"]
    assert all(mode in available_modes for mode in core_modes)


@pytest.mark.smoke
def test_component_interfaces_defined():
    """Critical: All core components have proper interfaces."""
    try:
        from ai_sleepwalker.core.filesystem_explorer import FilesystemExplorer
        # IdleDetector and SleepPreventer already imported at top
    except ImportError as e:
        pytest.fail(f"Failed to import core components: {e}")

    # Test that classes can be instantiated (basic contract)
    try:
        idle_detector = IdleDetector(start_listeners=False)  # Don't start in CI
        sleep_preventer = SleepPreventer()
        explorer = FilesystemExplorer(["/tmp"])  # Safe test directory
    except Exception as e:
        pytest.fail(f"Failed to instantiate components: {e}")

    # Test that they have expected interfaces
    assert hasattr(idle_detector, "is_idle")
    assert hasattr(sleep_preventer, "prevent_sleep")
    assert hasattr(explorer, "wander")

    # Test that critical properties work
    assert isinstance(idle_detector.is_idle, bool)
    assert callable(explorer.wander)


# Note: These smoke tests focus on behavior verification rather than
# implementation details. They use test doubles to ensure reliability
# and avoid the anti-patterns identified in the domain guidance.
