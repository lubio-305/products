"""給每個承辦人看「自己上傳過哪些東西」：規定/計畫版本跟公文附件都算，
不分節點彙總在一起，附下載連結。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Attachment, BusinessNode, RegulationVersion, User
from app.schemas import MyUploadOut

router = APIRouter(prefix="/api/my", tags=["my"])


@router.get("/uploads", response_model=list[MyUploadOut])
def list_my_uploads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    results: list[MyUploadOut] = []

    reg_rows = (
        db.query(RegulationVersion, BusinessNode)
        .join(BusinessNode, BusinessNode.id == RegulationVersion.node_id)
        .filter(RegulationVersion.uploaded_by_id == user.id)
        .all()
    )
    for reg, node in reg_rows:
        results.append(
            MyUploadOut(
                type="regulation",
                id=reg.id,
                node_id=node.id,
                node_name=node.name,
                filename=f"{reg.title} v{reg.version_no}",
                uploaded_at=reg.uploaded_at,
            )
        )

    att_rows = (
        db.query(Attachment, BusinessNode)
        .join(BusinessNode, BusinessNode.id == Attachment.node_id)
        .filter(Attachment.uploaded_by_id == user.id)
        .all()
    )
    for att, node in att_rows:
        results.append(
            MyUploadOut(
                type="attachment",
                id=att.id,
                node_id=node.id,
                node_name=node.name,
                filename=att.original_filename,
                uploaded_at=att.uploaded_at,
            )
        )

    results.sort(key=lambda r: r.uploaded_at, reverse=True)
    return results
