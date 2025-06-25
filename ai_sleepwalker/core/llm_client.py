"""LLM client for dream generation."""

import logging
import time
from dataclasses import dataclass
from datetime import datetime

import litellm

# Suppress verbose LiteLLM logging
litellm.suppress_debug_info = True
from tenacity import retry, stop_after_attempt, wait_exponential

from ..experiences.base import ExperienceResult, ExperienceType, Observation
from .prompts import format_dream_prompt

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base exception for LLM-related errors."""

    pass


class LLMAPIError(LLMError):
    """LLM API communication error."""

    pass


class LLMValidationError(LLMError):
    """LLM response validation error."""

    pass


@dataclass
class LLMConfig:
    """Type-safe LLM configuration."""

    model: str = "gemini/gemini-2.5-flash-preview"
    timeout: int = 10
    max_tokens: int | None = None
    temperature: float | None = None
    fallback_models: list[str] | None = None

    def __post_init__(self) -> None:
        """Set up fallback models if not provided."""
        if self.fallback_models is None:
            self.fallback_models = ["gpt-4o-mini"]


class LLMClient:
    """LLM client for dream generation with multi-provider fallback."""

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig()
        self._models_to_try = [self.config.model] + (self.config.fallback_models or [])

    async def generate_dream(self, observations: list[Observation]) -> ExperienceResult:
        """Generate dream narrative from observations with fallback models."""
        start_time = time.time()
        prompt = format_dream_prompt(observations)

        last_error = None
        models_attempted = []

        for model in self._models_to_try:
            try:
                logger.debug(f"Attempting dream generation with model: {model}")
                result = await self._try_model_with_retry(
                    model, prompt, observations, start_time
                )
                logger.debug(
                    f"Dream generation successful with {model}. "
                    f"Duration: {result.metadata['duration_seconds']:.2f}s"
                )
                return result
            except Exception as e:
                last_error = e
                models_attempted.append(model)
                logger.debug(f"Model {model} failed: {e}")
                continue

        # All models failed
        error_msg = (
            f"All LLM providers failed. Attempted: {models_attempted}. "
            f"Last error: {last_error}"
        )
        logger.error(error_msg)
        raise LLMAPIError(error_msg) from last_error

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _try_model_with_retry(
        self,
        model: str,
        prompt: str,
        observations: list[Observation],
        start_time: float,
    ) -> ExperienceResult:
        """Try specific model with retry logic."""
        # Build completion params with only non-None values
        params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "timeout": self.config.timeout,
        }

        # Add optional params only if configured
        if self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens
        if self.config.temperature is not None:
            params["temperature"] = self.config.temperature

        try:
            response = await litellm.acompletion(**params)
        except Exception as e:
            raise LLMAPIError(f"API call failed for model {model}: {e}") from e

        # Validate response
        if not response.choices or not response.choices[0].message.content:
            raise LLMValidationError(f"Empty response from model {model}")

        duration = time.time() - start_time
        content = response.choices[0].message.content.strip()

        # Enhanced metadata with observability
        now = datetime.now()
        metadata = {
            "model": model,
            "duration_seconds": duration,
            "observation_count": len(observations),
            "prompt_length": len(prompt),
            "content_length": len(content),
        }

        # Add token usage if available
        if hasattr(response, "usage") and response.usage:
            metadata.update(
                {
                    "total_tokens": response.usage.total_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }
            )

        return ExperienceResult(
            experience_type=ExperienceType.DREAM,
            session_start=observations[0].timestamp if observations else now,
            session_end=observations[-1].timestamp if observations else now,
            total_observations=len(observations),
            content=content,
            metadata=metadata,
            file_extension=".md",
        )
