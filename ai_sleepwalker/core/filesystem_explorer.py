"""Safe filesystem exploration with security boundaries."""

import random
from pathlib import Path
from typing import Any


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

    def wander(self) -> dict[str, Any] | None:
        """Pick a random direction to explore."""
        # TODO: Implement actual filesystem wandering
        # For now, return None to indicate no discoveries
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

    def _create_discovery(self, path: Path) -> dict[str, Any]:
        """Create discovery object for a filesystem item."""
        # TODO: Implement discovery creation with proper metadata
        return {
            "path": str(path),
            "name": path.name,
            "type": "file" if path.is_file() else "directory",
            "size_bytes": path.stat().st_size if path.is_file() else None,
        }
