"""Constants and configuration values for the sleepwalker system."""

from enum import Enum
from pathlib import Path


class DiscoveryType(Enum):
    """Types of filesystem discoveries."""

    FILE = "file"
    DIRECTORY = "directory"


class ExperienceMode(Enum):
    """Available experience modes for the sleepwalker."""

    DREAM = "dream"
    ADVENTURE = "adventure"
    SCRAPBOOK = "scrapbook"
    JOURNAL = "journal"


class FileExtension(Enum):
    """Supported file extensions for different outputs."""

    MARKDOWN = ".md"
    JSON = ".json"
    HTML = ".html"
    TEXT = ".txt"


# Default configuration values
DEFAULT_IDLE_TIMEOUT_SECONDS = 900  # 15 minutes
DEFAULT_OUTPUT_DIRECTORY = Path.home() / ".sleepwalker" / "dreams"
DEFAULT_EXPERIENCE_MODE = ExperienceMode.DREAM

# File size limits
MAX_FILE_PREVIEW_SIZE_BYTES = 1024  # 1KB for text preview
MAX_EXPLORATION_DEPTH = 3  # Maximum directory depth to explore

# LLM configuration
DEFAULT_LLM_MODEL = "gemini/gemini-2.5-flash-preview-05-20"
LLM_MAX_TOKENS = 2048
LLM_TEMPERATURE = 0.7

# Safety limits
MAX_DISCOVERIES_PER_SESSION = 100
MAX_SESSION_DURATION_MINUTES = 60
