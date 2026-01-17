#!/bin/bash
# macOS build script for VideoDub

set -e

echo "=== Building VideoDub for macOS ==="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Install Nuitka if not present
if ! python3 -m nuitka --version &> /dev/null; then
    echo "Installing Nuitka..."
    pip3 install nuitka ordered-set zstandard
fi

# Clean previous builds
rm -rf dist build

# Build for current architecture
echo "Building for $(uname -m) architecture..."
python3 build.py

# Check if build succeeded
if [ -f "dist/videodub.bin" ] || [ -f "dist/videodub.exe" ]; then
    echo "Build successful!"
    ls -la dist/
else
    echo "Build failed!"
    exit 1
fi