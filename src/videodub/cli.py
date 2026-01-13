"""Command-line interface for VideoDub."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import generate_subtitles
from .config import Config


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate subtitles for videos using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s video.mp4 --src-lang ja --tgt-lang zh
  %(prog)s video.mp4 --src-lang en --tgt-lang es --use-en-as-intermediate
        """,
    )

    # Version argument
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # Positional arguments
    parser.add_argument("video_path", help="Path to the video file", type=Path)

    # Optional arguments
    config = Config()

    parser.add_argument(
        "--src-lang",
        default=config.DEFAULT_SRC_LANG,
        help=f"Source language code (default: {config.DEFAULT_SRC_LANG})",
    )

    parser.add_argument(
        "--tgt-lang",
        default=config.DEFAULT_TGT_LANG,
        help=f"Target language code (default: {config.DEFAULT_TGT_LANG})",
    )

    parser.add_argument(
        "--use-en-as-intermediate",
        action="store_true",
        default=config.DEFAULT_USE_EN_AS_INTERMEDIATE,
        help="Use English as intermediate language for translation when direct model is not available",
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate video file
    if not args.video_path.exists():
        print(f"Error: Video file '{args.video_path}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        # Generate subtitles
        output_path = generate_subtitles(
            str(args.video_path),
            args.src_lang,
            args.tgt_lang,
            args.use_en_as_intermediate,
        )
        print(f"Success! Subtitles saved to: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
