#!/usr/bin/env python3
"""Demo script to showcase the dream generation capability.

This script creates sample filesystem discoveries and generates a dream narrative
using the complete LLM integration pipeline.
"""

import asyncio
import logging
import os
import warnings
from datetime import datetime
from pathlib import Path

# Suppress verbose LiteLLM output
os.environ["LITELLM_LOG"] = "ERROR"
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

# Suppress pydantic warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
# Suppress aiohttp unclosed session warnings 
warnings.filterwarnings("ignore", message="Unclosed client session")
warnings.filterwarnings("ignore", message="Unclosed connector")

from ai_sleepwalker.constants import DiscoveryType
from ai_sleepwalker.experiences.base import ExperienceType
from ai_sleepwalker.experiences.factory import ExperienceFactory
from ai_sleepwalker.models import FileSystemDiscovery


def create_sample_discoveries() -> list[FileSystemDiscovery]:
    """Create realistic sample filesystem discoveries for dream generation."""
    return [
        FileSystemDiscovery(
            path=Path("/Users/alex/Documents/forgotten_diary.txt"),
            name="forgotten_diary.txt",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=4096,
            preview="Dear future self, today I discovered something strange in the digital realm...",
            timestamp=datetime(2024, 1, 15, 14, 30)
        ),
        FileSystemDiscovery(
            path=Path("/Library/Application Support/Mysterious App/hidden_config.json"),
            name="hidden_config.json", 
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=1337,
            preview='{"secret_key": "████████", "last_access": "never", "purpose": "unknown"}',
            timestamp=datetime(2024, 1, 15, 15, 15)
        ),
        FileSystemDiscovery(
            path=Path("/tmp/encryption_keys_backup"),
            name="encryption_keys_backup",
            discovery_type=DiscoveryType.DIRECTORY.value,
            timestamp=datetime(2024, 1, 15, 16, 0)
        ),
        FileSystemDiscovery(
            path=Path("/var/log/system_whispers.log"),
            name="system_whispers.log",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=0,
            timestamp=datetime(2024, 1, 15, 16, 30)
        ),
        FileSystemDiscovery(
            path=Path("/Users/alex/Desktop/draft_letter_never_sent.txt"),
            name="draft_letter_never_sent.txt",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=2048,
            preview="To whom it may concern, I've been wandering through digital corridors...",
            timestamp=datetime(2024, 1, 15, 17, 0)
        )
    ]


async def generate_sample_dream() -> None:
    """Generate and display a sample dream narrative."""
    print("🌙 AI Sleepwalker - Dream Generation Demo")
    print("=" * 50)
    
    # Check for API keys
    has_api_keys = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY"))
    if has_api_keys:
        print("🔑 API keys detected - will use real LLM for dream generation")
    else:
        print("📝 No API keys found - will use fallback dream content")
        print("   (Set GEMINI_API_KEY or OPENAI_API_KEY to use real LLM)")
    
    print("\n📁 Creating sample filesystem discoveries...")
    discoveries = create_sample_discoveries()
    
    for discovery in discoveries:
        discovery_type = "📄" if discovery.discovery_type == "file" else "📁"
        size_info = f" ({discovery.size_bytes} bytes)" if discovery.size_bytes is not None else ""
        print(f"   {discovery_type} {discovery.name}{size_info}")
    
    print(f"\n🔮 Processing {len(discoveries)} discoveries through dream pipeline...")
    
    # Create experience components
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)
    
    # Collect observations
    for discovery in discoveries:
        collector.add_observation(discovery)
    
    observations = collector.get_observations()
    print(f"✨ Collected {len(observations)} observations")
    
    # Generate dream narrative
    print("🧠 Generating dream narrative...")
    start_time = datetime.now()
    
    try:
        # Temporarily suppress logging during generation
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = await synthesizer.synthesize(observations)
        
        generation_time = (datetime.now() - start_time).total_seconds()
        print(f"⚡ Generated in {generation_time:.2f} seconds")
        
        # Give a brief moment for any async cleanup
        await asyncio.sleep(0.1)
        
        # Display results
        print("\n" + "=" * 70)
        print("🌟 GENERATED DREAM NARRATIVE")
        print("=" * 70)
        print(result.content)
        print("=" * 70)
        
        # Display metadata
        print(f"\n📊 Dream Metadata:")
        print(f"   Experience Type: {result.experience_type.value}")
        print(f"   Total Observations: {result.total_observations}")
        print(f"   Session Duration: {result.session_start} → {result.session_end}")
        print(f"   File Extension: {result.file_extension}")
        
        if "model" in result.metadata:
            print(f"   🤖 LLM Model: {result.metadata['model']}")
            print(f"   ⏱️  Generation Time: {result.metadata['duration_seconds']:.2f}s")
            print(f"   📝 Content Length: {result.metadata['content_length']} chars")
            if "total_tokens" in result.metadata:
                print(f"   🪙 Tokens Used: {result.metadata['total_tokens']}")
        else:
            print(f"   🔄 Fallback Mode: {result.metadata.get('fallback_used', False)}")
            print(f"   💭 Mood: {result.metadata.get('mood', 'N/A')}")
        
        # Save to file
        output_file = Path("sample_dream.md")
        output_file.write_text(result.content)
        print(f"\n💾 Dream saved to: {output_file.absolute()}")
        
    except Exception as e:
        print(f"❌ Error generating dream: {e}")
        print("   This might happen if there are API issues or configuration problems")
    
    finally:
        # Final cleanup to prevent unclosed session warnings
        await asyncio.sleep(0.2)


if __name__ == "__main__":
    print("Starting dream generation demo...\n")
    asyncio.run(generate_sample_dream())
    print("\n🌙 Dream generation demo complete!")