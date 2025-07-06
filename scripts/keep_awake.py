#!/usr/bin/env python3
"""Keep computer awake by continuously running the AI sleepwalker.

This script simulates continuous filesystem exploration and dream generation
to prevent the computer from going to sleep.
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


def generate_random_discoveries() -> list[FileSystemDiscovery]:
    """Generate random filesystem discoveries to keep things interesting."""
    base_paths = [
        "/Users/alex/Documents",
        "/Users/alex/Desktop", 
        "/Users/alex/Downloads",
        "/Library/Caches",
        "/tmp",
        "/var/log",
        "/Users/alex/.config",
        "/Applications"
    ]
    
    file_types = [
        ("notes.txt", "Remember to check the..."),
        ("config.json", '{"last_modified": "2024-01-15", "status": "active"}'),
        ("draft.md", "# Ideas for tomorrow\n\n- [ ] Explore new paths"),
        ("data.csv", "timestamp,event,value\n2024-01-15,discovery,42"),
        ("screenshot.png", "[Binary image data]"),
        ("backup.zip", "[Compressed archive]"),
        ("history.log", "2024-01-15 14:30:00 - System started"),
        ("preferences.plist", '<?xml version="1.0" encoding="UTF-8"?>')
    ]
    
    discoveries = []
    num_discoveries = random.randint(3, 7)
    
    for _ in range(num_discoveries):
        base_path = random.choice(base_paths)
        
        if random.random() < 0.7:  # 70% files, 30% directories
            file_name, preview = random.choice(file_types)
            path = Path(base_path) / f"{random.randint(1000, 9999)}_{file_name}"
            discoveries.append(FileSystemDiscovery(
                path=path,
                name=path.name,
                discovery_type=DiscoveryType.FILE.value,
                size_bytes=random.randint(0, 1048576),  # 0 to 1MB
                preview=preview[:80] if random.random() < 0.8 else None,
                timestamp=datetime.now()
            ))
        else:
            dir_name = random.choice(["cache", "temp", "backup", "archive", "old"])
            path = Path(base_path) / f"{dir_name}_{random.randint(100, 999)}"
            discoveries.append(FileSystemDiscovery(
                path=path,
                name=path.name,
                discovery_type=DiscoveryType.DIRECTORY.value,
                timestamp=datetime.now()
            ))
    
    return discoveries


async def sleepwalk_cycle(cycle_num: int) -> None:
    """Run one complete sleepwalking cycle."""
    logger.info(f"🌙 Starting sleepwalk cycle #{cycle_num}")
    
    # Generate random discoveries
    discoveries = generate_random_discoveries()
    logger.info(f"📁 Found {len(discoveries)} items in filesystem")
    
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
        dream_file = Path(f"sleepwalk_dreams/dream_{cycle_num:04d}.md")
        dream_file.parent.mkdir(exist_ok=True)
        dream_file.write_text(result.content)
        
        # Also save latest dream
        latest_file = Path("sleepwalk_dreams/latest_dream.md")
        latest_file.write_text(result.content)
        
        logger.info(f"💾 Dream saved to {dream_file}")
        
        # Show snippet of dream
        snippet = result.content[:100].replace('\n', ' ')
        logger.info(f"📝 Dream snippet: {snippet}...")
        
    except Exception as e:
        logger.error(f"❌ Dream generation failed: {e}")
        logger.info("😴 Using meditation pause instead...")
        await asyncio.sleep(10)


async def keep_awake() -> None:
    """Main loop to keep computer awake indefinitely."""
    logger.info("🚀 AI Sleepwalker - Keep Awake Mode")
    logger.info("=" * 50)
    
    # Check for API keys
    has_api_keys = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
    if has_api_keys:
        logger.info("🔑 API keys detected - will generate real dreams")
    else:
        logger.info("📝 No API keys - using fallback dreams")
        logger.info("   Set GEMINI_API_KEY or OPENAI_API_KEY for AI dreams")
    
    logger.info("\n⏰ Will generate dreams continuously to keep system awake")
    logger.info("   Press Ctrl+C to stop\n")
    
    cycle = 1
    
    while not shutdown_requested:
        try:
            # Run sleepwalk cycle
            await sleepwalk_cycle(cycle)
            
            # Random wait between cycles (30s to 2 min)
            wait_time = random.randint(30, 120)
            logger.info(f"😴 Resting for {wait_time}s before next cycle...\n")
            
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
    
    logger.info("\n👋 Sleepwalker shutting down gracefully")
    logger.info(f"📊 Generated {cycle - 1} dreams this session")


def main():
    """Entry point with signal handling."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(keep_awake())
    except KeyboardInterrupt:
        logger.info("\n👋 Sleepwalker stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()