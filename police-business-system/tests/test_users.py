def test_only_admin_can_list_users(admin_client, staff_client):
    resp = staff_client.get("/api/users")
    assert resp.status_code == 403

    resp = admin_client.get("/api/users")
    assert resp.status_code == 200
    usernames = {u["username"] for u in resp.json()}
    assert "admin" in usernames
    assert "chen" in usernames


def test_user_assignments_lists_nodes_with_role(admin_client, staff_user, other_staff_user):
    top = admin_client.post("/api/nodes", json={"name": "詐欺業務"}).json()
    leaf = admin_client.post("/api/nodes", json={"name": "防制面", "parent_id": top["id"]}).json()
    admin_client.post(
        f"/api/nodes/{leaf['id']}/assignments",
        json={"user_id": staff_user.id, "role": "primary"},
    )
    admin_client.post(
        f"/api/nodes/{leaf['id']}/assignments",
        json={"user_id": other_staff_user.id, "role": "support"},
    )

    resp = admin_client.get(f"/api/users/{staff_user.id}/assignments")
    assert resp.status_code == 200
    body = resp.json()
    assert body == [{"node_id": leaf["id"], "node_name": "防制面", "role": "primary"}]

    resp2 = admin_client.get(f"/api/users/{other_staff_user.id}/assignments")
    assert resp2.json()[0]["role"] == "support"


def test_user_with_no_assignments_returns_empty_list(admin_client, staff_user):
    resp = admin_client.get(f"/api/users/{staff_user.id}/assignments")
    assert resp.status_code == 200
    assert resp.json() == []
