from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import AssignmentHistory, BusinessNode, NodeAssignment, User
from app.schemas import AssignmentRequest

router = APIRouter(prefix="/api/nodes/{node_id}/assignments", tags=["assignments"])


@router.get("")
def list_assignments(
    node_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    assignments = db.query(NodeAssignment).filter(NodeAssignment.node_id == node_id).all()
    return [
        {
            "user_id": a.user_id,
            "display_name": a.user.display_name,
            "role": a.role,
        }
        for a in assignments
    ]


def _require_leaf(db: Session, node_id: int) -> BusinessNode:
    node = db.get(BusinessNode, node_id)
    if node is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到節點")
    if not node.is_leaf():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "只有最底層節點才能指派承辦人")
    return node


@router.post("", status_code=status.HTTP_201_CREATED)
def assign_user(
    node_id: int,
    payload: AssignmentRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    _require_leaf(db, node_id)

    existing = (
        db.query(NodeAssignment)
        .filter(NodeAssignment.node_id == node_id, NodeAssignment.user_id == payload.user_id)
        .first()
    )
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "此人員已指派到這個節點")

    db.add(NodeAssignment(node_id=node_id, user_id=payload.user_id, role=payload.role))
    db.add(
        AssignmentHistory(
            node_id=node_id,
            user_id=payload.user_id,
            role=payload.role,
            start_date=date.today(),
        )
    )
    db.commit()
    return {"ok": True}


@router.delete("/{user_id}")
def remove_assignment(
    node_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    assignment = (
        db.query(NodeAssignment)
        .filter(NodeAssignment.node_id == node_id, NodeAssignment.user_id == user_id)
        .first()
    )
    if assignment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到指派紀錄")

    history = (
        db.query(AssignmentHistory)
        .filter(
            AssignmentHistory.node_id == node_id,
            AssignmentHistory.user_id == user_id,
            AssignmentHistory.end_date.is_(None),
        )
        .first()
    )
    if history:
        history.end_date = date.today()

    db.delete(assignment)
    db.commit()
    return {"ok": True}
