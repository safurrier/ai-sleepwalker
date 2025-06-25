"""Integration tests for LLM functionality."""
import os
from datetime import datetime

import pytest

from ai_sleepwalker.core.llm_client import LLMAPIError, LLMClient, LLMConfig
from ai_sleepwalker.experiences.base import ExperienceResult, Observation


class TestLLMIntegration:
    """Integration tests for LLM client with real API calls."""

    @pytest.fixture
    def integration_config(self) -> LLMConfig:
        """Provide configuration for integration tests."""
        return LLMConfig(
            model="gemini/gemini-2.5-flash-preview",
            timeout=10
        )

    @pytest.fixture
    def test_observations(self) -> list[Observation]:
        """Provide realistic test observations for integration tests."""
        return [
            Observation(
                timestamp=datetime(2024, 3, 15, 14, 30),
                path="/Users/test/Documents/forgotten_diary.txt",
                name="forgotten_diary.txt",
                type="file",
                size_bytes=4096,
                preview="Dear diary, today something strange happened..."
            ),
            Observation(
                timestamp=datetime(2024, 2, 10, 9, 15),
                path="/tmp/mysterious_cache",
                name="mysterious_cache",
                type="directory"
            ),
            Observation(
                timestamp=datetime(2023, 1, 1, 0, 0),
                path="/var/log/ancient.log",
                name="ancient.log",
                type="file",
                size_bytes=0
            )
        ]

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No LLM API keys available"
    )
    async def test_real_dream_generation(
        self, integration_config: LLMConfig, test_observations: list[Observation]
    ) -> None:
        """Test dream generation with real LLM API."""
        client = LLMClient(integration_config)

        result = await client.generate_dream(test_observations)

        assert isinstance(result, ExperienceResult)
        assert len(result.content) > 50  # Substantial content
        assert isinstance(result.content, str)

        # Performance validation
        assert "duration_seconds" in result.metadata
        # Should complete within reasonable time (allowing for API latency)
        assert result.metadata["duration_seconds"] <= 45

        # Content validation
        content_lower = result.content.lower()
        # Should reference some of the observations
        keywords = ["diary", "cache", "log", "forgotten"]
        assert any(word in content_lower for word in keywords)

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No LLM API keys available"
    )
    async def test_dream_generation_with_many_observations(
        self, integration_config: LLMConfig
    ) -> None:
        """Test performance with larger observation sets."""
        # Create many observations to test performance
        observations = []
        for i in range(20):
            observations.append(
                Observation(
                    timestamp=datetime(2024, 1, 1, 12, i),
                    path=f"/test/file_{i}.txt",
                    name=f"file_{i}.txt",
                    type="file" if i % 2 == 0 else "directory",
                    size_bytes=i * 100 if i % 2 == 0 else None
                )
            )

        client = LLMClient(integration_config)

        result = await client.generate_dream(observations)

        assert isinstance(result, ExperienceResult)
        assert result.metadata["observation_count"] == 20

        # Should handle many observations without timeout
        assert result.metadata["duration_seconds"] <= 45

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No LLM API keys available"
    )
    async def test_dream_generation_consistency(
        self, integration_config: LLMConfig, test_observations: list[Observation]
    ) -> None:
        """Test that multiple calls produce valid results."""
        client = LLMClient(integration_config)

        # Generate multiple dreams to test consistency
        results = []
        for _ in range(3):
            result = await client.generate_dream(test_observations)
            results.append(result)

        # All should be successful
        for result in results:
            assert isinstance(result, ExperienceResult)
            assert len(result.content) > 20

        # Results should be different (creative variety)
        contents = [r.content for r in results]
        assert len(set(contents)) > 1  # Not all identical

    @pytest.mark.integration
    async def test_api_key_missing_behavior(
        self, integration_config: LLMConfig, test_observations: list[Observation]
    ) -> None:
        """Test behavior when API keys are not available."""
        # Temporarily remove API keys from environment
        original_gemini = os.environ.get("GEMINI_API_KEY")
        original_openai = os.environ.get("OPENAI_API_KEY")

        if original_gemini:
            del os.environ["GEMINI_API_KEY"]
        if original_openai:
            del os.environ["OPENAI_API_KEY"]

        try:
            client = LLMClient(integration_config)

            # Should raise an exception about missing API key
            with pytest.raises((LLMAPIError, Exception)):
                await client.generate_dream(test_observations)

        finally:
            # Restore original environment
            if original_gemini:
                os.environ["GEMINI_API_KEY"] = original_gemini
            if original_openai:
                os.environ["OPENAI_API_KEY"] = original_openai

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No LLM API keys available"
    )
    async def test_dream_experience_integration(
        self, test_observations: list[Observation]
    ) -> None:
        """Test LLM integration with dream experience framework."""
        from ai_sleepwalker.experiences.dream import DreamSynthesizer

        synthesizer = DreamSynthesizer()

        # This should use the new LLM integration
        result = await synthesizer.synthesize(test_observations)

        assert isinstance(result, ExperienceResult)
        # Without API keys, this will use fallback content
        # With API keys, this would use real LLM content
        assert len(result.content) > 50
