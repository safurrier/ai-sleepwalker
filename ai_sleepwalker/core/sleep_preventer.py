"""Cross-platform sleep prevention during exploration sessions."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from wakepy import keep

logger = logging.getLogger(__name__)


class SleepPreventer:
    """Prevents computer from going to sleep during exploration."""

    def __init__(self) -> None:
        """Initialize sleep preventer."""
        self.is_preventing_sleep = False
        self.prevention_count = 0
        self._current_mode: Any = None
        self._active_sessions = 0

    @asynccontextmanager
    async def prevent_sleep(self) -> AsyncGenerator[None, None]:
        """Context manager for sleep prevention during exploration.

        Uses wakepy to prevent system sleep while allowing screen lock.
        Handles failures gracefully - logs warnings but continues execution.

        Example:
            async with sleep_preventer.prevent_sleep():
                await long_running_exploration()
        """
        try:
            # Only create wakepy context for first session (nested sessions reuse)
            if self._active_sessions == 0:
                with keep.running(on_fail="warn") as mode:
                    self._current_mode = mode
                    self._active_sessions += 1
                    self.is_preventing_sleep = True
                    self.prevention_count += 1

                    if not mode.active:
                        logger.warning(
                            "Could not prevent system sleep. "
                            "Exploration may be interrupted by system suspend."
                        )
                    else:
                        logger.info(
                            f"Sleep prevention active using: {mode.active_method}"
                        )

                    yield
            else:
                # Nested session - just track count, reuse existing wakepy context
                self._active_sessions += 1
                self.prevention_count += 1
                yield

        except Exception as e:
            logger.error(f"Sleep prevention failed: {e}")
            # Continue execution even if sleep prevention fails
            raise
        finally:
            self._active_sessions -= 1
            # Only deactivate when all sessions are done
            if self._active_sessions == 0:
                self.is_preventing_sleep = False
                self._current_mode = None
                logger.debug("Sleep prevention deactivated")
