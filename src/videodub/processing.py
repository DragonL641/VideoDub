"""Video processing and subtitle generation."""

import os
import platform
import time
import threading
from pathlib import Path
from typing import Dict, Any

import ffmpeg
import torch
import whisper
from transformers import pipeline

from .config import Config
from .model_selection import select_optimal_model
from .progress import ProgressTracker, ConsoleProgressObserver, TimeEstimator


class VideoProcessor:
    """Handles video processing and subtitle generation."""

    def __init__(self) -> None:
        self.config = Config()

    def generate_subtitles(
        self,
        video_path: str,
        src_lang: str,
        tgt_lang: str,
        use_en_as_intermediate: bool,
    ) -> str:
        """
        Generate subtitles for a video file.

        Args:
            video_path: Path to the video file
            src_lang: Source language code
            tgt_lang: Target language code
            use_en_as_intermediate: Whether to use English as intermediate language

        Returns:
            Path to the generated subtitle file
        """
        # Validate inputs
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # 1. Select optimal model
        model_size = select_optimal_model()
        print(f"Loading model: {model_size}")

        # 2. Load Whisper model with performance optimizations
        device = self._select_device()
        print(f"Using device: {device}")

        # Load model (compute_type parameter may not be supported in all Whisper versions)
        model = whisper.load_model(model_size, device=device)

        # 3. Extract audio
        print("Extracting audio...")
        audio_path = self._extract_audio(video_path)

        try:
            # 4. Transcribe and translate
            result = self._transcribe_and_translate(
                model, audio_path, src_lang, tgt_lang, use_en_as_intermediate
            )

            # 5. Generate subtitle file
            output_path = self._generate_subtitle_file(video_path, result, tgt_lang)

            return output_path

        finally:
            # 6. Cleanup temporary files
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def _select_device(self) -> str:
        """Select the optimal computing device."""
        if platform.system().lower() == "darwin" and platform.processor() == "arm":
            return "cpu"  # Force CPU on Apple Silicon to avoid MPS issues
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"

    def _extract_audio(self, video_path: str) -> str:
        """Extract audio from video file with progress tracking."""
        # Ensure absolute paths for both video and audio files
        video_path = os.path.abspath(video_path)
        audio_path = os.path.abspath(self.config.TEMP_AUDIO_FILE)

        # Setup progress tracking
        file_size = os.path.getsize(video_path)
        # Better estimation: cap at reasonable values for small files
        estimated_time = min(
            TimeEstimator.estimate_ffmpeg_extraction_time(file_size), 30.0
        )
        progress_tracker = ProgressTracker("Extracting audio", estimated_time)
        console_observer = ConsoleProgressObserver("Extracting audio", estimated_time)
        progress_tracker.add_observer(console_observer)

        # Event to signal completion to monitoring thread
        completion_event = threading.Event()

        try:
            # Use ffmpeg-python for precise audio extraction with progress monitoring
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                audio_path,
                acodec="pcm_s16le",
                ac=1,
                ar=self.config.AUDIO_SAMPLE_RATE,
                vn=None,
                f="wav",
                loglevel="error",
                copyts=True,
            )

            # Start progress monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_ffmpeg_progress,
                args=(progress_tracker, estimated_time, completion_event),
            )
            monitor_thread.start()

            try:
                ffmpeg.run(
                    stream,
                    overwrite_output=True,
                    quiet=True,
                    capture_stdout=True,
                    capture_stderr=True,
                )
            finally:
                # Signal completion and wait for monitor thread
                completion_event.set()
                monitor_thread.join(timeout=1.0)  # Wait max 1 second
                progress_tracker.complete()

        except ffmpeg.Error as e:
            print(f"FFmpeg error during audio extraction: {e}")
            # Print detailed error information for debugging
            if e.stdout:
                print(f"FFmpeg stdout: {e.stdout.decode()}")
            if e.stderr:
                print(f"FFmpeg stderr: {e.stderr.decode()}")
            # Fallback to subprocess with proper argument separation
            # nosec B404: subprocess is needed for audio extraction, inputs are validated
            # nosec B603: command arguments are hardcoded, no user input in command
            try:
                import subprocess  # nosec B404

                cmd = [
                    "ffmpeg",
                    "-i",
                    video_path,
                    "-ar",
                    str(self.config.AUDIO_SAMPLE_RATE),
                    "-ac",
                    "1",
                    "-y",
                    "-loglevel",
                    "error",
                    "-copyts",
                    audio_path,
                ]
                # Validate paths before subprocess call
                if not os.path.exists(video_path):
                    raise ValueError(f"Input file does not exist: {video_path}")
                if not os.path.isabs(audio_path):
                    raise ValueError(f"Audio path must be absolute: {audio_path}")

                # Run subprocess with progress monitoring
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False
                )  # nosec B603

                # Monitor subprocess progress
                self._monitor_subprocess_progress(
                    process, progress_tracker, estimated_time, completion_event
                )

                _, stderr = process.communicate()
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(
                        process.returncode, cmd, stderr=stderr
                    )

            except Exception as subproc_error:
                print(f"Subprocess fallback also failed: {subproc_error}")
                raise RuntimeError(
                    f"Unable to extract audio from {video_path}"
                ) from subproc_error
            finally:
                # Signal completion and wait for monitor thread
                completion_event.set()
                # Note: monitor thread will be joined in outer finally block

        return audio_path

    def _transcribe_and_translate(
        self,
        model: Any,
        audio_path: str,
        src_lang: str,
        tgt_lang: str,
        use_en_as_intermediate: bool,
    ):
        """Transcribe audio and translate if needed with quality prioritized."""
        print("Recognizing speech...")

        # Since Whisper already provides its own progress, skip our progress tracking
        # to avoid double progress bars
        transcribe_kwargs = {
            "language": src_lang,
            "task": "transcribe",
            "verbose": False,  # Suppress Whisper's verbose output to avoid interference
        }

        # Perform transcription with quality settings
        transcription_result = model.transcribe(audio_path, **transcribe_kwargs)

        if src_lang != tgt_lang:
            return self._translate_segments(
                transcription_result, src_lang, tgt_lang, use_en_as_intermediate
            )
        else:
            return transcription_result

    def _translate_segments(
        self,
        result: Dict,
        src_lang: str,
        tgt_lang: str,
        use_en_as_intermediate: bool,
    ) -> Dict:
        """Translate transcribed segments."""
        print(f"Translating from {src_lang} to {tgt_lang}...")

        # Try direct translation first
        success = self._attempt_direct_translation(result, src_lang, tgt_lang)

        # If direct translation failed
        if not success:
            if use_en_as_intermediate:
                # Use English as intermediate: source -> English -> target
                result = self._translate_via_english(result, src_lang, tgt_lang)
            else:
                # Just translate to English only
                result = self._translate_to_english(result, src_lang)

        return result

    def _attempt_direct_translation(
        self, result: Dict, src_lang: str, tgt_lang: str
    ) -> bool:
        """Attempt direct translation from source to target language.
        Returns True if successful, False otherwise."""
        try:
            direct_model = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
            translator = pipeline("translation", model=direct_model, device="cpu")

            for i in range(len(result["segments"])):
                original_text = result["segments"][i]["text"].strip()
                if original_text:
                    try:
                        translation = translator(original_text)
                        translated_text = (
                            translation[0]["translation_text"]
                            if isinstance(translation, list) and len(translation) > 0
                            else str(translation)
                        )
                        result["segments"][i]["text"] = translated_text
                    except Exception as translation_error:
                        print(
                            f"Warning: Direct translation failed for segment {i}: {translation_error}"
                        )
                        # Keep original text if translation fails
            return True

        except Exception as e:
            print(f"Direct translation model loading failed: {e}")
            return False

    def _translate_to_english(self, result: Dict, src_lang: str) -> Dict:
        """Translate from source language to English with enhanced accuracy."""
        print("Translating to English as fallback...")
        try:
            # Try source to English model
            src_to_en_model = f"Helsinki-NLP/opus-mt-{src_lang}-en"
            src_to_en_translator = pipeline(
                "translation",
                model=src_to_en_model,
                device="cpu",
                max_length=512,
                truncation=True,
            )
        except Exception:
            # Try multilingual model as fallback
            src_to_en_translator = pipeline(
                "translation",
                model="Helsinki-NLP/opus-mt-mul-en",
                device="cpu",
                max_length=512,
                truncation=True,
            )

        for i in range(len(result["segments"])):
            original_text = result["segments"][i]["text"].strip()
            if original_text:
                try:
                    translation = src_to_en_translator(
                        original_text, max_length=512, truncation=True
                    )
                    translated_text = (
                        translation[0]["translation_text"]
                        if isinstance(translation, list) and len(translation) > 0
                        else str(translation)
                    )
                    result["segments"][i]["text"] = translated_text
                except Exception as translation_error:
                    print(
                        f"Warning: Translation to English failed for segment {i}: {translation_error}"
                    )
                    # Keep original text if translation fails

        return result

    def _translate_via_english(
        self, result: Dict, src_lang: str, tgt_lang: str
    ) -> Dict:
        """Translate via English as intermediate language."""
        print("Translating via English intermediate...")

        # Source to English
        try:
            src_to_en_model = f"Helsinki-NLP/opus-mt-{src_lang}-en"
            src_to_en_translator = pipeline(
                "translation", model=src_to_en_model, device="cpu"
            )
        except Exception:
            # Try multilingual model
            src_to_en_translator = pipeline(
                "translation", model="Helsinki-NLP/opus-mt-mul-en", device="cpu"
            )

        # English to target
        try:
            en_to_tgt_model = f"Helsinki-NLP/opus-mt-en-{tgt_lang}"
            en_to_tgt_translator = pipeline(
                "translation", model=en_to_tgt_model, device="cpu"
            )

            # Two-step translation
            for i in range(len(result["segments"])):
                original_text = result["segments"][i]["text"].strip()
                if original_text:
                    try:
                        # Step 1: Source -> English
                        en_translation = src_to_en_translator(original_text)
                        en_text = (
                            en_translation[0]["translation_text"]
                            if isinstance(en_translation, list)
                            and len(en_translation) > 0
                            else str(en_translation)
                        )

                        # Step 2: English -> Target
                        final_translation = en_to_tgt_translator(en_text)
                        final_text = (
                            final_translation[0]["translation_text"]
                            if isinstance(final_translation, list)
                            and len(final_translation) > 0
                            else str(final_translation)
                        )

                        result["segments"][i]["text"] = final_text
                    except Exception as translation_error:
                        print(
                            f"Warning: Two-step translation failed for segment {i}: {translation_error}"
                        )
                        # Keep original text if translation fails

        except Exception:
            # Fallback to source->English only
            for i in range(len(result["segments"])):
                original_text = result["segments"][i]["text"].strip()
                if original_text:
                    try:
                        translation = src_to_en_translator(original_text)
                        translated_text = (
                            translation[0]["translation_text"]
                            if isinstance(translation, list) and len(translation) > 0
                            else str(translation)
                        )
                        result["segments"][i]["text"] = translated_text
                    except Exception as translation_error:
                        print(
                            f"Warning: Source to English translation failed for segment {i}: {translation_error}"
                        )
                        # Keep original text if translation fails

        return result

    def _generate_subtitle_file(
        self, video_path: str, result: Dict, tgt_lang: str
    ) -> str:
        """Generate SRT subtitle file."""
        video_dir = os.path.dirname(video_path)
        video_name = Path(video_path).stem
        output_srt_path = os.path.join(video_dir, f"{video_name}_{tgt_lang}.srt")

        with open(output_srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], 1):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()

                f.write(f"{i}\n")
                f.write(
                    f"{self._format_timestamp(start)} --> {self._format_timestamp(end)}\n"
                )
                f.write(f"{text}\n\n")

        print(f"Subtitle generation complete: {output_srt_path}")
        return output_srt_path

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _monitor_ffmpeg_progress(
        self,
        progress_tracker: ProgressTracker,
        estimated_time: float,
        completion_event: threading.Event,
    ) -> None:
        """Monitor FFmpeg progress by simulating progress over estimated time."""
        start_time = time.time()
        update_interval = 0.3  # More frequent updates

        while (
            not completion_event.is_set() and time.time() - start_time < estimated_time
        ):
            elapsed = time.time() - start_time
            # More aggressive progress for small files, capped at 90%
            progress_ratio = min(elapsed / estimated_time, 0.9)
            progress = progress_ratio * 100
            progress_tracker.update(progress, "Processing audio")
            time.sleep(update_interval)

        # Don't call complete() here - let main thread handle it

    def _monitor_subprocess_progress(
        self,
        process,
        progress_tracker: ProgressTracker,
        estimated_time: float,
        completion_event: threading.Event,
    ) -> None:
        """Monitor subprocess progress."""
        start_time = time.time()
        update_interval = 0.3

        while (
            not completion_event.is_set()
            and process.poll() is None
            and time.time() - start_time < estimated_time
        ):
            elapsed = time.time() - start_time
            progress_ratio = min(elapsed / estimated_time, 0.9)
            progress = progress_ratio * 100
            progress_tracker.update(progress, "Running FFmpeg")
            time.sleep(update_interval)

        # Don't call complete() here - let main thread handle it

    def _monitor_transcription_progress(
        self,
        progress_tracker: ProgressTracker,
        estimated_time: float,
        completion_event: threading.Event,
    ) -> None:
        """Monitor Whisper transcription progress."""
        start_time = time.time()
        update_interval = 0.5  # Update twice per second

        while (
            not completion_event.is_set() and time.time() - start_time < estimated_time
        ):
            elapsed = time.time() - start_time
            # More realistic progress curve for transcription
            if elapsed < estimated_time * 0.3:
                # Slow start (loading model)
                progress = (elapsed / (estimated_time * 0.3)) * 30
            elif elapsed < estimated_time * 0.8:
                # Main processing phase
                progress = (
                    30
                    + ((elapsed - estimated_time * 0.3) / (estimated_time * 0.5)) * 60
                )
            else:
                # Final phase
                progress = (
                    90 + ((elapsed - estimated_time * 0.8) / (estimated_time * 0.2)) * 8
                )

            progress = min(progress, 98)  # Cap at 98%
            progress_tracker.update(progress, "Analyzing audio")
            time.sleep(update_interval)

        # Don't call complete() here - let main thread handle it
