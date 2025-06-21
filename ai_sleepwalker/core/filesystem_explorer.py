"""Safe filesystem exploration with security boundaries."""

import random
from pathlib import Path

from ..constants import MAX_FILE_PREVIEW_SIZE_BYTES, DiscoveryType
from ..models import FileSystemDiscovery


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

    def wander(self) -> FileSystemDiscovery | None:
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
