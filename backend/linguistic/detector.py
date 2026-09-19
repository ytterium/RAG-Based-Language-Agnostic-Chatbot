# WHAT: Language detection module classifying incoming student queries into supported languages ('en' or 'hi' / Hinglish).
# WHY: Implements Layer 3 Linguistic Pre-Processing according to Section III-B of the architecture spec.
#      Language detection runs first on every incoming query before retrieval to:
#      1. Determine whether Hinglish normalization is required.
#      2. Store detected language in LangGraph AgentState so Node 5 (Language Consistency Validator)
#         can enforce response language consistency and eliminate language drift.

import re
from typing import Optional
from lingua import Language, LanguageDetectorBuilder

# WHAT: Supported language targets for the academic institution chatbot.
# WHY: System architecture restricts production scope to English and Hindi (including Romanized Hinglish).
SUPPORTED_LANGUAGES = [Language.ENGLISH, Language.HINDI]

# Module-level singleton cache for the Lingua detector
_detector: Optional[object] = None

# WHAT: Curated lexical markers representing common Romanized Hindi (Hinglish) question words, auxiliaries, and morphemes.
# WHY: Standard statistical language detectors (including Lingua) are trained primarily on native Devanagari script
#      for Hindi, and classify Latin-script Romanized Hindi as English or other Latin-alphabet languages.
#      Matching distinct Hinglish phonetic tokens allows instantaneous zero-latency classification of Hinglish queries as 'hi'.
#      English stop words and common tokens are strictly omitted to prevent false positive classification of English questions.
HINGLISH_MARKERS = {
    # Interrogatives (Question words)
    "kab", "kahan", "kaha", "kidhar", "kaise", "kaisa", "kaisi", "kyun", "kyu",
    "kya", "kis", "kisko", "kiska", "kiski", "kiske", "kitna", "kitni", "kitne",
    "kaun", "kon", "kaunsa", "kaunsi", "kaunse",
    # Verbs and auxiliaries
    "hai", "hain", "hoon", "hun", "tha", "thi", "hoga", "hogi", "hoge",
    "milega", "milegi", "milege", "milna", "milta", "milti", "milte",
    "bharna", "bhare", "bhari", "bhara", "bharo", "karna", "kare", "karo", "karein",
    "kiya", "kiye", "aayega", "aayegi", "aana", "jaana", "dena", "dedo", "diya",
    "chahiye", "batao", "bataiye", "bataye", "suno", "dekho", "lagta", "lagti", "lagte",
    "sakta", "sakti", "sakte", "rakhna", "kismein",
    # Academic & institutional vocabulary in Hindi/Hinglish
    "aakhri", "taarikh", "tarikh", "chutti", "chhutti", "paisa", "paise", "rupaye", "rupya",
    # Pronouns and particles
    "mera", "meri", "mere", "humara", "hamara", "aapka", "tumhara", "iska", "iski", "iske",
    "usko", "isko", "sabka", "kisi", "nahi", "nhi", "bhi", "aur", "lekin", "magar",
    "kyunki", "sirf", "pehle", "baad", "jaldi"
}


# WHAT: Initializes and returns a cached singleton instance of Lingua LanguageDetector.
# WHY: Building the n-gram language detector model takes significant CPU time and memory.
#      Caching the detector globally ensures it is only built once upon first query invocation.
def get_detector():
    global _detector
    if _detector is None:
        _detector = LanguageDetectorBuilder.from_languages(*SUPPORTED_LANGUAGES).build()
    return _detector


# WHAT: Detects whether a given query text is English ('en') or Hindi/Hinglish ('hi').
# WHY: Implements a 3-tier detection hierarchy:
#      1. Devanagari Unicode check: instant detection for native Hindi script (U+0900 to U+097F).
#      2. Hinglish marker check: identifies Romanized Hindi tokens commonly typed by Indian students.
#      3. Lingua n-gram classification: statistical language detection fallback between English and Hindi.
def detect_language(text: str) -> str:
    """
    Classifies student query language.
    Returns: 'en' for English, 'hi' for Hindi or Romanized Hinglish.
    """
    if not text or not text.strip():
        return "en"

    cleaned = text.strip()

    # Tier 1: Check for native Devanagari Unicode characters (Hindi script)
    if re.search(r"[\u0900-\u097F]", cleaned):
        return "hi"

    # Tier 2: Check for Romanized Hindi / Hinglish lexical markers
    tokens = set(re.findall(r"\b[a-zA-Z]+\b", cleaned.lower()))
    if tokens & HINGLISH_MARKERS:
        return "hi"

    # Tier 3: Statistical n-gram detection using Lingua
    detector = get_detector()
    result = detector.detect_language_of(cleaned)
    if result == Language.HINDI:
        return "hi"

    # Default to English for general institutional queries
    return "en"
