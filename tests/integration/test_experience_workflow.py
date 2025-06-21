"""Integration tests for experience workflow components.

Tests how the experience system components work together, following
testing domain guidance to focus on component interactions rather
than implementation details.
"""

import pytest
from pathlib import Path
from datetime import datetime

from ai_sleepwalker.experiences.factory import ExperienceFactory
from ai_sleepwalker.experiences.base import ExperienceType
from ai_sleepwalker.models import FileSystemDiscovery
from ai_sleepwalker.constants import DiscoveryType
from tests.fixtures.test_doubles import create_test_discoveries


@pytest.mark.integration
async def test_dream_collector_synthesizer_integration():
    """Test that dream collector and synthesizer work together properly."""
    # Arrange - Create real components through factory
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)
    
    # Act - Run complete collection and synthesis workflow
    discoveries = create_test_discoveries()
    
    # Collect observations
    for discovery in discoveries:
        collector.add_observation(discovery)
    
    observations = collector.get_observations()
    result = await synthesizer.synthesize(observations)
    
    # Assert - Verify integration behavior
    assert len(observations) == len(discoveries)  # All discoveries collected
    assert result.total_observations == len(observations)  # Count consistency
    assert result.experience_type == ExperienceType.DREAM  # Type consistency
    assert result.session_start <= result.session_end  # Time consistency
    
    # Verify observation structure without testing exact content
    for obs in observations:
        assert obs.timestamp is not None
        assert len(obs.path) > 0
        assert len(obs.name) > 0
        assert obs.type in ["file", "directory"]
    
    # Verify result structure
    assert isinstance(result.content, str)
    assert len(result.content) > 0
    assert isinstance(result.metadata, dict)


@pytest.mark.integration
def test_experience_factory_consistency():
    """Test that factory creates compatible components."""
    # Arrange & Act - Create components through factory
    dream_collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    dream_synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)
    
    # Assert - Verify components are compatible
    assert dream_synthesizer.experience_type == ExperienceType.DREAM
    
    # Test that collector produces observations synthesizer can handle
    test_discovery = FileSystemDiscovery(
        path=Path("/test/file.txt"),
        name="file.txt",
        discovery_type=DiscoveryType.FILE.value,
        size_bytes=100
    )
    
    dream_collector.add_observation(test_discovery)
    observations = dream_collector.get_observations()
    
    # Should be able to synthesize without errors
    import asyncio
    result = asyncio.run(dream_synthesizer.synthesize(observations))
    assert result is not None


@pytest.mark.integration
def test_multiple_discovery_types_handling():
    """Test that system handles different discovery types properly."""
    # Arrange
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    
    # Different types of discoveries
    discoveries = [
        FileSystemDiscovery(
            path=Path("/test/doc.txt"), 
            name="doc.txt", 
            discovery_type=DiscoveryType.FILE.value, 
            size_bytes=100
        ),
        FileSystemDiscovery(
            path=Path("/test/folder"), 
            name="folder", 
            discovery_type=DiscoveryType.DIRECTORY.value
        ),
        FileSystemDiscovery(
            path=Path("/test/large.dat"), 
            name="large.dat", 
            discovery_type=DiscoveryType.FILE.value, 
            size_bytes=1024000
        ),
        FileSystemDiscovery(
            path=Path("/test/empty.txt"), 
            name="empty.txt", 
            discovery_type=DiscoveryType.FILE.value, 
            size_bytes=0
        ),
    ]
    
    # Act - Process different discovery types
    for discovery in discoveries:
        collector.add_observation(discovery)
    
    observations = collector.get_observations()
    
    # Assert - All types handled properly
    assert len(observations) == len(discoveries)
    
    # Verify type mapping
    file_observations = [obs for obs in observations if obs.type == DiscoveryType.FILE.value]
    dir_observations = [obs for obs in observations if obs.type == DiscoveryType.DIRECTORY.value]
    
    assert len(file_observations) == 3  # 3 files
    assert len(dir_observations) == 1   # 1 directory
    
    # Verify size handling for files
    for obs in file_observations:
        if obs.name == "large.dat":
            assert obs.size_bytes == 1024000
        elif obs.name == "empty.txt":
            assert obs.size_bytes == 0


@pytest.mark.integration  
async def test_empty_session_handling():
    """Test that system handles sessions with no discoveries gracefully."""
    # Arrange
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    synthesizer = ExperienceFactory.create_synthesizer(ExperienceType.DREAM)
    
    # Act - Process empty session
    observations = collector.get_observations()  # No observations added
    result = await synthesizer.synthesize(observations)
    
    # Assert - Handles empty session gracefully
    assert len(observations) == 0
    assert result.total_observations == 0
    assert len(result.content) > 0  # Still generates some content
    assert result.experience_type == ExperienceType.DREAM


@pytest.mark.integration
def test_observation_timestamp_ordering():
    """Test that observations maintain proper temporal ordering."""
    # Arrange
    collector = ExperienceFactory.create_collector(ExperienceType.DREAM)
    
    # Act - Add observations with some delay
    import time
    
    discoveries = [
        FileSystemDiscovery(
            path=Path("/test/first.txt"), 
            name="first.txt", 
            discovery_type=DiscoveryType.FILE.value
        ),
        FileSystemDiscovery(
            path=Path("/test/second.txt"), 
            name="second.txt", 
            discovery_type=DiscoveryType.FILE.value
        ),
        FileSystemDiscovery(
            path=Path("/test/third.txt"), 
            name="third.txt", 
            discovery_type=DiscoveryType.FILE.value
        ),
    ]
    
    timestamps = []
    for discovery in discoveries:
        collector.add_observation(discovery)
        timestamps.append(datetime.now())
        time.sleep(0.001)  # Small delay to ensure different timestamps
    
    observations = collector.get_observations()
    
    # Assert - Timestamps are in order
    obs_timestamps = [obs.timestamp for obs in observations]
    assert obs_timestamps == sorted(obs_timestamps)  # Chronological order
    
    # Verify all timestamps are within reasonable range
    for ts in obs_timestamps:
        assert abs((datetime.now() - ts).total_seconds()) < 10  # Within 10 seconds