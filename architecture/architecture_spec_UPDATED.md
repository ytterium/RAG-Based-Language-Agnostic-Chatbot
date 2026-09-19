# System Architecture and Technical Design Specification
### RAG-Based Language Agnostic Chatbot for Smart Query Response in Academic Institutions
**Team MNP059 | MAIT CSE | B.Tech VII Semester (2023–2027)**

---

## 1. Executive Summary and Problem Context

Campus administrative offices are overwhelmed each semester with thousands of repetitive inquiries regarding scholarship forms, fee deadlines, exam schedules, and eligibility rules. Official guidelines are published almost exclusively in English within unstructured PDF circulars and dynamic departmental web notices. A significant proportion of students communicate more naturally in Hindi or colloquial Hinglish. This linguistic divide leads to long physical queues, communication breakdowns, and administrative fatigue.

**What makes this harder:** institutional notices are predominantly published as *scanned noticeboard images*, *physical circular photographs*, and *non-searchable image-based PDFs* — not as clean digital text. Traditional chatbots and naive RAG systems completely fail on this input format.

---

## 2. Architectural Philosophy: Why Moving Beyond Naive RAG is Essential

Most basic student chatbot projects implement a Naive RAG workflow: chunk a PDF, store text in a vector database, and pass the top matches to an LLM with a single prompt. Academic literature and real-world testing demonstrate that Naive RAG fails in institutional environments due to four critical flaws:

- **Blind Context Trust:** The system blindly passes whatever chunks the vector search returns. If the retrieved text is irrelevant or incomplete, the generator produces ungrounded hallucinations.
- **Failure on Scanned Images:** Naive RAG only processes searchable text. The majority of institutional notices — scanned photos of noticeboards, image PDFs — are completely invisible to it.
- **Failure on Exact Identifiers:** Dense vector embeddings excel at broad conceptual matching but consistently miss exact notice numbers, dates, and form codes (such as 'Notice Acad/2026/04' or 'Form 16-A').
- **Language Drift in Multi-Turn Chats:** As established by IEEE research (EduX-RAG, 2025), prompt-based chatbots suffer an average 27% language drift rate, slipping back into English when students switch languages during a conversation.

---

## 3. The Proposed Solution: An Agentic Self-Corrective Architecture

To resolve these challenges, our project introduces an **Agentic Self-Corrective RAG** system orchestrated through LangGraph. Rather than treating question answering as a rigid one-way script, the system runs as a state machine equipped with self-evaluation loops. It actively grades document relevance, reformulates unclear queries, verifies factual grounding before output, enforces response-language consistency, and gracefully hands off unresolved inquiries to human administrative staff.

---

## 4. Layer-by-Layer Architectural Specifications

> **IMPORTANT — Runtime Order Clarification:**
> Despite the layer numbering, the actual runtime order is:
> **Layer 3 (Linguistic Pre-processing) → Layer 2 (Retrieval, using Layer 1's offline index) → Layer 4 (LangGraph Decision Engine)**
> Layer 1 runs as a scheduled offline batch job, not in the query-time critical path.

---

### Layer 1: Automated Ingestion and Multi-Modal Indexing Pipeline *(Offline / Scheduled)*

The ingestion pipeline runs as a **scheduled batch job** (not at query time) and continuously processes two primary institutional data streams, building and updating the offline vector index.

#### 1a. Web Scraping Engine (BeautifulSoup / bs4)
Periodically monitors the college portal's active notice boards, extracting headline announcements, publication timestamps, and administrative links. Runs on a configurable schedule (e.g., every 6 hours). Results are stored to disk and fed into the chunker.

#### 1b. Adaptive OCR & Document Ingestion Engine *(Key Research Contribution)*

This is a **three-path adaptive router** that selects the optimal extraction strategy based on the input type and quality:

| Input Type | Detection Method | Extraction Path | Cite |
|---|---|---|---|
| **Digital PDF** (searchable text) | PyMuPDF text layer check | **PyMuPDF** — layout-aware text + table extraction | — |
| **Clean scanned image / scan PDF** | Image sharpness + contrast score ≥ threshold | **Tesseract 5.x OCR** — fast, free, local | Smith, 2007 |
| **Noisy / complex image** (stamps, skew, handwriting, low-res) | Sharpness + contrast score < threshold | **Pixtral-12B** (Mistral vision model, open weights) — handles degraded images natively | Agrawal et al., 2024 |

**Pre-processing pipeline** (before Tesseract): binarization, deskewing, noise reduction using OpenCV.

**Why this matters for the paper:** All three paths are benchmarked on a curated set of 50+ real MAIT notice images, measuring Character Error Rate (CER) and Word Error Rate (WER). This adaptive routing strategy — choosing based on image quality metrics — is a novel contribution over single-method OCR baselines.

#### 1c. Metadata-Rich Chunking
Text is split using recursive semantic chunking with a **500-token window and 100-token overlap**. Each chunk is tagged with structured metadata:
```
{
  "circular_number": "Acad/2026/04",
  "date": "2026-09-10",
  "department": "Academic Section",
  "page_number": 2,
  "source_url": "https://mait.ac.in/notices/...",
  "ocr_method": "pixtral-12b",   ← tracks which path was used
  "language": "en"
}
```
Metadata enables verifiable, clickable citations in the frontend.

#### 1d. Dual Indexing
Each chunk is indexed into both:
- **ChromaDB** (persistent vector store) — via BGE-M3 embeddings
- **BM25 index** (rank-bm25) — for sparse lexical search

---

### Layer 2: Hybrid Retrieval Engine *(Query-Time)*

Rather than relying solely on dense vectors, the architecture employs a dual-index hybrid search pipeline:

#### Dense Vector Search — BGE-M3 (BAAI)
BAAI's BGE-M3 model maps regional queries (Hindi, Hinglish) and English circulars into a shared **1024-dimensional semantic space**, capturing conceptual intent across languages without requiring parallel translation corpora. Achieves 97.6% top-k accuracy (Son et al., 2025).

#### Sparse Lexical Search — BM25 (rank-bm25)
Indexes exact keywords, numerical dates, circular IDs, and form identifiers that dense semantic models often dilute. Critical for queries like *"Form 16-A submission date"*.

#### Reciprocal Rank Fusion (RRF, k=60)
Combines the ranked candidate lists from both retrievers using score fusion (constant k=60), ensuring documents that match both semantically and lexically are prioritized. Returns top-10 candidates.

#### Cross-Encoder Re-Ranking
The top-10 fused candidates are re-evaluated by a lightweight cross-encoder to produce the final **top-3 highly relevant context passages**, stripping out background noise before generation.

---

### Layer 3: Pre-Processing and Linguistic Router *(Query-Time — Runs FIRST)*

Incoming student messages undergo immediate pre-processing **before** entering the retrieval pipeline.

#### Language Detector
Identifies the source language of the student query (English or Hindi/Hinglish). Detected language is stored in the LangGraph conversation state and used by Node 5 (Language Consistency Validator) to enforce response language.

#### Hinglish Normalization Module *(Research Contribution)*
If Romanized Hindi/Hinglish is detected:
1. **Phonetic transliteration** — maps Romanized Hindi tokens to normalized Hindi/English equivalents (e.g., "kab hai" → "when is", "form kahan milega" → "where to get form")
2. **Intent-keyword extraction** — identifies anchor terms (scholarship, deadline, form number) to guide BM25 retrieval

This two-step pipeline ensures standard tokenizers do not split Romanized regional words into nonsensical subwords, preserving retrieval quality.

#### Contextual Query Rewriter
Resolves follow-up pronoun ambiguity using conversational state stored in memory (e.g., transforming *"When is its last date?"* into *"When is the submission deadline for the 2026 post-matric scholarship?"*). Prevents context failure in multi-turn conversations.

---

### Layer 4: LangGraph Self-Corrective Decision Engine *(Query-Time)*

At the heart of the system is a stateful decision graph built with **LangGraph**. The graph maintains an explicit state object containing: original student query, detected language, conversational history, retrieved document chunks, generated draft, and verification scores.

The workflow moves through five specialized decision nodes:

**Node 1 — Document Relevance Grader**
An evaluation step checks whether the retrieved passages genuinely contain the facts needed to answer the student's question. If relevance score < 0.70 or key terms are absent, the graph branches into the Query Reformulation loop.

**Node 2 — Query Reformulation and Retrieval Fallback**
When initial retrieval fails:
1. Reframes the query keywords to capture alternate phrasings
2. Re-queries **ChromaDB** with the reformulated query
3. If ChromaDB still yields insufficient context, queries the **live web scraper** as a last resort for newly published notices
4. If information remains absent after all retries → **Escalation Trigger**

**Node 3 — Grounded Generation Engine (Mistral 7B Instruct)**
Uses **Mistral 7B Instruct** (open weights, Apache 2.0, citable: Jiang et al., 2023) to generate an answer strictly constrained by the verified top-3 passages. The system prompt explicitly prohibits speculation and instructs the model to attach source metadata citations to every factual assertion.

**Node 4 — Hallucination and Factuality Grader**
An automated verification check compares the generated draft against the source text. If the model introduced unsourced dates, fee numbers, or rules, the draft is rejected and sent back to Node 3 for re-synthesis with stricter context bounds.

**Node 5 — Language Consistency Validator**
Directly solves the 27% language drift flaw. If the generated draft's language differs from the student's detected query language, this node enforces translation/alignment while preserving all citation tags before dispatch.

---

### Decision and Escalation Rules

| Decision Point | Condition Checked | Action Taken |
|---|---|---|
| Retrieval Assessment | Relevance score > 0.70 and key terms present | Proceed directly to Node 3 (Grounded Generation) |
| Ambiguity / Context Gap | Relevance score < 0.70 on initial retrieval | Route to Node 2: reformulate → re-query ChromaDB → try live scraper |
| Factuality Check | Generated facts lack direct grounding in source passages | Reject draft; regenerate with stricter temperature and context bounds |
| Language Verification | Draft language differs from detected query language | Node 5 alignment pass while preserving citation tags |
| Escalation Trigger | Information absent from all sources after reformulation | Halt generation; display office contact card; log query in SQLite |

---

## 5. Technology Stack (Final — Prototype)

| System Layer | Technology | Engineering Rationale |
|---|---|---|
| **Frontend UI** | ReactJS, Tailwind CSS | Responsive multilingual chat interface and citation cards |
| **Backend API** | Python, Flask | Lightweight REST API routing requests between UI and AI pipeline |
| **Generation LLM** | Mistral 7B Instruct (open weights) | Open-source, Apache 2.0, fully citable (Jiang et al., 2023), reproducible |
| **OCR — Digital PDF** | PyMuPDF | Layout-aware text + table extraction for searchable PDFs |
| **OCR — Clean Scans** | Tesseract 5.x | Fast, free, local OCR for clean scanned images (Smith, 2007) |
| **OCR — Noisy Images** | Pixtral-12B (open weights) | Vision LLM for complex/degraded notices (Agrawal et al., 2024) |
| **OCR Preprocessing** | OpenCV | Binarization, deskewing, noise reduction before Tesseract |
| **Orchestration** | LangGraph, LangChain | Stateful self-corrective workflow with typed state graph |
| **Web Scraper** | BeautifulSoup (bs4) | Offline scheduled batch job — NOT in runtime critical path |
| **Hinglish Normalizer** | Custom (indic-transliteration lib) | Phonetic token normalization for Romanized Hindi queries |
| **Language Detection** | langdetect / lingua-py | Lightweight query language classification |
| **Dense Embedder** | BGE-M3 (BAAI, open weights) | Multilingual dense retrieval, 97.6% top-k accuracy (Son et al., 2025) |
| **Sparse Search** | BM25 (rank-bm25) | Exact matching for circular IDs, form numbers, dates |
| **Vector Store** | **ChromaDB** | Persistent, Python-native, no ambiguity — chosen for prototype |
| **Relational DB** | **SQLite** | Session history, audit trails, escalation queue — chosen for prototype |

---

## 6. Research Contributions (IEEE Paper Sections)

| Section | Contribution |
|---|---|
| **Section III-A** | Adaptive OCR Routing: quality-based dispatcher across PyMuPDF / Tesseract / Pixtral-12B |
| **Section III-B** | Hinglish Normalization Pipeline: two-step phonetic transliteration + intent-keyword extraction |
| **Section III-C** | Hybrid Retrieval: BGE-M3 + BM25 + RRF + cross-encoder re-ranking |
| **Section III-D** | Self-Corrective LangGraph Pipeline: 5-node stateful agentic orchestration |
| **Section IV** | Evaluation: OCR CER/WER benchmark, RAGAS scores, cross-lingual consistency, workload deflection rate |

---

## 7. Project Evaluation Plan

Three measurable evaluation criteria:

1. **OCR Accuracy (Table II in paper):** CER and WER benchmarked across PyMuPDF, Tesseract, and Pixtral-12B on a curated set of 50+ MAIT notice images with ground-truth transcriptions.
2. **RAG Quality (RAGAS framework):** Context relevance, answer faithfulness, and citation precision across a benchmark of 200 verified institutional Q&A pairs (English + Hindi/Hinglish).
3. **Administrative Workload Deflection:** Percentage of routine queries successfully resolved by the bot vs. escalated to staff — targeting 80%+ deflection rate.

---

## 8. What Was Removed and Why

| Removed | Reason |
|---|---|
| Voice/audio input | Out of scope for minor project prototype; listed as future work |
| Marathi + Tamil support | Expands evaluation scope significantly; deferred to future work |
| FAISS (ambiguous OR with ChromaDB) | Decided: ChromaDB for prototype |
| PostgreSQL (ambiguous OR with SQLite) | Decided: SQLite for prototype |
| EasyOCR | Replaced by Pixtral-12B for noisy images (better accuracy, citable) |
| Live scraper as primary runtime fallback | Demoted to last-resort-only in Node 2; primary fallback is ChromaDB re-query |
