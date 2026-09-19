"""
Adaptive OCR Router and Ingestion Dispatcher.
Implements the 3-path quality-aware selection:
- Path A: PyMuPDF for digital searchable PDFs (layout-aware text + table extraction)
- Path B: Tesseract 5.x for clean scanned images/PDFs (Laplacian sharpness >= threshold)
- Path C: Pixtral-12B vision LLM for noisy, skewed, or degraded notices (sharpness < threshold)
"""
import os
from typing import Dict, Any
import cv2
import fitz
import numpy as np

try:
    from config import OCR_SHARPNESS_THRESHOLD
    from ingestion.pdf_parser import extract_text_from_pdf
    from ingestion.tesseract_ocr import run_tesseract, compute_sharpness, load_image
    from ingestion.pixtral_ocr import run_pixtral_ocr
except ImportError:
    from backend.config import OCR_SHARPNESS_THRESHOLD
    from backend.ingestion.pdf_parser import extract_text_from_pdf
    from backend.ingestion.tesseract_ocr import run_tesseract, compute_sharpness, load_image
    from backend.ingestion.pixtral_ocr import run_pixtral_ocr


def route_and_extract(file_path: str) -> Dict[str, Any]:
    """
    Adaptive OCR router. Inspects input file format and image degradation metrics,
    dispatching to the optimal extraction backend.

    Args:
        file_path: Absolute or relative path to the input document or image.

    Returns:
        Dict with:
            - "text": str (extracted text)
            - "method": str ("pymupdf", "tesseract", "pixtral-12b", or compound for scanned pdfs)
            - "source": str (original file path)
            - "sharpness": float (Laplacian variance if computed, else None)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found for extraction: {file_path}")

    ext = file_path.lower().split(".")[-1]

    # PATH A: Digital Searchable PDF (or raster PDF fallback)
    if ext == "pdf":
        pages = extract_text_from_pdf(file_path)
        if any(p.get("is_searchable", False) for p in pages):
            full_text = "\n\n".join(p["text"] for p in pages if p["text"].strip())
            return {
                "text": full_text,
                "method": "pymupdf",
                "source": file_path,
                "sharpness": None
            }

        # PDF has no text layer: render pages to high-resolution images and run image OCR
        rendered_texts = []
        methods_used = set()
        with fitz.open(file_path) as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                if pix.n == 4:
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_RGBA2BGR)
                elif pix.n == 3:
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
                elif pix.n == 1:
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_GRAY2BGR)

                sharpness = compute_sharpness(img_data)
                if sharpness >= OCR_SHARPNESS_THRESHOLD:
                    page_text = run_tesseract(img_data)
                    methods_used.add("tesseract")
                else:
                    page_text = run_pixtral_ocr(img_data)
                    methods_used.add("pixtral-12b")

                if page_text.strip():
                    rendered_texts.append(page_text.strip())

        full_text = "\n\n".join(rendered_texts).strip()
        method_desc = "+".join(sorted(methods_used)) if methods_used else "pymupdf_empty"
        return {
            "text": full_text,
            "method": f"pdf_ocr_{method_desc}",
            "source": file_path,
            "sharpness": None
        }

    # PATH B or C: Image Notice
    elif ext in ("jpg", "jpeg", "png", "tiff", "bmp", "webp"):
        img = load_image(file_path)
        sharpness = compute_sharpness(img)

        if sharpness >= OCR_SHARPNESS_THRESHOLD:
            # PATH B: Clean scan -> Fast local Tesseract OCR
            text = run_tesseract(img)
            return {
                "text": text,
                "method": "tesseract",
                "source": file_path,
                "sharpness": round(sharpness, 2)
            }
        else:
            # PATH C: Noisy / degraded / complex image -> Pixtral-12B Vision LLM
            text = run_pixtral_ocr(img)
            return {
                "text": text,
                "method": "pixtral-12b",
                "source": file_path,
                "sharpness": round(sharpness, 2)
            }

    else:
        raise ValueError(f"Unsupported file format: .{ext} for file {file_path}")
