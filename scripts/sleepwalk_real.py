#!/usr/bin/env python3
"""Keep computer awake by exploring real filesystem directories.

This script continuously explores actual directories and generates dreams
based on real files found, keeping your computer active.
"""

import asyncio
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import wakepy

# Suppress verbose output
os.environ["LITELLM_LOG"] = "ERROR"
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

from ai_sleepwalker.constants import DiscoveryType
from ai_sleepwalker.experiences.base import ExperienceType
from ai_sleepwalker.experiences.factory import ExperienceFactory
from ai_sleepwalker.models import FileSystemDiscovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    logger.info("\n🛑 Shutdown requested. Finishing current dream...")
    shutdown_requested = True


def get_file_preview(file_path: Path, max_bytes: int = 200) -> str | None:
    """Safely get a preview of file contents."""
    try:
        # Skip binary files
        binary_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.exe', '.bin', 
                           '.zip', '.tar', '.gz', '.dmg', '.app', '.dylib', '.so'}
        if file_path.suffix.lower() in binary_extensions:
            return "[Binary file]"
        
        # Try to read first few bytes
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            preview = f.read(max_bytes)
            if preview:
                # Clean up whitespace and truncate
                preview = ' '.join(preview.split())
                if len(preview) > 100:
                    preview = preview[:97] + "..."
                return preview
    except Exception:
        pass
    
    return None


def explore_directory(base_path: Path, max_items: int = 20) -> list[FileSystemDiscovery]:
    """Explore a directory and return discoveries."""
    discoveries = []
    items_found = 0
    
    # Define patterns to skip
    skip_patterns = {
        '.git', '__pycache__', '.cache', 'node_modules', '.venv', 
        'venv', '.pytest_cache', '.mypy_cache', '.DS_Store'
    }
    
    try:
        # Use rglob with a depth limit
        for item in base_path.rglob('*'):
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
                    
                    discoveries.append(FileSystemDiscovery(
                        path=item,
                        name=item.name,
                        discovery_type=DiscoveryType.FILE.value,
                        size_bytes=size,
                        preview=preview,
                        timestamp=datetime.fromtimestamp(stat.st_mtime)
                    ))
                    items_found += 1
                    
                elif item.is_dir():
                    discoveries.append(FileSystemDiscovery(
                        path=item,
                        name=item.name,
                        discovery_type=DiscoveryType.DIRECTORY.value,
                        timestamp=datetime.now()
                    ))
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
                if item.is_dir() and not item.name.startswith('.'):
                    subdirs.append(item)
            except (PermissionError, OSError):
                continue
        
        if subdirs:
            return random.choice(subdirs)
    except Exception:
        pass
    
    return base_path


async def sleepwalk_cycle(cycle_num: int, search_path: Path) -> None:
    """Run one complete sleepwalking cycle with real filesystem exploration."""
    logger.info(f"🌙 Starting sleepwalk cycle #{cycle_num}")
    
    # Sometimes explore a subdirectory for variety
    if random.random() < 0.3 and cycle_num > 1:
        explore_path = select_random_subdirectory(search_path)
        if explore_path != search_path:
            logger.info(f"📂 Exploring subdirectory: {explore_path}")
    else:
        explore_path = search_path
    
    # Explore real filesystem
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
        
        # Save dream to rotating log
        dream_dir = Path("sleepwalk_dreams")
        dream_dir.mkdir(exist_ok=True)
        dream_file = dream_dir / f"dream_{cycle_num:04d}.md"
        
        # Add metadata header
        dream_content = f"""# Dream #{cycle_num}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Explored: {explore_path}
Discoveries: {len(discoveries)}

---

{result.content}
"""
        
        dream_file.write_text(dream_content)
        
        # Also save latest dream
        latest_file = dream_dir / "latest_dream.md"
        latest_file.write_text(dream_content)
        
        logger.info(f"💾 Dream saved to {dream_file}")
        
        # Show snippet of dream
        snippet = result.content[:100].replace('\n', ' ')
        logger.info(f"📝 Dream snippet: {snippet}...")
        
    except Exception as e:
        logger.error(f"❌ Dream generation failed: {e}")
        logger.info("😴 Using meditation pause instead...")
        await asyncio.sleep(10)


async def keep_awake_real(search_path: Path) -> None:
    """Main loop to keep computer awake by exploring real directories."""
    logger.info("🚀 AI Sleepwalker - Real Filesystem Explorer")
    logger.info("=" * 50)
    
    # Check for API keys
    has_api_keys = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
    if has_api_keys:
        logger.info("🔑 API keys detected - will generate real dreams")
    else:
        logger.info("📝 No API keys - using fallback dreams")
        logger.info("   Set GEMINI_API_KEY or OPENAI_API_KEY for AI dreams")
    
    logger.info(f"\n📁 Exploring: {search_path.absolute()}")
    logger.info("🔒 System wake lock activated - preventing sleep and screen lock")
    logger.info("⏰ Will explore and dream continuously to keep system awake")
    logger.info("   Press Ctrl+C to stop\n")
    
    cycle = 1
    
    # Use wakepy to prevent sleep and screen lock
    with wakepy.keep.running():
        while not shutdown_requested:
            try:
                # Run sleepwalk cycle
                await sleepwalk_cycle(cycle, search_path)
                
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
                    dream_files = sorted(Path("sleepwalk_dreams").glob("dream_*.md"))
                    if len(dream_files) > 100:
                        for old_file in dream_files[:-100]:
                            old_file.unlink()
                        logger.info(f"🧹 Cleaned up {len(dream_files) - 100} old dreams")
                
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                logger.info("🔄 Restarting in 30 seconds...")
                await asyncio.sleep(30)
    
    logger.info("\n🔓 System wake lock released")
    logger.info("👋 Sleepwalker shutting down gracefully")
    logger.info(f"📊 Generated {cycle - 1} dreams this session")


def main():
    """Entry point with user confirmation and signal handling."""
    # Get search path from command line or use default
    if len(sys.argv) > 1:
        search_path = Path(sys.argv[1])
    else:
        search_path = Path("..")  # Parent directory by default
    
    # Resolve to absolute path
    search_path = search_path.resolve()
    
    # Confirm with user
    print("🔍 AI Sleepwalker - Real Filesystem Explorer")
    print("=" * 50)
    print(f"\nThis will explore the following directory and all subdirectories:")
    print(f"📁 {search_path}")
    print("\nThe sleepwalker will:")
    print("  • Read file names and directory structures")
    print("  • Preview text file contents (first ~100 chars)")
    print("  • Generate dream narratives based on discoveries")
    print("  • Save dreams to sleepwalk_dreams/ directory")
    print("\nIt will NOT:")
    print("  • Modify any files")
    print("  • Access system files or hidden directories")
    print("  • Read large or binary files")
    
    response = input("\n❓ Is this OK? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Cancelled by user")
        sys.exit(0)
    
    print("\n✅ Starting sleepwalker...\n")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(keep_awake_real(search_path))
    except KeyboardInterrupt:
        logger.info("\n👋 Sleepwalker stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()