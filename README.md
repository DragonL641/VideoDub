# VideoDub

A tool for dubbing videos with automatic subtitle generation using OpenAI Whisper.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/release/python-380/)

## Overview

VideoDub is a Python application that leverages OpenAI's Whisper model to automatically generate subtitles for videos. The tool intelligently selects the optimal Whisper model based on your system's hardware capabilities and generates SRT subtitle files that can be used with your video content.

## Features

- Automatic subtitle generation using state-of-the-art speech recognition
- Intelligent model selection based on system resources (CPU, GPU, memory)
- Support for multiple languages
- Cross-platform compatibility (Windows, macOS, Linux)
- Easy command-line interface

## Prerequisites

- Python 3.8 or higher
- FFmpeg for audio extraction
- Hardware requirements vary by model size (more powerful hardware enables larger, more accurate models)

## Quick Start Guide

1. **Clone the repository**
   ```bash
   git clone https://github.com/Dragon/VideoDub.git
   cd VideoDub
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Run the application**
   ```bash
   python videodub_cli.py path/to/your/video.mp4 --src-lang ja --tgt-lang zh
   ```

4. **Check the output**
   The generated subtitle file will be created in the same directory as the input video with the target language code in the filename.



## Installation

### Using pip with requirements.txt

```bash
# Clone the repository
git clone https://github.com/Dragon/VideoDub.git
cd VideoDub

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install PyTorch with CPU support (recommended for compatibility):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### From source

```bash
# Clone the repository
git clone https://github.com/Dragon/VideoDub.git
cd VideoDub

# Install in development mode
pip install -e .

# Install PyTorch with CPU support (recommended for compatibility):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```
```

## Usage

### Command Line Interface

First, make sure you have installed the dependencies and PyTorch as shown in the Installation section.

To run the application from command line:

```bash
# Generate subtitles for a video
python videodub_cli.py path/to/video.mp4 --src-lang ja --tgt-lang zh

# Generate subtitles with custom source and target languages
python videodub_cli.py path/to/video.mp4 --src-lang en --tgt-lang es

# Enable English as intermediate language for translation when direct translation model is not available
python videodub_cli.py path/to/video.mp4 --src-lang ja --tgt-lang zh --use-en-as-intermediate

# Note: --use-en-as-intermediate is a flag that doesn't take a value
# When present, it enables English as intermediate language for translation
```

### As a Library

```python
from videodub.process_video import generate_subtitles

# Generate subtitles for a video
generate_subtitles("path/to/video.mp4", src_lang="ja", tgt_lang="zh")

# Generate subtitles with English as intermediate language for translation
generate_subtitles("path/to/video.mp4", src_lang="ja", tgt_lang="zh", use_en_as_intermediate=True)
```

## Configuration

The application automatically selects the optimal Whisper model based on your system's specifications:
- On Apple Silicon Macs: Selects 'small' or 'medium' models depending on available memory
- With NVIDIA GPUs: Selects larger models ('large-v3') if sufficient VRAM is available
- On systems with limited resources: Falls back to lighter models ('base', 'small')

### Translation Options

- **Direct Translation**: When a direct translation model is available (e.g., from Japanese to Chinese), the application will use it directly
- **English as Intermediate**: If `--use-en-as-intermediate` is enabled and no direct translation model is available, the application will:
  1. Translate from source language to English
  2. Translate from English to target language
- **Fallback**: If no translation models are available, the application falls back to Whisper's built-in translation (English only)

## Architecture

The project follows a modular structure:

```
videodub/
├── __init__.py
├── main.py              # Main application logic
├── process_video.py     # Core video processing and transcription logic
├── utils/
│   ├── __init__.py
│   └── select_model.py  # Model selection logic
├── videodub_cli.py      # Command-line interface entry point
└── requirements.txt     # Project dependencies
```

## Development

### Setup

```bash
# Install all dependencies
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Running Tests

```bash
# Run tests (if available)
python -m pytest videodub/tests/
```

### Running the Application

```bash
# Run with command line interface
python videodub_cli.py path/to/video.mp4 --src-lang ja --tgt-lang zh

# Or import as a module
python -c "from videodub.process_video import generate_subtitles; generate_subtitles('path/to/video.mp4', 'ja', 'zh')"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Ensure code quality standards are met (`make check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for the Whisper model
- The machine learning community for continued advances in speech recognition