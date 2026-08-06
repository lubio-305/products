from datetime import date

from app.models import AwardCycle, BusinessNode, CycleType, User
from app.services.award_status import compute_status, ensure_records_up_to_today


def _make_leaf(db, name="防制面"):
    admin = db.query(User).filter(User.is_admin.is_(True)).first()
    node = BusinessNode(name=name, parent_id=None, created_by_id=admin.id)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def test_ensure_records_backfills_quarterly_periods(db_session, admin_user):
    node = _make_leaf(db_session)
    cycle = AwardCycle(node_id=node.id, cycle_type=CycleType.QUARTERLY, start_date=date(2025, 1, 1))
    db_session.add(cycle)
    db_session.commit()

    created = ensure_records_up_to_today(db_session, cycle, today=date(2025, 8, 15))
    db_session.commit()

    # 2025-01-01 起算，每季一期：Q1(1/1-4/1)、Q2(4/1-7/1)、Q3(7/1-10/1) 三期都已開始
    assert len(created) == 3
    assert [r.period_end for r in created] == [date(2025, 4, 1), date(2025, 7, 1), date(2025, 10, 1)]
    assert created[0].deadline == date(2025, 5, 1)  # period_end + 1 個月緩衝期


def test_ensure_records_is_idempotent(db_session, admin_user):
    node = _make_leaf(db_session)
    cycle = AwardCycle(node_id=node.id, cycle_type=CycleType.ANNUAL, start_date=date(2024, 1, 1))
    db_session.add(cycle)
    db_session.commit()

    ensure_records_up_to_today(db_session, cycle, today=date(2025, 6, 1))
    db_session.commit()
    first_count = len(cycle.records)

    # 同一個範圍再跑一次，不應該重複建立
    ensure_records_up_to_today(db_session, cycle, today=date(2025, 6, 1))
    db_session.commit()
    assert len(cycle.records) == first_count


def test_status_not_due_before_period_end():
    record = _fake_record(period_end=date(2025, 4, 1), deadline=date(2025, 5, 1))
    assert compute_status(record, today=date(2025, 3, 1)) == "not_due"


def test_status_open_right_after_period_end():
    record = _fake_record(period_end=date(2025, 4, 1), deadline=date(2025, 5, 1))
    assert compute_status(record, today=date(2025, 4, 1)) == "open"


def test_status_due_soon_within_7_days_of_deadline():
    record = _fake_record(period_end=date(2025, 4, 1), deadline=date(2025, 5, 1))
    assert compute_status(record, today=date(2025, 4, 25)) == "due_soon"


def test_status_overdue_after_deadline():
    record = _fake_record(period_end=date(2025, 4, 1), deadline=date(2025, 5, 1))
    assert compute_status(record, today=date(2025, 5, 2)) == "overdue"


def test_status_done_once_completed():
    from datetime import datetime

    record = _fake_record(period_end=date(2025, 4, 1), deadline=date(2025, 5, 1))
    record.completed_at = datetime(2025, 4, 10)
    assert compute_status(record, today=date(2025, 6, 1)) == "done"


def _fake_record(period_end, deadline):
    from app.models import AwardRecord

    return AwardRecord(period_start=date(2025, 1, 1), period_end=period_end, deadline=deadline)


def test_award_endpoints_via_api(admin_client):
    node = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    admin_client.post(
        f"/api/nodes/{node['id']}/awards/cycles",
        json={"cycle_type": "quarterly", "start_date": "2025-01-01"},
    )

    records = admin_client.get(f"/api/nodes/{node['id']}/awards/records").json()
    assert len(records) >= 1
    first = records[0]

    complete_resp = admin_client.post(f"/api/nodes/{node['id']}/awards/records/{first['id']}/complete")
    assert complete_resp.status_code == 200

    records_after = admin_client.get(f"/api/nodes/{node['id']}/awards/records").json()
    assert records_after[0]["status"] == "done"


def test_only_leaf_node_can_have_award_cycle(admin_client):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    admin_client.post("/api/nodes", json={"name": "防制面", "parent_id": top["id"]})

    resp = admin_client.post(
        f"/api/nodes/{top['id']}/awards/cycles",
        json={"cycle_type": "quarterly", "start_date": "2025-01-01"},
    )
    assert resp.status_code == 400
