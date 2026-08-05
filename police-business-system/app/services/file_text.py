"""從上傳檔案抽取文字；抽不到文字層（多半是掃描檔/圖片）時交給 OCR。"""

import os

from pypdf import PdfReader
from docx import Document

TEXT_EXTRACTABLE_EXT = {".pdf", ".docx"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def extract_text(file_path: str) -> tuple[str, bool]:
    """回傳 (抽出的文字, 是否需要 OCR)。"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = _extract_pdf_text(file_path)
        if text.strip():
            return text, False
        return "", True  # 抽不到文字層，可能是掃描 PDF

    if ext == ".docx":
        return _extract_docx_text(file_path), False

    if ext in IMAGE_EXT:
        return "", True

    return "", False


def _extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)
