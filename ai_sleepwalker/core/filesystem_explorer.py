"""Safe filesystem exploration with security boundaries."""

import logging
import random
from pathlib import Path

from ..constants import (
    MAX_DISCOVERIES_PER_SESSION,
    MAX_EXPLORATION_DEPTH,
    MAX_FILE_PREVIEW_SIZE_BYTES,
    DiscoveryType,
)
from ..models import FileSystemDiscovery

logger = logging.getLogger(__name__)


class FilesystemExplorer:
    """Safe filesystem exploration that respects directory boundaries."""

    def __init__(self, allowed_dirs: list[str]) -> None:
        """Initialize explorer with allowed directories.

        Args:
            allowed_dirs: List of directory paths that are safe to explore
        """
        self.allowed_paths = [Path(d).resolve() for d in allowed_dirs]
        self.current_path = (
            random.choice(self.allowed_paths) if self.allowed_paths else None
        )
        self.discoveries_made = 0  # Track discoveries for session limits

    def wander(self) -> FileSystemDiscovery | None:
        """Pick a random direction to explore and return a discovery.

        Implements a random walk algorithm that safely explores within
        allowed directory boundaries. Respects session limits for
        discoveries and exploration depth.

        Returns:
            FileSystemDiscovery object if an item is found, None if
            exploration limits reached or no items available.
        """
        # Early validation - group all precondition checks
        if not self._can_explore():
            return None

        # Safe exploration with consistent error handling
        discovered_item = self._safe_explore()
        if not discovered_item:
            return None

        # Process successful discovery
        return self._process_discovery(discovered_item)

    def _can_explore(self) -> bool:
        """Check if exploration can proceed."""
        if self.discoveries_made >= MAX_DISCOVERIES_PER_SESSION:
            logger.debug(
                f"Discovery limit reached. [limit={MAX_DISCOVERIES_PER_SESSION}]"
            )
            return False

        if not self.allowed_paths or self.current_path is None:
            logger.debug("No allowed paths available for exploration")
            return False

        return True

    def _safe_explore(self) -> Path | None:
        """Safely explore current location with error handling."""
        try:
            start_path = self._get_valid_start_path()
            return self._explore_location(start_path)
        except (OSError, PermissionError) as e:
            logger.debug(f"Exploration error. [path={self.current_path}, error={e}]")
            return None

    def _get_valid_start_path(self) -> Path:
        """Get a valid starting path for exploration."""
        if self.current_path and self.current_path.exists():
            return self.current_path

        # Fallback to random allowed path
        start_path = random.choice(self.allowed_paths)
        self.current_path = start_path
        return start_path

    def _process_discovery(self, discovered_item: Path) -> FileSystemDiscovery:
        """Process a successful discovery."""
        self.discoveries_made += 1
        discovery = self._create_discovery(discovered_item)
        self._update_current_path(discovered_item)

        logger.debug(
            f"Discovery made. [name={discovery.name}, "
            f"type={discovery.discovery_type}, path={discovery.path}]"
        )
        return discovery

    def _explore_location(self, location: Path) -> Path | None:
        """Explore a location and randomly select an item to discover.

        Args:
            location: Path to explore (file or directory)

        Returns:
            Path of discovered item, or None if nothing found or accessible.
        """
        if not self._is_safe_path(location):
            return None

        if location.is_file():
            return location

        if location.is_dir():
            return self._explore_directory(location)

        return None

    def _explore_directory(self, directory: Path) -> Path | None:
        """Explore a directory and return a random item or the directory itself."""
        # Try to get directory contents, fallback to directory itself if fails
        items = self._get_directory_items(directory)
        if items is None:
            return directory  # Can't read directory, return it as discovery

        # Handle empty directory
        if not items:
            return directory

        # Filter to safe and depth-compliant items
        safe_items = self._filter_safe_items(items)
        if not safe_items:
            return directory

        # Random selection: 30% chance to return directory, 70% to explore contents
        if random.random() < 0.3:
            return directory
        return random.choice(safe_items)

    def _get_directory_items(self, directory: Path) -> list[Path] | None:
        """Get directory contents, return None if inaccessible."""
        try:
            return list(directory.iterdir())
        except (OSError, PermissionError):
            return None

    def _filter_safe_items(self, items: list[Path]) -> list[Path]:
        """Filter items to only include safe and depth-compliant paths."""
        return [
            item
            for item in items
            if self._is_safe_path(item) and self._is_within_depth_limit(item)
        ]

    def _update_current_path(self, discovered_item: Path) -> None:
        """Update current path for next exploration (random walk behavior).

        Args:
            discovered_item: The path that was just discovered.
        """
        new_path = self._determine_next_path(discovered_item)
        self.current_path = new_path or self._get_fallback_path()

    def _determine_next_path(self, discovered_item: Path) -> Path | None:
        """Determine the next path based on discovered item type."""
        try:
            if discovered_item.is_dir() and self._is_safe_path(discovered_item):
                return discovered_item

            if discovered_item.is_file():
                parent = discovered_item.parent
                if self._is_safe_path(parent):
                    return parent

        except (OSError, AttributeError):
            pass

        return None

    def _get_fallback_path(self) -> Path | None:
        """Get a fallback path when path determination fails."""
        return random.choice(self.allowed_paths) if self.allowed_paths else None

    def _is_within_depth_limit(self, path: Path) -> bool:
        """Check if path is within the maximum exploration depth.

        Args:
            path: Path to check for depth compliance.

        Returns:
            True if path is within MAX_EXPLORATION_DEPTH, False otherwise.
        """
        try:
            resolved_path = path.resolve()
        except (OSError, ValueError):
            return False

        # Check depth relative to each allowed path
        for allowed_path in self.allowed_paths:
            depth = self._calculate_depth(resolved_path, allowed_path, path.is_file())
            if depth is not None and depth <= MAX_EXPLORATION_DEPTH:
                return True

        return False

    def _calculate_depth(
        self, resolved_path: Path, allowed_path: Path, is_file: bool
    ) -> int | None:
        """Calculate depth of path relative to allowed path."""
        try:
            relative_path = resolved_path.relative_to(allowed_path)
            depth = len(relative_path.parts)
            # For files, subtract 1 since the file itself doesn't count as depth
            return depth - 1 if is_file else depth
        except ValueError:
            # Path is not relative to this allowed_path
            return None

    def _is_safe_path(self, path: Path) -> bool:
        """Validate path is within allowed directories."""
        try:
            resolved = path.resolve()
            return any(
                resolved.is_relative_to(allowed) for allowed in self.allowed_paths
            )
        except (OSError, ValueError):
            return False

    def _create_discovery(self, path: Path) -> FileSystemDiscovery:
        """Create discovery object for a filesystem item."""
        # TODO: Implement discovery creation with proper metadata
        discovery_type = (
            DiscoveryType.FILE.value
            if path.is_file()
            else DiscoveryType.DIRECTORY.value
        )
        size_bytes = None
        preview = None

        if path.is_file():
            try:
                stat = path.stat()
                size_bytes = stat.st_size

                # Generate preview for small text files
                if size_bytes <= MAX_FILE_PREVIEW_SIZE_BYTES and self._is_text_file(
                    path
                ):
                    preview = self._generate_preview(path)
            except (OSError, PermissionError):
                pass  # Skip files we can't read

        return FileSystemDiscovery(
            path=path,
            name=path.name,
            discovery_type=discovery_type,
            size_bytes=size_bytes,
            preview=preview,
        )

    def _is_text_file(self, path: Path) -> bool:
        """Check if file appears to be a text file."""
        text_extensions = {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".json",
            ".xml",
            ".html",
            ".css",
        }
        return path.suffix.lower() in text_extensions

    def _generate_preview(self, path: Path) -> str | None:
        """Generate a brief preview of file content."""
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                content = f.read(MAX_FILE_PREVIEW_SIZE_BYTES)
                # Return first few lines, truncated
                lines = content.split("\n")[:3]
                return "\n".join(lines).strip()
        except (OSError, UnicodeDecodeError):
            return None
