"""Tests for LLM client functionality."""

# ruff: noqa: E501
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from ai_sleepwalker.core.llm_client import (
    LLMAPIError,
    LLMClient,
    LLMConfig,
)
from ai_sleepwalker.experiences.base import ExperienceResult, Observation


@dataclass
class MockLLMResponse:
    """Mock response from LLM API."""

    choices: list[Any]
    usage: Any = None

    def __post_init__(self) -> None:
        if self.usage is None:
            self.usage = MockUsage()


@dataclass
class MockChoice:
    """Mock choice from LLM response."""

    message: Any

    def __post_init__(self) -> None:
        if not hasattr(self.message, "content"):
            self.message = MockMessage(self.message)


@dataclass
class MockMessage:
    """Mock message from LLM choice."""

    content: str


@dataclass
class MockUsage:
    """Mock usage statistics."""

    total_tokens: int = 150
    prompt_tokens: int = 100
    completion_tokens: int = 50


class TestLLMConfig:
    """Test suite for LLM configuration."""

    def test_llm_config_defaults(self) -> None:
        """Test LLMConfig has correct default values."""
        config = LLMConfig()

        assert config.model == "gemini/gemini-2.5-flash-preview"
        assert config.timeout == 15
        assert config.max_tokens is None
        assert config.temperature is None

    def test_llm_config_custom_values(self) -> None:
        """Test LLMConfig accepts custom configuration."""
        config = LLMConfig(
            model="gpt-4o-mini",
            timeout=15,
            max_tokens=500,
            temperature=0.7,
            fallback_models=["gemini/gemini-2.5-flash-preview"],
        )

        assert config.model == "gpt-4o-mini"
        assert config.timeout == 15
        assert config.max_tokens == 500
        assert config.temperature == 0.7
        assert config.fallback_models == ["gemini/gemini-2.5-flash-preview"]

    def test_llm_config_fallback_models_default(self) -> None:
        """Test LLMConfig sets default fallback models."""
        config = LLMConfig()

        assert config.fallback_models == ["gpt-4o-mini"]


class TestLLMClient:
    """Test suite for LLM client functionality."""

    @pytest.fixture
    def llm_config(self) -> LLMConfig:
        """Provide test LLM configuration."""
        return LLMConfig(model="gemini/gemini-2.5-flash-preview", timeout=10)

    @pytest.fixture
    def sample_observations(self) -> list[Observation]:
        """Provide test observations."""
        return [
            Observation(
                timestamp=datetime(2025, 1, 15, 10, 30),
                path="/home/user/document.txt",
                name="document.txt",
                type="file",
                size_bytes=1024,
                preview="Sample document content",
            ),
            Observation(
                timestamp=datetime(2025, 1, 15, 11, 45),
                path="/tmp/cache",
                name="cache",
                type="directory",
            ),
        ]

    @pytest.fixture
    def mock_llm_response(self) -> MockLLMResponse:
        """Provide mock LLM response."""
        return MockLLMResponse(
            choices=[
                MockChoice(MockMessage("A surreal dream about digital wandering..."))
            ]
        )

    def test_llm_client_initialization_default_config(self) -> None:
        """Test LLMClient initializes with default configuration."""
        client = LLMClient()

        assert client.config is not None
        assert isinstance(client.config, LLMConfig)
        assert client.config.model == "gemini/gemini-2.5-flash-preview"

    def test_llm_client_initialization_custom_config(
        self, llm_config: LLMConfig
    ) -> None:
        """Test LLMClient initializes with custom configuration."""
        client = LLMClient(llm_config)

        assert client.config == llm_config
        assert client.config.timeout == 10

    @pytest.mark.asyncio
    async def test_generate_dream_success(
        self,
        llm_config: LLMConfig,
        sample_observations: list[Observation],
        mock_llm_response: MockLLMResponse,
    ) -> None:
        """Test successful dream generation from observations."""
        client = LLMClient(llm_config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_llm_response

            result = await client.generate_dream(sample_observations)

            assert isinstance(result, ExperienceResult)
            assert result.content == "A surreal dream about digital wandering..."
            assert "model" in result.metadata
            assert result.metadata["model"] == llm_config.model

    @pytest.mark.asyncio
    async def test_generate_dream_includes_performance_timing(
        self,
        llm_config: LLMConfig,
        sample_observations: list[Observation],
        mock_llm_response: MockLLMResponse,
    ) -> None:
        """Test that dream generation includes performance timing."""
        client = LLMClient(llm_config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_llm_response

            result = await client.generate_dream(sample_observations)

            assert "duration_seconds" in result.metadata
            assert isinstance(result.metadata["duration_seconds"], float)
            assert result.metadata["duration_seconds"] >= 0
            assert "observation_count" in result.metadata
            assert result.metadata["observation_count"] == len(sample_observations)

    @pytest.mark.asyncio
    async def test_generate_dream_calls_litellm_with_correct_params(
        self,
        llm_config: LLMConfig,
        sample_observations: list[Observation],
        mock_llm_response: MockLLMResponse,
    ) -> None:
        """Test that LLM client calls litellm with correct parameters."""
        client = LLMClient(llm_config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_llm_response

            await client.generate_dream(sample_observations)

            mock_completion.assert_called_once()
            call_args = mock_completion.call_args

            assert call_args.kwargs["model"] == llm_config.model
            assert call_args.kwargs["timeout"] == llm_config.timeout
            assert "messages" in call_args.kwargs
            assert len(call_args.kwargs["messages"]) == 1
            assert call_args.kwargs["messages"][0]["role"] == "user"
            assert "content" in call_args.kwargs["messages"][0]

    @pytest.mark.asyncio
    async def test_generate_dream_with_optional_params(
        self, sample_observations: list[Observation], mock_llm_response: MockLLMResponse
    ) -> None:
        """Test that optional parameters are included when configured."""
        config = LLMConfig(
            model="gpt-4o-mini", timeout=15, max_tokens=500, temperature=0.8
        )
        client = LLMClient(config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_llm_response

            await client.generate_dream(sample_observations)

            call_args = mock_completion.call_args
            assert call_args.kwargs["max_tokens"] == 500
            assert call_args.kwargs["temperature"] == 0.8

    @pytest.mark.asyncio
    async def test_generate_dream_excludes_none_optional_params(
        self, sample_observations: list[Observation], mock_llm_response: MockLLMResponse
    ) -> None:
        """Test that None optional parameters are excluded from API call."""
        config = LLMConfig(
            model="gemini/gemini-2.5-flash-preview",
            timeout=10,
            max_tokens=None,
            temperature=None,
        )
        client = LLMClient(config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_llm_response

            await client.generate_dream(sample_observations)

            call_args = mock_completion.call_args
            assert "max_tokens" not in call_args.kwargs
            assert "temperature" not in call_args.kwargs

    @pytest.mark.asyncio
    async def test_generate_dream_uses_prompt_formatting(
        self,
        llm_config: LLMConfig,
        sample_observations: list[Observation],
        mock_llm_response: MockLLMResponse,
    ) -> None:
        """Test that dream generation uses external prompt formatting."""
        client = LLMClient(llm_config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            with patch(
                "ai_sleepwalker.core.llm_client.format_dream_prompt"
            ) as mock_format:
                mock_format.return_value = "Formatted test prompt"
                mock_completion.return_value = mock_llm_response

                await client.generate_dream(sample_observations)

                mock_format.assert_called_once_with(sample_observations)
                call_args = mock_completion.call_args
                assert (
                    call_args.kwargs["messages"][0]["content"]
                    == "Formatted test prompt"
                )

    @pytest.mark.asyncio
    async def test_generate_dream_with_empty_observations(
        self, llm_config: LLMConfig, mock_llm_response: MockLLMResponse
    ) -> None:
        """Test dream generation with no observations."""
        client = LLMClient(llm_config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_llm_response

            result = await client.generate_dream([])

            assert isinstance(result, ExperienceResult)
            assert result.metadata["observation_count"] == 0

    @pytest.mark.asyncio
    async def test_generate_dream_api_failure_raises_exception(
        self, llm_config: LLMConfig, sample_observations: list[Observation]
    ) -> None:
        """Test that API failures raise appropriate exceptions."""
        client = LLMClient(llm_config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.side_effect = Exception("API Error")

            with pytest.raises(LLMAPIError, match="All LLM providers failed"):
                await client.generate_dream(sample_observations)

    @pytest.mark.asyncio
    async def test_generate_dream_fallback_models(
        self, sample_observations: list[Observation], mock_llm_response: MockLLMResponse
    ) -> None:
        """Test fallback to secondary models when primary fails."""
        config = LLMConfig(
            model="gemini/gemini-2.5-flash-preview", fallback_models=["gpt-4o-mini"]
        )
        client = LLMClient(config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            # Primary model fails 3 times (retry exhausted), fallback succeeds
            primary_failure = Exception("Primary model failed")
            mock_completion.side_effect = [
                primary_failure,
                primary_failure,
                primary_failure,  # 3 retries for primary
                mock_llm_response,  # Fallback succeeds
            ]

            result = await client.generate_dream(sample_observations)

            assert isinstance(result, ExperienceResult)
            assert result.metadata["model"] == "gpt-4o-mini"  # Should use fallback
            assert mock_completion.call_count == 4  # 3 retries + 1 fallback

    @pytest.mark.asyncio
    async def test_generate_dream_enhanced_metadata(
        self,
        llm_config: LLMConfig,
        sample_observations: list[Observation],
        mock_llm_response: MockLLMResponse,
    ) -> None:
        """Test that enhanced metadata is included in results."""
        mock_llm_response.usage.total_tokens = 250
        mock_llm_response.usage.prompt_tokens = 150
        mock_llm_response.usage.completion_tokens = 100

        client = LLMClient(llm_config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = mock_llm_response

            result = await client.generate_dream(sample_observations)

            metadata = result.metadata
            assert "total_tokens" in metadata
            assert "prompt_tokens" in metadata
            assert "completion_tokens" in metadata
            assert "prompt_length" in metadata
            assert "content_length" in metadata
            assert metadata["total_tokens"] == 250

    @pytest.mark.asyncio
    async def test_generate_dream_validation_error(
        self, llm_config: LLMConfig, sample_observations: list[Observation]
    ) -> None:
        """Test handling of empty LLM responses."""
        # Mock response with empty content
        empty_response = MockLLMResponse(
            choices=[MockChoice(MockMessage(""))]  # Empty content
        )

        client = LLMClient(llm_config)

        with patch("litellm.acompletion", new_callable=AsyncMock) as mock_completion:
            mock_completion.return_value = empty_response

            with pytest.raises(LLMAPIError, match="All LLM providers failed"):
                await client.generate_dream(sample_observations)
