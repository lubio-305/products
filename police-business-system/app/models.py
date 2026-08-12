import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class AssignmentRole(str, enum.Enum):
    PRIMARY = "primary"  # 主辦
    SUPPORT = "support"  # 協辦


class CycleType(str, enum.Enum):
    QUARTERLY = "quarterly"  # 每季
    SEMIANNUAL = "semiannual"  # 每半年
    ANNUAL = "annual"  # 每年


class AwardStatus(str, enum.Enum):
    NOT_DUE = "not_due"  # 尚未到期
    OPEN = "open"  # 可開始敘獎（緩衝期內，剩7天以上）
    DUE_SOON = "due_soon"  # 即將逾期（剩7天內）
    OVERDUE = "overdue"  # 已逾期
    DONE = "done"  # 已完成


class NodeChangeAction(str, enum.Enum):
    CREATE = "create"
    RENAME = "rename"
    MOVE = "move"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    color = Column(String(7), nullable=True)  # 卡片式總覽用，依建立順序自動分配
    created_at = Column(DateTime, default=datetime.utcnow)

    assignments = relationship("NodeAssignment", back_populates="user")


class BusinessNode(Base):
    """不限層數的業務樹狀結構；只有沒有子節點的「葉節點」才會實際掛
    規定/計畫、敘獎週期、附件與承辦人指派，上層節點純粹是分類用的資料夾。"""

    __tablename__ = "business_nodes"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("BusinessNode", remote_side=[id], back_populates="children")
    children = relationship("BusinessNode", back_populates="parent")

    assignments = relationship(
        "NodeAssignment", back_populates="node", cascade="all, delete-orphan"
    )
    regulation_versions = relationship(
        "RegulationVersion", back_populates="node", cascade="all, delete-orphan"
    )
    award_cycles = relationship(
        "AwardCycle", back_populates="node", cascade="all, delete-orphan"
    )
    attachments = relationship(
        "Attachment", back_populates="node", cascade="all, delete-orphan"
    )
    assignment_history = relationship(
        "AssignmentHistory", back_populates="node", cascade="all, delete-orphan"
    )

    def is_leaf(self) -> bool:
        return len(self.children) == 0


class NodeAssignment(Base):
    """目前生效的「誰負責這個業務節點」，主辦/協辦皆可多筆。"""

    __tablename__ = "node_assignments"
    __table_args__ = (UniqueConstraint("node_id", "user_id", name="uq_node_user"),)

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(AssignmentRole), nullable=False, default=AssignmentRole.PRIMARY)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    node = relationship("BusinessNode", back_populates="assignments")
    user = relationship("User", back_populates="assignments")


class AssignmentHistory(Base):
    """交接留下的完整承辦歷程：誰在哪段時間負責過這個節點。"""

    __tablename__ = "assignment_history"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(AssignmentRole), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # NULL 代表目前仍在職務中

    node = relationship("BusinessNode", back_populates="assignment_history")
    user = relationship("User")


class RegulationVersion(Base):
    """業務節點的規定/計畫檔案，每次上傳新版都新增一筆，保留完整版本歷史。"""

    __tablename__ = "regulation_versions"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=False)
    title = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    version_no = Column(Integer, nullable=False)
    effective_date = Column(Date, nullable=False)
    expired_date = Column(Date, nullable=True)  # 新版上傳時，前一版自動填入
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    node = relationship("BusinessNode", back_populates="regulation_versions")
    uploaded_by = relationship("User")

    @property
    def is_current(self) -> bool:
        return self.expired_date is None


class AwardCycle(Base):
    """敘獎週期設定：週期類型＋起算日，用來推算每一期的到期日與最終期限。"""

    __tablename__ = "award_cycles"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=False)
    cycle_type = Column(Enum(CycleType), nullable=False)
    start_date = Column(Date, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    node = relationship("BusinessNode", back_populates="award_cycles")
    records = relationship(
        "AwardRecord", back_populates="cycle", cascade="all, delete-orphan"
    )


class AwardRecord(Base):
    """每一期的敘獎執行紀錄。deadline = period_end + 1 個月緩衝期。"""

    __tablename__ = "award_records"

    id = Column(Integer, primary_key=True)
    cycle_id = Column(Integer, ForeignKey("award_cycles.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    deadline = Column(Date, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    completed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    cycle = relationship("AwardCycle", back_populates="records")
    completed_by = relationship("User")


class Attachment(Base):
    """業務節點的公文/補充資料上傳，含承辦人手動填寫的重點摘要。"""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=False)
    original_filename = Column(String(300), nullable=False)
    file_path = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    needs_ocr = Column(Boolean, default=False, nullable=False)
    ocr_text = Column(Text, nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    node = relationship("BusinessNode", back_populates="attachments")
    uploaded_by = relationship("User")


class NodeChangeLog(Base):
    """業務樹結構異動歷程：誰、何時、對哪個節點做了新增/改名/搬移。"""

    __tablename__ = "node_change_log"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("business_nodes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(Enum(NodeChangeAction), nullable=False)
    detail = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    node = relationship("BusinessNode")
    user = relationship("User")
