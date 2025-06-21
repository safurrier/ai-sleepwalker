"""Base classes and types for the experience framework."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ExperienceType(Enum):
    """Available experience modes for the sleepwalker."""

    DREAM = "dream"
    ADVENTURE = "adventure"
    SCRAPBOOK = "scrapbook"
    JOURNAL = "journal"


@dataclass
class Observation:
    """Raw observation during filesystem exploration."""

    timestamp: datetime
    path: str
    name: str
    type: str  # "file" or "directory"
    size_bytes: int | None = None  # Only for files
    preview: str | None = None  # Brief content for text files
    brief_note: str = ""  # Simple human description


@dataclass
class ExperienceResult:
    """Final result after experience synthesis."""

    experience_type: ExperienceType
    session_start: datetime
    session_end: datetime
    total_observations: int
    content: str  # The main narrative/output
    metadata: dict[str, Any]  # Experience-specific data
    file_extension: str  # .md, .html, .json, etc.


class ExperienceCollector(ABC):
    """Base class for collecting observations during exploration."""

    @abstractmethod
    def add_observation(self, discovery: dict[str, Any]) -> None:
        """Process and store an observation."""
        pass

    @abstractmethod
    def get_observations(self) -> list[Observation]:
        """Get all collected observations."""
        pass


class ExperienceSynthesizer(ABC):
    """Base class for synthesizing observations into final experience."""

    @abstractmethod
    async def synthesize(self, observations: list[Observation]) -> ExperienceResult:
        """Create final experience from observations."""
        pass

    @property
    @abstractmethod
    def experience_type(self) -> ExperienceType:
        """Type of experience this synthesizer creates."""
        pass
