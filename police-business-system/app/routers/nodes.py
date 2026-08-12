from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import (
    AssignmentRole,
    AwardCycle,
    BusinessNode,
    NodeAssignment,
    NodeChangeAction,
    NodeChangeLog,
    User,
)
from app.schemas import NodeCardOut, NodeCreateRequest, NodeMoveRequest, NodeOut, NodeRenameRequest
from app.services.award_status import compute_status, ensure_records_up_to_today

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


def _user_has_scope(db: Session, user: User, node_id: int) -> bool:
    """管理者不受限；一般承辦人只能在自己已有份（本節點或往上任一祖先節點）
    有主辦/協辦指派的範圍下新增子節點。"""
    if user.is_admin:
        return True

    node = db.get(BusinessNode, node_id)
    while node is not None:
        has_assignment = (
            db.query(NodeAssignment)
            .filter(NodeAssignment.node_id == node.id, NodeAssignment.user_id == user.id)
            .first()
        )
        if has_assignment:
            return True
        node = node.parent
    return False


@router.get("", response_model=list[NodeOut])
def list_nodes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    nodes = db.query(BusinessNode).all()
    return [
        NodeOut(id=n.id, name=n.name, parent_id=n.parent_id, is_leaf=n.is_leaf())
        for n in nodes
    ]


@router.get("/cards", response_model=list[NodeCardOut])
def list_node_cards(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """卡片式業務總覽用：每個底層節點一張卡片，含業務大類/子項目的麵包屑、
    主辦承辦人（含固定顏色）、協辦人員姓名、最新一期敘獎狀態。"""
    nodes = db.query(BusinessNode).all()
    by_id = {n.id: n for n in nodes}
    children_count: dict[int, int] = {}
    for n in nodes:
        if n.parent_id is not None:
            children_count[n.parent_id] = children_count.get(n.parent_id, 0) + 1

    def breadcrumb(node: BusinessNode) -> str:
        names = []
        cur = by_id.get(node.parent_id) if node.parent_id else None
        while cur is not None:
            names.append(cur.name)
            cur = by_id.get(cur.parent_id) if cur.parent_id else None
        return " › ".join(reversed(names))

    cards = []
    for n in nodes:
        if children_count.get(n.id, 0) > 0:
            continue  # 只有葉節點才是卡片，上層節點純粹分類用

        assignments = db.query(NodeAssignment).filter(NodeAssignment.node_id == n.id).all()
        primary = next((a for a in assignments if a.role == AssignmentRole.PRIMARY), None)
        support_names = [a.user.display_name for a in assignments if a.role == AssignmentRole.SUPPORT]

        award_status = None
        cycle = (
            db.query(AwardCycle)
            .filter(AwardCycle.node_id == n.id, AwardCycle.active.is_(True))
            .first()
        )
        if cycle is not None:
            ensure_records_up_to_today(db, cycle)
            db.commit()
            latest = max(cycle.records, key=lambda r: r.period_start, default=None)
            if latest is not None:
                award_status = compute_status(latest)

        cards.append(
            NodeCardOut(
                id=n.id,
                name=n.name,
                breadcrumb=breadcrumb(n),
                primary_user=primary.user if primary else None,
                support_names=support_names,
                award_status=award_status,
            )
        )
    return cards


@router.post("", response_model=NodeOut, status_code=status.HTTP_201_CREATED)
def create_node(
    payload: NodeCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.parent_id is None and not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "頂層業務大類僅限管理者建立")

    if payload.parent_id is not None:
        parent = db.get(BusinessNode, payload.parent_id)
        if parent is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到上層節點")
        if not _user_has_scope(db, user, payload.parent_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "只能在自己已有份的節點下新增子節點")

    node = BusinessNode(name=payload.name, parent_id=payload.parent_id, created_by_id=user.id)
    db.add(node)
    db.flush()

    db.add(
        NodeChangeLog(
            node_id=node.id,
            user_id=user.id,
            action=NodeChangeAction.CREATE,
            detail=f"建立節點「{node.name}」",
        )
    )
    db.commit()
    db.refresh(node)
    return NodeOut(id=node.id, name=node.name, parent_id=node.parent_id, is_leaf=node.is_leaf())


@router.patch("/{node_id}/rename", response_model=NodeOut)
def rename_node(
    node_id: int,
    payload: NodeRenameRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    node = db.get(BusinessNode, node_id)
    if node is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到節點")

    old_name = node.name
    node.name = payload.name
    db.add(
        NodeChangeLog(
            node_id=node.id,
            user_id=user.id,
            action=NodeChangeAction.RENAME,
            detail=f"「{old_name}」→「{payload.name}」",
        )
    )
    db.commit()
    db.refresh(node)
    return NodeOut(id=node.id, name=node.name, parent_id=node.parent_id, is_leaf=node.is_leaf())


@router.patch("/{node_id}/move", response_model=NodeOut)
def move_node(
    node_id: int,
    payload: NodeMoveRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    node = db.get(BusinessNode, node_id)
    if node is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "找不到節點")

    old_parent_id = node.parent_id
    node.parent_id = payload.new_parent_id
    db.add(
        NodeChangeLog(
            node_id=node.id,
            user_id=user.id,
            action=NodeChangeAction.MOVE,
            detail=f"上層節點 {old_parent_id} → {payload.new_parent_id}",
        )
    )
    db.commit()
    db.refresh(node)
    return NodeOut(id=node.id, name=node.name, parent_id=node.parent_id, is_leaf=node.is_leaf())
