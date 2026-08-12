from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import NodeChangeLog, User
from app.schemas import NodeChangeLogOut

router = APIRouter(prefix="/api/changelog", tags=["changelog"])


@router.get("", response_model=list[NodeChangeLogOut])
def list_changelog(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(NodeChangeLog).order_by(NodeChangeLog.created_at.desc()).limit(200).all()
