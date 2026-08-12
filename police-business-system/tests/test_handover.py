from app.models import AssignmentHistory, NodeAssignment


def _assigned_leaf(admin_client, staff_user, name="防制面"):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    leaf = admin_client.post("/api/nodes", json={"name": name, "parent_id": top["id"]}).json()
    admin_client.post(
        f"/api/nodes/{leaf['id']}/assignments",
        json={"user_id": staff_user.id, "role": "primary"},
    )
    return leaf


def test_handover_moves_assignment_and_keeps_history(
    admin_client, db_session, staff_user, other_staff_user
):
    leaf = _assigned_leaf(admin_client, staff_user)

    resp = admin_client.post(
        "/api/handover",
        json={
            "from_user_id": staff_user.id,
            "to_user_id": other_staff_user.id,
            "node_ids": [leaf["id"]],
            "role": "primary",
            "effective_date": "2025-09-01",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["moved_node_ids"] == [leaf["id"]]

    remaining = (
        db_session.query(NodeAssignment)
        .filter(NodeAssignment.node_id == leaf["id"], NodeAssignment.user_id == staff_user.id)
        .first()
    )
    assert remaining is None

    new_assignment = (
        db_session.query(NodeAssignment)
        .filter(NodeAssignment.node_id == leaf["id"], NodeAssignment.user_id == other_staff_user.id)
        .first()
    )
    assert new_assignment is not None
    assert new_assignment.role.value == "primary"

    old_history = (
        db_session.query(AssignmentHistory)
        .filter(
            AssignmentHistory.node_id == leaf["id"],
            AssignmentHistory.user_id == staff_user.id,
        )
        .first()
    )
    assert old_history.end_date is not None

    new_history = (
        db_session.query(AssignmentHistory)
        .filter(
            AssignmentHistory.node_id == leaf["id"],
            AssignmentHistory.user_id == other_staff_user.id,
        )
        .first()
    )
    assert new_history is not None
    assert new_history.end_date is None


def test_only_admin_can_handover(staff_client, staff_user, other_staff_user):
    resp = staff_client.post(
        "/api/handover",
        json={
            "from_user_id": staff_user.id,
            "to_user_id": other_staff_user.id,
            "node_ids": [],
            "role": "primary",
            "effective_date": "2025-09-01",
        },
    )
    assert resp.status_code == 403
