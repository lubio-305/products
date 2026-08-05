from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import AwardCycle, AwardRecord, BusinessNode, User
from app.schemas import AwardCycleRequest, AwardRecordOut
from app.services.award_status import compute_status, ensure_records_up_to_today

router = APIRouter(prefix="/api/nodes/{node_id}/awards", tags=["awards"])


@router.post("/cycles", status_code=status.HTTP_201_CREATED)
def create_cycle(
    node_id: int,
    payload: AwardCycleRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    node = db.get(BusinessNode, node_id)
    if node is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到節點")
    if not node.is_leaf():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "只有最底層節點才能設定敘獎週期")

    cycle = AwardCycle(node_id=node_id, cycle_type=payload.cycle_type, start_date=payload.start_date)
    db.add(cycle)
    db.flush()
    ensure_records_up_to_today(db, cycle)
    db.commit()
    return {"id": cycle.id}


@router.get("/records", response_model=list[AwardRecordOut])
def list_records(node_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cycles = db.query(AwardCycle).filter(AwardCycle.node_id == node_id, AwardCycle.active.is_(True)).all()

    results = []
    for cycle in cycles:
        ensure_records_up_to_today(db, cycle)
    db.commit()

    for cycle in cycles:
        for record in cycle.records:
            results.append(
                AwardRecordOut(
                    id=record.id,
                    period_start=record.period_start,
                    period_end=record.period_end,
                    deadline=record.deadline,
                    status=compute_status(record),
                    completed_at=record.completed_at,
                )
            )
    return sorted(results, key=lambda r: r.period_start)


@router.post("/records/{record_id}/complete")
def complete_record(
    node_id: int,
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = db.get(AwardRecord, record_id)
    if record is None or record.cycle.node_id != node_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到敘獎紀錄")

    record.completed_at = datetime.utcnow()
    record.completed_by_id = user.id
    db.commit()
    return {"ok": True}
