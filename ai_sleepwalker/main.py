"""Main sleepwalker orchestrator.

This module will contain the main sleepwalking logic that coordinates
idle detection, sleep prevention, filesystem exploration, and dream generation.
"""

from pathlib import Path


async def start_sleepwalking(
    experience_type: str,
    allowed_dirs: list[str],
    idle_timeout: int,
    output_dir: Path,
) -> None:
    """Start the sleepwalking session.

    This is a stub implementation that will be developed following TDD.
    The E2E tests define the expected behavior.
    """
    # TODO: Implement the main sleepwalker loop
    # This should:
    # 1. Set up idle detection
    # 2. Monitor for idle state
    # 3. Prevent sleep during exploration
    # 4. Explore filesystem safely
    # 5. Generate dreams from observations
    # 6. Save dream logs
    raise NotImplementedError("Main sleepwalker loop not yet implemented")
