"""給管理者選單用：人員清單、某人目前身兼哪些業務節點（交接時要用來勾選要移轉哪些業務）。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import BusinessNode, NodeAssignment, User
from app.schemas import UserAssignmentOut, UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).order_by(User.display_name).all()


@router.get("/{user_id}/assignments", response_model=list[UserAssignmentOut])
def list_user_assignments(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    rows = (
        db.query(NodeAssignment, BusinessNode)
        .join(BusinessNode, BusinessNode.id == NodeAssignment.node_id)
        .filter(NodeAssignment.user_id == user_id)
        .all()
    )
    return [
        UserAssignmentOut(node_id=node.id, node_name=node.name, role=assignment.role)
        for assignment, node in rows
    ]
