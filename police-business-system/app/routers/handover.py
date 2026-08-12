"""人員異動（交接）：管理者選離職/調任人員 -> 勾選要移轉的業務(可整批) ->
指定新的主辦/協辦人員。系統結束舊的承辦歷程、新增新的一筆，不覆蓋舊紀錄。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import AssignmentHistory, NodeAssignment, User
from app.schemas import HandoverRequest

router = APIRouter(prefix="/api/handover", tags=["handover"])


@router.post("", status_code=status.HTTP_200_OK)
def handover(
    payload: HandoverRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    if db.get(User, payload.from_user_id) is None or db.get(User, payload.to_user_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到人員")

    moved = []
    for node_id in payload.node_ids:
        old_assignment = (
            db.query(NodeAssignment)
            .filter(
                NodeAssignment.node_id == node_id,
                NodeAssignment.user_id == payload.from_user_id,
            )
            .first()
        )
        if old_assignment is None:
            continue

        old_history = (
            db.query(AssignmentHistory)
            .filter(
                AssignmentHistory.node_id == node_id,
                AssignmentHistory.user_id == payload.from_user_id,
                AssignmentHistory.end_date.is_(None),
            )
            .first()
        )
        if old_history:
            old_history.end_date = payload.effective_date

        db.delete(old_assignment)

        already_assigned = (
            db.query(NodeAssignment)
            .filter(NodeAssignment.node_id == node_id, NodeAssignment.user_id == payload.to_user_id)
            .first()
        )
        if not already_assigned:
            db.add(
                NodeAssignment(node_id=node_id, user_id=payload.to_user_id, role=payload.role)
            )
            db.add(
                AssignmentHistory(
                    node_id=node_id,
                    user_id=payload.to_user_id,
                    role=payload.role,
                    start_date=payload.effective_date,
                )
            )
        moved.append(node_id)

    db.commit()
    return {"moved_node_ids": moved}
