# VideoDub Documentation

Welcome to the VideoDub documentation! This guide will help you understand and use VideoDub effectively.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio extraction)
- At least 4GB RAM (8GB+ recommended)

### Install from PyPI

```bash
pip install videodub
```

### Install from Source

```bash
git clone https://github.com/Dragon/VideoDub.git
cd VideoDub
pip install -e .
```

### Install Development Dependencies

```bash
pip install -e .[dev]
```

## Quick Start

### Command Line Usage

```bash
# Basic usage - Japanese to Chinese subtitles
videodub video.mp4 --src-lang ja --tgt-lang zh

# English to Spanish with intermediate translation
videodub video.mp4 --src-lang en --tgt-lang es --use-en-as-intermediate

# Check version
videodub --version
```

### Python API Usage

```python
from videodub import generate_subtitles

# Generate subtitles
subtitle_path = generate_subtitles(
    video_path="video.mp4",
    src_lang="ja",
    tgt_lang="zh"
)
print(f"Subtitles saved to: {subtitle_path}")
```

## Advanced Usage

### Language Support

VideoDub supports translation between many language pairs:

```bash
# Direct translation (when available)
videodub video.mp4 --src-lang fr --tgt-lang de

# Via English intermediate (fallback)
videodub video.mp4 --src-lang ko --tgt-lang ru --use-en-as-intermediate
```

### Model Selection

The tool automatically selects the optimal Whisper model based on your system:

- **Apple Silicon Macs**: `small` or `medium` models
- **NVIDIA GPUs**: `large-v3` for high precision
- **CPU systems**: `base` or `small` for efficiency

You can check the recommended model:

```python
from videodub.model_selection import select_optimal_model

recommended_model = select_optimal_model()
print(f"Recommended model: {recommended_model}")
```

### Batch Processing

Process multiple videos:

```python
import os
from videodub import generate_subtitles

video_directory = "/path/to/videos"
for filename in os.listdir(video_directory):
    if filename.endswith(('.mp4', '.mov', '.avi')):
        video_path = os.path.join(video_directory, filename)
        try:
            generate_subtitles(video_path, src_lang="ja", tgt_lang="en")
            print(f"Processed: {filename}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")
```

## API Reference

### `generate_subtitles()`

Main function for generating subtitles.

**Parameters:**
- `video_path` (str): Path to the video file
- `src_lang` (str, optional): Source language code (default: "ja")
- `tgt_lang` (str, optional): Target language code (default: "zh")
- `use_en_as_intermediate` (bool, optional): Use English as intermediate for translation (default: False)

**Returns:**
- `str`: Path to the generated subtitle file

**Example:**
```python
from videodub import generate_subtitles

subtitle_file = generate_subtitles(
    "my_video.mp4",
    src_lang="ko",
    tgt_lang="en",
    use_en_as_intermediate=True
)
```

### Configuration

Customize VideoDub behavior through the `Config` class:

```python
from videodub.config import Config

config = Config()
config.AUDIO_SAMPLE_RATE = 22050  # Higher quality audio
config.DEFAULT_USE_EN_AS_INTERMEDIATE = True  # Always use English intermediate
```

## Configuration

### Environment Variables

VideoDub respects these environment variables:

```bash
# Force specific device
export VIDEODUB_DEVICE=cuda  # or cpu, mps

# Custom temporary directory
export VIDEODUB_TEMP_DIR=/tmp/videodub

# Whisper model cache directory
export WHISPER_CACHE_DIR=~/.cache/whisper
```

### Configuration File

Create `~/.videodub/config.json`:

```json
{
    "default_source_language": "ja",
    "default_target_language": "zh",
    "use_english_intermediate": false,
    "preferred_model": "medium",
    "audio_sample_rate": 16000
}
```

## Troubleshooting

### Common Issues

**1. FFmpeg not found**
```bash
# Install FFmpeg
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

**2. CUDA Out of Memory**
```bash
# Force CPU usage
export VIDEODUB_DEVICE=cpu
# or use smaller Whisper models
```

**3. Translation Models Not Found**
```bash
# Enable English intermediate translation
videodub video.mp4 --use-en-as-intermediate

# Check available models
pip list | grep transformers
```

**4. Slow Performance**
```bash
# Use smaller model
export WHISPER_MODEL=small

# Ensure GPU acceleration (if available)
nvidia-smi  # Check GPU status
```

### Debug Mode

Enable verbose logging:

```bash
# Command line
videodub video.mp4 --debug

# Python API
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/Dragon/VideoDub.git
cd VideoDub
python -m venv venv
source venv/bin/activate
pip install -e .[dev]

# Run tests
pytest

# Check code quality
make check
```

## License

VideoDub is released under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Hugging Face Transformers](https://huggingface.co/transformers/) for translation models
- The open-source community for continuous innovation