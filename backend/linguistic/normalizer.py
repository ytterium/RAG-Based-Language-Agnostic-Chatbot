# WHAT: Hinglish normalization module providing phonetic mapping and intent keyword extraction for Romanized Hindi queries.
# WHY: Implements Layer 3 Linguistic Pre-Processing according to Section III-B of the architecture spec.
#      Students frequently query academic systems in Romanized Hindi/Hinglish (e.g., 'fees kab bharna hai submission').
#      Standard multilingual tokenizers split colloquial Romanized Hindi tokens into disjoint subwords, causing
#      vocabulary mismatch in sparse retrieval (BM25) and semantic drift in dense retrieval (BGE-M3).
#      Normalizing Hinglish queries into canonical English/academic intent tokens preserves retrieval quality.

import re
from typing import List
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# WHAT: Curated mapping of colloquial Hinglish phrases and Romanized Hindi idioms to formal academic English concepts.
# WHY: Directly bridges vocabulary gaps between student phrasing and institutional English circulars/notices.
#      Ensures BM25 sparse search and BGE-M3 dense embeddings align with official institutional terminology.
HINGLISH_INTENT_MAP = {
    # Deadlines and submission schedules
    r"\blast date\b": "submission deadline",
    r"\baakhri taarikh\b": "submission deadline",
    r"\baakhri tarikh\b": "submission deadline",
    r"\bkab submit\b": "submission deadline",
    r"\bkab tak submit\b": "submission deadline",
    r"\bkab tak\b": "until when deadline",
    # Fees and payments
    r"\bfees kab bharna\b": "fee payment schedule",
    r"\bfees kab bhari\b": "fee payment schedule",
    r"\bfees kaise bhare\b": "fee payment method process",
    r"\bkitna paisa\b": "amount fee",
    r"\bkitne paise\b": "amount fee",
    r"\bkitni fees\b": "fee amount",
    r"\bfee kitni lagegi\b": "fee amount structure",
    r"\blate fee\b": "late submission fine penalty",
    r"\bfine kitna\b": "late penalty fine amount",
    # Forms and applications
    r"\bscholarship form\b": "scholarship application form",
    r"\bform kahan milega\b": "where to get form",
    r"\bform kahan milegi\b": "where to get form",
    r"\bform submit karna\b": "submit application form",
    r"\bform kaise bhare\b": "how to fill application form",
    # Academic calendar, exams, and results
    r"\bchutti\b": "academic holiday",
    r"\bchhutti\b": "academic holiday",
    r"\bexam kab hai\b": "examination date",
    r"\bexams kab honge\b": "examination schedule",
    r"\bresult kab aayega\b": "result announcement date",
    r"\bdate sheet kab aayegi\b": "examination date sheet timetable",
    r"\bdatesheet\b": "examination date sheet timetable",
    r"\badmit card\b": "hall ticket admit card release",
    # Campus, hostel, and policies
    r"\bhostel admission\b": "hostel accommodation admission",
    r"\bhostel fees\b": "hostel accommodation fee",
    r"\battendance rule\b": "minimum attendance requirement criteria",
    r"\battendance kitni\b": "minimum attendance percentage required",
    r"\bplacement kaisa\b": "campus placement statistics report",
    r"\bsyllabus kya\b": "course syllabus curriculum",
}

# WHAT: Anchored institutional keyword patterns for BM25 sparse retrieval guidance.
# WHY: Identifies core subject anchors (scholarship, fee, exam, circular) to boost lexical matching.
CORE_ANCHOR_PATTERNS = [
    r"\bscholarship\b", r"\bfee[s]?\b", r"\bexam[s]?\b", r"\bdeadline\b",
    r"\bnotice\b", r"\bcircular\b", r"\badmission\b", r"\bhostel\b",
    r"\bholiday\b", r"\bresult\b", r"\battendance\b", r"\bsyllabus\b",
    r"\bform\b", r"\bdepartment\b", r"\bcse\b", r"\bit\b", r"\bece\b"
]


# WHAT: Transliterates Romanized ASCII text into native Devanagari script using the ITRANS scheme.
# WHY: Section III-B research contribution specifies phonetic transliteration support for Romanized text.
#      Allows cross-script comparisons and phonetic matching when student queries use Indian Romanization.
def transliterate_to_devanagari(text: str, scheme: str = sanscript.ITRANS) -> str:
    """
    Phonetically transliterates Romanized text into Devanagari script.
    """
    if not text or not text.strip():
        return ""
    try:
        return transliterate(text.strip(), scheme, sanscript.DEVANAGARI)
    except Exception:
        # Fallback to original text if transliteration fails
        return text


# WHAT: Extracts salient institutional intent anchor keywords from a query string.
# WHY: BM25 sparse search relies on exact keyword matching. Extracting core institutional anchors
#      allows downstream components (retriever / re-ranker) to verify anchor presence.
def extract_intent_keywords(query: str) -> List[str]:
    """
    Extracts high-priority academic and administrative keywords from the query.
    """
    found_keywords = []
    lower_q = query.lower()
    for pattern in CORE_ANCHOR_PATTERNS:
        match = re.search(pattern, lower_q)
        if match:
            found_keywords.append(match.group(0))
    return list(dict.fromkeys(found_keywords))


# WHAT: Normalizes colloquial Romanized Hindi/Hinglish queries into structured academic English intent expressions.
# WHY: Two-step normalization pipeline:
#      Step 1: Replace known multi-word Hinglish idioms and phrases with canonical English equivalents
#              via HINGLISH_INTENT_MAP.
#      Step 2: Clean redundant whitespace and normalize casing for uniform embedding and lexical search.
def normalize_hinglish(query: str) -> str:
    """
    Applies regex phrase replacement to convert colloquial Hinglish into formal English expressions.
    """
    normalized = query.lower().strip()
    for pattern, replacement in HINGLISH_INTENT_MAP.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # Clean redundant whitespace
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


# WHAT: Main linguistic normalization entry point routing queries according to detected language.
# WHY: Queries detected as Hindi/Hinglish ('hi') are routed through the Hinglish normalization pipeline,
#      while English queries ('en') pass through cleanly to avoid unnecessary string mutations.
def normalize_query(query: str, detected_language: str) -> str:
    """
    Main normalization entry point.
    If detected_language is 'hi', normalizes Hinglish phrases to formal English.
    If detected_language is 'en', returns query unchanged.
    """
    if not query or not query.strip():
        return ""

    if detected_language == "hi":
        return normalize_hinglish(query)

    # English queries pass through unchanged
    return query.strip()
