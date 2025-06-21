"""Command-line interface for the AI sleepwalker.

This module provides a user-friendly CLI using Click that allows users
to configure and run the sleepwalker with custom options.
"""

from pathlib import Path

import click


@click.command()
@click.option(
    "--dirs",
    multiple=True,
    type=click.Path(exists=True),
    help="Directories to explore (can specify multiple)",
)
@click.option(
    "--idle-timeout",
    default=900,
    type=int,
    help="Seconds of inactivity before exploration starts (default: 15 minutes)",
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
def sleepwalk(
    dirs: tuple[str, ...], idle_timeout: int, mode: str, output_dir: str
) -> None:
    """Digital sleepwalker - explores your filesystem during idle time.

    The sleepwalker monitors for user inactivity and then safely explores
    your specified directories, generating dream-like reflections about
    the files and folders it discovers.

    Examples:
        sleepwalker                          # Use defaults (Desktop, Documents)
        sleepwalker --dirs ~/Projects        # Explore custom directory
        sleepwalker --idle-timeout 600       # Wait 10 minutes before exploring
        sleepwalker --mode adventure         # Adventure mode (coming soon)
    """
    if not dirs:
        home = Path.home()
        dirs = (str(home / "Desktop"), str(home / "Documents"))

    click.echo(f"🌙 Sleepwalker starting in {mode} mode...")
    click.echo(f"📁 Will explore: {', '.join(dirs)}")
    click.echo(f"⏱️  Idle timeout: {idle_timeout} seconds")
    click.echo(f"💾 Output directory: {output_dir}")
    click.echo("\nPress Ctrl+C to stop")

    # TODO: Integrate with main sleepwalker logic
    click.echo("🚧 Implementation coming soon via TDD approach!")


if __name__ == "__main__":
    sleepwalk()
