# VideoDub Documentation

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Progress Tracking](#progress-tracking)
- [Architecture](#architecture)
- [Development](#development)
- [API Reference](#api-reference)

## Installation

### Prerequisites
- Python 3.9 or higher
- FFmpeg for audio extraction
- Hardware requirements vary by model size

### Quick Installation
```bash
# Clone the repository
git clone https://github.com/Dragon/VideoDub.git
cd VideoDub

# Install dependencies
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install in development mode
pip install -e .
```

## Usage

### Command Line Interface
```bash
# Generate subtitles for a video
videodub path/to/video.mp4 --src-lang ja --tgt-lang zh

# With English as intermediate language
videodub path/to/video.mp4 --src-lang ja --tgt-lang zh --use-en-as-intermediate

# Direct script execution (development)
python videodub_cli.py path/to/video.mp4 --src-lang ja --tgt-lang zh
```

### As a Library
```python
from videodub.core import generate_subtitles

# Generate subtitles
result = generate_subtitles("path/to/video.mp4", src_lang="ja", tgt_lang="zh")
```

## Features

### Core Features
- Automatic subtitle generation using OpenAI Whisper
- Intelligent model selection based on system resources
- Multi-language support
- Cross-platform compatibility
- Real-time progress tracking

### Progress Tracking
VideoDub includes advanced progress tracking for long-running operations:

#### Visual Progress Display
```
Extracting audio: [██████████░░░░░░░░░░] 50.0% (45s remaining) Processing audio
Speech recognition: [████████████████████] 100.0% Speech recognition completed in 127.3s
```

#### How It Works
1. **Audio Extraction Progress**: Tracks FFmpeg processing with file size-based estimation
2. **Speech Recognition Progress**: Monitors Whisper transcription with duration-based estimation
3. **Automatic Cleanup**: Progress resources are properly managed

#### Technical Implementation
The progress system uses a modular observer pattern:
```
ProgressObserver (Interface)
    ↓
ConsoleProgressObserver (Implementation)
    ↓
ProgressTracker (Manager)
```

## Architecture

### Project Structure
```
src/videodub/
├── __init__.py
├── __version__.py       # Version information
├── cli.py               # Command-line interface
├── config.py            # Configuration settings
├── core.py              # Core functionality interface
├── model_selection.py   # Model selection logic
├── processing.py        # Core video processing and transcription
├── progress/            # Progress tracking module
│   └── __init__.py      # Progress tracking classes
└── utils/
    └── __init__.py      # Utility functions
```

### Key Components

#### Video Processing Pipeline
1. **Model Selection**: Automatically chooses optimal Whisper model based on hardware
2. **Audio Extraction**: Uses FFmpeg to extract audio from video files
3. **Speech Recognition**: Processes audio with Whisper for transcription
4. **Translation**: Handles language translation when needed
5. **Subtitle Generation**: Creates SRT subtitle files

#### Progress Tracking System
- Thread-safe progress updates
- Smart time estimation algorithms
- Graceful error handling
- Resource cleanup management

## Development

### Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/videodub
```

### Code Quality
```bash
# Run linting
make check

# Format code
make format

# Run security checks
make security
```

### Testing
The test suite includes:
- Unit tests for core functionality
- Integration tests for processing pipeline
- Progress tracking system verification

## API Reference

### Core Functions

#### `generate_subtitles()`
```python
def generate_subtitles(
    video_path: str,
    src_lang: str = "ja",
    tgt_lang: str = "zh",
    use_en_as_intermediate: bool = False
) -> str
```
Generates subtitles for a video file.

**Parameters:**
- `video_path`: Path to the video file
- `src_lang`: Source language code (default: "ja")
- `tgt_lang`: Target language code (default: "zh")
- `use_en_as_intermediate`: Use English as intermediate language for translation

**Returns:**
- Path to the generated subtitle file

### Configuration

#### Config Class
```python
class Config:
    DEFAULT_SRC_LANG: str = "ja"
    DEFAULT_TGT_LANG: str = "zh"
    AUDIO_SAMPLE_RATE: int = 16000
    TEMP_AUDIO_FILE: str = "temp_audio.wav"
```

### Progress Tracking

#### ProgressTracker
Main progress management class for tracking operation progress.

#### TimeEstimator
Utility class for estimating operation durations:
- `estimate_ffmpeg_extraction_time()`: Estimates audio extraction time
- `estimate_whisper_transcription_time()`: Estimates transcription time
- `get_video_duration()`: Gets actual video duration

## Troubleshooting

### Common Issues

1. **Missing FFmpeg**: Ensure FFmpeg is installed and accessible in PATH
2. **Import Errors**: Check that all dependencies are installed
3. **CUDA/MPS Issues**: The system automatically falls back to CPU mode
4. **Memory Issues**: Use smaller Whisper models for limited memory systems

### Debugging
Enable verbose output by setting environment variables:
```bash
export VIDEO_DUB_DEBUG=1
```

## Contributing
See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.