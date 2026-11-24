"""Feedback Engine evaluating grammar, vocabulary, natural expressions, and logging practice history."""

from typing import Dict, Any, List, Optional
from modules.gemini_engine import GeminiEngine
from modules.database import save_feedback, save_practice_item
from modules.grammar_validator import detect_grammatical_errors, correct_text_general
from config.settings import SCENARIOS

class FeedbackEngine:
    """Analyzes learner messages and generates educational corrections and insights."""

    def __init__(self, gemini_engine: GeminiEngine):
        self.gemini = gemini_engine

    def evaluate_message(
        self,
        session_id: str,
        scenario_id: str,
        proficiency: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive language evaluation of a user message with validation & second-pass checks."""
        original_sentence = user_message.strip()
        scenario = SCENARIOS.get(scenario_id, SCENARIOS["shopping"])
        scenario_title = scenario["title"]
        history = conversation_history or []

        # Step 1: Pre-validation using grammar validator
        detected_errors = detect_grammatical_errors(original_sentence)
        has_detected_errors = len(detected_errors) > 0

        # Step 2: Attempt Gemini evaluation
        success, feedback_data = self.gemini.generate_feedback(
            scenario_title=scenario_title,
            proficiency=proficiency,
            user_message=original_sentence,
            previous_messages=history
        )

        corrected_sentence: str = ""
        is_correct: bool = False
        individual_errors: List[Dict[str, str]] = []
        corrections_explanation: str = ""
        has_error: bool = False
        error_message: Optional[str] = None
        natural_alternative: str = ""
        natural_alternative_explanation: str = ""
        natural_alternative_example: str = ""
        vocabulary_suggestions: str = ""
        mistake_category: str = "None"
        mistake_description: str = "None"
        fluency_and_clarity: str = ""
        encouraging_tip: str = ""

        if success and not feedback_data.get("has_error") and "error" not in feedback_data:
            # Gemini succeeded
            gemini_corr = (feedback_data.get("corrected_sentence") or feedback_data.get("corrected_text", "")).strip()
            gemini_is_correct = feedback_data.get("is_correct", False)
            individual_errors = feedback_data.get("individual_errors", [])

            # Validation step: If original sentence has identifiable errors,
            # reject false "No corrections needed." claims and run second-pass correction.
            if has_detected_errors and (gemini_is_correct or gemini_corr == "No corrections needed." or gemini_corr == original_sentence):
                second_pass_sent, fixed_errors = correct_text_general(original_sentence)
                corrected_sentence = second_pass_sent
                is_correct = False
                individual_errors = fixed_errors
                corrections_explanation = " \n".join([f"• {e['fix']}: {e['explanation']}" for e in fixed_errors])
                mistake_category = fixed_errors[0]["category"] if fixed_errors else "Grammar"
                mistake_description = fixed_errors[0]["issue"] if fixed_errors else "Grammar error"
            elif not has_detected_errors and (gemini_is_correct or gemini_corr == "No corrections needed." or gemini_corr == original_sentence):
                corrected_sentence = "No corrections needed."
                is_correct = True
                individual_errors = []
                corrections_explanation = "No corrections needed. Your sentence is grammatically correct and well-expressed!"
            else:
                corrected_sentence = gemini_corr
                is_correct = False
                if not individual_errors and detected_errors:
                    individual_errors = detected_errors
                corrections_explanation = feedback_data.get("corrections_explanation") or feedback_data.get("grammar_feedback", "")
                mistake_category = feedback_data.get("mistake_category", "Grammar")
                mistake_description = feedback_data.get("mistake_description", "Grammar mistake")

            natural_alternative = feedback_data.get("natural_alternative") or feedback_data.get("natural_expression", original_sentence)
            natural_alternative_explanation = feedback_data.get("natural_alternative_explanation") or feedback_data.get("natural_expression_explanation", "Authentic conversational phrasing.")
            natural_alternative_example = feedback_data.get("natural_alternative_example") or feedback_data.get("natural_expression_example", "Keep practicing!")
            vocabulary_suggestions = feedback_data.get("vocabulary_suggestions", "Word choices look appropriate.")
            fluency_and_clarity = feedback_data.get("fluency_and_clarity", "Good communication effort!")
            encouraging_tip = feedback_data.get("encouraging_tip", "Great job practicing English!")
        else:
            # Gemini failed or returned an API error
            has_error = True
            error_message = feedback_data.get("error", "Gemini API service was unreachable.")
            
            # Apply second-pass grammar engine so learner gets real corrections instead of a fake pass
            if has_detected_errors:
                second_pass_sent, fixed_errors = correct_text_general(original_sentence)
                corrected_sentence = second_pass_sent
                is_correct = False
                individual_errors = fixed_errors
                corrections_explanation = " \n".join([f"• {e['fix']}: {e['explanation']}" for e in fixed_errors])
                mistake_category = fixed_errors[0]["category"] if fixed_errors else "Grammar"
                mistake_description = fixed_errors[0]["issue"] if fixed_errors else "Grammar error"
            else:
                corrected_sentence = "No corrections needed."
                is_correct = True
                individual_errors = []
                corrections_explanation = "No corrections needed. Your sentence is grammatically correct and well-expressed!"

            natural_alternative = corrected_sentence if not is_correct else original_sentence
            natural_alternative_explanation = "Standard natural phrasing for this situation."
            natural_alternative_example = "Example: 'Could you please help me with this?'"
            vocabulary_suggestions = "Try incorporating descriptive adjectives and polite conversation markers."
            fluency_and_clarity = "Sentence structure evaluated via rule validator."
            encouraging_tip = "Consistent daily practice is the fastest path to natural fluency!"

        # Guarantee original and corrected sentences are stored in separate keys
        cleaned_feedback = {
            "original_sentence": original_sentence,
            "original_text": original_sentence,
            "corrected_sentence": corrected_sentence,
            "corrected_text": corrected_sentence,
            "is_correct": is_correct,
            "individual_errors": individual_errors,
            "corrections_explanation": corrections_explanation,
            "grammar_feedback": corrections_explanation,
            "vocabulary_suggestions": vocabulary_suggestions,
            "natural_alternative": natural_alternative,
            "natural_expression": natural_alternative,
            "natural_alternative_explanation": natural_alternative_explanation,
            "natural_alternative_example": natural_alternative_example,
            "fluency_and_clarity": fluency_and_clarity,
            "mistake_category": mistake_category,
            "mistake_description": mistake_description,
            "encouraging_tip": encouraging_tip,
            "has_error": has_error,
            "error_message": error_message
        }

        # Persist feedback to database
        if session_id:
            save_feedback(
                session_id=session_id,
                original_text=cleaned_feedback["original_sentence"],
                corrected_text=cleaned_feedback["corrected_sentence"],
                grammar_feedback=cleaned_feedback["corrections_explanation"],
                vocabulary_feedback=cleaned_feedback["vocabulary_suggestions"],
                natural_expression=cleaned_feedback["natural_alternative"]
            )

            if not cleaned_feedback["is_correct"] and cleaned_feedback["mistake_category"] not in ("None", "none", ""):
                save_practice_item(
                    session_id=session_id,
                    mistake_category=cleaned_feedback["mistake_category"],
                    mistake_description=cleaned_feedback["mistake_description"],
                    suggested_correction=cleaned_feedback["corrected_sentence"]
                )

        return cleaned_feedback
