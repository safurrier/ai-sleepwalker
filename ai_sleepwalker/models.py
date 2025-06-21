"""Shared data models for the sleepwalker system.

Type-safe data structures to replace Dict[str, Any] patterns and provide
clear contracts between components.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class FileSystemDiscovery:
    """A discovered filesystem item during exploration.

    Immutable data structure representing a file or directory found
    during filesystem wandering. Replaces Dict[str, Any] patterns.
    """

    path: Path
    name: str
    discovery_type: str  # "file" or "directory"
    size_bytes: int | None = None  # Only for files
    preview: str | None = None  # Brief content preview for text files
    timestamp: datetime = field(
        default_factory=datetime.now
    )  # When this was discovered

    @property
    def is_file(self) -> bool:
        """Check if this discovery is a file."""
        return self.discovery_type == "file"

    @property
    def is_directory(self) -> bool:
        """Check if this discovery is a directory."""
        return self.discovery_type == "directory"


@dataclass
class ExplorationSession:
    """Represents a complete filesystem exploration session.

    Tracks the session metadata and discovered items in a type-safe way.
    """

    session_id: str
    start_time: datetime
    allowed_directories: list[Path]
    discoveries: list[FileSystemDiscovery]
    end_time: datetime | None = None

    @property
    def duration_seconds(self) -> float | None:
        """Calculate session duration if completed."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time).total_seconds()

    @property
    def discovery_count(self) -> int:
        """Number of items discovered in this session."""
        return len(self.discoveries)

    def add_discovery(self, discovery: FileSystemDiscovery) -> None:
        """Add a new discovery to this session."""
        self.discoveries.append(discovery)

    def complete_session(self) -> None:
        """Mark the exploration session as completed."""
        self.end_time = datetime.now()


@dataclass
class IdleState:
    """Represents the current idle state of the system."""

    is_idle: bool
    last_activity_time: datetime
    idle_duration_seconds: float
    threshold_seconds: int

    @property
    def time_until_idle(self) -> float:
        """Seconds remaining until system is considered idle."""
        if self.is_idle:
            return 0.0
        return max(0.0, self.threshold_seconds - self.idle_duration_seconds)


@dataclass
class SleepPreventionState:
    """Tracks the current state of sleep prevention."""

    is_active: bool
    activation_count: int
    last_activated: datetime | None = None
    last_deactivated: datetime | None = None

    def activate(self) -> None:
        """Record sleep prevention activation."""
        self.is_active = True
        self.activation_count += 1
        self.last_activated = datetime.now()

    def deactivate(self) -> None:
        """Record sleep prevention deactivation."""
        self.is_active = False
        self.last_deactivated = datetime.now()
