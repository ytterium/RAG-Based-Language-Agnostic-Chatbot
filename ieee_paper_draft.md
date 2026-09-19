# An Agentic Self-Corrective RAG Framework with Adaptive OCR Routing for Multilingual Academic Query Resolution

**Yash Jain, Yash Mishra, Uday Khanna**
*Department of Computer Science and Engineering*
*Maharaja Agrasen Institute of Technology, New Delhi, India*
`{02596402723, 02396402723, 01096402723}@mait.ac.in`

*Project Guide: Ms. Prachi Gupta*

---

> **IEEE FORMAT NOTE:** This document is the manuscript source. In final submission, format as double-column IEEE using the official `IEEEtran.cls` LaTeX template (conference variant). Section numbering, citation style, and heading hierarchy follow IEEE guidelines throughout.

---

## Abstract

Campus administrative offices at academic institutions face persistent pressure from repetitive, time-sensitive student queries regarding scholarship deadlines, fee schedules, examination timetables, and eligibility criteria. Existing institutional chatbot deployments rely on naive Retrieval-Augmented Generation (RAG) pipelines that fail on three documented axes: inability to process scanned noticeboard images and image-based PDFs, exact-identifier retrieval failure on circular codes and form numbers, and cross-lingual language drift in multilingual conversational settings. This paper presents an agentic, self-corrective RAG framework that addresses all three failure modes simultaneously. The proposed system introduces an adaptive OCR routing strategy that dispatches document ingestion across PyMuPDF, Tesseract 5.x, and Pixtral-12B based on measurable image-quality metrics, enabling extraction from previously inaccessible scanned notices. A two-step Hinglish normalization pipeline applies phonetic transliteration and intent-keyword mapping to handle Romanized Hindi-English code-mixed queries. Dense retrieval via BGE-M3 is fused with BM25 sparse lexical search using Reciprocal Rank Fusion (RRF, k=60), followed by cross-encoder re-ranking to produce high-precision context passages. A five-node LangGraph decision graph orchestrates document relevance grading, query reformulation, grounded generation via Mistral 7B Instruct, factuality verification, and language consistency validation, with confident human escalation when information is unavailable. All models are open-weight and locally deployable, ensuring reproducibility. Quantitative evaluation using the RAGAS framework across a benchmark of 200 verified institutional question-answer pairs is described; results are reported separately upon system deployment.

**Index Terms** — Retrieval-Augmented Generation, Optical Character Recognition, Multilingual Information Retrieval, LangGraph, Hinglish Normalization, Institutional Chatbot, Self-Corrective AI, BGE-M3, Mistral, Dense-Sparse Hybrid Retrieval

---

## I. Introduction

Academic institutions routinely publish critical administrative information — scholarship application procedures, fee payment deadlines, examination schedules, and eligibility conditions — in formats that are structurally inaccessible to automated processing. A significant share of this information is disseminated as physical noticeboard postings that are photographed and circulated, scanned raster-image PDFs, and dynamically updated departmental web pages. Simultaneously, a substantial proportion of the student population is more fluent in Hindi or colloquial Romanized Hinglish than in formal English, creating a compounded barrier: the information is in English and locked in image formats that standard text pipelines cannot read.

Contemporary deployments of Retrieval-Augmented Generation (RAG) chatbots in educational settings [1] adopt a naive pipeline: ingest searchable PDFs, chunk text, embed into a vector store, and retrieve the top-k chunks as context for a language model. While this approach demonstrates viability for clean digital documents, it produces three well-documented failure modes in institutional deployments. First, as Lewis et al. [5] established in the original RAG formulation, the system offers no self-correction mechanism; irrelevant retrieved passages are blindly passed to the generator, which then produces hallucinated responses. Second, dense vector embeddings trained on semantic similarity consistently miss exact identifiers such as circular codes (e.g., "Notice Acad/2026/04"), form numbers, and specific numerical dates, as documented by Son et al. [3]. Third, Medina et al. [2] empirically measured a 27% cross-lingual language drift rate in prompt-only multilingual RAG systems, whereby the generator reverts to English even when the student's query was posed in Hindi or another regional language.

This paper presents a framework that addresses all three failure modes through four architectural contributions:

1. **Adaptive OCR Routing:** A quality-aware dispatcher that selects among PyMuPDF [6], Tesseract 5.x [7], and the Pixtral-12B vision language model [8] based on computed image sharpness, enabling extraction from scanned noticeboard photographs and image PDFs.

2. **Hinglish Normalization Pipeline:** A two-step module combining phonetic transliteration and intent-keyword mapping to handle Romanized Hindi-English code-mixed queries before retrieval.

3. **Hybrid Dense-Sparse Retrieval with RRF and Re-Ranking:** BGE-M3 [9] dense retrieval fused with BM25 [10] sparse lexical retrieval via Reciprocal Rank Fusion [11], followed by cross-encoder re-ranking.

4. **LangGraph Self-Corrective Decision Engine:** A five-node stateful graph [1] that grades document relevance, reformulates failed queries, generates grounded answers via Mistral 7B Instruct [12], verifies factuality, enforces language consistency [2], and escalates to human staff when necessary.

All components use open-weight models, making the system fully reproducible and locally deployable without proprietary API dependencies. The remainder of this paper is organized as follows: Section II reviews related work. Section III describes the system architecture in detail. Section IV presents the experimental setup. Section V reports results. Section VI discusses findings and limitations. Section VII concludes.

---

## II. Related Work

### A. RAG in Educational Settings

Swacha and Gracel [1] conducted a comprehensive survey of RAG chatbot applications in education, analyzing 47 deployments across university and K-12 contexts. They report that the dominant architectural pattern remains a single-pass retrieve-then-generate pipeline, and that fewer than 12% of surveyed systems incorporate any self-correction or grounding verification mechanism. The survey identifies hallucination on time-sensitive facts such as deadlines and fees as the primary trust failure, and calls for agentic verification loops as a research priority. Our work directly responds to this gap by introducing a LangGraph orchestrated self-corrective loop with explicit factuality grading.

### B. Cross-Lingual and Multilingual RAG

Medina et al. [2] introduced EduX-RAG, a cross-lingual RAG framework evaluated on English, Spanish, and Korean educational corpora. They document the language drift phenomenon quantitatively, measuring a 27% drift rate in zero-shot multilingual prompting, and propose language-locking through conversational state as a mitigation. Their evaluation does not address code-mixed Romanized regional languages, which present a distinct challenge because standard tokenizers fragment Romanized Hindi into semantically incoherent subword units. Our system extends their language-locking approach via Node 5 of the LangGraph pipeline, while additionally addressing the code-mixing problem through the dedicated Hinglish normalization module (Section III-B).

### C. Retrieval Quality and Hybrid Methods

Son et al. [3] evaluated a RAG-based electronic medical record chatbot and identified two critical retrieval failure modes: dense embeddings missing exact alphanumeric identifiers, and single-modality retrieval returning contextually irrelevant passages. They propose a hybrid dense-sparse approach and report improved retrieval precision on clinical identifier queries. We adopt their hybrid retrieval insight and extend it with Reciprocal Rank Fusion [11] and cross-encoder re-ranking, which Son et al. did not employ. The institutional notice domain shares the exact-identifier retrieval challenge (form codes, circular numbers) identified in their medical record context, making their findings directly applicable.

### D. Multilingual Conversational AI and Human Fallback

Sharanesha et al. [4] reviewed multilingual conversational AI systems in healthcare delivery and identified confidence-based human escalation as a critical safety mechanism. They observe that systems without escalation pathways either fabricate responses when information is unavailable or fail silently. Their systematic review of 34 deployments reports a 30–70% administrative workload deflection rate for systems with robust fallback mechanisms. Our system incorporates their recommendation directly: when retrieval confidence falls below the 0.70 threshold after two reformulation attempts and a live scraper pass, the system presents the physical office contact details, visiting hours, and email, and logs the unresolved query in SQLite for staff review.

### E. OCR in Document Processing

Smith [7] introduced Tesseract as an open-source OCR engine with strong performance on clean scanned documents. Its limitations on degraded images — low-resolution photographs, skewed text, stamped or handwritten annotations — are well-established. Agrawal et al. [8] introduced Pixtral-12B, a multimodal language model with demonstrated OCR capability on complex document images, including those with mixed fonts, stamps, and irregular layouts. No prior work has proposed an adaptive routing strategy that selects between classical OCR and vision language model OCR based on image quality metrics; this constitutes a novel contribution of the present paper.

---

## III. System Architecture

The proposed system is organized as a four-layer pipeline. **Layer 1** is an offline scheduled ingestion pipeline. **Layer 3** (Linguistic Pre-processing) executes first at query time, followed by **Layer 2** (Hybrid Retrieval), and finally **Layer 4** (LangGraph Decision Engine). This numbering follows the architectural specification; the runtime execution order is L3 → L2 → L4, with L1 operating asynchronously as a background batch job.

### A. Layer 1: Adaptive OCR and Multi-Modal Ingestion Pipeline

The ingestion pipeline processes two primary institutional data streams: a scheduled web scraper and a document ingestion engine. The web scraper, implemented with BeautifulSoup4, periodically monitors the institutional notice board portal and extracts headline announcements with publication timestamps. This component runs as a scheduled offline batch job and is never invoked at query time, ensuring that the runtime critical path remains bounded.

The document ingestion engine is the primary architectural contribution of this layer. Rather than applying a single OCR strategy to all inputs, the system dispatches each document through one of three extraction paths based on the document type and computed image quality (Fig. 1).

**Path A — PyMuPDF for Digital PDFs:** When the input is a PDF with an extractable text layer, PyMuPDF [6] is used for layout-aware text and table extraction. This path provides near-perfect fidelity for digitally authored circulars and incurs minimal computational cost.

**Path B — Tesseract 5.x for Clean Scanned Images:** When the input is a raster image or an image-only PDF, image sharpness is quantified using the Laplacian variance method. A sharpness score at or above the threshold *τ* (empirically set to 100.0 Laplacian variance units) indicates a clean scan suitable for classical OCR. The image undergoes OpenCV preprocessing — binarization via Otsu's method and deskewing — before being passed to Tesseract 5.x with English language data [7].

**Path C — Pixtral-12B for Noisy or Complex Images:** When the Laplacian variance falls below *τ*, indicating blur, noise, perspective distortion, stamps, or handwritten annotations, the image is routed to Pixtral-12B [8]. As a vision language model, Pixtral processes the image holistically without requiring preprocessing, yielding substantially higher accuracy on degraded institutional notice photographs. The model is run locally via Ollama, preserving data privacy by ensuring no institutional documents are transmitted to external servers.

Each extracted text block, regardless of its OCR path, is tagged with an `ocr_method` metadata field (`pymupdf`, `tesseract`, or `pixtral-12b`). This field is stored with each chunk and used during evaluation to benchmark extraction accuracy across paths (Section IV).

Following extraction, text is segmented using recursive semantic chunking with a 500-token window and a 100-token overlap. Each chunk is stored with structured metadata:

```
{
  "circular_number": "Acad/2026/04",
  "date":            "2026-09-10",
  "department":      "Academic Section",
  "page_num":        2,
  "source_url":      "https://mait.ac.in/...",
  "ocr_method":      "pixtral-12b"
}
```

This metadata enables verifiable, clickable citation cards in the frontend, allowing students to trace every factual claim to its source document and page.

All chunks are simultaneously indexed into two stores: a **ChromaDB** persistent vector index (via BGE-M3 embeddings) and a **BM25 lexical index** (via rank-bm25). Both indices are rebuilt on each scheduled ingestion run.

### B. Layer 3: Linguistic Pre-Processing and Query Routing

Layer 3 executes first on every incoming student query, before any retrieval operation. It comprises three sequential components: language detection, Hinglish normalization, and contextual query rewriting.

**Language Detection:** The lingua-py library identifies the query language as English (`en`) or Hindi/Hinglish (`hi`). The detected language is stored in the LangGraph `AgentState` and propagated through the entire pipeline. Node 5 (Section III-D) uses this value to enforce response language consistency.

**Hinglish Normalization Module:** Romanized Hindi-English code-mixing (Hinglish) presents a distinct retrieval challenge. Standard tokenizers split tokens such as "aakhri taarikh" or "fees kab bharna hai" into semantically incoherent subword units, destroying the retrieval signal. The proposed normalization pipeline applies two steps:

1. *Phonetic transliteration:* The indic-transliteration library maps Romanized Hindi tokens to their normalized Hindi equivalents, which BGE-M3's multilingual embedding space handles natively.
2. *Intent-keyword mapping:* A curated lexicon maps colloquial campus phrases to formal institutional terminology (e.g., "last date" → "submission deadline", "form kahan milega" → "where to obtain form").

This two-step approach ensures that BGE-M3's cross-lingual semantic space can map the normalized query directly to English notice passages without requiring a parallel translation corpus [2].

**Contextual Query Rewriter:** In multi-turn conversations, students frequently pose follow-up queries with unresolved pronoun references (e.g., "When is its last date?" following a question about a scholarship). The query rewriter uses Mistral 7B Instruct [12] with the last two conversational turns to rewrite ambiguous follow-up queries into complete, self-contained search queries. This prevents retrieval failure caused by underspecified inputs.

### C. Layer 2: Hybrid Retrieval Engine

Following linguistic pre-processing, the rewritten query is submitted to the hybrid retrieval engine, which operates over the offline-built ChromaDB and BM25 indices.

**Dense Retrieval — BGE-M3:** BGE-M3 [9] generates a 1024-dimensional embedding of the query in a shared multilingual semantic space. Because BGE-M3 was trained on multilingual corpora including Indic languages, it maps Hindi and Hinglish query representations directly to semantically equivalent English passage representations without translation. Dense retrieval returns the top-10 candidates by cosine similarity from ChromaDB.

**Sparse Retrieval — BM25:** BM25 Okapi [10] performs lexical retrieval over the tokenized text corpus. Unlike dense embeddings, BM25 assigns high scores to exact lexical matches, making it robust to queries containing specific circular codes (e.g., "Form 16-A"), numerical dates, and department identifiers that dense models tend to dilute through semantic generalization. BM25 retrieval returns the top-10 candidates by BM25 score.

**Reciprocal Rank Fusion:** The two ranked lists are merged using Reciprocal Rank Fusion (RRF) [11] with constant *k* = 60:

$$\text{RRF}(d) = \sum_{r \in \{r_{\text{dense}}, r_{\text{sparse}}\}} \frac{1}{k + \text{rank}_r(d)}$$

RRF produces a unified ranking that elevates documents that rank highly in both lists, combining semantic and lexical relevance signals without requiring score normalization across heterogeneous retrieval systems. The top 10 fused candidates proceed to re-ranking.

**Cross-Encoder Re-Ranking:** A BAAI/bge-reranker-v2-m3 cross-encoder scores each query-passage pair jointly, capturing fine-grained relevance signals that bi-encoder models cannot express. The top 3 passages by cross-encoder score are selected as the final context window for generation.

### D. Layer 4: LangGraph Self-Corrective Decision Engine

The retrieved passages enter a stateful LangGraph [1] workflow comprising five decision nodes. The workflow maintains an explicit `AgentState` object containing the original query, detected language, conversation history, retrieved chunks, relevance score, retry count, draft response, citation list, groundedness flag, and final response.

**Node 1 — Document Relevance Grader:** The grader evaluates whether the top-3 retrieved passages collectively contain the factual content required to answer the query. A relevance score is computed from the cross-encoder output; if this score exceeds the threshold *θ* = 0.70 and key query terms are present in the passages, the workflow proceeds to generation. If the score falls below *θ*, control passes to Node 2.

**Node 2 — Query Reformulation and Retrieval Fallback:** When initial retrieval is insufficient, Node 2 applies three sequential escalation strategies:
1. Reformulates the query by prompting Mistral 7B to generate alternative phrasings, then re-queries ChromaDB.
2. If the re-query still falls below threshold and the web scraper's batch output has not yet been queried as a supplementary source, the live ChromaDB index (which includes scraped notices from the most recent batch run) is queried with the reformulated query.
3. If information remains absent after a maximum of two reformulation attempts (configurable via `MAX_RETRY_COUNT`), the workflow routes to the escalation handler.

**Node 3 — Grounded Generation Engine:** Mistral 7B Instruct [12] generates a response strictly constrained to the verified top-3 passages. The system prompt explicitly prohibits speculation and instructs the model to attach structured citation tags to every factual assertion in the format `[Source: filename, Page: N]`. Mistral 7B is selected for its combination of strong instruction-following capability, open-weight Apache 2.0 licensing, and local deployability, ensuring the system is reproducible without proprietary API dependencies [12].

**Node 4 — Hallucination and Factuality Grader:** The generated draft is submitted to a factuality verification step. Mistral 7B is prompted to assess whether every factual claim in the draft has direct textual support in the source passages. If the verification returns a negative judgment and the retry count permits, the draft is rejected and Node 3 is invoked again with a lower generation temperature and tighter context constraints. This loop prevents fabricated deadlines, fees, or eligibility conditions from reaching the student.

**Node 5 — Language Consistency Validator:** The draft's output language is compared against the `detected_language` field in `AgentState`. If the draft is in English but the student queried in Hindi, Mistral 7B is prompted to translate the response while explicitly preserving all citation tags. This architectural enforcement directly resolves the 27% language drift failure documented by Medina et al. [2] by making language consistency a hard system constraint rather than a prompt-level instruction.

**Escalation Handler:** When the workflow determines that reliable information cannot be retrieved, generation halts. The system displays the administrative office's physical location, visiting hours, and contact email, and inserts the unresolved query, detected language, and failure reason into the SQLite `escalation_tickets` table. This creates an automated operational backlog for staff, surfacing which institutional notices are missing or inaccessible from the knowledge base [4].

The complete routing logic is formalized in Table I.

**TABLE I: LangGraph Routing Decision Rules**

| Decision Point | Condition | Action |
|---|---|---|
| Retrieval Assessment | Relevance score ≥ 0.70 and key terms present | Proceed to Node 3 (Generation) |
| Ambiguity / Context Gap | Relevance score < 0.70 on initial retrieval | Route to Node 2: reformulate + re-query ChromaDB |
| Second Retrieval Attempt | Reformulated query still below threshold | Node 2: query live scraper batch index |
| Max Retries Exceeded | Failure after `MAX_RETRY_COUNT` attempts | Route to Escalation Handler |
| Factuality Check | Generated facts lack direct grounding | Reject draft; re-invoke Node 3 with temperature ↓ |
| Language Verification | Draft language ≠ detected query language | Node 5: alignment pass preserving citation tags |

### E. Frontend and Infrastructure

The student-facing interface is a ReactJS application styled with Tailwind CSS. The chat window renders bot and user messages in separate bubbles; each bot message is accompanied by `CitationCard` components displaying the circular title, issuing department, publication date, and page number, with a link that opens the source PDF directly to the cited page. When the escalation handler triggers, an `EscalationCard` component renders the office contact details in place of a chatbot response.

The backend is a Python Flask REST API exposing four endpoints: `POST /api/chat` (invokes the LangGraph agent), `GET /api/health` (verifies Ollama and ChromaDB status), `GET /api/unresolved` (returns the escalation ticket backlog for administrative staff), and `POST /api/feedback` (records student rating of each response). All session history, query logs, retrieval scores, latency measurements, and escalation events are persisted in SQLite via SQLAlchemy.

The complete technology stack is summarized in Table II.

**TABLE II: System Technology Stack**

| System Layer | Component | Reference |
|---|---|---|
| Generation LLM | Mistral 7B Instruct (open weights, Apache 2.0) | Jiang et al. [12] |
| OCR — Digital PDF | PyMuPDF | [6] |
| OCR — Clean Scans | Tesseract 5.x + OpenCV | Smith [7] |
| OCR — Noisy Images | Pixtral-12B (open weights) | Agrawal et al. [8] |
| Dense Embedder | BGE-M3 (BAAI, open weights) | Chen et al. [9] |
| Sparse Search | BM25 Okapi (rank-bm25) | Robertson et al. [10] |
| Rank Fusion | Reciprocal Rank Fusion, k=60 | Cormack et al. [11] |
| Re-Ranker | BAAI/bge-reranker-v2-m3 | Chen et al. [9] |
| Orchestration | LangGraph + LangChain | [1] |
| Vector Store | ChromaDB (persistent) | — |
| Relational DB | SQLite + SQLAlchemy | — |
| Language Detection | lingua-py | — |
| Hinglish Normalization | indic-transliteration + custom lexicon | [2], [4] |
| Web Scraper | BeautifulSoup4 (offline batch) | — |
| Frontend | ReactJS + Tailwind CSS | — |
| Backend API | Python + Flask | — |
| Evaluation | RAGAS Framework | Es et al. [13] |

---

## IV. Experimental Setup

### A. Dataset Construction

The absence of a publicly available benchmark dataset for Indian institutional notice-board OCR and multilingual academic Q&A necessitates the construction of two purpose-built evaluation datasets.

**OCR Benchmark Dataset:** A collection of 50 institutional notice images is assembled from MAIT administrative records, spanning three categories: (i) digitally authored PDFs converted to images, (ii) clean scans of printed circulars, and (iii) photographs of physical noticeboard postings. Ground-truth transcriptions are prepared manually by two independent annotators; inter-annotator agreement is measured using Cohen's Kappa. All three OCR paths (PyMuPDF, Tesseract 5.x, Pixtral-12B) are applied to the entire dataset regardless of the routing decision, enabling controlled comparison.

**RAG Evaluation Dataset:** A set of 200 question-answer pairs is constructed from verified MAIT institutional documents. The dataset spans five query categories: (i) fee payment deadlines, (ii) scholarship application procedures, (iii) examination schedules, (iv) eligibility criteria, and (v) form submission locations. Fifty of the 200 pairs are posed in Hindi or Romanized Hinglish to evaluate cross-lingual retrieval and generation. Ground-truth answers are extracted directly from source documents by human annotators.

### B. Evaluation Metrics

**OCR Evaluation:**
- **Character Error Rate (CER):** The ratio of character-level edit distance to total characters in the ground-truth transcription. Lower is better.
- **Word Error Rate (WER):** The ratio of word-level edit distance to total words in the ground-truth transcription. Lower is better.

**RAG Evaluation (RAGAS Framework [13]):**
- **Faithfulness:** The fraction of claims in the generated answer that are directly supported by the retrieved context passages. Measures hallucination resistance.
- **Context Precision:** Whether the ground-truth relevant passages appear in the top-3 retrieved context. Measures retrieval quality.
- **Answer Relevance:** Semantic similarity between the generated answer and the ground-truth answer. Measures generation quality.

**Operational Metrics:**
- **Administrative Workload Deflection Rate:** The percentage of the 200 benchmark queries resolved by the bot without escalation to human staff. Target: ≥ 80% [4].
- **Language Consistency Rate:** The percentage of Hindi/Hinglish queries that receive a response in the correct target language. Target: ≥ 99% (versus the 73% baseline implied by the 27% drift rate in [2]).
- **End-to-End Latency:** Mean response time from query receipt to final response delivery, measured in milliseconds.

### C. Baselines

Three baseline systems are evaluated against the proposed framework:

1. **Naive RAG (Baseline 1):** Tesseract-only OCR, single FAISS dense index using BGE-M3, top-3 retrieval by cosine similarity, Mistral 7B generation with no verification. This represents the standard single-pass pipeline [1].
2. **Hybrid RAG without Self-Correction (Baseline 2):** Same adaptive OCR routing and BGE-M3 + BM25 + RRF retrieval, but generation via Mistral 7B without LangGraph verification nodes.
3. **Proposed System:** Full pipeline as described in Section III.

Comparison across these three baselines isolates the individual contributions of (a) adaptive OCR, (b) hybrid retrieval, and (c) the self-corrective LangGraph engine.

### D. Implementation Details

All models are run locally on a single machine using Ollama for LLM inference, ensuring no data is transmitted to external servers. BGE-M3 and the bge-reranker-v2-m3 cross-encoder are loaded via the sentence-transformers library. ChromaDB is configured with a persistent local storage path. The LangGraph workflow is compiled with a maximum retry count of 2 (`MAX_RETRY_COUNT = 2`) and a relevance threshold of 0.70 (`RELEVANCE_THRESHOLD = 0.70`). All hyperparameters are defined in a centralized `config.py` to facilitate reproducibility.

---

## V. Results and Discussion

*[TO BE COMPLETED AFTER SYSTEM DEPLOYMENT AND EVALUATION]*

*Planned tables:*
- *Table III: OCR Accuracy Comparison (CER and WER across PyMuPDF, Tesseract 5.x, Pixtral-12B, and Adaptive Router)*
- *Table IV: RAGAS Scores — Faithfulness, Context Precision, Answer Relevance (across three baselines)*
- *Table V: Language Consistency Rate and Administrative Workload Deflection Rate*
- *Table VI: Mean End-to-End Latency by Query Type*

---

## VI. Conclusion

This paper presents an agentic, self-corrective RAG framework for multilingual academic query resolution at institutional scale. The system makes four primary contributions over existing educational chatbot deployments [1]: (i) an adaptive OCR routing strategy that extends RAG to scanned institutional notices previously inaccessible to text-based pipelines, (ii) a two-step Hinglish normalization pipeline enabling retrieval over Romanized Hindi-English code-mixed queries, (iii) a hybrid BGE-M3 and BM25 retrieval architecture fused via RRF and re-ranked by a cross-encoder, and (iv) a five-node LangGraph self-corrective decision engine with grounded generation, factuality grading, and architectural language drift prevention.

The use of exclusively open-weight, locally deployable models — Mistral 7B Instruct [12], Pixtral-12B [8], and BGE-M3 [9] — ensures full reproducibility and institutional data privacy without dependence on proprietary APIs. Confident human escalation with SQL audit logging provides a governance layer aligned with institutional trust requirements [4].

Future work will extend language support to Marathi and Tamil, investigate fine-tuning BGE-M3 on domain-specific institutional terminology, explore voice input via speech-to-text integration for Hindi queries, and evaluate the system's generalizability across multiple Indian academic institutions beyond MAIT.

---

## References

[1] J. Swacha and M. Gracel, "Retrieval-Augmented Generation (RAG) Chatbots for Education: A Survey of Applications," *Applied Sciences*, vol. 15, no. 8, Art. no. 4234, Apr. 2025, doi: 10.3390/app15084234.

[2] J. Medina, S. Gyo-Jung, J. Salminen, K. K. Aldous, and B. J. Jansen, "EduX-RAG: Retrieval Augmented Generation Framework for Cross-Lingual Educational Chatbots," in *Proc. 3rd Int. Conf. Foundation and Large Language Models (FLLM)*, Dubai, UAE, Feb. 2025, pp. 465–473, doi: 10.1109/FLLM65463.2025.00078.

[3] N. Son, I. Kang, I. Kim, K. Lee, S. Nam, and D. Lee, "Development and Evaluation of a Retrieval-Augmented Generation-Based Electronic Medical Record Chatbot System," *Healthcare Informatics Research*, vol. 31, no. 3, pp. 218–225, Jul. 2025, doi: 10.4258/hir.2025.31.3.218.

[4] R. B. Sharanesha, D. Virupakshappa, A. Abushanan, and S. Alghamdi, "Multilingual Conversational AI Chatbots for Efficient Healthcare Delivery During Case History-Taking: A Systematic Review," *Informatics*, vol. 13, no. 8, Art. no. 129, Aug. 2026, doi: 10.3390/informatics13080129.

[5] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, 2020, pp. 9459–9474.

[6] Artifex Software, "MuPDF: A Lightweight PDF and XPS Viewer," 2024. [Online]. Available: https://mupdf.com

[7] R. Smith, "An Overview of the Tesseract OCR Engine," in *Proc. 9th Int. Conf. Document Analysis and Recognition (ICDAR)*, Curitiba, Brazil, Sep. 2007, pp. 629–633, doi: 10.1109/ICDAR.2007.4376991.

[8] A. Agrawal, B. Bojanowski, E. Gu, G. Lample, G. Parhar, G. Rozière, and the Mistral AI Team, "Pixtral 12B," *arXiv preprint*, arXiv:2410.07073, Oct. 2024. [Online]. Available: https://arxiv.org/abs/2410.07073

[9] J. Chen, S. Xiao, P. Zhang, K. Luo, D. Lian, and Z. Liu, "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation," *arXiv preprint*, arXiv:2309.07597, Sep. 2023. [Online]. Available: https://arxiv.org/abs/2309.07597

[10] S. Robertson and H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," *Foundations and Trends in Information Retrieval*, vol. 3, no. 4, pp. 333–389, 2009, doi: 10.1561/1500000019.

[11] G. V. Cormack, C. L. A. Clarke, and S. Buettcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," in *Proc. 32nd Int. ACM SIGIR Conf. Research and Development in Information Retrieval*, Boston, MA, USA, Jul. 2009, pp. 758–759, doi: 10.1145/1571941.1572114.

[12] A. Q. Jiang, A. Sablayrolles, A. Mensch, C. Bamford, D. S. Chaplot, D. de las Casas, F. Bressand, G. Lengyel, G. Lample, L. Saulnier, L. R. Lavaud, M.-A. Lachaux, P. Stock, T. L. Scao, T. Lavril, T. Wang, T. Lacroix, and W. E. Sayed, "Mistral 7B," *arXiv preprint*, arXiv:2310.06825, Oct. 2023. [Online]. Available: https://arxiv.org/abs/2310.06825

[13] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, "RAGAS: Automated Evaluation of Retrieval Augmented Generation," in *Proc. 18th Conf. European Chapter of the Association for Computational Linguistics (EACL): System Demonstrations*, Malta, Mar. 2024, pp. 150–158, doi: 10.18653/v1/2024.eacl-demo.16.
