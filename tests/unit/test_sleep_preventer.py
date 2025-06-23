"""Unit tests for SleepPreventer component.

Following testing conventions:
- Test behavior, not implementation details
- Use test doubles instead of mocking wakepy directly
- Table-driven testing for multiple scenarios
- Focus on observable outcomes
"""

import asyncio
import logging
from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest

from ai_sleepwalker.core.sleep_preventer import SleepPreventer


@dataclass
class WakepyTestCase:
    """Test case for wakepy behavior scenarios."""

    name: str
    active: bool
    active_method: str | None
    should_log_warning: bool
    should_log_info: bool


class TestSleepPreventerInitialization:
    """Test suite for SleepPreventer initialization and basic state."""

    @pytest.fixture
    def sleep_preventer(self) -> SleepPreventer:
        """Provides clean SleepPreventer instance for testing."""
        return SleepPreventer()

    @pytest.mark.unit
    def test_initializes_with_inactive_state(
        self, sleep_preventer: SleepPreventer
    ) -> None:
        """SleepPreventer starts in inactive state after creation."""
        assert not sleep_preventer.is_preventing_sleep
        assert sleep_preventer.prevention_count == 0
        assert sleep_preventer._current_mode is None

    @pytest.mark.unit
    def test_provides_expected_interface(self, sleep_preventer: SleepPreventer) -> None:
        """SleepPreventer provides expected interface for other components."""
        # Should have required properties and methods
        assert hasattr(sleep_preventer, "is_preventing_sleep")
        assert hasattr(sleep_preventer, "prevention_count")
        assert hasattr(sleep_preventer, "prevent_sleep")

        # Properties should return expected types
        assert isinstance(sleep_preventer.is_preventing_sleep, bool)
        assert isinstance(sleep_preventer.prevention_count, int)
        assert callable(sleep_preventer.prevent_sleep)


class TestSleepPreventionBehavior:
    """Test suite for sleep prevention context manager behavior."""

    @pytest.fixture
    def sleep_preventer(self) -> SleepPreventer:
        """Provides clean SleepPreventer instance for testing."""
        return SleepPreventer()

    # Table-driven testing for various wakepy scenarios
    wakepy_test_cases = [
        WakepyTestCase(
            name="successful_prevention",
            active=True,
            active_method="caffeinate",
            should_log_warning=False,
            should_log_info=True,
        ),
        WakepyTestCase(
            name="failed_prevention",
            active=False,
            active_method=None,
            should_log_warning=True,
            should_log_info=False,
        ),
        WakepyTestCase(
            name="windows_method",
            active=True,
            active_method="SetThreadExecutionState",
            should_log_warning=False,
            should_log_info=True,
        ),
    ]

    @pytest.mark.unit
    @pytest.mark.parametrize("case", wakepy_test_cases)
    async def test_prevent_sleep_context_manager_behavior(
        self, sleep_preventer: SleepPreventer, case: WakepyTestCase, caplog
    ) -> None:
        """SleepPreventer context manager handles various wakepy scenarios correctly."""
        # Create mock wakepy mode object
        mock_mode = Mock()
        mock_mode.active = case.active
        mock_mode.active_method = case.active_method

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            with caplog.at_level(logging.INFO):
                async with sleep_preventer.prevent_sleep():
                    # Act & Assert - Check state during prevention
                    assert sleep_preventer.is_preventing_sleep is True
                    assert sleep_preventer.prevention_count == 1
                    assert sleep_preventer._current_mode == mock_mode

            # Assert - Check state after prevention ends
            assert sleep_preventer.is_preventing_sleep is False
            assert sleep_preventer._current_mode is None
            assert sleep_preventer.prevention_count == 1  # Count persists

            # Assert - Check logging behavior
            log_messages = [record.message for record in caplog.records]

            if case.should_log_warning:
                assert any(
                    "Could not prevent system sleep" in msg for msg in log_messages
                )
            if case.should_log_info:
                assert any(case.active_method in msg for msg in log_messages)

    @pytest.mark.unit
    async def test_prevention_count_increments_with_multiple_uses(
        self, sleep_preventer: SleepPreventer
    ) -> None:
        """Prevention count tracks total number of prevention sessions."""
        mock_mode = Mock()
        mock_mode.active = True
        mock_mode.active_method = "test_method"

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            # First prevention session
            async with sleep_preventer.prevent_sleep():
                assert sleep_preventer.prevention_count == 1

            # Second prevention session
            async with sleep_preventer.prevent_sleep():
                assert sleep_preventer.prevention_count == 2

            # Count persists after sessions end
            assert sleep_preventer.prevention_count == 2

    @pytest.mark.unit
    async def test_context_manager_cleans_up_on_exception(
        self, sleep_preventer: SleepPreventer
    ) -> None:
        """Context manager properly cleans up state even when exceptions occur."""
        mock_mode = Mock()
        mock_mode.active = True
        mock_mode.active_method = "test_method"

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            with pytest.raises(ValueError, match="test exception"):
                async with sleep_preventer.prevent_sleep():
                    assert sleep_preventer.is_preventing_sleep is True
                    raise ValueError("test exception")

            # State should be cleaned up despite exception
            assert sleep_preventer.is_preventing_sleep is False
            assert sleep_preventer._current_mode is None

    @pytest.mark.unit
    async def test_concurrent_prevention_sessions_not_supported(
        self, sleep_preventer: SleepPreventer
    ) -> None:
        """Multiple concurrent prevention sessions behave predictably."""
        mock_mode = Mock()
        mock_mode.active = True
        mock_mode.active_method = "test_method"

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            # Start first session
            async with sleep_preventer.prevent_sleep():
                assert sleep_preventer.is_preventing_sleep is True
                assert sleep_preventer.prevention_count == 1

                # Nested session (should work but overwrite state)
                async with sleep_preventer.prevent_sleep():
                    assert sleep_preventer.is_preventing_sleep is True
                    assert sleep_preventer.prevention_count == 2

                # Back to outer session
                assert sleep_preventer.is_preventing_sleep is True

            # All sessions ended
            assert sleep_preventer.is_preventing_sleep is False


class TestWakepyIntegration:
    """Test suite for wakepy library integration and error handling."""

    @pytest.fixture
    def sleep_preventer(self) -> SleepPreventer:
        """Provides clean SleepPreventer instance for testing."""
        return SleepPreventer()

    @pytest.mark.unit
    async def test_wakepy_called_with_correct_parameters(
        self, sleep_preventer: SleepPreventer
    ) -> None:
        """SleepPreventer calls wakepy with correct configuration."""
        mock_mode = Mock()
        mock_mode.active = True
        mock_mode.active_method = "test_method"

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            async with sleep_preventer.prevent_sleep():
                pass

            # Verify wakepy was called with warning on failure
            mock_keep.assert_called_once_with(on_fail="warn")

    @pytest.mark.unit
    async def test_wakepy_exception_handling(
        self, sleep_preventer: SleepPreventer, caplog
    ) -> None:
        """SleepPreventer handles wakepy exceptions gracefully."""
        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.side_effect = RuntimeError("Wakepy failed")

            with caplog.at_level(logging.ERROR):
                with pytest.raises(RuntimeError, match="Wakepy failed"):
                    async with sleep_preventer.prevent_sleep():
                        pass

            # Should log error and clean up state
            assert any(
                "Sleep prevention failed" in record.message for record in caplog.records
            )
            assert sleep_preventer.is_preventing_sleep is False


class TestLoggingBehavior:
    """Test suite for logging and debugging functionality."""

    @pytest.fixture
    def sleep_preventer(self) -> SleepPreventer:
        """Provides clean SleepPreventer instance for testing."""
        return SleepPreventer()

    @pytest.mark.unit
    async def test_logs_successful_activation(
        self, sleep_preventer: SleepPreventer, caplog
    ) -> None:
        """SleepPreventer logs successful sleep prevention activation."""
        mock_mode = Mock()
        mock_mode.active = True
        mock_mode.active_method = "caffeinate"

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            with caplog.at_level(logging.INFO):
                async with sleep_preventer.prevent_sleep():
                    pass

            log_messages = [record.message for record in caplog.records]
            assert any(
                "Sleep prevention active using: caffeinate" in msg
                for msg in log_messages
            )

    @pytest.mark.unit
    async def test_logs_deactivation_debug(
        self, sleep_preventer: SleepPreventer, caplog
    ) -> None:
        """SleepPreventer logs deactivation at debug level."""
        mock_mode = Mock()
        mock_mode.active = True
        mock_mode.active_method = "test_method"

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            with caplog.at_level(logging.DEBUG):
                async with sleep_preventer.prevent_sleep():
                    pass

            debug_messages = [
                record.message
                for record in caplog.records
                if record.levelno == logging.DEBUG
            ]
            assert any("Sleep prevention deactivated" in msg for msg in debug_messages)


class TestAsyncBehavior:
    """Test suite for async context manager behavior and coroutine handling."""

    @pytest.fixture
    def sleep_preventer(self) -> SleepPreventer:
        """Provides clean SleepPreventer instance for testing."""
        return SleepPreventer()

    @pytest.mark.unit
    async def test_works_with_async_operations(
        self, sleep_preventer: SleepPreventer
    ) -> None:
        """SleepPreventer context manager works correctly with async operations."""
        mock_mode = Mock()
        mock_mode.active = True
        mock_mode.active_method = "test_method"

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            async with sleep_preventer.prevent_sleep():
                # Simulate async work
                await asyncio.sleep(0.01)
                result = await self._async_helper()
                assert result == "async_complete"

            assert sleep_preventer.is_preventing_sleep is False

    async def _async_helper(self) -> str:
        """Helper method for testing async operations."""
        await asyncio.sleep(0.01)
        return "async_complete"

    @pytest.mark.unit
    async def test_multiple_concurrent_async_operations(
        self, sleep_preventer: SleepPreventer
    ) -> None:
        """SleepPreventer handles multiple concurrent async operations."""
        mock_mode = Mock()
        mock_mode.active = True
        mock_mode.active_method = "test_method"

        with patch("ai_sleepwalker.core.sleep_preventer.keep.running") as mock_keep:
            mock_keep.return_value.__enter__.return_value = mock_mode
            mock_keep.return_value.__exit__.return_value = None

            async with sleep_preventer.prevent_sleep():
                # Run multiple async operations concurrently
                tasks = [
                    asyncio.create_task(self._async_helper()),
                    asyncio.create_task(self._async_helper()),
                    asyncio.create_task(self._async_helper()),
                ]

                results = await asyncio.gather(*tasks)
                assert all(result == "async_complete" for result in results)

            assert sleep_preventer.is_preventing_sleep is False
