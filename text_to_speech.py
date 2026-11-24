"""Text-to-Speech module using edge-tts for natural, lifelike English speech generation."""

import asyncio
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
import edge_tts

from config.settings import DEFAULT_TTS_VOICE, TEMP_AUDIO_DIR

class TextToSpeech:
    """Generates natural English MP3 audio using edge-tts."""

    def __init__(self, voice: Optional[str] = None):
        self.voice = voice or os.getenv("TTS_VOICE", DEFAULT_TTS_VOICE)

    def set_voice(self, voice: str) -> None:
        """Update active TTS voice."""
        self.voice = voice

    async def _generate_audio_async(self, text: str, output_path: str) -> None:
        """Async worker to fetch edge-tts audio stream and save to output file."""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def generate_speech(self, text: str, output_filename: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Synthesize text into natural speech and save as an MP3 file.
        
        Args:
            text: Text string to synthesize
            output_filename: Optional custom output file name
            
        Returns:
            Tuple of (success_bool, path_to_mp3_or_error_msg)
        """
        clean_text = text.strip()
        if not clean_text:
            return False, "Text for speech generation cannot be empty."

        TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        if not output_filename:
            output_filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        output_path = str(TEMP_AUDIO_DIR / output_filename)

        try:
            # Safely run async synthesis in dedicated event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._generate_audio_async(clean_text, output_path))
            finally:
                loop.close()

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return True, output_path
            return False, "Audio synthesis produced empty file."

        except Exception as e:
            return False, f"TTS synthesis error: {str(e)}"
