"""Factory for creating experience collectors and synthesizers."""

from typing import Any

from .base import ExperienceCollector, ExperienceSynthesizer, ExperienceType


class ExperienceFactory:
    """Factory for creating experience collectors and synthesizers."""

    @staticmethod
    def create_collector(experience_type: ExperienceType) -> ExperienceCollector:
        """Create appropriate collector for experience type."""
        match experience_type:
            case ExperienceType.DREAM:
                from .dream import DreamCollector

                return DreamCollector()
            case ExperienceType.ADVENTURE:
                raise NotImplementedError("Adventure mode coming soon!")
            case ExperienceType.SCRAPBOOK:
                raise NotImplementedError("Scrapbook mode coming soon!")
            case _:
                raise ValueError(f"Unknown experience type: {experience_type}")

    @staticmethod
    def create_synthesizer(
        experience_type: ExperienceType, **kwargs: Any
    ) -> ExperienceSynthesizer:
        """Create appropriate synthesizer for experience type."""
        match experience_type:
            case ExperienceType.DREAM:
                from .dream import DreamSynthesizer

                return DreamSynthesizer(**kwargs)
            case ExperienceType.ADVENTURE:
                raise NotImplementedError("Adventure mode coming soon!")
            case ExperienceType.SCRAPBOOK:
                raise NotImplementedError("Scrapbook mode coming soon!")
            case _:
                raise ValueError(f"Unknown experience type: {experience_type}")
