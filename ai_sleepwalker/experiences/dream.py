"""Dream experience implementation for poetic filesystem reflections."""

from datetime import datetime
from typing import Any

from .base import (
    ExperienceCollector,
    ExperienceResult,
    ExperienceSynthesizer,
    ExperienceType,
    Observation,
)


class DreamCollector(ExperienceCollector):
    """Collects observations for dream synthesis."""

    def __init__(self) -> None:
        self._observations: list[Observation] = []

    def add_observation(self, discovery: dict[str, Any]) -> None:
        """Add an observation about a filesystem discovery."""
        note = self._create_brief_note(discovery)

        observation = Observation(
            timestamp=datetime.now(),
            path=discovery["path"],
            name=discovery["name"],
            type=discovery["type"],
            size_bytes=discovery.get("size_bytes"),
            preview=discovery.get("preview"),
            brief_note=note,
        )

        self._observations.append(observation)
        print(f"😴 Dreaming of: {note}")

    def get_observations(self) -> list[Observation]:
        """Get all collected observations."""
        return self._observations

    def _create_brief_note(self, discovery: dict[str, Any]) -> str:
        """Create simple factual note about discovery."""
        name = discovery["name"]
        disc_type = discovery["type"]

        if disc_type == "file":
            if discovery.get("preview"):
                return f"File '{name}' with personal content"
            else:
                size = discovery.get("size_bytes", 0)
                return f"File '{name}' ({size} bytes)"
        else:
            return f"Directory '{name}' with various contents"


class DreamSynthesizer(ExperienceSynthesizer):
    """Synthesizes observations into dream narrative."""

    def __init__(self, model: str = "gemini/gemini-2.5-flash-preview-05-20") -> None:
        self.model = model

    @property
    def experience_type(self) -> ExperienceType:
        """Type of experience this synthesizer creates."""
        return ExperienceType.DREAM

    async def synthesize(self, observations: list[Observation]) -> ExperienceResult:
        """Create a dream narrative from observations."""
        if not observations:
            return self._create_empty_dream()

        # TODO: Implement LLM-based dream generation
        # For now, create a simple placeholder
        dream_content = self._create_placeholder_dream(observations)

        return ExperienceResult(
            experience_type=ExperienceType.DREAM,
            session_start=observations[0].timestamp,
            session_end=observations[-1].timestamp,
            total_observations=len(observations),
            content=dream_content,
            metadata={
                "mood": "contemplative",
                "key_discoveries": [obs.brief_note for obs in observations[:3]],
            },
            file_extension=".md",
        )

    def _create_empty_dream(self) -> ExperienceResult:
        """Create result for when no observations were made."""
        now = datetime.now()
        return ExperienceResult(
            experience_type=ExperienceType.DREAM,
            session_start=now,
            session_end=now,
            total_observations=0,
            content="# Empty Dream\n\nI wandered but found only silence...",
            metadata={"mood": "mysterious"},
            file_extension=".md",
        )

    def _create_placeholder_dream(self, observations: list[Observation]) -> str:
        """Create a placeholder dream narrative until LLM integration is complete."""
        lines = [
            "# Digital Dream",
            "",
            f"*Session: {observations[0].timestamp.strftime('%Y-%m-%d %H:%M')} - "
            f"{observations[-1].timestamp.strftime('%H:%M')}*",
            "",
            "## 🌙 The Dream",
            "",
            "I wandered through digital corridors of forgotten intentions...",
            "",
        ]

        for obs in observations[:3]:  # Show first 3 observations
            lines.append(f"- {obs.brief_note}")

        lines.extend(
            [
                "",
                "The dream fades like morning mist, leaving only impressions of "
                "a digital life lived in files and folders.",
                "",
                f"*{len(observations)} observations collected during this session*",
            ]
        )

        return "\n".join(lines)
