from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import BusinessNode, NodeAssignment, NodeChangeAction, NodeChangeLog, User
from app.schemas import NodeCreateRequest, NodeMoveRequest, NodeOut, NodeRenameRequest

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
