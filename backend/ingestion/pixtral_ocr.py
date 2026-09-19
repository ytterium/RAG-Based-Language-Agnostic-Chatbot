"""
Pixtral-12B vision OCR module for noisy, degraded, or complex institutional notice images.
Communicates with Ollama's multimodal API with an automated Tesseract fallback.
"""
import base64
import os
from typing import Union
import cv2
import numpy as np
import ollama

try:
    from config import OLLAMA_VISION_MODEL, OLLAMA_BASE_URL
except ImportError:
    from backend.config import OLLAMA_VISION_MODEL, OLLAMA_BASE_URL


def image_to_base64(image_input: Union[str, np.ndarray]) -> str:
    """
    Convert an image file path or numpy ndarray to a base64 encoded string.
    """
    if isinstance(image_input, str):
        if not os.path.exists(image_input):
            raise FileNotFoundError(f"Image not found at: {image_input}")
        with open(image_input, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    elif isinstance(image_input, np.ndarray):
        success, encoded_img = cv2.imencode(".png", image_input)
        if not success:
            raise ValueError("Failed to encode image array to PNG format.")
        return base64.b64encode(encoded_img.tobytes()).decode("utf-8")
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")


def run_pixtral_ocr(image_input: Union[str, np.ndarray]) -> str:
    """
    Use Pixtral-12B (via Ollama) to extract verbatim text from noisy or complex notice images.
    Preserves circular IDs, dates, tabular numbers, and administrative signatures.
    If Pixtral is unavailable or encounters an error, falls back to Tesseract OCR.

    Args:
        image_input: File path or numpy ndarray.

    Returns:
        Extracted text string.
    """
    try:
        img_b64 = image_to_base64(image_input)
        client = ollama.Client(host=OLLAMA_BASE_URL)

        prompt = (
            "You are an OCR assistant. Extract ALL text visible in this institutional "
            "notice image exactly as it appears. Preserve dates, form numbers, circular "
            "IDs, and amounts. Do not summarize. Output only the extracted text."
        )

        response = client.chat(
            model=OLLAMA_VISION_MODEL,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [img_b64]
            }]
        )
        content = response["message"]["content"].strip()
        if content:
            return content
    except Exception as exc:
        print(f"[PIXTRAL_OCR] Vision model '{OLLAMA_VISION_MODEL}' call failed ({exc}). Falling back to Tesseract.")

    # Graceful fallback to Tesseract
    try:
        from ingestion.tesseract_ocr import run_tesseract
    except ImportError:
        from backend.ingestion.tesseract_ocr import run_tesseract

    return run_tesseract(image_input)
