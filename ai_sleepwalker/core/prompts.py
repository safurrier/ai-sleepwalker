"""Prompt management for LLM dream generation."""

from ..experiences.base import Observation

DREAM_PROMPT_TEMPLATE = """Digital sleepwalking. These files trigger dream memories:

{observations}

Write 2 tiny paragraphs. Each 2-3 sentences max. Use content previews for surreal
connections."""


def format_dream_prompt(observations: list[Observation]) -> str:
    """Format observations into dream prompt."""
    if not observations:
        return DREAM_PROMPT_TEMPLATE.format(observations="(No recent discoveries)")

    obs_details = []
    for obs in observations:
        detail = f"- {obs.type.title()}: {obs.name}"

        if obs.size_bytes is not None:
            detail += f" ({obs.size_bytes} bytes)"
        if hasattr(obs, "timestamp") and obs.timestamp:
            detail += f" modified {obs.timestamp.strftime('%Y-%m-%d')}"

        # Include preview content if available
        if obs.preview:
            detail += f"\n  Content preview: {obs.preview}"

        obs_details.append(detail)

    return DREAM_PROMPT_TEMPLATE.format(observations="\n".join(obs_details))
