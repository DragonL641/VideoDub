#!/usr/bin/env python3
"""Test script to verify installation."""

def main():
    print("Testing VideoDub installation...")
    
    # Try importing the package
    try:
        import videodub
        print("✓ Successfully imported videodub package")
        print(f"Version: {videodub.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import videodub: {e}")
        return False
    
    # Try importing core components
    try:
        from videodub.core import generate_subtitles
        print("✓ Successfully imported core functions")
    except ImportError as e:
        print(f"✗ Failed to import core functions: {e}")
        return False
    
    print("✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)