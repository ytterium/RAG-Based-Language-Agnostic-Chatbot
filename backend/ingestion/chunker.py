"""
Semantic Chunker and Metadata Enrichment Module.
Implements token-window chunking (default 500 tokens, 100 overlap)
with automated regex extraction for institutional notice metadata:
- circular_number
- date
- department
- source & chunk ID
- ocr_method
"""
import re
from typing import List, Dict, Any

try:
    from config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS
except ImportError:
    from backend.config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS

# Regex patterns for institutional notice metadata extraction
CIRCULAR_PATTERNS = [
    re.compile(r'(?:Notice|Circular|Ref\.?|Order)\s*(?:No\.?|Number|#)?[:\s-]*([A-Za-z0-9\/\-\.]+)', re.IGNORECASE),
    re.compile(r'\b([A-Z]{2,6}\/[A-Za-z0-9\/\-]+\/\d{2,4}(?:\/\d+)?)\b'),
    re.compile(r'\b([A-Z]{2,6}\/\d{4}\/\d{1,4})\b'),
]

DATE_PATTERNS = [
    re.compile(r'\b(?:Dated?|Date)[:\s-]*(\d{1,2}[-\/\.]\d{1,2}[-\/\.]\d{2,4})\b', re.IGNORECASE),
    re.compile(r'\b(?:Dated?|Date)[:\s-]*(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*,?\s*\d{2,4})\b', re.IGNORECASE),
    re.compile(r'\b(\d{1,2}[-\/\.]\d{1,2}[-\/\.]\d{4})\b'),
    re.compile(r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*\d{4})\b', re.IGNORECASE),
]

DEPARTMENTS = [
    "Academic Section",
    "Dean Academics",
    "Examination Branch",
    "Accounts Section",
    "Training & Placement Cell",
    "Student Welfare",
    "Library",
    "Hostel Administration",
    "Registrar Office",
    "Director Office",
]


def extract_metadata_from_text(text: str) -> Dict[str, str]:
    """
    Extract institutional identifiers (circular number, date, department) using heuristics.
    """
    extracted: Dict[str, str] = {
        "circular_number": "",
        "date": "",
        "department": ""
    }

    # Circular Number
    for pat in CIRCULAR_PATTERNS:
        match = pat.search(text)
        if match:
            cand = match.group(1).strip(" .:,;()")
            if len(cand) >= 3 and any(ch.isdigit() for ch in cand):
                extracted["circular_number"] = cand
                break

    # Date
    for pat in DATE_PATTERNS:
        match = pat.search(text)
        if match:
            extracted["date"] = match.group(1).strip(" .:,;()")
            break

    # Department
    for dept in DEPARTMENTS:
        if re.search(r'\b' + re.escape(dept) + r'\b', text, re.IGNORECASE):
            extracted["department"] = dept
            break

    return extracted


def chunk_text(text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recursively chunk text using sliding token window with overlap.
    Enriches metadata with auto-extracted circular ID, dates, and departments if missing.

    Args:
        text: Raw document text string.
        metadata: Base metadata dictionary (source, ocr_method, etc.).

    Returns:
        List of dicts: {"text": str, "metadata": Dict[str, Any]}
    """
    if not text or not text.strip():
        return []

    # Auto-extract metadata from document text if not already explicitly provided
    auto_meta = extract_metadata_from_text(text)

    sanitized_meta = {
        "source": str(metadata.get("source", "unknown")),
        "date": str(metadata.get("date") or auto_meta["date"] or ""),
        "department": str(metadata.get("department") or auto_meta["department"] or "General Administration"),
        "circular_number": str(metadata.get("circular_number") or auto_meta["circular_number"] or ""),
        "ocr_method": str(metadata.get("ocr_method", "unknown")),
        "language": str(metadata.get("language", "en")),
    }

    # Include any extra metadata fields, ensuring primitive types for ChromaDB compatibility
    for k, v in metadata.items():
        if k not in sanitized_meta:
            if v is None:
                sanitized_meta[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                sanitized_meta[k] = v
            else:
                sanitized_meta[k] = str(v)

    words = text.split()
    chunks: List[Dict[str, Any]] = []
    step = max(1, CHUNK_SIZE_TOKENS - CHUNK_OVERLAP_TOKENS)

    # If the text is short, don't discard the document
    if len(words) <= CHUNK_SIZE_TOKENS:
        if len(words) >= 3:
            chunk_meta = {
                **sanitized_meta,
                "chunk_index": 0,
                "chunk_id": f"{sanitized_meta['source']}_chunk_0"
            }
            chunks.append({"text": text.strip(), "metadata": chunk_meta})
        return chunks

    chunk_idx = 0
    for start in range(0, len(words), step):
        chunk_words = words[start:start + CHUNK_SIZE_TOKENS]
        # Skip small trailing fragments if we already have chunks
        if start > 0 and len(chunk_words) < 20:
            continue

        chunk_text_str = " ".join(chunk_words).strip()
        if not chunk_text_str:
            continue

        chunk_meta = {
            **sanitized_meta,
            "chunk_index": chunk_idx,
            "chunk_id": f"{sanitized_meta['source']}_chunk_{chunk_idx}"
        }
        chunks.append({"text": chunk_text_str, "metadata": chunk_meta})
        chunk_idx += 1

    return chunks
