"""Conversation Manager handling session lifecycle, context persistence, and AI roleplay orchestration."""

import uuid
from typing import List, Dict, Any, Optional, Tuple
from modules.database import create_session, end_session, save_message, get_session_messages
from modules.gemini_engine import GeminiEngine
from modules.text_to_speech import TextToSpeech
from config.settings import SCENARIOS

class ConversationManager:
    """Manages multi-turn conversation sessions, history, and message dispatch."""

    def __init__(self, gemini_engine: GeminiEngine, tts: Optional[TextToSpeech] = None):
        self.gemini = gemini_engine
        self.tts = tts or TextToSpeech()
        self.session_id: Optional[str] = None
        self.scenario_id: Optional[str] = None
        self.proficiency: str = "Beginner"
        self.messages: List[Dict[str, Any]] = []

    def start_session(self, scenario_id: str, proficiency: str) -> str:
        """Start a new roleplay conversation session and return session_id."""
        self.session_id = f"sess_{uuid.uuid4().hex[:12]}"
        self.scenario_id = scenario_id
        self.proficiency = proficiency
        self.messages = []

        # Persist session to SQLite
        create_session(self.session_id, scenario_id, proficiency)

        # Add initial scenario greeting from AI character
        scenario = SCENARIOS.get(scenario_id, SCENARIOS["shopping"])
        greeting = scenario["initial_greeting"]
        
        self.add_message("ai", greeting)
        return self.session_id

    def load_session(self, session_id: str, scenario_id: str, proficiency: str) -> None:
        """Load an existing session and its messages from the database."""
        self.session_id = session_id
        self.scenario_id = scenario_id
        self.proficiency = proficiency
        db_msgs = get_session_messages(session_id)
        self.messages = [{"sender": m["sender"], "message": m["message"]} for m in db_msgs]

    def add_message(self, sender: str, message: str) -> None:
        """Record a message in memory and write to database."""
        self.messages.append({"sender": sender, "message": message})
        if self.session_id:
            save_message(self.session_id, sender, message)

    def send_user_message(
        self,
        user_message: str,
        generate_audio: bool = True,
        voice: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Process learner message, get Gemini response, and synthesize speech.
        
        Args:
            user_message: Text entered or transcribed from the learner
            generate_audio: Whether to synthesize AI response audio via edge-tts
            voice: Optional TTS voice override
            
        Returns:
            Tuple of (success_bool, ai_response_text, audio_file_path_or_none)
        """
        clean_msg = user_message.strip()
        if not clean_msg:
            return False, "Message cannot be empty.", None

        # 1. Save user message
        self.add_message("user", clean_msg)

        # 2. Generate roleplay response from Gemini
        success, ai_reply = self.gemini.generate_roleplay_response(
            scenario_id=self.scenario_id or "shopping",
            proficiency=self.proficiency,
            messages=self.messages
        )

        if not success:
            # Revert or don't append faulty AI message, but preserve user message
            return False, ai_reply, None

        # 3. Save AI response
        self.add_message("ai", ai_reply)

        # 4. Synthesize AI speech if requested
        audio_path: Optional[str] = None
        if generate_audio:
            if voice:
                self.tts.set_voice(voice)
            tts_success, tts_res = self.tts.generate_speech(ai_reply)
            if tts_success:
                audio_path = tts_res

        return True, ai_reply, audio_path

    def finish_session(self) -> None:
        """Mark active session as completed."""
        if self.session_id:
            end_session(self.session_id)
