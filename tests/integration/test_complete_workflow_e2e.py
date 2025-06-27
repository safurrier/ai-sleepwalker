"""End-to-end test for complete sleepwalker workflow.

Tests the full pipeline from filesystem discovery through dream generation,
verifying that all components work together properly including the new LLM integration.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ai_sleepwalker.constants import DiscoveryType
from ai_sleepwalker.experiences.base import ExperienceType
from ai_sleepwalker.experiences.factory import ExperienceFactory
from ai_sleepwalker.models import FileSystemDiscovery


@pytest.mark.integration
async def test_complete_dream_workflow_with_real_llm() -> None:
    """Test complete workflow from filesystem discovery to dream generation.

    This E2E test verifies:
    1. FileSystemDiscovery creation and collection
    2. Dream collector observation processing
    3. LLM-based dream synthesis (if API keys available)
    4. Fallback behavior when LLM unavailable
    5. Complete metadata and content generation
    """
    # Create realistic filesystem discoveries
    discoveries = [
        FileSystemDiscovery(
            path=Path("/Users/test/Documents/old_diary.txt"),
            name="old_diary.txt",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=2048,
            preview="Today I found something strange in the digital realm...",
            timestamp=datetime(2024, 1, 15, 14, 30),
        ),
        FileSystemDiscovery(
            path=Path("/tmp/mysterious_cache"),
            name="mysterious_cache",
            discovery_type=DiscoveryType.DIRECTORY.value,
            timestamp=datetime(2024, 1, 15, 15, 15),
        ),
        FileSystemDiscovery(
            path=Path("/var/log/forgotten.log"),
            name="forgotten.log",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=0,
            timestamp=datetime(2024, 1, 15, 16, 0),
        ),
    ]

    # Step 1: Create experience components through factory
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)

    # Step 2: Collect observations from filesystem discoveries
    for discovery in discoveries:
        collector.add_observation(discovery)

    observations = collector.get_observations()

    # Verify collection phase
    assert len(observations) == len(discoveries)
    assert all(obs.timestamp is not None for obs in observations)
    assert any("diary" in obs.name for obs in observations)
    assert any("cache" in obs.name for obs in observations)
    assert any("log" in obs.name for obs in observations)

    # Step 3: Synthesize dream narrative
    # This will use real LLM if API keys available, otherwise fallback
    result = await synthesizer.synthesize(observations)

    # Verify synthesis results
    assert result is not None
    assert result.experience_type == ExperienceType.DREAM
    assert result.total_observations == len(observations)
    assert result.session_start <= result.session_end

    # Verify content quality
    assert len(result.content) > 100  # Substantial narrative content
    assert isinstance(result.content, str)
    assert result.file_extension == ".md"

    # Verify metadata structure
    assert isinstance(result.metadata, dict)
    assert "mood" in result.metadata or "model" in result.metadata  # LLM or fallback

    # If LLM was used, verify enhanced metadata
    if "model" in result.metadata:
        # Real LLM was used
        assert "duration_seconds" in result.metadata
        assert "observation_count" in result.metadata
        assert "prompt_length" in result.metadata
        assert "content_length" in result.metadata
        assert result.metadata["observation_count"] == len(observations)

        # Content should reference the observations
        content_lower = result.content.lower()
        keywords = ["diary", "cache", "log", "digital", "strange"]
        assert any(word in content_lower for word in keywords)

    else:
        # Fallback was used
        assert "fallback_used" in result.metadata
        assert result.metadata["fallback_used"] is True


@pytest.mark.integration
async def test_complete_workflow_with_file_system_simulation() -> None:
    """Test workflow with simulated filesystem operations and temporary files.

    Creates actual temporary files and directories to test more realistic
    filesystem discovery scenarios.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create realistic test files
        diary_file = temp_path / "forgotten_diary.txt"
        diary_file.write_text("Chapter 1: The digital wandering began at midnight...")

        cache_dir = temp_path / "mysterious_cache"
        cache_dir.mkdir()

        log_file = temp_path / "system.log"
        log_file.write_text("")  # Empty log file

        # Create discoveries from real files
        discoveries = [
            FileSystemDiscovery(
                path=diary_file,
                name=diary_file.name,
                discovery_type=DiscoveryType.FILE.value,
                size_bytes=diary_file.stat().st_size,
                preview=diary_file.read_text()[:50],
                timestamp=datetime.now(),
            ),
            FileSystemDiscovery(
                path=cache_dir,
                name=cache_dir.name,
                discovery_type=DiscoveryType.DIRECTORY.value,
                timestamp=datetime.now(),
            ),
            FileSystemDiscovery(
                path=log_file,
                name=log_file.name,
                discovery_type=DiscoveryType.FILE.value,
                size_bytes=log_file.stat().st_size,
                timestamp=datetime.now(),
            ),
        ]

        # Process through complete workflow
        collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
        synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)

        # Collect observations
        for discovery in discoveries:
            collector.add_observation(discovery)

        observations = collector.get_observations()

        # Verify realistic file data was captured
        diary_obs = next(obs for obs in observations if "diary" in obs.name)
        assert diary_obs.size_bytes > 0
        preview_content = str(diary_obs.preview or "")
        has_wandering = "digital wandering" in diary_obs.brief_note
        has_chapter = "Chapter 1" in preview_content
        assert has_wandering or has_chapter

        empty_log_obs = next(obs for obs in observations if "log" in obs.name)
        assert empty_log_obs.size_bytes == 0

        # Generate dream narrative
        result = await synthesizer.synthesize(observations)

        # Verify complete result
        assert result.total_observations == 3
        assert len(result.content) > 50
        assert result.experience_type == ExperienceType.DREAM

        # Result should be saveable to file
        result_content = result.content
        assert isinstance(result_content, str)
        assert len(result_content.strip()) > 0


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"),
    reason="No LLM API keys available for full E2E test",
)
async def test_complete_workflow_with_real_llm_api() -> None:
    """Test complete workflow with real LLM API calls.

    Only runs when API keys are available. Tests the full pipeline
    including actual LLM dream generation.
    """
    # Create rich, narrative-worthy discoveries
    discoveries = [
        FileSystemDiscovery(
            path=Path("/Library/Application Support/Mysterious App/hidden_config.json"),
            name="hidden_config.json",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=1337,
            preview='{"secret_key": "████████", "last_access": "never"}',
            timestamp=datetime(2023, 12, 31, 23, 59),
        ),
        FileSystemDiscovery(
            path=Path("/Users/someone/Desktop/draft_letter_never_sent.txt"),
            name="draft_letter_never_sent.txt",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=4096,
            preview="Dear future self, if you're reading this...",
            timestamp=datetime(2024, 1, 1, 0, 0),
        ),
        FileSystemDiscovery(
            path=Path("/tmp/encryption_keys_backup"),
            name="encryption_keys_backup",
            discovery_type=DiscoveryType.DIRECTORY.value,
            timestamp=datetime(2024, 6, 15, 3, 33),
        ),
    ]

    # Process through complete workflow
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)

    for discovery in discoveries:
        collector.add_observation(discovery)

    observations = collector.get_observations()
    result = await synthesizer.synthesize(observations)

    # Verify real LLM was used (not fallback)
    assert "model" in result.metadata
    assert "fallback_used" not in result.metadata

    # Verify LLM-specific metadata
    assert "duration_seconds" in result.metadata
    assert "total_tokens" in result.metadata or "prompt_tokens" in result.metadata
    assert result.metadata["duration_seconds"] > 0
    assert result.metadata["duration_seconds"] < 60  # Should be reasonable

    # Verify dream content quality from real LLM
    content = result.content.lower()

    # Should reference key elements from observations
    keywords = ["config", "letter", "key", "hidden", "secret"]
    assert any(word in content for word in keywords)

    # Should have dream-like, narrative qualities
    dream_indicators = [
        "dream",
        "wandering",
        "discovered",
        "found",
        "strange",
        "mysterious",
        "forgotten",
        "digital",
        "surreal",
    ]
    assert any(indicator in content for indicator in dream_indicators)

    # Should be substantial narrative (not just bullet points)
    assert len(result.content) > 200
    assert "\n" in result.content  # Multi-line narrative

    # Should be properly formatted markdown
    assert result.file_extension == ".md"


@pytest.mark.integration
async def test_workflow_error_resilience() -> None:
    """Test that workflow handles various error conditions gracefully."""

    # Test with problematic discovery data
    problematic_discoveries = [
        FileSystemDiscovery(
            path=Path("/nonexistent/path/file.txt"),
            name="file.txt",
            discovery_type=DiscoveryType.FILE.value,
            size_bytes=None,  # Missing size
            timestamp=datetime.now(),
        ),
        FileSystemDiscovery(
            path=Path(""),  # Empty path
            name="",  # Empty name
            discovery_type=DiscoveryType.DIRECTORY.value,
            timestamp=datetime.now(),
        ),
    ]

    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)

    # Should handle problematic data without crashing
    for discovery in problematic_discoveries:
        try:
            collector.add_observation(discovery)
        except Exception:
            pass  # Some data might be rejected, that's OK

    observations = collector.get_observations()

    # Should still be able to synthesize even with limited/no observations
    result = await synthesizer.synthesize(observations)

    assert result is not None
    assert result.experience_type == ExperienceType.DREAM
    assert isinstance(result.content, str)
    assert len(result.content) > 0  # Should have some content even in error cases
