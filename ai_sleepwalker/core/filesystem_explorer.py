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
        # Check discovery limits
        if self.discoveries_made >= MAX_DISCOVERIES_PER_SESSION:
            logger.debug(
                f"Discovery limit reached. [limit={MAX_DISCOVERIES_PER_SESSION}]"
            )
            return None

        # Need allowed paths to explore
        if not self.allowed_paths or self.current_path is None:
            logger.debug("No allowed paths available for exploration")
            return None

        try:
            # Start exploration from current path or random allowed path
            start_path = self.current_path
            if not start_path.exists():
                start_path = random.choice(self.allowed_paths)
                self.current_path = start_path

            # Find items to explore at current location
            discovered_item = self._explore_location(start_path)

            if discovered_item:
                self.discoveries_made += 1
                discovery = self._create_discovery(discovered_item)

                # Update current path for next wander (random walk)
                self._update_current_path(discovered_item)

                logger.debug(
                    f"Discovery made. [name={discovery.name}, "
                    f"type={discovery.discovery_type}, path={discovery.path}]"
                )
                return discovery

            return None

        except (OSError, PermissionError) as e:
            logger.debug(f"Exploration error. [path={start_path}, error={e}]")
            return None

    def _explore_location(self, location: Path) -> Path | None:
        """Explore a location and randomly select an item to discover.

        Args:
            location: Path to explore (file or directory)

        Returns:
            Path of discovered item, or None if nothing found or accessible.
        """
        try:
            # If location is a file, return it for discovery
            if location.is_file() and self._is_safe_path(location):
                return location

            # If location is a directory, randomly select something inside
            if location.is_dir() and self._is_safe_path(location):
                # Get all items in directory (files and subdirectories)
                try:
                    items = list(location.iterdir())
                    if not items:
                        # Empty directory - return the directory itself as discovery
                        return location

                    # Filter to safe paths and respect depth limits
                    safe_items = []
                    for item in items:
                        if self._is_safe_path(item) and self._is_within_depth_limit(
                            item
                        ):
                            safe_items.append(item)

                    if not safe_items:
                        return location  # Return directory if no safe items

                    # Random selection from available items
                    # Sometimes prefer returning the directory itself for exploration
                    if random.random() < 0.3:  # 30% chance to discover the directory
                        return location
                    else:
                        return random.choice(safe_items)

                except (OSError, PermissionError):
                    # Can't read directory, return it as discovery
                    return location

            return None

        except (OSError, PermissionError):
            return None

    def _update_current_path(self, discovered_item: Path) -> None:
        """Update current path for next exploration (random walk behavior).

        Args:
            discovered_item: The path that was just discovered.
        """
        try:
            if discovered_item.is_dir() and self._is_safe_path(discovered_item):
                # Move into discovered directory
                self.current_path = discovered_item
            elif discovered_item.is_file():
                # Stay in the parent directory of discovered file
                parent = discovered_item.parent
                if self._is_safe_path(parent):
                    self.current_path = parent
                else:
                    # Fallback to random allowed path
                    self.current_path = random.choice(self.allowed_paths)
            else:
                # Fallback to random allowed path
                self.current_path = random.choice(self.allowed_paths)

        except (OSError, AttributeError):
            # Fallback to random allowed path on any error
            if self.allowed_paths:
                self.current_path = random.choice(self.allowed_paths)

    def _is_within_depth_limit(self, path: Path) -> bool:
        """Check if path is within the maximum exploration depth.

        Args:
            path: Path to check for depth compliance.

        Returns:
            True if path is within MAX_EXPLORATION_DEPTH, False otherwise.
        """
        try:
            # Find the depth relative to any allowed path
            for allowed_path in self.allowed_paths:
                try:
                    relative_path = path.resolve().relative_to(allowed_path)
                    depth = len(relative_path.parts)
                    # For files, subtract 1 since the file itself doesn't count as depth
                    if path.is_file():
                        depth -= 1
                    return depth <= MAX_EXPLORATION_DEPTH
                except ValueError:
                    # path is not relative to this allowed_path, try next
                    continue

            # If path is not relative to any allowed path, it's not within limits
            return False

        except (OSError, ValueError):
            return False

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
