"""Entry point for running the AI sleepwalker as a module.

This allows users to run the sleepwalker with:
    python -m ai_sleepwalker
    uv run -m ai_sleepwalker
"""

from .cli import sleepwalk

if __name__ == "__main__":
    sleepwalk()
