"""Main entry point for the VideoDub application."""

import argparse
import sys
from . import __version__
from .process_video import generate_subtitles


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate subtitles for videos using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 添加版本参数
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        "video_path",
        help="Path to the video file"
    )
    from . import config
    
    parser.add_argument(
        "--src-lang",
        default=config.DEFAULT_SRC_LANG,
        help=f"Source language code (default: {config.DEFAULT_SRC_LANG} for Japanese)"
    )
    parser.add_argument(
        "--tgt-lang",
        default=config.DEFAULT_TGT_LANG,
        help=f"Target language code (default: {config.DEFAULT_TGT_LANG} for Chinese)"
    )
    parser.add_argument(
        "--use-en-as-intermediate",
        action="store_true",
        default=config.DEFAULT_USE_EN_AS_INTERMEDIATE,
        help="Allow using English as intermediate language for translation when direct translation model is not available (default: {} for False)".format(config.DEFAULT_USE_EN_AS_INTERMEDIATE)
    )

    args = parser.parse_args()

    generate_subtitles(args.video_path, args.src_lang, args.tgt_lang, args.use_en_as_intermediate)


if __name__ == "__main__":
    main()