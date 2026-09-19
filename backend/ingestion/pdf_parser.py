"""
PDF Parser module for extracting text and tables from digital institutional PDF circulars.
Uses PyMuPDF (fitz) for fast, layout-aware extraction.
"""
from typing import List, Dict, Any
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract text page-by-page from a digital/searchable PDF.
    Preserves table structures by extracting rows with cell delimiters.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        List of dictionaries with:
            - "page_num": int (1-indexed)
            - "text": str (combined extracted text and formatted tables)
            - "is_searchable": bool (True if native text layer contains non-whitespace content)
    """
    pages: List[Dict[str, Any]] = []

    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()

            table_text = ""
            try:
                tables = page.find_tables()
                if tables and hasattr(tables, "tables"):
                    for table in tables.tables:
                        extracted_rows = table.extract()
                        if extracted_rows:
                            for row in extracted_rows:
                                row_str = " | ".join(str(cell or "").strip() for cell in row)
                                if row_str.strip():
                                    table_text += row_str + "\n"
            except Exception as e:
                # Layouts without clear tables or unsupported geometries should not break extraction
                pass

            combined_text = (text + ("\n" + table_text if table_text else "")).strip()

            pages.append({
                "page_num": page_num + 1,
                "text": combined_text,
                "is_searchable": bool(text.strip())
            })

    return pages
