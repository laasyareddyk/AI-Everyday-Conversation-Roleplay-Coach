"""Gemini AI conversational engine using the Google Gen AI SDK."""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from google import genai
from google.genai import types
from google.genai.errors import APIError

from config.settings import DEFAULT_GEMINI_MODEL
from prompts.roleplay_prompts import build_roleplay_system_prompt
from prompts.feedback_prompts import build_feedback_prompt

class GeminiEngine:
    """Manages Gemini model interactions for roleplay and pedagogical feedback."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        self.client: Optional[genai.Client] = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize the Google Gen AI Client if API key is present."""
        if self.api_key and self.api_key.strip():
            try:
                self.client = genai.Client(
                    api_key=self.api_key.strip(),
                    http_options=types.HttpOptions(timeout=15000)
                )
            except Exception as e:
                print(f"[GeminiEngine] Error initializing client: {e}")
                self.client = None
        else:
            self.client = None

    def update_credentials(self, api_key: str, model_name: Optional[str] = None) -> None:
        """Update API key and model dynamically at runtime."""
        self.api_key = api_key
        if model_name:
            self.model_name = model_name
        self._init_client()

    def is_configured(self) -> bool:
        """Check if client is configured with an API key."""
        return self.client is not None and bool(self.api_key)

    def generate_roleplay_response(
        self,
        scenario_id: str,
        proficiency: str,
        messages: List[Dict[str, str]]
    ) -> Tuple[bool, str]:
        """Generate the next in-character roleplay response.
        
        Args:
            scenario_id: Identifier for the scenario
            proficiency: Beginner, Intermediate, or Advanced
            messages: List of dicts with 'sender' ('user' or 'ai') and 'message'
            
        Returns:
            Tuple of (success_bool, response_text_or_error_msg)
        """
        if not self.is_configured():
            return False, "⚠️ Gemini API key is not configured. Please add your GEMINI_API_KEY in the Settings screen or .env file to enable live AI responses."

        system_instruction = build_roleplay_system_prompt(scenario_id, proficiency)

        try:
            contents = []
            for m in messages:
                role = "user" if m.get("sender") == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=m.get("message", ""))]
                    )
                )

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                max_output_tokens=300
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            if response and response.text:
                return True, response.text.strip()
            return False, "Received an empty response from Gemini. Please try again."

        except APIError as e:
            err_msg = str(e)
            if e.code == 503 or "503" in err_msg or "UNAVAILABLE" in err_msg:
                return False, f"⚠️ Gemini Model '{self.model_name}' is currently unavailable (503: High demand spike). Please try again shortly."
            if e.code == 504 or "504" in err_msg or "DEADLINE_EXCEEDED" in err_msg:
                return False, f"⚠️ Request to Gemini Model '{self.model_name}' timed out (504: Model temporarily unresponsive). Please try again shortly."
            if e.code == 404 or "404" in err_msg or "NOT_FOUND" in err_msg:
                return False, f"⚠️ Gemini Model '{self.model_name}' was not found or is unavailable for this API key."
            return False, f"⚠️ Gemini API Error ({e.code}): {e.message}"
        except Exception as e:
            err_str = str(e)
            if "503" in err_str or "UNAVAILABLE" in err_str:
                return False, f"⚠️ Gemini Model '{self.model_name}' is currently unavailable (503: High demand spike). Please try again shortly."
            if "504" in err_str or "DEADLINE_EXCEEDED" in err_str:
                return False, f"⚠️ Request to Gemini Model '{self.model_name}' timed out (504: Model temporarily unresponsive). Please try again shortly."
            if "404" in err_str or "NOT_FOUND" in err_str:
                return False, f"⚠️ Gemini Model '{self.model_name}' was not found or is unavailable for this API key."
            if "RESOURCE_EXHAUSTED" in err_str:
                return False, "⚠️ Gemini API Quota Exceeded. Please check your Gemini rate limits or billing."
            return False, f"⚠️ Error communicating with Gemini: {err_str}"

    def generate_feedback(
        self,
        scenario_title: str,
        proficiency: str,
        user_message: str,
        previous_messages: List[Dict[str, str]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Generate grammar and vocabulary feedback as a structured dictionary."""
        if not self.is_configured():
            return False, {
                "has_error": True,
                "error": "Gemini API key is not configured.",
                "original_text": user_message,
                "is_correct": False,
                "corrected_sentence": "⚠️ Correction unavailable (API key not configured)",
                "corrected_text": "⚠️ Correction unavailable (API key not configured)",
                "corrections_explanation": "Please add your GEMINI_API_KEY in Settings or .env to enable AI grammar corrections.",
                "grammar_feedback": "Please add your GEMINI_API_KEY in Settings or .env to enable AI grammar corrections.",
                "vocabulary_suggestions": "Vocabulary suggestions require an active Gemini API key.",
                "natural_alternative": user_message,
                "natural_alternative_explanation": "AI explanations require an active Gemini API key.",
                "natural_alternative_example": "Keep practicing your everyday English!",
                "fluency_and_clarity": "API key required for fluency analysis.",
                "mistake_category": "None",
                "mistake_description": "None",
                "encouraging_tip": "Configure your Gemini API key in Settings to unlock live feedback!"
            }

        prompt = build_feedback_prompt(scenario_title, proficiency, user_message, previous_messages)

        try:
            config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=700,
                response_mime_type="application/json"
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            raw_text = response.text if response and response.text else ""
            cleaned = self._clean_json_text(raw_text)
            feedback_data = json.loads(cleaned)

            # Ensure corrected_sentence is never simply a copy of an erroneous input
            corr = feedback_data.get("corrected_sentence") or feedback_data.get("corrected_text", "")
            is_correct = feedback_data.get("is_correct", False)

            if is_correct or corr.strip() == "No corrections needed." or corr.strip() == user_message.strip():
                if is_correct:
                    corr = "No corrections needed."

            feedback_data["corrected_sentence"] = corr
            feedback_data["corrected_text"] = corr
            feedback_data["has_error"] = False
            return True, feedback_data

        except json.JSONDecodeError:
            try:
                json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if json_match:
                    feedback_data = json.loads(json_match.group(0))
                    corr = feedback_data.get("corrected_sentence") or feedback_data.get("corrected_text", "")
                    if feedback_data.get("is_correct") and (not corr or corr.strip() == user_message.strip()):
                        corr = "No corrections needed."
                    feedback_data["corrected_sentence"] = corr
                    feedback_data["corrected_text"] = corr
                    feedback_data["has_error"] = False
                    return True, feedback_data
            except Exception:
                pass
            return False, {"error": "Failed to parse feedback response into structured JSON.", "has_error": True}
        except APIError as e:
            err_msg = str(e)
            if e.code == 503 or "503" in err_msg or "UNAVAILABLE" in err_msg:
                return False, {"error": f"⚠️ Gemini Model '{self.model_name}' is currently unavailable (503: High demand spike).", "has_error": True}
            if e.code == 504 or "504" in err_msg or "DEADLINE_EXCEEDED" in err_msg:
                return False, {"error": f"⚠️ Request to Gemini Model '{self.model_name}' timed out (504: Model unresponsive).", "has_error": True}
            if e.code == 404 or "404" in err_msg or "NOT_FOUND" in err_msg:
                return False, {"error": f"⚠️ Gemini Model '{self.model_name}' was not found or is unavailable for this API key.", "has_error": True}
            return False, {"error": f"⚠️ Gemini API Error ({e.code}): {e.message}", "has_error": True}
        except Exception as e:
            err_str = str(e)
            if "503" in err_str or "UNAVAILABLE" in err_str:
                return False, {"error": f"⚠️ Gemini Model '{self.model_name}' is currently unavailable (503: High demand spike).", "has_error": True}
            if "504" in err_str or "DEADLINE_EXCEEDED" in err_str:
                return False, {"error": f"⚠️ Request to Gemini Model '{self.model_name}' timed out (504: Model unresponsive).", "has_error": True}
            return False, {"error": f"Feedback generation failed: {err_str}", "has_error": True}

    @staticmethod
    def _clean_json_text(text: str) -> str:
        """Strip markdown fences from JSON output if present."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
