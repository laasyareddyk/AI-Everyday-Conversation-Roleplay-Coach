"""General helper functions for UI and data formatting."""

import datetime
from typing import Optional

def format_timestamp(ts_str: Optional[str] = None) -> str:
    """Format an ISO timestamp into a user-friendly string."""
    if not ts_str:
        return datetime.datetime.now().strftime("%b %d, %Y %I:%M %p")
    try:
        dt = datetime.datetime.fromisoformat(ts_str)
        return dt.strftime("%b %d, %Y %I:%M %p")
    except Exception:
        return ts_str

def get_proficiency_badge(level: str) -> str:
    """Return an HTML badge string for proficiency level."""
    colors = {
        "Beginner": "#10B981",      # Emerald
        "Intermediate": "#3B82F6",  # Blue
        "Advanced": "#8B5CF6"       # Purple
    }
    bg = colors.get(level, "#6B7280")
    return f'<span style="background-color: {bg}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.82rem; font-weight: 600;">{level}</span>'

def truncate_text(text: str, max_chars: int = 80) -> str:
    """Truncate text with ellipsis if it exceeds max_chars."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 3] + "..."
