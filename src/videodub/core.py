"""Core functionality for VideoDub."""

from typing import Optional
from .config import Config
from .processing import VideoProcessor


def generate_subtitles(
    video_path: str,
    src_lang: str = Config.DEFAULT_SRC_LANG,
    tgt_lang: str = Config.DEFAULT_TGT_LANG,
    use_en_as_intermediate: bool = Config.DEFAULT_USE_EN_AS_INTERMEDIATE,
) -> str:
    """
    Generate subtitles for a video file.
    
    Args:
        video_path: Path to the video file
        src_lang: Source language code (default: 'ja')
        tgt_lang: Target language code (default: 'zh')
        use_en_as_intermediate: Whether to use English as intermediate language
        
    Returns:
        Path to the generated subtitle file
    """
    processor = VideoProcessor()
    return processor.generate_subtitles(
        video_path, src_lang, tgt_lang, use_en_as_intermediate
    )