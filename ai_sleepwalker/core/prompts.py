"""Prompt management for LLM dream generation."""

from ..experiences.base import Observation

DREAM_PROMPT_TEMPLATE = """You are a surrealist writer who discovers hidden
connections between mundane digital artifacts and impossible dream worlds.

Transform these discoveries into surreal dream imagery:

{observations}

Think through this process:
1. Identify key elements: file names, dates, content fragments, numbers
2. Find unexpected connections between unrelated items
3. Transform technical elements into sensory experiences
4. Link scenes through dream logic (not real-world logic)

Requirements:
✓ Exactly 2-3 flowing scenes that connect naturally
✓ Maximum 4 sentences total
✓ Incorporate actual quotes/numbers/content from the discoveries
✓ Make source files traceable through creative wordplay or imagery
✓ Dates as surreal physical elements (can be full date, month+day, or just month)
✓ Prioritize atmosphere and flow over cramming in every detail

Individual transformation examples:
- "error_log.txt" → a mirror labeled "error_log"
- "IMG_3847.jpg" → "portrait number 3847"
- "project_notes.md" → a notebook titled "project notes"

Example of connected dream from multiple discoveries:
Input: [July 2022] error_log.txt with "connection refused",
[Dec 25, 2020] IMG_3847.jpg (2.3MB),
[March 2024] project_notes.md with "TODO: fix the navigation bug"

Output: Portrait number 3847 hangs in a July corridor, its pixels slowly
refusing connections one by one.

Behind the frame, someone has carved "TODO: fix the navigation bug" in letters
that glow like Christmas lights, leading deeper into rooms that shouldn't exist.

Notice the gentler flow - not every element appears, but the dream maintains
its surreal logic and atmosphere.

Format your output with each sentence on its own line for better readability:

Output only your connected dream narrative:

"""


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
