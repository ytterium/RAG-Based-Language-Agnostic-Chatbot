# RAG-Based Language Agnostic Chatbot

**Team MNP059 | MAIT CSE | B.Tech VII Semester (2023–2027)**

> An agentic, self-corrective Retrieval-Augmented Generation (RAG) chatbot for multilingual academic query resolution — with adaptive OCR routing for scanned institutional notices.

---

## Team

| Name | Enrollment No. |
|---|---|
| Yash Jain | 02596402723 |
| Yash Mishra | 02396402723 |
| Uday Khanna | 01096402723 |

**Project Guide:** Ms. Prachi Gupta

---

## Architecture Overview

```
Student Query (English / Hindi / Hinglish)
         │
         ▼
Layer 3: Linguistic Pre-Processing  [RUNS FIRST]
  ├── Language Detector
  ├── Hinglish Normalizer (phonetic transliteration)
  └── Contextual Query Rewriter
         │
         ▼
Layer 2: Hybrid Retrieval Engine
  ├── BGE-M3 Dense Retrieval (ChromaDB)
  ├── BM25 Sparse Retrieval
  ├── RRF Fusion (k=60)
  └── Cross-Encoder Re-Ranker → Top-3 Passages
         │
         ▼
Layer 4: LangGraph Self-Corrective Engine
  ├── Node 1: Relevance Grader (θ=0.70)
  ├── Node 2: Query Reformulation + Fallback
  ├── Node 3: Grounded Generation (Mistral 7B)
  ├── Node 4: Hallucination Grader
  └── Node 5: Language Consistency Validator
         │
         ▼
  Response + Citation Cards  OR  Escalate to Admin

Layer 1: Offline Ingestion (Scheduled Batch)
  ├── Web Scraper (bs4)
  └── Adaptive OCR Router
        ├── Digital PDF → PyMuPDF
        ├── Clean Scan → Tesseract 5.x
        └── Noisy Image → Pixtral-12B (Vision LLM)
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Generation LLM | Mistral 7B Instruct (open weights, Ollama) |
| Vision OCR | Pixtral-12B (open weights, Ollama) |
| Classic OCR | Tesseract 5.x + OpenCV |
| PDF Parsing | PyMuPDF |
| Dense Embeddings | BGE-M3 (BAAI) |
| Sparse Search | BM25 (rank-bm25) |
| Vector Store | ChromaDB |
| Orchestration | LangGraph + LangChain |
| Backend | Python + Flask |
| Frontend | ReactJS + Tailwind CSS |
| Database | SQLite |
| Evaluation | RAGAS Framework |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed

```powershell
# 1. Pull required models
ollama pull mistral
ollama pull pixtral

# 2. Install Tesseract
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# 3. Backend setup
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 4. Build the index (place documents in data/raw/pdfs/ and data/raw/scanned_images/)
python run_ingestion.py

# 5. Start the API
python app.py

# 6. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Project Documents

| Document | Description |
|---|---|
| [`project_implementation.md`](./project_implementation.md) | Step-by-step implementation guide with checklists and AI handoff protocol |
| [`ieee_paper_draft.md`](./ieee_paper_draft.md) | IEEE research paper draft |
| [`architecture/architecture_spec_UPDATED.md`](./architecture/architecture_spec_UPDATED.md) | Full architecture specification |
| [`IEEE_Paper_RAG_Chatbot.docx`](./IEEE_Paper_RAG_Chatbot.docx) | Shareable IEEE paper (Word format) |

---

## Implementation Progress

See [`project_implementation.md`](./project_implementation.md) for the full checklist and current status.

| Milestone | Status |
|---|---|
| M1: Environment Setup | ⬜ Pending |
| M2: Adaptive OCR & Ingestion Pipeline | ⬜ Pending |
| M3: Hybrid Retrieval Engine | ⬜ Pending |
| M4: Linguistic Pre-Processing | ⬜ Pending |
| M5: LangGraph Self-Corrective Engine | ⬜ Pending |
| M6: SQLite Database Layer | ⬜ Pending |
| M7: Flask REST API | ⬜ Pending |
| M8: ReactJS Frontend | ⬜ Pending |
| M9: Evaluation & Benchmarking | ⬜ Pending |

---

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(scope): <short description>

Types: feat | fix | docs | chore | test | refactor | style
```

Examples:
```
feat(ocr): add adaptive OCR router with Pixtral-12B fallback
feat(retrieval): implement BGE-M3 ChromaDB dense search
fix(agent): handle retry loop edge case in Node 2
docs(paper): update results section with RAGAS scores
chore(deps): add sentence-transformers to requirements.txt
test(ocr): add benchmark test for noisy notice images
```

---

## License

Academic project — MAIT, New Delhi. Not for commercial use.
