"""Speech-to-Text module using faster-whisper for accurate, local microphone transcription."""

import os
from pathlib import Path
from typing import Optional, Union, Tuple

# Compatibility fix: PyAV 15+ removed 'metadata_errors' parameter which older faster-whisper uses
try:
    import av
    _orig_av_open = av.open
    def _safe_av_open(*args, **kwargs):
        kwargs.pop("metadata_errors", None)
        return _orig_av_open(*args, **kwargs)
    av.open = _safe_av_open
except Exception:
    pass

from faster_whisper import WhisperModel
from config.settings import DEFAULT_WHISPER_MODEL

class SpeechToText:
    """Wrapper around faster-whisper for local speech recognition."""
    
    _instance: Optional['SpeechToText'] = None
    _model: Optional[WhisperModel] = None
    _current_model_size: Optional[str] = None

    def __init__(self, model_size: Optional[str] = None):
        self.model_size = model_size or os.getenv("WHISPER_MODEL", DEFAULT_WHISPER_MODEL)

    def _load_model(self) -> None:
        """Load or retrieve singleton WhisperModel to avoid repeated downloads and memory allocations."""
        if SpeechToText._model is None or SpeechToText._current_model_size != self.model_size:
            try:
                # Use int8 compute_type for low CPU/memory footprint on Windows
                SpeechToText._model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"
                )
                SpeechToText._current_model_size = self.model_size
            except Exception as e:
                print(f"[SpeechToText] Error loading faster-whisper model '{self.model_size}': {e}")
                SpeechToText._model = None

    def transcribe(self, audio_source: Union[str, Path, bytes]) -> Tuple[bool, str]:
        """Transcribe an audio file or raw audio bytes into text.
        
        Args:
            audio_source: Path to audio file or raw bytes
            
        Returns:
            Tuple of (success_bool, transcribed_text_or_error_message)
        """
        # Validate inputs first before attempting model operations
        if isinstance(audio_source, bytes):
            if len(audio_source) == 0:
                return False, "Audio recording is empty. Please speak clearly into the microphone."
        elif isinstance(audio_source, (str, Path)):
            target_path_check = str(audio_source)
            if not os.path.exists(target_path_check) or os.path.getsize(target_path_check) == 0:
                return False, "Audio file is missing or empty."
        else:
            return False, "Unsupported audio input type."

        # Ensure model is initialized
        if SpeechToText._model is None or SpeechToText._current_model_size != self.model_size:
            self._load_model()
            if SpeechToText._model is None:
                return False, "Speech-to-Text model failed to load. Check internet connection or system resources."

        temp_file_created = False
        target_path: Optional[str] = None

        try:
            if isinstance(audio_source, bytes):
                from utils.audio_utils import save_temp_audio_bytes
                temp_file = save_temp_audio_bytes(audio_source, extension="wav")
                target_path = str(temp_file)
                temp_file_created = True
            else:
                target_path = str(audio_source)

            # Perform speech recognition
            segments, info = SpeechToText._model.transcribe(
                target_path,
                beam_size=5,
                language="en",
                vad_filter=True
            )

            # Join transcribed segments
            transcription = " ".join([segment.text.strip() for segment in segments]).strip()

            if not transcription:
                return False, "No speech detected in the recording. Please try speaking again."

            return True, transcription

        except Exception as e:
            return False, f"Transcription error: {str(e)}"

        finally:
            if temp_file_created and target_path and os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except Exception:
                    pass
