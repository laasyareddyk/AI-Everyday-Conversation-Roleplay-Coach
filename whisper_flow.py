"""WhisperFlow: End-to-end Voice Interaction Pipeline coordinating STT and TTS."""

from pathlib import Path
from typing import Optional, Union, Tuple
from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech

class WhisperFlow:
    """Coordinates Audio-to-Text (faster-whisper) and Text-to-Audio (edge-tts)."""

    def __init__(self, whisper_model: Optional[str] = None, tts_voice: Optional[str] = None):
        self.stt = SpeechToText(model_size=whisper_model)
        self.tts = TextToSpeech(voice=tts_voice)

    def transcribe_audio(self, audio_source: Union[str, Path, bytes]) -> Tuple[bool, str]:
        """Convert learner's spoken audio into editable text using faster-whisper.
        
        Args:
            audio_source: Audio file path or raw bytes from microphone input
            
        Returns:
            Tuple of (success_bool, transcribed_text_or_error_message)
        """
        return self.stt.transcribe(audio_source)

    def generate_speech(self, text: str, voice: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Synthesize AI text response into realistic spoken audio using edge-tts.
        
        Args:
            text: AI response text
            voice: Optional TTS voice override
            
        Returns:
            Tuple of (success_bool, path_to_mp3_or_error_message)
        """
        if voice:
            self.tts.set_voice(voice)
        return self.tts.generate_speech(text)
