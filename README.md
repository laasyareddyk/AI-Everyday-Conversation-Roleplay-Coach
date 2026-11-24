# 🗣️ AI Everyday Conversation Roleplay Coach

> An interactive, beginner-friendly AI-powered conversational English practice platform that simulates everyday situations (shopping, interviews, travel, dining, and self-introductions). Learners can converse through speech or text, receive supportive grammar corrections, learn natural alternative expressions, and track their improvement over time.

---

## 📖 Table of Contents

- [1. Project Description](#1-project-description)
- [2. Problem Statement](#2-problem-statement)
- [3. Project Objectives](#3-project-objectives)
- [4. Target Users](#4-target-users)
- [5. Core Features](#5-core-features)
- [6. Application User Flow](#6-application-user-flow)
- [7. Technology Stack](#7-technology-stack)
- [8. Project Folder Structure](#8-project-folder-structure)
- [9. Installation & Virtual Environment Setup](#9-installation--virtual-environment-setup)
- [10. Gemini API Configuration](#10-gemini-api-configuration)
- [11. WhisperFlow Implementation (STT & TTS)](#11-whisperflow-implementation-stt--tts)
- [12. SQLite Database Architecture](#12-sqlite-database-architecture)
- [13. How to Run the Application](#13-how-to-run-the-application)
- [14. Testing & Verification](#14-testing--verification)
- [15. Screenshots & UI Walkthrough](#15-screenshots--ui-walkthrough)
- [16. Future Enhancements](#16-future-enhancements)
- [17. License](#17-license)

---

## 1. Project Description

**AI Everyday Conversation Roleplay Coach** is an EdTech web application built with Streamlit, Google Gemini AI, faster-whisper, and Edge TTS. It addresses the common challenge faced by second-language learners who study vocabulary lists and grammar rules but lack confidence and spontaneous fluency in real-life spoken English.

Through five realistic everyday roleplay scenarios, learners interact with personalized AI roleplay partners (a Shopkeeper, Hiring Manager, Airport Staff, Waiter, or Social Partner) who adapt to their proficiency level (Beginner, Intermediate, Advanced). Learners can speak into their microphone or type messages, and receive constructive, encouraging feedback including grammar corrections, richer vocabulary suggestions, and native-speaker natural expressions.

---

## 2. Problem Statement

Language learners frequently experience the **"silent fluency gap"**: they can read vocabulary lists and score well on written tests, but struggle to speak naturally during everyday social interactions such as ordering in a restaurant, asking for sizes at a clothing store, or answering questions in a job interview. Traditional classroom setups rarely offer sufficient one-on-one conversation time or real-time diagnostic feedback.

This project bridges that gap by providing a private, supportive, zero-judgment conversational training environment with voice-first interaction and recurring mistake tracking.

---

## 3. Project Objectives

1. **Practical Roleplay Immersion**: Create dynamic, non-scripted conversational simulations for five everyday life situations.
2. **Proficiency Level Adaptation**: Tailor vocabulary complexity, sentence length, and conversation pacing to Beginner, Intermediate, and Advanced learners.
3. **Dual Voice Flow (WhisperFlow)**: Implement bidirectional voice interaction—local microphone speech-to-text with `faster-whisper` and natural neural speech synthesis with `edge-tts`.
4. **Pedagogical Feedback**: Separate roleplay immersion from educational feedback so the conversation flows naturally without interruptions.
5. **Authentic Natural Expressions**: Teach learners how native speakers actually express common thoughts (e.g. replacing *"I need one help"* with *"Could you help me with something?"*).
6. **Recurring Mistake Diagnostics**: Aggregate past mistakes in SQLite to identify repeating error patterns across sessions (such as missing articles or plural confusion).

---

## 4. Target Users

- **Language Learners & Beginners**: Individuals learning English who need a friendly, patient conversation partner.
- **Job Applicants & Students**: Candidates preparing for English-language interviews, university admissions, or travel.
- **Immigrants & International Travelers**: Individuals navigating practical situations like airports, restaurants, and retail shops.
- **EdTech Educators**: Teachers seeking an interactive practice tool to complement classroom instruction.

---

## 5. Core Features

- **5 Real-Life Scenarios**:
  1. *Shopping*: Roleplay with a friendly shopkeeper to ask about products, sizes, prices, and discounts.
  2. *Job Interview*: Roleplay with a professional interviewer covering self-introductions, skills, strengths, and career aspirations.
  3. *Travel / Airport*: Roleplay with airport customer service covering check-in, baggage, boarding, and security.
  4. *Restaurant*: Roleplay with an attentive waiter to order food, ask about specials, and request the bill.
  5. *Self-Introduction*: Roleplay with a warm conversational partner to practice introducing oneself in social settings.
- **3 Adaptive Proficiency Levels**:
  - *Beginner*: Simple words, short sentences (1–2 sentences), gentle pacing, and one simple follow-up question.
  - *Intermediate*: Everyday conversational English, moderate vocabulary, common idioms, and contextual follow-ups.
  - *Advanced*: Professional, fluent English with nuanced phrasing, idiomatic expressions, and realistic challenges.
- **WhisperFlow (Dual Voice Pipeline)**:
  - *Audio-to-Text*: Record microphone speech via `st.audio_input`, transcribe locally using `faster-whisper` (int8 quantized base model).
  - *Editable Transcription*: Review and edit the recognized text before sending it to Gemini.
  - *Text-to-Audio*: Synthesize AI responses into natural neural MP3 speech with `edge-tts` and replay anytime.
- **Comprehensive Educational Feedback**:
  - Grammar correction (Original vs. Corrected with highlighted differences).
  - Clear, kind explanations of grammatical rules.
  - Contextual vocabulary suggestions.
  - Native-speaker natural expressions with real-world examples.
  - Fluency, pacing, and clarity comments.
- **Learning Progress & Mistake Diagnostics**:
  - SQLite persistent database storing sessions, messages, feedback, and practice history.
  - Recurring mistake tracker that aggregates patterns across previous sessions (e.g., Article, Plural, Tense, Preposition errors).
  - Actionable recommendations tailored to detected error habits.
  - Interactive Plotly charts (Practice distribution by scenario, mistakes by category).

---

## 6. Application User Flow

```
[1. Select Scenario & Proficiency Level]
              ↓
[2. AI Character Initiates Real-Life Greeting]
              ↓
[3. Learner Speaks via Mic or Types Text]
              ↓
[4. Whisper Transcribes Audio (Editable by Learner)]
              ↓
[5. Gemini AI Generates In-Character Response]
              ↓
[6. Edge TTS Generates MP3 Spoken Audio]
              ↓
[7. Learner Listens & Continues Roleplay]
              ↓
[8. Learner Requests Feedback / Ends Conversation]
              ↓
[9. System Stores Mistakes & Updates Progress Dashboard]
```

---

## 7. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Programming Language** | Python 3.10+ / 3.14 | Core application logic |
| **Web Framework** | Streamlit 1.38+ | Frontend UI, audio recording, and navigation |
| **AI LLM Engine** | Google Gen AI SDK (`google-genai`) | Multi-turn contextual roleplay & educational feedback |
| **Speech-to-Text (STT)** | `faster-whisper` (CTranslate2) | Fast local microphone speech transcription |
| **Text-to-Speech (TTS)** | `edge-tts` | High-quality Microsoft neural speech synthesis |
| **Database** | SQLite 3 | Persistent storage for sessions, messages, feedback, and history |
| **Data Visualizations** | Plotly & Pandas | Learning progress charts and metric displays |
| **Configuration** | `python-dotenv` | Secure API key and environment management |
| **Testing** | `pytest` | Unit tests with mocks and live integration tests |

---

## 8. Project Folder Structure

```
ai-everyday-conversation-coach/
│
├── app.py                     # Main Streamlit application entry point & router
├── requirements.txt           # Python package dependencies
├── .env.example               # Example environment variable file
├── .gitignore                 # Files excluded from git tracking
├── README.md                  # Comprehensive project documentation
│
├── config/
│   ├── __init__.py
│   └── settings.py            # App configurations, scenarios, levels, voices
│
├── modules/
│   ├── __init__.py
│   ├── database.py            # SQLite schema, queries, recurring mistake analysis
│   ├── gemini_engine.py       # Google Gen AI SDK wrapper & error handling
│   ├── conversation_manager.py# Multi-turn roleplay session lifecycle
│   ├── speech_to_text.py      # faster-whisper local STT with PyAV 15+ compatibility
│   ├── text_to_speech.py      # edge-tts neural voice synthesis to MP3
│   ├── whisper_flow.py        # End-to-end voice pipeline coordinator
│   ├── feedback_engine.py     # Educational grammar and vocabulary evaluation
│   └── progress_tracker.py    # Metric aggregation & Plotly chart generators
│
├── prompts/
│   ├── __init__.py
│   ├── roleplay_prompts.py    # Roleplay system instructions for 5 scenarios
│   └── feedback_prompts.py    # Structured JSON feedback prompts
│
├── pages/
│   ├── __init__.py
│   ├── dashboard.py           # Screen 1: Home & Dashboard
│   ├── scenarios.py           # Screen 2: Scenario & Level Selection
│   ├── conversation.py        # Screen 3: AI Conversation Room (Voice/Text)
│   ├── feedback.py            # Screen 4: Language Feedback & Natural Expressions
│   ├── progress.py            # Screen 5: Learning Progress & Diagnostics
│   └── settings.py            # Screen 6: API & Audio Settings
│
├── assets/
│   └── style.css              # Custom modern EdTech styling
│
├── data/
│   ├── .gitkeep
│   └── coach.db               # SQLite database (created automatically)
│
├── temp_audio/                # Temporary directory for generated MP3/WAV files
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py             # Date formatting and badge utilities
│   └── audio_utils.py         # Temporary audio storage & cleanup
│
└── tests/
    ├── __init__.py
    ├── fixtures/
    │   └── sample.mp3         # Audio fixture for live transcription tests
    ├── test_database.py       # SQLite database & recurring mistake tests
    ├── test_conversation.py   # ConversationManager & roleplay tests
    ├── test_whisper_flow.py   # STT, TTS, and WhisperFlow tests
    ├── test_feedback.py       # FeedbackEngine & JSON parsing tests
    └── test_live_audio_transcription.py # Live faster-whisper inference test
```

---

## 9. Installation & Virtual Environment Setup

### 1. Clone or Open the Workspace
```bash
cd "AI _Everyday _Conversation _Roleplay _Coach"
```

### 2. Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 10. Gemini API Configuration

1. Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com).
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Set your API key in `.env`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-3.8-flash
   WHISPER_MODEL=base
   TTS_VOICE=en-US-AriaNeural
   ```
4. Alternatively, you can configure your API key at runtime in the **Settings (⚙️)** screen within the web application.

---

## 11. WhisperFlow Implementation (STT & TTS)

WhisperFlow is the application's dedicated dual-directional voice module:

### A. Speech-to-Text (`modules/speech_to_text.py`)
- Powered by `faster-whisper` (running local quantized int8 models on CPU).
- Takes actual microphone audio from Streamlit's native `st.audio_input` component.
- Transcribes audio into readable English text.
- Includes a compatibility wrapper for PyAV 15+ ensuring seamless audio container reading.
- Allows the learner to review and edit recognized speech before submitting.

### B. Text-to-Speech (`modules/text_to_speech.py`)
- Powered by `edge-tts`.
- Converts Gemini's text responses into natural, lifelike MP3 speech.
- Supports multiple English neural voices (US, UK, and Australian accents).
- Displays an inline audio player directly beneath each AI response for listening and replays.

---

## 12. SQLite Database Architecture

The SQLite database (`data/coach.db`) automatically initializes on startup with four relational tables:

1. `conversation_sessions`:
   - `session_id` (TEXT PRIMARY KEY)
   - `scenario` (TEXT)
   - `proficiency_level` (TEXT)
   - `start_time` (TEXT)
   - `end_time` (TEXT)

2. `conversation_messages`:
   - `message_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `session_id` (TEXT FOREIGN KEY)
   - `sender` (TEXT: 'user' or 'ai')
   - `message` (TEXT)
   - `timestamp` (TEXT)

3. `feedback`:
   - `feedback_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `session_id` (TEXT FOREIGN KEY)
   - `original_text` (TEXT)
   - `corrected_text` (TEXT)
   - `grammar_feedback` (TEXT)
   - `vocabulary_feedback` (TEXT)
   - `natural_expression` (TEXT)
   - `timestamp` (TEXT)

4. `practice_history`:
   - `practice_id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `session_id` (TEXT FOREIGN KEY)
   - `mistake_category` (TEXT)
   - `mistake_description` (TEXT)
   - `suggested_correction` (TEXT)
   - `timestamp` (TEXT)

---

## 13. How to Run the Application

Launch the application using Streamlit:

```bash
streamlit run app.py
```

Open your web browser and navigate to:
```
http://localhost:8501
```

---

## 14. Testing & Verification

The project includes an automated test suite with 17 unit and integration tests covering database operations, roleplay conversation management, WhisperFlow speech recognition, Edge TTS synthesis, and educational feedback:

```bash
# Run the entire test suite
pytest tests/ -v
```

### Test Results Summary:
- **`tests/test_database.py`**: Tables initialization, session lifecycle, message storage, feedback persistence, recurring mistake aggregation, overall stats calculation. (Passed)
- **`tests/test_conversation.py`**: Session startup, initial greeting, sending user messages, roleplay reply generation, empty input validation. (Passed)
- **`tests/test_whisper_flow.py`**: Empty audio validation, missing file handling, WhisperFlow STT/TTS coordination with mocks. (Passed)
- **`tests/test_feedback.py`**: Structured JSON feedback parsing, database logging, mistake categorization, and fallback when API is unconfigured. (Passed)
- **`tests/test_live_audio_transcription.py`**: Real local `faster-whisper` inference on actual audio fixture, verifying live AI transcription. (Passed)

---

## 15. Screenshots & UI Walkthrough

1. **Dashboard (Screen 1)**: Key metrics, scenario quick-start cards, and WhisperFlow workflow explanation.
2. **Scenario Selection (Screen 2)**: Proficiency level configuration (Beginner, Intermediate, Advanced) and 5 detailed scenario cards.
3. **AI Conversation Room (Screen 3)**: Interactive chat with AI audio player, microphone voice recorder, editable transcription, and text input.
4. **Supportive Feedback (Screen 4)**: Sentence improvement cards, grammar explanations, vocabulary boosts, and natural native expressions with examples.
5. **Learning Progress (Screen 5)**: Recurring mistake diagnostics with coach tips, Plotly charts, and past session history.
6. **Settings (Screen 6)**: Live API key configuration, connection tester, voice selector, and Whisper model selection.

---

## 16. Future Enhancements

- **Pronunciation Scoring**: Integrate phoneme-level pronunciation scoring (e.g. via wav2vec2 or CTC forced alignment).
- **Custom Scenario Builder**: Allow teachers and learners to define custom roles, scenarios, and vocabulary goals.
- **Speech Speed Control**: Add adjustable playback rate (0.75x, 1.0x, 1.25x) for beginners.
- **Export Learning Summary**: Generate downloadable PDF or markdown learning progress reports.

---

## 17. License

MIT License. Developed for educational purposes.
