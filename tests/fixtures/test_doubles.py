"""Test doubles for sleepwalker components.

These are proper fakes and stubs that implement the same interfaces as real
components but provide predictable behavior for testing, following testing
domain guidance to avoid excessive mocking.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_sleepwalker.constants import DiscoveryType
from ai_sleepwalker.experiences.base import (
    ExperienceResult,
    ExperienceType,
    Observation,
)
from ai_sleepwalker.models import FileSystemDiscovery


class FakeIdleDetector:
    """Test double for idle detection that provides predictable behavior."""

    def __init__(self, is_idle: bool = False) -> None:
        self._is_idle = is_idle
        self.activity_events: list[str] = []

    @property
    def is_idle(self) -> bool:
        return self._is_idle

    def set_idle(self, idle: bool) -> None:
        """Control idle state for testing."""
        self._is_idle = idle
        self.activity_events.append(f"idle_set_to_{idle}")


class FakeSleepPreventer:
    """Test double for sleep prevention that tracks prevention state."""

    def __init__(self) -> None:
        self.is_preventing_sleep = False
        self.prevention_count = 0

    @asynccontextmanager
    async def prevent_sleep(self) -> AsyncGenerator[None, None]:
        """Context manager that tracks sleep prevention."""
        self.is_preventing_sleep = True
        self.prevention_count += 1
        try:
            yield
        finally:
            self.is_preventing_sleep = False


class InMemoryFilesystemExplorer:
    """Test double that simulates filesystem exploration without file I/O."""

    def __init__(self, discoveries: list[FileSystemDiscovery] | None = None) -> None:
        self._discoveries = discoveries or []
        self._index = 0
        self.wander_count = 0

    def wander(self) -> FileSystemDiscovery | None:
        """Return next discovery or None if exhausted."""
        self.wander_count += 1

        if self._index >= len(self._discoveries):
            return None

        result = self._discoveries[self._index]
        self._index += 1
        return result

    def add_discovery(self, discovery: FileSystemDiscovery) -> None:
        """Add a discovery to be returned by future wander() calls."""
        self._discoveries.append(discovery)


class FakeExperienceCollector:
    """Test double that tracks observation collection behavior."""

    def __init__(self) -> None:
        self.observations: list[Observation] = []
        self.discovery_count = 0

    def add_observation(self, discovery: FileSystemDiscovery) -> None:
        """Track observation creation without complex logic."""
        self.discovery_count += 1
        observation = Observation(
            timestamp=discovery.timestamp,
            path=str(discovery.path),
            name=discovery.name,
            type=discovery.discovery_type,
            size_bytes=discovery.size_bytes,
            preview=discovery.preview,
            brief_note=f"Test observation {self.discovery_count}",
        )
        self.observations.append(observation)

    def get_observations(self) -> list[Observation]:
        """Return collected observations."""
        return self.observations


class FakeExperienceSynthesizer:
    """Test double that creates predictable experience results."""

    def __init__(self, experience_type: ExperienceType = ExperienceType.DREAM) -> None:
        self._experience_type = experience_type
        self.synthesize_count = 0

    @property
    def experience_type(self) -> ExperienceType:
        return self._experience_type

    async def synthesize(self, observations: list[Observation]) -> ExperienceResult:
        """Create test experience result with predictable content."""
        self.synthesize_count += 1

        now = datetime.now()
        start_time = observations[0].timestamp if observations else now

        # Create predictable content based on observation count
        content = self._generate_test_content(len(observations))

        return ExperienceResult(
            experience_type=self._experience_type,
            session_start=start_time,
            session_end=now,
            total_observations=len(observations),
            content=content,
            metadata={"test_synthesizer_call": self.synthesize_count},
            file_extension=".md",
        )

    def _generate_test_content(self, observation_count: int) -> str:
        """Generate test content that avoids brittle string matching."""
        lines = [
            "# Test Dream Session",
            "",
            f"Session with {observation_count} observations",
            "",
            "## Dream Content",
            "",
            "Test dream narrative generated for testing purposes.",
            "",
            f"*Synthesizer call #{self.synthesize_count}*",
        ]
        return "\n".join(lines)


class FakeLLMClient:
    """Test double for LLM client that provides controlled responses."""

    def __init__(self, responses: list[str] | None = None) -> None:
        self.responses = responses or ["Test LLM response for dream synthesis."]
        self.call_count = 0
        self.requests: list[dict[str, Any]] = []

    async def acompletion(self, **kwargs: Any) -> dict[str, Any]:
        """Return predictable LLM response."""
        self.requests.append(kwargs)
        response_text = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1

        return {"choices": [{"message": {"content": response_text}}]}


def create_test_discoveries() -> list[FileSystemDiscovery]:
    """Create standard test discoveries for filesystem exploration."""
    return [
        FileSystemDiscovery(
            path=Path("/test/documents/notes.txt"),
            name="notes.txt",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=156,
            preview="Test file content",
        ),
        FileSystemDiscovery(
            path=Path("/test/photos"),
            name="photos",
            discovery_type=DiscoveryType.DIRECTORY.value,
        ),
        FileSystemDiscovery(
            path=Path("/test/projects/readme.md"),
            name="readme.md",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=1024,
        ),
    ]


def create_temp_output_structure(base_dir: Path) -> Path:
    """Create a temporary directory structure for testing output."""
    output_dir = base_dir / "sleepwalker_output"
    output_dir.mkdir(exist_ok=True)
    return output_dir
