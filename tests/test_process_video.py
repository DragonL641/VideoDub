"""Tests for the VideoDub processing module."""

import pytest
from videodub.processing import VideoProcessor


class TestVideoProcessor:
    """Test suite for VideoProcessor class."""
    
    def test_processor_initialization(self):
        """Test that VideoProcessor can be initialized."""
        processor = VideoProcessor()
        assert processor is not None
        assert hasattr(processor, "config")
    
    def test_format_timestamp_method(self):
        """Test the timestamp formatting method."""
        processor = VideoProcessor()
        # Test basic formatting
        assert processor._format_timestamp(0) == "00:00:00,000"
        assert processor._format_timestamp(1) == "00:00:01,000"
        assert processor._format_timestamp(60) == "00:01:00,000"
        assert processor._format_timestamp(3600) == "01:00:00,000"
        
        # Test with fractional seconds
        assert processor._format_timestamp(1.5) == "00:00:01,500"
        assert processor._format_timestamp(61.25) == "00:01:01,250"


# Tests can be run with: python -m pytest tests/
# or poetry run pytest