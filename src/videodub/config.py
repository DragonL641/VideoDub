"""Configuration settings for VideoDub."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Global configuration for VideoDub."""

    # Default language codes
    DEFAULT_SRC_LANG: str = "ja"  # Japanese
    DEFAULT_TGT_LANG: str = "zh"  # Chinese

    # Audio processing settings
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1

    # File settings
    TEMP_AUDIO_FILE: str = "temp_audio.wav"

    # Model settings
    AVAILABLE_MODELS: List[str] = field(default_factory=lambda: ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"])

    # Translation settings
    DEFAULT_USE_EN_AS_INTERMEDIATE: bool = False

    # Device settings
    ALLOWED_DEVICES: List[str] = field(default_factory=lambda: ["cpu", "cuda", "mps"])