"""Unit tests for IdleDetector component.

Following testing conventions:
- Test behavior, not implementation details
- Use fixtures for reusable test data
- Table-driven testing for multiple scenarios
- Focus on observable outcomes
"""

import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest

from ai_sleepwalker.core.idle_detector import IdleDetector


@dataclass
class IdleTestCase:
    """Test case for idle detection behavior."""

    name: str
    threshold_seconds: int
    elapsed_seconds: float
    expected_idle: bool


class TestIdleDetectorInitialization:
    """Test suite for IdleDetector initialization and configuration."""

    @pytest.fixture
    def detector_without_listeners(self) -> IdleDetector:
        """Provides IdleDetector without pynput listeners for unit testing."""
        detector = IdleDetector(start_listeners=False)
        yield detector
        detector.stop()

    @pytest.mark.unit
    def test_initializes_with_default_threshold(
        self, detector_without_listeners: IdleDetector
    ) -> None:
        """IdleDetector uses 15-minute default threshold when not specified."""
        assert detector_without_listeners.idle_threshold == 900  # 15 minutes

    @pytest.mark.unit
    def test_accepts_custom_threshold(self) -> None:
        """IdleDetector accepts custom idle threshold configuration."""
        custom_threshold = 300  # 5 minutes
        detector = IdleDetector(idle_threshold=custom_threshold, start_listeners=False)

        try:
            assert detector.idle_threshold == custom_threshold
        finally:
            detector.stop()

    @pytest.mark.unit
    def test_starts_in_active_state(
        self, detector_without_listeners: IdleDetector
    ) -> None:
        """IdleDetector starts in active state (not idle) after creation."""
        assert not detector_without_listeners.is_idle

    @pytest.mark.unit
    def test_tracks_creation_timestamp(
        self, detector_without_listeners: IdleDetector
    ) -> None:
        """IdleDetector records last activity timestamp on creation."""
        assert isinstance(detector_without_listeners.last_activity, datetime)
        # Should be very recent (within last few seconds)
        time_diff = (
            datetime.now() - detector_without_listeners.last_activity
        ).total_seconds()
        assert time_diff < 5.0


class TestIdleDetectionBehavior:
    """Test suite for idle detection logic and state transitions."""

    @pytest.fixture
    def detector_with_short_threshold(self) -> IdleDetector:
        """Provides IdleDetector with 1-second threshold for fast testing."""
        detector = IdleDetector(idle_threshold=1, start_listeners=False)
        yield detector
        detector.stop()

    # Table-driven testing for various threshold scenarios
    idle_detection_cases = [
        IdleTestCase("active_under_threshold", 1, 0.5, False),
        IdleTestCase("idle_over_threshold", 1, 1.5, True),
        IdleTestCase("active_long_threshold", 5, 3.0, False),
        IdleTestCase("idle_long_threshold", 5, 6.0, True),
        IdleTestCase(
            "exact_threshold_boundary", 2, 2.0, True
        ),  # Exactly at threshold (should be idle)
        IdleTestCase("just_over_threshold", 2, 2.1, True),  # Just over threshold
    ]

    @pytest.mark.parametrize("case", idle_detection_cases)
    @pytest.mark.unit
    def test_idle_detection_with_various_thresholds(self, case: IdleTestCase) -> None:
        """IdleDetector correctly determines idle state across threshold scenarios."""
        detector = IdleDetector(
            idle_threshold=case.threshold_seconds, start_listeners=False
        )

        try:
            # Arrange - Set activity timestamp to simulate elapsed time
            detector.last_activity = datetime.now() - timedelta(
                seconds=case.elapsed_seconds
            )

            # Act & Assert - Check idle state matches expectation
            assert detector.is_idle == case.expected_idle, (
                f"Test case '{case.name}' failed: "
                f"threshold={case.threshold_seconds}s, elapsed={case.elapsed_seconds}s"
            )
        finally:
            detector.stop()

    @pytest.mark.unit
    def test_activity_resets_idle_state(
        self, detector_with_short_threshold: IdleDetector
    ) -> None:
        """Activity detection resets idle state back to active."""
        # Arrange - Make detector idle by setting old timestamp
        detector_with_short_threshold.last_activity = datetime.now() - timedelta(
            seconds=2
        )
        assert detector_with_short_threshold.is_idle  # Verify it's idle

        # Act - Trigger activity
        detector_with_short_threshold._on_activity()

        # Assert - Should no longer be idle
        assert not detector_with_short_threshold.is_idle

    @pytest.mark.unit
    def test_activity_updates_timestamp(
        self, detector_with_short_threshold: IdleDetector
    ) -> None:
        """Activity callback updates last_activity timestamp to current time."""
        # Arrange - Record old timestamp
        old_timestamp = detector_with_short_threshold.last_activity
        time.sleep(0.01)  # Ensure time difference

        # Act - Trigger activity
        detector_with_short_threshold._on_activity()

        # Assert - Timestamp should be updated to more recent time
        assert detector_with_short_threshold.last_activity > old_timestamp

    @pytest.mark.unit
    def test_activity_callback_accepts_various_arguments(self) -> None:
        """Activity callback handles various argument patterns from pynput listeners."""
        detector = IdleDetector(idle_threshold=2, start_listeners=False)

        try:
            # Make detector idle first
            detector.last_activity = datetime.now() - timedelta(seconds=3)
            assert detector.is_idle

            # Test positional arguments (mouse events)
            detector._on_activity("dummy", "args")
            assert not detector.is_idle

            # Reset to idle state
            detector.last_activity = datetime.now() - timedelta(seconds=3)
            assert detector.is_idle

            # Test keyword arguments (mouse coordinates)
            detector._on_activity(x=100, y=200)
            assert not detector.is_idle
        finally:
            detector.stop()


class TestIdleDetectorLifecycle:
    """Test suite for IdleDetector lifecycle management and cleanup."""

    @pytest.mark.unit
    def test_stop_method_exists_and_callable(self) -> None:
        """IdleDetector provides stop method for clean shutdown."""
        detector = IdleDetector(start_listeners=False)

        # Should be able to call stop without error
        detector.stop()

        # Should be safe to call stop multiple times
        detector.stop()

    @pytest.mark.unit
    def test_stop_method_is_idempotent(self) -> None:
        """Calling stop multiple times is safe and has no side effects."""
        detector = IdleDetector(start_listeners=False)

        # Multiple stop calls should not raise exceptions
        for _ in range(5):
            detector.stop()


class TestThreadSafety:
    """Test suite for thread safety of IdleDetector operations."""

    @pytest.mark.unit
    def test_concurrent_activity_updates_are_thread_safe(self) -> None:
        """Multiple threads can safely update activity timestamps concurrently."""
        detector = IdleDetector(start_listeners=False)

        try:

            def simulate_activity() -> None:
                """Simulate rapid activity updates from multiple threads."""
                for _ in range(10):
                    detector._on_activity()
                    time.sleep(0.001)  # Small delay to encourage race conditions

            # Act - Run multiple threads updating activity simultaneously
            threads = [threading.Thread(target=simulate_activity) for _ in range(5)]
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            # Assert - Should complete without errors or corruption
            assert isinstance(detector.last_activity, datetime)
            # Timestamp should be very recent after all the activity
            time_diff = (datetime.now() - detector.last_activity).total_seconds()
            assert time_diff < 1.0
        finally:
            detector.stop()

    @pytest.mark.unit
    def test_idle_state_checks_are_thread_safe(self) -> None:
        """Checking idle state from multiple threads is safe."""
        detector = IdleDetector(idle_threshold=1, start_listeners=False)

        try:
            results = []

            def check_idle_state() -> None:
                """Check idle state multiple times from thread."""
                for _ in range(50):
                    results.append(detector.is_idle)
                    time.sleep(0.001)

            # Start multiple threads checking idle state
            threads = [threading.Thread(target=check_idle_state) for _ in range(3)]
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            # Should have collected many results without errors
            assert len(results) > 0
            assert all(isinstance(result, bool) for result in results)
        finally:
            detector.stop()


class TestIntegrationBoundaries:
    """Test integration points and expected interfaces for other components."""

    @pytest.mark.unit
    def test_provides_expected_interface(self) -> None:
        """IdleDetector provides the interface expected by other components."""
        detector = IdleDetector(start_listeners=False)

        try:
            # Should have required properties and methods
            assert hasattr(detector, "is_idle")
            assert hasattr(detector, "idle_threshold")
            assert hasattr(detector, "last_activity")
            assert hasattr(detector, "stop")

            # Properties should return expected types
            assert isinstance(detector.is_idle, bool)
            assert isinstance(detector.idle_threshold, int)
            assert isinstance(detector.last_activity, datetime)
            assert callable(detector.stop)
        finally:
            detector.stop()

    @pytest.mark.unit
    def test_supports_dependency_injection_for_testing(self) -> None:
        """IdleDetector supports dependency injection pattern for testing."""
        # Can be created without starting real listeners
        detector = IdleDetector(start_listeners=False)

        try:
            # Should work fully without real pynput listeners
            assert not detector.is_idle
            detector._on_activity()
            assert not detector.is_idle
        finally:
            detector.stop()
