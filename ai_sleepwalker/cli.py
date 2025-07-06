"""Command-line interface for the AI sleepwalker.

This module provides a user-friendly CLI using Click that allows users
to configure and run the sleepwalker with custom options.
"""

import asyncio
import logging
import os
from pathlib import Path

import click

from .main import start_sleepwalking

# Suppress verbose LLM output for cleaner CLI experience
os.environ["LITELLM_LOG"] = "ERROR"
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


@click.command()
@click.option(
    "--dirs",
    multiple=True,
    type=click.Path(exists=True),
    help="Directories to explore (can specify multiple)",
)
@click.option(
    "--idle-timeout",
    default=0,  # Changed default - start immediately rather than wait
    type=int,
    help="Seconds of inactivity before exploration starts (default: start immediately)",
)
@click.option(
    "--mode",
    type=click.Choice(["dream", "adventure", "scrapbook"]),
    default="dream",
    help="Experience mode (default: dream)",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    default="~/.sleepwalker/dreams",
    help="Directory to save experience logs",
)
@click.option(
    "--confirm/--no-confirm",
    default=True,
    help="Ask for confirmation before exploring directories",
)
def sleepwalk(
    dirs: tuple[str, ...], idle_timeout: int, mode: str, output_dir: str, confirm: bool
) -> None:
    """Digital sleepwalker - explores your filesystem and generates dreams.

    The sleepwalker safely explores your specified directories, generating
    dream-like reflections about the files and folders it discovers while
    keeping your computer awake.

    Examples:
        sleepwalker                          # Use defaults (Desktop, Documents)
        sleepwalker --dirs ~/Projects        # Explore custom directory
        sleepwalker --dirs . --no-confirm    # Explore current dir without asking
        sleepwalker --output-dir ./dreams    # Custom output location
    """
    # Set defaults if no directories specified
    if not dirs:
        home = Path.home()
        dirs = (str(home / "Desktop"), str(home / "Documents"))

    # Expand output directory path
    output_path = Path(output_dir).expanduser()

    # Show configuration
    click.echo("🌙 AI Sleepwalker - Digital Dream Explorer")
    click.echo("=" * 50)
    click.echo(f"Mode: {mode}")
    click.echo("Directories to explore:")
    for d in dirs:
        click.echo(f"  📁 {Path(d).resolve()}")
    click.echo(f"Dream output: {output_path}")

    # Check for API keys
    has_api_keys = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
    if has_api_keys:
        click.echo("🔑 API keys detected - will generate AI dreams")
    else:
        click.echo("📝 No API keys - will use fallback dreams")
        click.echo("   Set GEMINI_API_KEY or OPENAI_API_KEY for AI-generated content")

    # Confirmation prompt
    if confirm:
        click.echo("\nThe sleepwalker will:")
        click.echo("  • Explore the directories above and their subdirectories")
        click.echo("  • Read file names, sizes, and preview text content")
        click.echo("  • Generate dream narratives about discoveries")
        click.echo("  • Keep your computer awake while running")
        click.echo("  • Save dreams to the output directory")
        click.echo("\nIt will NOT modify any files.")

        if not click.confirm("\nStart sleepwalking?"):
            click.echo("❌ Cancelled")
            return

    click.echo("\n🚀 Starting sleepwalker...\n")

    # Run the main sleepwalking function
    try:
        asyncio.run(
            start_sleepwalking(
                experience_type=mode,
                allowed_dirs=list(dirs),
                idle_timeout=idle_timeout,
                output_dir=output_path,
            )
        )
    except KeyboardInterrupt:
        click.echo("\n👋 Sleepwalker stopped by user")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    sleepwalk()
