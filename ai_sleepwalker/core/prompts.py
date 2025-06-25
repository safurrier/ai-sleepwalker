"""Prompt management for LLM dream generation."""

from ..experiences.base import Observation

DREAM_PROMPT_TEMPLATE = """You are experiencing a digital sleepwalk through a computer's filesystem. Create a short, surreal narrative (2-3 paragraphs) based on these discoveries. The dream should feel oddly specific and slightly unsettling, like remembering fragments of a vivid but strange dream.

Recent discoveries during your digital wandering:
{observations}

Generate a narrative that weaves these discoveries into a coherent but surreal story. Focus on the uncanny feeling of discovering forgotten digital artifacts and the strange connections between files and folders."""  # noqa: E501


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

        obs_details.append(detail)

    return DREAM_PROMPT_TEMPLATE.format(observations="\n".join(obs_details))
