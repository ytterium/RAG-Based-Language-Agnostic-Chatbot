# Project Implementation Guide: RAG-Based Language Agnostic Chatbot

**Project Title:** RAG-Based Language Agnostic Chatbot for Smart Query Response in Academic Institutions
**Team:** MNP059 | MAIT CSE | B.Tech VII Semester (2023–2027)
**Track:** EdTech / Education Technology
**Architecture:** Agentic Self-Corrective RAG — LangGraph + BGE-M3 + BM25 + Adaptive OCR + Mistral 7B + Flask + ReactJS
**GitHub Repo:** `https://github.com/YOUR_USERNAME/algolens` ← replace with actual URL after creating repo

---

## ⚡ HOW TO USE THIS DOCUMENT (READ FIRST — FOR ANY AI MODEL)

This is a **living implementation guide** designed so that any AI coding assistant can pick it up at any point and continue the work. Follow these rules strictly:

1. **Before starting any task** — read the current milestone's checklist and the `## 🤝 HANDOFF` block at the bottom.
2. **After completing each sub-task** — mark its checkbox `[x]` with a brief inline note.
3. **After completing a full milestone:**
   - Run the **🧪 Test & Verify** block for that milestone — fix ALL errors before proceeding
   - Run the **📦 Git Commit & Push** block — use the exact commit message format shown
   - Replace the `## 🤝 HANDOFF` block at the bottom with a new one
4. **Never delete or modify completed `[x]` items** — they are the audit trail.
5. **Always include relevant file paths** in the handoff note.

---

## 📐 COMMIT MESSAGE CONVENTION (MANDATORY — ALL AI MODELS MUST FOLLOW)

All commits use **Conventional Commits** format:

```
<type>(<scope>): <short imperative description>

[optional body — explain WHY, not what]
```

**Types:** `feat` | `fix` | `test` | `refactor` | `docs` | `chore` | `style`

**Scopes:** `ocr` | `retrieval` | `agent` | `linguistic` | `db` | `api` | `frontend` | `eval` | `config` | `deps`

**✅ Good commit messages:**
```
feat(ocr): add adaptive OCR router with Pixtral-12B fallback
feat(retrieval): implement BGE-M3 ChromaDB dense search
feat(retrieval): add BM25 sparse index and RRF fusion (k=60)
feat(agent): implement 5-node LangGraph self-corrective pipeline
feat(linguistic): add Hinglish normalizer with phonetic transliteration
feat(linguistic): add contextual query rewriter for multi-turn chats
feat(db): add SQLite schema for query_logs and escalation_tickets
feat(api): add Flask REST API with /chat /health /unresolved /feedback
feat(frontend): add chat UI with citation cards and escalation card
fix(ocr): correct Tesseract binary path on Windows
fix(agent): handle infinite retry loop in Node 2 edge case
test(ocr): add benchmark comparing PyMuPDF vs Tesseract vs Pixtral-12B
test(retrieval): verify BM25 exact match on circular IDs and form numbers
chore(deps): add sentence-transformers chromadb rank-bm25 to requirements
refactor(agent): extract node functions from graph.py into nodes.py
docs(paper): update IEEE paper results section with RAGAS evaluation data
```

**❌ NEVER do this:**
```
git commit -m "update"
git commit -m "fixed bug"
git commit -m "changes"
git commit -m "working now"
```

---

## 📋 ARCHITECTURE DECISIONS (LOCKED — DO NOT CHANGE WITHOUT DISCUSSION)

| Decision | Choice | Reason |
|---|---|---|
| **Generation LLM** | Mistral 7B Instruct (open weights, Apache 2.0) | Citable: Jiang et al., arXiv:2310.06825. Reproducible. Free. |
| **OCR — Digital PDFs** | PyMuPDF | Fast, layout-aware, free |
| **OCR — Clean scans** | Tesseract 5.x | Fast, free, local. Cite: Smith 2007 |
| **OCR — Noisy/complex images** | Pixtral-12B (open weights) | Best quality. Cite: Agrawal et al., arXiv:2410.07073 |
| **OCR Preprocessing** | OpenCV | Binarize, deskew before Tesseract |
| **Dense Embedder** | BGE-M3 (BAAI, open weights) | Multilingual, citable: Chen et al., arXiv:2309.07597 |
| **Sparse Search** | BM25 (rank-bm25) | Exact keyword/date/ID matching |
| **Vector Store** | ChromaDB (persistent) | Decided. Not FAISS. |
| **Relational DB** | SQLite | Decided. Not PostgreSQL. |
| **Orchestration** | LangGraph + LangChain | Stateful self-corrective graph |
| **Backend** | Python + Flask | Lightweight REST API |
| **Frontend** | ReactJS + Tailwind CSS | Chat UI + Citation Cards |
| **Languages in scope** | English + Hindi + Hinglish | Marathi/Tamil deferred to future work |
| **Web scraper** | bs4 (BeautifulSoup) | Offline scheduled batch job ONLY — NOT in runtime path |
| **Voice input** | ❌ Removed | Out of scope for v1 |

> **RUNTIME ORDER:** Layer 3 (Linguistic) → Layer 2 (Retrieval via Layer 1 index) → Layer 4 (LangGraph)
> Layer 1 (Ingestion) runs as an **offline scheduled batch job**, never at query time.

---

---

## 📋 ARCHITECTURE DECISIONS (LOCKED — DO NOT CHANGE WITHOUT DISCUSSION)

These are final. Do not deviate from them:

| Decision | Choice | Reason |
|---|---|---|
| **Generation LLM** | Mistral 7B Instruct (open weights, Apache 2.0) | Citable: Jiang et al., arXiv:2310.06825. Reproducible. Free. |
| **OCR — Digital PDFs** | PyMuPDF | Fast, layout-aware, free |
| **OCR — Clean scans** | Tesseract 5.x | Fast, free, local. Cite: Smith 2007 |
| **OCR — Noisy/complex images** | Pixtral-12B (open weights) | Best quality. Cite: Agrawal et al., arXiv:2410.07073 |
| **OCR Preprocessing** | OpenCV | Binarize, deskew before Tesseract |
| **Dense Embedder** | BGE-M3 (BAAI, open weights) | Multilingual, citable: Chen et al., arXiv:2309.07597 |
| **Sparse Search** | BM25 (rank-bm25) | Exact keyword/date/ID matching |
| **Vector Store** | ChromaDB (persistent) | Decided. Not FAISS. |
| **Relational DB** | SQLite | Decided. Not PostgreSQL. |
| **Orchestration** | LangGraph + LangChain | Stateful self-corrective graph |
| **Backend** | Python + Flask | Lightweight REST API |
| **Frontend** | ReactJS + Tailwind CSS | Chat UI + Citation Cards |
| **Languages in scope** | English + Hindi + Hinglish | Marathi/Tamil deferred to future work |
| **Web scraper** | bs4 (BeautifulSoup) | Offline scheduled batch job ONLY — NOT in runtime path |
| **Voice input** | ❌ Removed | Out of scope for v1 |

> **RUNTIME ORDER:** Layer 3 (Linguistic Pre-processing) → Layer 2 (Retrieval using Layer 1's offline index) → Layer 4 (LangGraph Engine)
> Layer 1 (Ingestion) runs as an **offline scheduled batch job**, never at query time.

---

## 1. Technology Stack

| System Layer | Library / Model | Install Command |
|---|---|---|
| **Generation LLM** | Mistral 7B Instruct via Ollama | `ollama pull mistral` |
| **LLM Python client** | ollama-python | `pip install ollama` |
| **OCR — Digital PDF** | PyMuPDF | `pip install pymupdf` |
| **OCR — Clean scans** | Tesseract 5.x + pytesseract | Install Tesseract binary + `pip install pytesseract` |
| **OCR — Noisy images** | Pixtral-12B via Ollama | `ollama pull pixtral` |
| **OCR Preprocessing** | OpenCV | `pip install opencv-python` |
| **Dense Embedder** | BGE-M3 (BAAI) | `pip install sentence-transformers` |
| **Vector Store** | ChromaDB | `pip install chromadb` |
| **Sparse Search** | rank-bm25 | `pip install rank-bm25` |
| **Re-Ranker** | BAAI/bge-reranker-v2-m3 | `pip install sentence-transformers` |
| **Orchestration** | LangGraph + LangChain | `pip install langgraph langchain langchain-community` |
| **Language Detection** | lingua-py | `pip install lingua-language-detector` |
| **Hinglish Normalization** | indic-transliteration | `pip install indic-transliteration` |
| **Web Scraper** | BeautifulSoup4 | `pip install beautifulsoup4 requests` |
| **Backend API** | Flask + Flask-CORS | `pip install flask flask-cors` |
| **SQL DB** | SQLite (built-in) + SQLAlchemy | `pip install sqlalchemy` |
| **Frontend** | ReactJS + Vite + Tailwind | `npm create vite@latest frontend -- --template react` |
| **Evaluation** | RAGAS | `pip install ragas` |

---

## 2. Final Project Directory Structure

```text
minor/
├── README.md
├── project_implementation.md          ← This file — living guide
├── architecture/
│   ├── architecture_spec_UPDATED.md   ← Full architecture spec (source of truth)
│   └── architecture_FINAL.jpg         ← Visual diagram
│
├── data/
│   ├── raw/
│   │   ├── pdfs/                      ← Digital PDF circulars
│   │   ├── scanned_images/            ← Scanned noticeboard images (.jpg/.png)
│   │   └── scraped/                   ← Web-scraped notice text files
│   └── processed/
│       ├── chromadb/                  ← Persistent ChromaDB vector store
│       ├── bm25_store.pkl             ← Serialized BM25 index
│       └── ocr_cache/                 ← Cached OCR outputs (avoid re-processing)
│
├── backend/
│   ├── app.py                         ← Flask REST API entry point
│   ├── config.py                      ← All config constants (paths, thresholds, model names)
│   ├── requirements.txt               ← Python dependencies
│   ├── run_ingestion.py               ← CLI script: run offline ingestion pipeline
│   │
│   ├── ingestion/                     ← LAYER 1: Offline ingestion (batch only)
│   │   ├── __init__.py
│   │   ├── ocr_router.py              ← Adaptive OCR dispatcher (PyMuPDF / Tesseract / Pixtral)
│   │   ├── pdf_parser.py              ← PyMuPDF digital PDF text + table extraction
│   │   ├── tesseract_ocr.py           ← Tesseract OCR + OpenCV preprocessing
│   │   ├── pixtral_ocr.py             ← Pixtral-12B vision OCR for noisy images
│   │   ├── web_crawler.py             ← BeautifulSoup scraper (scheduled batch, not runtime)
│   │   └── chunker.py                 ← Recursive semantic chunker + metadata tagging
│   │
│   ├── retrieval/                     ← LAYER 2: Hybrid retrieval (query-time)
│   │   ├── __init__.py
│   │   ├── embedder.py                ← BGE-M3 dense embedding wrapper + ChromaDB interface
│   │   ├── sparse_search.py           ← BM25 lexical retriever
│   │   ├── rrf_fusion.py              ← Reciprocal Rank Fusion (RRF, k=60)
│   │   └── reranker.py                ← Cross-encoder re-ranking → top-3 passages
│   │
│   ├── linguistic/                    ← LAYER 3: Linguistic pre-processing (query-time, runs first)
│   │   ├── __init__.py
│   │   ├── detector.py                ← Language detection (English / Hindi / Hinglish)
│   │   ├── normalizer.py              ← Hinglish phonetic transliteration + intent extraction
│   │   └── query_rewriter.py          ← Contextual query rewriter (resolves follow-up refs)
│   │
│   ├── agent/                         ← LAYER 4: LangGraph self-corrective engine (query-time)
│   │   ├── __init__.py
│   │   ├── state.py                   ← AgentState TypedDict definition
│   │   ├── nodes.py                   ← All 5 LangGraph nodes
│   │   ├── edges.py                   ← Conditional routing + retry logic
│   │   └── graph.py                   ← Compiled LangGraph workflow
│   │
│   └── db/
│       ├── __init__.py
│       ├── models.py                  ← SQLite schema (query_logs, escalation_tickets)
│       └── database.py                ← SQLAlchemy connection + CRUD helpers
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── components/
        │   ├── ChatWindow.jsx         ← Message feed + auto-scroll
        │   ├── MessageBubble.jsx      ← Bot/user message formatting
        │   ├── CitationCard.jsx       ← Clickable source reference cards
        │   ├── LanguageBadge.jsx      ← Shows detected language
        │   └── EscalationCard.jsx     ← Helpdesk contact card on fallback
        └── services/
            └── api.js                 ← Axios client for Flask API
```

---

## 3. Step-by-Step Implementation Roadmap

---

### ✅ Milestone 1: Environment Setup

**Goal:** Get a working dev environment with all dependencies installed and verified.

- [ ] **1.1** Create the full directory structure from Section 2 above.
  ```powershell
  # Run from C:\Users\ynj02\Desktop\minor\
  mkdir backend, backend\ingestion, backend\retrieval, backend\linguistic, backend\agent, backend\db
  mkdir data\raw\pdfs, data\raw\scanned_images, data\raw\scraped, data\processed\chromadb, data\processed\ocr_cache
  mkdir frontend
  New-Item backend\__init__.py, backend\ingestion\__init__.py, backend\retrieval\__init__.py -ItemType File
  New-Item backend\linguistic\__init__.py, backend\agent\__init__.py, backend\db\__init__.py -ItemType File
  ```

- [ ] **1.2** Create and activate Python virtual environment, install all backend dependencies.
  ```powershell
  cd C:\Users\ynj02\Desktop\minor\backend
  python -m venv venv
  .\venv\Scripts\activate
  pip install flask flask-cors sqlalchemy
  pip install langgraph langchain langchain-community langchain-ollama
  pip install sentence-transformers chromadb rank-bm25
  pip install pymupdf pytesseract opencv-python
  pip install requests beautifulsoup4
  pip install lingua-language-detector indic-transliteration
  pip install ollama ragas
  pip freeze > requirements.txt
  ```

- [ ] **1.3** Install Ollama and pull required models.
  ```powershell
  # Download Ollama from https://ollama.com and install
  ollama pull mistral        # Mistral 7B Instruct for generation
  ollama pull mistrallite    # Optional: lighter version for low VRAM
  # Pixtral for noisy OCR - pull when needed (large model)
  # ollama pull pixtral
  ollama list                # Verify models are available
  ```

- [ ] **1.4** Install Tesseract binary (Windows).
  ```powershell
  # Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
  # Install to default path: C:\Program Files\Tesseract-OCR\tesseract.exe
  # Verify:
  & "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
  ```

- [ ] **1.5** Create `backend/config.py` with all system constants.
  ```python
  # backend/config.py
  import os

  # Paths
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
  RAW_PDFS_DIR = os.path.join(DATA_DIR, 'raw', 'pdfs')
  RAW_IMAGES_DIR = os.path.join(DATA_DIR, 'raw', 'scanned_images')
  CHROMADB_PATH = os.path.join(DATA_DIR, 'processed', 'chromadb')
  BM25_STORE_PATH = os.path.join(DATA_DIR, 'processed', 'bm25_store.pkl')
  OCR_CACHE_DIR = os.path.join(DATA_DIR, 'processed', 'ocr_cache')
  SQLITE_DB_PATH = os.path.join(DATA_DIR, 'chatbot_audit.db')

  # OCR
  TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  OCR_SHARPNESS_THRESHOLD = 100.0   # Laplacian variance threshold: below = use Pixtral

  # Retrieval
  CHROMA_COLLECTION_NAME = "mait_notices"
  BGE_M3_MODEL = "BAAI/bge-m3"
  RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
  RRF_K = 60
  TOP_K_FUSED = 10
  TOP_K_FINAL = 3
  RELEVANCE_THRESHOLD = 0.70

  # LLM
  OLLAMA_MODEL = "mistral"           # Generation model
  OLLAMA_VISION_MODEL = "pixtral"    # Vision OCR model
  OLLAMA_BASE_URL = "http://localhost:11434"

  # Chunking
  CHUNK_SIZE_TOKENS = 500
  CHUNK_OVERLAP_TOKENS = 100

  # Agent
  MAX_RETRY_COUNT = 2
  ```

- [ ] **1.6** Scaffold React frontend.
  ```powershell
  cd C:\Users\ynj02\Desktop\minor
  npm create vite@latest frontend -- --template react
  cd frontend
  npm install
  npm install tailwindcss postcss autoprefixer axios lucide-react
  npx tailwindcss init -p
  ```

- [ ] **1.7** Verify entire setup: Python imports, Ollama running, Tesseract binary found.
  ```python
  # Run this quick verification check
  import chromadb, langchain, langgraph, ollama, fitz, pytesseract, cv2
  from sentence_transformers import SentenceTransformer
  from lingua import LanguageDetectorBuilder
  print("All imports OK")
  response = ollama.chat(model='mistral', messages=[{'role':'user','content':'Say OK'}])
  print("Ollama OK:", response['message']['content'])
  ```

#### 🧪 Test & Verify — Milestone 1
```powershell
# Run this in backend/ with venv activated — ALL must pass before committing
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
python -c "import chromadb, langchain, langgraph, ollama, fitz, pytesseract, cv2, flask, rank_bm25; print('ALL IMPORTS OK')"
python -c "from lingua import Language, LanguageDetectorBuilder; print('lingua OK')"
python -c "from sentence_transformers import SentenceTransformer; print('sentence-transformers OK')"
ollama list   # Must show: mistral
& "C:\Program Files\Tesseract-OCR\tesseract.exe" --version   # Must show version
python -c "import ollama; r=ollama.chat(model='mistral',messages=[{'role':'user','content':'Say OK'}]); print('Mistral OK:', r['message']['content'])"
```
> Fix any ImportError or connection error before moving to Milestone 2.

#### 📦 Git Commit & Push — Milestone 1
```powershell
cd C:\Users\ynj02\Desktop\minor
git add backend/requirements.txt backend/config.py backend/__init__.py
git add backend/ingestion/__init__.py backend/retrieval/__init__.py
git add backend/linguistic/__init__.py backend/agent/__init__.py backend/db/__init__.py
git add frontend/package.json frontend/vite.config.js frontend/tailwind.config.js
git commit -m "chore(deps): environment setup — all dependencies installed and verified

- Python venv created with all required packages
- Ollama installed with mistral model pulled
- Tesseract 5.x installed at C:/Program Files/Tesseract-OCR/
- React frontend scaffolded with Tailwind CSS
- config.py created with all system constants"
git push origin main
```

---

### ✅ Milestone 2: Layer 1 — Adaptive OCR & Ingestion Pipeline

**Goal:** Build the offline ingestion pipeline. Given a folder of PDFs and scanned images, produce metadata-tagged text chunks ready for indexing.

**Key files to create:**
- `backend/ingestion/ocr_router.py`
- `backend/ingestion/pdf_parser.py`
- `backend/ingestion/tesseract_ocr.py`
- `backend/ingestion/pixtral_ocr.py`
- `backend/ingestion/chunker.py`
- `backend/ingestion/web_crawler.py`
- `backend/run_ingestion.py`

- [ ] **2.1** Implement `backend/ingestion/pdf_parser.py` — PyMuPDF digital PDF parser.
  ```python
  # backend/ingestion/pdf_parser.py
  import fitz  # PyMuPDF

  def extract_text_from_pdf(pdf_path: str) -> list[dict]:
      """Extract text page-by-page from a searchable PDF. Returns list of page dicts."""
      doc = fitz.open(pdf_path)
      pages = []
      for page_num in range(len(doc)):
          page = doc[page_num]
          text = page.get_text("text").strip()
          tables = page.find_tables()
          table_text = ""
          for table in tables.tables:
              table_text += " | ".join(
                  [" ".join([cell or "" for cell in row]) for row in table.extract()]
              ) + "\n"
          pages.append({
              "page_num": page_num + 1,
              "text": text + "\n" + table_text,
              "is_searchable": bool(text)
          })
      return pages
  ```

- [ ] **2.2** Implement `backend/ingestion/tesseract_ocr.py` — Tesseract + OpenCV preprocessing.
  ```python
  # backend/ingestion/tesseract_ocr.py
  import cv2
  import numpy as np
  import pytesseract
  from config import TESSERACT_PATH

  pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

  def compute_sharpness(image: np.ndarray) -> float:
      """Laplacian variance — higher = sharper image."""
      gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      return cv2.Laplacian(gray, cv2.CV_64F).var()

  def preprocess_image(image: np.ndarray) -> np.ndarray:
      """Binarize + deskew image before OCR."""
      gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
      return binary

  def run_tesseract(image_path: str) -> str:
      """Run Tesseract OCR on a clean/preprocessed image."""
      img = cv2.imread(image_path)
      preprocessed = preprocess_image(img)
      return pytesseract.image_to_string(preprocessed, lang='eng')
  ```

- [ ] **2.3** Implement `backend/ingestion/pixtral_ocr.py` — Pixtral-12B vision OCR for noisy images.
  ```python
  # backend/ingestion/pixtral_ocr.py
  import ollama
  import base64
  from config import OLLAMA_VISION_MODEL

  def image_to_base64(image_path: str) -> str:
      with open(image_path, "rb") as f:
          return base64.b64encode(f.read()).decode("utf-8")

  def run_pixtral_ocr(image_path: str) -> str:
      """Use Pixtral-12B to extract text from noisy/complex notice images."""
      img_b64 = image_to_base64(image_path)
      response = ollama.chat(
          model=OLLAMA_VISION_MODEL,
          messages=[{
              "role": "user",
              "content": (
                  "You are an OCR assistant. Extract ALL text visible in this institutional "
                  "notice image exactly as it appears. Preserve dates, form numbers, circular "
                  "IDs, and amounts. Do not summarize. Output only the extracted text."
              ),
              "images": [img_b64]
          }]
      )
      return response["message"]["content"]
  ```

- [ ] **2.4** Implement `backend/ingestion/ocr_router.py` — the adaptive OCR dispatcher.
  ```python
  # backend/ingestion/ocr_router.py
  import cv2
  import fitz
  from config import OCR_SHARPNESS_THRESHOLD
  from ingestion.pdf_parser import extract_text_from_pdf
  from ingestion.tesseract_ocr import run_tesseract, compute_sharpness
  from ingestion.pixtral_ocr import run_pixtral_ocr

  def route_and_extract(file_path: str) -> dict:
      """
      Adaptive OCR router.
      Returns: {"text": str, "method": str, "source": str}
      """
      ext = file_path.lower().split(".")[-1]

      # PATH A: Digital searchable PDF
      if ext == "pdf":
          pages = extract_text_from_pdf(file_path)
          if any(p["is_searchable"] for p in pages):
              full_text = "\n".join([p["text"] for p in pages])
              return {"text": full_text, "method": "pymupdf", "source": file_path}
          # PDF with no text layer — treat pages as images (fall through to image OCR)
          # For now, return empty and let caller handle raster PDF conversion
          return {"text": "", "method": "pymupdf_empty", "source": file_path}

      # PATH B or C: Image file
      elif ext in ("jpg", "jpeg", "png", "tiff", "bmp"):
          img = cv2.imread(file_path)
          sharpness = compute_sharpness(img)
          if sharpness >= OCR_SHARPNESS_THRESHOLD:
              # PATH B: Clean image → Tesseract
              text = run_tesseract(file_path)
              return {"text": text, "method": "tesseract", "source": file_path}
          else:
              # PATH C: Noisy/degraded image → Pixtral
              text = run_pixtral_ocr(file_path)
              return {"text": text, "method": "pixtral-12b", "source": file_path}

      else:
          raise ValueError(f"Unsupported file type: {ext}")
  ```

- [ ] **2.5** Implement `backend/ingestion/chunker.py` — metadata-rich semantic chunker.
  ```python
  # backend/ingestion/chunker.py
  import re
  from config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS

  def chunk_text(text: str, metadata: dict) -> list[dict]:
      """
      Recursively chunk text with token window + overlap.
      metadata must include: source, date, department, circular_number, ocr_method
      """
      words = text.split()
      chunks = []
      step = CHUNK_SIZE_TOKENS - CHUNK_OVERLAP_TOKENS
      for i, start in enumerate(range(0, len(words), step)):
          chunk_words = words[start:start + CHUNK_SIZE_TOKENS]
          if len(chunk_words) < 20:   # Skip tiny trailing chunks
              continue
          chunk_text = " ".join(chunk_words)
          chunk_meta = {
              **metadata,
              "chunk_index": i,
              "chunk_id": f"{metadata.get('source', 'unknown')}_chunk_{i}"
          }
          chunks.append({"text": chunk_text, "metadata": chunk_meta})
      return chunks
  ```

- [ ] **2.6** Implement `backend/ingestion/web_crawler.py` — scheduled offline scraper.
  ```python
  # backend/ingestion/web_crawler.py
  # NOTE: This runs as an OFFLINE batch job (run_ingestion.py) — NOT at query time.
  import requests
  from bs4 import BeautifulSoup
  from datetime import datetime

  NOTICE_BOARD_URLS = [
      # Add MAIT notice board URLs here
      "https://www.mait.ac.in/notices.php",
  ]

  def scrape_notices() -> list[dict]:
      """Scrape institutional notice boards and return list of notice dicts."""
      all_notices = []
      for url in NOTICE_BOARD_URLS:
          try:
              resp = requests.get(url, timeout=10)
              soup = BeautifulSoup(resp.text, "html.parser")
              # TODO: Adjust selectors to match actual MAIT notice board HTML structure
              notices = soup.find_all("div", class_="notice-item")
              for n in notices:
                  title = n.find("h3") or n.find("a")
                  date = n.find("span", class_="date")
                  all_notices.append({
                      "text": title.get_text(strip=True) if title else "",
                      "metadata": {
                          "source": url,
                          "date": date.get_text(strip=True) if date else str(datetime.today().date()),
                          "department": "General",
                          "circular_number": "",
                          "ocr_method": "web_scrape"
                      }
                  })
          except Exception as e:
              print(f"[SCRAPER] Failed to scrape {url}: {e}")
      return all_notices
  ```

- [ ] **2.7** Implement `backend/run_ingestion.py` — CLI entry point for the full offline pipeline.
  ```python
  # backend/run_ingestion.py
  # Run this script to rebuild the ChromaDB and BM25 index from scratch.
  # Usage: python run_ingestion.py
  import os, pickle, sys
  sys.path.insert(0, os.path.dirname(__file__))

  from config import RAW_PDFS_DIR, RAW_IMAGES_DIR, BM25_STORE_PATH, CHROMA_COLLECTION_NAME, CHROMADB_PATH
  from ingestion.ocr_router import route_and_extract
  from ingestion.chunker import chunk_text
  from ingestion.web_crawler import scrape_notices
  from retrieval.embedder import build_chromadb_index
  from retrieval.sparse_search import build_bm25_index

  def run_ingestion():
      all_chunks = []

      # 1. Process all PDFs
      for fname in os.listdir(RAW_PDFS_DIR):
          fpath = os.path.join(RAW_PDFS_DIR, fname)
          result = route_and_extract(fpath)
          if result["text"]:
              meta = {"source": fname, "date": "", "department": "", "circular_number": "", "ocr_method": result["method"]}
              all_chunks.extend(chunk_text(result["text"], meta))
              print(f"[INGESTION] {fname} → {result['method']} → {len(all_chunks)} chunks so far")

      # 2. Process scanned images
      for fname in os.listdir(RAW_IMAGES_DIR):
          fpath = os.path.join(RAW_IMAGES_DIR, fname)
          result = route_and_extract(fpath)
          if result["text"]:
              meta = {"source": fname, "date": "", "department": "", "circular_number": "", "ocr_method": result["method"]}
              all_chunks.extend(chunk_text(result["text"], meta))

      # 3. Scrape live notices (offline batch)
      web_notices = scrape_notices()
      for notice in web_notices:
          all_chunks.extend(chunk_text(notice["text"], notice["metadata"]))

      print(f"[INGESTION] Total chunks: {len(all_chunks)}")

      # 4. Build ChromaDB index
      build_chromadb_index(all_chunks)
      print("[INGESTION] ChromaDB index built.")

      # 5. Build BM25 index
      bm25 = build_bm25_index(all_chunks)
      with open(BM25_STORE_PATH, "wb") as f:
          pickle.dump({"bm25": bm25, "chunks": all_chunks}, f)
      print(f"[INGESTION] BM25 index saved to {BM25_STORE_PATH}")

  if __name__ == "__main__":
      run_ingestion()
  ```

  ```powershell
  # Run ingestion from backend directory:
  cd C:\Users\ynj02\Desktop\minor\backend
  .\venv\Scripts\activate
  python run_ingestion.py
  ```

#### 🧪 Test & Verify — Milestone 2
```powershell
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
# Test 1: Digital PDF extraction
python -c "from ingestion.pdf_parser import extract_text_from_pdf; r=extract_text_from_pdf('../data/raw/pdfs/scholarship_2026.pdf'); print('Pages extracted:', len(r)); print('Sample:', r[0]['text'][:200])"
# Test 2: OCR router — put a clean image in data/raw/scanned_images/ and test
python -c "from ingestion.ocr_router import route_and_extract; r=route_and_extract('../data/raw/scanned_images/test_notice.jpg'); print('Method:', r['method']); print('Text:', r['text'][:200])"
# Test 3: Chunker
python -c "from ingestion.chunker import chunk_text; c=chunk_text('word '*600, {'source':'test','date':'','department':'','circular_number':'','ocr_method':'test'}); print('Chunks:', len(c)); print('First chunk tokens:', len(c[0]['text'].split()))"
# Test 4: Full ingestion run (needs at least 1 PDF in data/raw/pdfs/)
python run_ingestion.py
# Expected output: "[INGESTION] Total chunks: N" and "[INGESTION] ChromaDB index built."
```
> All 4 tests must produce output without errors. If ChromaDB or BM25 file not created, debug run_ingestion.py.

#### 📦 Git Commit & Push — Milestone 2
```powershell
cd C:\Users\ynj02\Desktop\minor
git add backend/ingestion/ backend/run_ingestion.py
git commit -m "feat(ocr): adaptive OCR ingestion pipeline with 3-path router

- pdf_parser.py: PyMuPDF layout-aware text and table extraction
- tesseract_ocr.py: Tesseract 5.x with OpenCV binarize/deskew preprocessing
- pixtral_ocr.py: Pixtral-12B vision LLM for noisy/complex notice images
- ocr_router.py: quality-aware dispatcher using Laplacian sharpness metric
- chunker.py: 500-token/100-overlap recursive chunker with metadata tagging
- web_crawler.py: BeautifulSoup offline batch scraper for notice boards
- run_ingestion.py: CLI entry point building ChromaDB + BM25 index"
git push origin main
```

---

### ✅ Milestone 3: Layer 2 — Hybrid Retrieval Engine

**Goal:** Build ChromaDB-backed dense retrieval + BM25 sparse retrieval + RRF fusion + cross-encoder re-ranking.

**Key files to create:**
- `backend/retrieval/embedder.py`
- `backend/retrieval/sparse_search.py`
- `backend/retrieval/rrf_fusion.py`
- `backend/retrieval/reranker.py`

- [ ] **3.1** Implement `backend/retrieval/embedder.py` — BGE-M3 + ChromaDB interface.
  ```python
  # backend/retrieval/embedder.py
  import chromadb
  from sentence_transformers import SentenceTransformer
  from config import BGE_M3_MODEL, CHROMADB_PATH, CHROMA_COLLECTION_NAME, TOP_K_FUSED

  _embed_model = None
  _chroma_client = None
  _collection = None

  def get_embed_model():
      global _embed_model
      if _embed_model is None:
          _embed_model = SentenceTransformer(BGE_M3_MODEL)
      return _embed_model

  def get_collection():
      global _chroma_client, _collection
      if _collection is None:
          _chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
          _collection = _chroma_client.get_or_create_collection(CHROMA_COLLECTION_NAME)
      return _collection

  def build_chromadb_index(chunks: list[dict]):
      """Index all chunks into ChromaDB. Called by run_ingestion.py."""
      model = get_embed_model()
      collection = get_collection()
      texts = [c["text"] for c in chunks]
      ids = [c["metadata"]["chunk_id"] for c in chunks]
      metadatas = [c["metadata"] for c in chunks]
      embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=True).tolist()
      collection.add(documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids)

  def dense_search(query: str, top_k: int = TOP_K_FUSED) -> list[dict]:
      """Search ChromaDB with BGE-M3 embeddings. Returns list of result dicts."""
      model = get_embed_model()
      collection = get_collection()
      q_embedding = model.encode([query], normalize_embeddings=True).tolist()
      results = collection.query(query_embeddings=q_embedding, n_results=top_k)
      return [
          {"text": doc, "metadata": meta, "score": 1 - dist, "rank_index": i}
          for i, (doc, meta, dist) in enumerate(
              zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
          )
      ]
  ```

- [ ] **3.2** Implement `backend/retrieval/sparse_search.py` — BM25 lexical retriever.
  ```python
  # backend/retrieval/sparse_search.py
  import pickle
  from rank_bm25 import BM25Okapi
  from config import BM25_STORE_PATH, TOP_K_FUSED

  _bm25 = None
  _chunks = None

  def build_bm25_index(chunks: list[dict]) -> BM25Okapi:
      texts = [c["text"] for c in chunks]
      tokenized = [t.lower().split() for t in texts]
      return BM25Okapi(tokenized)

  def load_bm25():
      global _bm25, _chunks
      if _bm25 is None:
          with open(BM25_STORE_PATH, "rb") as f:
              data = pickle.load(f)
          _bm25 = data["bm25"]
          _chunks = data["chunks"]
      return _bm25, _chunks

  def sparse_search(query: str, top_k: int = TOP_K_FUSED) -> list[dict]:
      bm25, chunks = load_bm25()
      tokenized_query = query.lower().split()
      scores = bm25.get_scores(tokenized_query)
      top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
      return [
          {"text": chunks[i]["text"], "metadata": chunks[i]["metadata"], "score": float(scores[i]), "rank_index": idx}
          for idx, i in enumerate(top_indices)
      ]
  ```

- [ ] **3.3** Implement `backend/retrieval/rrf_fusion.py` — RRF algorithm.
  ```python
  # backend/retrieval/rrf_fusion.py
  from config import RRF_K, TOP_K_FUSED

  def reciprocal_rank_fusion(dense_results: list[dict], sparse_results: list[dict]) -> list[dict]:
      """
      Fuse dense + sparse results using RRF (k=60).
      Returns top-10 fused candidates ranked by combined RRF score.
      """
      scores = {}
      chunk_map = {}

      for rank, result in enumerate(dense_results):
          key = result["metadata"]["chunk_id"]
          scores[key] = scores.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)
          chunk_map[key] = result

      for rank, result in enumerate(sparse_results):
          key = result["metadata"]["chunk_id"]
          scores[key] = scores.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)
          chunk_map[key] = result

      sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
      return [
          {**chunk_map[k], "rrf_score": scores[k]}
          for k in sorted_keys[:TOP_K_FUSED]
      ]
  ```

- [ ] **3.4** Implement `backend/retrieval/reranker.py` — cross-encoder re-ranking to top-3.
  ```python
  # backend/retrieval/reranker.py
  from sentence_transformers import CrossEncoder
  from config import RERANKER_MODEL, TOP_K_FINAL

  _reranker = None

  def get_reranker():
      global _reranker
      if _reranker is None:
          _reranker = CrossEncoder(RERANKER_MODEL)
      return _reranker

  def rerank(query: str, candidates: list[dict]) -> list[dict]:
      """Re-rank top-10 fused candidates. Returns final top-3."""
      reranker = get_reranker()
      pairs = [(query, c["text"]) for c in candidates]
      scores = reranker.predict(pairs)
      ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
      return [c for _, c in ranked[:TOP_K_FINAL]]
  ```

- [ ] **3.5** Write a quick retrieval test to verify the full pipeline:
  ```python
  # Test: python -c "from retrieval.embedder import dense_search; print(dense_search('scholarship form last date'))"
  ```

#### 🧪 Test & Verify — Milestone 3
```powershell
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
# Test 1: Dense search returns results
python -c "from retrieval.embedder import dense_search; r=dense_search('scholarship form last date'); print('Dense hits:', len(r)); print('Top score:', r[0]['score'] if r else 'NO RESULTS')"
# Test 2: BM25 exact match on form number
python -c "from retrieval.sparse_search import sparse_search; r=sparse_search('Form 16-A submission'); print('BM25 hits:', len(r))"
# Test 3: RRF fusion
python -c "from retrieval.embedder import dense_search; from retrieval.sparse_search import sparse_search; from retrieval.rrf_fusion import reciprocal_rank_fusion; d=dense_search('fee deadline'); s=sparse_search('fee deadline'); fused=reciprocal_rank_fusion(d,s); print('Fused candidates:', len(fused))"
# Test 4: Full retrieval pipeline
python -c "from retrieval.embedder import dense_search; from retrieval.sparse_search import sparse_search; from retrieval.rrf_fusion import reciprocal_rank_fusion; from retrieval.reranker import rerank; q='when is the last date for scholarship'; d=dense_search(q); s=sparse_search(q); f=reciprocal_rank_fusion(d,s); top3=rerank(q,f); print('Final top-3 chunks:'); [print(f' - {c[\"metadata\"][\"source\"]} (score: {c.get(\"rrf_score\",0):.3f})') for c in top3]"
```
> Test 2 must return BM25 matches with high score for exact terms. Test 4 must print exactly 3 chunks.

#### 📦 Git Commit & Push — Milestone 3
```powershell
cd C:\Users\ynj02\Desktop\minor
git add backend/retrieval/
git commit -m "feat(retrieval): hybrid retrieval pipeline — BGE-M3 + BM25 + RRF + cross-encoder

- embedder.py: BGE-M3 ChromaDB dense search with lazy model loading
- sparse_search.py: BM25 Okapi index with pickle persistence
- rrf_fusion.py: Reciprocal Rank Fusion (k=60) combining dense + sparse
- reranker.py: BAAI/bge-reranker-v2-m3 cross-encoder producing top-3 passages"
git push origin main
```

---

### ✅ Milestone 4: Layer 3 — Linguistic Pre-Processing

**Goal:** Build the linguistic router — language detection, Hinglish normalization, and contextual query rewriting. This runs FIRST on every incoming query before retrieval.

**Key files to create:**
- `backend/linguistic/detector.py`
- `backend/linguistic/normalizer.py`
- `backend/linguistic/query_rewriter.py`

- [ ] **4.1** Implement `backend/linguistic/detector.py` — language detection.
  ```python
  # backend/linguistic/detector.py
  from lingua import Language, LanguageDetectorBuilder

  SUPPORTED_LANGUAGES = [Language.ENGLISH, Language.HINDI]
  _detector = None

  def get_detector():
      global _detector
      if _detector is None:
          _detector = LanguageDetectorBuilder.from_languages(*SUPPORTED_LANGUAGES).build()
      return _detector

  def detect_language(text: str) -> str:
      """Returns: 'en', 'hi', or 'hi' for Hinglish (detected as Hindi)."""
      detector = get_detector()
      result = detector.detect_language_of(text)
      if result == Language.HINDI:
          return "hi"
      return "en"   # Default to English if uncertain
  ```

- [ ] **4.2** Implement `backend/linguistic/normalizer.py` — Hinglish transliteration + intent extraction.
  ```python
  # backend/linguistic/normalizer.py
  # Research contribution: two-step normalization for Romanized Hindi/Hinglish queries
  import re
  from indic_transliteration import sanscript
  from indic_transliteration.sanscript import transliterate

  # Step 1: Known Hinglish phrase → formal English intent mapping
  HINGLISH_INTENT_MAP = {
      r"last date": "submission deadline",
      r"aakhri taarikh": "submission deadline",
      r"kab submit": "submission deadline",
      r"fees kab bharna": "fee payment schedule",
      r"fees kab bhari": "fee payment schedule",
      r"form kahan milega": "where to get form",
      r"form submit karna": "submit application form",
      r"chutti": "academic holiday",
      r"exam kab hai": "examination date",
      r"result kab aayega": "result announcement date",
      r"scholarship form": "scholarship application form",
      r"kitna paisa": "amount fee",
      r"kitni fees": "fee amount",
  }

  def normalize_hinglish(query: str) -> str:
      """
      Two-step Hinglish normalization:
      1. Map known Hinglish phrases to formal English equivalents.
      2. Pass remaining tokens through for BGE-M3 multilingual embedding.
      """
      normalized = query.lower().strip()
      for pattern, replacement in HINGLISH_INTENT_MAP.items():
          normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
      return normalized

  def normalize_query(query: str, detected_language: str) -> str:
      """Main normalization entry point."""
      if detected_language == "hi":
          return normalize_hinglish(query)
      return query   # English queries pass through unchanged
  ```

- [ ] **4.3** Implement `backend/linguistic/query_rewriter.py` — contextual query rewriter.
  ```python
  # backend/linguistic/query_rewriter.py
  import ollama
  from config import OLLAMA_MODEL

  REWRITE_SYSTEM_PROMPT = """You are a query rewriting assistant for an academic institution chatbot.
  Given a conversational history and a follow-up query, rewrite the follow-up into a complete,
  standalone search query that includes all necessary context.
  Output ONLY the rewritten query. No explanation. No extra text."""

  def rewrite_query(query: str, history: list[dict]) -> str:
      """
      Resolve pronouns and follow-up references using conversation history.
      Example: 'When is its last date?' → 'When is the submission deadline for the 2026 scholarship?'
      If history is empty or query is already standalone, return query unchanged.
      """
      if not history:
          return query

      history_text = "\n".join([
          f"{'User' if m['role']=='user' else 'Bot'}: {m['content']}"
          for m in history[-4:]   # Last 2 turns
      ])

      prompt = f"""Conversation history:
  {history_text}

  Follow-up query: {query}

  Rewrite the follow-up query as a complete standalone question:"""

      response = ollama.chat(
          model=OLLAMA_MODEL,
          messages=[
              {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
              {"role": "user", "content": prompt}
          ]
      )
      return response["message"]["content"].strip()
  ```

#### 🧪 Test & Verify — Milestone 4
```powershell
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
# Test 1: Language detection
python -c "from linguistic.detector import detect_language; print(detect_language('scholarship form kab milegi')); print(detect_language('when is the fee deadline'))"
# Expected: hi, en
# Test 2: Hinglish normalizer
python -c "from linguistic.normalizer import normalize_query; print(normalize_query('fees kab bharna hai submission', 'hi'))"
# Expected: should contain 'fee payment schedule'
# Test 3: Query rewriter (needs Ollama running)
python -c "from linguistic.query_rewriter import rewrite_query; history=[{'role':'user','content':'Tell me about the scholarship form'},{'role':'assistant','content':'The scholarship form is available...'}]; print(rewrite_query('When is its last date?', history))"
# Expected: a complete standalone question mentioning scholarship
```
> Test 1 language codes must be correct. Test 3 must produce a coherent standalone question.

#### 📦 Git Commit & Push — Milestone 4
```powershell
cd C:\Users\ynj02\Desktop\minor
git add backend/linguistic/
git commit -m "feat(linguistic): language detection, Hinglish normalizer, and query rewriter

- detector.py: lingua-py based English/Hindi classification
- normalizer.py: two-step Hinglish pipeline — phonetic transliteration + intent mapping
- query_rewriter.py: Mistral 7B contextual rewriter resolving multi-turn follow-ups"
git push origin main
```

---

### ✅ Milestone 5: Layer 4 — LangGraph Self-Corrective Engine

**Goal:** Build the 5-node LangGraph state machine. This is the core of the system.

**Key files to create:**
- `backend/agent/state.py`
- `backend/agent/nodes.py`
- `backend/agent/edges.py`
- `backend/agent/graph.py`

- [ ] **5.1** Define `backend/agent/state.py` — AgentState TypedDict.
  ```python
  # backend/agent/state.py
  from typing import TypedDict, List, Dict, Any, Optional

  class AgentState(TypedDict):
      # Input
      original_query: str
      normalized_query: str
      detected_language: str             # 'en' or 'hi'
      conversation_history: List[Dict[str, str]]

      # Processing
      rewritten_query: str
      retrieved_chunks: List[Dict[str, Any]]
      relevance_score: float
      retry_count: int                   # Max: MAX_RETRY_COUNT (2)
      used_live_scraper: bool            # Track if scraper was already tried

      # Output
      draft_response: str
      citations: List[Dict[str, Any]]
      is_grounded: bool
      escalated: bool
      final_response: str
  ```

- [ ] **5.2** Implement `backend/agent/nodes.py` — all 5 LangGraph nodes.
  ```python
  # backend/agent/nodes.py
  import ollama
  from config import OLLAMA_MODEL, RELEVANCE_THRESHOLD, MAX_RETRY_COUNT
  from retrieval.embedder import dense_search
  from retrieval.sparse_search import sparse_search
  from retrieval.rrf_fusion import reciprocal_rank_fusion
  from retrieval.reranker import rerank
  from linguistic.query_rewriter import rewrite_query
  from ingestion.web_crawler import scrape_notices
  from ingestion.chunker import chunk_text

  # ── NODE 1: Document Relevance Grader ─────────────────────────────────────────
  def relevance_grader_node(state: dict) -> dict:
      """Check if retrieved chunks score >= 0.70 relevance."""
      chunks = state.get("retrieved_chunks", [])
      if not chunks:
          return {**state, "relevance_score": 0.0}
      # Use top chunk's reranker score as relevance proxy
      top_score = chunks[0].get("rrf_score", 0.0)
      return {**state, "relevance_score": top_score}

  # ── NODE 2: Query Reformulation + Fallback ────────────────────────────────────
  def reformulation_node(state: dict) -> dict:
      """Reformulate query and re-retrieve. Try live scraper if 2nd attempt also fails."""
      retry = state.get("retry_count", 0) + 1
      query = state["rewritten_query"]

      # Reformulate
      reformulated = rewrite_query(query + " (search for related terms)", state["conversation_history"])

      # Re-retrieve from ChromaDB
      dense = dense_search(reformulated)
      sparse = sparse_search(reformulated)
      fused = reciprocal_rank_fusion(dense, sparse)
      reranked = rerank(reformulated, fused)

      # If still poor AND scraper not tried yet → try live scraper
      used_scraper = state.get("used_live_scraper", False)
      if not reranked and not used_scraper:
          # TODO: chunk scraper results and add to retrieval candidates
          used_scraper = True

      return {
          **state,
          "rewritten_query": reformulated,
          "retrieved_chunks": reranked,
          "retry_count": retry,
          "used_live_scraper": used_scraper
      }

  # ── NODE 3: Grounded Generation Engine (Mistral 7B) ──────────────────────────
  def grounded_generator_node(state: dict) -> dict:
      """Generate answer strictly from verified top-3 passages using Mistral 7B."""
      chunks = state["retrieved_chunks"]
      context = "\n\n".join([
          f"[Source: {c['metadata'].get('source','?')}, Page: {c['metadata'].get('page_num','?')}]\n{c['text']}"
          for c in chunks
      ])
      citations = [
          {"source": c["metadata"].get("source"), "page": c["metadata"].get("page_num"),
           "circular_number": c["metadata"].get("circular_number", ""),
           "date": c["metadata"].get("date", "")}
          for c in chunks
      ]

      system_prompt = """You are a precise academic institution assistant.
  Answer ONLY using the provided context passages. 
  Do not speculate, extrapolate, or add any information not present in the context.
  Every factual claim must include a citation in format [Source: filename, Page: X].
  If the context is insufficient, say: "I could not find this information in the available notices." """

      user_prompt = f"""Context passages:
  {context}

  Student question: {state['rewritten_query']}

  Answer in the same language as the question ({state['detected_language']}):"""

      response = ollama.chat(
          model=OLLAMA_MODEL,
          messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt}
          ]
      )
      return {**state, "draft_response": response["message"]["content"], "citations": citations}

  # ── NODE 4: Hallucination & Factuality Grader ─────────────────────────────────
  def hallucination_grader_node(state: dict) -> dict:
      """Verify draft contains no claims unsupported by source chunks."""
      draft = state["draft_response"]
      context = " ".join([c["text"] for c in state["retrieved_chunks"]])

      grader_prompt = f"""Given the context and draft response, answer with only YES or NO.
  Does every factual claim in the draft response have direct support in the context?

  Context: {context[:3000]}

  Draft response: {draft}

  Answer (YES/NO only):"""

      response = ollama.chat(
          model=OLLAMA_MODEL,
          messages=[{"role": "user", "content": grader_prompt}]
      )
      is_grounded = "yes" in response["message"]["content"].lower()
      return {**state, "is_grounded": is_grounded}

  # ── NODE 5: Language Consistency Validator ────────────────────────────────────
  def language_validator_node(state: dict) -> dict:
      """Ensure response language matches student's detected language."""
      draft = state["draft_response"]
      target_lang = state["detected_language"]

      if target_lang == "en":
          return {**state, "final_response": draft}

      # For Hindi: translate draft while preserving citations
      translate_prompt = f"""Translate the following response to Hindi.
  Preserve all citation tags in format [Source: ..., Page: ...] exactly as they appear.
  Output only the translated text, no explanation.

  Text to translate:
  {draft}"""

      response = ollama.chat(
          model=OLLAMA_MODEL,
          messages=[{"role": "user", "content": translate_prompt}]
      )
      return {**state, "final_response": response["message"]["content"]}
  ```

- [ ] **5.3** Implement `backend/agent/edges.py` — conditional routing logic.
  ```python
  # backend/agent/edges.py
  from config import RELEVANCE_THRESHOLD, MAX_RETRY_COUNT

  def route_after_grader(state: dict) -> str:
      """After Node 1: route to generate or reformulate."""
      if state["relevance_score"] >= RELEVANCE_THRESHOLD:
          return "generate"
      if state.get("retry_count", 0) >= MAX_RETRY_COUNT:
          return "escalate"
      return "reformulate"

  def route_after_hallucination_check(state: dict) -> str:
      """After Node 4: if grounded → validate language, else → regenerate."""
      if state.get("is_grounded", False):
          return "validate_language"
      if state.get("retry_count", 0) >= MAX_RETRY_COUNT:
          return "validate_language"   # Accept after max retries to avoid infinite loop
      return "regenerate"
  ```

- [ ] **5.4** Implement `backend/agent/graph.py` — compiled LangGraph workflow.
  ```python
  # backend/agent/graph.py
  from langgraph.graph import StateGraph, END
  from agent.state import AgentState
  from agent.nodes import (
      relevance_grader_node, reformulation_node, grounded_generator_node,
      hallucination_grader_node, language_validator_node
  )
  from agent.edges import route_after_grader, route_after_hallucination_check
  from retrieval.embedder import dense_search
  from retrieval.sparse_search import sparse_search
  from retrieval.rrf_fusion import reciprocal_rank_fusion
  from retrieval.reranker import rerank
  from linguistic.detector import detect_language
  from linguistic.normalizer import normalize_query
  from linguistic.query_rewriter import rewrite_query

  def linguistic_preprocessing_node(state: dict) -> dict:
      """Layer 3: runs first — detect language, normalize, rewrite."""
      lang = detect_language(state["original_query"])
      normalized = normalize_query(state["original_query"], lang)
      rewritten = rewrite_query(normalized, state.get("conversation_history", []))
      return {**state, "detected_language": lang, "normalized_query": normalized, "rewritten_query": rewritten}

  def hybrid_retrieval_node(state: dict) -> dict:
      """Layer 2: dense + sparse retrieval → RRF → rerank."""
      query = state["rewritten_query"]
      dense = dense_search(query)
      sparse = sparse_search(query)
      fused = reciprocal_rank_fusion(dense, sparse)
      reranked = rerank(query, fused)
      return {**state, "retrieved_chunks": reranked, "retry_count": 0}

  def escalation_node(state: dict) -> dict:
      """Halt generation, log to SQLite, return office contact."""
      from db.database import log_escalation
      log_escalation(state)
      escalation_message = (
          "I was unable to find reliable information for your query in the available notices. "
          "Please contact the administrative office directly:\n"
          "📍 Room 101, Admin Block | 🕐 9 AM – 5 PM (Mon–Fri) | 📧 admin@mait.ac.in"
      )
      return {**state, "final_response": escalation_message, "escalated": True}

  # ── Build the Graph ────────────────────────────────────────────────────────────
  workflow = StateGraph(AgentState)

  workflow.add_node("linguistic_preprocess", linguistic_preprocessing_node)
  workflow.add_node("hybrid_retrieval", hybrid_retrieval_node)
  workflow.add_node("relevance_grader", relevance_grader_node)
  workflow.add_node("reformulation", reformulation_node)
  workflow.add_node("generator", grounded_generator_node)
  workflow.add_node("hallucination_grader", hallucination_grader_node)
  workflow.add_node("language_validator", language_validator_node)
  workflow.add_node("escalation", escalation_node)

  workflow.set_entry_point("linguistic_preprocess")
  workflow.add_edge("linguistic_preprocess", "hybrid_retrieval")
  workflow.add_edge("hybrid_retrieval", "relevance_grader")

  workflow.add_conditional_edges("relevance_grader", route_after_grader, {
      "generate": "generator",
      "reformulate": "reformulation",
      "escalate": "escalation"
  })
  workflow.add_edge("reformulation", "relevance_grader")
  workflow.add_edge("generator", "hallucination_grader")
  workflow.add_conditional_edges("hallucination_grader", route_after_hallucination_check, {
      "validate_language": "language_validator",
      "regenerate": "generator"
  })
  workflow.add_edge("language_validator", END)
  workflow.add_edge("escalation", END)

  chatbot_agent = workflow.compile()
  ```

#### 🧪 Test & Verify — Milestone 5
```powershell
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
# Test 1: Full end-to-end agent run — English query
python -c "
from agent.graph import chatbot_agent
result = chatbot_agent.invoke({
    'original_query': 'What is the last date for scholarship form submission?',
    'conversation_history': [],
    'retry_count': 0,
    'used_live_scraper': False,
    'escalated': False
})
print('Language:', result['detected_language'])
print('Response:', result['final_response'][:300])
print('Citations:', result['citations'])
"
# Test 2: Hindi query — language validator must respond in Hindi
python -c "
from agent.graph import chatbot_agent
result = chatbot_agent.invoke({
    'original_query': 'scholarship form ki last date kya hai',
    'conversation_history': [],
    'retry_count': 0,
    'used_live_scraper': False,
    'escalated': False
})
print('Detected lang:', result['detected_language'])
print('Escalated:', result.get('escalated', False))
print('Response preview:', result['final_response'][:200])
"
# Test 3: Unanswerable query — must escalate
python -c "
from agent.graph import chatbot_agent
result = chatbot_agent.invoke({
    'original_query': 'xyzabcunknownquery123',
    'conversation_history': [],
    'retry_count': 0,
    'used_live_scraper': False,
    'escalated': False
})
print('Escalated:', result.get('escalated'))   # Must be True
"
```
> Test 1 must return a grounded response with citations. Test 2 response must not be in pure English. Test 3 MUST show escalated=True.

#### 📦 Git Commit & Push — Milestone 5
```powershell
cd C:\Users\ynj02\Desktop\minor
git add backend/agent/
git commit -m "feat(agent): 5-node LangGraph self-corrective decision engine

- state.py: AgentState TypedDict with all pipeline fields
- nodes.py: Node1 relevance grader, Node2 reformulation+fallback,
  Node3 Mistral 7B grounded generation, Node4 hallucination grader,
  Node5 language consistency validator + escalation handler
- edges.py: conditional routing with retry count bounds
- graph.py: compiled LangGraph StateGraph with linguistic pre-processing
  and hybrid retrieval integrated as entry nodes"
git push origin main
```

---

### ✅ Milestone 6: SQLite Database Layer

**Goal:** Log every query, response, and escalation. Enables RAGAS eval data collection.

**Key files to create:** `backend/db/models.py`, `backend/db/database.py`

- [ ] **6.1** Implement `backend/db/models.py` — SQL schema.
  ```sql
  -- query_logs: every interaction
  CREATE TABLE IF NOT EXISTS query_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      user_query TEXT NOT NULL,
      detected_language TEXT,
      rewritten_query TEXT,
      retrieved_sources TEXT,   -- JSON array of source filenames
      relevance_score REAL,
      generated_response TEXT,
      is_grounded INTEGER,      -- 1 = grounded, 0 = failed grounding
      ocr_method TEXT,          -- Which OCR path was used
      latency_ms REAL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  -- escalation_tickets: unresolved queries
  CREATE TABLE IF NOT EXISTS escalation_tickets (
      ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      unresolved_query TEXT NOT NULL,
      detected_language TEXT,
      failure_reason TEXT,
      status TEXT DEFAULT 'PENDING_STAFF_REVIEW',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  ```

- [ ] **6.2** Implement `backend/db/database.py` — SQLAlchemy connection + helpers.

- [ ] **6.3** Wire up logging into `graph.py` — log every query after `language_validator` node.

- [ ] **6.4** Verify by querying SQLite after 3 test runs: `sqlite3 data/chatbot_audit.db "SELECT * FROM query_logs;"`

#### 🧪 Test & Verify — Milestone 6
```powershell
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
python -c "from db.database import init_db, log_query, log_escalation; init_db(); print('DB initialized OK')"
python -c "import sqlite3; conn=sqlite3.connect('../data/chatbot_audit.db'); tables=conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall(); print('Tables:', tables)"
# Expected: [('query_logs',), ('escalation_tickets',)]
```

#### 📦 Git Commit & Push — Milestone 6
```powershell
cd C:\Users\ynj02\Desktop\minor
git add backend/db/
git commit -m "feat(db): SQLite schema and SQLAlchemy helpers for audit logging

- models.py: query_logs and escalation_tickets table definitions
- database.py: init_db, log_query, log_escalation CRUD functions"
git push origin main
```

---

### ✅ Milestone 7: Flask REST API

**Goal:** Expose the LangGraph agent and SQLite logging via a clean REST API.

**Key file to create:** `backend/app.py`

- [ ] **7.1** Implement `backend/app.py` with all 4 endpoints:
  - `POST /api/chat` — invoke LangGraph agent, return response + citations
  - `GET /api/health` — verify Ollama running + ChromaDB loaded
  - `GET /api/unresolved` — return escalation tickets for staff
  - `POST /api/feedback` — accept thumbs up/down from student

- [ ] **7.2** Enable CORS for `http://localhost:5173`.

- [ ] **7.3** Add error handling and latency measurement to all routes.

- [ ] **7.4** Test with curl:
  ```powershell
  curl -X POST http://localhost:5000/api/chat `
    -H "Content-Type: application/json" `
    -d '{"query": "What is the last date for scholarship form submission?", "session_id": "test-001", "history": []}'
  ```

#### 🧪 Test & Verify — Milestone 7
```powershell
# Terminal 1: Start Ollama + Flask
ollama serve
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
python app.py

# Terminal 2: Test endpoints
Invoke-WebRequest -Uri http://localhost:5000/api/health -Method GET | Select-Object -ExpandProperty Content
Invoke-WebRequest -Uri http://localhost:5000/api/chat -Method POST -ContentType "application/json" -Body '{"query":"What is the fee deadline?","session_id":"test-001","history":[]}' | Select-Object -ExpandProperty Content
Invoke-WebRequest -Uri http://localhost:5000/api/unresolved -Method GET | Select-Object -ExpandProperty Content
```
> `/api/health` must return `{"status":"ok"}`. `/api/chat` must return a JSON response with `response` and `citations` keys.

#### 📦 Git Commit & Push — Milestone 7
```powershell
cd C:\Users\ynj02\Desktop\minor
git add backend/app.py
git commit -m "feat(api): Flask REST API with 4 endpoints

- POST /api/chat: invokes LangGraph agent, returns response + citations + escalation flag
- GET /api/health: verifies Ollama and ChromaDB are ready
- GET /api/unresolved: returns pending escalation tickets for staff
- POST /api/feedback: stores student thumbs-up/down rating in SQLite"
git push origin main
```

---

### ✅ Milestone 8: ReactJS Frontend

**Goal:** Build the chat UI with citation cards. No voice input.

**Key components to create:**
- `ChatWindow.jsx`, `MessageBubble.jsx`, `CitationCard.jsx`, `LanguageBadge.jsx`, `EscalationCard.jsx`
- `services/api.js`

- [ ] **8.1** Implement `services/api.js` — Axios client for Flask API.

- [ ] **8.2** Implement `ChatWindow.jsx` — message feed with auto-scroll, language badge, input box.

- [ ] **8.3** Implement `CitationCard.jsx` — clickable source card showing circular name, date, page.

- [ ] **8.4** Implement `EscalationCard.jsx` — rendered when backend returns `escalated: true`.

- [ ] **8.5** Implement `LanguageBadge.jsx` — small badge showing detected language (EN / HI / Hinglish).

- [ ] **8.6** Wire up `App.jsx` and verify end-to-end chat flow.
  ```powershell
  cd C:\Users\ynj02\Desktop\minor\frontend
  npm run dev
  ```

#### 🧪 Test & Verify — Milestone 8
```powershell
# Ensure backend is running (python app.py in Terminal 1)
cd C:\Users\ynj02\Desktop\minor\frontend
npm run dev
# Open http://localhost:5173 in browser and manually verify:
# 1. Type "What is the scholarship deadline?" → response appears with citation card
# 2. Type "fees kab bharna hai" → response appears (Hindi/Hinglish query)
# 3. Type "xyzunknown123" → escalation card appears with office contact
# 4. Check that CitationCard shows source filename and page number
# 5. Check that LanguageBadge shows correct detected language
```
> All 5 manual checks must pass before committing.

#### 📦 Git Commit & Push — Milestone 8
```powershell
cd C:\Users\ynj02\Desktop\minor
git add frontend/src/ frontend/package.json frontend/tailwind.config.js
git commit -m "feat(frontend): React chat UI with citation cards and escalation card

- ChatWindow.jsx: message feed with auto-scroll and language badge
- MessageBubble.jsx: formatted bot/user messages
- CitationCard.jsx: clickable source cards showing filename, date, page
- EscalationCard.jsx: admin contact card triggered on confidence fallback
- LanguageBadge.jsx: detected language indicator (EN/HI)
- api.js: Axios client for all Flask endpoints"
git push origin main
```

---

### ✅ Milestone 9: Evaluation & Benchmarking (IEEE Paper Data)

**Goal:** Produce the quantitative results tables for the paper.

- [ ] **9.1 OCR Benchmark dataset:** Collect 50 MAIT notice images with ground-truth transcriptions. Store in `data/eval/ocr_benchmark/`.

- [ ] **9.2 OCR Benchmark script:** Run PyMuPDF / Tesseract / Pixtral on each image, compute CER and WER. Output `results/ocr_comparison_table.csv`.
  ```powershell
  cd C:\Users\ynj02\Desktop\minor\backend
  python eval/benchmark_ocr.py
  ```

- [ ] **9.3 RAGAS evaluation dataset:** Create 200 Q&A pairs (English + Hindi/Hinglish) from real MAIT notices. Store in `data/eval/ragas_dataset.json`.

- [ ] **9.4 RAGAS evaluation script:** Run RAGAS metrics (faithfulness, context precision, answer relevance).
  ```powershell
  python eval/run_ragas.py
  ```

- [ ] **9.5 Deflection rate test:** Run 50 routine queries through the system and count bot-resolved vs. escalated.

- [ ] **9.6** Compile all results into `results/evaluation_summary.md` for the IEEE paper.

#### 🧪 Test & Verify — Milestone 9
```powershell
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
# Run OCR benchmark
python eval/benchmark_ocr.py
# Expected: results/ocr_comparison_table.csv created with CER/WER per method

# Run RAGAS evaluation
python eval/run_ragas.py
# Expected: results/ragas_scores.json created with faithfulness/precision/relevance

# Check output
python -c "import json; d=open('../results/ragas_scores.json').read(); print(json.loads(d))"
```
> Both scripts must complete without error and produce output CSV/JSON files in `results/`.

#### 📦 Git Commit & Push — Milestone 9
```powershell
cd C:\Users\ynj02\Desktop\minor
git add backend/eval/ results/
git commit -m "test(eval): RAGAS and OCR benchmark evaluation complete

- eval/benchmark_ocr.py: CER/WER comparison across PyMuPDF/Tesseract/Pixtral-12B
- eval/run_ragas.py: faithfulness, context precision, answer relevance evaluation
- results/ocr_comparison_table.csv: OCR benchmark results for IEEE paper Table III
- results/ragas_scores.json: RAGAS scores for IEEE paper Table IV"
git push origin main
```

---

## 4. How to Run the Complete Project

```powershell
# Step 1: Start Ollama (must be running before Flask)
ollama serve   # Runs on http://localhost:11434

# Step 2: Build the offline index (run once, then after new notices are added)
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
python run_ingestion.py

# Step 3: Start Flask API
python app.py
# → Runs at http://localhost:5000

# Step 4: Start React frontend (new terminal)
cd C:\Users\ynj02\Desktop\minor\frontend
npm run dev
# → Runs at http://localhost:5173
```

---

## 5. Quick Verification Commands

```powershell
# Check Ollama models available
ollama list

# Test Mistral 7B
ollama run mistral "What is RAG?"

# Check ChromaDB has data
cd C:\Users\ynj02\Desktop\minor\backend
.\venv\Scripts\activate
python -c "import chromadb; c=chromadb.PersistentClient('../data/processed/chromadb'); col=c.get_collection('mait_notices'); print('Chunks indexed:', col.count())"

# Check SQLite logs
python -c "import sqlite3; conn=sqlite3.connect('../data/chatbot_audit.db'); print(conn.execute('SELECT COUNT(*) FROM query_logs').fetchone())"

# Test Flask API
curl http://localhost:5000/api/health
```

---

## 🤝 HANDOFF

**Status:** Initial implementation guide written. No code implemented yet.

**What exists:**
- `project_implementation.md` — This file (fully updated per final architecture)
- `architecture/architecture_spec_UPDATED.md` — Full architecture spec
- `architecture/architecture_FINAL.jpg` — Visual diagram

**Architecture locked decisions:**
- Mistral 7B Instruct via Ollama for generation
- Pixtral-12B via Ollama for noisy image OCR
- Tesseract 5.x for clean scan OCR, PyMuPDF for digital PDFs
- ChromaDB (not FAISS), SQLite (not PostgreSQL)
- Languages: English + Hindi/Hinglish only
- Web scraper is offline batch only (not runtime)
- No voice input

**Next task for incoming AI session:**
Start at **Milestone 1: Environment Setup**. Read this file top to bottom first, then create the directory structure (task 1.1) and install all dependencies (task 1.2). After finishing Milestone 1, update the checkboxes and replace this HANDOFF block with a new one describing what was installed and any issues encountered.

**Key files to read first:**
- `C:\Users\ynj02\Desktop\minor\project_implementation.md` ← This file
- `C:\Users\ynj02\Desktop\minor\architecture\architecture_spec_UPDATED.md` ← Architecture reference
