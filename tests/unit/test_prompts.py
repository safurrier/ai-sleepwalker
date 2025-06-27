"""Tests for LLM prompt management."""

from datetime import datetime

import pytest

from ai_sleepwalker.core.prompts import DREAM_PROMPT_TEMPLATE, format_dream_prompt
from ai_sleepwalker.experiences.base import Observation


class TestDreamPromptFormatting:
    """Test suite for dream prompt formatting functionality."""

    @pytest.fixture
    def simple_observations(self) -> list[Observation]:
        """Provide simple test observations."""
        return [
            Observation(
                timestamp=datetime(2024, 1, 15, 10, 30),
                path="/home/user/old_photo.jpg",
                name="old_photo.jpg",
                type="file",
                size_bytes=2048,
            ),
            Observation(
                timestamp=datetime(2024, 1, 16, 9, 15),
                path="/tmp/cache",
                name="cache",
                type="directory",
            ),
        ]

    @pytest.fixture
    def complex_observations(self) -> list[Observation]:
        """Provide complex test observations with rich metadata."""
        return [
            Observation(
                timestamp=datetime(2024, 12, 20, 14, 45),
                path="/Users/alex/Documents/draft_novel.txt",
                name="draft_novel.txt",
                type="file",
                size_bytes=50432,
                preview="Chapter 1: It was a dark and stormy night...",
            ),
            Observation(
                timestamp=datetime(2024, 11, 5, 8, 20),
                path="/System/Library/mysterious_folder",
                name="mysterious_folder",
                type="directory",
            ),
            Observation(
                timestamp=datetime(2023, 1, 1, 0, 0),
                path="/var/log/forgotten.log",
                name="forgotten.log",
                type="file",
                size_bytes=0,
            ),
        ]

    def test_prompt_template_exists(self) -> None:
        """Test that dream prompt template constant exists."""
        assert DREAM_PROMPT_TEMPLATE is not None
        assert len(DREAM_PROMPT_TEMPLATE) > 0
        assert isinstance(DREAM_PROMPT_TEMPLATE, str)

    def test_prompt_template_contains_required_elements(self) -> None:
        """Test that prompt template has required narrative elements."""
        template = DREAM_PROMPT_TEMPLATE.lower()

        # Should set surreal/dream context
        assert any(word in template for word in ["dream", "surreal", "sleep"])

        # Should reference digital/filesystem context
        assert any(word in template for word in ["digital", "filesystem", "computer"])

        # Should have placeholder for observations
        assert "{observations}" in DREAM_PROMPT_TEMPLATE

    def test_format_dream_prompt_with_simple_observations(
        self, simple_observations: list[Observation]
    ) -> None:
        """Test formatting prompt with basic observations."""
        prompt = format_dream_prompt(simple_observations)

        assert isinstance(prompt, str)
        assert len(prompt) > len(DREAM_PROMPT_TEMPLATE)

        # Should include observation details
        assert "old_photo.jpg" in prompt
        assert "cache" in prompt
        assert "File:" in prompt
        assert "Directory:" in prompt

    def test_format_dream_prompt_includes_metadata(
        self, simple_observations: list[Observation]
    ) -> None:
        """Test that formatting includes observation metadata."""
        prompt = format_dream_prompt(simple_observations)

        # Should include size information
        assert "2048 bytes" in prompt

        # Should include modification date
        assert "2024-01-15" in prompt

    def test_format_dream_prompt_with_complex_observations(
        self, complex_observations: list[Observation]
    ) -> None:
        """Test formatting with complex observations and metadata."""
        prompt = format_dream_prompt(complex_observations)

        # Should include all file names
        assert "draft_novel.txt" in prompt
        assert "mysterious_folder" in prompt
        assert "forgotten.log" in prompt

        # Should include various metadata
        assert "50432 bytes" in prompt
        assert "0 bytes" in prompt
        assert "2024-12-20" in prompt

    def test_format_dream_prompt_with_empty_observations(self) -> None:
        """Test formatting with no observations."""
        prompt = format_dream_prompt([])

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        # Should still contain the base template text
        assert "digital" in prompt.lower()

    def test_format_dream_prompt_handles_missing_metadata(self) -> None:
        """Test formatting gracefully handles observations without metadata."""
        observations = [
            Observation(
                timestamp=datetime(2024, 1, 1, 12, 0),
                path="/test/file.txt",
                name="file.txt",
                type="file",
            )
        ]

        prompt = format_dream_prompt(observations)
        assert "file.txt" in prompt
        assert isinstance(prompt, str)

    def test_formatted_prompt_structure(
        self, simple_observations: list[Observation]
    ) -> None:
        """Test that formatted prompt maintains expected structure."""
        prompt = format_dream_prompt(simple_observations)

        # Should contain original template content
        assert "Digital sleepwalking" in prompt

        # Should have observations section
        lines = prompt.split("\n")
        observation_lines = [line for line in lines if line.startswith("- ")]
        assert len(observation_lines) == len(simple_observations)

    def test_observation_capitalization_in_prompt(
        self, simple_observations: list[Observation]
    ) -> None:
        """Test that discovery types are properly capitalized in prompt."""
        prompt = format_dream_prompt(simple_observations)

        # type should be capitalized in output
        assert "File:" in prompt
        assert "Directory:" in prompt
        assert "file:" not in prompt
        assert "directory:" not in prompt
