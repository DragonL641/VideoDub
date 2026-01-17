#!/usr/bin/env python3
"""Command-line interface for VideoDub."""

import sys
from pathlib import Path

# Add src to path so we can import the package directly
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Main entry point."""
    try:
        from videodub.cli import main as cli_main

        cli_main()
    except ImportError as e:
        print(f"Error importing VideoDub modules: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running VideoDub: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
