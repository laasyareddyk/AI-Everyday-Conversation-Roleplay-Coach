"""AI Everyday Conversation Roleplay Coach - Main Streamlit Application."""

import os
import streamlit as st
from pathlib import Path

from config.settings import (
    ASSETS_DIR,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_WHISPER_MODEL,
    DEFAULT_TTS_VOICE,
    SCENARIOS
)
from modules.database import init_db
from modules.gemini_engine import GeminiEngine
from modules.whisper_flow import WhisperFlow
from modules.conversation_manager import ConversationManager
from modules.feedback_engine import FeedbackEngine

from pages.dashboard import render_dashboard
from pages.scenarios import render_scenarios
from pages.conversation import render_conversation
from pages.feedback import render_feedback
from pages.progress import render_progress
from pages.settings import render_settings

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Everyday Conversation Coach",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load CSS ---
def load_css() -> None:
    css_path = ASSETS_DIR / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# --- Initialize SQLite Database ---
init_db()

# --- Initialize Session State ---
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "dashboard"

if "gemini_api_key" not in st.session_state:
    st.session_state["gemini_api_key"] = os.getenv("GEMINI_API_KEY", "")

if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)

if "tts_voice" not in st.session_state:
    st.session_state["tts_voice"] = os.getenv("TTS_VOICE", DEFAULT_TTS_VOICE)

if "whisper_model" not in st.session_state:
    st.session_state["whisper_model"] = os.getenv("WHISPER_MODEL", DEFAULT_WHISPER_MODEL)

if "selected_scenario" not in st.session_state:
    st.session_state["selected_scenario"] = "shopping"

if "proficiency_level" not in st.session_state:
    st.session_state["proficiency_level"] = "Beginner"

if "active_session_id" not in st.session_state:
    st.session_state["active_session_id"] = None

if "conversation_messages" not in st.session_state:
    st.session_state["conversation_messages"] = []

if "last_feedback" not in st.session_state:
    st.session_state["last_feedback"] = None

if "stt_transcription" not in st.session_state:
    st.session_state["stt_transcription"] = ""

if "last_processed_audio_hash" not in st.session_state:
    st.session_state["last_processed_audio_hash"] = None


# --- Cache Backend Engines ---
@st.cache_resource
def get_gemini_engine(api_key: str, model_name: str) -> GeminiEngine:
    return GeminiEngine(api_key=api_key, model_name=model_name)

@st.cache_resource
def get_whisper_flow(whisper_model: str, tts_voice: str) -> WhisperFlow:
    return WhisperFlow(whisper_model=whisper_model, tts_voice=tts_voice)

# Instantiate engines
gemini_engine = get_gemini_engine(
    st.session_state["gemini_api_key"],
    st.session_state["gemini_model"]
)
whisper_flow = get_whisper_flow(
    st.session_state["whisper_model"],
    st.session_state["tts_voice"]
)
conv_manager = ConversationManager(gemini_engine=gemini_engine, tts=whisper_flow.tts)
feedback_engine = FeedbackEngine(gemini_engine=gemini_engine)

# Keep API credentials updated on the engine
if st.session_state["gemini_api_key"] != gemini_engine.api_key or st.session_state["gemini_model"] != gemini_engine.model_name:
    gemini_engine.update_credentials(
        st.session_state["gemini_api_key"],
        st.session_state["gemini_model"]
    )


# --- Page Navigation Routing Helper ---
def switch_page(page_name: str, start_new: bool = False):
    """Safely change page view and optionally reset active conversation session."""
    if start_new:
        st.session_state["active_session_id"] = None
        st.session_state["conversation_messages"] = []
        st.session_state["last_feedback"] = None
        st.session_state["stt_transcription"] = ""
        st.session_state["last_processed_audio_hash"] = None
    st.session_state["current_page"] = page_name
    st.rerun()


# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
            <div style="font-size: 2.8rem; line-height: 1;">🗣️</div>
            <h2 style="margin: 0.3rem 0 0 0; font-size: 1.25rem; color: #1E293B;">Conversation Coach</h2>
            <span style="font-size: 0.8rem; color: #64748B;">AI Everyday English Roleplay</span>
        </div>
    """, unsafe_allow_html=True)

    pages = {
        "dashboard": "🏠 Home / Dashboard",
        "scenarios": "🎯 Scenario Selection",
        "conversation": "💬 AI Conversation Room",
        "feedback": "📝 Language Feedback",
        "progress": "📊 Learning Progress",
        "settings": "⚙️ Settings & API"
    }

    # Radio button navigation synced with session_state
    page_keys = list(pages.keys())
    page_labels = list(pages.values())
    curr_idx = page_keys.index(st.session_state["current_page"]) if st.session_state["current_page"] in page_keys else 0

    selected_label = st.radio(
        "Navigation",
        options=page_labels,
        index=curr_idx,
        label_visibility="collapsed"
    )
    new_page = page_keys[page_labels.index(selected_label)]
    if new_page != st.session_state["current_page"]:
        st.session_state["current_page"] = new_page
        st.rerun()

    st.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Active Session Info Pill
    curr_sc = SCENARIOS.get(st.session_state.get("selected_scenario"), {})
    st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 0.7rem; border: 1px solid #E2E8F0; font-size: 0.82rem; margin-bottom: 0.8rem;">
            <div><strong>Active Scenario:</strong> {curr_sc.get('icon', '')} {curr_sc.get('title', 'Shopping')}</div>
            <div style="margin-top: 0.2rem;"><strong>Level:</strong> {st.session_state.get('proficiency_level', 'Beginner')}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("➕ Start New Session", use_container_width=True):
        switch_page("scenarios", start_new=True)

    st.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # System Status Badges
    st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 0.4rem;'>System Status</div>", unsafe_allow_html=True)
    if gemini_engine.is_configured():
        st.markdown("🟢 <span style='font-size:0.85rem;'>Gemini API: <strong>Connected</strong></span>", unsafe_allow_html=True)
    else:
        st.markdown("🟡 <span style='font-size:0.85rem;'>Gemini API: <em>Key Needed</em></span>", unsafe_allow_html=True)
    st.markdown("🟢 <span style='font-size:0.85rem;'>Whisper STT: <strong>Ready</strong></span>", unsafe_allow_html=True)
    st.markdown("🟢 <span style='font-size:0.85rem;'>Edge TTS: <strong>Ready</strong></span>", unsafe_allow_html=True)
    st.markdown("🟢 <span style='font-size:0.85rem;'>SQLite DB: <strong>Connected</strong></span>", unsafe_allow_html=True)


# --- Page Routing ---
current_page = st.session_state.get("current_page", "dashboard")

if current_page == "dashboard":
    render_dashboard(switch_page)
elif current_page == "scenarios":
    render_scenarios(switch_page)
elif current_page == "conversation":
    render_conversation(
        gemini_engine=gemini_engine,
        whisper_flow=whisper_flow,
        conv_manager=conv_manager,
        feedback_engine=feedback_engine,
        switch_page_fn=switch_page
    )
elif current_page == "feedback":
    render_feedback(switch_page)
elif current_page == "progress":
    render_progress(switch_page)
elif current_page == "settings":
    render_settings(gemini_engine=gemini_engine)
else:
    render_dashboard(switch_page)
