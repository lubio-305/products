"""從上傳檔案抽取文字；抽不到文字層（多半是掃描檔/圖片）時交給 OCR。"""

import os

from pypdf import PdfReader
from docx import Document

TEXT_EXTRACTABLE_EXT = {".pdf", ".docx"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def extract_text(file_path: str) -> tuple[str, bool]:
    """回傳 (抽出的文字, 是否需要 OCR)。檔案損毀或格式異常時，視同抽不到文字層，
    一樣落到 OCR 這條路，而不是讓上傳整支 API 500。"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        try:
            text = _extract_pdf_text(file_path)
        except Exception:
            return "", True
        if text.strip():
            return text, False
        return "", True  # 抽不到文字層，可能是掃描 PDF

    if ext == ".docx":
        try:
            return _extract_docx_text(file_path), False
        except Exception:
            return "", True

    if ext in IMAGE_EXT:
        return "", True

    return "", False


def _extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)
