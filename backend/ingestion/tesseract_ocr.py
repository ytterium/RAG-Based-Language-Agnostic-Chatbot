"""
Tesseract OCR module with OpenCV preprocessing.
Handles image deskewing, Otsu adaptive binarization, Laplacian sharpness computation,
and text extraction via Tesseract 5.x.
"""
import os
from typing import Union
import cv2
import numpy as np
import pytesseract

try:
    from config import TESSERACT_PATH
except ImportError:
    from backend.config import TESSERACT_PATH

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def load_image(image_input: Union[str, np.ndarray]) -> np.ndarray:
    """
    Load an image safely from a file path or return existing ndarray.
    Supports Unicode/Windows file paths.
    """
    if isinstance(image_input, np.ndarray):
        return image_input

    if not isinstance(image_input, str) or not os.path.exists(image_input):
        raise FileNotFoundError(f"Image path does not exist: {image_input}")

    # Use imdecode to support Unicode and Windows special character paths
    img = cv2.imdecode(np.fromfile(image_input, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        img = cv2.imread(image_input)
    if img is None:
        raise ValueError(f"OpenCV failed to decode image from: {image_input}")
    return img


def compute_sharpness(image: Union[str, np.ndarray]) -> float:
    """
    Compute image sharpness using the variance of the Laplacian.
    Higher values indicate sharp, in-focus text.
    Values below OCR_SHARPNESS_THRESHOLD indicate blurry/degraded images.
    """
    img = load_image(image)
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def deskew_image(gray: np.ndarray) -> np.ndarray:
    """
    Detect text orientation and deskew grayscale image if slight rotation is detected.
    """
    try:
        # Invert to have foreground text as white pixels
        thresh = cv2.bitwise_not(gray)
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 100:
            return gray

        angle = cv2.minAreaRect(coords)[-1]
        # Adjust angle from OpenCV conventions
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        # Avoid extreme rotation if text layout is unusual
        if abs(angle) > 20:
            return gray

        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            gray,
            rotation_matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
    except Exception:
        # Fallback to unrotated image if deskew fails
        return gray


def preprocess_image(image: Union[str, np.ndarray]) -> np.ndarray:
    """
    Full OpenCV preprocessing pipeline before OCR:
    1. Grayscale conversion
    2. Optional deskewing
    3. Noise reduction
    4. Otsu automatic adaptive binarization
    """
    img = load_image(image)

    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Deskew
    deskewed = deskew_image(gray)

    # Slight Gaussian blur to reduce high-frequency scan noise
    blurred = cv2.GaussianBlur(deskewed, (3, 3), 0)

    # Otsu adaptive binarization
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary


def run_tesseract(image_input: Union[str, np.ndarray], lang: str = "eng") -> str:
    """
    Run Tesseract OCR on a clean or preprocessed image.

    Args:
        image_input: File path or numpy ndarray of the image.
        lang: Tesseract language code (default: 'eng').

    Returns:
        Extracted text string.
    """
    preprocessed = preprocess_image(image_input)
    custom_config = r"--oem 3 --psm 3"
    text = pytesseract.image_to_string(preprocessed, lang=lang, config=custom_config)
    return text.strip()
