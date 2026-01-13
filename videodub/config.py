"""Configuration settings for VideoDub."""

# Default language codes
DEFAULT_SRC_LANG = "ja"  # Japanese
DEFAULT_TGT_LANG = "zh"  # Chinese

# Audio processing settings
AUDIO_SAMPLE_RATE = 16000  # Sample rate for extracted audio
AUDIO_CHANNELS = 1         # Mono audio

# File settings
TEMP_AUDIO_FILE = "temp_audio.wav"

# Model settings
AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]

# Translation settings
DEFAULT_USE_EN_AS_INTERMEDIATE = False

# Device settings
ALLOWED_DEVICES = ["cpu", "cuda", "mps"]