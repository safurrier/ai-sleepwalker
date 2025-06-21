"""Cross-platform sleep prevention during exploration sessions."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any


class SleepPreventer:
    """Prevents computer from going to sleep during exploration."""

    def __init__(self) -> None:
        """Initialize sleep preventer."""
        self.is_active = False
        self._keep_awake: Any = None

    @asynccontextmanager
    async def prevent_sleep(self) -> AsyncGenerator[None, None]:
        """Context manager for sleep prevention during exploration."""
        try:
            # TODO: Implement actual sleep prevention using wakepy
            # For now, just set the flag
            self.is_active = True
            yield
        finally:
            self.is_active = False
            if self._keep_awake:
                # TODO: Clean up wakepy resources
                pass
