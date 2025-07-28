import fitz
import os
from pdf2image import convert_from_path
import pytesseract

def extract_text_with_ocr(pdf_path: str) -> str:
    images = convert_from_path(pdf_path)
    full_text = ""
    for image in images:
        text = pytesseract.image_to_string(image)
        full_text += text + "\n"
    return full_text


def extract_chunks_from_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    full_text = "".join([page.get_text() for page in doc])

    # OCR fallback if no extractable text
    if not full_text.strip():
        full_text = extract_text_with_ocr(pdf_path)

    # Simple chunking logic
    parts = full_text.split("Test Report")
    chunks = []
    for section in parts[1:]:
        if "Test Name" in section:
            chunks.append(section.strip())

    # fallback to page-wise
    if not chunks:
        for page in doc:
            txt = page.get_text().strip()
            if txt:
                chunks.append(txt)

    return chunks, full_text
