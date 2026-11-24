"""SQLite Database module for conversation sessions, messages, feedback, and recurring mistake tracking."""

import sqlite3
import datetime
from typing import List, Dict, Any, Optional
from config.settings import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize SQLite database tables if they do not already exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Conversation sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                session_id TEXT PRIMARY KEY,
                scenario TEXT NOT NULL,
                proficiency_level TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT
            )
        """)
        
        # 2. Conversation messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                sender TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (session_id) ON DELETE CASCADE
            )
        """)
        
        # 3. Feedback
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                original_text TEXT NOT NULL,
                corrected_text TEXT NOT NULL,
                grammar_feedback TEXT,
                vocabulary_feedback TEXT,
                natural_expression TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (session_id) ON DELETE CASCADE
            )
        """)
        
        # 4. Practice history (tracks specific mistake categories for recurring issue analysis)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS practice_history (
                practice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                mistake_category TEXT NOT NULL,
                mistake_description TEXT NOT NULL,
                suggested_correction TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES conversation_sessions (session_id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()

# Session operations
def create_session(session_id: str, scenario: str, proficiency_level: str) -> bool:
    """Create a new conversation session record."""
    try:
        start_time = datetime.datetime.now().isoformat()
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversation_sessions (session_id, scenario, proficiency_level, start_time)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, scenario, proficiency_level, start_time)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB Error] Failed to create session: {e}")
        return False

def end_session(session_id: str) -> bool:
    """Mark a session as ended with current timestamp."""
    try:
        end_time = datetime.datetime.now().isoformat()
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE conversation_sessions SET end_time = ? WHERE session_id = ?",
                (end_time, session_id)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB Error] Failed to end session: {e}")
        return False

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve session details by ID."""
    try:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT * FROM conversation_sessions WHERE session_id = ?",
                (session_id,)
            ).fetchone()
            return dict(row) if row else None
    except Exception as e:
        print(f"[DB Error] Failed to get session: {e}")
        return None

def get_all_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    """Get list of past sessions ordered by newest first."""
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM conversation_sessions ORDER BY start_time DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB Error] Failed to fetch sessions: {e}")
        return []

# Message operations
def save_message(session_id: str, sender: str, message: str) -> bool:
    """Save an exchange message to the database."""
    try:
        now = datetime.datetime.now().isoformat()
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversation_messages (session_id, sender, message, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, sender, message, now)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB Error] Failed to save message: {e}")
        return False

def get_session_messages(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve all messages for a specific session."""
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT message_id, session_id, sender, message, timestamp
                FROM conversation_messages
                WHERE session_id = ?
                ORDER BY message_id ASC
                """,
                (session_id,)
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB Error] Failed to get session messages: {e}")
        return []

# Feedback operations
def save_feedback(
    session_id: str,
    original_text: str,
    corrected_text: str,
    grammar_feedback: str,
    vocabulary_feedback: str,
    natural_expression: str
) -> bool:
    """Save educational feedback record for a learner message."""
    try:
        now = datetime.datetime.now().isoformat()
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO feedback (
                    session_id, original_text, corrected_text,
                    grammar_feedback, vocabulary_feedback, natural_expression, timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id, original_text, corrected_text,
                    grammar_feedback, vocabulary_feedback, natural_expression, now
                )
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB Error] Failed to save feedback: {e}")
        return False

def get_session_feedback(session_id: str) -> List[Dict[str, Any]]:
    """Get all feedback items associated with a session."""
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM feedback WHERE session_id = ? ORDER BY feedback_id ASC",
                (session_id,)
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB Error] Failed to get feedback: {e}")
        return []

# Practice history & recurring mistakes
def save_practice_item(
    session_id: str,
    mistake_category: str,
    mistake_description: str,
    suggested_correction: str
) -> bool:
    """Log an identified mistake into practice history for recurring pattern tracking."""
    if not mistake_category or mistake_category.lower() in ("none", "n/a", ""):
        return True
    try:
        now = datetime.datetime.now().isoformat()
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO practice_history (
                    session_id, mistake_category, mistake_description,
                    suggested_correction, timestamp
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, mistake_category, mistake_description, suggested_correction, now)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB Error] Failed to save practice item: {e}")
        return False

def get_recurring_mistakes() -> List[Dict[str, Any]]:
    """Analyze practice history across all sessions to find recurring mistake patterns."""
    try:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT 
                    mistake_category,
                    mistake_description,
                    COUNT(*) as occurrence_count,
                    GROUP_CONCAT(suggested_correction, ' | ') as sample_corrections
                FROM practice_history
                WHERE mistake_category NOT IN ('None', 'none', '')
                GROUP BY mistake_category, mistake_description
                ORDER BY occurrence_count DESC
                LIMIT 10
                """
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB Error] Failed to aggregate recurring mistakes: {e}")
        return []

def get_overall_stats() -> Dict[str, Any]:
    """Calculate overall learning statistics across all sessions."""
    try:
        with get_db_connection() as conn:
            total_sessions = conn.execute("SELECT COUNT(*) FROM conversation_sessions").fetchone()[0]
            total_messages = conn.execute("SELECT COUNT(*) FROM conversation_messages WHERE sender = 'user'").fetchone()[0]
            total_corrections = conn.execute("SELECT COUNT(*) FROM practice_history WHERE mistake_category NOT IN ('None', 'none', '')").fetchone()[0]
            
            # Most practiced scenario
            scenario_row = conn.execute(
                """
                SELECT scenario, COUNT(*) as cnt
                FROM conversation_sessions
                GROUP BY scenario
                ORDER BY cnt DESC
                LIMIT 1
                """
            ).fetchone()
            most_practiced = scenario_row[0] if scenario_row else "None yet"
            
            # Mistake category breakdown
            category_rows = conn.execute(
                """
                SELECT mistake_category, COUNT(*) as cnt
                FROM practice_history
                WHERE mistake_category NOT IN ('None', 'none', '')
                GROUP BY mistake_category
                ORDER BY cnt DESC
                """
            ).fetchall()
            category_counts = {r[0]: r[1] for r in category_rows}

            # Scenario breakdown
            scenario_rows = conn.execute(
                """
                SELECT scenario, COUNT(*) as cnt
                FROM conversation_sessions
                GROUP BY scenario
                ORDER BY cnt DESC
                """
            ).fetchall()
            scenario_counts = {r[0]: r[1] for r in scenario_rows}

            return {
                "total_sessions": total_sessions,
                "total_user_messages": total_messages,
                "total_corrections": total_corrections,
                "most_practiced_scenario": most_practiced,
                "mistake_category_counts": category_counts,
                "scenario_counts": scenario_counts
            }
    except Exception as e:
        print(f"[DB Error] Failed to get overall stats: {e}")
        return {
            "total_sessions": 0,
            "total_user_messages": 0,
            "total_corrections": 0,
            "most_practiced_scenario": "None",
            "mistake_category_counts": {},
            "scenario_counts": {}
        }
