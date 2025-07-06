"""Main sleepwalker orchestrator.

This module contains the main sleepwalking logic that coordinates
idle detection, sleep prevention, filesystem exploration, and dream generation.
"""

import asyncio
import logging
import os
import random
import signal
import time
from datetime import datetime
from pathlib import Path

import wakepy

from .constants import DiscoveryType
from .experiences.base import ExperienceType
from .experiences.factory import ExperienceFactory
from .models import FileSystemDiscovery

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum: int, frame: object) -> None:
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    logger.info("\n🛑 Shutdown requested. Finishing current dream...")
    shutdown_requested = True


def get_file_preview(file_path: Path, max_bytes: int = 200) -> str | None:
    """Safely get a preview of file contents."""
    try:
        # Skip binary files
        binary_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".pdf",
            ".exe",
            ".bin",
            ".zip",
            ".tar",
            ".gz",
            ".dmg",
            ".app",
            ".dylib",
            ".so",
        }
        if file_path.suffix.lower() in binary_extensions:
            return "[Binary file]"

        # Try to read first few bytes
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            preview = f.read(max_bytes)
            if preview:
                # Clean up whitespace and truncate
                preview = " ".join(preview.split())
                if len(preview) > 100:
                    preview = preview[:97] + "..."
                return preview
    except Exception:
        pass

    return None


def explore_directory(
    base_path: Path, max_items: int = 20
) -> list[FileSystemDiscovery]:
    """Explore a directory and return discoveries."""
    discoveries = []
    items_found = 0

    # Define patterns to skip
    skip_patterns = {
        ".git",
        "__pycache__",
        ".cache",
        "node_modules",
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
        ".DS_Store",
    }

    try:
        # Use rglob with a depth limit
        for item in base_path.rglob("*"):
            if items_found >= max_items:
                break

            # Skip if any part of path contains skip patterns
            if any(skip in str(item) for skip in skip_patterns):
                continue

            # Skip if we can't access it
            try:
                if item.is_file():
                    stat = item.stat()
                    size = stat.st_size

                    # Skip very large files
                    if size > 10 * 1024 * 1024:  # 10MB
                        continue

                    preview = get_file_preview(item) if size < 100000 else None

                    discoveries.append(
                        FileSystemDiscovery(
                            path=item,
                            name=item.name,
                            discovery_type=DiscoveryType.FILE.value,
                            size_bytes=size,
                            preview=preview,
                            timestamp=datetime.fromtimestamp(stat.st_mtime),
                        )
                    )
                    items_found += 1

                elif item.is_dir():
                    discoveries.append(
                        FileSystemDiscovery(
                            path=item,
                            name=item.name,
                            discovery_type=DiscoveryType.DIRECTORY.value,
                            timestamp=datetime.now(),
                        )
                    )
                    items_found += 1

            except (PermissionError, OSError):
                # Skip files we can't access
                continue

    except Exception as e:
        logger.warning(f"Error exploring {base_path}: {e}")

    return discoveries


def select_random_subdirectory(base_path: Path) -> Path:
    """Select a random subdirectory to explore."""
    try:
        # Get all accessible subdirectories
        subdirs = []
        for item in base_path.iterdir():
            try:
                if item.is_dir() and not item.name.startswith("."):
                    subdirs.append(item)
            except (PermissionError, OSError):
                continue

        if subdirs:
            return random.choice(subdirs)
    except Exception:
        pass

    return base_path


async def sleepwalk_cycle(
    cycle_num: int, search_paths: list[Path], output_dir: Path
) -> None:
    """Run one complete sleepwalking cycle."""
    logger.info(f"🌙 Starting sleepwalk cycle #{cycle_num}")

    # Choose a random path from allowed directories
    search_path = random.choice(search_paths)

    # Sometimes explore a subdirectory for variety
    if random.random() < 0.3 and cycle_num > 1:
        explore_path = select_random_subdirectory(search_path)
        if explore_path != search_path:
            logger.info(f"📂 Exploring subdirectory: {explore_path}")
    else:
        explore_path = search_path

    # Explore filesystem
    logger.info(f"🔍 Exploring {explore_path}...")
    discoveries = explore_directory(explore_path, max_items=random.randint(5, 15))

    if not discoveries:
        logger.warning("⚠️  No accessible files found, trying parent directory...")
        discoveries = explore_directory(search_path, max_items=10)

    logger.info(f"📁 Found {len(discoveries)} items in filesystem")

    # Log some of what was found
    for d in discoveries[:3]:
        icon = "📄" if d.discovery_type == "file" else "📁"
        size_info = f" ({d.size_bytes} bytes)" if d.size_bytes else ""
        logger.info(f"   {icon} {d.name}{size_info}")
    if len(discoveries) > 3:
        logger.info(f"   ... and {len(discoveries) - 3} more items")

    # Create experience components
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)

    # Collect observations
    for discovery in discoveries:
        collector.add_observation(discovery)

    observations = collector.get_observations()

    # Generate dream
    logger.info("💭 Generating dream narrative...")
    start_time = time.time()

    try:
        result = await synthesizer.synthesize(observations)
        duration = time.time() - start_time

        # Log summary
        logger.info(f"✨ Dream generated in {duration:.2f}s")

        # Save dream
        dream_file = output_dir / f"dream_{cycle_num:04d}.md"

        # Add metadata header
        dream_content = f"""# Dream #{cycle_num}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Explored: {explore_path}
Discoveries: {len(discoveries)}

---

{result.content}
"""

        dream_file.write_text(dream_content)

        # Also save latest dream
        latest_file = output_dir / "latest_dream.md"
        latest_file.write_text(dream_content)

        logger.info(f"💾 Dream saved to {dream_file}")

        # Show snippet of dream
        snippet = result.content[:100].replace("\n", " ")
        logger.info(f"📝 Dream snippet: {snippet}...")

    except Exception as e:
        logger.error(f"❌ Dream generation failed: {e}")
        logger.info("😴 Using meditation pause instead...")
        await asyncio.sleep(10)


async def start_sleepwalking(
    experience_type: str,
    allowed_dirs: list[str],
    idle_timeout: int,
    output_dir: Path,
) -> None:
    """Start the sleepwalking session.

    This is the main sleepwalker loop that:
    1. Prevents sleep using wakepy
    2. Explores allowed directories
    3. Generates dreams from discoveries
    4. Saves dream logs to output directory
    5. Runs continuously until stopped
    """
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Convert directory strings to Path objects
    search_paths = [Path(d).resolve() for d in allowed_dirs]

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("🚀 AI Sleepwalker Starting")
    logger.info("=" * 50)

    # Check for API keys
    has_api_keys = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
    if has_api_keys:
        logger.info("🔑 API keys detected - will generate real dreams")
    else:
        logger.info("📝 No API keys - using fallback dreams")
        logger.info("   Set GEMINI_API_KEY or OPENAI_API_KEY for AI dreams")

    logger.info(f"\n📁 Exploring: {', '.join(str(p) for p in search_paths)}")
    logger.info(f"💾 Dreams saved to: {output_dir}")
    logger.info("🔒 Display wake lock activated - preventing sleep and screen lock")
    logger.info("⏰ Will explore and dream continuously")
    logger.info("   Press Ctrl+C to stop\n")

    cycle = 1

    # Use wakepy to prevent sleep and screen lock
    with wakepy.keep.presenting():
        while not shutdown_requested:
            try:
                # Run sleepwalk cycle
                await sleepwalk_cycle(cycle, search_paths, output_dir)

                # Random wait between cycles (30s to 2 min)
                wait_time = random.randint(30, 120)
                logger.info(f"😴 Resting for {wait_time}s before next exploration...\n")

                # Sleep in small chunks to check for shutdown
                for _ in range(wait_time):
                    if shutdown_requested:
                        break
                    await asyncio.sleep(1)

                cycle += 1

                # Clean up old dreams periodically (keep last 100)
                if cycle % 50 == 0:
                    dream_files = sorted(output_dir.glob("dream_*.md"))
                    if len(dream_files) > 100:
                        for old_file in dream_files[:-100]:
                            old_file.unlink()
                        logger.info(
                            f"🧹 Cleaned up {len(dream_files) - 100} old dreams"
                        )

            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                logger.info("🔄 Restarting in 30 seconds...")
                await asyncio.sleep(30)

    logger.info("\n🔓 Display wake lock released")
    logger.info("👋 Sleepwalker shutting down gracefully")
    logger.info(f"📊 Generated {cycle - 1} dreams this session")
