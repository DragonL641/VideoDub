#!/bin/bash
# Setup script for VideoDub build environment

echo "=== Setting up VideoDub build environment ==="

# Install build dependencies
echo "Installing build dependencies..."
pip3 install -r requirements-dev.txt

# Verify Nuitka installation
echo "Verifying Nuitka installation..."
if python3 -m nuitka --version; then
    echo "Nuitka installed successfully!"
else
    echo "Failed to install Nuitka"
    exit 1
fi

echo "Build environment setup complete!"
echo "You can now run:"
echo "  python3 scripts/build.py --help   # See all build options"