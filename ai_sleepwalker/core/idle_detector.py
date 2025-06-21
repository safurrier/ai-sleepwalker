"""User activity detection for triggering sleepwalker sessions."""

from datetime import datetime
from typing import Any


class IdleDetector:
    """Detects when the system has been idle for a configurable period."""

    def __init__(self, idle_threshold: int = 900) -> None:
        """Initialize idle detector.

        Args:
            idle_threshold: Seconds before idle (default: 15m)
        """
        self.idle_threshold = idle_threshold
        self.last_activity = datetime.now()
        # TODO: Set up pynput listeners for mouse and keyboard activity

    @property
    def is_idle(self) -> bool:
        """Check if system has been idle long enough."""
        # TODO: Implement actual idle detection logic
        # For now, return False (always active) until implementation
        elapsed = (datetime.now() - self.last_activity).total_seconds()
        return elapsed > self.idle_threshold

    def _on_activity(self, *args: Any, **kwargs: Any) -> None:
        """Called when user activity is detected."""
        self.last_activity = datetime.now()
