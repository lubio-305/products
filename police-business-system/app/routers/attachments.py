"""公文/補充資料上傳，承辦人手動填寫重點摘要（3-5行），
避免更換承辦人時斷點。掃描檔會標記 needs_ocr，並非同步跑 OCR 補上 ocr_text。"""

import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import UPLOAD_DIR, get_db
from app.models import Attachment, BusinessNode, User
from app.schemas import AttachmentOut
from app.services.file_text import extract_text
from app.services.ocr import ocr_file

router = APIRouter(prefix="/api/nodes/{node_id}/attachments", tags=["attachments"])


@router.get("", response_model=list[AttachmentOut])
def list_attachments(node_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Attachment)
        .filter(Attachment.node_id == node_id)
        .order_by(Attachment.uploaded_at.desc())
        .all()
    )


@router.post("", response_model=AttachmentOut, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    node_id: int,
    summary: str = Form(default=""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    node = db.get(BusinessNode, node_id)
    if node is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到節點")
    if not node.is_leaf():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "只有最底層節點才能上傳附件")

    node_dir = os.path.join(UPLOAD_DIR, "attachments", str(node_id))
    os.makedirs(node_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    stored_path = os.path.join(node_dir, stored_name)
    with open(stored_path, "wb") as f:
        f.write(file.file.read())

    _, needs_ocr = extract_text(stored_path)
    ocr_text = ocr_file(stored_path) if needs_ocr else None

    attachment = Attachment(
        node_id=node_id,
        original_filename=file.filename,
        file_path=stored_path,
        summary=summary or None,
        needs_ocr=needs_ocr,
        ocr_text=ocr_text,
        uploaded_by_id=user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment
