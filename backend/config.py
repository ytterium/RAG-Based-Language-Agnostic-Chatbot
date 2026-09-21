"""
System configuration and constants for the RAG-Based Language Agnostic Chatbot.
"""
import os

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
RAW_PDFS_DIR = os.path.join(DATA_DIR, 'raw', 'pdfs')
RAW_IMAGES_DIR = os.path.join(DATA_DIR, 'raw', 'scanned_images')
RAW_SCRAPED_DIR = os.path.join(DATA_DIR, 'raw', 'scraped')
CHROMADB_PATH = os.path.join(DATA_DIR, 'processed', 'chromadb')
BM25_STORE_PATH = os.path.join(DATA_DIR, 'processed', 'bm25_store.pkl')
OCR_CACHE_DIR = os.path.join(DATA_DIR, 'processed', 'ocr_cache')
SQLITE_DB_PATH = os.path.join(DATA_DIR, 'chatbot_audit.db')

# OCR Configuration
TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
OCR_SHARPNESS_THRESHOLD = 100.0   # Laplacian variance threshold: below = use Pixtral

# Retrieval Configuration
CHROMA_COLLECTION_NAME = "mait_notices"
BGE_M3_MODEL = "BAAI/bge-m3"
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"
RRF_K = 60
TOP_K_FUSED = 10
TOP_K_FINAL = 3
RELEVANCE_THRESHOLD = 0.70

# LLM Configuration
# Defaults to mistrallite for local testing; can be overridden by env var OLLAMA_MODEL=mistral
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistrallite")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "pixtral")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# WHAT: Unified Ollama CPU runtime execution options.
# WHY: Ensures all nodes (rewriter, generator, grader, validator) share identical context size (2048)
#      and thread count (6). Eliminates the 105s model reload penalty triggered when Ollama switches runners,
#      and keeps KV cache within 256MB for optimal CPU cache locality.
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))
OLLAMA_NUM_THREAD = int(os.getenv("OLLAMA_NUM_THREAD", "6"))

# Chunking Configuration
CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 100

# Agent Configuration
MAX_RETRY_COUNT = 2
