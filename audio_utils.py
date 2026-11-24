"""Audio utility functions for temporary storage and format handling."""

import os
import uuid
from pathlib import Path
from typing import Optional
from config.settings import TEMP_AUDIO_DIR

def save_temp_audio_bytes(audio_bytes: bytes, extension: str = "wav") -> Path:
    """Save raw audio bytes to a temporary file and return its path."""
    TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"rec_{uuid.uuid4().hex[:8]}.{extension}"
    file_path = TEMP_AUDIO_DIR / filename
    with open(file_path, "wb") as f:
        f.write(audio_bytes)
    return file_path

def cleanup_old_audio_files(max_files: int = 30) -> None:
    """Clean up old temporary audio files to conserve disk space."""
    if not TEMP_AUDIO_DIR.exists():
        return
    try:
        files = sorted(
            TEMP_AUDIO_DIR.glob("*"),
            key=lambda x: x.stat().st_mtime if x.is_file() else 0
        )
        if len(files) > max_files:
            for f in files[:-max_files]:
                try:
                    f.unlink(missing_ok=True)
                except Exception:
                    pass
    except Exception:
        pass
