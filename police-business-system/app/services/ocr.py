"""繁體中文 OCR，只在 file_text.extract_text 判斷需要時才呼叫（避免每份都跑，拖慢效能）。
需要容器內安裝 tesseract-ocr 與 chi_tra 語言包，見 Dockerfile。"""

import os

import pytesseract
from PIL import Image

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def ocr_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext in IMAGE_EXT:
        return pytesseract.image_to_string(Image.open(file_path), lang="chi_tra")

    if ext == ".pdf":
        return _ocr_pdf(file_path)

    return ""


def _ocr_pdf(file_path: str) -> str:
    from pdf2image import convert_from_path

    pages = convert_from_path(file_path)
    return "\n".join(
        pytesseract.image_to_string(page, lang="chi_tra") for page in pages
    )
