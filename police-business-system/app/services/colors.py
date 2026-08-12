"""承辦人色盤：新帳號依建立順序自動領一個顏色，卡片式總覽用這個顏色分辨
「這是誰的業務」，帳號管理頁面也會顯示每人對應的顏色。"""

from sqlalchemy.orm import Session

from app.models import User

STAFF_PALETTE = [
    "#2563eb",  # blue
    "#16a34a",  # green
    "#ea580c",  # orange
    "#9333ea",  # purple
    "#0d9488",  # teal
    "#db2777",  # magenta
    "#ca8a04",  # amber
    "#4f46e5",  # indigo
    "#059669",  # emerald
    "#c2410c",  # burnt orange
    "#7c3aed",  # violet
    "#0891b2",  # cyan
]


def next_color(db: Session) -> str:
    existing = db.query(User).count()
    return STAFF_PALETTE[existing % len(STAFF_PALETTE)]
