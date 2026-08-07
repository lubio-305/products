from datetime import date, datetime

from pydantic import BaseModel

from app.models import AssignmentRole, AwardStatus, CycleType, NodeChangeAction


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    is_admin: bool

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    username: str
    password: str
    display_name: str
    is_admin: bool = False


class NodeCreateRequest(BaseModel):
    name: str
    parent_id: int | None = None


class NodeRenameRequest(BaseModel):
    name: str


class NodeMoveRequest(BaseModel):
    new_parent_id: int | None


class NodeOut(BaseModel):
    id: int
    name: str
    parent_id: int | None
    is_leaf: bool

    class Config:
        from_attributes = True


class AssignmentRequest(BaseModel):
    user_id: int
    role: AssignmentRole


class UserAssignmentOut(BaseModel):
    node_id: int
    node_name: str
    role: AssignmentRole


class HandoverRequest(BaseModel):
    from_user_id: int
    to_user_id: int
    node_ids: list[int]
    role: AssignmentRole
    effective_date: date


class RegulationVersionOut(BaseModel):
    id: int
    title: str
    version_no: int
    effective_date: date
    expired_date: date | None
    uploaded_at: datetime

    class Config:
        from_attributes = True


class AwardCycleRequest(BaseModel):
    cycle_type: CycleType
    start_date: date


class AwardRecordOut(BaseModel):
    id: int
    period_start: date
    period_end: date
    deadline: date
    status: AwardStatus
    completed_at: datetime | None

    class Config:
        from_attributes = True


class AttachmentOut(BaseModel):
    id: int
    original_filename: str
    summary: str | None
    needs_ocr: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True


class NodeChangeLogOut(BaseModel):
    id: int
    node_id: int
    action: NodeChangeAction
    detail: str | None
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
