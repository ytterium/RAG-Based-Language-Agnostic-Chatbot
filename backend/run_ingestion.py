"""
Offline Batch Ingestion CLI Entry Point.
Processes raw PDFs, scanned noticeboard images, and scraped notices.
Extracts text via the Adaptive OCR router, chunks text, extracts metadata,
and constructs both the persistent ChromaDB vector store and BM25 sparse index.

Usage:
    cd backend
    python run_ingestion.py
"""
import os
import pickle
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from config import (
        RAW_PDFS_DIR,
        RAW_IMAGES_DIR,
        BM25_STORE_PATH,
        CHROMA_COLLECTION_NAME,
        CHROMADB_PATH
    )
except ImportError:
    from backend.config import (
        RAW_PDFS_DIR,
        RAW_IMAGES_DIR,
        BM25_STORE_PATH,
        CHROMA_COLLECTION_NAME,
        CHROMADB_PATH
    )

from ingestion.ocr_router import route_and_extract
from ingestion.chunker import chunk_text
from ingestion.web_crawler import scrape_notices
from retrieval.embedder import build_chromadb_index
from retrieval.sparse_search import build_bm25_index


def run_ingestion():
    """
    Execute offline batch ingestion pipeline.
    """
    print("=" * 60)
    print("[START] ADAPTIVE OCR & INGESTION PIPELINE (LAYER 1)")
    print("=" * 60)

    all_chunks = []

    # 1. Process all digital & scanned PDFs
    if os.path.exists(RAW_PDFS_DIR):
        pdf_files = [f for f in os.listdir(RAW_PDFS_DIR) if f.lower().endswith(".pdf")]
        print(f"[INGESTION] Found {len(pdf_files)} PDF document(s) in {RAW_PDFS_DIR}")
        for fname in pdf_files:
            fpath = os.path.join(RAW_PDFS_DIR, fname)
            try:
                result = route_and_extract(fpath)
                if result.get("text", "").strip():
                    meta = {
                        "source": fname,
                        "date": "",
                        "department": "",
                        "circular_number": "",
                        "ocr_method": result.get("method", "pymupdf")
                    }
                    new_chunks = chunk_text(result["text"], meta)
                    all_chunks.extend(new_chunks)
                    print(f"[INGESTION] {fname} -> {result.get('method')} -> +{len(new_chunks)} chunks (Total: {len(all_chunks)})")
                else:
                    print(f"[INGESTION] Warning: No text extracted from {fname}")
            except Exception as e:
                print(f"[INGESTION] Error processing PDF {fname}: {e}")

    # 2. Process scanned noticeboard images
    if os.path.exists(RAW_IMAGES_DIR):
        valid_img_exts = (".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp")
        img_files = [f for f in os.listdir(RAW_IMAGES_DIR) if f.lower().endswith(valid_img_exts)]
        print(f"[INGESTION] Found {len(img_files)} noticeboard image(s) in {RAW_IMAGES_DIR}")
        for fname in img_files:
            fpath = os.path.join(RAW_IMAGES_DIR, fname)
            try:
                result = route_and_extract(fpath)
                if result.get("text", "").strip():
                    meta = {
                        "source": fname,
                        "date": "",
                        "department": "",
                        "circular_number": "",
                        "ocr_method": result.get("method", "tesseract")
                    }
                    new_chunks = chunk_text(result["text"], meta)
                    all_chunks.extend(new_chunks)
                    print(f"[INGESTION] {fname} -> {result.get('method')} -> +{len(new_chunks)} chunks (Total: {len(all_chunks)})")
                else:
                    print(f"[INGESTION] Warning: No text extracted from {fname}")
            except Exception as e:
                print(f"[INGESTION] Error processing image {fname}: {e}")

    # 3. Scrape institutional notice boards (offline scheduled batch)
    try:
        print("[INGESTION] Fetching notice board announcements...")
        web_notices = scrape_notices()
        print(f"[INGESTION] Scraped/cached {len(web_notices)} web notice(s)")
        for notice in web_notices:
            if notice.get("text", "").strip():
                new_chunks = chunk_text(notice["text"], notice.get("metadata", {}))
                all_chunks.extend(new_chunks)
    except Exception as e:
        print(f"[INGESTION] Notice board scraping encountered an issue: {e}")

    print(f"\n[INGESTION] Total chunks: {len(all_chunks)}")

    if not all_chunks:
        print("[INGESTION] No documents to index. Please add files to data/raw/pdfs/ or data/raw/scanned_images/")
        return

    # 4. Build ChromaDB dense vector index
    print("\n[INGESTION] Generating BGE-M3 embeddings and updating ChromaDB...")
    build_chromadb_index(all_chunks)
    print("[INGESTION] ChromaDB index built.")

    # 5. Build and serialize BM25 lexical sparse index
    print("[INGESTION] Building BM25 lexical index...")
    bm25 = build_bm25_index(all_chunks)
    os.makedirs(os.path.dirname(BM25_STORE_PATH), exist_ok=True)
    with open(BM25_STORE_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": all_chunks}, f)
    print(f"[INGESTION] BM25 index saved to {BM25_STORE_PATH}")
    print("=" * 60)
    print("[SUCCESS] INGESTION PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_ingestion()
