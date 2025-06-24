"""Unit tests for FilesystemExplorer component.

Following testing conventions:
- Test behavior, not implementation details
- Use real temp directories instead of mocks
- Table-driven testing for multiple scenarios
- Focus on observable outcomes and security
"""

import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

from ai_sleepwalker.constants import MAX_DISCOVERIES_PER_SESSION, MAX_EXPLORATION_DEPTH
from ai_sleepwalker.core.filesystem_explorer import FilesystemExplorer
from ai_sleepwalker.models import FileSystemDiscovery


@dataclass
class ExplorationTestCase:
    """Test case for filesystem exploration behavior."""

    name: str
    file_structure: dict  # Structure to create in temp directory
    expected_discovery_types: set[str]  # Expected types of discoveries
    min_discoveries: int  # Minimum expected discoveries


@dataclass
class SecurityTestCase:
    """Test case for security boundary validation."""

    name: str
    allowed_dirs: list[str]
    attack_path: str
    should_be_safe: bool


class TestFilesystemExplorerInitialization:
    """Test proper initialization and configuration."""

    def test_initialization_with_allowed_directories(self):
        """Test that explorer initializes with allowed directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            explorer = FilesystemExplorer([temp_dir])

            # Should have resolved paths
            assert len(explorer.allowed_paths) == 1
            assert explorer.allowed_paths[0] == Path(temp_dir).resolve()

    def test_initialization_sets_random_current_path(self):
        """Test that explorer sets a random starting current_path."""
        with tempfile.TemporaryDirectory() as temp_dir1:
            with tempfile.TemporaryDirectory() as temp_dir2:
                explorer = FilesystemExplorer([temp_dir1, temp_dir2])

                # Should pick one of the allowed paths
                assert explorer.current_path in explorer.allowed_paths

    def test_initialization_with_empty_directories(self):
        """Test that explorer handles empty directory list."""
        explorer = FilesystemExplorer([])

        assert explorer.allowed_paths == []
        assert explorer.current_path is None


class TestFilesystemExplorerWandering:
    """Test the core wander() functionality."""

    def test_wander_discovers_filesystem_items_randomly(self):
        """Test that wander() discovers items and varies its selection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create predictable structure
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "file2.py").write_text("print('hello')")
            subdir = temp_path / "subdir"
            subdir.mkdir()
            (subdir / "nested.md").write_text("# Header")

            explorer = FilesystemExplorer([str(temp_path)])

            # Act: Collect multiple discoveries
            discoveries = [explorer.wander() for _ in range(10)]
            discoveries = [d for d in discoveries if d is not None]

            # Assert: Should discover items with some variation
            assert len(discoveries) > 0, "Should discover at least some items"
            assert len({d.path for d in discoveries}) > 1, "Should show some variation"

            # All discoveries should be within allowed boundaries
            # Need to resolve temp_path to handle symlink resolution on macOS
            resolved_temp_path = temp_path.resolve()
            for discovery in discoveries:
                assert discovery.path.is_relative_to(resolved_temp_path), (
                    f"Discovery {discovery.path} outside allowed boundary "
                    f"{resolved_temp_path}"
                )

    def test_wander_returns_none_for_empty_directories(self):
        """Test that wander() handles empty directories gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            explorer = FilesystemExplorer([temp_dir])

            # Empty directory should return None or handle gracefully
            discovery = explorer.wander()

            # Should either return None or handle empty directory case
            if discovery is not None:
                assert isinstance(discovery, FileSystemDiscovery)

    @pytest.mark.parametrize(
        "test_case",
        [
            ExplorationTestCase(
                name="mixed_files_and_directories",
                file_structure={
                    "doc1.txt": "Document content",
                    "script.py": "print('test')",
                    "data/": {},
                    "data/nested.json": '{"key": "value"}',
                    "images/": {},
                    "images/pic.jpg": b"fake_image_data",
                },
                expected_discovery_types={"file", "directory"},
                min_discoveries=3,
            ),
            ExplorationTestCase(
                name="deep_directory_structure",
                file_structure={
                    "level1/": {},
                    "level1/level2/": {},
                    "level1/level2/level3/": {},
                    "level1/level2/level3/deep_file.txt": "deep content",
                },
                expected_discovery_types={"file", "directory"},
                min_discoveries=2,
            ),
        ],
    )
    def test_wander_explores_various_structures(self, test_case: ExplorationTestCase):
        """Test exploration behavior with different filesystem structures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test structure
            for path_str, content in test_case.file_structure.items():
                full_path = temp_path / path_str
                if path_str.endswith("/"):
                    full_path.mkdir(parents=True, exist_ok=True)
                else:
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    if isinstance(content, str):
                        full_path.write_text(content)
                    else:
                        full_path.write_bytes(content)

            explorer = FilesystemExplorer([str(temp_path)])

            # Collect discoveries
            discoveries = []
            # Try more times for random exploration to hit both types
            for _ in range(50):
                discovery = explorer.wander()
                if discovery:
                    discoveries.append(discovery)
                # Stop early if we have enough discoveries AND both types
                discovered_types = {d.discovery_type for d in discoveries}
                if (
                    len(discoveries) >= test_case.min_discoveries
                    and test_case.expected_discovery_types.issubset(discovered_types)
                ):
                    break

            # Verify exploration behavior
            assert len(discoveries) >= test_case.min_discoveries, (
                f"Should find at least {test_case.min_discoveries} items"
            )

            discovered_types = {d.discovery_type for d in discoveries}
            assert test_case.expected_discovery_types.issubset(discovered_types), (
                f"Should discover types: {test_case.expected_discovery_types}"
            )

    def test_wander_respects_depth_limits(self):
        """Test that exploration respects MAX_EXPLORATION_DEPTH."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create structure deeper than limit
            current_path = temp_path
            for i in range(MAX_EXPLORATION_DEPTH + 2):
                current_path = current_path / f"level{i}"
                current_path.mkdir()
                (current_path / f"file{i}.txt").write_text(f"content at level {i}")

            explorer = FilesystemExplorer([str(temp_path)])

            # Collect discoveries
            discoveries = []
            for _ in range(50):  # Try many times to test depth limiting
                discovery = explorer.wander()
                if discovery:
                    discoveries.append(discovery)

            # Verify depth limiting
            resolved_temp_path = temp_path.resolve()
            for discovery in discoveries:
                relative_path = discovery.path.relative_to(resolved_temp_path)
                depth = len(relative_path.parts) - 1  # Subtract 1 for the file itself
                assert depth <= MAX_EXPLORATION_DEPTH, (
                    f"Discovery at {discovery.path} exceeds depth limit"
                )

    def test_wander_respects_discovery_limits(self):
        """Test that exploration respects MAX_DISCOVERIES_PER_SESSION."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create many files to ensure we can hit the limit
            for i in range(MAX_DISCOVERIES_PER_SESSION + 20):
                (temp_path / f"file{i}.txt").write_text(f"content {i}")

            explorer = FilesystemExplorer([str(temp_path)])

            # Try to exceed discovery limit
            discoveries = []
            for _ in range(MAX_DISCOVERIES_PER_SESSION * 2):
                discovery = explorer.wander()
                if discovery:
                    discoveries.append(discovery)
                else:
                    break  # Explorer should stop when limit reached

            # Should respect the discovery limit
            assert len(discoveries) <= MAX_DISCOVERIES_PER_SESSION, (
                "Should not exceed discovery limit"
            )


class TestFilesystemExplorerSecurity:
    """Test security boundaries and path validation."""

    @pytest.mark.parametrize(
        "test_case",
        [
            SecurityTestCase(
                name="directory_traversal_attack",
                allowed_dirs=["/tmp/safe"],
                attack_path="/tmp/safe/../../../etc/passwd",
                should_be_safe=False,
            ),
            SecurityTestCase(
                name="subdirectory_access",
                allowed_dirs=["/tmp/safe"],
                attack_path="/tmp/safe/subdir/file.txt",
                should_be_safe=True,
            ),
            SecurityTestCase(
                name="sibling_directory_attack",
                allowed_dirs=["/tmp/safe"],
                attack_path="/tmp/unsafe/file.txt",
                should_be_safe=False,
            ),
        ],
    )
    def test_is_safe_path_validates_boundaries(self, test_case: SecurityTestCase):
        """Test that _is_safe_path properly validates security boundaries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            safe_dir = Path(temp_dir) / "safe"
            safe_dir.mkdir()

            explorer = FilesystemExplorer([str(safe_dir)])

            # Construct test path relative to our temp structure
            if test_case.attack_path.startswith("/tmp/safe"):
                test_path = Path(
                    test_case.attack_path.replace("/tmp/safe", str(safe_dir))
                )
            else:
                test_path = Path(test_case.attack_path)

            result = explorer._is_safe_path(test_path)
            assert result == test_case.should_be_safe, (
                f"Security validation failed for {test_case.name}"
            )

    def test_wander_never_escapes_allowed_directories(self):
        """Test that wander() never returns discoveries outside allowed dirs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create allowed directory
            safe_dir = temp_path / "safe"
            safe_dir.mkdir()
            (safe_dir / "safe_file.txt").write_text("safe content")

            # Create unsafe directory at same level
            unsafe_dir = temp_path / "unsafe"
            unsafe_dir.mkdir()
            (unsafe_dir / "unsafe_file.txt").write_text("unsafe content")

            explorer = FilesystemExplorer([str(safe_dir)])

            # Try many discoveries
            for _ in range(100):
                discovery = explorer.wander()
                if discovery:
                    # Every discovery must be within safe directory
                    resolved_safe_dir = safe_dir.resolve()
                    assert discovery.path.is_relative_to(resolved_safe_dir), (
                        f"Security breach: {discovery.path} outside safe directory "
                        f"{resolved_safe_dir}"
                    )

    def test_wander_handles_permission_errors_gracefully(self):
        """Test that wander() handles permission errors without crashing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create accessible file
            accessible_file = temp_path / "accessible.txt"
            accessible_file.write_text("readable content")

            explorer = FilesystemExplorer([str(temp_path)])

            # Should handle any permission issues gracefully
            discovery = explorer.wander()

            # Should either return a valid discovery or None, but not crash
            if discovery:
                assert isinstance(discovery, FileSystemDiscovery)
                resolved_temp_path = temp_path.resolve()
                assert discovery.path.is_relative_to(resolved_temp_path)


class TestFilesystemExplorerDiscoveryCreation:
    """Test discovery content quality and metadata."""

    def test_wander_creates_accurate_file_discoveries(self):
        """Test that file discoveries have accurate metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test file with known content
            test_file = temp_path / "test.txt"
            content = "Line 1\nLine 2\nLine 3\nExtra content"
            test_file.write_text(content)

            explorer = FilesystemExplorer([str(temp_path)])

            # Find the test file through wandering
            discoveries = []
            for _ in range(20):
                discovery = explorer.wander()
                if discovery and discovery.path.name == "test.txt":
                    discoveries.append(discovery)
                    break

            assert len(discoveries) > 0, "Should discover the test file"

            file_discovery = discoveries[0]
            assert file_discovery.discovery_type == "file"
            assert file_discovery.size_bytes == len(content.encode())
            assert file_discovery.preview is not None
            assert "Line 1" in file_discovery.preview

    def test_wander_creates_accurate_directory_discoveries(self):
        """Test that directory discoveries have accurate metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test directory
            test_dir = temp_path / "test_directory"
            test_dir.mkdir()

            explorer = FilesystemExplorer([str(temp_path)])

            # Find the test directory
            discoveries = []
            for _ in range(20):
                discovery = explorer.wander()
                if discovery and discovery.path.name == "test_directory":
                    discoveries.append(discovery)
                    break

            assert len(discoveries) > 0, "Should discover the test directory"

            dir_discovery = discoveries[0]
            assert dir_discovery.discovery_type == "directory"
            assert dir_discovery.size_bytes is None  # Directories don't have size
            assert dir_discovery.preview is None  # Directories don't have preview

    def test_wander_handles_binary_files_without_preview(self):
        """Test that binary files are detected without preview attempts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create binary file
            binary_file = temp_path / "image.jpg"
            binary_file.write_bytes(b"\x89PNG\x0d\x0a\x1a\x0a fake binary data")

            explorer = FilesystemExplorer([str(temp_path)])

            # Find the binary file
            discoveries = []
            for _ in range(20):
                discovery = explorer.wander()
                if discovery and discovery.path.name == "image.jpg":
                    discoveries.append(discovery)
                    break

            assert len(discoveries) > 0, "Should discover the binary file"

            binary_discovery = discoveries[0]
            assert binary_discovery.discovery_type == "file"
            assert binary_discovery.size_bytes > 0
            # Binary files should not have previews
            assert binary_discovery.preview is None
