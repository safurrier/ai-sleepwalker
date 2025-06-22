"""Unit tests for IdleDetector component."""

import time
from datetime import datetime, timedelta

import pytest

from ai_sleepwalker.core.idle_detector import IdleDetector


@pytest.mark.unit
def test_idle_detector_initialization():
    """Test IdleDetector initializes with correct defaults."""
    detector = IdleDetector(start_listeners=False)

    try:
        assert detector.idle_threshold == 900  # 15 minutes default
        assert isinstance(detector.last_activity, datetime)
        assert not detector.is_idle  # Should not be idle immediately
    finally:
        detector.stop()


@pytest.mark.unit
def test_idle_detector_custom_threshold():
    """Test IdleDetector accepts custom idle threshold."""
    custom_threshold = 300  # 5 minutes
    detector = IdleDetector(idle_threshold=custom_threshold, start_listeners=False)

    try:
        assert detector.idle_threshold == custom_threshold
    finally:
        detector.stop()


@pytest.mark.unit
def test_is_idle_initially_false():
    """Test that detector is not idle immediately after creation."""
    detector = IdleDetector(
        idle_threshold=1, start_listeners=False
    )  # 1 second threshold

    try:
        assert not detector.is_idle
    finally:
        detector.stop()


@pytest.mark.unit
def test_is_idle_becomes_true_after_threshold():
    """Test that detector becomes idle after threshold time."""
    detector = IdleDetector(
        idle_threshold=1, start_listeners=False
    )  # 1 second threshold

    try:
        # Manually set last_activity to past
        detector.last_activity = datetime.now() - timedelta(seconds=2)

        assert detector.is_idle
    finally:
        detector.stop()


@pytest.mark.unit
def test_activity_resets_idle_state():
    """Test that activity resets the idle timer."""
    detector = IdleDetector(
        idle_threshold=1, start_listeners=False
    )  # 1 second threshold

    try:
        # Make it idle
        detector.last_activity = datetime.now() - timedelta(seconds=2)
        assert detector.is_idle

        # Trigger activity
        detector._on_activity()
        assert not detector.is_idle
    finally:
        detector.stop()


@pytest.mark.unit
def test_thread_safety_of_activity_updates():
    """Test that activity timestamp updates are thread-safe."""
    detector = IdleDetector(start_listeners=False)

    try:
        # This test ensures _on_activity can be called from multiple threads
        # without causing race conditions
        import threading

        def simulate_activity():
            for _ in range(10):
                detector._on_activity()
                time.sleep(0.01)

        # Run multiple threads updating activity
        threads = [threading.Thread(target=simulate_activity) for _ in range(3)]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should complete without error
        assert isinstance(detector.last_activity, datetime)
    finally:
        detector.stop()


@pytest.mark.unit
def test_stop_method_exists_and_callable():
    """Test that stop method exists and can be called safely."""
    detector = IdleDetector(start_listeners=False)

    # Should be able to call stop without error
    detector.stop()

    # Should be safe to call stop multiple times
    detector.stop()


@pytest.mark.unit
def test_on_activity_updates_timestamp():
    """Test that _on_activity method updates the timestamp correctly."""
    detector = IdleDetector(start_listeners=False)

    try:
        old_timestamp = detector.last_activity
        time.sleep(0.01)  # Ensure time difference

        detector._on_activity()

        # Should have updated to a newer timestamp
        assert detector.last_activity > old_timestamp
    finally:
        detector.stop()


@pytest.mark.unit
def test_idle_check_with_various_thresholds():
    """Test idle detection with different threshold values."""
    test_cases = [
        (1, 0.5, False),  # threshold=1s, elapsed=0.5s, should_be_idle=False
        (1, 1.5, True),  # threshold=1s, elapsed=1.5s, should_be_idle=True
        (5, 3, False),  # threshold=5s, elapsed=3s, should_be_idle=False
        (5, 6, True),  # threshold=5s, elapsed=6s, should_be_idle=True
    ]

    for threshold, elapsed_seconds, expected_idle in test_cases:
        detector = IdleDetector(idle_threshold=threshold, start_listeners=False)

        try:
            # Set activity to past
            detector.last_activity = datetime.now() - timedelta(seconds=elapsed_seconds)

            assert detector.is_idle == expected_idle, (
                f"Failed for threshold={threshold}s, elapsed={elapsed_seconds}s"
            )
        finally:
            detector.stop()


@pytest.mark.unit
def test_activity_callback_behavior():
    """Test that activity callback properly resets idle state."""
    detector = IdleDetector(idle_threshold=2, start_listeners=False)

    try:
        # Make it idle
        detector.last_activity = datetime.now() - timedelta(seconds=3)
        assert detector.is_idle

        # Simulate activity (what pynput listeners would call)
        detector._on_activity("dummy", "args")

        # Should no longer be idle
        assert not detector.is_idle

        # Test with keyword arguments too
        detector.last_activity = datetime.now() - timedelta(seconds=3)
        assert detector.is_idle

        detector._on_activity(x=100, y=200)
        assert not detector.is_idle
    finally:
        detector.stop()
