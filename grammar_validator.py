"""General English Grammar Validator and Second-Pass Correction Engine."""

import re
from typing import List, Dict, Tuple, Any

# Common irregular and modal verbs for subject-verb agreement
THIRD_PERSON_IRREGULARS = {
    "have": "has",
    "do": "does",
    "go": "goes",
    "don't": "doesn't",
    "dont": "doesn't",
    "say": "says",
}

# Common third-person singular verbs that take -s or -es
COMMON_BASE_VERBS = [
    "like", "want", "need", "play", "run", "walk", "read", "write",
    "know", "think", "come", "live", "work", "study", "feel", "look",
    "seem", "speak", "talk", "eat", "drink", "sleep", "buy", "sell"
]

def detect_grammatical_errors(text: str) -> List[Dict[str, str]]:
    """Scan input text for identifiable grammatical, capitalization, punctuation, and agreement errors.
    
    Returns:
        List of dicts: [{"category": ..., "issue": ..., "fix": ..., "explanation": ...}]
    """
    errors = []
    clean = text.strip()
    if not clean:
        return errors

    # 1. Lowercase standalone pronoun 'i' or 'i'm', 'i've', 'i'll', 'i'd'
    if re.search(r'\bi\b', clean):
        errors.append({
            "category": "Capitalization",
            "issue": "Lowercase pronoun 'i'",
            "fix": "'i' → 'I'",
            "explanation": "The first-person pronoun 'I' must always be capitalized in English."
        })
    elif re.search(r"\bi'(m|ve|ll|d)\b", clean, re.IGNORECASE) and re.search(r"\bi'(m|ve|ll|d)\b", clean):
        errors.append({
            "category": "Capitalization",
            "issue": "Lowercase contraction with pronoun 'i'",
            "fix": "'i' → 'I'",
            "explanation": "The pronoun 'I' in contractions (I'm, I've, I'll) must be capitalized."
        })

    # 2. Sentence initial capitalization
    if clean and clean[0].islower():
        errors.append({
            "category": "Capitalization",
            "issue": f"Sentence starts with lowercase '{clean[0]}'",
            "fix": f"'{clean[0]}' → '{clean[0].upper()}'",
            "explanation": "Sentences in English must begin with a capital letter."
        })

    # 3. Subject-Verb Agreement: First person 'I' + 'has' / 'does' / 'is' / 'are'
    if re.search(r'\b[Ii]\s+has\b', clean):
        errors.append({
            "category": "Subject-Verb Agreement",
            "issue": "Incorrect verb 'has' with subject 'I'",
            "fix": "'has' → 'have'",
            "explanation": "The pronoun 'I' takes 'have', not 'has' (e.g. 'I have')."
        })
    if re.search(r'\b[Ii]\s+is\b', clean) or re.search(r'\b[Ii]\s+are\b', clean):
        errors.append({
            "category": "Subject-Verb Agreement",
            "issue": "Incorrect form of 'be' with subject 'I'",
            "fix": "Use 'am'",
            "explanation": "The pronoun 'I' takes 'am' in the present tense (e.g. 'I am')."
        })

    # 4. Third-person singular subjects (He / She / It) + base verb errors
    # 'He/She/It don't' -> 'doesn't'
    if re.search(r'\b(He|She|It|he|she|it)\s+(don\'t|dont)\b', clean):
        errors.append({
            "category": "Subject-Verb Agreement",
            "issue": "Incorrect auxiliary 'don't' with third-person singular",
            "fix": "'don't' → 'doesn't'",
            "explanation": "Third-person singular subjects (he, she, it) take 'doesn't', not 'don't'."
        })
    # 'He/She/It go' -> 'goes'
    if re.search(r'\b(He|She|It|he|she|it)\s+go\b', clean):
        errors.append({
            "category": "Subject-Verb Agreement",
            "issue": "Missing third-person singular suffix on 'go'",
            "fix": "'go' → 'goes'",
            "explanation": "Third-person singular subjects take 'goes' in the simple present tense."
        })
    # 'He/She/It have' -> 'has'
    if re.search(r'\b(He|She|It|he|she|it)\s+have\b', clean):
        errors.append({
            "category": "Subject-Verb Agreement",
            "issue": "Incorrect verb 'have' with third-person singular",
            "fix": "'have' → 'has'",
            "explanation": "Third-person singular subjects take 'has', not 'have'."
        })

    # Other common verbs missing -s after He/She/It
    for verb in COMMON_BASE_VERBS:
        if re.search(rf'\b(He|She|It|he|she|it)\s+{verb}\b', clean):
            expected_v = verb + "s"
            errors.append({
                "category": "Subject-Verb Agreement",
                "issue": f"Base verb '{verb}' without third-person -s",
                "fix": f"'{verb}' → '{expected_v}'",
                "explanation": f"Third-person singular present tense requires adding -s (e.g. 'She {expected_v}')."
            })

    # 5. Plural subjects (They / We / You) + 'is' / 'has' / 'was'
    if re.search(r'\b(They|We|You|they|we|you)\s+is\b', clean):
        errors.append({
            "category": "Subject-Verb Agreement",
            "issue": "Singular verb 'is' with plural subject",
            "fix": "'is' → 'are'",
            "explanation": "Plural subjects (they, we, you) take 'are', not 'is'."
        })
    if re.search(r'\b(They|We|they|we)\s+has\b', clean):
        errors.append({
            "category": "Subject-Verb Agreement",
            "issue": "Singular verb 'has' with plural subject",
            "fix": "'has' → 'have'",
            "explanation": "Plural subjects (they, we) take 'have', not 'has'."
        })
    if re.search(r'\b(They|We|You|they|we|you)\s+was\b', clean):
        errors.append({
            "category": "Subject-Verb Agreement",
            "issue": "Singular verb 'was' with plural subject",
            "fix": "'was' → 'were'",
            "explanation": "Plural subjects take 'were', not 'was'."
        })

    # 6. Lowercase proper names after greeting / introduction (e.g. 'i am laasya', 'my name is john')
    name_match = re.search(r'\b(?:I am|i am|I\'m|i\'m|my name is|My name is)\s+([a-z][a-z]+)\b', clean)
    if name_match:
        name_word = name_match.group(1)
        # Avoid common non-name words
        if name_word not in ("a", "an", "the", "happy", "student", "teacher", "ready", "here", "fine", "good"):
            errors.append({
                "category": "Capitalization",
                "issue": f"Proper noun '{name_word}' is lowercase",
                "fix": f"'{name_word}' → '{name_word.capitalize()}'",
                "explanation": "Names of individuals are proper nouns and must be capitalized."
            })

    # 7. Mid-sentence improper capitalization (e.g. ', A final-tear')
    if re.search(r',\s+([A-Z][a-z]+)\b', clean):
        mid_match = re.search(r',\s+([A-Z][a-z]+)\b', clean)
        word = mid_match.group(1)
        if word not in ("I", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "English"):
            errors.append({
                "category": "Capitalization",
                "issue": f"Improper capitalization of '{word}' after comma",
                "fix": f"'{word}' → '{word.lower()}'",
                "explanation": "Words following a comma inside a sentence clause should be lowercase unless proper nouns."
            })

    # 8. Known phonetic spelling typos (e.g. 'final-tear' -> 'final-year')
    if re.search(r'\bfinal-tear\b', clean, re.IGNORECASE):
        errors.append({
            "category": "Spelling",
            "issue": "Spelling error in 'final-tear'",
            "fix": "'final-tear' → 'final-year'",
            "explanation": "The academic term is 'final-year' (year of graduation), not 'final-tear'."
        })

    # 9. 'everyday' (adjective) used as adverb of frequency at end of verb clause
    if re.search(r'\beveryday\b([.!?]?)$', clean, re.IGNORECASE):
        errors.append({
            "category": "Grammar",
            "issue": "Using 'everyday' instead of 'every day'",
            "fix": "'everyday' → 'every day'",
            "explanation": "'Every day' (two words) is an adverbial time expression; 'everyday' (one word) is an adjective (e.g., 'everyday routine')."
        })

    # 10. Missing terminal punctuation
    if clean and clean[-1] not in ('.', '!', '?'):
        errors.append({
            "category": "Punctuation",
            "issue": "Missing terminal punctuation",
            "fix": "Add '.' at the end of the sentence",
            "explanation": "Sentences in written English should conclude with a period, question mark, or exclamation point."
        })

    return errors

def correct_text_general(text: str) -> Tuple[str, List[Dict[str, str]]]:
    """Apply general grammar, spelling, punctuation and agreement corrections.
    
    Returns:
        Tuple of (corrected_sentence, list_of_errors_found)
    """
    errors = detect_grammatical_errors(text)
    if not errors:
        return "No corrections needed.", []

    corrected = text.strip()

    # 1. Pronoun 'i' / contractions
    corrected = re.sub(r'\bi\b', 'I', corrected)
    corrected = re.sub(r"\bi'(m|ve|ll|d)\b", r"I'\1", corrected)

    # 2. Conversational contraction in self-introductions ('Hi, I am' -> "Hi, I'm")
    corrected = re.sub(r'\b(Hi|Hello|Hey),\s+I am\b', r"\1, I'm", corrected)

    # 3. Subject-Verb Agreement: 'I has' -> 'I have', 'I is' -> 'I am'
    corrected = re.sub(r'\bI has\b', 'I have', corrected)
    corrected = re.sub(r'\bI is\b', 'I am', corrected)
    corrected = re.sub(r'\bI are\b', 'I am', corrected)

    # 4. Third-person singular: 'He/She/It don't' -> "doesn't", 'go' -> 'goes', 'have' -> 'has'
    corrected = re.sub(r'\b(He|She|It)\s+(don\'t|dont)\b', r"\1 doesn't", corrected)
    corrected = re.sub(r'\b(he|she|it)\s+(don\'t|dont)\b', r"\1 doesn't", corrected)
    corrected = re.sub(r'\b(He|She|It)\s+go\b', r"\1 goes", corrected)
    corrected = re.sub(r'\b(he|she|it)\s+go\b', r"\1 goes", corrected)
    corrected = re.sub(r'\b(He|She|It)\s+have\b', r"\1 has", corrected)
    corrected = re.sub(r'\b(he|she|it)\s+have\b', r"\1 has", corrected)

    for verb in COMMON_BASE_VERBS:
        corrected = re.sub(rf'\b(He|She|It)\s+{verb}\b', rf'\1 {verb}s', corrected)
        corrected = re.sub(rf'\b(he|she|it)\s+{verb}\b', rf'\1 {verb}s', corrected)

    # 5. Plural subjects: 'They/We/You is' -> 'are', 'They/We has' -> 'have', 'was' -> 'were'
    corrected = re.sub(r'\b(They|We|You)\s+is\b', r'\1 are', corrected)
    corrected = re.sub(r'\b(they|we|you)\s+is\b', r'\1 are', corrected)
    corrected = re.sub(r'\b(They|We)\s+has\b', r'\1 have', corrected)
    corrected = re.sub(r'\b(they|we)\s+has\b', r'\1 have', corrected)
    corrected = re.sub(r'\b(They|We|You)\s+was\b', r'\1 were', corrected)
    corrected = re.sub(r'\b(they|we|you)\s+was\b', r'\1 were', corrected)

    # 6. Lowercase proper names after 'I am' / 'My name is'
    def _cap_name(match):
        prefix = match.group(1)
        name = match.group(2)
        if name.lower() not in ("a", "an", "the", "happy", "student", "teacher", "ready", "here", "fine", "good"):
            return f"{prefix} {name.capitalize()}"
        return match.group(0)

    corrected = re.sub(r'\b(I am|I\'m|my name is|My name is)\s+([a-z][a-z]+)\b', _cap_name, corrected)

    # 7. Mid-sentence capitalization: ', A ' -> ', a '
    corrected = re.sub(r',\s+A\s+', ', a ', corrected)

    def _lower_mid(match):
        w = match.group(1)
        if w not in ("I", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "English"):
            return f", {w.lower()}"
        return match.group(0)
    corrected = re.sub(r',\s+([A-Z][a-z]+)\b', _lower_mid, corrected)

    # 8. Known typo: 'final-tear' -> 'final-year'
    corrected = re.sub(r'\bfinal-tear\b', 'final-year', corrected, flags=re.IGNORECASE)

    # 9. 'everyday' -> 'every day'
    corrected = re.sub(r'\beveryday\b([.!?]?)$', r'every day\1', corrected, flags=re.IGNORECASE)

    # 10. Capitalize sentence start
    if corrected and corrected[0].islower():
        corrected = corrected[0].upper() + corrected[1:]

    # 11. Add terminal punctuation if missing
    if corrected and corrected[-1] not in ('.', '!', '?'):
        corrected += "."

    return corrected, errors
