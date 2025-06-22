"""User activity detection for triggering sleepwalker sessions."""

import logging
import threading
from datetime import datetime
from typing import Any

from pynput import keyboard, mouse

# Module-level logger for configurable debug messages
logger = logging.getLogger(__name__)


class IdleDetector:
    """Detects when the system has been idle for a configurable period."""

    def __init__(self, idle_threshold: int = 900, start_listeners: bool = True) -> None:
        """Initialize idle detector.

        Args:
            idle_threshold: Seconds before idle (default: 15m)
            start_listeners: Whether to start pynput listeners (default: True)
        """
        self.idle_threshold = idle_threshold
        self.last_activity = datetime.now()
        self._activity_lock = threading.Lock()
        self._mouse_listener: mouse.Listener | None = None
        self._keyboard_listener: keyboard.Listener | None = None

        if start_listeners:
            self._setup_listeners()

        logger.debug(
            f"IdleDetector initialized. [threshold={idle_threshold}s, listeners={start_listeners}]"
        )

    def _setup_listeners(self) -> None:
        """Set up and start pynput listeners."""
        # Set up pynput listeners for mouse and keyboard activity
        self._mouse_listener = mouse.Listener(
            on_move=self._on_activity,
            on_click=self._on_activity,
            on_scroll=self._on_activity,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_activity, on_release=self._on_activity
        )

        # Start listeners
        self._mouse_listener.start()
        self._keyboard_listener.start()

    @property
    def is_idle(self) -> bool:
        """Check if system has been idle long enough."""
        with self._activity_lock:
            elapsed = (datetime.now() - self.last_activity).total_seconds()
            return elapsed > self.idle_threshold

    def stop(self) -> None:
        """Stop pynput listeners for clean shutdown."""
        if self._mouse_listener is not None:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._keyboard_listener is not None:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        logger.debug("IdleDetector stopped")

    def _on_activity(self, *args: Any, **kwargs: Any) -> None:
        """Called when user activity is detected."""
        with self._activity_lock:
            self.last_activity = datetime.now()
        logger.debug(f"Activity detected. [timestamp={self.last_activity}]")
