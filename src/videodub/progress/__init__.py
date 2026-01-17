"""Progress tracking utilities for VideoDub operations."""

from typing import Optional
import time
import threading
from abc import ABC, abstractmethod


class ProgressObserver(ABC):
    """Abstract base class for progress observers."""

    @abstractmethod
    def on_progress_update(self, progress: float, message: str = "") -> None:
        """Called when progress is updated."""
        pass

    @abstractmethod
    def on_complete(self) -> None:
        """Called when operation is complete."""
        pass


class ConsoleProgressObserver(ProgressObserver):
    """Console-based progress observer with visual progress bar."""

    def __init__(self, operation_name: str, total: float = 100.0):
        self.operation_name = operation_name
        self.total = total
        self.current = 0.0
        self.start_time = time.time()
        self._lock = threading.Lock()

    def on_progress_update(self, progress: float, message: str = "") -> None:
        """Update progress display in console."""
        with self._lock:
            self.current = min(progress, self.total)
            self._display_progress(message)

    def on_complete(self) -> None:
        """Display completion message."""
        elapsed = time.time() - self.start_time
        print(f"\r{self.operation_name} completed in {elapsed:.1f}s")

    def _display_progress(self, message: str = "") -> None:
        """Display progress bar in console."""
        percentage = (self.current / self.total) * 100
        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        # Calculate ETA
        if self.current > 0:
            elapsed = time.time() - self.start_time
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f" ({eta:.0f}s remaining)"
        else:
            eta_str = ""

        msg = f" {message}" if message else ""
        print(
            f"\r{self.operation_name}: [{bar}] {percentage:.1f}%{eta_str}{msg}",
            end="",
            flush=True,
        )


class ProgressTracker:
    """Main progress tracking class that manages observers."""

    def __init__(self, operation_name: str, total: float = 100.0):
        self.operation_name = operation_name
        self.total = total
        self.current = 0.0
        self.observers: list[ProgressObserver] = []
        self._lock = threading.Lock()

    def add_observer(self, observer: ProgressObserver) -> None:
        """Add a progress observer."""
        self.observers.append(observer)

    def update(self, progress: float, message: str = "") -> None:
        """Update progress for all observers."""
        with self._lock:
            self.current = min(progress, self.total)
            for observer in self.observers:
                observer.on_progress_update(self.current, message)

    def increment(self, amount: float = 1.0) -> None:
        """Increment progress by amount."""
        self.update(self.current + amount)

    def complete(self) -> None:
        """Mark operation as complete."""
        self.update(self.total)
        for observer in self.observers:
            observer.on_complete()


class TimeEstimator:
    """Utility class for estimating operation durations."""

    @staticmethod
    def estimate_ffmpeg_extraction_time(file_size_bytes: int) -> float:
        """Estimate FFmpeg extraction time based on file size."""
        mb_size = file_size_bytes / (1024 * 1024)
        # Rough estimation: ~2-3x real-time processing
        base_time_per_mb = 0.1  # seconds per MB
        safety_factor = 3.0
        return mb_size * base_time_per_mb * safety_factor

    @staticmethod
    def estimate_whisper_transcription_time(
        audio_duration: float, model_size: str = "small"
    ) -> float:
        """Estimate Whisper transcription time."""
        # Whisper processing factors by model size
        model_factors = {
            "tiny": 2.0,
            "base": 2.5,
            "small": 3.0,
            "medium": 3.5,
            "large": 4.0,
            "large-v2": 4.0,
            "large-v3": 4.2,
        }

        factor = model_factors.get(model_size, 3.0)
        return audio_duration * factor

    @staticmethod
    def get_video_duration(video_path: str) -> Optional[float]:
        """Get actual video duration using ffprobe."""
        try:
            import ffmpeg

            probe = ffmpeg.probe(video_path)
            # Try to get duration from the first stream
            for stream in probe.get("streams", []):
                if "duration" in stream:
                    return float(stream["duration"])
            # Fallback to format duration
            if "format" in probe and "duration" in probe["format"]:
                return float(probe["format"]["duration"])
        except Exception:
            pass
        return None
