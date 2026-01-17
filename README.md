# VideoDub

A professional tool for automatic video subtitle generation using OpenAI Whisper.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

## Quick Start

### Installation
```bash
git clone https://github.com/Dragon/VideoDub.git
cd VideoDub
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Usage
```bash
# Generate subtitles
videodub video.mp4 --src-lang ja --tgt-lang zh

# Development mode
python videodub_cli.py video.mp4 --src-lang ja --tgt-lang zh
```

## Features
- Automatic subtitle generation with OpenAI Whisper
- **Intelligent hardware-aware model selection** (optimized for your system)
- Multi-language support with translation
- **Real-time progress tracking with visual progress bars** (for audio extraction)
- **Quality-focused processing** for accurate results
- Cross-platform compatibility

## Quality-Focused Processing

VideoDub prioritizes subtitle quality and accuracy:

### Quality Optimizations
- **Default quality settings**: Uses Whisper's default parameters for best results
- **Apple Silicon Macs**: Recommended `small` model for high accuracy
- **Model selection**: Automatically chooses quality-appropriate models

### Translation Accuracy Enhancements
- **Context-aware translation**: Considers neighboring segments for better translation quality
- **Improved text alignment**: Better extraction of relevant translated portions
- **Enhanced error handling**: Graceful fallbacks when translation models fail
- **Two-step translation optimization**: Improved intermediate language processing

### Performance Analysis
Analyze your system's capabilities:
```bash
python performance_analyzer.py
```

### Quality vs Speed Trade-offs
For best results:
- **Highest Quality**: `small` or `medium` models
- **Balanced**: `base` model
- **Fastest**: `tiny` model (lower accuracy)

## Progress Tracking

VideoDub features **improved** real-time progress tracking during audio extraction:

```
Extracting audio: [████████████████████] 100.0% Extracting audio completed in 0.3s
```

**Note**: Speech recognition progress is handled by Whisper internally for optimal quality.

**Key Improvements:**
- ✅ **No duplicate progress bars** - Clean single progress display for audio extraction
- ✅ **Accurate completion** - Progress reaches 100% when operation finishes
- ✅ **Realistic timing** - Better time estimation for small files

**Requirements:**
- Activate virtual environment: `source .venv/bin/activate`
- Ensure FFmpeg is installed and accessible

**Verification:**
```bash
# Test the improved progress system
python test_progress_fixes.py
```

## Building Executables

VideoDub can be compiled into standalone executables for Windows and macOS using Nuitka.

### Setup Build Environment
```bash
# Install build dependencies
pip install -r requirements-dev.txt

# Or use the setup script
./scripts/setup_build_env.sh
```

### Build Commands
```bash
# Build for current platform
python scripts/build.py

# Build for specific platform
python scripts/build.py --platform macos
python scripts/build.py --platform windows

# Build for all platforms
python scripts/build.py --all

# Clean previous builds
python scripts/build.py --clean

# Custom output filename
python scripts/build.py --output myapp

# Show all options
python scripts/build.py --help
```

### Platform-Specific Scripts
```bash
# macOS
./scripts/build_macos.sh

# Windows
scripts\build_windows.bat
```

## Troubleshooting

### Common Issues and Solutions

**FFmpeg "Invalid duration" Error**
- **Problem**: `Invalid duration for option ss: -t` error during audio extraction
- **Solution**: This has been fixed in the latest version. The code no longer passes invalid `None` parameters to FFmpeg.

**Subtitles Generated in Wrong Language**
- **Problem**: Subtitles appear in source language instead of target language
- **Solution**: This was caused by duplicate code blocks preventing translation. Fixed in the latest version.

**Progress Bar Issues**
- **Problem**: Double progress bars or incorrect timing
- **Solution**: See the Progress Tracking section above for the current improved implementation.

## Documentation
For detailed documentation, see [docs/index.md](docs/index.md)

## License
MIT License - see [LICENSE](LICENSE) file for details.