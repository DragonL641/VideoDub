"""Tests for the process_video module."""

from videodub.process_video import format_timestamp


def test_format_timestamp():
    """Test timestamp formatting function."""
    # Test basic formatting
    assert format_timestamp(0) == "00:00:00,000"
    assert format_timestamp(1) == "00:00:01,000"
    assert format_timestamp(60) == "00:01:00,000"
    assert format_timestamp(3600) == "01:00:00,000"
    
    # Test with fractional seconds
    assert format_timestamp(1.5) == "00:00:01,500"
    assert format_timestamp(61.25) == "00:01:01,250"


# Tests can be run with: python -m pytest tests/
# or poetry run pytest