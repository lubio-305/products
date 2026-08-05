"""規定/計畫上傳：每次上傳新版都新增一筆版本紀錄，並把前一個「現行版本」標記失效，
保留完整版本歷史供之後回溯查閱。"""

import os
import uuid
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import UPLOAD_DIR, get_db
from app.models import BusinessNode, RegulationVersion, User
from app.schemas import RegulationVersionOut

router = APIRouter(prefix="/api/nodes/{node_id}/regulations", tags=["regulations"])


@router.get("", response_model=list[RegulationVersionOut])
def list_versions(node_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(RegulationVersion)
        .filter(RegulationVersion.node_id == node_id)
        .order_by(RegulationVersion.version_no.desc())
        .all()
    )


@router.post("", response_model=RegulationVersionOut, status_code=status.HTTP_201_CREATED)
def upload_version(
    node_id: int,
    title: str = Form(...),
    effective_date: date = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    node = db.get(BusinessNode, node_id)
    if node is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到節點")
    if not node.is_leaf():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "只有最底層節點才能上傳規定/計畫")

    current = (
        db.query(RegulationVersion)
        .filter(RegulationVersion.node_id == node_id, RegulationVersion.expired_date.is_(None))
        .first()
    )
    next_version_no = (current.version_no + 1) if current else 1
    if current:
        current.expired_date = effective_date

    node_dir = os.path.join(UPLOAD_DIR, "regulations", str(node_id))
    os.makedirs(node_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{file.filename}"
    stored_path = os.path.join(node_dir, stored_name)
    with open(stored_path, "wb") as f:
        f.write(file.file.read())

    version = RegulationVersion(
        node_id=node_id,
        title=title,
        file_path=stored_path,
        version_no=next_version_no,
        effective_date=effective_date,
        uploaded_by_id=user.id,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version
