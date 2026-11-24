"""Learning Progress Tracker and Visualizations using SQLite and Plotly."""

from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.database import get_overall_stats, get_recurring_mistakes, get_all_sessions
from config.settings import SCENARIOS

class ProgressTracker:
    """Aggregates metrics, diagnoses recurring language mistakes, and produces Plotly charts."""

    @staticmethod
    def get_summary_metrics() -> Dict[str, Any]:
        """Retrieve high-level summary learning statistics."""
        return get_overall_stats()

    @staticmethod
    def get_recurring_mistake_insights() -> List[Dict[str, Any]]:
        """Identify recurring grammar and vocabulary mistake areas across previous sessions."""
        mistakes = get_recurring_mistakes()
        insights = []

        advice_map = {
            "Article": "You frequently miss or misplace articles (a, an, the). Remember: use 'a' before consonant sounds, 'an' before vowel sounds, and omit before plurals.",
            "Plural": "Watch out for plural nouns! Uncountable nouns or plural nouns do not take 'a' or 'an' (e.g. 'I want shoes' instead of 'I want a shoes').",
            "Tense": "Pay close attention to verb tenses when describing past experiences or future goals.",
            "Preposition": "Prepositions (in, on, at, to) can be tricky. Try memorizing common fixed collocations.",
            "Vocabulary": "Work on expanding your situational vocabulary to sound more natural and varied.",
            "Word Order": "Keep standard English word order: Subject + Verb + Object in declarative sentences."
        }

        for item in mistakes:
            cat = item.get("mistake_category", "Grammar")
            desc = item.get("mistake_description", "")
            count = item.get("occurrence_count", 0)
            custom_tip = advice_map.get(cat, f"Focus on reviewing {cat.lower()} rules in everyday practice.")
            
            insights.append({
                "category": cat,
                "description": desc,
                "count": count,
                "advice": custom_tip,
                "samples": item.get("sample_corrections", "")
            })

        return insights

    @staticmethod
    def create_category_chart(category_counts: Dict[str, int]) -> Optional[go.Figure]:
        """Create a Plotly bar chart showing distribution of mistake categories."""
        if not category_counts:
            return None

        df = pd.DataFrame(list(category_counts.items()), columns=["Category", "Occurrences"])
        df = df.sort_values(by="Occurrences", ascending=True)

        fig = px.bar(
            df,
            x="Occurrences",
            y="Category",
            orientation="h",
            title="Grammar & Vocabulary Practice Areas",
            color="Occurrences",
            color_continuous_scale="Purples"
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", size=13),
            margin=dict(l=20, r=20, t=40, b=20),
            height=320,
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
            yaxis=dict(showgrid=False)
        )
        return fig

    @staticmethod
    def create_scenario_chart(scenario_counts: Dict[str, int]) -> Optional[go.Figure]:
        """Create a Plotly donut chart showing practice sessions per scenario."""
        if not scenario_counts:
            return None

        # Map scenario keys to nice titles
        labels = [SCENARIOS.get(k, {}).get("title", k.replace("_", " ").title()) for k in scenario_counts.keys()]
        values = list(scenario_counts.values())

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker_colors=["#6366F1", "#8B5CF6", "#EC4899", "#3B82F6", "#10B981"]
        )])
        fig.update_layout(
            title="Practice Distribution by Scenario",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", size=13),
            margin=dict(l=20, r=20, t=40, b=20),
            height=320
        )
        return fig
