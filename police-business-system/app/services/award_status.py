"""敘獎週期/緩衝期計算：週期結束後有 1 個月緩衝期才是最終敘獎期限，
剩 7 天內轉「即將逾期」，超過期限未完成則持續顯示「已逾期」。"""

from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app.models import AwardCycle, AwardRecord, AwardStatus, CycleType

DUE_SOON_WINDOW_DAYS = 7

_CYCLE_MONTHS = {
    CycleType.QUARTERLY: 3,
    CycleType.SEMIANNUAL: 6,
    CycleType.ANNUAL: 12,
}


def period_length(cycle_type: CycleType) -> relativedelta:
    return relativedelta(months=_CYCLE_MONTHS[cycle_type])


def ensure_records_up_to_today(db: Session, cycle: AwardCycle, today: date | None = None) -> list[AwardRecord]:
    """把從 start_date 到今天為止、已經結束的週期都補齊對應的 AwardRecord。"""
    today = today or date.today()
    step = period_length(cycle.cycle_type)

    existing_ends = {r.period_end for r in cycle.records}
    period_start = cycle.start_date
    period_end = period_start + step
    created: list[AwardRecord] = []

    while period_end <= today or not existing_ends:
        if period_end not in existing_ends:
            record = AwardRecord(
                cycle_id=cycle.id,
                period_start=period_start,
                period_end=period_end,
                deadline=period_end + relativedelta(months=1),
            )
            db.add(record)
            created.append(record)
        if period_end > today:
            break
        period_start = period_end
        period_end = period_start + step

    if created:
        db.flush()
    return created


def compute_status(record: AwardRecord, today: date | None = None) -> AwardStatus:
    today = today or date.today()

    if record.completed_at is not None:
        return AwardStatus.DONE
    if today < record.period_end:
        return AwardStatus.NOT_DUE
    if today > record.deadline:
        return AwardStatus.OVERDUE
    if (record.deadline - today).days <= DUE_SOON_WINDOW_DAYS:
        return AwardStatus.DUE_SOON
    return AwardStatus.OPEN


STATUS_LABEL = {
    AwardStatus.NOT_DUE: ("尚未到期", "gray"),
    AwardStatus.OPEN: ("可開始敘獎", "yellow"),
    AwardStatus.DUE_SOON: ("即將逾期", "red"),
    AwardStatus.OVERDUE: ("已逾期", "dark-red"),
    AwardStatus.DONE: ("已完成", "green"),
}
